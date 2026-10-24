"""Decide what a scheduled wake-up should do (standard library only, runs before any install).

The workflow is woken every 30 minutes by an external timer (GitHub's own schedule can start
hours late) and at fixed backup times. Each wake-up picks one mode:
  final  - today's first match starts within FINAL_BEFORE minutes and today is not final yet:
           full run with fresh Betpawa prices; today's slips become final; notification.
  full   - a fixed run time (07:00, 13:00, 18:00 Tanzania) has passed since the last full run.
  prices - a published match kicks off within PRICE_BEFORE minutes: log Betpawa prices only.
  skip   - nothing to do.
Writes `mode=<mode>` to $GITHUB_OUTPUT when set; always prints the decision.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PREDICTIONS = Path(__file__).resolve().parents[1] / "web" / "public" / "data" / "predictions.json"
EAT = timezone(timedelta(hours=3))           # Tanzania, no daylight saving
FULL_RUNS_EAT = (7, 13, 18)                  # hours of the regular full runs
FINAL_BEFORE = timedelta(minutes=55)         # final run from 55 minutes before the first match
PRICE_BEFORE = timedelta(minutes=35)         # price snapshot for matches starting within 35 minutes


def _utc(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "")).replace(tzinfo=timezone.utc)


def decide(published: dict, now: datetime) -> str:
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

    if any(now < _utc(f["kickoff_utc"]) <= now + PRICE_BEFORE for f in published.get("fixtures", [])):
        return "prices"
    return "skip"


def main() -> None:
    forced = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ("", "auto") else None
    mode = forced or decide(json.loads(PREDICTIONS.read_text(encoding="utf-8")), datetime.now(timezone.utc))
    print(f"mode={mode}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            out.write(f"mode={mode}\n")


if __name__ == "__main__":
    main()
