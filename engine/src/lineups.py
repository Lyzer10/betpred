"""Announced line-ups from ESPN's public scoreboard/summary data (no account, no scraping protection).

Clubs announce line-ups about an hour before kick-off; ESPN shows them as soon as they are out.
Display only: line-ups are not a model input until a study shows they improve on the odds (the
earlier absences study found no gain beyond the bookmaker price).
Usage: python -m src.lineups   (writes web/public/data/lineups.json for matches in the next 36 hours)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import requests

from .calibration import ENGINE_DIR
from .team_names import canonical_team

ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer"
SLUGS = {"EPL": "eng.1", "LALIGA": "esp.1", "SERIEA": "ita.1", "BUNDES": "ger.1", "LIGUE1": "fra.1"}
LINEUPS_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "lineups.json"
HORIZON = pd.Timedelta(hours=36)


def _team(roster: dict) -> dict:
    players = roster.get("roster", [])
    def player(p):
        return {"name": p["athlete"]["displayName"], "number": p.get("jersey"),
                "position": (p.get("position") or {}).get("abbreviation")}
    return {"formation": roster.get("formation"),
            "starters": [player(p) for p in players if p.get("starter")],
            "subs": [player(p) for p in players if not p.get("starter")]}


def parse_summary(summary: dict, league: str) -> dict | None:
    """Line-ups of one match, or None until both teams' starting elevens are announced."""
    teams = {}
    for roster in summary.get("rosters", []):
        side = roster.get("homeAway")
        lineup = _team(roster)
        if side not in ("home", "away") or len(lineup["starters"]) != 11:
            return None
        teams[side] = (canonical_team(roster["team"]["displayName"], league), lineup)
    if set(teams) != {"home", "away"}:
        return None
    return {"league": league, "home": teams["home"][0], "away": teams["away"][0],
            "home_lineup": teams["home"][1], "away_lineup": teams["away"][1]}


def fetch_lineups(now: pd.Timestamp, session: requests.Session | None = None) -> list[dict]:
    session = session or requests.Session()
    found = []
    days = sorted({(now + pd.Timedelta(hours=h)).strftime("%Y%m%d") for h in (0, 12, 24, 36)})
    for league, slug in SLUGS.items():
        for day in days:
            try:
                events = session.get(f"{ESPN}/{slug}/scoreboard", params={"dates": day}, timeout=20).json().get("events", [])
            except Exception as error:      # ESPN down: line-ups are optional
                print(f"{league} {day}: scoreboard unavailable ({error})")
                continue
            for event in events:
                kickoff = pd.Timestamp(event["date"]).tz_localize(None)
                if not (now - pd.Timedelta(hours=3) <= kickoff <= now + HORIZON):
                    continue
                try:
                    summary = session.get(f"{ESPN}/{slug}/summary", params={"event": event["id"]}, timeout=20).json()
                    lineup = parse_summary(summary, league)
                except (requests.RequestException, ValueError, KeyError) as error:
                    print(f"{league} {event.get('name')}: line-ups unavailable ({error})")
                    continue
                if lineup:
                    found.append(lineup | {"kickoff_utc": kickoff.isoformat() + "Z"})
    return found


def main() -> None:
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    lineups = fetch_lineups(now)
    LINEUPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LINEUPS_PATH.write_text(json.dumps({"generated_at": now.isoformat() + "Z", "matches": lineups}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    print(f"Line-ups: {len(lineups)} matches announced")


if __name__ == "__main__":
    main()
