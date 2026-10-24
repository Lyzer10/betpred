"""Phone notification after the final run: today's final slips (standard library only).

Sent through ntfy (https://ntfy.sh, free, no account): install the ntfy app and subscribe to the
topic stored in the repository secret NTFY_TOPIC. Without the secret nothing is sent.
A failed notification never fails the run.
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


def main() -> None:
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    built = message(json.loads(PREDICTIONS.read_text(encoding="utf-8")), datetime.now(timezone.utc))
    if not built:
        print("No final slips today: nothing to notify")
        return
    if not topic:
        print("NTFY_TOPIC not set: notification skipped")
        return
    title, body = built
    request = urllib.request.Request(f"https://ntfy.sh/{topic}", data=body.encode("utf-8"), method="POST",
                                     headers={"Title": title.encode("utf-8"), "Click": APP_URL, "Tags": "soccer"})
    try:
        urllib.request.urlopen(request, timeout=20)
        print("Notification sent")
    except Exception as error:
        print(f"Notification failed ({error}); the slips are published anyway")


if __name__ == "__main__":
    main()
