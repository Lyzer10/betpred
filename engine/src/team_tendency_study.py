"""Do teams have a lasting tendency the prices miss? Pre-registered in PROJECT.md (task 8), 2026-10-29.

Two families, decided separately:
  lead: home_1up / away_1up (the team goes a goal ahead at any point; the owner's "first to lead").
  win:  home_win / away_win (e.g. "Juventus keeps failing": a team the market keeps over- or underrating).
Features, from each team's previous TEAM_WINDOW (38) league matches only (0 with fewer than MIN_HISTORY = 10):
  r_for     = mean(outcome - bookmaker probability) of the team itself in those matches;
  r_against = mean(outcome - bookmaker probability) of the opponents the other team faced (it lets in
              early goals / loses more than priced).
Bookmaker probability = de-margined average odds read through the score matrix
(`accumulators.bookmaker_implied`, league rho), the same reading the live app uses.
Primary (all five leagues pooled, 2014/15 onwards): for each evaluation season S from 2017/18, fit
  baseline   won ~ logit(p) + away
  challenger won ~ logit(p) + away + r_for + r_against
on seasons 2015/16 .. S-1 and score S. Paired per-leg log loss (baseline - challenger); 95% CI by
bootstrap of whole days (2,000, seed 20261029). The baseline recalibrates the price too, so a gain is
the team information, not a recalibration.
Secondary (the probabilities the slips really use, test seasons 2024/25 onwards): EPL live blend
(`market_gates.gate_column`), market leagues `market_probability`; first 60% of days fit, last 40% score,
same two models with p = live probability.
Decision per family: use it only if the primary CI is entirely above 0 AND the secondary difference
is above 0. Reported, not deciding: coefficients, per-league results, and how persistent a team's
season residual is from one season to the next.
Usage: python -m src.team_tendency_study   (writes reports/team_tendency_study.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .accumulators import bookmaker_implied
from .calibration import ENGINE_DIR
from .leagues import paths
from .market_live import league_rho

REPORT_PATH = ENGINE_DIR / "reports" / "team_tendency_study.md"
LEAGUES = ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1")
FAMILIES = {"lead": ("home_1up", "away_1up"), "win": ("home_win", "away_win")}
TEAM_WINDOW, MIN_HISTORY = 38, 10
FIRST_FIT_SEASON, FIRST_EVAL_SEASON, LIVE_FROM = "2015/16", "2017/18", "2024/25"
FIT_SHARE, BOOTSTRAP, SEED = 0.6, 2000, 20261029
ODDS = ["avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25"]


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _loss(p, y):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def team_rows(matches: pd.DataFrame, league: str, rho: float) -> pd.DataFrame:
    """Two rows per match (one per team) with both families' outcome and bookmaker probability."""
    matches = matches.dropna(subset=ODDS + ["home_goals", "home_led_at_any_point"])
    rows = []
    for m in matches.itertuples(index=False):
        fair = bookmaker_implied(*(getattr(m, c) for c in ODDS), rho)[0]
        for side, team, opp in (("home", m.home_team, m.away_team), ("away", m.away_team, m.home_team)):
            scored, conceded = (m.home_goals, m.away_goals) if side == "home" else (m.away_goals, m.home_goals)
            rows.append({"league": league, "match_id": str(m.match_id), "date": m.date, "season": m.season,
                         "side": side, "team": team, "opp": opp,
                         "lead_won": float(getattr(m, f"{side}_led_at_any_point")), "lead_p": fair[f"{side}_1up"],
                         "win_won": float(scored > conceded), "win_p": fair[f"{side}_win"]})
    return pd.DataFrame(rows)


def add_features(rows: pd.DataFrame) -> pd.DataFrame:
    """r_for / r_against per family from the previous TEAM_WINDOW matches only (no look-ahead)."""
    rows = rows.sort_values(["date", "match_id", "side"]).reset_index(drop=True)
    for family in FAMILIES:
        rows[f"{family}_res"] = rows[f"{family}_won"] - rows[f"{family}_p"]
        # residual of this team's opponent in the same match (what the team "allowed")
        other = rows.groupby(["league", "match_id"])[f"{family}_res"].transform("sum") - rows[f"{family}_res"]
        rows[f"{family}_allowed"] = other

        def past(column):
            return rows.groupby(["league", "team"])[column].transform(
                lambda s: s.shift(1).rolling(TEAM_WINDOW, min_periods=MIN_HISTORY).mean()).fillna(0.0)

        rows[f"{family}_r_for"] = past(f"{family}_res")
        allowed = past(f"{family}_allowed")
        key = rows.set_index(["league", "match_id", "team"]).index
        lookup = pd.Series(allowed.to_numpy(), index=key)
        rows[f"{family}_r_against"] = lookup.reindex(pd.MultiIndex.from_arrays(
            [rows.league, rows.match_id, rows.opp])).to_numpy()
    return rows


def _design(frame: pd.DataFrame, p: np.ndarray, family: str, with_team: bool) -> np.ndarray:
    columns = [_logit(p), (frame.side == "away").to_numpy(float)]
    if with_team:
        columns += [frame[f"{family}_r_for"].to_numpy(), frame[f"{family}_r_against"].to_numpy()]
    return sm.add_constant(np.column_stack(columns), has_constant="add")


def _paired(fit: pd.DataFrame, test: pd.DataFrame, fit_p, test_p, family: str):
    y_fit, y = fit[f"{family}_won"].to_numpy(), test[f"{family}_won"].to_numpy()
    base = sm.Logit(y_fit, _design(fit, fit_p, family, False)).fit(disp=0)
    chal = sm.Logit(y_fit, _design(fit, fit_p, family, True)).fit(disp=0)
    diff = _loss(base.predict(_design(test, test_p, family, False)), y) - _loss(chal.predict(_design(test, test_p, family, True)), y)
    return diff, chal.params


def _ci(diff: np.ndarray, days: np.ndarray) -> tuple[float, float]:
    frame = pd.DataFrame({"d": diff, "day": days})
    grouped = frame.groupby("day").d
    sums, counts = grouped.sum().to_numpy(), grouped.size().to_numpy()
    picks = np.random.default_rng(SEED).integers(0, len(sums), size=(BOOTSTRAP, len(sums)))
    low, high = np.percentile(sums[picks].sum(axis=1) / counts[picks].sum(axis=1), [2.5, 97.5])
    return float(low), float(high)


def primary(rows: pd.DataFrame, family: str) -> dict:
    seasons = sorted(rows.season.unique())
    diffs, frames, params = [], [], {}
    for season in [s for s in seasons if s >= FIRST_EVAL_SEASON]:
        fit = rows[(rows.season >= FIRST_FIT_SEASON) & (rows.season < season)]
        test = rows[rows.season == season]
        diff, coef = _paired(fit, test, fit[f"{family}_p"], test[f"{family}_p"], family)
        diffs.append(diff)
        frames.append(test.assign(diff=diff))
        params[season] = [round(float(c), 3) for c in coef]
    scored = pd.concat(frames, ignore_index=True)
    low, high = _ci(scored["diff"].to_numpy(), scored.date.dt.normalize().to_numpy())
    per_league = {league: round(float(group["diff"].mean()), 5) for league, group in scored.groupby("league")}
    return {"legs": len(scored), "gain": float(scored["diff"].mean()), "ci": (low, high),
            "per_league": per_league, "coefficients": params}


def secondary(rows: pd.DataFrame, live: pd.DataFrame, family: str) -> dict:
    markets = FAMILIES[family]
    legs = live[live.market.isin(markets)].copy()
    legs["side"] = np.where(legs.market == markets[0], "home", "away")
    legs = legs.merge(rows[["league", "match_id", "side", f"{family}_won", f"{family}_r_for", f"{family}_r_against"]],
                      on=["league", "match_id", "side"], how="inner", validate="one_to_one")
    legs[f"{family}_won"] = legs.won.astype(float)         # same outcome; the leg's own result is authoritative
    days = sorted(legs.date.dt.normalize().unique())
    fit_days = set(days[:int(len(days) * FIT_SHARE)])
    in_fit = legs.date.dt.normalize().isin(fit_days)
    fit, test = legs[in_fit], legs[~in_fit]
    diff, coef = _paired(fit, test, fit.live_p, test.live_p, family)
    low, high = _ci(diff, test.date.dt.normalize().to_numpy())
    return {"legs": len(test), "gain": float(diff.mean()), "ci": (low, high), "coefficients": [round(float(c), 3) for c in coef]}


def persistence(rows: pd.DataFrame, family: str) -> tuple[float, int]:
    """Correlation of a team's season residual (>= 30 matches) with its next season's."""
    season = rows.groupby(["league", "team", "season"])[f"{family}_res"].agg(["mean", "size"])
    season = season[season["size"] >= 30]["mean"].reset_index()
    order = {s: i for i, s in enumerate(sorted(rows.season.unique()))}
    season["k"] = season.season.map(order)
    nxt = season.assign(k=season.k - 1).rename(columns={"mean": "next"})
    pairs = season.merge(nxt[["league", "team", "k", "next"]], on=["league", "team", "k"])
    return float(np.corrcoef(pairs["mean"], pairs["next"])[0, 1]), len(pairs)


def live_legs() -> pd.DataFrame:
    from .market_gates import gate_column
    parts = []
    for league in LEAGUES:
        legs = pd.read_parquet(paths(league).accumulator_legs)      # all markets: the EPL weight is fitted on all
        column = gate_column(legs, "blended" if league == "EPL" else "market")
        legs = legs[legs.market.isin(sum(FAMILIES.values(), ()))]
        parts.append(legs.assign(league=league, match_id=legs.match_id.astype(str), live_p=legs[column]))
    return pd.concat(parts, ignore_index=True)[["league", "match_id", "date", "market", "won", "live_p"]]


def decide(first: dict, second: dict) -> str:
    return "USE" if first["ci"][0] > 0 and second["gain"] > 0 else "DO NOT USE"


def main() -> None:
    rows = add_features(pd.concat([team_rows(pd.read_parquet(paths(l).matches), l, league_rho(l)) for l in LEAGUES],
                                  ignore_index=True))
    live = live_legs()
    lines = ["# Team tendency study (PROJECT.md task 8, pre-registered 2026-10-29)", ""]
    for family in FAMILIES:
        first, second = primary(rows, family), secondary(rows, live, family)
        corr, n = persistence(rows, family)
        lines += [f"## {family}: {', '.join(FAMILIES[family])}", "",
                  f"- Primary (bookmaker price, seasons {FIRST_EVAL_SEASON}+): {first['legs']} legs, log loss gain "
                  f"{first['gain']:+.5f} (95% CI {first['ci'][0]:+.5f} to {first['ci'][1]:+.5f})",
                  f"- Per league gain: {first['per_league']}",
                  f"- Secondary (live probabilities, last 40% of days {LIVE_FROM}+): {second['legs']} legs, gain "
                  f"{second['gain']:+.5f} (95% CI {second['ci'][0]:+.5f} to {second['ci'][1]:+.5f})",
                  f"- Season-to-season persistence of a team's residual: r = {corr:.3f} ({n} team pairs)",
                  f"- Coefficients [const, logit p, away, r_for, r_against] by season: {first['coefficients']}",
                  f"- Secondary coefficients: {second['coefficients']}",
                  f"- **Decision: {decide(first, second)}**", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
