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

    # Index football-data fixtures for consensus odds matching
    fd_lookup: dict[tuple[str, str, str], dict[str, float]] = {}
    if fixtures_df is not None and not fixtures_df.empty:
        for r in fixtures_df.itertuples():
            div = getattr(r, "Div", None)
            if div not in RESEARCH_LEAGUES:
                continue
            h_raw = getattr(r, "HomeTeam", None)
            a_raw = getattr(r, "AwayTeam", None)
            h = normalize_research_team(h_raw, div)
            a = normalize_research_team(a_raw, div)
            if not h or not a:
                continue
            fd_lookup[(div, h, a)] = {
                "AvgH": getattr(r, "AvgH", None),
                "AvgD": getattr(r, "AvgD", None),
                "AvgA": getattr(r, "AvgA", None),
                "Avg>2.5": getattr(r, "Avg_over25", getattr(r, "Avg>2.5", None)),
                "Avg<2.5": getattr(r, "Avg_under25", getattr(r, "Avg<2.5", None)),
            }

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
    home_sh = (home_ft - home_ht) if home_ht is not None else None
    away_sh = (away_ft - away_ht) if away_ht is not None else None
    total_sh = (home_sh + away_sh) if home_sh is not None and away_sh is not None else None
    total_ht = (home_ht + away_ht) if home_ht is not None and away_ht is not None else None

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

    # Half markets
    if home_ht is not None and away_ht is not None:
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

    # Goal-timing, 1up, 2up, interval_10, first_goal
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


def settle_research_events(now: pd.Timestamp, session: requests.Session | None = None) -> int:
    """Query ESPN completed events and settle markets into results.csv."""
    session = session or requests.Session()
    headers = {"User-Agent": "BetPredz research", "Accept": "application/json"}
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    settled_keys: set[tuple[str, str, str, str]] = set()
    if RESULTS_PATH.exists():
        try:
            existing_df = pd.read_csv(RESULTS_PATH, dtype=str)
            for r in existing_df.itertuples():
                ht_val = getattr(r, "HT", "")
                if pd.notna(ht_val) and str(ht_val).strip() != "":
                    settled_keys.add((str(r.league), str(r.home), str(r.away), str(r.kickoff)))
        except Exception:
            pass

    result_rows: list[dict[str, Any]] = []

    for div, (name, country, _cid, slug) in RESEARCH_LEAGUES.items():
        time.sleep(PAUSE_SECONDS)
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
        try:
            resp = session.get(url, headers=headers, timeout=20)
            if not resp.ok:
                continue
            board = resp.json()
        except Exception as err:
            print(f"Research settlement {div}: ESPN scoreboard error ({err})")
            continue

        events = board.get("events", [])
        for ev in events:
            status = ev.get("status", {}).get("type", {})
            if not status.get("completed"):
                continue

            comps = ev.get("competitions", [])
            if not comps:
                continue
            comp = comps[0]
            competitors = comp.get("competitors", [])
            home_c = next((c for c in competitors if c.get("homeAway") == "home"), None)
            away_c = next((c for c in competitors if c.get("homeAway") == "away"), None)
            if not home_c or not away_c:
                continue

            h_raw = home_c.get("team", {}).get("displayName", "")
            a_raw = away_c.get("team", {}).get("displayName", "")
            home = normalize_research_team(h_raw, div)
            away = normalize_research_team(a_raw, div)
            if not home or not away:
                print(f"Research settlement {div}: unmapped team ({h_raw} v {a_raw}); skipping")
                continue

            kickoff = ev.get("date", "")
            if (div, home, away, kickoff) in settled_keys:
                continue

            time.sleep(PAUSE_SECONDS)
            try:
                s_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/summary?event={ev['id']}"
                s_res = session.get(s_url, headers=headers, timeout=20)
                if not s_res.ok:
                    continue
                s_json = s_res.json()
            except Exception as err:
                print(f"Research settlement {div}: summary error event {ev['id']} ({err})")
                continue

            header_comps = s_json.get("header", {}).get("competitions", [])
            if not header_comps:
                continue
            h_comp = header_comps[0]
            h_competitors = h_comp.get("competitors", [])
            h_home_c = next((c for c in h_competitors if c.get("homeAway") == "home"), None)
            h_away_c = next((c for c in h_competitors if c.get("homeAway") == "away"), None)
            if not h_home_c or not h_away_c:
                continue

            try:
                home_ft = int(h_home_c.get("score", 0))
                away_ft = int(h_away_c.get("score", 0))
            except (ValueError, TypeError):
                continue

            home_ls = h_home_c.get("linescores", [])
            away_ls = h_away_c.get("linescores", [])
            home_ht = away_ht = None
            if home_ls and away_ls:
                try:
                    home_ht = int(home_ls[0].get("displayValue"))
                    away_ht = int(away_ls[0].get("displayValue"))
                except (ValueError, TypeError):
                    home_ht = away_ht = None

            g_objs = parse_espn_summary_goals(s_json)
            goals = [{"side": g.team, "seconds": g.seconds, "period": g.period} for g in g_objs]

            outcomes = settle_markets(home_ft, away_ft, home_ht, away_ht, goals)
            row = {
                "match_id": str(ev["id"]),
                "league": div,
                "home": home,
                "away": away,
                "kickoff": kickoff,
                "FT": f"{home_ft}-{away_ft}",
                "HT": f"{home_ht}-{away_ht}" if home_ht is not None and away_ht is not None else "",
            }
            for m in sorted(RESEARCH_MARKETS):
                val = outcomes.get(m)
                row[m] = "1" if val is True else ("0" if val is False else "")
            result_rows.append(row)

    if not result_rows:
        print("Research settlement: 0 new completed matches found")
        return 0

    df_new = pd.DataFrame(result_rows)
    if RESULTS_PATH.exists():
        existing = pd.read_csv(RESULTS_PATH, dtype=str)
        combined = pd.concat([existing, df_new], ignore_index=True)
        combined = combined.drop_duplicates(subset=["league", "home", "away", "kickoff"], keep="last")
        combined.to_csv(RESULTS_PATH, index=False)
    else:
        df_new.to_csv(RESULTS_PATH, index=False)

    print(f"Research settlement: recorded {len(result_rows)} matches to {RESULTS_PATH.name}")
    return len(result_rows)


if __name__ == "__main__":
    now = pd.Timestamp.now(tz=timezone.utc)
    print(f"Running research leagues at {now.isoformat()}...")
    prices_count = collect_research_prices(now)
    settled_count = settle_research_events(now)
    print(f"Done: {prices_count} prices, {settled_count} settled matches.")
