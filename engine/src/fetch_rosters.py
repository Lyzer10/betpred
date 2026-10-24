"""Download Understat match rosters (who played, minutes, xG, xA) for the injury study.

Cached per season in data/raw/understat/epl_<year>_rosters.json and checkpointed
after every match, so an interrupted run resumes where it stopped.
Usage: python -m src.fetch_rosters 2021 2026
"""
from __future__ import annotations

import json
import random
import sys
import time

from understatapi import UnderstatClient

from .fetch_understat import RAW_DIR, _write_json


def fetch_season_rosters(year: int, client: UnderstatClient) -> dict:
    results = json.loads((RAW_DIR / f"epl_{year}_results.json").read_text(encoding="utf-8"))
    path = RAW_DIR / f"epl_{year}_rosters.json"
    rosters = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    todo = [str(m["id"]) for m in results if m.get("isResult") and str(m["id"]) not in rosters]
    for count, match_id in enumerate(todo, 1):
        rosters[match_id] = client.match(match=match_id).get_roster_data()
        _write_json(path, rosters)
        if count % 50 == 0:
            print(f"{year}: {count}/{len(todo)}", flush=True)
        time.sleep(random.uniform(1, 2))
    return rosters


def main() -> None:
    start, end = (int(a) for a in sys.argv[1:3])
    with UnderstatClient() as client:
        for year in range(start, end + 1):
            rosters = fetch_season_rosters(year, client)
            print(f"{year}: {len(rosters)} matches cached", flush=True)


if __name__ == "__main__":
    main()
