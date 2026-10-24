"""Phone notification after the final run: today's final slips.

Two channels, each used when its secrets exist (a failed notification never fails the run):
  - app: Web Push to the BetPredz app itself. Secrets VAPID_PRIVATE_KEY (pairs with the public key in
    web/src/push.ts) and PUSH_SUBSCRIPTION (the code the app shows under Money -> Notifications).
  - ntfy (https://ntfy.sh): the ntfy app subscribed to the topic in secret NTFY_TOPIC.
"""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PREDICTIONS = Path(__file__).resolve().parents[1] / "web" / "public" / "data" / "predictions.json"
EAT = timezone(timedelta(hours=3))
APP_URL = "https://betpredz.vercel.app"


def message(published: dict, now: datetime) -> tuple[str, str] | None:
    today = now.astimezone(EAT).date().isoformat()
    day = next((d for d in published.get("days", []) if d["date"] == today and d.get("final")), None)
    if not day:
        return None
    first = datetime.fromisoformat(day["first_kickoff_utc"].replace("Z", "")).replace(tzinfo=timezone.utc)
    lines = [f"{tier.title()}: odds {slip['total_odds']:.2f} · {slip['win_probability']:.0%} chance · {len(slip['legs'])} matches"
             for tier, slip in day["slips"].items() if slip.get("final")]
    if not lines:
        return None
    title = f"Today's bets are final · first match {first.astimezone(EAT):%H:%M}"
    return title, "\n".join(lines)


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
