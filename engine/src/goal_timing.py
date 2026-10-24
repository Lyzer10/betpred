"""Walk forward goal timing model, vectorized simulation, and Stage 3 report."""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .dixon_coles import score_matrix
from .leagues import get_league, paths
from .calibration import (
    ENGINE_DIR, MATCHES_PATH, DC_PATH, OUTPUT_PATH, TEST_SEASONS, add_actuals,
    binary_metrics, choose_methods, walk_forward_calibration,
)

GOALS_PATH = ENGINE_DIR / "data" / "processed" / "goals.parquet"
TIMING_PATH = ENGINE_DIR / "data" / "processed" / "predictions_goal_timing.parquet"
REPORT_PATH = ENGINE_DIR / "reports" / "stage3_report.md"
VALIDATION_SEASONS = ["2021/22", "2022/23", "2023/24"]
ALL_SEASONS = VALIDATION_SEASONS + TEST_SEASONS
BUCKET_LABELS = ["1 to 15", "16 to 30", "31 to 45 plus", "46 to 60", "61 to 75", "76 to 90 plus"]
STATE_LABELS = ["level", "leading_1", "leading_2plus", "trailing_1", "trailing_2plus"]
TIMING_MARKETS = {
    "home_first": ("sim_home_first", "actual_home_first"),
    "away_first": ("sim_away_first", "actual_away_first"),
    "no_goal": ("sim_no_goal", "actual_no_goal"),
    "home_1up": ("sim_home_1up", "actual_home_1up"),
    "away_1up": ("sim_away_1up", "actual_away_1up"),
}


def minute_bucket(minute: int) -> int:
    minute = min(max(int(minute), 1), 90)
    return min((minute - 1) // 15, 5)


def estimate_time_profile(goals: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return six bucket shares and a 90 minute profile summing to one."""
    counts = np.zeros(6, dtype=float)
    for minute in goals.minute:
        counts[minute_bucket(minute)] += 1
    shares = counts / counts.sum() if counts.sum() else np.full(6, 1 / 6)
    profile = np.repeat(shares / 15, 15)
    return shares, profile


def _state_index(difference: np.ndarray | int) -> np.ndarray:
    difference = np.asarray(difference)
    return np.select([difference == 0, difference == 1, difference >= 2, difference == -1],
                     [0, 1, 2, 3], default=4).astype(int)


def build_state_exposure(matches: pd.DataFrame, goals: pd.DataFrame, predictions: pd.DataFrame,
                         profile: np.ndarray) -> pd.DataFrame:
    """Build match and team state exposures with DC lambda as the offset base."""
    joined = matches.merge(predictions[["match_id", "lambda_home", "lambda_away"]], on="match_id", validate="one_to_one")
    goals_by_match = {match_id: group for match_id, group in goals.groupby("match_id")}
    records = []
    for match in joined.itertuples(index=False):
        events = goals_by_match.get(match.match_id, pd.DataFrame(columns=["minute", "team"]))
        event_counts = {(min(max(int(row.minute), 1), 90), row.team): 0 for row in events.itertuples(index=False)}
        for row in events.itertuples(index=False):
            key = (min(max(int(row.minute), 1), 90), row.team)
            event_counts[key] = event_counts.get(key, 0) + 1
        home_score = away_score = 0
        accumulated = {(side, state): [0.0, 0] for side in ("home", "away") for state in range(5)}
        for minute in range(1, 91):
            difference = home_score - away_score
            home_state = int(_state_index(difference))
            away_state = int(_state_index(-difference))
            home_goals = event_counts.get((minute, "home"), 0)
            away_goals = event_counts.get((minute, "away"), 0)
            accumulated[("home", home_state)][0] += profile[minute - 1]
            accumulated[("home", home_state)][1] += home_goals
            accumulated[("away", away_state)][0] += profile[minute - 1]
            accumulated[("away", away_state)][1] += away_goals
            home_score += home_goals
            away_score += away_goals
        for (side, state), (base_exposure, scored) in accumulated.items():
            if base_exposure:
                records.append({"match_id": match.match_id, "side": side, "state": state,
                                "goals": scored, "base_exposure": base_exposure,
                                "lambda": match.lambda_home if side == "home" else match.lambda_away})
    return pd.DataFrame(records)


def fit_state_multipliers(matches: pd.DataFrame, goals: pd.DataFrame, predictions: pd.DataFrame,
                          profile: np.ndarray) -> np.ndarray:
    if predictions.empty:
        return np.ones(5)
    exposure = build_state_exposure(matches, goals, predictions, profile)
    design = np.eye(5)[exposure.state.to_numpy(int)]
    offset = np.log(np.clip(exposure["lambda"].to_numpy() * exposure.base_exposure.to_numpy(), 1e-12, None))
    try:
        result = sm.GLM(exposure.goals.to_numpy(), design, family=sm.families.Poisson(), offset=offset).fit()
        multipliers = np.exp(np.asarray(result.params))
    except Exception:
        multipliers = np.ones(5)
    return np.clip(multipliers, 0.25, 4.0)


def _simulate_once(lam: float, mu: float, profile: np.ndarray, multipliers: np.ndarray,
                   simulations: int, seed: int, scale_home: float, scale_away: float):
    rng = np.random.default_rng(seed)
    home_score = np.zeros(simulations, dtype=np.int16)
    away_score = np.zeros(simulations, dtype=np.int16)
    first = np.zeros(simulations, dtype=np.int8)
    home_led = np.zeros(simulations, dtype=bool)
    away_led = np.zeros(simulations, dtype=bool)
    for minute in range(90):
        difference = home_score - away_score
        home_rate = lam * scale_home * profile[minute] * multipliers[_state_index(difference)]
        away_rate = mu * scale_away * profile[minute] * multipliers[_state_index(-difference)]
        home_events = rng.poisson(home_rate)
        away_events = rng.poisson(away_rate)
        scoreless = first == 0
        only_home = scoreless & (home_events > 0) & (away_events == 0)
        only_away = scoreless & (away_events > 0) & (home_events == 0)
        both = scoreless & (home_events > 0) & (away_events > 0)
        first[only_home] = 1
        first[only_away] = 2
        if both.any():
            probability_home_first = home_events[both] / (home_events[both] + away_events[both])
            first[both] = np.where(rng.random(both.sum()) < probability_home_first, 1, 2)
        home_led |= only_home | (both & (first == 1))
        away_led |= only_away | (both & (first == 2))
        home_score += home_events
        away_score += away_events
        home_led |= home_score > away_score
        away_led |= away_score > home_score
    return home_score, away_score, first, home_led, away_led


MAX_GOALS = 10
SHRINK_PSEUDO_COUNT = 20.0


def exchangeable_priors() -> dict[str, np.ndarray]:
    """Path probabilities given a final score h-a when goal order is uniformly random.

    First scorer: h / (h + a). Ever leading (ballot theorem): certain if h > a,
    otherwise h / (a + 1). Used to smooth sparsely simulated scorelines.
    """
    h, a = np.meshgrid(np.arange(MAX_GOALS + 1), np.arange(MAX_GOALS + 1), indexing="ij")
    total = np.maximum(h + a, 1)
    return {
        "home_first": np.where(h + a > 0, h / total, 0.0),
        "away_first": np.where(h + a > 0, a / total, 0.0),
        "home_1up": np.where(h > a, 1.0, h / (a + 1)),
        "away_1up": np.where(a > h, 1.0, a / (h + 1)),
    }


PRIORS = exchangeable_priors()


def path_market_probabilities(home_score, away_score, events: dict[str, np.ndarray],
                              matrix: np.ndarray) -> dict[str, float]:
    """Combine DC final-score probabilities with simulated path behaviour per score.

    P(event) = sum over scores of P_DC(score) * P_sim(event | score). The DC matrix
    stays the authority on final scores (including its low-score correction); the
    simulation only contributes how matches tend to unfold on the way to each score.
    """
    cell = np.minimum(home_score, MAX_GOALS) * (MAX_GOALS + 1) + np.minimum(away_score, MAX_GOALS)
    counts = np.bincount(cell, minlength=(MAX_GOALS + 1) ** 2).reshape(MAX_GOALS + 1, -1)
    output = {}
    for name, happened in events.items():
        hits = np.bincount(cell, weights=happened.astype(float),
                           minlength=(MAX_GOALS + 1) ** 2).reshape(MAX_GOALS + 1, -1)
        prior = PRIORS[name]
        conditional = (hits + SHRINK_PSEUDO_COUNT * prior) / (counts + SHRINK_PSEUDO_COUNT)
        # Structurally certain cells (e.g. 2-0 means home scored first) stay exact.
        certain = (prior == 0) | (prior == 1)
        conditional = np.where(certain, prior, conditional)
        output[name] = float(np.sum(matrix * conditional))
    return output


def simulate_match(lam: float, mu: float, profile: np.ndarray, multipliers: np.ndarray,
                   simulations: int = 20_000, seed: int = 0,
                   matrix: np.ndarray | None = None) -> dict[str, float]:
    """Simulate one match minute by minute.

    With a DC score matrix, timing markets are re-weighted onto the DC final-score
    distribution (see path_market_probabilities). Raw simulation values are kept
    under raw_* for diagnostics.
    """
    profile = np.asarray(profile, float) / np.sum(profile)
    multipliers = np.asarray(multipliers, float)
    scale_home = scale_away = 1.0
    if not np.allclose(multipliers, 1):
        # Same seed and size as the final run (common random numbers), so the scale
        # converges on the final sample rather than chasing independent noise.
        for _ in range(4):
            scores = _simulate_once(lam, mu, profile, multipliers, simulations, seed,
                                    scale_home, scale_away)
            scale_home *= lam / max(scores[0].mean(), 1e-6)
            scale_away *= mu / max(scores[1].mean(), 1e-6)
    home_score, away_score, first, home_led, away_led = _simulate_once(
        lam, mu, profile, multipliers, simulations, seed, scale_home, scale_away)
    result = {
        "raw_home_first": float(np.mean(first == 1)), "raw_away_first": float(np.mean(first == 2)),
        "raw_no_goal": float(np.mean(first == 0)), "raw_home_1up": float(home_led.mean()),
        "raw_away_1up": float(away_led.mean()), "raw_home_win": float(np.mean(home_score > away_score)),
        "raw_draw": float(np.mean(home_score == away_score)),
        "raw_over25": float(np.mean(home_score + away_score > 2)),
        "raw_mean_home_goals": float(home_score.mean()), "raw_mean_away_goals": float(away_score.mean()),
    }
    if matrix is None:
        timing = {name: result[f"raw_{name}"] for name in ("home_first", "away_first", "home_1up", "away_1up")}
        no_goal = result["raw_no_goal"]
    else:
        timing = path_market_probabilities(home_score, away_score, {
            "home_first": first == 1, "away_first": first == 2,
            "home_1up": home_led, "away_1up": away_led,
        }, matrix)
        no_goal = float(matrix[0, 0])
    result.update({f"sim_{name}": value for name, value in timing.items()})
    result["sim_no_goal"] = no_goal
    return result


def build_timing_predictions(league="EPL") -> tuple[pd.DataFrame, dict, dict, dict]:
    league_paths = paths(get_league(league))
    matches = pd.read_parquet(league_paths.matches)
    goals = pd.read_parquet(league_paths.goals)
    dc = pd.read_parquet(league_paths.predictions_dc)
    dc = dc[(dc.variant == "blend") & dc.split.isin(["validation", "test"])].copy()
    source = add_actuals(dc.merge(matches, on=["match_id", "date"], validate="one_to_one"))
    rows, fold_models = [], {}
    for season in ALL_SEASONS:
        fold = source[source.season == season].sort_values("date")
        first_date = fold.date.min()
        historical_matches = matches[matches.date < first_date]
        historical_ids = set(historical_matches.match_id)
        historical_goals = goals[goals.match_id.isin(historical_ids)]
        shares, profile = estimate_time_profile(historical_goals)
        training_predictions = dc[dc.date < first_date]
        training_matches = matches[matches.match_id.isin(training_predictions.match_id)]
        training_goals = goals[goals.match_id.isin(set(training_matches.match_id))]
        multipliers = fit_state_multipliers(training_matches, training_goals, training_predictions, profile)
        fold_models[season] = {"training_max_date": None if training_predictions.empty else training_predictions.date.max().isoformat(),
                               "first_prediction_date": first_date.isoformat(), "shares": shares.tolist(),
                               "multipliers": multipliers.tolist()}
        for match in fold.itertuples(index=False):
            seed = int(match.match_id) if str(match.match_id).isdigit() else abs(hash(match.match_id)) % (2**32)
            matrix = score_matrix(match.lambda_home, match.lambda_away, match.rho)
            timing = simulate_match(match.lambda_home, match.lambda_away, profile, multipliers,
                                    seed=seed, matrix=matrix)
            rows.append({"match_id": match.match_id, "date": match.date, "season": season,
                         "split": match.split, "lambda_home": match.lambda_home, "lambda_away": match.lambda_away,
                         "prob_home": match.prob_home, "prob_draw": match.prob_draw,
                         "prob_over25": match.prob_over25, **timing})
        print(f"Simulated {season}: {len(fold)} matches")
    timing = add_actuals(pd.DataFrame(rows).merge(matches, on=["match_id", "date", "season"], validate="one_to_one"))
    calibrated, audit = walk_forward_calibration(timing, TIMING_MARKETS)
    methods, scores = choose_methods(calibrated, TIMING_MARKETS)
    calibrated.to_parquet(league_paths.predictions_goal_timing, index=False)
    return calibrated, methods, scores, {"folds": fold_models, "audit": audit}


def _calibration_table(probability, actual) -> list[str]:
    frame = pd.DataFrame({"probability": probability, "actual": actual})
    frame["bin"] = pd.cut(frame.probability, np.linspace(0, 1, 11), labels=False, include_lowest=True)
    grouped = frame.groupby("bin", observed=False).agg(mean_predicted=("probability", "mean"), actual_rate=("actual", "mean"), count=("actual", "size"))
    lines = ["| Bin | Mean predicted | Actual rate | Count |", "|---|---:|---:|---:|"]
    for index in range(10):
        if index in grouped.index:
            row = grouped.loc[index]
            lines.append(f"| {index / 10:.1f} to {(index + 1) / 10:.1f} | {row.mean_predicted:.3f} | {row.actual_rate:.3f} | {int(row['count'])} |")
        else:
            lines.append(f"| {index / 10:.1f} to {(index + 1) / 10:.1f} | NA | NA | 0 |")
    return lines


def _value_rows(frame: pd.DataFrame) -> list[str]:
    specifications = [
        ("1X2 home", "cal_home", "odds_home", "close_odds_home", frame.home_goals > frame.away_goals),
        ("1X2 draw", "cal_draw", "odds_draw", "close_odds_draw", frame.home_goals == frame.away_goals),
        ("1X2 away", "cal_away", "odds_away", "close_odds_away", frame.home_goals < frame.away_goals),
        ("Goals over 2.5", "cal_over25", "odds_over25", "close_odds_over25", frame.home_goals + frame.away_goals > 2.5),
        ("Goals under 2.5", "cal_under25", "odds_under25", "close_odds_under25", frame.home_goals + frame.away_goals < 2.5),
    ]
    rows = []
    for label, probability, odds, close, actual in specifications:
        valid = frame[[probability, odds, close]].notna().all(axis=1)
        selected = valid & (frame[probability] * frame[odds] > 1.05)
        count = int(selected.sum())
        won = np.asarray(actual)[selected]
        profit = np.where(won, frame.loc[selected, odds] - 1, -1).sum() if count else 0
        clv = (frame.loc[selected, odds] > frame.loc[selected, close]).mean() if count else np.nan
        sample = "insufficient sample" if count < 200 else "adequate sample"
        rows.append(f"| {label} | {count} | {won.mean():.2%} | {profit / count:.2%} | {clv:.2%} | {sample} |" if count else
                    f"| {label} | 0 | NA | NA | NA | insufficient sample |")
    return rows


def write_stage3_report(timing: pd.DataFrame, timing_methods: dict, timing_scores: dict, model_audit: dict, league="EPL") -> Path:
    league_paths = paths(get_league(league))
    matches = pd.read_parquet(league_paths.matches)
    calibrated = pd.read_parquet(league_paths.predictions_calibrated)
    base = calibrated[(calibrated.variant == "blend")].merge(matches, on=["match_id", "date"], validate="one_to_one")
    base = add_actuals(base)
    timing_test = timing[timing.season.isin(TEST_SEASONS)].copy()
    base_market_map = {
        "home": ("prob_home", "actual_home"), "draw": ("prob_draw", "actual_draw"), "away": ("prob_away", "actual_away"),
        "over05": ("prob_over05", "actual_over05"), "over15": ("prob_over15", "actual_over15"),
        "over25": ("prob_over25", "actual_over25"), "over35": ("prob_over35", "actual_over35"),
        "btts": ("prob_btts", "actual_btts"), "home_clean_sheet": ("prob_home_clean_sheet", "actual_home_clean_sheet"),
        "away_clean_sheet": ("prob_away_clean_sheet", "actual_away_clean_sheet"),
    }
    lines = ["# Stage 3 report", "", f"Test seasons: {', '.join(TEST_SEASONS)} ({len(base):,} matches).", "",
             "## Calibration metrics", "", "| Market | Method | Log loss | Brier score |", "|---|---|---:|---:|"]
    for market, (raw, actual) in base_market_map.items():
        for method, column in (("raw", raw), ("Platt", f"platt_{market}"), ("isotonic", f"isotonic_{market}")):
            loss, brier = binary_metrics(base[column], base[actual])
            lines.append(f"| {market} | {method} | {loss:.4f} | {brier:.4f} |")
    for market, (raw, actual) in TIMING_MARKETS.items():
        for method, column in (("raw", raw), ("Platt", f"platt_{market}"), ("isotonic", f"isotonic_{market}")):
            loss, brier = binary_metrics(timing_test[column], timing_test[actual])
            lines.append(f"| {market} | {method} | {loss:.4f} | {brier:.4f} |")

    timing_lookup = timing_test.set_index("match_id")
    calibration_specs = [
        ("Home win", base, "prob_home", "cal_home", "actual_home"),
        ("Over 1.5", base, "prob_over15", "cal_over15", "actual_over15"),
        ("Over 2.5", base, "prob_over25", "cal_over25", "actual_over25"),
        ("BTTS", base, "prob_btts", "cal_btts", "actual_btts"),
        ("Home first scorer", timing_test, "sim_home_first", "cal_home_first", "actual_home_first"),
        ("Home 1Up", timing_test, "sim_home_1up", "cal_home_1up", "actual_home_1up"),
        ("Away 1Up", timing_test, "sim_away_1up", "cal_away_1up", "actual_away_1up"),
    ]
    lines += ["", "## Calibration tables", ""]
    for label, frame, raw, after, actual in calibration_specs:
        lines += [f"### {label}, raw", "", *_calibration_table(frame[raw], frame[actual]), "",
                  f"### {label}, calibrated", "", *_calibration_table(frame[after], frame[actual]), ""]

    combined = base.set_index("match_id")
    for column in timing_test.columns:
        if column.startswith("cal_") or column.startswith("actual_") or column.startswith("sim_"):
            combined[column] = timing_lookup[column]
    combined["cal_under25"] = 1 - combined.cal_over25
    confidence = [
        ("Home win", "cal_home", "actual_home"), ("Away win", "cal_away", "actual_away"),
        ("Over 0.5", "cal_over05", "actual_over05"), ("Over 1.5", "cal_over15", "actual_over15"),
        ("Over 2.5", "cal_over25", "actual_over25"), ("BTTS yes", "cal_btts", "actual_btts"),
        ("Home first scorer", "cal_home_first", "actual_home_first"),
        ("Home 1Up", "cal_home_1up", "actual_home_1up"), ("Away 1Up", "cal_away_1up", "actual_away_1up"),
    ]
    lines += ["## Confidence buckets", "", "| Market | Threshold | Hit rate | Count |", "|---|---:|---:|---:|"]
    for label, probability, actual in confidence:
        for threshold in (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90):
            selected = combined[probability] >= threshold
            lines.append(f"| {label} | {threshold:.2f} | {combined.loc[selected, actual].mean():.2%} | {int(selected.sum())} |" if selected.any()
                         else f"| {label} | {threshold:.2f} | NA | 0 |")

    lines += ["", "## Simulation checks", "",
              "Timing markets are P(event) = sum over final scores of P_DC(score) x P_sim(event | score), "
              "so final-score markets come from the DC matrix exactly. The raw (unweighted) simulation is "
              "shown below as a diagnostic of how well the minute-level process reproduces DC on its own.", "",
              "| Raw simulation check | Mean absolute difference |", "|---|---:|",
              f"| Home win versus DC matrix | {np.mean(np.abs(timing_test.raw_home_win - timing_test.prob_home)):.4f} |",
              f"| Draw versus DC matrix | {np.mean(np.abs(timing_test.raw_draw - timing_test.prob_draw)):.4f} |",
              f"| Over 2.5 versus DC matrix | {np.mean(np.abs(timing_test.raw_over25 - timing_test.prob_over25)):.4f} |",
              f"| Mean goals versus DC lambda (relative) | {np.mean(np.abs(np.r_[timing_test.raw_mean_home_goals / timing_test.lambda_home, timing_test.raw_mean_away_goals / timing_test.lambda_away] - 1)):.4f} |", "",
              "| Outcome | Simulated rate | Actual rate |", "|---|---:|---:|",
              f"| Home first scorer | {timing_test.sim_home_first.mean():.2%} | {timing_test.actual_home_first.mean():.2%} |",
              f"| Away first scorer | {timing_test.sim_away_first.mean():.2%} | {timing_test.actual_away_first.mean():.2%} |",
              f"| No goal | {timing_test.sim_no_goal.mean():.2%} | {timing_test.actual_no_goal.mean():.2%} |",
              f"| Home 1Up | {timing_test.sim_home_1up.mean():.2%} | {timing_test.actual_home_1up.mean():.2%} |",
              f"| Away 1Up | {timing_test.sim_away_1up.mean():.2%} | {timing_test.actual_away_1up.mean():.2%} |", ""]
    final_model = model_audit["folds"][TEST_SEASONS[-1]]
    lines += ["## Final fold time profile", "", "| Bucket | Goal share |", "|---|---:|"]
    lines += [f"| {label} | {share:.3f} |" for label, share in zip(BUCKET_LABELS, final_model["shares"])]
    lines += ["", "## Final fold state multipliers", "", "| State | Multiplier |", "|---|---:|"]
    lines += [f"| {label} | {value:.3f} |" for label, value in zip(STATE_LABELS, final_model["multipliers"])]
    lines += ["", "## Calibrated value test", "", "| Bet | Bets | Hit rate | ROI | Positive closing line value | Sample |",
              "|---|---:|---:|---:|---:|---|", *_value_rows(combined.reset_index()), ""]
    league_paths.stage3_report.write_text("\n".join(lines), encoding="utf-8")
    return league_paths.stage3_report


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="EPL")
    args = parser.parse_args()
    league_paths = paths(get_league(args.league))
    if not league_paths.predictions_calibrated.exists():
        from .calibration import build_calibrated_predictions
        build_calibrated_predictions(args.league)
    started = time.perf_counter()
    timing, methods, scores, audit = build_timing_predictions(args.league)
    report = write_stage3_report(timing, methods, scores, audit, args.league)
    print(f"Wrote {len(timing):,} timing predictions to {league_paths.predictions_goal_timing}")
    print(f"Wrote {report} in {time.perf_counter() - started:.1f} seconds")
    print("Chosen timing methods:", methods)


if __name__ == "__main__":
    main()
