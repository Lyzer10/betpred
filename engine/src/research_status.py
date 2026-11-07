"""Task 23: research status report (counts only, no decisions).

For each of the 30 research markets: settled priced legs in the 9 live leagues (prices from
engine/data/live/prices) and in the 7 research leagues (engine/data/live/research/prices), each
priced leg matched to an ESPN result in engine/data/live/research/results.csv by league, teams
and kickoff day (UTC), versus the 300 legs every pre-registered real-price test needs.

A leg = the last Betpawa price (> 1.0) logged before kickoff for that match and market, with the
market settled won or lost (DNB draws are void and do not count).

Usage: python -m src.research_status
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .betpawa import RESEARCH_MARKETS
from .calibration import ENGINE_DIR
from .leagues import LEAGUES
from .research_leagues import PRICES_DIR as RESEARCH_PRICES_DIR, RESEARCH_LEAGUES, RESULTS_PATH

LIVE_PRICES_DIR = ENGINE_DIR / "data" / "live" / "prices"
REPORT_PATH = ENGINE_DIR / "reports" / "research_status.md"
THRESHOLD = 300
KEY = ["league", "home", "away", "day"]


def _last_prices(folder: Path) -> pd.DataFrame:
    """Last valid pre-kickoff price per match and market from every CSV in folder."""
    frames = [pd.read_csv(f) for f in sorted(folder.glob("*.csv"))] if folder.exists() else []
    frames = [f for f in frames if not f.empty and {"market", "betpawa_odds", "kickoff_utc"} <= set(f.columns)]
    if not frames:
        return pd.DataFrame(columns=KEY + ["market", "betpawa_odds"])
    prices = pd.concat(frames, ignore_index=True)
    prices = prices[prices.market.isin(RESEARCH_MARKETS)]
    snap = pd.to_datetime(prices.snapshot_utc, utc=True, format="mixed")
    kick = pd.to_datetime(prices.kickoff_utc, utc=True, format="mixed")
    prices = prices.assign(snap=snap, day=kick.dt.strftime("%Y-%m-%d"))
    prices = prices[(snap < kick) & pd.to_numeric(prices.betpawa_odds, errors="coerce").gt(1.0)]
    return prices.sort_values("snap").groupby(KEY + ["market"], as_index=False).last()


def _results() -> pd.DataFrame:
    if not RESULTS_PATH.exists():
        return pd.DataFrame(columns=KEY + list(RESEARCH_MARKETS))
    res = pd.read_csv(RESULTS_PATH, dtype=str).fillna("")
    res["day"] = pd.to_datetime(res.kickoff, utc=True, format="mixed").dt.strftime("%Y-%m-%d")
    return res.drop_duplicates(KEY, keep="last")


def settled_legs(prices: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    """One row per priced leg whose market is settled won (1) or lost (0)."""
    long = results.melt(id_vars=KEY, value_vars=[m for m in RESEARCH_MARKETS if m in results.columns],
                        var_name="market", value_name="won")
    legs = prices.merge(long, on=KEY + ["market"], how="inner")
    return legs[legs.won.isin(["0", "1"])]


def build_counts() -> tuple[pd.DataFrame, pd.DataFrame]:
    results = _results()
    legs = pd.concat([settled_legs(_last_prices(LIVE_PRICES_DIR), results).assign(group="live"),
                      settled_legs(_last_prices(RESEARCH_PRICES_DIR), results).assign(group="research")],
                     ignore_index=True)
    counts = (legs.groupby(["market", "group"]).size().unstack(fill_value=0)
              .reindex(index=sorted(RESEARCH_MARKETS), columns=["live", "research"], fill_value=0))
    counts["total"] = counts.live + counts.research
    per_league = results.groupby("league").size().rename("results").to_frame()
    per_league["priced_legs"] = legs.groupby("league").size()
    return counts, per_league.fillna(0).astype(int)


def generate_status_report(write: bool = True) -> tuple[str, list[str]]:
    now_eat = datetime.now(timezone.utc).astimezone(pd.Timestamp.now(tz="Africa/Dar_es_Salaam").tz)
    counts, per_league = build_counts()
    reached = [m for m in counts.index if counts.at[m, "total"] >= THRESHOLD]
    md = ["# Research markets status (task 23)", "",
          f"Generated {now_eat:%a %d %b %Y %H:%M} EAT. Counts only: no decision is made here.",
          f"Each market needs {THRESHOLD} settled priced legs before its pre-registered real-price test.", ""]
    md.append(f"**Markets at {THRESHOLD}+:** {', '.join(reached)}" if reached else
              f"**No market has reached {THRESHOLD} settled priced legs yet.** Live betting is unchanged.")
    md += ["", "| Market | 9 live leagues | 7 research leagues | Total | Still needed |", "|:--|--:|--:|--:|--:|"]
    for m, r in counts.iterrows():
        md.append(f"| `{m}` | {r.live} | {r.research} | **{r.total}** | {max(0, THRESHOLD - r.total)} |")
    names = {code: LEAGUES[code].name for code in LEAGUES} | {d: v[0] for d, v in RESEARCH_LEAGUES.items()}
    md += ["", "| League | ESPN results recorded | Settled priced legs (all markets) |", "|:--|--:|--:|"]
    for code, r in per_league.iterrows():
        md.append(f"| {names.get(code, code)} ({code}) | {r.results} | {r.priced_legs} |")
    content = "\n".join(md) + "\n"
    if write:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(content, encoding="utf-8")
    return content, reached


def main() -> None:
    content, reached = generate_status_report()
    print(content)
    print(f"Written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
