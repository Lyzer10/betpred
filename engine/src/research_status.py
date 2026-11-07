"""Task 23: Research Status Report.

Counts settled priced legs across all 30 candidate markets:
- 9 live betting leagues (prices from live/prices, results from live archive)
- 7 research leagues (prices from live/research/prices, results from live/research/results.csv)
- Total settled legs, distance to 300-leg threshold, and decision status.
- Per-league statistics: matches logged, matches settled, market coverage rate.
- Prominent notice when any candidate market reaches 300 settled legs.

Usage: python -m src.research_status
"""
from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .betpawa import RESEARCH_MARKETS
from .calibration import ENGINE_DIR
from .leagues import LEAGUES
from .predict import settled_predictions
from .research_leagues import PRICES_DIR as RESEARCH_PRICES_DIR, RESEARCH_LEAGUES, RESULTS_PATH as RESEARCH_RESULTS_FILE

LIVE_PRICES_DIR = ENGINE_DIR / "data" / "live" / "prices"
REPORT_PATH = ENGINE_DIR / "reports" / "research_status.md"
THRESHOLD = 300


def get_live_settled_legs() -> tuple[dict[str, int], dict[str, dict[str, Any]]]:
    """Calculate settled priced legs and match counts for the 9 live leagues."""
    preds = settled_predictions()
    live_res_map: dict[tuple[str, str, str], dict[str, Any]] = {}
    settled_matches_per_league: dict[str, set[tuple[str, str]]] = {c: set() for c in LEAGUES}

    for p in preds:
        if "result" in p and "score" in p["result"]:
            code = p.get("league", {}).get("code", "EPL") if isinstance(p.get("league"), dict) else (p.get("league") or "EPL")
            key = (code, p["home"], p["away"])
            live_res_map[key] = p["result"]
            if code in settled_matches_per_league:
                settled_matches_per_league[code].add((p["home"], p["away"]))

    # Load live prices
    price_files = sorted(LIVE_PRICES_DIR.glob("*.csv"))
    if not price_files:
        return {m: 0 for m in RESEARCH_MARKETS}, {}

    dfs = []
    for f in price_files:
        try:
            df = pd.read_csv(f)
            if not df.empty and "market" in df.columns:
                dfs.append(df)
        except Exception:
            pass
    if not dfs:
        return {m: 0 for m in RESEARCH_MARKETS}, {}

    all_prices = pd.concat(dfs, ignore_index=True)
    valid = all_prices[
        (all_prices.snapshot_utc < all_prices.kickoff_utc)
        & all_prices.betpawa_odds.notna()
        & (all_prices.betpawa_odds > 1.0)
    ]
    last_prices = valid.sort_values("snapshot_utc").groupby(["league", "home", "away", "market"], as_index=False).last()

    market_counts: dict[str, int] = {m: 0 for m in RESEARCH_MARKETS}
    league_stats: dict[str, dict[str, Any]] = {}

    for code in LEAGUES:
        sub = last_prices[last_prices.league == code]
        m_matches = sub.groupby(["home", "away"]).size()
        n_logged = len(m_matches)
        n_settled = len(settled_matches_per_league.get(code, set()))
        sub_res = sub[sub.market.isin(RESEARCH_MARKETS)]
        n_res_mkt = sub_res.groupby(["home", "away"])["market"].nunique()
        avg_cov = (n_res_mkt.mean() / len(RESEARCH_MARKETS)) if not n_res_mkt.empty else 0.0
        league_stats[code] = {
            "type": "live",
            "name": LEAGUES[code].name if hasattr(LEAGUES[code], "name") else code,
            "logged_matches": n_logged,
            "settled_matches": n_settled,
            "market_coverage": avg_cov,
        }

    for m in sorted(RESEARCH_MARKETS):
        sub_m = last_prices[last_prices.market == m]
        settled_count = 0
        for r in sub_m.itertuples():
            key = (r.league, r.home, r.away)
            if key in live_res_map:
                res = live_res_map[key]
                outcomes = res.get("outcomes", {})
                if m in ("home_over_0.5", "home_over_1.5", "away_over_0.5", "away_over_1.5"):
                    settled_count += 1
                elif m in ("dnb_home", "dnb_away"):
                    score = res.get("score", [])
                    if len(score) == 2 and score[0] != score[1]:
                        settled_count += 1
                elif m in outcomes and outcomes[m] is not None:
                    settled_count += 1
        market_counts[m] = settled_count

    return market_counts, league_stats


def get_research_settled_legs() -> tuple[dict[str, int], dict[str, dict[str, Any]]]:
    """Calculate settled priced legs and match counts for the 7 research leagues."""
    # Load research results
    res_map: dict[tuple[str, str, str], dict[str, Any]] = {}
    settled_matches_per_league: dict[str, set[tuple[str, str]]] = {div: set() for div in RESEARCH_LEAGUES}
    if RESEARCH_RESULTS_FILE.exists():
        try:
            res_df = pd.read_csv(RESEARCH_RESULTS_FILE, dtype=str)
            for r in res_df.itertuples():
                key = (r.league, r.home, r.away)
                res_map[key] = {m: getattr(r, m, "") for m in RESEARCH_MARKETS}
                if r.league in settled_matches_per_league:
                    settled_matches_per_league[r.league].add((r.home, r.away))
        except Exception:
            pass

    # Load research prices
    price_files = sorted(RESEARCH_PRICES_DIR.glob("*.csv")) if RESEARCH_PRICES_DIR.exists() else []
    if not price_files:
        league_stats = {}
        for div, (name, _country, _cid, _slug) in RESEARCH_LEAGUES.items():
            league_stats[div] = {
                "type": "research",
                "name": name,
                "logged_matches": 0,
                "settled_matches": len(settled_matches_per_league.get(div, set())),
                "market_coverage": 0.0,
            }
        return {m: 0 for m in RESEARCH_MARKETS}, league_stats

    dfs = []
    for f in price_files:
        try:
            df = pd.read_csv(f)
            if not df.empty and "market" in df.columns:
                dfs.append(df)
        except Exception:
            pass
    all_prices = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    if all_prices.empty:
        return {m: 0 for m in RESEARCH_MARKETS}, {}

    valid = all_prices[
        (all_prices.snapshot_utc < all_prices.kickoff_utc)
        & all_prices.betpawa_odds.notna()
        & (all_prices.betpawa_odds > 1.0)
    ]
    last_prices = valid.sort_values("snapshot_utc").groupby(["league", "home", "away", "market"], as_index=False).last()

    market_counts: dict[str, int] = {m: 0 for m in RESEARCH_MARKETS}
    league_stats = {}

    for div, (name, _country, _cid, _slug) in RESEARCH_LEAGUES.items():
        sub = last_prices[last_prices.league == div]
        m_matches = sub.groupby(["home", "away"]).size()
        n_logged = len(m_matches)
        n_settled = len(settled_matches_per_league.get(div, set()))
        sub_res = sub[sub.market.isin(RESEARCH_MARKETS)]
        n_res_mkt = sub_res.groupby(["home", "away"])["market"].nunique()
        avg_cov = (n_res_mkt.mean() / len(RESEARCH_MARKETS)) if not n_res_mkt.empty else 0.0
        league_stats[div] = {
            "type": "research",
            "name": name,
            "logged_matches": n_logged,
            "settled_matches": n_settled,
            "market_coverage": avg_cov,
        }

    for m in sorted(RESEARCH_MARKETS):
        sub_m = last_prices[last_prices.market == m]
        settled_count = 0
        for r in sub_m.itertuples():
            key = (r.league, r.home, r.away)
            if key in res_map:
                val = res_map[key].get(m, "")
                if str(val) in ("1", "0"):
                    settled_count += 1
        market_counts[m] = settled_count

    return market_counts, league_stats


def generate_status_report() -> tuple[str, list[str]]:
    """Generate Markdown report content and list of markets that reached 300."""
    now_eat = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S EAT")
    live_counts, live_stats = get_live_settled_legs()
    research_counts, research_stats = get_research_settled_legs()

    reached_markets: list[str] = []
    rows: list[dict[str, Any]] = []

    for m in sorted(RESEARCH_MARKETS):
        l_cnt = live_counts.get(m, 0)
        r_cnt = research_counts.get(m, 0)
        tot = l_cnt + r_cnt
        dist = max(0, THRESHOLD - tot)
        status = "REACHED 300" if tot >= THRESHOLD else "INSUFFICIENT"
        if tot >= THRESHOLD:
            reached_markets.append(m)
        rows.append({
            "market": m,
            "live_legs": l_cnt,
            "research_legs": r_cnt,
            "total_legs": tot,
            "distance": dist,
            "status": status,
        })

    md = []
    md.append("# BetPredz Research Markets Status Report")
    md.append("")
    md.append(f"*Generated at: {now_eat}*")
    md.append("")
    md.append("This report tracks progress toward the **300 settled priced legs** threshold for all 30 candidate research markets.")
    md.append("**Rule:** No candidate market may enter live betting slips or best picks until it reaches >= 300 settled priced legs and passes the pre-registered decision gates (Tasks 15-22).")
    md.append("")

    if reached_markets:
        md.append("> [!IMPORTANT]")
        md.append(f"> **NOTICE: {len(reached_markets)} market(s) have reached 300 settled legs:** {', '.join(reached_markets)}.")
        md.append("> This triggers the pre-registered decision rules in Tasks 15-22. NO automatic change to live betting.")
        md.append("")
    else:
        md.append("> [!NOTE]")
        md.append(f"> **Status:** All 30 candidate markets currently have < {THRESHOLD} settled priced legs. Live betting unchanged.")
        md.append("")

    md.append("## 1. Candidate Markets Settled Legs Summary (30 Markets)")
    md.append("")
    md.append("| Market | Live Leagues (9) | Research Leagues (7) | Total Settled Legs | Distance to 300 | Status |")
    md.append("|:---|---:|---:|---:|---:|:---|")
    for r in rows:
        md.append(f"| `{r['market']}` | {r['live_legs']} | {r['research_legs']} | **{r['total_legs']}** | {r['distance']} | {r['status']} |")
    md.append("")

    md.append("## 2. Research Leagues Coverage & Match Volume (7 Leagues)")
    md.append("")
    md.append("| Div | League Name | Matches Logged | Matches Settled | 30-Market Coverage | Status |")
    md.append("|:---|:---|---:|---:|---:|:---|")
    for div, st in research_stats.items():
        cov_pct = f"{st['market_coverage'] * 100:.1f}%"
        note = "Active research" if st["logged_matches"] > 0 or st["settled_matches"] > 0 else "Pending fixtures"
        md.append(f"| `{div}` | {st['name']} | {st['logged_matches']} | {st['settled_matches']} | {cov_pct} | {note} |")
    md.append("")

    md.append("## 3. Live Betting Leagues Reference (9 Leagues)")
    md.append("")
    md.append("| Code | League Name | Matches Logged | Matches Settled | 30-Market Coverage |")
    md.append("|:---|:---|---:|---:|---:|")
    for code, st in live_stats.items():
        cov_pct = f"{st['market_coverage'] * 100:.1f}%"
        md.append(f"| `{code}` | {st['name']} | {st['logged_matches']} | {st['settled_matches']} | {cov_pct} |")
    md.append("")

    report_content = "\n".join(md)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_content, encoding="utf-8")
    root_rep = ENGINE_DIR.parent / "reports" / "research_status.md"
    root_rep.parent.mkdir(parents=True, exist_ok=True)
    root_rep.write_text(report_content, encoding="utf-8")
    return report_content, reached_markets


def main() -> None:
    print("Refreshing research status report...")
    content, reached = generate_status_report()
    print(f"Report updated at {REPORT_PATH}")
    print("=" * 70)
    print("RESEARCH MARKETS SUMMARY (Distance to 300 settled legs)")
    print("=" * 70)
    # Print clean terminal table
    for line in content.splitlines():
        if line.startswith("| `") or line.startswith("| Div") or line.startswith("|:---") or line.startswith("| Market"):
            print(line)
    print("=" * 70)
    if reached:
        print(f"*** PROMINENT NOTICE: {len(reached)} MARKETS REACHED 300 LEGS: {reached} ***")
    else:
        print("All 30 candidate markets currently under 300 legs. Research in progress.")


if __name__ == "__main__":
    main()
