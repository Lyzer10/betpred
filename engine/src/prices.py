"""Betpawa price log and closing-line value (CLV).

Every run appends the Betpawa prices of the slip markets for matches in the next two local days to
data/live/prices/<local day>.csv. Price-only snapshots (`python -m src.prices`) run shortly before
kick-offs and change nothing else: they record the closing price.

CLV of a slip leg = price we published / last logged price before kick-off - 1. Positive CLV means the
price fell after we published (the market moved towards our pick): the most direct early evidence of
an edge, long before win/loss records are large enough.
Usage: python -m src.prices   (snapshot of matches kicking off within the next SNAPSHOT_MINUTES)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from .accumulators import SLIP_MARKETS
from .betpawa import RESEARCH_MARKETS, fetch_competition_odds
from .calibration import ENGINE_DIR

PRICES_DIR = ENGINE_DIR / "data" / "live" / "prices"
WEB_DATA_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "predictions.json"
COLUMNS = ["snapshot_utc", "league", "home", "away", "kickoff_utc", "market", "betpawa_odds",
           "probability", "bookmaker_probability"]
SNAPSHOT_MINUTES = 75      # a snapshot covers matches kicking off within this many minutes
CLOSE_WINDOW_MINUTES = 90  # a "closing" price must be logged at most this long before kick-off


def _append(rows: pd.DataFrame, day: str) -> None:
    PRICES_DIR.mkdir(parents=True, exist_ok=True)
    path = PRICES_DIR / f"{day}.csv"
    rows[COLUMNS].to_csv(path, mode="a", header=not path.exists(), index=False, float_format="%.4f")


def log_prices(legs: pd.DataFrame, now: pd.Timestamp, days: int = 2) -> int:
    """Append priced slip-market legs of the next `days` local days (legs carry `day` and `league`)."""
    wanted = sorted(legs.day.unique())[:days]
    rows = legs[legs.market.isin(SLIP_MARKETS) & legs.betpawa_odds.notna() & legs.day.isin(wanted)
                & (legs.kickoff_utc > now)]
    if rows.empty:
        return 0
    rows = rows.assign(snapshot_utc=now.isoformat() + "Z", home=rows.home_team, away=rows.away_team,
                       kickoff_utc=rows.kickoff_utc.map(lambda t: t.isoformat() + "Z"))
    for day, group in rows.groupby("day"):
        _append(group, day)
    return len(rows)


def snapshot(now: pd.Timestamp) -> int:
    """Log Betpawa prices for published matches kicking off within SNAPSHOT_MINUTES. Nothing else changes."""
    published = json.loads(WEB_DATA_PATH.read_text(encoding="utf-8"))
    soon = [f for f in published["fixtures"]
            if now < pd.Timestamp(f["kickoff_utc"]).tz_localize(None) <= now + pd.Timedelta(minutes=SNAPSHOT_MINUTES)]
    logged = 0
    for code in sorted({f["league"]["code"] for f in soon}):
        try:
            odds = fetch_competition_odds(code)
        except Exception as error:      # a missed snapshot only loses one closing price
            print(f"{code}: Betpawa unavailable ({error})")
            continue
        for f in (f for f in soon if f["league"]["code"] == code):
            rows = odds[(odds.home_team == f["home"]) & (odds.away_team == f["away"])
                        & odds.market.isin((*SLIP_MARKETS, *RESEARCH_MARKETS))]
            if rows.empty:
                continue
            rows = rows.assign(snapshot_utc=now.isoformat() + "Z", league=code, home=f["home"], away=f["away"],
                               kickoff_utc=f["kickoff_utc"], probability=None, bookmaker_probability=None)
            _append(rows, f["day"])
            logged += len(rows)
    return logged


def log_research_prices(odds: pd.DataFrame, now: pd.Timestamp) -> int:
    """Collect candidate prices only; there are no model probabilities for these markets."""
    if odds.empty:
        return 0
    rows = odds[odds.market.isin(RESEARCH_MARKETS) & odds.betpawa_odds.notna()
                & (odds.kickoff_utc > now)].copy()
    rows["day"] = rows.kickoff_utc.dt.tz_localize("UTC").dt.tz_convert("Africa/Dar_es_Salaam").dt.strftime("%Y-%m-%d")
    today = now.tz_localize("UTC").tz_convert("Africa/Dar_es_Salaam").strftime("%Y-%m-%d")
    tomorrow = (now + pd.Timedelta(days=1)).tz_localize("UTC").tz_convert("Africa/Dar_es_Salaam").strftime("%Y-%m-%d")
    rows = rows[rows.day.isin((today, tomorrow))]
    rows = rows.assign(snapshot_utc=now.isoformat() + "Z", home=rows.home_team, away=rows.away_team,
                       probability=None, bookmaker_probability=None,
                       kickoff_utc=rows.kickoff_utc.map(lambda t: t.isoformat() + "Z"))
    for day, group in rows.groupby("day"):
        _append(group, day)
    return len(rows)


def load_prices() -> pd.DataFrame:
    files = sorted(PRICES_DIR.glob("*.csv")) if PRICES_DIR.exists() else []
    if not files:
        return pd.DataFrame(columns=COLUMNS)
    prices = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    for column in ("snapshot_utc", "kickoff_utc"):
        prices[column] = pd.to_datetime(prices[column]).dt.tz_localize(None)
    return prices


def closing_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Last logged price per match and market, if logged within CLOSE_WINDOW_MINUTES before kick-off."""
    before = prices[(prices.snapshot_utc < prices.kickoff_utc)
                    & (prices.snapshot_utc >= prices.kickoff_utc - pd.Timedelta(minutes=CLOSE_WINDOW_MINUTES))]
    last = before.sort_values("snapshot_utc").groupby(["home", "away", "kickoff_utc", "market"], as_index=False).last()
    return last[["home", "away", "kickoff_utc", "market", "betpawa_odds"]].rename(columns={"betpawa_odds": "closing_odds"})


def clv_rows(history: list[dict], prices: pd.DataFrame) -> pd.DataFrame:
    """One row per recorded slip leg that has both a published and a closing Betpawa price."""
    legs = [{"tier": entry["tier"], "final": bool(entry.get("final")), "league": leg["league"]["code"]
             if isinstance(leg.get("league"), dict) else leg.get("league", "EPL"),
             "home": leg["home"], "away": leg["away"], "market": leg["market"],
             "kickoff_utc": pd.Timestamp(leg["kickoff_utc"]).tz_localize(None),
             "published_odds": leg.get("betpawa_odds"), "won": leg.get("won")}
            for entry in history for leg in entry["legs"]]
    legs = pd.DataFrame(legs, columns=["tier", "final", "league", "home", "away", "market", "kickoff_utc",
                                       "published_odds", "won"]).dropna(subset=["published_odds"])
    if legs.empty or prices.empty:
        return legs.assign(closing_odds=pd.Series(dtype=float), clv=pd.Series(dtype=float)).iloc[0:0]
    rows = legs.merge(closing_prices(prices), on=["home", "away", "kickoff_utc", "market"], how="inner")
    return rows.assign(clv=rows.published_odds / rows.closing_odds - 1)


def _summary(rows: pd.DataFrame) -> dict:
    return {"legs": int(len(rows)), "mean_clv": round(float(rows.clv.mean()), 4),
            "beat_close": round(float((rows.clv > 0).mean()), 4), "moved_against": round(float((rows.clv < 0).mean()), 4)}


def clv_report(history: list[dict], prices: pd.DataFrame | None = None) -> dict:
    """CLV overall and per league, market and tier (slip legs; one leg counts once per slip it is in)."""
    rows = clv_rows(history, load_prices() if prices is None else prices)
    if rows.empty:
        return {"legs": 0}
    return _summary(rows) | {group: {str(key): _summary(part) for key, part in rows.groupby(group)}
                             for group in ("league", "market", "tier")}


def main() -> None:
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    print(f"Price snapshot: {snapshot(now)} prices logged")


if __name__ == "__main__":
    main()
