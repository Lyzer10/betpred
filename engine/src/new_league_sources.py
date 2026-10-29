"""Capture public source evidence for name mapping, badges and integration tests. Offline setup only."""
import json
import time

import requests

from .betpawa import BASE_URL, HEADERS
from .leagues import ENGINE_DIR
from .new_league_config import NEW_LEAGUES
from .team_names import canonical_team

FIXTURES = ENGINE_DIR / "tests" / "fixtures" / "new_leagues"


def capture():
    session = requests.Session()
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for code, (_, _, _, competition, slug) in NEW_LEAGUES.items():
        query = {"queries": [{"query": {"eventType": "UPCOMING", "categories": ["2"],
                 "zones": {"competitions": [str(competition)]}}, "take": 50}]}
        response = session.get(f"{BASE_URL}/events/lists/by-queries", params={"q": json.dumps(query)},
                               headers=HEADERS, timeout=30)
        response.raise_for_status()
        payload = response.json()
        (FIXTURES / f"{code}_betpawa.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(1)
        response = session.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/teams", timeout=30)
        response.raise_for_status()
        payload = response.json()
        (FIXTURES / f"{code}_teams.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        for item in payload["sports"][0]["leagues"][0]["teams"]:
            canonical_team(item["team"]["displayName"], code)
        time.sleep(1)
        response = session.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard",
                               params={"dates": "20261025"}, timeout=30)
        response.raise_for_status()
        (FIXTURES / f"{code}_completed.json").write_text(json.dumps(response.json(), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{code}: real Betpawa teams, ESPN teams/logos and completed-score responses captured", flush=True)


if __name__ == "__main__":
    capture()
