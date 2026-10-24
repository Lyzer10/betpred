"""Fetch cached Understat league results and credited goal events."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
import argparse

import pandas as pd
from understatapi import UnderstatClient

from .fetch_results import START_SEASON, current_season_start, season_label
from .team_names import canonical_team
from .leagues import get_league, paths

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "understat"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def fetch_season(year: int, refresh: bool = False, league="EPL") -> tuple[list[dict], dict[str, dict]]:
    """Return league results and shots by match id, using per season caches.

    refresh re-downloads the results list; shots are only fetched for new matches.
    """
    selected = get_league(league)
    results_path = paths(selected).understat_file(year, "results")
    shots_path = paths(selected).understat_file(year, "shots")
    if results_path.exists() and shots_path.exists() and not refresh:
        return json.loads(results_path.read_text(encoding="utf-8")), json.loads(shots_path.read_text(encoding="utf-8"))

    with UnderstatClient() as client:
        if results_path.exists() and not refresh:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        else:
            results = client.league(league=selected.understat_name).get_match_data(season=str(year))
            _write_json(results_path, results)
            time.sleep(random.uniform(1, 2))

        shots = json.loads(shots_path.read_text(encoding="utf-8")) if shots_path.exists() else {}
        changed = False
        for match in results:
            if not match.get("isResult", False):
                continue
            match_id = str(match["id"])
            if match_id in shots:
                continue
            shots[match_id] = client.match(match=match_id).get_shot_data()
            changed = True
            # Checkpoint each response so an interrupted long first run resumes.
            _write_json(shots_path, shots)
            time.sleep(random.uniform(1, 2))
        if changed or not shots_path.exists():
            _write_json(shots_path, shots)
    return results, shots


def _side_name(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("title") or value.get("name"))
    return str(value)


def normalize_season(year: int, results: list[dict], shots: dict[str, dict], league="EPL") -> tuple[pd.DataFrame, pd.DataFrame]:
    matches, goals = [], []
    for match in results:
        if not match.get("isResult", False):
            continue
        match_id = str(match["id"])
        home = canonical_team(_side_name(match["h"]), league)
        away = canonical_team(_side_name(match["a"]), league)
        xg = match.get("xG", {})
        matches.append({"understat_id": match_id, "date": pd.to_datetime(match["datetime"]),
                        "season": season_label(year), "home_team": home, "away_team": away,
                        "home_xg": pd.to_numeric(xg.get("h"), errors="coerce"),
                        "away_xg": pd.to_numeric(xg.get("a"), errors="coerce")})
        event_groups = shots.get(match_id, {})
        for side, team in (("h", "home"), ("a", "away")):
            for event in event_groups.get(side, []):
                result = str(event.get("result", "")).lower()
                if result in {"goal", "owngoal"}:
                    credited_team = ({"home": "away", "away": "home"}[team]
                                     if result == "owngoal" else team)
                    goals.append({"understat_id": match_id, "minute": int(float(event["minute"])), "team": credited_team})
    return pd.DataFrame(matches, columns=["understat_id", "date", "season", "home_team", "away_team", "home_xg", "away_xg"]), pd.DataFrame(goals, columns=["understat_id", "minute", "team"])


def fetch_all(start: int = START_SEASON, end: int | None = None,
              refresh_current: bool = False, league="EPL") -> tuple[pd.DataFrame, pd.DataFrame]:
    current = current_season_start()
    end = current if end is None else end
    matches, goals = [], []
    for year in range(start, end + 1):
        results, shots = fetch_season(year, refresh_current and year == current, league)
        season_matches, season_goals = normalize_season(year, results, shots, league)
        matches.append(season_matches)
        goals.append(season_goals)
    return pd.concat(matches, ignore_index=True), pd.concat(goals, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="EPL")
    args = parser.parse_args()
    matches, goals = fetch_all(league=args.league)
    print(f"Loaded {len(matches):,} Understat matches and {len(goals):,} goals.")


if __name__ == "__main__":
    main()
