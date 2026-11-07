"""Task 23: Research-only price collection for 7 extra leagues.

Leagues: E1 Championship, I2 Serie B, D2 2. Bundesliga, F2 Ligue 2,
         SP2 Segunda, G1 Greece Super League, SC0 Scottish Premiership.

ISOLATION GUARANTEE:
- These leagues are RESEARCH ONLY and must NEVER appear in predictions, slips,
  best picks, tables, health checks, or calibrations.
- Failure of this module fails safely (prints one line and continues).
- Output files are strictly confined to engine/data/live/research/.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .betpawa import (BASE_URL as BETPAWA_BASE_URL, HEADERS as BETPAWA_HEADERS, PAUSE_SECONDS,
                      RESEARCH_MARKETS, parse_markets)
from .calibration import ENGINE_DIR
from .goal_minute_check import parse_espn_summary_goals

RESEARCH_DIR = ENGINE_DIR / "data" / "live" / "research"
PRICES_DIR = RESEARCH_DIR / "prices"
RESULTS_PATH = RESEARCH_DIR / "results.csv"
ALIASES_PATH = Path(__file__).resolve().parent / "research_aliases.json"

# Div -> (name, country, betpawa_comp_id, espn_slug)
RESEARCH_LEAGUES: dict[str, tuple[str, str, int | None, str]] = {
    "E1": ("Championship", "England", 12101, "eng.2"),
    "I2": ("Serie B", "Italy", 12241, "ita.2"),
    "D2": ("2. Bundesliga", "Germany", 12091, "ger.2"),
    "F2": ("Ligue 2", "France", None, "fra.2"),
    "SP2": ("Segunda", "Spain", 12142, "esp.2"),
    "G1": ("Super League 1", "Greece", 12332, "gre.1"),
    "SC0": ("Premiership", "Scotland", 12281, "sco.1"),
}

aliases_data = json.loads(ALIASES_PATH.read_text(encoding="utf-8")) if ALIASES_PATH.exists() else {}
RESEARCH_TEAM_ALIASES: dict[tuple[str, str], str] = {
    tuple(k.split(":::", 1)): v for k, v in aliases_data.items()
}


def normalize_research_team(name: str, league: str) -> str | None:
    """Normalize team name for research leagues. Return None if unmapped (logged, never guessed)."""
    cleaned = str(name).strip()
    return RESEARCH_TEAM_ALIASES.get((league, cleaned))


def _to_utc_timestamp(ts: pd.Timestamp) -> pd.Timestamp:
    if ts.tz is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def _to_eat_timestamp(ts: pd.Timestamp) -> pd.Timestamp:
    return _to_utc_timestamp(ts).tz_convert("Africa/Dar_es_Salaam")


def should_collect_prices(now: pd.Timestamp) -> bool:
    """At most once per hour: skip if the latest research snapshot is < 55 minutes old."""
    if not PRICES_DIR.exists():
        return True
    files = sorted(PRICES_DIR.glob("*.csv"))
    if not files:
        return True
    try:
        latest = pd.read_csv(files[-1])
        if latest.empty or "snapshot_utc" not in latest.columns:
            return True
        last_time = pd.to_datetime(latest["snapshot_utc"]).max()
        if pd.isna(last_time):
            return True
        last_utc = _to_utc_timestamp(pd.Timestamp(last_time))
        cur_utc = _to_utc_timestamp(now)
        return (cur_utc - last_utc).total_seconds() >= 55 * 60
    except Exception:
        return True


def consensus_lookup(fixtures_df: pd.DataFrame | None) -> dict[tuple[str, str, str], dict[str, Any]]:
    """(Div, home, away) -> football-data average odds for the research leagues."""
    lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    if fixtures_df is None or fixtures_df.empty:
        return lookup
    # Rows as dicts: itertuples() renames columns such as "Avg>2.5" and would silently drop them.
    for r in fixtures_df.to_dict("records"):
        div = r.get("Div")
        if div not in RESEARCH_LEAGUES:
            continue
        h = normalize_research_team(r.get("HomeTeam"), div)
        a = normalize_research_team(r.get("AwayTeam"), div)
        if h and a:
            lookup[(div, h, a)] = {col: r.get(col) for col in ("AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5")}
    return lookup


def collect_research_prices(
    now: pd.Timestamp,
    fixtures_df: pd.DataFrame | None = None,
    session: requests.Session | None = None,
) -> int:
    """Collect Betpawa prices for 30 RESEARCH_MARKETS on the 7 extra leagues.

    Fails safely: wraps all operations and logs cleanly.
    """
    if not should_collect_prices(now):
        print("Research league price collection: skipped (snapshot is < 55 minutes old)")
        return 0

    session = session or requests.Session()
    PRICES_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    now_utc = _to_utc_timestamp(now)
    eat_date = _to_eat_timestamp(now).strftime("%Y-%m-%d")
    eat_iso = _to_eat_timestamp(now).isoformat()
    horizon_utc = now_utc + pd.Timedelta(hours=48)

    fd_lookup = consensus_lookup(fixtures_df)

    for div, (name, country, cid, slug) in RESEARCH_LEAGUES.items():
        if cid is None:
            continue
        time.sleep(PAUSE_SECONDS)
        q = {"queries": [{"query": {"eventType": "UPCOMING", "categories": ["2"],
                         "zones": {"competitions": [str(cid)]}}, "take": 50}]}
        try:
            res = session.get(f"{BETPAWA_BASE_URL}/events/lists/by-queries",
                             params={"q": json.dumps(q)},
                             headers=BETPAWA_HEADERS, timeout=30)
            if not res.ok:
                print(f"Research prices {div}: list HTTP {res.status_code}; skipping")
                continue
            events = res.json().get("responses", [{}])[0].get("responses", [])
        except Exception as err:
            print(f"Research prices {div}: list error ({err}); skipping")
            continue

        for ev in events:
            kickoff = _to_utc_timestamp(pd.Timestamp(ev["startTime"]))
            if kickoff <= now_utc or kickoff > horizon_utc:
                continue
            parts = sorted(ev.get("participants", []), key=lambda p: p.get("position", 0))
            if len(parts) < 2:
                continue
            h_raw = parts[0]["name"]
            a_raw = parts[1]["name"]
            home = normalize_research_team(h_raw, div)
            away = normalize_research_team(a_raw, div)
            if not home or not away:
                print(f"Research prices {div}: unmapped team in event {ev['id']} ({h_raw} v {a_raw}); skipping")
                continue
            time.sleep(PAUSE_SECONDS)
            try:
                det_res = session.get(f"{BETPAWA_BASE_URL}/events/{ev['id']}",
                                      headers=BETPAWA_HEADERS, timeout=30)
                if not det_res.ok:
                    continue
                detail = det_res.json()
            except Exception as err:
                print(f"Research prices {div}: detail error event {ev['id']} ({err}); skipping")
                continue

            markets_map = parse_markets(detail.get("markets", []))
            consensus = fd_lookup.get((div, home, away), {})

            core_markets = ("home_win", "draw", "away_win", "over_2.5", "under_2.5")
            logged_markets = core_markets + RESEARCH_MARKETS

            for mkt in logged_markets:
                odds_val = markets_map.get(mkt)
                if odds_val is None:
                    continue
                rows.append({
                    "snapshot_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "snapshot_eat": eat_iso,
                    "league": div,
                    "league_name": name,
                    "home": home,
                    "away": away,
                    "kickoff_utc": kickoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "market": mkt,
                    "betpawa_odds": odds_val,
                    "consensus_avgh": consensus.get("AvgH"),
                    "consensus_avgd": consensus.get("AvgD"),
                    "consensus_avga": consensus.get("AvgA"),
                    "consensus_over25": consensus.get("Avg>2.5"),
                    "consensus_under25": consensus.get("Avg<2.5"),
                })

    if not rows:
        print("Research prices: 0 rows collected")
        return 0

    df_out = pd.DataFrame(rows)
    target_csv = PRICES_DIR / f"{eat_date}.csv"
    if target_csv.exists():
        existing = pd.read_csv(target_csv)
        combined = pd.concat([existing, df_out], ignore_index=True)
        combined = combined.drop_duplicates(subset=["snapshot_utc", "league", "home", "away", "market"])
        combined.to_csv(target_csv, index=False)
    else:
        df_out.to_csv(target_csv, index=False)

    print(f"Research prices: logged {len(rows)} prices to {target_csv.name}")
    return len(rows)


def settle_markets(
    home_ft: int, away_ft: int,
    home_ht: int | None, away_ht: int | None,
    goals: list[dict] | None,
) -> dict[str, bool | None]:
    """Settle research markets using pre-registered Task 15-20 rules."""
    outcomes: dict[str, bool | None] = {}
    total_ft = home_ft + away_ft

    # Core
    outcomes["home_win"] = bool(home_ft > away_ft)
    outcomes["draw"] = bool(home_ft == away_ft)
    outcomes["away_win"] = bool(home_ft < away_ft)
    outcomes["over_2.5"] = bool(total_ft > 2.5)
    outcomes["under_2.5"] = bool(total_ft < 2.5)

    # Team totals
    outcomes["home_over_0.5"] = bool(home_ft > 0.5)
    outcomes["home_over_1.5"] = bool(home_ft > 1.5)
    outcomes["away_over_0.5"] = bool(away_ft > 0.5)
    outcomes["away_over_1.5"] = bool(away_ft > 1.5)

    # DNB
    outcomes["dnb_home"] = True if home_ft > away_ft else (False if home_ft < away_ft else None)
    outcomes["dnb_away"] = True if away_ft > home_ft else (False if away_ft < home_ft else None)

    # Half markets (a half-time score larger than the final score is a data error: unsettled)
    if home_ht is not None and away_ht is not None and not (0 <= home_ht <= home_ft and 0 <= away_ht <= away_ft):
        home_ht = away_ht = None
    if home_ht is not None and away_ht is not None:
        home_sh, away_sh = home_ft - home_ht, away_ft - away_ht
        total_sh, total_ht = home_sh + away_sh, home_ht + away_ht
        outcomes["fh_over_0.5"] = bool(total_ht > 0.5)
        outcomes["fh_over_1.5"] = bool(total_ht > 1.5)
        outcomes["sh_over_0.5"] = bool(total_sh > 0.5)
        outcomes["sh_over_1.5"] = bool(total_sh > 1.5)
        outcomes["home_win_either_half"] = bool((home_ht > away_ht) or (home_sh > away_sh))
        outcomes["away_win_either_half"] = bool((away_ht > home_ht) or (away_sh > home_sh))
        outcomes["home_score_both_halves"] = bool((home_ht > 0) and (home_sh > 0))
        outcomes["away_score_both_halves"] = bool((away_ht > 0) and (away_sh > 0))
        outcomes["home_win_both_halves"] = bool((home_ht > away_ht) and (home_sh > away_sh))
        outcomes["away_win_both_halves"] = bool((away_ht > home_ht) and (away_sh > home_sh))
        outcomes["home_fh_over_0.5"] = bool(home_ht > 0.5)
        outcomes["away_fh_over_0.5"] = bool(away_ht > 0.5)
        outcomes["home_sh_over_0.5"] = bool(home_sh > 0.5)
        outcomes["away_sh_over_0.5"] = bool(away_sh > 0.5)

    # Goal-timing, 1up, 2up, interval_10, first_goal: only when ESPN's goal list is complete
    # (every goal assigned to a side and the per-side counts equal the final score). Never inferred.
    if goals is not None:
        goals = sorted(goals, key=lambda g: (g["period"], g["seconds"]))
        complete = (all(g["side"] in ("home", "away") for g in goals)
                    and sum(g["side"] == "home" for g in goals) == home_ft
                    and sum(g["side"] == "away" for g in goals) == away_ft)
        if not complete:
            goals = None
    if goals is not None:
        # First goal
        if len(goals) > 0:
            first = goals[0]["side"]
            outcomes["first_goal_home"] = bool(first == "home")
            outcomes["first_goal_away"] = bool(first == "away")
        else:
            outcomes["first_goal_home"] = False
            outcomes["first_goal_away"] = False

        # Interval 1-10 minutes (< 600s in period 1)
        goals_10 = [g for g in goals if g["period"] == 1 and g["seconds"] < 600]
        h10 = sum(1 for g in goals_10 if g["side"] == "home")
        a10 = sum(1 for g in goals_10 if g["side"] == "away")
        outcomes["interval_10_home"] = bool(h10 > a10)
        outcomes["interval_10_draw"] = bool(h10 == a10)
        outcomes["interval_10_away"] = bool(a10 > h10)

        # 1UP and 2UP tracking
        h = a = 0
        h_ever_1up = a_ever_1up = False
        h_ever_2up = a_ever_2up = False
        for g in goals:
            if g["side"] == "home":
                h += 1
            else:
                a += 1
            if h > a:
                h_ever_1up = True
            if a > h:
                a_ever_1up = True
            if h - a >= 2:
                h_ever_2up = True
            if a - h >= 2:
                a_ever_2up = True

        # DECISION CORRECTION: 2UP wins if ever 2 ahead OR team won
        outcomes["home_2up"] = bool(h_ever_2up or home_ft > away_ft)
        outcomes["away_2up"] = bool(a_ever_2up or away_ft > home_ft)

        # DC1UP: wins if team 1UP or suitable FT condition
        outcomes["dc1up_1x"] = bool(h_ever_1up or home_ft >= away_ft)
        outcomes["dc1up_x2"] = bool(a_ever_1up or away_ft >= home_ft)
        outcomes["dc1up_12"] = bool((h_ever_1up or a_ever_1up) or home_ft != away_ft)

    return outcomes


ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"
ESPN_HEADERS = {"User-Agent": "BetPredz research", "Accept": "application/json"}
# Betpawa research prices exist from this day (engine/data/live/prices/2026-10-25.csv): settle from here.
BACKFILL_START = pd.Timestamp("2026-10-25", tz="UTC")
RECENT_DAYS = 3                 # after the backfill, look back this many days each settlement
SETTLE_EVERY = pd.Timedelta(hours=3)
MAX_REQUESTS = 150              # ESPN requests per settlement run (the backfill finishes over a few runs)
LAST_SETTLEMENT_PATH = RESEARCH_DIR / "last_settlement.txt"
RESULT_COLUMNS = ["match_id", "league", "home", "away", "kickoff", "FT", "HT", "goals_complete"]


def _settlement_targets() -> list[tuple[str, str, Any]]:
    """(league code, ESPN slug, ESPN event -> (home, away) or None) for the 7 research + 9 live leagues.

    Live leagues use the same name mapping as the line-ups (lineups.event_teams), so names equal the
    names in engine/data/live/prices. Live leagues are settled here for research markets only.
    """
    from .lineups import SLUGS, event_teams

    def research_teams(event: dict, div: str) -> tuple[str, str] | None:
        sides = {c.get("homeAway"): normalize_research_team(c.get("team", {}).get("displayName", ""), div)
                 for c in event["competitions"][0]["competitors"]}
        return (sides["home"], sides["away"]) if sides.get("home") and sides.get("away") else None

    def live_teams(event: dict, code: str) -> tuple[str, str] | None:
        try:
            return event_teams(event, code)
        except (ValueError, KeyError):
            return None

    targets: list[tuple[str, str, Any]] = [(div, slug, lambda ev, d=div: research_teams(ev, d))
                                           for div, (_n, _c, _cid, slug) in RESEARCH_LEAGUES.items()]
    targets += [(code, slug, lambda ev, c=code: live_teams(ev, c)) for code, slug in SLUGS.items()]
    return targets


def _due(now: pd.Timestamp) -> bool:
    try:
        last = pd.Timestamp(LAST_SETTLEMENT_PATH.read_text(encoding="utf-8").strip())
        return _to_utc_timestamp(now) - _to_utc_timestamp(last) >= SETTLE_EVERY
    except (OSError, ValueError):
        return True


def settle_research_events(now: pd.Timestamp, session: requests.Session | None = None, force: bool = False) -> int:
    """Record full-time, half-time and goal-time outcomes from ESPN into results.csv (research only)."""
    if not force and not _due(now):
        print("Research settlement: skipped (last run < 3 hours ago)")
        return 0
    session = session or requests.Session()
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    now_utc = _to_utc_timestamp(now)
    if RESULTS_PATH.exists():
        existing = pd.read_csv(RESULTS_PATH, dtype=str).fillna("")
    else:
        existing = pd.DataFrame(columns=RESULT_COLUMNS)
    done_ids = set(existing.loc[existing.goals_complete.eq("1") & existing.HT.ne(""), "match_id"])
    seen_leagues = set(existing.league)

    requests_left = MAX_REQUESTS
    rows: list[dict[str, Any]] = []
    unmapped: list[str] = []
    for code, slug, teams_of in _settlement_targets():
        recent = now_utc.normalize() - pd.Timedelta(days=RECENT_DAYS)
        start = BACKFILL_START if code not in seen_leagues else max(BACKFILL_START, recent)
        for day in pd.date_range(start.normalize(), now_utc.normalize(), freq="D"):
            if requests_left <= 0:
                break
            time.sleep(PAUSE_SECONDS)
            requests_left -= 1
            try:   # ESPN accepts one day per request (date ranges return HTTP 400, checked 2026-11-08)
                res = session.get(f"{ESPN_BASE}/{slug}/scoreboard", params={"dates": day.strftime("%Y%m%d")},
                                  headers=ESPN_HEADERS, timeout=20)
                events = res.json().get("events", []) if res.ok else []
            except (requests.RequestException, ValueError) as err:
                print(f"Research settlement {code} {day.date()}: scoreboard unavailable ({err})")
                continue
            for ev in events:
                if not ev.get("status", {}).get("type", {}).get("completed") or str(ev.get("id")) in done_ids:
                    continue
                teams = teams_of(ev)
                if teams is None:
                    unmapped.append(f"{code}: {ev.get('name', ev.get('id'))}")
                    continue
                if requests_left <= 0:
                    break
                time.sleep(PAUSE_SECONDS)
                requests_left -= 1
                try:
                    s_res = session.get(f"{ESPN_BASE}/{slug}/summary", params={"event": ev["id"]},
                                        headers=ESPN_HEADERS, timeout=20)
                    if not s_res.ok:
                        continue
                    row = _result_row(s_res.json(), code, teams, ev)
                except (requests.RequestException, ValueError, KeyError, StopIteration, TypeError) as err:
                    print(f"Research settlement {code}: summary {ev.get('id')} unusable ({err})")
                    continue
                rows.append(row)
                done_ids.add(row["match_id"])

    if requests_left > 0:      # every league reached today: next settlement after SETTLE_EVERY
        LAST_SETTLEMENT_PATH.write_text(now_utc.isoformat(), encoding="utf-8")
    if unmapped:
        print(f"Research settlement: {len(unmapped)} completed matches skipped, team names not mapped: "
              + "; ".join(sorted(set(unmapped))[:20]))
    if not rows:
        print("Research settlement: 0 new completed matches")
        return 0
    combined = pd.concat([existing, pd.DataFrame(rows).astype(str)], ignore_index=True)
    combined = combined.drop_duplicates(subset=["match_id"], keep="last").sort_values(["kickoff", "league", "home"])
    combined.to_csv(RESULTS_PATH, index=False)
    print(f"Research settlement: recorded {len(rows)} matches ({requests_left} ESPN requests unused)")
    return len(rows)


def _result_row(summary: dict, code: str, teams: tuple[str, str], event: dict) -> dict[str, Any]:
    comp = summary["header"]["competitions"][0]
    sides = {c["homeAway"]: c for c in comp["competitors"]}
    home_ft, away_ft = int(sides["home"]["score"]), int(sides["away"]["score"])
    home_ht = away_ht = None
    hl, al = sides["home"].get("linescores") or [], sides["away"].get("linescores") or []
    if hl and al:     # linescores[0] = first half (checked against real summaries, task 23 review)
        try:
            home_ht, away_ht = int(hl[0]["displayValue"]), int(al[0]["displayValue"])
        except (KeyError, ValueError, TypeError):
            home_ht = away_ht = None
    goals = [{"side": g.team, "seconds": g.seconds, "period": g.period} for g in parse_espn_summary_goals(summary)]
    outcomes = settle_markets(home_ft, away_ft, home_ht, away_ht, goals)
    row = {"match_id": str(event["id"]), "league": code, "home": teams[0], "away": teams[1],
           "kickoff": str(event.get("date", "")), "FT": f"{home_ft}-{away_ft}",
           "HT": f"{home_ht}-{away_ht}" if outcomes.get("fh_over_0.5") is not None else "",
           "goals_complete": "1" if outcomes.get("interval_10_draw") is not None else "0"}
    for m in sorted(RESEARCH_MARKETS):
        val = outcomes.get(m)
        row[m] = "1" if val is True else ("0" if val is False else "")
    return row


def run_research_safely(now: pd.Timestamp, fixtures_df: pd.DataFrame | None) -> None:
    """Called by predict.main: research collection and settlement can never break the main run."""
    for step, call in (("collection", lambda: collect_research_prices(now, fixtures_df)),
                       ("settlement", lambda: settle_research_events(now))):
        try:
            call()
        except Exception as error:   # noqa: BLE001 - research only, the betting run must continue
            print(f"Research {step} unavailable ({error})")


if __name__ == "__main__":
    now = pd.Timestamp.now(tz=timezone.utc)
    print(f"Running research leagues at {now.isoformat()}...")
    collect_research_prices(now)
    settle_research_events(now, force=True)
