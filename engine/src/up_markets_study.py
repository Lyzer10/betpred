"""Task 17 study: Double Chance 1UP and 1X2 2UP across the five main leagues.

Research backtest only. Uses football-data average odds and Understat goal
minutes in engine/data/processed/<league>/{matches,goals}.parquet from 2014/15
onwards. Does not touch live predictions, calibrations, gates or slips.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .accumulators import PRIORS, bookmaker_implied
from .dixon_coles import score_matrix
from .goal_timing import MAX_GOALS
from .calibration import TEST_SEASONS, fit_calibrator
from .leagues import LEAGUES, paths
from .market_gates import SEED, evaluate
from .market_live import league_rho

ENGINE_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = ENGINE_DIR / "reports" / "up_markets_study.md"
MAIN_LEAGUES = ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1")
MARKETS = (
    "dc1up_1x",
    "dc1up_x2",
    "dc1up_12",
    "home_2up",
    "away_2up",
)
ODDS_COLS = ["avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25"]


def enumerate_score_orders(h: int, a: int) -> dict:
    """Explicitly enumerate every goal order of final score (h, a) and count lead states."""
    if h < 0 or a < 0:
        raise ValueError("Goal counts must be non-negative")
    total = h + a
    if total == 0:
        return {
            "score": f"{h}-{a}",
            "total_orders": 1,
            "home_led_orders": 0,
            "away_led_orders": 0,
            "home_2up_ever_orders": 0,
            "away_2up_ever_orders": 0,
            "p_home_led_ever": 0.0,
            "p_away_led_ever": 0.0,
            "p_home_2up_ever": 0.0,
            "p_away_2up_ever": 0.0,
            "home_2up_weight": 0.0,
            "away_2up_weight": 0.0,
            "orders": [{"order": "", "running_diff": [], "max_home_lead": 0, "home_2up_ever": False}],
        }
    orders_detail = []
    home_led_hits = 0
    away_led_hits = 0
    home_2up_hits = 0
    away_2up_hits = 0
    count = 0
    for home_positions in itertools.combinations(range(total), h):
        count += 1
        home_set = set(home_positions)
        diff = 0
        max_lead = 0
        min_lead = 0
        running = []
        chars = []
        for idx in range(total):
            if idx in home_set:
                diff += 1
                chars.append("H")
            else:
                diff -= 1
                chars.append("A")
            running.append(diff)
            if diff > max_lead:
                max_lead = diff
            if diff < min_lead:
                min_lead = diff
        if max_lead >= 1:
            home_led_hits += 1
        if min_lead <= -1:
            away_led_hits += 1
        if max_lead >= 2:
            home_2up_hits += 1
        if min_lead <= -2:
            away_2up_hits += 1
        if total <= 6:
            orders_detail.append({
                "order": "".join(chars),
                "running_diff": running,
                "max_home_lead": max_lead,
                "home_2up_ever": max_lead >= 2,
            })
    p_home_2up_ever = home_2up_hits / count
    p_away_2up_ever = away_2up_hits / count
    return {
        "score": f"{h}-{a}",
        "total_orders": count,
        "home_led_orders": home_led_hits,
        "away_led_orders": away_led_hits,
        "home_2up_ever_orders": home_2up_hits,
        "away_2up_ever_orders": away_2up_hits,
        "p_home_led_ever": home_led_hits / count,
        "p_away_led_ever": away_led_hits / count,
        "p_home_2up_ever": p_home_2up_ever,
        "p_away_2up_ever": p_away_2up_ever,
        "home_2up_weight": 1.0 if h > a else p_home_2up_ever,
        "away_2up_weight": 1.0 if a > h else p_away_2up_ever,
        "orders": orders_detail,
    }


def _lead_reached_2_prob(h: int, a: int) -> float:
    """Exact fraction of goal orders for score (h, a) where home ever leads by >= 2."""
    total = h + a
    if h < 2:
        return 0.0
    if h - a >= 2:
        return 1.0
    hits = 0
    count = 0
    for home_positions in itertools.combinations(range(total), h):
        count += 1
        for idx, pos in enumerate(home_positions):
            if 2 * idx + 1 - pos >= 2:
                hits += 1
                break
    return hits / count


def build_score_weight_grids(max_goals: int = MAX_GOALS) -> dict[str, np.ndarray]:
    """Build exact (max_goals+1) x (max_goals+1) score weight grids for DC 1UP and 2UP."""
    size = max_goals + 1
    h, a = np.meshgrid(np.arange(size), np.arange(size), indexing="ij")
    home_1up_ever = np.where(h > a, 1.0, h / (a + 1))
    away_1up_ever = np.where(a > h, 1.0, a / (h + 1))

    home_2up_ever = np.zeros((size, size), dtype=float)
    for hi in range(size):
        for ai in range(size):
            home_2up_ever[hi, ai] = _lead_reached_2_prob(hi, ai)
    away_2up_ever = home_2up_ever.T.copy()

    return {
        "home_1up_ever": home_1up_ever,
        "away_1up_ever": away_1up_ever,
        "home_2up_ever": home_2up_ever,
        "away_2up_ever": away_2up_ever,
        "dc1up_1x": np.where(h >= a, 1.0, home_1up_ever),
        "dc1up_x2": np.where(a >= h, 1.0, away_1up_ever),
        "dc1up_12": np.where((h != a) | ((h + a) > 0), 1.0, 0.0),
        "home_2up": np.where(h > a, 1.0, home_2up_ever),
        "away_2up": np.where(a > h, 1.0, away_2up_ever),
    }


SCORE_WEIGHTS = build_score_weight_grids(MAX_GOALS)


def raw_up_probabilities_from_matrix(matrix: np.ndarray) -> dict[str, float]:
    """Compute raw DC 1UP and 2UP probabilities from a (MAX_GOALS+1)x(MAX_GOALS+1) score matrix."""
    out = {}
    for market in MARKETS:
        val = float(np.sum(matrix * SCORE_WEIGHTS[market]))
        out[market] = float(np.clip(val, 1e-6, 1.0 - 1e-6))
    return out


def derive_up_goal_states(goals: pd.DataFrame) -> tuple[bool, bool, bool, bool]:
    """Derive (home_led_ever, away_led_ever, home_2up_ever, away_2up_ever) in event order."""
    if goals.empty:
        return False, False, False, False
    ordered = goals.reset_index().sort_values(["minute", "index"], kind="stable")
    home = away = 0
    home_led = away_led = False
    home_2up = away_2up = False
    for team in ordered["team"]:
        if team == "home":
            home += 1
        elif team == "away":
            away += 1
        else:
            raise ValueError(f"Unexpected goal team: {team!r}")
        diff = home - away
        if diff >= 1:
            home_led = True
        if diff <= -1:
            away_led = True
        if diff >= 2:
            home_2up = True
        if diff <= -2:
            away_2up = True
    return home_led, away_led, home_2up, away_2up


def add_up_actuals(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute binary outcomes for DC 1UP and 2UP from goal-state columns and final scores."""
    out = frame.copy()
    hg = out["home_goals"].to_numpy(int)
    ag = out["away_goals"].to_numpy(int)
    h_led = out["home_led_ever"].to_numpy(bool)
    a_led = out["away_led_ever"].to_numpy(bool)
    h_2up = out["home_2up_ever"].to_numpy(bool)
    a_2up = out["away_2up_ever"].to_numpy(bool)

    out["actual_dc1up_1x"] = (h_led | (hg >= ag)).astype(int)
    out["actual_dc1up_x2"] = (a_led | (ag >= hg)).astype(int)
    out["actual_dc1up_12"] = (h_led | a_led | (hg != ag)).astype(int)
    out["actual_home_2up"] = (h_2up | (hg > ag)).astype(int)
    out["actual_away_2up"] = (a_2up | (ag > hg)).astype(int)
    return out


def load_league_matches(code: str) -> tuple[pd.DataFrame, dict]:
    """Load reconciled matches and goal-minute states for one of the five main leagues."""
    league = LEAGUES[code]
    lp = paths(league)
    matches = pd.read_parquet(lp.matches)
    goals = pd.read_parquet(lp.goals)
    matches = matches[matches["season"] >= "2014/15"].copy()
    total_rows = len(matches)

    needed = ["date", "season", "home_team", "away_team", "home_goals", "away_goals", *ODDS_COLS]
    valid_odds = matches[needed].notna().all(axis=1)
    for col in ODDS_COLS:
        valid_odds &= matches[col] > 1.0

    g_counts = goals.groupby(["match_id", "team"]).size().unstack(fill_value=0)
    has_understat = ~matches["match_id"].astype(str).str.startswith("fd-")
    gh = matches["match_id"].map(g_counts.get("home", pd.Series(dtype=int))).fillna(0).astype(int)
    ga = matches["match_id"].map(g_counts.get("away", pd.Series(dtype=int))).fillna(0).astype(int)
    reconciled = has_understat & (gh == matches["home_goals"]) & (ga == matches["away_goals"])

    kept = matches[valid_odds & reconciled].copy()
    kept["date"] = pd.to_datetime(kept["date"])
    kept["home_goals"] = kept["home_goals"].astype(int)
    kept["away_goals"] = kept["away_goals"].astype(int)

    relevant_goals = goals[goals["match_id"].isin(set(kept["match_id"]))][["match_id", "minute", "team"]]
    states = relevant_goals.groupby("match_id", sort=False).apply(
        derive_up_goal_states, include_groups=False
    ).to_dict()
    derived = kept["match_id"].map(lambda mid: states.get(mid, (False, False, False, False)))
    kept["home_led_ever"] = derived.map(lambda v: v[0]).astype(bool)
    kept["away_led_ever"] = derived.map(lambda v: v[1]).astype(bool)
    kept["home_2up_ever"] = derived.map(lambda v: v[2]).astype(bool)
    kept["away_2up_ever"] = derived.map(lambda v: v[3]).astype(bool)

    stats = {
        "total_rows": int(total_rows),
        "dropped_missing_odds": int((~valid_odds).sum()),
        "dropped_unreconciled_goals": int((valid_odds & ~reconciled).sum()),
        "kept_rows": int(len(kept)),
    }
    return add_up_actuals(kept.sort_values("date").reset_index(drop=True)), stats


def add_raw_probabilities(frame: pd.DataFrame, rho: float) -> pd.DataFrame:
    """Compute raw DC 1UP and 2UP probabilities from bookmaker_implied score matrix."""
    out = frame.copy()
    rows = []
    for m in out.itertuples(index=False):
        _, _, matrix = bookmaker_implied(*(getattr(m, c) for c in ODDS_COLS), rho)
        probs = raw_up_probabilities_from_matrix(matrix)
        rows.append({f"raw_{mkt}": probs[mkt] for mkt in MARKETS})
    return pd.concat([out.reset_index(drop=True), pd.DataFrame(rows)], axis=1)


def walk_forward_platt(frame: pd.DataFrame) -> pd.DataFrame:
    """Fit Platt on earlier seasons only; build test-season (2024/25+) leg table."""
    seasons = sorted(frame["season"].unique())
    parts = []
    for idx, season in enumerate(seasons):
        if idx == 0 or season not in TEST_SEASONS:
            continue
        prior = frame[frame["season"].isin(seasons[:idx])]
        fold = frame[frame["season"] == season].copy()
        for market in MARKETS:
            raw_col = f"raw_{market}"
            act_col = f"actual_{market}"
            cal = fit_calibrator(prior[raw_col], prior[act_col], "platt")
            p_cal = np.clip(cal.predict(fold[raw_col]), 1e-6, 1.0 - 1e-6)
            for row, p_val, b_val, won in zip(
                fold.itertuples(index=False),
                p_cal,
                fold[raw_col].to_numpy(float),
                fold[act_col].to_numpy(int),
            ):
                parts.append({
                    "match_id": f"{row.season}:{row.date.strftime('%Y-%m-%d')}:{row.home_team}:{row.away_team}",
                    "date": row.date,
                    "season": row.season,
                    "home_team": row.home_team,
                    "away_team": row.away_team,
                    "market": market,
                    "probability": float(p_val),
                    "market_probability": float(p_val),
                    "bookmaker_probability": float(b_val),
                    "won": int(won),
                })
    return pd.DataFrame(parts)


def run_study() -> tuple[list[dict], dict[str, dict], dict[str, dict]]:
    results: list[dict] = []
    coverage: dict[str, dict] = {}
    hand_checks = {
        f"{h}-{a}": enumerate_score_orders(h, a)
        for h, a in ((1, 0), (2, 1), (3, 1), (1, 3), (2, 2), (2, 3), (3, 3))
    }
    rng = np.random.default_rng(SEED)
    for code in MAIN_LEAGUES:
        rho = league_rho(code)
        df, cov = load_league_matches(code)
        coverage[code] = cov
        df = add_raw_probabilities(df, rho)
        legs = walk_forward_platt(df)
        for market in MARKETS:
            sub = legs[legs["market"] == market].copy()
            res = evaluate(code, market, sub, "probability", rng)
            fair_odds = float(np.median(1.0 / sub["probability"].to_numpy(float)))
            eligibility = (
                "eligible pending real Betpawa prices"
                if res["status"] == "PASS"
                else "stays out"
            )
            results.append({
                **res,
                "fair_odds": round(fair_odds, 2),
                "eligibility": eligibility,
            })
    return results, coverage, hand_checks


def write_report(
    results: list[dict] | None = None,
    coverage: dict[str, dict] | None = None,
    hand_checks: dict[str, dict] | None = None,
) -> Path:
    if results is None or coverage is None or hand_checks is None:
        results, coverage, hand_checks = run_study()
    lines = [
        "# Double Chance 1UP and 1X2 2UP study (PROJECT.md task 17, pre-registered 2026-11-07)",
        "",
        "Five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`), seasons 2014/15 onwards (`matches.parquet` and `goals.parquet`).",
        "Matches missing average odds or failing exact goal-count reconciliation with `goals.parquet` are dropped (never filled).",
        "",
        "## Settlement definitions confirmed from real Betpawa events (Part A & Task 17 correction)",
        "- `dc1up_1x`: wins if the home team led at any point (`home - away >= 1`) OR full-time result is home win or draw (`home >= away`).",
        "- `dc1up_x2`: wins if the away team led at any point (`away - home >= 1`) OR full-time result is away win or draw (`away >= home`).",
        "- `dc1up_12`: wins if either team led at any point OR full-time result is not a draw (equivalently, `home + away > 0`).",
        "- `home_2up`: wins if the home team was ever two goals ahead (`home - away >= 2`) OR the home team won at full time (`home > away`).",
        "- `away_2up`: wins if the away team was ever two goals ahead (`away - home >= 2`) OR the away team won at full time (`away > home`).",
        "",
        "### Real Betpawa price inequality verification across all 9 leagues (fetched 2026-11-07)",
        "| League | Event ID | Match | 1X2 `1` / `2` | 2UP `1` / `2` | DC `1X` / `X2` / `12` | DC 1UP `1X` / `X2` / `12` |",
        "|---|---|---|---|---|---|---|",
        "| EPL | 38945042 | Arsenal FC - Hull City | 1.16 / 19.96 | 1.14 / 19.86 | 1.01 / 4.82 / 1.10 | susp (0.0) / 3.47 / susp (0.0) |",
        "| LALIGA | 37360154 | Espanyol Barcelona - RC Deportivo de A Coruna | 2.58 / 3.00 | 2.49 / 2.89 | 1.41 / 1.53 / 1.35 | 1.30 / 1.38 / 1.05 |",
        "| SERIEA | 38292840 | Torino FC - US Lecce | 1.82 / 4.77 | 1.77 / 4.57 | 1.21 / 1.99 / 1.29 | 1.16 / 1.66 / 1.03 |",
        "| BUNDES | 38336446 | SC Paderborn 07 - Eintracht Frankfurt | 2.87 / 2.42 | 2.70 / 2.29 | 1.58 / 1.44 / 1.29 | 1.38 / 1.29 / 1.01 |",
        "| LIGUE1 | 38916210 | AJ Auxerre - Paris FC | 4.76 / 1.76 | 4.54 / 1.71 | 2.09 / 1.20 / 1.26 | 1.70 / 1.15 / 1.03 |",
        "| EREDIV | 38395807 | Fortuna Sittard - SC Telstar | 2.15 / 3.53 | 2.07 / 3.35 | 1.31 / 1.69 / 1.29 | 1.20 / 1.44 / 1.02 |",
        "| JUPILER | 38366400 | KVC Westerlo - Royal Charleroi SC | 3.09 / 2.30 | 2.92 / 2.20 | 1.63 / 1.39 / 1.29 | 1.42 / 1.26 / 1.02 |",
        "| PRIMEIRA | 38916889 | Nacional da Madeira - Academico de Viseu FC | 3.11 / 2.50 | 3.01 / 2.41 | 1.56 / 1.39 / 1.33 | 1.40 / 1.29 / 1.03 |",
        "| SUPERLIG | 37359120 | Goztepe Izmir - Istanbul Basaksehir | 2.03 / 3.75 | 1.96 / 3.55 | 1.29 / 1.78 / 1.27 | 1.19 / 1.50 / 1.03 |",
        "",
        "## Exact goal-order enumeration checks on small scores",
        "| Score (h-a) | Total orders | Orders reaching +2 (`P(lead >= 2 given score)`) | `home_2up` weight `[1 if h > a else P(lead >= 2 given score)]` | Enumerated orders (running `home - away`) |",
        "|---|---:|---:|---:|---|",
    ]
    for score_key, info in hand_checks.items():
        ord_str = "; ".join(
            f"`{o['order'] or 'none'}` ({o['running_diff']}, >=2: {o['home_2up_ever']})"
            for o in info["orders"][:6]
        )
        if len(info["orders"]) > 6:
            ord_str += f"; ... ({info['total_orders']} total)"
        lines.append(
            f"| {score_key} | {info['total_orders']} | "
            f"{info['home_2up_ever_orders']}/{info['total_orders']} ({info['p_home_2up_ever']:.4f}) | "
            f"{info['home_2up_weight']:.4f} | {ord_str} |"
        )

    lines += [
        "",
        "## Walk-forward evaluation on 2024/25+ (`market_gates.evaluate` unchanged)",
        "| League | Market | n | Said | Won | Fair odds | Gates | Eligibility |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['league']} | {r['market']} | {r['n']} | {r['mean_p']:.4f} | "
            f"{r['actual']:.4f} | {r['fair_odds']:.2f} | **{r['status']}** | {r['eligibility']} |"
        )
    passed = sum(r["status"] == "PASS" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)
    insuff = sum(r["status"] == "INSUFFICIENT" for r in results)
    lines += [
        "",
        f"Summary: **{passed} PASS / {failed} FAIL" + (f" / {insuff} INSUFFICIENT" if insuff else "") + f"** across {len(results)} league x market pairs.",
        "",
        "Match reconciliation coverage by league:",
        "```json",
        json.dumps(coverage, indent=2),
        "```",
        "",
        "Gate details:",
        "```json",
        json.dumps(results, indent=2),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


if __name__ == "__main__":
    print(f"Wrote {write_report()}")
