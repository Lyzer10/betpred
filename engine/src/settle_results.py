"""Repair published results from ESPN, without fitting or selecting any bets.

Only completed regulation league matches with exact canonical teams and UTC date
are accepted. Scores settle score markets. Timing markets require a complete goal
sequence which reconciles to both final scores. Missing evidence stays unknown.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from .accumulators import LEG_MARKETS
from .football_only import parse_completed, score_actuals
from .leagues import ENGINE_DIR
from .lineups import ESPN, SLUGS
from .new_league_config import NEW_LEAGUES

CACHE = ENGINE_DIR / "data" / "raw" / "espn_results"
TIMING = ("home_1up", "away_1up", "home_first", "away_first")


def league_code(item):
    league = item.get("league", "EPL")
    return league["code"] if isinstance(league, dict) else league


def match_key(item):
    kickoff = pd.Timestamp(item.get("kickoff_utc", item["date"]))
    return league_code(item), kickoff.strftime("%Y-%m-%d"), item["home"], item["away"]


def parse_result(event: dict, league: str) -> dict | None:
    """ESPN credits own goals to the benefiting team. Never invert that credit."""
    status = event.get("status", {}).get("type", {})
    if status.get("name") != "STATUS_FULL_TIME":
        return None  # no abandoned matches, extra time, penalties or provisional scores
    frame = parse_completed({"events": [event]}, league)
    if frame.empty:
        return None
    from .predict import outcome
    row = frame.iloc[0]
    actuals = score_actuals(frame).iloc[0]
    outcomes = {market: outcome(actuals, market) for market in LEG_MARKETS}
    competition = event["competitions"][0]
    sides = {str(c["team"]["id"]): c["homeAway"] for c in competition["competitors"]}
    goals = []
    valid = True
    for detail in competition.get("details", []):
        if not detail.get("scoringPlay"):
            continue
        side = sides.get(str(detail.get("team", {}).get("id")))
        clock = re.fullmatch(r"(\d+)'(?:\+(\d+)')?", detail.get("clock", {}).get("displayValue", ""))
        if side is None or clock is None or detail.get("shootout") or detail.get("scoreValue") != 1:
            valid = False
            break
        # Preserve ESPN's order within a minute, but do not guess ambiguous order.
        stamp = (int(clock[1]), int(clock[2] or 0), float(detail["clock"].get("value", 0)))
        goals.append((stamp, side))
    goals.sort(key=lambda goal: goal[0])
    valid &= all(a[0] != b[0] or a[1] == b[1] for a, b in zip(goals, goals[1:]))
    valid &= [sum(side == team for _, side in goals) for team in ("home", "away")] == [row.home_goals, row.away_goals]
    if valid:
        h = a = 0
        home_led = away_led = False
        for _, side in goals:
            h += side == "home"
            a += side == "away"
            home_led |= h > a
            away_led |= a > h
        outcomes.update(home_1up=home_led, away_1up=away_led,
                        home_first=bool(goals and goals[0][1] == "home"),
                        away_first=bool(goals and goals[0][1] == "away"))
    return {"date": row.date.strftime("%Y-%m-%d"), "league": league,
            "home": row.home_team, "away": row.away_team,
            "score": [int(row.home_goals), int(row.away_goals)], "outcomes": outcomes,
            "source": "ESPN", "event_id": str(event["id"])}


def needs_result(fixture):
    result = fixture.get("result", {})
    markets = [m for m in LEG_MARKETS if league_code(fixture) not in NEW_LEAGUES or m not in TIMING]
    return not result or any(result.get("outcomes", {}).get(m) is None for m in markets)


def fetch_pending(fixtures, now, cache=CACHE, session=None):
    """One polite request per needed league/day. A failed source cannot erase a result."""
    wanted = {match_key(f) for f in fixtures if needs_result(f)
              and pd.Timestamp(f.get("kickoff_utc", f["date"])).tz_localize(None) < now}
    found = {}
    session = session or requests.Session()
    for league, day in sorted({key[:2] for key in wanted}):
        if league not in SLUGS:
            continue
        path = cache / f"{league}_{day}.json"

        def read(board):
            if not isinstance(board, dict) or SLUGS[league] not in {entry.get("slug") for entry in board.get("leagues", [])}:
                raise ValueError("scoreboard league does not match requested competition")
            for event in board.get("events", []):
                try:
                    result = parse_result(event, league)
                    if result is not None:
                        key = (league, result["date"], result["home"], result["away"])
                        if key in wanted:
                            found[key] = result
                except (KeyError, TypeError, ValueError) as error:
                    print(f"{league} ESPN event {event.get('id')} skipped: {error}")

        if path.exists():
            try:
                read(json.loads(path.read_text(encoding="utf-8")))
            except (ValueError, TypeError) as error:
                print(f"{league} {day}: unusable ESPN cache ({error}); requesting fresh results")
        required = {key for key in wanted if key[:2] == (league, day)}
        if all(key in found and all(found[key]["outcomes"].get(m) is not None for m in LEG_MARKETS) for key in required):
            continue
        try:
            response = session.get(f"{ESPN}/{SLUGS[league]}/scoreboard",
                                   params={"dates": day.replace("-", "")}, timeout=20)
            response.raise_for_status()
            board = response.json()
            read(board)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
        except (requests.RequestException, ValueError) as error:
            print(f"{league} {day}: ESPN results unavailable ({error}); keeping existing results")
        finally:
            time.sleep(1)
    return found


def fill_result(existing, incoming):
    """Fill unknown fields only. Never replace an already settled official outcome."""
    if existing and existing["score"] != incoming["score"]:
        print(f"Score conflict for {incoming['home']} v {incoming['away']}; keeping existing result")
        return existing
    if not existing:
        return {key: incoming[key] for key in ("score", "outcomes", "source", "event_id")}
    result = {**existing, "outcomes": dict(existing["outcomes"])}
    for market, won in incoming["outcomes"].items():
        if result["outcomes"].get(market) is None:
            result["outcomes"][market] = won
    return result


def settle_slip(slip, results):
    for leg in slip["legs"]:
        result = results.get(match_key(leg))
        if result and leg.get("won") is None:
            leg["won"] = result["outcomes"].get(leg["market"])
    outcomes = [leg.get("won") for leg in slip["legs"]]
    slip["status"] = "lost" if False in outcomes else "pending" if None in outcomes else "won"


def repair(now=None, data_dir=None, history_path=None, cache=CACHE, session=None):
    from . import predict
    now = pd.Timestamp(now or datetime.now(timezone.utc)).tz_localize(None)
    data_dir = Path(data_dir or predict.WEB_DATA_PATH.parent)
    history_path = Path(history_path or predict.HISTORY_PATH)
    snapshots = {p: json.loads(p.read_text(encoding="utf-8"))
                 for p in sorted((data_dir / "archive").glob("20*.json"))}
    fixtures = [f for snapshot in snapshots.values() for f in snapshot["fixtures"]]
    incoming = fetch_pending(fixtures, now, cache, session)
    results = {}
    changed = 0
    for fixture in fixtures:
        key = match_key(fixture)
        before = fixture.get("result")
        if key in incoming:
            fixture["result"] = fill_result(before, incoming[key])
            changed += fixture["result"] != before
        if fixture.get("result"):
            results[key] = fixture["result"]
    for path, snapshot in snapshots.items():
        for slip in snapshot.get("slips", {}).values():
            settle_slip(slip, results)
        write_changed(path, snapshot)
    index = [{"date": s["date"], "fixtures": len(s["fixtures"]),
              "settled": sum(bool(f.get("result")) for f in s["fixtures"])}
             for s in reversed(list(snapshots.values()))]
    write_changed(data_dir / "archive" / "index.json", index)
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    for slip in history:
        settle_slip(slip, results)
    if history_path.exists():
        write_changed(history_path, history)
    output_path = data_dir / "predictions.json"
    if output_path.exists():
        output = json.loads(output_path.read_text(encoding="utf-8"))
        output["history"] = history
        output["archive"] = index
        for day in output.get("days", []):
            for slip in day.get("slips", {}).values():
                settle_slip(slip, results)
        published = {(r["date"], r["home"], r["away"]): r for r in output.get("results", [])}
        for (league, day, home, away), result in results.items():
            key = (day, home, away)
            if pd.Timestamp(day) >= now - pd.Timedelta(days=120):
                published[key] = {"date": day, "home": home, "away": away,
                                  "score": result["score"], "outcomes": result["outcomes"]}
        output["results"] = sorted(published.values(), key=lambda r: r["date"], reverse=True)
        # Do not recompute health, stakes, prices, picks or slip selection in this repair.
        write_changed(output_path, output)
    print(f"Results repair: {changed} archived matches updated; no predictions or selected bets changed")
    return changed


def write_changed(path, value):
    if path.exists() and json.loads(path.read_text(encoding="utf-8")) == value:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if path.name in ("predictions.json", "slip_history.json") else 1
    path.write_text(json.dumps(value, indent=indent), encoding="utf-8")


if __name__ == "__main__":
    repair()
