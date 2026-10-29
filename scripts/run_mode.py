"""Decide what a scheduled wake-up should do (standard library only, runs before any install).

The workflow is woken every 15 minutes by an external timer (GitHub's own schedule can start
hours late) and at fixed backup times. Each wake-up picks one mode:
  final  - today's first match starts within FINAL_BEFORE minutes and today is not final yet:
           full run with fresh Betpawa prices; today's slips become final; notification.
  full   - a fixed run time (07:00, 13:00, 18:00 Tanzania) has passed since the last full run, or
           football-data has posted upcoming matches (with odds) that we have not published yet
           (e.g. a late midweek round); at most once an hour for that reason.
  prices - a published match kicks off within PRICE_BEFORE minutes: log Betpawa prices only.
  skip   - nothing to do.
Writes `mode=<mode>` to $GITHUB_OUTPUT when set; always prints the decision.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PREDICTIONS = Path(__file__).resolve().parents[1] / "web" / "public" / "data" / "predictions.json"
EAT = timezone(timedelta(hours=3))           # Tanzania, no daylight saving
FULL_RUNS_EAT = (7, 13, 18)                  # hours of the regular full runs
FINAL_BEFORE = timedelta(minutes=55)         # final run from 55 minutes before the first match
PRICE_BEFORE = timedelta(minutes=35)         # price snapshot for matches starting within 35 minutes
FIXTURES_URL = "https://www.football-data.co.uk/fixtures.csv"
LEAGUE_DIVS = {"E0": "EPL", "SP1": "LALIGA", "I1": "SERIEA", "D1": "BUNDES", "F1": "LIGUE1"}
LEAGUE_DIVS.update({"N1": "EREDIV", "B1": "JUPILER", "P1": "PRIMEIRA", "T1": "SUPERLIG"})
NEW_FIXTURES_EVERY = timedelta(minutes=55)   # re-run for newly posted fixtures at most about once an hour


def _utc(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "")).replace(tzinfo=timezone.utc)


def posted_upcoming(rows: list[dict], now: datetime) -> dict[str, int]:
    """Matches of our leagues in football-data's fixture list that start after now and carry odds."""
    london = ZoneInfo("Europe/London")
    counts: dict[str, int] = {}
    for row in rows:
        league = LEAGUE_DIVS.get(row.get("Div", ""))
        if not league or not (row.get("AvgH") or row.get("B365H")):
            continue
        try:
            kickoff = datetime.strptime(f"{row['Date']} {row.get('Time') or '15:00'}", "%d/%m/%Y %H:%M").replace(tzinfo=london)
        except ValueError:
            continue
        if kickoff > now:
            counts[league] = counts.get(league, 0) + 1
    return counts


def fetch_fixture_rows() -> list[dict] | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(FIXTURES_URL, headers={"User-Agent": "BetPredz"}), timeout=20) as r:
            return list(csv.DictReader(io.StringIO(r.read().decode("utf-8-sig", errors="replace"))))
    except Exception as error:          # the check is only a shortcut: the fixed runs still happen
        print(f"fixtures.csv unavailable ({error})")
        return None


def new_fixtures_posted(published: dict, now: datetime, rows: list[dict] | None) -> bool:
    if not rows or now - _utc(published["generated_at"]) < NEW_FIXTURES_EVERY:
        return False
    ours: dict[str, int] = {}
    for f in published.get("fixtures", []):
        if _utc(f["kickoff_utc"]) > now:
            code = f["league"]["code"] if isinstance(f.get("league"), dict) else (f.get("league") or "EPL")
            ours[code] = ours.get(code, 0) + 1
    return any(count > ours.get(league, 0) for league, count in posted_upcoming(rows, now).items())


def decide(published: dict, now: datetime, fixture_rows: list[dict] | None = None) -> str:
    today = now.astimezone(EAT).date().isoformat()
    day = next((d for d in published.get("days", []) if d["date"] == today), None)
    open_slips = day and any(not slip.get("locked") for slip in day.get("slips", {}).values())
    if open_slips and day.get("first_kickoff_utc") and not day.get("final"):
        first = _utc(day["first_kickoff_utc"])
        if now >= first - FINAL_BEFORE:
            return "final"

    local = now.astimezone(EAT)
    due = [local.replace(hour=h, minute=0, second=0, microsecond=0) for h in FULL_RUNS_EAT if local.hour >= h]
    if due and _utc(published["generated_at"]) < max(due).astimezone(timezone.utc):
        return "full"
    if new_fixtures_posted(published, now, fixture_rows):
        return "full"

    if any(now < _utc(f["kickoff_utc"]) <= now + PRICE_BEFORE for f in published.get("fixtures", [])):
        return "prices"
    return "skip"


def main() -> None:
    forced = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ("", "auto") else None
    mode = forced or decide(json.loads(PREDICTIONS.read_text(encoding="utf-8")), datetime.now(timezone.utc),
                            fetch_fixture_rows())
    print(f"mode={mode}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            out.write(f"mode={mode}\n")


if __name__ == "__main__":
    main()
