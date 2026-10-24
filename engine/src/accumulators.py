"""Stage 4: accumulator (multi-bet) builder and walk-forward slip backtest.

Three tiers, one slip per tier per betting round:
  safe    total odds 2.5-3.5,  2-3 legs
  medium  total odds 5-8,      3-5 legs
  big     total odds 10-25,    4-8 legs
At most one leg per match, so legs are treated as independent and the slip win
probability is the product of the calibrated leg probabilities.

Odds: football-data.co.uk has no history for 1Up, first scorer, BTTS or the other
goal lines. Leg odds are therefore ESTIMATED from the bookmaker's own pre-match
average prices, the kind fixtures.csv offers live (never from our model, which would make the backtest circular):
  1. remove the margin from opening 1X2 and over/under 2.5 odds;
  2. fit the bookmaker-implied DC score matrix to those fair probabilities;
  3. read every market off that matrix (1Up/first scorer via the exchangeable
     path priors in goal_timing);
  4. apply a retail margin (RETAIL_MARGIN) to mimic SportyBet-style prices.
In the app the user enters the real odds instead.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from sklearn.linear_model import LogisticRegression

from .calibration import ENGINE_DIR, MATCHES_PATH, OUTPUT_PATH, TEST_SEASONS
from .dixon_coles import market_probabilities, score_matrix
from .goal_timing import PRIORS, TIMING_PATH
from .leagues import get_league, paths

LEGS_PATH = ENGINE_DIR / "data" / "processed" / "accumulator_legs.parquet"
SLIPS_PATH = ENGINE_DIR / "data" / "processed" / "accumulator_slips.parquet"
REPORT_PATH = ENGINE_DIR / "reports" / "stage4_report.md"
RETAIL_MARGIN = 0.07
AVERAGE_ODDS = ["avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25"]
ODDS_RESOLUTION = 0.005  # log-odds bucket width for the slip search (~0.5% in odds)


@dataclass(frozen=True)
class Tier:
    name: str
    min_odds: float
    max_odds: float
    min_legs: int
    max_legs: int


# The user's tiers. Legs per slip allow low-odds markets (1Up, overs, double
# chance) to reach the odds range.
TIERS = (
    Tier("safe", 2.5, 3.5, 2, 4),
    Tier("medium", 3.5, 8.0, 3, 6),
    Tier("big", 8.0, 12.0, 4, 8),
)

# market -> (calibrated probability column, actual outcome column)
LEG_MARKETS = {
    "home_win": ("cal_home", "actual_home"),
    "draw": ("cal_draw", "actual_draw"),
    "away_win": ("cal_away", "actual_away"),
    "over_0.5": ("cal_over05", "actual_over05"),
    "over_1.5": ("cal_over15", "actual_over15"),
    "over_2.5": ("cal_over25", "actual_over25"),
    "over_3.5": ("cal_over35", "actual_over35"),
    "under_2.5": ("cal_under25", "actual_under25"),
    "under_3.5": ("cal_under35", "actual_under35"),
    "btts_yes": ("cal_btts", "actual_btts"),
    "btts_no": ("cal_btts_no", "actual_btts_no"),
    "home_1up": ("cal_home_1up", "actual_home_1up"),
    "away_1up": ("cal_away_1up", "actual_away_1up"),
    "home_first": ("cal_home_first", "actual_home_first"),
    "away_first": ("cal_away_first", "actual_away_first"),
    "double_1x": ("cal_dc_1x", "actual_dc_1x"),
    "double_x2": ("cal_dc_x2", "actual_dc_x2"),
    "double_12": ("cal_dc_12", "actual_dc_12"),
}

# Markets the user bets in accumulators: 1Up, over/under goals, a team to win, double chance.
SLIP_MARKETS = ("home_1up", "away_1up", "over_0.5", "over_1.5", "over_2.5", "under_2.5", "under_3.5",
                "home_win", "away_win", "double_1x", "double_x2", "double_12")


def bookmaker_fair_probabilities(odds_home, odds_draw, odds_away, odds_over, odds_under, rho):
    """Market probabilities implied by the bookmaker's 1X2 and O/U 2.5 prices."""
    inverse = 1 / np.array([odds_home, odds_draw, odds_away])
    target_1x2 = inverse / inverse.sum()
    ou = 1 / np.array([odds_over, odds_under])
    target_over = ou[0] / ou.sum()

    def residuals(log_lambdas):
        markets = market_probabilities(score_matrix(*np.exp(log_lambdas), rho))
        return [markets["prob_home"] - target_1x2[0], markets["prob_draw"] - target_1x2[1],
                markets["prob_away"] - target_1x2[2], markets["prob_over25"] - target_over]

    fit = least_squares(residuals, np.log([1.5, 1.2]), bounds=(np.log(0.05), np.log(6.0)))
    matrix = score_matrix(*np.exp(fit.x), rho)
    markets = market_probabilities(matrix)
    return {
        # Directly priced markets keep the bookmaker's own fair probabilities.
        "home_win": target_1x2[0], "draw": target_1x2[1], "away_win": target_1x2[2],
        "over_2.5": target_over, "under_2.5": 1 - target_over,
        "over_0.5": markets["prob_over05"], "over_1.5": markets["prob_over15"],
        "over_3.5": markets["prob_over35"], "under_3.5": 1 - markets["prob_over35"],
        "btts_yes": markets["prob_btts"], "btts_no": 1 - markets["prob_btts"],
        "home_1up": float(np.sum(matrix * PRIORS["home_1up"])),
        "away_1up": float(np.sum(matrix * PRIORS["away_1up"])),
        "home_first": float(np.sum(matrix * PRIORS["home_first"])),
        "double_1x": target_1x2[0] + target_1x2[1], "double_x2": target_1x2[1] + target_1x2[2],
        "double_12": target_1x2[0] + target_1x2[2],
        "away_first": float(np.sum(matrix * PRIORS["away_first"])),
    }


def betting_round(dates: pd.Series) -> pd.Series:
    """Group fixtures into rounds: weekend (Fri-Mon) and midweek (Tue-Thu)."""
    dates = pd.to_datetime(dates)
    midweek = dates.dt.weekday.isin([1, 2, 3])
    shifted = (dates - pd.to_timedelta(4, unit="D")).dt.isocalendar()
    label = np.where(midweek, "midweek", "weekend")
    return shifted.year.astype(str) + "-W" + shifted.week.astype(str).str.zfill(2) + "-" + label


def _rows_to_legs(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert one row per match with calibrated fields into market leg rows."""
    # Use market-average prices, the same kind the live fixtures file provides.
    frame["cal_under25"] = 1 - frame.cal_over25
    frame["cal_under35"] = 1 - frame.cal_over35
    frame["cal_btts_no"] = 1 - frame.cal_btts
    frame["cal_dc_1x"] = frame.cal_home + frame.cal_draw
    frame["cal_dc_x2"] = frame.cal_draw + frame.cal_away
    frame["cal_dc_12"] = frame.cal_home + frame.cal_away
    frame["actual_dc_1x"] = (frame.home_goals >= frame.away_goals).astype(int)
    frame["actual_dc_x2"] = (frame.home_goals <= frame.away_goals).astype(int)
    frame["actual_dc_12"] = (frame.home_goals != frame.away_goals).astype(int)
    frame["actual_under25"] = 1 - frame.actual_over25
    frame["actual_under35"] = 1 - frame.actual_over35
    frame["actual_btts_no"] = 1 - frame.actual_btts
    frame["round"] = betting_round(frame.date)

    rows = []
    for match in frame.itertuples(index=False):
        fair = bookmaker_fair_probabilities(*(getattr(match, column) for column in AVERAGE_ODDS), match.rho)
        for market, (probability_column, actual_column) in LEG_MARKETS.items():
            rows.append({
                "match_id": match.match_id, "date": match.date, "season": match.season,
                "round": match.round, "home_team": match.home_team, "away_team": match.away_team,
                "market": market, "probability": float(getattr(match, probability_column)),
                "bookmaker_probability": fair[market],
                "odds": 1 / (fair[market] * (1 + RETAIL_MARGIN)),
                "won": int(getattr(match, actual_column)),
            })
    return pd.DataFrame(rows)


def _prepare_leg_frame(timing: pd.DataFrame, matches: pd.DataFrame,
                       calibrated: pd.DataFrame | None = None) -> pd.DataFrame:
    if calibrated is not None:
        cal_columns = ["cal_home", "cal_draw", "cal_away", "cal_over05", "cal_over15",
                       "cal_over25", "cal_over35", "cal_btts", "rho"]
        timing = timing.merge(calibrated[["match_id", *cal_columns]], on="match_id", validate="one_to_one")
    missing_odds = [column for column in AVERAGE_ODDS if column not in timing]
    if missing_odds:
        timing = timing.merge(matches[["match_id", *missing_odds]], on="match_id", validate="one_to_one")
    valid = (timing[AVERAGE_ODDS].notna() & timing[AVERAGE_ODDS].gt(0)).all(axis=1) & timing.rho.notna()
    return timing[valid].copy()


def build_validation_leg_table(league="EPL") -> pd.DataFrame:
    league_paths = paths(get_league(league))
    from .goal_timing import build_validation_timing_predictions
    if not league_paths.predictions_goal_timing_validation.exists():
        build_validation_timing_predictions(league)
    timing = pd.read_parquet(league_paths.predictions_goal_timing_validation)
    matches = pd.read_parquet(league_paths.matches)
    legs = _rows_to_legs(_prepare_leg_frame(timing, matches))
    legs = legs[legs.odds >= 1.05].reset_index(drop=True)
    legs = legs.rename(columns={"probability": "model_probability"})
    return legs


def _platt_market(history: pd.DataFrame, probability: pd.Series, regularization: float = 1.0) -> np.ndarray:
    if history.empty or history.won.nunique() < 2:
        return probability.to_numpy(float)
    model = LogisticRegression(C=regularization, solver="lbfgs", max_iter=1000)
    model.fit(_logit(history.bookmaker_probability).to_numpy().reshape(-1, 1), history.won)
    return model.predict_proba(_logit(probability).to_numpy().reshape(-1, 1))[:, 1]


def _select_market_regularization(validation: pd.DataFrame) -> float:
    """Choose Platt regularisation on date-forward validation predictions only."""
    candidates = (0.1, 1.0, 10.0, 1e6)
    scores = []
    for candidate in candidates:
        probabilities, outcomes = [], []
        dates = sorted(validation.date.unique())
        for prediction_date in dates:
            history = validation[validation.date < prediction_date]
            fold = validation[validation.date == prediction_date]
            if history.empty:
                continue
            probabilities.extend(_platt_market(history, fold.bookmaker_probability, candidate))
            outcomes.extend(fold.won)
        probabilities, outcomes = np.asarray(probabilities), np.asarray(outcomes)
        if len(np.unique(outcomes)) < 2:
            scores.append((0.0, _log_loss(probabilities, outcomes)))
            continue
        calibration = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        calibration.fit(_logit(probabilities).reshape(-1, 1), outcomes)
        slope = float(calibration.coef_[0, 0])
        scores.append((abs(slope - 1), _log_loss(probabilities, outcomes)))
    return float(candidates[min(range(len(candidates)), key=lambda index: scores[index])])


def calibrate_market_probabilities(validation: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Platt calibrate bookmaker consensus with earlier seasons only."""
    validation, test = validation.copy(), test.copy()
    validation["market_probability"] = np.nan
    test["market_probability"] = np.nan
    for market in validation.market.unique():
        market_validation = validation[validation.market == market]
        regularization = _select_market_regularization(market_validation)
        for prediction_date in sorted(market_validation.date.unique()):
            current = (validation.market == market) & (validation.date == prediction_date)
            history = market_validation[market_validation.date < prediction_date]
            validation.loc[current, "market_probability"] = _platt_market(history, validation.loc[current, "bookmaker_probability"], regularization)
        market_test = test[test.market == market]
        for prediction_date in sorted(market_test.date.unique()):
            current = (test.market == market) & (test.date == prediction_date)
            history = pd.concat([validation[validation.market == market],
                                 market_test[market_test.date < prediction_date]], ignore_index=True)
            test.loc[current, "market_probability"] = _platt_market(history, test.loc[current, "bookmaker_probability"], regularization)
    return validation, test


def build_leg_table(league="EPL") -> pd.DataFrame:
    """One row per test match and market with final blended probability."""
    league_paths = paths(get_league(league))
    timing = pd.read_parquet(league_paths.predictions_goal_timing)
    timing = timing[timing.season.isin(TEST_SEASONS)]
    calibrated = pd.read_parquet(league_paths.predictions_calibrated)
    calibrated = calibrated[calibrated.variant == "blend"]
    matches = pd.read_parquet(league_paths.matches)
    legs = _rows_to_legs(_prepare_leg_frame(timing, matches, calibrated))
    validation = build_validation_leg_table(league)
    validation, legs = calibrate_market_probabilities(validation, legs)
    # Legs paying under 1.05 add risk without meaningfully moving the slip odds.
    legs = legs[legs.odds >= 1.05].reset_index(drop=True)
    legs = legs.rename(columns={"probability": "model_probability"})
    legs["probability"], weights = blend_with_market(legs, validation)
    legs["edge"] = legs.probability * legs.odds - 1
    legs.attrs["model_weights"] = weights
    return legs


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _log_loss(p, y) -> float:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def blend(model_probability, market_probability, model_weight: float):
    z = model_weight * _logit(model_probability) + (1 - model_weight) * _logit(market_probability)
    return 1 / (1 + np.exp(-z))


def fit_model_weight(history: pd.DataFrame) -> float:
    """Model weight in [0, 1] (0.05 steps) minimising log loss on settled legs."""
    grid = np.linspace(0, 1, 21)
    market_column = "market_probability" if "market_probability" in history else "bookmaker_probability"
    losses = [_log_loss(blend(history.model_probability, history[market_column], w), history.won)
              for w in grid]
    return float(grid[int(np.argmin(losses))])


def blend_with_market(legs: pd.DataFrame, validation_legs: pd.DataFrame | None = None,
                      default_weight: float = 0.5) -> tuple[np.ndarray, dict]:
    """Logit-blend model and bookmaker probabilities, weight learned walk-forward.

    On its own the model loses to the sharp market on most markets, and picking
    the slips where it disagrees most with the market selects its errors (winner's
    curse). For each season the model weight is chosen on earlier seasons only;
    the first season, with no history, uses default_weight.
    """
    blended = np.empty(len(legs))
    weights = {}
    for season in sorted(legs.season.unique()):
        history = legs[legs.season < season]
        if validation_legs is not None:
            history = pd.concat([validation_legs, history], ignore_index=True)
        weight = default_weight if history.empty else fit_model_weight(history)
        current = (legs.season == season).to_numpy()
        market_column = "market_probability" if "market_probability" in legs else "bookmaker_probability"
        blended[current] = blend(legs.model_probability[current], legs.loc[current, market_column], weight)
        weights[season] = weight
    return blended, weights


def best_slip(legs: pd.DataFrame, tier: Tier) -> list[int] | None:
    """Return leg indices of the slip with the highest win probability for a tier.

    Exact search over at most one leg per match by dynamic programming on
    (number of legs, total log-odds bucket), maximising the summed log probability.
    """
    max_bucket = int(np.ceil(np.log(tier.max_odds) / ODDS_RESOLUTION)) + 1
    depth = tier.max_legs + 1
    best = np.full((depth, max_bucket), -np.inf)
    best[0, 0] = 0.0
    history = []  # per match: chosen leg index per state (-1 = match skipped)
    for _, match_legs in legs.groupby("match_id", sort=False):
        updated = best.copy()
        choice = np.full((depth, max_bucket), -1, dtype=int)
        for index, leg in match_legs.iterrows():
            step = int(round(np.log(leg.odds) / ODDS_RESOLUTION))
            if step >= max_bucket:
                continue
            candidate = np.full_like(best, -np.inf)
            candidate[1:, step:] = best[:-1, : max_bucket - step] + np.log(leg.probability)
            improved = candidate > updated
            updated[improved] = candidate[improved]
            choice[improved] = index
        history.append((choice, best))
        best = updated

    lowest = int(np.floor(np.log(tier.min_odds) / ODDS_RESOLUTION))
    states = [(best[n, b], n, b) for n in range(tier.min_legs, depth)
              for b in range(max(lowest - tier.max_legs, 0), max_bucket) if np.isfinite(best[n, b])]
    # Bucket rounding can shift the total by a fraction of a percent, so verify the
    # exact odds of each candidate, best first.
    for _, n, b in sorted(states, reverse=True):
        picks = _backtrack(history, legs, n, b)
        total = float(np.prod(legs.loc[picks, "odds"]))
        if tier.min_odds <= total <= tier.max_odds:
            return picks
    return None


def _backtrack(history, legs: pd.DataFrame, n: int, b: int) -> list[int]:
    picks = []
    for choice, _ in reversed(history):
        index = choice[n, b]
        if index >= 0:
            picks.append(int(index))
            n -= 1
            b -= int(round(np.log(legs.loc[index, "odds"]) / ODDS_RESOLUTION))
    return picks[::-1]


def backtest_slips(legs: pd.DataFrame, modes: dict[str, float | None]) -> pd.DataFrame:
    """Build and settle one slip per tier, match day and mode, from SLIP_MARKETS only.

    Grouping by day mirrors the live app, which offers each day's own slips.
    modes maps a mode name to (probability column, minimum leg edge or None).
    """
    slips = []
    legs = legs[legs.market.isin(SLIP_MARKETS)]
    for round_id, round_legs in legs.groupby(legs.date.dt.strftime("%Y-%m-%d"), sort=True):
        for mode, (probability_column, min_edge) in modes.items():
            pool = round_legs.assign(probability=round_legs[probability_column])
            if min_edge is not None:
                pool = pool[pool.probability * pool.odds - 1 >= min_edge]
            for tier in TIERS:
                picks = best_slip(pool, tier) if not pool.empty else None
                if picks is None:
                    continue
                chosen = pool.loc[picks]
                slips.append({
                    "round": round_id, "season": chosen.season.iloc[0], "mode": mode, "tier": tier.name,
                    "legs": len(chosen), "total_odds": float(chosen.odds.prod()),
                    "predicted_win": float(chosen.probability.prod()),
                    "bookmaker_win": float(chosen.bookmaker_probability.prod()),
                    "won": int(chosen.won.all()), "legs_won": int(chosen.won.sum()),
                    "markets": ",".join(chosen.market),
                    "selections": " | ".join(f"{r.home_team} v {r.away_team}: {r.market} @ {r.odds:.2f}"
                                             for r in chosen.itertuples()),
                })
    return pd.DataFrame(slips)


def _wilson(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return float("nan"), float("nan")
    p = successes / total
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return centre - half, centre + half


def write_report(legs: pd.DataFrame, slips: pd.DataFrame, report_path=REPORT_PATH) -> None:
    lines = ["# Stage 4 report: accumulator tiers", "",
             f"Test seasons: {', '.join(TEST_SEASONS)}; {legs.match_id.nunique()} matches, "
             f"{legs['round'].nunique()} betting rounds (weekend Fri-Mon / midweek Tue-Thu).", "",
             f"Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a "
             f"{RETAIL_MARGIN:.0%} retail margin (see module docstring). Hit rates do not depend on "
             "odds; ROI does, so treat ROI as indicative only.", "",
             "Leg probability = logit blend of calibrated model and bookmaker-implied probability. "
             "Model weight per season, learned on earlier seasons only: "
             + ", ".join(f"{s}: {w:.2f}" for s, w in legs.attrs.get("model_weights", {}).items()) + ".", "",
             "Modes: `blended` picks the most likely slip using the learned model and market blend; "
             "`market` uses the calibrated bookmaker consensus; `model_only` is a diagnostic; "
             "`value` only uses legs where blended probability x estimated odds >= 1.03. "
             "Predicted win uses each mode's own probabilities.", "",
             "## Slip results", "",
             "| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |",
             "|---|---|---:|---:|---:|---:|---:|---|---:|---:|"]
    for (mode, tier), group in slips.groupby(["mode", "tier"], sort=False):
        low, high = _wilson(int(group.won.sum()), len(group))
        roi = (np.where(group.won == 1, group.total_odds, 0) - 1).mean()
        lines.append(f"| {mode} | {tier} | {len(group)} | {group.legs.mean():.1f} | {group.total_odds.mean():.2f} | "
                     f"{group.predicted_win.mean():.1%} | {group.won.mean():.1%} | {low:.0%}-{high:.0%} | "
                     f"{group.bookmaker_win.mean():.1%} | {roi:+.1%} |")

    lines += ["", "## By season (blended mode)", "", "| Tier | Season | Slips | Predicted win | Actual win |",
              "|---|---|---:|---:|---:|"]
    accuracy = slips[slips["mode"] == "blended"]
    for (tier, season), group in accuracy.groupby(["tier", "season"], sort=False):
        lines.append(f"| {tier} | {season} | {len(group)} | {group.predicted_win.mean():.1%} | {group.won.mean():.1%} |")

    lines += ["", "## Markets used in slips (blended mode)", "", "| Tier | Market | Legs | Leg hit rate |",
              "|---|---|---:|---:|"]
    for tier in TIERS:
        tier_slips = accuracy[accuracy.tier == tier.name]
        used = []
        for slip in tier_slips.itertuples():
            for selection in slip.selections.split(" | "):
                used.append(selection.split(": ")[1].split(" @ ")[0])
        counts = pd.Series(used).value_counts()
        chosen_legs = _chosen_legs(legs, tier_slips)
        for market, count in counts.items():
            rate = chosen_legs.loc[chosen_legs.market == market, "won"].mean()
            lines.append(f"| {tier.name} | {market} | {count} | {rate:.1%} |")

    lines += ["", "## Estimated odds sanity check", "",
              "Bookmaker-implied probability vs actual rate across all test matches, per market. "
              "Large gaps would mean the estimated odds are unrealistic.", "",
              "| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |", "|---|---:|---:|---:|---:|"]
    for market, group in legs.groupby("market", sort=False):
        lines.append(f"| {market} | {group.bookmaker_probability.mean():.1%} | {group.probability.mean():.1%} | "
                     f"{group.won.mean():.1%} | {group.odds.median():.2f} |")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _chosen_legs(legs: pd.DataFrame, slips: pd.DataFrame) -> pd.DataFrame:
    keys = set()
    for slip in slips.itertuples():
        for selection in slip.selections.split(" | "):
            fixture, rest = selection.split(": ")
            keys.add((slip.round, fixture, rest.split(" @ ")[0]))
    fixture = legs.home_team + " v " + legs.away_team
    day = legs.date.dt.strftime("%Y-%m-%d")  # slips are grouped by match day
    mask = [(r, f, m) in keys for r, f, m in zip(day, fixture, legs.market)]
    return legs[mask]


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="EPL")
    args = parser.parse_args()
    league_paths = paths(get_league(args.league))
    started = time.perf_counter()
    legs = build_leg_table(args.league)
    legs.to_parquet(league_paths.accumulator_legs, index=False)
    slips = backtest_slips(legs, {
        "blended": ("probability", None),
        "market": ("market_probability", None),
        "model_only": ("model_probability", None),       # shows the winner's curse
        "value": ("probability", 0.03),
    })
    slips.to_parquet(league_paths.accumulator_slips, index=False)
    write_report(legs, slips, league_paths.stage4_report)
    print(f"{len(legs):,} legs, {len(slips):,} slips in {time.perf_counter() - started:.1f}s")
    print(f"Wrote {league_paths.stage4_report}")


if __name__ == "__main__":
    main()
