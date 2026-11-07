"""Task 21: Replication of Tasks 16 and 17 on 2019/20-2023/24.

Pre-registered in PROJECT.md (task 21), 2026-11-07, before any result.
- Re-judges Task 16 (9 leagues x 6 half markets = 54 pairs) and Task 17 (5 main leagues x 5 UP
  markets = 25 pairs) on `2019/20-2023/24` with the exact same code and rules:
  each season calibrated on earlier seasons only with `LogisticRegression(C=1.0)` on `logit(raw)`,
  judged with `market_gates.evaluate` unchanged (`bookmaker_probability = raw`, `SEED = 20261029`).
- Reports `PASS`/`FAIL` per pair across both periods (`2024/25+` and `2019/20-2023/24`);
  `"Strong candidate"` = `PASS` in both periods. Does not alter `reports/half_markets_study.md` or
  `reports/up_markets_study.md`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .calibration import ENGINE_DIR
from .half_markets_study import (
    JUDGED_FROM as T16_JUDGED_FROM,
    MARKETS as T16_MARKETS,
    build_league_legs as build_t16_legs,
    load_league_matches as load_t16_matches,
)
from .leagues import LEAGUES
from .market_gates import SEED, evaluate
from .market_live import league_rho
from .new_markets_study import _logit
from .up_markets_study import (
    MAIN_LEAGUES as T17_LEAGUES,
    MARKETS as T17_MARKETS,
    add_raw_probabilities as add_t17_raw_probabilities,
    load_league_matches as load_t17_matches,
    walk_forward_platt as walk_forward_t17_primary,
)

REPORT_PATH = ENGINE_DIR / "reports" / "tasks_16_17_replication.md"
REPL_SEASONS: tuple[str, ...] = ("2019/20", "2020/21", "2021/22", "2022/23", "2023/24")


def walk_forward_t17_seasons(frame: pd.DataFrame, target_seasons: tuple[str, ...] = REPL_SEASONS) -> pd.DataFrame:
    """Exact Task 17 walk-forward Platt calibration (`LogisticRegression(C=1.0)` on `logit(raw)`) for `target_seasons`."""
    seasons = sorted(frame["season"].unique())
    parts: list[dict[str, Any]] = []
    for idx, season in enumerate(seasons):
        if idx == 0 or season not in target_seasons:
            continue
        prior = frame[frame["season"].isin(seasons[:idx])]
        fold = frame[frame["season"] == season].copy()
        for market in T17_MARKETS:
            raw_col = f"raw_{market}"
            act_col = f"actual_{market}"
            cal = LogisticRegression(C=1.0, max_iter=1000).fit(
                _logit(prior[raw_col]).reshape(-1, 1), prior[act_col]
            )
            p_cal = np.clip(
                cal.predict_proba(_logit(fold[raw_col]).reshape(-1, 1))[:, 1],
                1e-6,
                1.0 - 1e-6,
            )
            for row, p_val, b_val, won in zip(
                fold.itertuples(index=False),
                p_cal,
                fold[raw_col].to_numpy(float),
                fold[act_col].to_numpy(int),
            ):
                parts.append(
                    {
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
                    }
                )
    return pd.DataFrame(parts)


def replicate_task_16() -> list[dict[str, Any]]:
    """Run Task 16 primary (2024/25+) and replication (2019/20-2023/24) evaluations."""
    all_legs: list[pd.DataFrame] = []
    for code in LEAGUES:
        matches = load_t16_matches(code)
        legs, _ = build_t16_legs(matches, code, league_rho(code))
        all_legs.append(legs)
    legs_df = pd.concat(all_legs, ignore_index=True)

    prim_df = legs_df[legs_df["season"] >= T16_JUDGED_FROM].dropna(subset=["probability"])
    repl_df = legs_df[legs_df["season"].isin(REPL_SEASONS)].dropna(subset=["probability"])

    rng_prim = np.random.default_rng(SEED)
    rng_repl = np.random.default_rng(SEED)

    rows: list[dict[str, Any]] = []
    for code in LEAGUES:
        d_prim = prim_df[prim_df["league"] == code]
        d_repl = repl_df[repl_df["league"] == code]
        for market in T16_MARKETS:
            r_prim = evaluate(code, market, d_prim, "probability", rng_prim)
            r_repl = evaluate(code, market, d_repl, "probability", rng_repl)
            m_prim = d_prim[d_prim["market"] == market]
            m_repl = d_repl[d_repl["market"] == market]
            fo_prim = round(float((1.0 / m_prim["probability"]).median()), 2)
            fo_repl = round(float((1.0 / m_repl["probability"]).median()), 2)
            strong = r_prim["status"] == "PASS" and r_repl["status"] == "PASS"
            rows.append(
                {
                    "task": 16,
                    "league": code,
                    "market": market,
                    "primary_2024_25_plus": {**r_prim, "fair_odds": fo_prim},
                    "replication_2019_20_to_2023_24": {**r_repl, "fair_odds": fo_repl},
                    "strong_candidate": strong,
                    "verdict": "Strong candidate (pending real Betpawa prices)" if strong else "stays out",
                }
            )
    return rows


def replicate_task_17() -> list[dict[str, Any]]:
    """Run Task 17 primary (2024/25+) and replication (2019/20-2023/24) evaluations."""
    rng_prim = np.random.default_rng(SEED)
    rng_repl = np.random.default_rng(SEED)

    rows: list[dict[str, Any]] = []
    for code in T17_LEAGUES:
        rho = league_rho(code)
        df, _ = load_t17_matches(code)
        df = add_t17_raw_probabilities(df, rho)
        legs_prim = walk_forward_t17_primary(df)
        legs_repl = walk_forward_t17_seasons(df, REPL_SEASONS)
        for market in T17_MARKETS:
            sub_prim = legs_prim[legs_prim["market"] == market].copy()
            sub_repl = legs_repl[legs_repl["market"] == market].copy()
            r_prim = evaluate(code, market, sub_prim, "probability", rng_prim)
            r_repl = evaluate(code, market, sub_repl, "probability", rng_repl)
            fo_prim = round(float(np.median(1.0 / sub_prim["probability"].to_numpy(float))), 2)
            fo_repl = round(float(np.median(1.0 / sub_repl["probability"].to_numpy(float))), 2)
            strong = r_prim["status"] == "PASS" and r_repl["status"] == "PASS"
            rows.append(
                {
                    "task": 17,
                    "league": code,
                    "market": market,
                    "primary_2024_25_plus": {**r_prim, "fair_odds": fo_prim},
                    "replication_2019_20_to_2023_24": {**r_repl, "fair_odds": fo_repl},
                    "strong_candidate": strong,
                    "verdict": "Strong candidate (pending real Betpawa prices)" if strong else "stays out",
                }
            )
    return rows


def _summarize(rows: list[dict[str, Any]]) -> dict[str, int]:
    total = len(rows)
    p_pass = sum(r["primary_2024_25_plus"]["status"] == "PASS" for r in rows)
    p_fail = sum(r["primary_2024_25_plus"]["status"] == "FAIL" for r in rows)
    r_pass = sum(r["replication_2019_20_to_2023_24"]["status"] == "PASS" for r in rows)
    r_fail = sum(r["replication_2019_20_to_2023_24"]["status"] == "FAIL" for r in rows)
    strong = sum(bool(r["strong_candidate"]) for r in rows)
    return {
        "total": total,
        "p_pass": p_pass,
        "p_fail": p_fail,
        "r_pass": r_pass,
        "r_fail": r_fail,
        "strong": strong,
    }


def _format_table(rows: list[dict[str, Any]]) -> list[str]:
    out = [
        "| League | Market | 2024/25+ n | 2024/25+ Said | 2024/25+ Won | Fair odds | 2024/25+ Gate | 2019/20-23/24 n | 2019/20-23/24 Said | 2019/20-23/24 Won | 2019/20-23/24 Gate | Verdict |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|",
    ]
    for r in rows:
        p = r["primary_2024_25_plus"]
        rep = r["replication_2019_20_to_2023_24"]
        out.append(
            f"| {r['league']} | {r['market']} | {p['n']} | {p.get('mean_p', float('nan')):.4f} | "
            f"{p.get('actual', float('nan')):.4f} | {p['fair_odds']:.2f} | **{p['status']}** | "
            f"{rep['n']} | {rep.get('mean_p', float('nan')):.4f} | {rep.get('actual', float('nan')):.4f} | "
            f"**{rep['status']}** | {r['verdict']} |"
        )
    return out


def write_report() -> Path:
    t16_rows = replicate_task_16()
    t17_rows = replicate_task_17()
    all_rows = [*t16_rows, *t17_rows]

    s16 = _summarize(t16_rows)
    s17 = _summarize(t17_rows)
    sa = _summarize(all_rows)

    lines = [
        "# Replication of Tasks 16 and 17 on 2019/20-2023/24 (PROJECT.md task 21, pre-registered 2026-11-07)",
        "",
        "## Design",
        "- Re-judges every league x market pair from Task 16 (9 leagues x 6 half markets = 54 pairs) and Task 17 (5 main leagues x 5 UP markets = 25 pairs) on **`2019/20-2023/24`** using the exact same raw-probability formulas, walk-forward Platt calibration (`LogisticRegression(C=1.0)` on `logit(raw)` fitted on earlier seasons only), and `market_gates.evaluate` (`SEED = 20261029`).",
        "- Earlier reports (`reports/half_markets_study.md` and `reports/up_markets_study.md`) are unchanged; their `2024/25+` numbers are reproduced identically below alongside the `2019/20-2023/24` replication.",
        "- **Strong candidate** = `PASS` in both `2024/25+` and `2019/20-2023/24` (pending real Betpawa prices); otherwise `stays out`.",
        "",
        "## Summary",
        f"- **Task 16 (Goals by half & Win Either Half, {s16['total']} pairs)**: Primary `2024/25+` **{s16['p_pass']} PASS / {s16['p_fail']} FAIL**; Replication `2019/20-2023/24` **{s16['r_pass']} PASS / {s16['r_fail']} FAIL**; Strong candidates (`PASS` in both): **{s16['strong']} / {s16['total']}**.",
        f"- **Task 17 (Double Chance 1UP & 1X2 2UP, {s17['total']} pairs)**: Primary `2024/25+` **{s17['p_pass']} PASS / {s17['p_fail']} FAIL**; Replication `2019/20-2023/24` **{s17['r_pass']} PASS / {s17['r_fail']} FAIL**; Strong candidates (`PASS` in both): **{s17['strong']} / {s17['total']}**.",
        f"- **Combined ({sa['total']} pairs)**: Primary **{sa['p_pass']} PASS / {sa['p_fail']} FAIL**; Replication **{sa['r_pass']} PASS / {sa['r_fail']} FAIL**; Strong candidates (`PASS` in both): **{sa['strong']} / {sa['total']}**.",
        "",
        "## Part 1 — Task 16 Replication (Goals by Half & Win Either Half, 9 Live Leagues)",
        *_format_table(t16_rows),
        "",
        "## Part 2 — Task 17 Replication (Double Chance 1UP & 1X2 2UP, 5 Main Leagues)",
        *_format_table(t17_rows),
        "",
        "## Full Gate Details",
        "```json",
        json.dumps(all_rows, indent=2, default=str),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


if __name__ == "__main__":
    print(f"Wrote {write_report()}")
