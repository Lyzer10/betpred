"""Upcoming fixtures for the next two weeks and expected line-ups, from ESPN's public data (display only).

- `matches`: every fixture of our five leagues in the next SCHEDULE_DAYS days, also before our predictions
  exist (the app shows them as "predictions later").
- `expected_lineups`: for each team playing in the next EXPECTED_DAYS days, the starting XI of its last
  finished league match (looked up LOOKBACK_DAYS back). The app shows it until the official line-up is
  announced, clearly labelled as last match's XI: it is not a prediction of the line-up.
ESPN accepts one date per scoreboard request, so this runs on full and final runs only (not every price snapshot).
Usage: python -m src.schedule   (writes web/public/data/schedule.json)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import requests

from .lineups import ESPN, SLUGS, _team, event_teams, parse_summary
from .calibration import ENGINE_DIR
from .team_names import canonical_team

SCHEDULE_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "schedule.json"
ARCHIVE_DIR = SCHEDULE_PATH.parent / "archive"
SCHEDULE_DAYS, EXPECTED_DAYS, LOOKBACK_DAYS = 14, 3, 8


def _scoreboard(session: requests.Session, slug: str, day: pd.Timestamp) -> list[dict]:
    try:
        return session.get(f"{ESPN}/{slug}/scoreboard", params={"dates": day.strftime("%Y%m%d")}, timeout=20).json().get("events", [])
    except Exception as error:          # one missing day only shortens the list
        print(f"{slug} {day.date()}: scoreboard unavailable ({error})")
        return []


def last_xi(summary: dict, league: str, team: str) -> dict | None:
    """Starting XI of `team` in a finished match summary, or None."""
    for roster in summary.get("rosters", []):
        try:
            if canonical_team(roster["team"]["displayName"], league) != team:
                continue
        except ValueError:
            continue
        lineup = _team(roster)
        return lineup if len(lineup["starters"]) == 11 else None
    return None


def build_schedule(now: pd.Timestamp, session: requests.Session | None = None) -> dict:
    session = session or requests.Session()
    upcoming, finished = [], {}          # finished: (league, team) -> (kickoff, event, slug, label)
    played = []                          # every finished match seen: for the line-ups actually played
    for league, slug in SLUGS.items():
        for offset in range(-LOOKBACK_DAYS, SCHEDULE_DAYS + 1):
            for event in _scoreboard(session, slug, now.normalize() + pd.Timedelta(days=offset)):
                try:
                    home, away = event_teams(event, league)
                except (ValueError, KeyError):
                    continue
                kickoff = pd.Timestamp(event["date"]).tz_localize(None)
                state = event["status"]["type"]["state"]
                if state == "pre" and now <= kickoff <= now + pd.Timedelta(days=SCHEDULE_DAYS):
                    upcoming.append({"league": league, "home": home, "away": away, "kickoff_utc": kickoff.isoformat() + "Z",
                                     "event_id": event["id"], "slug": slug})
                if state == "post" and event["status"]["type"].get("completed"):
                    played.append({"league": league, "home": home, "away": away, "kickoff": kickoff,
                                   "event_id": event["id"], "slug": slug})
                    label = f"{home} v {away}, {kickoff.date().isoformat()}"
                    for team in (home, away):
                        if kickoff > finished.get((league, team), (pd.Timestamp.min,))[0]:
                            finished[(league, team)] = (kickoff, event["id"], slug, label)
    soon = {(m["league"], t) for m in upcoming for t in (m["home"], m["away"])
            if pd.Timestamp(m["kickoff_utc"]).tz_localize(None) <= now + pd.Timedelta(days=EXPECTED_DAYS)}
    expected = {}
    for league, team in sorted(soon):
        if (league, team) not in finished:
            continue
        _, event_id, slug, label = finished[(league, team)]
        try:
            summary = session.get(f"{ESPN}/{slug}/summary", params={"event": event_id}, timeout=20).json()
        except Exception as error:
            print(f"{team}: last line-up unavailable ({error})")
            continue
        xi = last_xi(summary, league, team)
        if xi:
            expected[team] = xi | {"from_match": label}
    store_played_lineups(played, session)
    return {"generated_at": now.isoformat() + "Z", "matches": sorted(upcoming, key=lambda m: m["kickoff_utc"]),
            "expected_lineups": expected}


def store_played_lineups(played: list[dict], session: requests.Session) -> int:
    """Save the line-ups actually played into archived matches that lack them (fetched once per match)."""
    if not ARCHIVE_DIR.exists():
        return 0
    stored = 0
    for path in sorted(ARCHIVE_DIR.glob("20*.json"))[-LOOKBACK_DAYS - 1:]:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for fixture in snapshot["fixtures"]:
            if fixture.get("lineups"):
                continue
            kickoff = pd.Timestamp(fixture["kickoff_utc"]).tz_localize(None)
            match = next((m for m in played if (m["home"], m["away"]) == (fixture["home"], fixture["away"])
                          and abs((m["kickoff"] - kickoff).total_seconds()) <= 36 * 3600), None)
            if not match:
                continue
            try:
                summary = session.get(f"{ESPN}/{match['slug']}/summary", params={"event": match["event_id"]}, timeout=20).json()
                lineup = parse_summary(summary, match["league"])
            except (requests.RequestException, ValueError, KeyError) as error:
                print(f"{fixture['home']} v {fixture['away']}: played line-ups unavailable ({error})")
                continue
            if lineup:
                fixture["lineups"] = {"home_lineup": lineup["home_lineup"], "away_lineup": lineup["away_lineup"]}
                changed = True
                stored += 1
        if changed:
            path.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")
    print(f"Played line-ups stored: {stored}")
    return stored


def main() -> None:
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    schedule = build_schedule(now)
    SCHEDULE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE_PATH.write_text(json.dumps(schedule, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Schedule: {len(schedule['matches'])} matches in the next {SCHEDULE_DAYS} days; "
          f"{len(schedule['expected_lineups'])} expected line-ups")


if __name__ == "__main__":
    main()
