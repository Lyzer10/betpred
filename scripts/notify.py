"""Phone notification after the final run: today's final slips (with Betpawa booking codes) and, on
check-in days, a reminder to come back to Claude for the planned update.

Two channels, each used when its secrets exist (a failed notification never fails the run):
  - app: Web Push to the BetPredz app itself. Secrets VAPID_PRIVATE_KEY (pairs with the public key in
    web/src/push.ts) and PUSH_SUBSCRIPTION (the code the app shows under Money -> Notifications).
  - ntfy (https://ntfy.sh): the ntfy app subscribed to the topic in secret NTFY_TOPIC.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PREDICTIONS = Path(__file__).resolve().parents[1] / "web" / "public" / "data" / "predictions.json"
EAT = timezone(timedelta(hours=3))
APP_URL = "https://betpredz.vercel.app"
ARCHIVE = PREDICTIONS.parent / "archive"

# Planned check-ins with Claude (PROJECT.md section 5). A reminder rides on the first final-slips
# notification on or after its date (a check-in can fall on a day without matches, e.g. an
# international break), and is dropped after REMIND_FOR_DAYS days.
CHECKINS = [
    ("2026-11-16", "weekly check of the new-market leg counts"),
    ("2026-11-28", "team overs / Draw No Bet decision and the closing-odds test"),
    ("2026-12-05", "new markets real-price test (300 legs)"),
]
REMIND_FOR_DAYS = 14


def checkin_note(today: str, match_days: list[str]) -> str | None:
    """Reminder if a check-in is due: its date has passed and no match day since has carried it.

    The newest due check-in wins (it supersedes an older one still waiting)."""
    for due, what in reversed(CHECKINS):
        if due > today:
            continue
        days_since = (datetime.fromisoformat(today) - datetime.fromisoformat(due)).days
        already = any(due <= day < today for day in match_days)
        if days_since <= REMIND_FOR_DAYS and not already:
            return f"📋 Check-in day: open Claude for the {what}."
        return None          # only the newest check-in that has started counts
    return None


def _archive_days() -> list[str]:
    return sorted(p.stem for p in ARCHIVE.glob("????-??-??.json"))


def message(published: dict, now: datetime, match_days: list[str] | None = None) -> tuple[str, str] | None:
    today = now.astimezone(EAT).date().isoformat()
    day = next((d for d in published.get("days", []) if d["date"] == today and d.get("final")), None)
    if not day:
        return None
    first = datetime.fromisoformat(day["first_kickoff_utc"].replace("Z", "")).replace(tzinfo=timezone.utc)
    lines = [f"{tier.title()}: odds {slip['total_odds']:.2f} · {slip['win_probability']:.0%} chance · {len(slip['legs'])} matches"
             + (f" · Betpawa code {slip['booking_code']}" if slip.get("booking_code") else "")
             for tier, slip in day["slips"].items() if slip.get("final")]
    if not lines:
        return None
    note = checkin_note(today, _archive_days() if match_days is None else match_days)
    title = f"Today's bets are final · first match {first.astimezone(EAT):%H:%M}"
    return title, "\n".join(lines + ([note] if note else []))


def send_push(title: str, body: str) -> None:
    subscription, key = os.environ.get("PUSH_SUBSCRIPTION", "").strip(), os.environ.get("VAPID_PRIVATE_KEY", "").strip()
    if not (subscription and key):
        print("App notification not set up (PUSH_SUBSCRIPTION / VAPID_PRIVATE_KEY)")
        return
    try:
        from pywebpush import webpush
        from py_vapid import Vapid
        webpush(json.loads(subscription), json.dumps({"title": title, "body": body, "url": APP_URL, "tag": "final"}),
                vapid_private_key=Vapid.from_pem(key.encode()), vapid_claims={"sub": "https://betpredz.vercel.app"}, ttl=3600)
        print("App notification sent")
    except Exception as error:
        print(f"App notification failed ({error}); the slips are published anyway")


def main() -> None:
    if "--test" in sys.argv:          # "Run workflow" with mode test-notify: checks the whole chain
        send_push("BetPredz notifications are on ✓", "You will get a message when each day's slips are final.")
        return
    built = message(json.loads(PREDICTIONS.read_text(encoding="utf-8")), datetime.now(timezone.utc))
    if not built:
        print("No final slips today: nothing to notify")
        return
    title, body = built
    send_push(title, body)
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        print("NTFY_TOPIC not set: ntfy skipped")
        return
    request = urllib.request.Request(f"https://ntfy.sh/{topic}", data=body.encode("utf-8"), method="POST",
                                     headers={"Title": title.encode("utf-8"), "Click": APP_URL, "Tags": "soccer"})
    try:
        urllib.request.urlopen(request, timeout=20)
        print("Notification sent")
    except Exception as error:
        print(f"Notification failed ({error}); the slips are published anyway")


if __name__ == "__main__":
    main()
