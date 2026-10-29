"""Announced line-ups from ESPN's public scoreboard/summary data (no account, no scraping protection).

Clubs announce line-ups about an hour before kick-off; ESPN shows them as soon as they are out.
Display only: line-ups are not a model input until a study shows they improve on the odds (the
earlier absences study found no gain beyond the bookmaker price).
The same file lists ESPN's event ids of the matches in that window (`events`), so the app can follow
live scores of the user's slips straight from ESPN without guessing team names.
Usage: python -m src.lineups   (writes web/public/data/lineups.json for matches in the next 36 hours)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import requests

from .calibration import ENGINE_DIR
from .team_names import canonical_team
from .new_league_config import NEW_LEAGUES

ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer"
SLUGS = {"EPL": "eng.1", "LALIGA": "esp.1", "SERIEA": "ita.1", "BUNDES": "ger.1", "LIGUE1": "fra.1"}
SLUGS.update({code: fields[4] for code, fields in NEW_LEAGUES.items()})
LINEUPS_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "lineups.json"
HORIZON = pd.Timedelta(hours=36)
EVENTS_BACK = pd.Timedelta(hours=18)    # finished matches keep their live FT score until the nightly settlement


def _team(roster: dict) -> dict:
    players = roster.get("roster", [])
    def player(p):
        return {"name": p["athlete"]["displayName"], "number": p.get("jersey"),
                "position": (p.get("position") or {}).get("abbreviation"),
                "formation_place": int(p["formationPlace"]) if p.get("formationPlace") is not None else None}
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


def event_teams(event: dict, league: str) -> tuple[str, str]:
    """Our (home, away) names for an ESPN scoreboard event."""
    sides = {c["homeAway"]: canonical_team(c["team"]["displayName"], league) for c in event["competitions"][0]["competitors"]}
    return sides["home"], sides["away"]


def fetch_lineups(now: pd.Timestamp, session: requests.Session | None = None) -> list[dict]:
    return fetch_espn(now, session)[0]


def fetch_espn(now: pd.Timestamp, session: requests.Session | None = None) -> tuple[list[dict], list[dict]]:
    """(announced line-ups from 3 hours ago, ESPN events from EVENTS_BACK ago) up to HORIZON ahead."""
    session = session or requests.Session()
    found, events_seen = [], {}
    days = sorted({(now + pd.Timedelta(hours=h)).strftime("%Y%m%d") for h in (-18, -12, 0, 12, 24, 36)})
    for league, slug in SLUGS.items():
        for day in days:
            try:
                events = session.get(f"{ESPN}/{slug}/scoreboard", params={"dates": day}, timeout=20).json().get("events", [])
            except Exception as error:      # ESPN down: line-ups are optional
                print(f"{league} {day}: scoreboard unavailable ({error})")
                continue
            for event in events:
                kickoff = pd.Timestamp(event["date"]).tz_localize(None)
                if not (now - EVENTS_BACK <= kickoff <= now + HORIZON):
                    continue
                try:
                    home, away = event_teams(event, league)
                    events_seen[event["id"]] = {"league": league, "home": home, "away": away,
                                                "kickoff_utc": kickoff.isoformat() + "Z", "slug": slug,
                                                "espn_date": day, "event_id": event["id"]}
                except (ValueError, KeyError) as error:
                    print(f"{league} {event.get('name')}: not mapped ({error})")
                if kickoff < now - pd.Timedelta(hours=3):
                    continue                     # line-ups only for matches still to come or just started
                try:
                    summary = session.get(f"{ESPN}/{slug}/summary", params={"event": event["id"]}, timeout=20).json()
                    lineup = parse_summary(summary, league)
                except (requests.RequestException, ValueError, KeyError) as error:
                    print(f"{league} {event.get('name')}: line-ups unavailable ({error})")
                    continue
                if lineup:
                    found.append(lineup | {"kickoff_utc": kickoff.isoformat() + "Z"})
    return found, list(events_seen.values())


def main() -> None:
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    lineups, events = fetch_espn(now)
    LINEUPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LINEUPS_PATH.write_text(json.dumps({"generated_at": now.isoformat() + "Z", "matches": lineups, "events": events},
                                       ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Line-ups: {len(lineups)} matches announced; {len(events)} ESPN events for live scores")


if __name__ == "__main__":
    main()
