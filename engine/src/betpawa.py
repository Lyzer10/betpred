"""Real Betpawa Tanzania prices for the markets the model covers.

Betpawa's robots.txt allows crawling of public pages; odds are public. We make a
plain, identified request (no browser disguise) for the Premier League event list,
then one request per match, pausing between requests.

Market ids and encodings were read from the site's own public API:
  3743      1X2 - FT                    1 / X / 2
  28000810  1X2 1UP - FT                1 = home 1Up, 2 = away 1Up
  28000224  Goal (row handicap 4 = goal 1)  1 / 2 = team to score first
  3795      Both Teams To Score - FT    Yes / No
  5000      Total Score Over/Under - FT row handicap = goal line x 4
  4693      Double Chance - FT          1X / X2 / 12
"""
from __future__ import annotations

import json
import time

import pandas as pd
import requests

from .leagues import get_league
from .team_names import canonical_team

BASE_URL = "https://www.betpawa.co.tz/api/sportsbook/v4"
PREMIER_LEAGUE_ID = "11965"
HEADERS = {
    "x-pawa-brand": "betpawa-tanzania", "x-pawa-language": "en", "accept": "application/json",
    "User-Agent": "PL-Predictor/1.0 (personal odds research)",
}
PAUSE_SECONDS = 1.0
RESEARCH_MARKETS = ("home_over_0.5", "home_over_1.5", "away_over_0.5", "away_over_1.5", "dnb_home", "dnb_away")


def parse_markets(markets: list[dict]) -> dict[str, float]:
    """Map Betpawa markets onto the model's market keys; skip suspended or empty prices."""
    odds: dict[str, float] = {}

    def take(key: str, price: dict) -> None:
        if price.get("odds", 0) > 1 and not price.get("suspended", False):
            odds[key] = float(price["odds"])

    for market in markets:
        type_id = market["marketType"]["id"]
        for row in market.get("row", []):
            prices = {p["name"]: p for p in row.get("prices", [])}
            handicap = row.get("handicap")
            if type_id == "3743":
                for name, key in (("1", "home_win"), ("X", "draw"), ("2", "away_win")):
                    if name in prices:
                        take(key, prices[name])
            elif type_id == "28000810":
                for name, key in (("1", "home_1up"), ("2", "away_1up")):
                    if name in prices:
                        take(key, prices[name])
            elif type_id == "28000224" and handicap is not None and float(handicap) == 4:
                for name, key in (("1", "home_first"), ("2", "away_first")):
                    if name in prices:
                        take(key, prices[name])
            elif type_id == "4693":
                for name, key in (("1X", "double_1x"), ("X2", "double_x2"), ("12", "double_12")):
                    if name in prices:
                        take(key, prices[name])
            elif type_id == "3795":
                for name, key in (("Yes", "btts_yes"), ("No", "btts_no")):
                    if name in prices:
                        take(key, prices[name])
            elif type_id == "4703":
                for name, key in (("1", "dnb_home"), ("2", "dnb_away")):
                    if name in prices:
                        take(key, prices[name])
            elif type_id in ("5006", "5003") and handicap is not None:
                try:
                    line = float(handicap) / 4
                except (TypeError, ValueError):
                    print(f"Research market {type_id}: invalid handicap; skipping row")
                    continue
                if line in (0.5, 1.5) and "Over" in prices:
                    side = "home" if type_id == "5006" else "away"
                    take(f"{side}_over_{line}", prices["Over"])
            elif type_id == "5000" and handicap is not None:
                line = float(handicap) / 4
                if line in (0.5, 1.5, 2.5, 3.5):
                    if "Over" in prices:
                        take(f"over_{line}", prices["Over"])
                    if "Under" in prices and line in (2.5, 3.5):
                        take(f"under_{line}", prices["Under"])
    return odds


def fetch_premier_league_odds(session: requests.Session | None = None) -> pd.DataFrame:
    return fetch_competition_odds("EPL", session)


def fetch_competition_odds(league="EPL", session: requests.Session | None = None) -> pd.DataFrame:
    """One row per (match, market) with Betpawa's current decimal odds."""
    session = session or requests.Session()
    query = {"queries": [{"query": {"eventType": "UPCOMING", "categories": ["2"],
                                    "zones": {"competitions": [str(get_league(league).betpawa_competition_id)]}}, "take": 50}]}
    response = session.get(f"{BASE_URL}/events/lists/by-queries", params={"q": json.dumps(query)},
                           headers=HEADERS, timeout=30)
    response.raise_for_status()
    events = response.json()["responses"][0]["responses"]
    rows = []
    for event in events:
        time.sleep(PAUSE_SECONDS)
        detail = session.get(f"{BASE_URL}/events/{event['id']}", headers=HEADERS, timeout=30)
        if not detail.ok:
            continue
        participants = sorted(event["participants"], key=lambda p: p["position"])
        home, away = (canonical_team(p["name"], league) for p in participants[:2])
        kickoff = pd.Timestamp(event["startTime"]).tz_convert("UTC").tz_localize(None)
        for market, price in parse_markets(detail.json().get("markets", [])).items():
            rows.append({"home_team": home, "away_team": away, "kickoff_utc": kickoff,
                         "market": market, "betpawa_odds": price, "betpawa_event_id": event["id"]})
    return pd.DataFrame(rows, columns=["home_team", "away_team", "kickoff_utc", "market", "betpawa_odds", "betpawa_event_id"])
