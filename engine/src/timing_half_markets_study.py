"""Task 20: Goal-timing and half markets backtest (2024/25+ primary and 2019/20-2023/24 replication).

Pre-registered in PROJECT.md (task 20), 2026-11-07, before any result.
- Timing markets (5 main leagues, settled from Understat goals.parquet after Task 19 PASS):
  `first_goal_home`, `first_goal_away`, `interval_10_home`, `interval_10_draw`, `interval_10_away`.
- Half markets (all 9 live leagues, settled from football-data HTHG/HTAG and FTHG/FTAG):
  `home_score_both_halves`, `away_score_both_halves`, `home_win_both_halves`, `away_win_both_halves`,
  `home_fh_over_0.5`, `away_fh_over_0.5`, `home_sh_over_0.5`, `away_sh_over_0.5`.
- Raw probability: `lam_home`, `lam_away` from `accumulators.bookmaker_implied` (league rho);
  first-half share `s` and 10-minute share `w` (goals with Understat `minute <= 9`, i.e., `< 10:00`)
  per league from EARLIER seasons only; each team's goals in a period ~ independent `Poisson(share * lambda)`;
  `first_goal_home = lam_home / (lam_home + lam_away) * (1 - exp(-(lam_home + lam_away)))`.
- Calibration: Platt (`LogisticRegression(C=1.0)` on `logit(raw)`) per league x market, walk-forward by season.
- Judgement: `market_gates.evaluate` unchanged (one-sided C1-C4, >= 300 legs, seed 20261029) with
  `bookmaker_probability = raw`, evaluated on `2024/25+` (primary) AND on `2019/20-2023/24` (replication).
  "Strong candidate" = PASS in both periods; otherwise stays out.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import poisson
from sklearn.linear_model import LogisticRegression

from .accumulators import bookmaker_implied
from .calibration import ENGINE_DIR
from .goal_minute_check import UNDERSTAT_10MIN_MAX_MINUTE, sort_understat_goals
from .half_markets_study import MAX_HALF_GOALS, _poisson_win_prob, load_league_matches as load_htft_matches
from .leagues import LEAGUES, paths
from .market_gates import SEED, evaluate
from .market_live import league_rho
from .new_markets_study import ODDS, _logit

REPORT_PATH = ENGINE_DIR / "reports" / "timing_half_markets_study.md"

MAIN_LEAGUES: tuple[str, ...] = ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1")
ALL_LEAGUES: tuple[str, ...] = tuple(LEAGUES.keys())

TIMING_MARKETS: tuple[str, ...] = (
    "first_goal_home",
    "first_goal_away",
    "interval_10_home",
    "interval_10_draw",
    "interval_10_away",
)
HALF_MARKETS: tuple[str, ...] = (
    "home_score_both_halves",
    "away_score_both_halves",
    "home_win_both_halves",
    "away_win_both_halves",
    "home_fh_over_0.5",
    "away_fh_over_0.5",
    "home_sh_over_0.5",
    "away_sh_over_0.5",
)

PRIMARY_FROM = "2024/25"
REPL_START = "2019/20"
REPL_END = "2023/24"


def timing_market_raw_probabilities(lam_home: float, lam_away: float, share_10: float) -> dict[str, float]:
    """Exact raw probabilities for first goal and 10-minute interval 1X2 from fixed lambdas and 10-min share w."""
    lam_total = lam_home + lam_away
    if lam_total <= 0.0:
        p_first_h = 0.0
        p_first_a = 0.0
    else:
        p_any_goal = 1.0 - float(np.exp(-lam_total))
        p_first_h = (lam_home / lam_total) * p_any_goal
        p_first_a = (lam_away / lam_total) * p_any_goal

    lam_10_h = share_10 * lam_home
    lam_10_a = share_10 * lam_away
    p_10_home = _poisson_win_prob(lam_10_h, lam_10_a)
    p_10_away = _poisson_win_prob(lam_10_a, lam_10_h)
    k = np.arange(MAX_HALF_GOALS + 1)
    p_10_draw = float(np.sum(poisson.pmf(k, lam_10_h) * poisson.pmf(k, lam_10_a)))

    return {
        "first_goal_home": float(np.clip(p_first_h, 1e-6, 1.0 - 1e-6)),
        "first_goal_away": float(np.clip(p_first_a, 1e-6, 1.0 - 1e-6)),
        "interval_10_home": float(np.clip(p_10_home, 1e-6, 1.0 - 1e-6)),
        "interval_10_draw": float(np.clip(p_10_draw, 1e-6, 1.0 - 1e-6)),
        "interval_10_away": float(np.clip(p_10_away, 1e-6, 1.0 - 1e-6)),
    }


def half_team_raw_probabilities(lam_home: float, lam_away: float, share_fh: float) -> dict[str, float]:
    """Exact raw probabilities for the 8 team-half markets from fixed lambdas and first-half share s."""
    lam_fh_h = share_fh * lam_home
    lam_fh_a = share_fh * lam_away
    lam_sh_h = (1.0 - share_fh) * lam_home
    lam_sh_a = (1.0 - share_fh) * lam_away

    p_h_fh_o05 = 1.0 - float(np.exp(-lam_fh_h))
    p_a_fh_o05 = 1.0 - float(np.exp(-lam_fh_a))
    p_h_sh_o05 = 1.0 - float(np.exp(-lam_sh_h))
    p_a_sh_o05 = 1.0 - float(np.exp(-lam_sh_a))

    p_h_win_fh = _poisson_win_prob(lam_fh_h, lam_fh_a)
    p_h_win_sh = _poisson_win_prob(lam_sh_h, lam_sh_a)
    p_a_win_fh = _poisson_win_prob(lam_fh_a, lam_fh_h)
    p_a_win_sh = _poisson_win_prob(lam_sh_a, lam_sh_h)

    raw = {
        "home_score_both_halves": p_h_fh_o05 * p_h_sh_o05,
        "away_score_both_halves": p_a_fh_o05 * p_a_sh_o05,
        "home_win_both_halves": p_h_win_fh * p_h_win_sh,
        "away_win_both_halves": p_a_win_fh * p_a_win_sh,
        "home_fh_over_0.5": p_h_fh_o05,
        "away_fh_over_0.5": p_a_fh_o05,
        "home_sh_over_0.5": p_h_sh_o05,
        "away_sh_over_0.5": p_a_sh_o05,
    }
    return {k: float(np.clip(v, 1e-6, 1.0 - 1e-6)) for k, v in raw.items()}


def half_team_outcomes(fthg: int, ftag: int, hthg: int, htag: int) -> dict[str, int]:
    """Actual binary outcomes for the 8 team-half markets from full-time and half-time scores."""
    sh_h = fthg - hthg
    sh_a = ftag - htag
    return {
        "home_score_both_halves": int(hthg >= 1 and sh_h >= 1),
        "away_score_both_halves": int(htag >= 1 and sh_a >= 1),
        "home_win_both_halves": int(hthg > htag and sh_h > sh_a),
        "away_win_both_halves": int(htag > hthg and sh_a > sh_h),
        "home_fh_over_0.5": int(hthg >= 1),
        "away_fh_over_0.5": int(htag >= 1),
        "home_sh_over_0.5": int(sh_h >= 1),
        "away_sh_over_0.5": int(sh_a >= 1),
    }


def derive_timing_outcomes_from_goals(goals: pd.DataFrame) -> dict[str, int] | None:
    """Derive first-goal and 10-minute (minute <= 9) outcomes from a match's Understat goals.

    Returns None if the earliest goal minute is tied between home and away (ambiguous first goal).
    """
    if goals.empty:
        return {
            "first_goal_home": 0,
            "first_goal_away": 0,
            "interval_10_home": 0,
            "interval_10_draw": 1,
            "interval_10_away": 0,
            "goals_10": 0,
        }
    ordered = sort_understat_goals(goals)
    min_minute = int(ordered["minute"].iloc[0])
    earliest_teams = set(ordered[ordered["minute"] == min_minute]["team"])
    if len(earliest_teams) > 1:
        return None
    first_team = str(ordered["team"].iloc[0])

    g10 = ordered[ordered["minute"] <= UNDERSTAT_10MIN_MAX_MINUTE]
    h10 = int((g10["team"] == "home").sum())
    a10 = int((g10["team"] == "away").sum())

    return {
        "first_goal_home": int(first_team == "home"),
        "first_goal_away": int(first_team == "away"),
        "interval_10_home": int(h10 > a10),
        "interval_10_draw": int(h10 == a10),
        "interval_10_away": int(a10 > h10),
        "goals_10": int(h10 + a10),
    }


def load_timing_matches(league_code: str) -> tuple[pd.DataFrame, dict[str, int]]:
    """Load 2014/15+ matches reconciled with Understat goals.parquet for one of the 5 main leagues."""
    lp = paths(LEAGUES[league_code])
    matches = pd.read_parquet(lp.matches)
    goals = pd.read_parquet(lp.goals)
    matches = matches[matches["season"] >= "2014/15"].copy()
    total_rows = len(matches)

    needed = ["date", "season", "home_team", "away_team", "home_goals", "away_goals", *ODDS]
    valid_odds = matches[needed].notna().all(axis=1)
    for col in ODDS:
        valid_odds &= matches[col] > 1.0

    g_counts = goals.groupby(["match_id", "team"]).size().unstack(fill_value=0)
    has_understat = ~matches["match_id"].astype(str).str.startswith("fd-")
    gh = matches["match_id"].map(g_counts.get("home", pd.Series(dtype=int))).fillna(0).astype(int)
    ga = matches["match_id"].map(g_counts.get("away", pd.Series(dtype=int))).fillna(0).astype(int)
    reconciled = has_understat & (gh == matches["home_goals"]) & (ga == matches["away_goals"])

    candidates = matches[valid_odds & reconciled].copy()
    candidates["date"] = pd.to_datetime(candidates["date"])
    candidates["home_goals"] = candidates["home_goals"].astype(int)
    candidates["away_goals"] = candidates["away_goals"].astype(int)

    relevant_goals = goals[goals["match_id"].isin(set(candidates["match_id"]))][["match_id", "minute", "team"]]
    by_match: dict[Any, dict[str, int] | None] = {}
    for mid, grp in relevant_goals.groupby("match_id", sort=False):
        by_match[mid] = derive_timing_outcomes_from_goals(grp)

    empty_outcome = derive_timing_outcomes_from_goals(pd.DataFrame(columns=["minute", "team"]))
    assert empty_outcome is not None

    outcomes_list: list[dict[str, int] | None] = []
    for mid, hg, ag in zip(candidates["match_id"], candidates["home_goals"], candidates["away_goals"]):
        if hg + ag == 0:
            outcomes_list.append(empty_outcome)
        else:
            outcomes_list.append(by_match.get(mid))

    keep_mask = [o is not None for o in outcomes_list]
    dropped_tied_first = int(sum(not k for k in keep_mask))
    kept = candidates[keep_mask].copy().reset_index(drop=True)
    kept_outcomes = [o for o in outcomes_list if o is not None]

    for col in (*TIMING_MARKETS, "goals_10"):
        kept[col] = [int(o[col]) for o in kept_outcomes]

    stats = {
        "total_rows": int(total_rows),
        "dropped_missing_odds": int((~valid_odds).sum()),
        "dropped_unreconciled_goals": int((valid_odds & ~reconciled).sum()),
        "dropped_tied_first_goal": dropped_tied_first,
        "kept_rows": int(len(kept)),
    }
    return kept, stats


def build_walkforward_half_legs(matches: pd.DataFrame, league: str, rho: float) -> tuple[pd.DataFrame, dict[str, float]]:
    """Build raw and walk-forward Platt-calibrated legs for the 8 team-half markets."""
    matches = matches.sort_values("date").reset_index(drop=True)
    if "lam_home" not in matches.columns or "lam_away" not in matches.columns:
        lambdas = [
            bookmaker_implied(*(getattr(m, c) for c in ODDS), rho)[1]
            for m in matches.itertuples(index=False)
        ]
        matches = matches.assign(
            lam_home=[x[0] for x in lambdas],
            lam_away=[x[1] for x in lambdas],
        )
    matches = matches.assign(
        fh_goals=matches.ht_home_goals + matches.ht_away_goals,
        ft_goals=matches.home_goals + matches.away_goals,
    )
    seasons = sorted(matches.season.unique())
    rows: list[dict[str, Any]] = []
    shares: dict[str, float] = {}
    for season in seasons[1:]:
        earlier = matches[matches.season < season]
        share_fh = float(earlier.fh_goals.sum() / earlier.ft_goals.sum())
        shares[season] = share_fh
        for m in matches[matches.season == season].itertuples(index=False):
            raw = half_team_raw_probabilities(float(m.lam_home), float(m.lam_away), share_fh)
            actual = half_team_outcomes(int(m.home_goals), int(m.away_goals), int(m.ht_home_goals), int(m.ht_away_goals))
            for market in HALF_MARKETS:
                rows.append(
                    {
                        "league": league,
                        "date": m.date,
                        "season": m.season,
                        "market": market,
                        "bookmaker_probability": raw[market],
                        "won": actual[market],
                    }
                )
    legs = pd.DataFrame(rows)
    legs["probability"] = np.nan
    cal_seasons = sorted(legs.season.unique())
    for season in cal_seasons[1:]:
        for market in HALF_MARKETS:
            past = legs[(legs.season < season) & (legs.market == market)]
            current = (legs.season == season) & (legs.market == market)
            if past["won"].nunique() < 2:
                continue
            model = LogisticRegression(C=1.0, max_iter=1000).fit(
                _logit(past.bookmaker_probability).reshape(-1, 1), past.won
            )
            legs.loc[current, "probability"] = model.predict_proba(
                _logit(legs.loc[current, "bookmaker_probability"]).reshape(-1, 1)
            )[:, 1]
    return legs, shares


def build_walkforward_timing_legs(matches: pd.DataFrame, league: str, rho: float) -> tuple[pd.DataFrame, dict[str, float]]:
    """Build raw and walk-forward Platt-calibrated legs for the 5 goal-timing markets."""
    matches = matches.sort_values("date").reset_index(drop=True)
    if "lam_home" not in matches.columns or "lam_away" not in matches.columns:
        lambdas = [
            bookmaker_implied(*(getattr(m, c) for c in ODDS), rho)[1]
            for m in matches.itertuples(index=False)
        ]
        matches = matches.assign(
            lam_home=[x[0] for x in lambdas],
            lam_away=[x[1] for x in lambdas],
        )
    matches = matches.assign(ft_goals=matches.home_goals + matches.away_goals)
    seasons = sorted(matches.season.unique())
    rows: list[dict[str, Any]] = []
    shares_10: dict[str, float] = {}
    for season in seasons[1:]:
        earlier = matches[matches.season < season]
        share_10 = float(earlier.goals_10.sum() / earlier.ft_goals.sum())
        shares_10[season] = share_10
        for m in matches[matches.season == season].itertuples(index=False):
            raw = timing_market_raw_probabilities(float(m.lam_home), float(m.lam_away), share_10)
            for market in TIMING_MARKETS:
                rows.append(
                    {
                        "league": league,
                        "date": m.date,
                        "season": m.season,
                        "market": market,
                        "bookmaker_probability": raw[market],
                        "won": int(getattr(m, market)),
                    }
                )
    legs = pd.DataFrame(rows)
    legs["probability"] = np.nan
    cal_seasons = sorted(legs.season.unique())
    for season in cal_seasons[1:]:
        for market in TIMING_MARKETS:
            past = legs[(legs.season < season) & (legs.market == market)]
            current = (legs.season == season) & (legs.market == market)
            if past["won"].nunique() < 2:
                continue
            model = LogisticRegression(C=1.0, max_iter=1000).fit(
                _logit(past.bookmaker_probability).reshape(-1, 1), past.won
            )
            legs.loc[current, "probability"] = model.predict_proba(
                _logit(legs.loc[current, "bookmaker_probability"]).reshape(-1, 1)
            )[:, 1]
    return legs, shares_10


def _evaluate_period(
    legs: pd.DataFrame,
    league: str,
    markets: tuple[str, ...],
    rng_primary: np.random.Generator,
    rng_repl: np.random.Generator,
) -> list[dict[str, Any]]:
    primary_df = legs[legs["season"] >= PRIMARY_FROM].dropna(subset=["probability"])
    repl_df = legs[(legs["season"] >= REPL_START) & (legs["season"] <= REPL_END)].dropna(subset=["probability"])

    rows: list[dict[str, Any]] = []
    for market in markets:
        r_prim = evaluate(league, market, primary_df, "probability", rng_primary)
        r_repl = evaluate(league, market, repl_df, "probability", rng_repl)

        m_prim = primary_df[primary_df["market"] == market]
        m_repl = repl_df[repl_df["market"] == market]
        fair_prim = float((1.0 / m_prim["probability"]).median()) if len(m_prim) else float("nan")
        fair_repl = float((1.0 / m_repl["probability"]).median()) if len(m_repl) else float("nan")

        strong = r_prim["status"] == "PASS" and r_repl["status"] == "PASS"
        verdict = "Strong candidate (pending real Betpawa prices)" if strong else "stays out"
        rows.append(
            {
                "league": league,
                "market": market,
                "primary_2024_25_plus": {
                    **r_prim,
                    "fair_odds": round(fair_prim, 2) if np.isfinite(fair_prim) else None,
                },
                "replication_2019_20_to_2023_24": {
                    **r_repl,
                    "fair_odds": round(fair_repl, 2) if np.isfinite(fair_repl) else None,
                },
                "strong_candidate": strong,
                "verdict": verdict,
            }
        )
    return rows


def run_study() -> dict[str, Any]:
    rng_primary = np.random.default_rng(SEED)
    rng_repl = np.random.default_rng(SEED)

    timing_results: list[dict[str, Any]] = []
    timing_coverage: dict[str, Any] = {}
    for code in MAIN_LEAGUES:
        rho = league_rho(code)
        t_matches, stats = load_timing_matches(code)
        t_legs, shares_10 = build_walkforward_timing_legs(t_matches, code, rho)
        timing_coverage[code] = {
            **stats,
            "share_10_2019_20": round(shares_10.get("2019/20", float("nan")), 4),
            "share_10_2024_25": round(shares_10.get("2024/25", float("nan")), 4),
            "share_10_2026_27": round(shares_10.get("2026/27", float("nan")), 4),
        }
        timing_results.extend(_evaluate_period(t_legs, code, TIMING_MARKETS, rng_primary, rng_repl))

    half_results: list[dict[str, Any]] = []
    half_coverage: dict[str, Any] = {}
    for code in ALL_LEAGUES:
        rho = league_rho(code)
        h_matches = load_htft_matches(code)
        h_legs, shares_fh = build_walkforward_half_legs(h_matches, code, rho)
        half_coverage[code] = {
            "kept_rows": int(len(h_matches)),
            "share_fh_2019_20": round(shares_fh.get("2019/20", float("nan")), 4),
            "share_fh_2024_25": round(shares_fh.get("2024/25", float("nan")), 4),
            "share_fh_2026_27": round(shares_fh.get("2026/27", float("nan")), 4),
        }
        half_results.extend(_evaluate_period(h_legs, code, HALF_MARKETS, rng_primary, rng_repl))

    return {
        "timing_results": timing_results,
        "timing_coverage": timing_coverage,
        "half_results": half_results,
        "half_coverage": half_coverage,
    }


def _format_table_rows(rows: list[dict[str, Any]]) -> list[str]:
    out = [
        "| League | Market | 2024/25+ n | 2024/25+ Said | 2024/25+ Won | Fair odds | 2024/25+ Gate | 2019/20-23/24 n | 2019/20-23/24 Said | 2019/20-23/24 Won | 2019/20-23/24 Gate | Verdict |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|",
    ]
    for r in rows:
        p = r["primary_2024_25_plus"]
        rep = r["replication_2019_20_to_2023_24"]
        fo = f"{p['fair_odds']:.2f}" if p["fair_odds"] is not None else "—"
        out.append(
            f"| {r['league']} | {r['market']} | {p['n']} | {p.get('mean_p', float('nan')):.4f} | "
            f"{p.get('actual', float('nan')):.4f} | {fo} | **{p['status']}** | "
            f"{rep['n']} | {rep.get('mean_p', float('nan')):.4f} | {rep.get('actual', float('nan')):.4f} | "
            f"**{rep['status']}** | {r['verdict']} |"
        )
    return out


def _summarize_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    total = len(rows)
    p_pass = sum(r["primary_2024_25_plus"]["status"] == "PASS" for r in rows)
    p_fail = sum(r["primary_2024_25_plus"]["status"] == "FAIL" for r in rows)
    p_ins = sum(r["primary_2024_25_plus"]["status"] == "INSUFFICIENT" for r in rows)
    r_pass = sum(r["replication_2019_20_to_2023_24"]["status"] == "PASS" for r in rows)
    r_fail = sum(r["replication_2019_20_to_2023_24"]["status"] == "FAIL" for r in rows)
    r_ins = sum(r["replication_2019_20_to_2023_24"]["status"] == "INSUFFICIENT" for r in rows)
    strong = sum(bool(r["strong_candidate"]) for r in rows)
    return {
        "total": total,
        "p_pass": p_pass,
        "p_fail": p_fail,
        "p_ins": p_ins,
        "r_pass": r_pass,
        "r_fail": r_fail,
        "r_ins": r_ins,
        "strong": strong,
    }


def write_report(data: dict[str, Any] | None = None) -> Path:
    if data is None:
        data = run_study()
    t_res = data["timing_results"]
    h_res = data["half_results"]
    all_res = [*t_res, *h_res]

    tc = _summarize_counts(t_res)
    hc = _summarize_counts(h_res)
    ac = _summarize_counts(all_res)

    lines = [
        "# Goal-timing and team-half markets backtest (PROJECT.md task 20, pre-registered 2026-11-07)",
        "",
        "## Pre-registered design and Task 19 prerequisite",
        "- **Task 19 gate**: **PASS** (`332/332 = 100.00%` `< 10:00` agreement with `Understat minute <= 9`, `73/73 = 100.00%` goal-order agreement when `goals.parquet` is sorted by `minute`). Therefore all 5 timing markets are evaluated on the 5 main leagues.",
        "- **Raw probability model**: From `accumulators.bookmaker_implied` lambdas (`league_rho(league)`):",
        "  - First-half share `s` and 10-minute share `w` (fraction of goals with `Understat minute <= 9`) per league from **earlier seasons only** (`< season`).",
        "  - Team goals in a period ~ independent `Poisson(share * lambda)`.",
        "  - `first_goal_home = lam_home / (lam_home + lam_away) * (1 - exp(-(lam_home + lam_away)))` (and mirror for `first_goal_away`).",
        "- **Walk-forward calibration & gates**: Platt (`LogisticRegression(C=1.0)` on `logit(raw)`) fitted per league x market on earlier seasons only; judged with `market_gates.evaluate` unchanged (`bookmaker_probability = raw`, one-sided C1-C4, >= 300 legs, `SEED = 20261029`) on **2024/25+** (primary) and **2019/20-2023/24** (replication). **Strong candidate** = `PASS` in both periods.",
        "",
        "## Overall Summary",
        f"- **Timing markets (5 main leagues x 5 markets = {tc['total']} pairs)**: Primary `2024/25+` **{tc['p_pass']} PASS / {tc['p_fail']} FAIL" + (f" / {tc['p_ins']} INSUFFICIENT" if tc['p_ins'] else "") + f"**; Replication `2019/20-2023/24` **{tc['r_pass']} PASS / {tc['r_fail']} FAIL" + (f" / {tc['r_ins']} INSUFFICIENT" if tc['r_ins'] else "") + f"**; Strong candidates (`PASS` in both): **{tc['strong']} / {tc['total']}**.",
        f"- **Team-half markets (9 live leagues x 8 markets = {hc['total']} pairs)**: Primary `2024/25+` **{hc['p_pass']} PASS / {hc['p_fail']} FAIL" + (f" / {hc['p_ins']} INSUFFICIENT" if hc['p_ins'] else "") + f"**; Replication `2019/20-2023/24` **{hc['r_pass']} PASS / {hc['r_fail']} FAIL" + (f" / {hc['r_ins']} INSUFFICIENT" if hc['r_ins'] else "") + f"**; Strong candidates (`PASS` in both): **{hc['strong']} / {hc['total']}**.",
        f"- **Combined ({ac['total']} pairs)**: Primary **{ac['p_pass']} PASS / {ac['p_fail']} FAIL**; Replication **{ac['r_pass']} PASS / {ac['r_fail']} FAIL**; Strong candidates (`PASS` in both): **{ac['strong']} / {ac['total']}**.",
        "",
        "## Part 1 — Goal-Timing Markets (5 Main Leagues, Understat `goals.parquet`)",
        *_format_table_rows(t_res),
        "",
        "## Part 2 — Team-Half Markets (All 9 Live Leagues, `HTHG`/`HTAG` & `FTHG`/`FTAG`)",
        *_format_table_rows(h_res),
        "",
        "## Coverage and Walk-Forward Shares (`w` and `s`)",
        "### Timing markets coverage & 10-minute share `w`",
        "```json",
        json.dumps(data["timing_coverage"], indent=2),
        "```",
        "",
        "### Team-half markets coverage & first-half share `s`",
        "```json",
        json.dumps(data["half_coverage"], indent=2),
        "```",
        "",
        "## Full Gate Details",
        "```json",
        json.dumps(all_res, indent=2, default=str),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


if __name__ == "__main__":
    out = write_report()
    print(f"Wrote {out}")
