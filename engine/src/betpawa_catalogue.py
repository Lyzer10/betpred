"""Task 18: Betpawa market catalogue across all 9 live leagues (read-only research).

Reads up to 3 real upcoming event detail responses per league from
engine/data/raw/betpawa/catalogue/ (or fetches them 1 s apart with
betpawa.HEADERS when missing or --refresh is given) and writes
engine/reports/betpawa_market_catalogue.md.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests

from .betpawa import BASE_URL, HEADERS, PAUSE_SECONDS
from .leagues import LEAGUES

ENGINE_DIR = Path(__file__).resolve().parents[1]
CATALOGUE_DIR = ENGINE_DIR / "data" / "raw" / "betpawa" / "catalogue"
REPORT_PATH = ENGINE_DIR / "reports" / "betpawa_market_catalogue.md"

HT_FT_IDS = {
    "3668", "3685", "3743", "3747", "3756", "3774", "3789", "3792", "3795",
    "3801", "3804", "3807", "3810", "3813", "3816", "3819", "4063",
    "4673", "4681", "4693", "4697", "4700", "4703", "4706",
    "4716", "4720", "4724", "4728", "4732", "4736",
    "4794", "4809", "4833", "4836", "4842",
    "4898", "4912", "4926", "4938", "4942", "4946", "4950",
    "4958", "4961", "4964", "4976", "4979", "4982", "5000", "5003", "5006",
    "5036", "5042", "5045", "5048", "5051",
    "1096755", "1096782", "1096805", "1096806", "1096807", "1096808", "1096809", "1096814",
    "3591790", "25451913", "25451920", "28000000", "28000007",
    "28000014", "28000021", "28000028", "28000035",
    "28000047", "28000065", "28000071", "28000077", "28000083",
    "28000089", "28000110", "28000113", "28000209", "28000228", "28000279", "28000869",
}
GOAL_MINUTE_IDS = {"4870", "80000", "28000173", "28000224", "28000810", "28000850"}
CORNERS_FT_IDS = {"1096783", "1096785", "1096787", "1096789", "1096793", "1096797", "1096803"}
CARDS_FT_IDS = {"1096764", "1096766", "1096768", "1096770", "1096774", "1096776", "1096778", "1096780"}


def fetch_catalogue_events(refresh: bool = False, max_per_league: int = 3) -> dict[str, list[dict]]:
    """Fetch or load up to `max_per_league` upcoming events per league across all 9 live leagues."""
    CATALOGUE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = CATALOGUE_DIR / "manifest.json"
    if manifest_path.exists() and not refresh:
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    session = requests.Session()
    summary: dict[str, list[dict]] = {}
    for code, league in LEAGUES.items():
        comp_id = str(league.betpawa_competition_id)
        query = {
            "queries": [{
                "query": {
                    "eventType": "UPCOMING",
                    "categories": ["2"],
                    "zones": {"competitions": [comp_id]},
                },
                "take": 50,
            }]
        }
        time.sleep(PAUSE_SECONDS)
        resp = session.get(
            f"{BASE_URL}/events/lists/by-queries",
            params={"q": json.dumps(query)},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        (CATALOGUE_DIR / f"list_{code}.json").write_text(json.dumps(resp.json(), indent=2), encoding="utf-8")
        events = resp.json()["responses"][0]["responses"][:max_per_league]
        summary[code] = []
        for ev in events:
            ev_id = str(ev["id"])
            ev_path = CATALOGUE_DIR / f"event_{code}_{ev_id}.json"
            if refresh or not ev_path.exists():
                time.sleep(PAUSE_SECONDS)
                det = session.get(f"{BASE_URL}/events/{ev_id}", headers=HEADERS, timeout=30)
                det.raise_for_status()
                ev_path.write_text(json.dumps(det.json(), indent=2), encoding="utf-8")
            summary[code].append({
                "id": ev_id,
                "name": ev.get("name"),
                "startTime": ev.get("startTime"),
            })
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def settlement_classification(mid: str) -> tuple[str, str]:
    """Return ('can we settle it from our data', 'historical outcomes available') for a marketType id."""
    if mid in HT_FT_IDS:
        return "HT-FT score", "all 9 leagues, 2014/15-2026/27 (13 seasons)"
    if mid in GOAL_MINUTE_IDS:
        return "goal minutes", "5 main leagues (EPL, LALIGA, SERIEA, BUNDES, LIGUE1), 2014/15-2026/27 (13 seasons)"
    if mid in CORNERS_FT_IDS:
        return (
            "corners HC,AC",
            "5 main leagues 2014/15-2026/27 (13 seasons); 4 new leagues (EREDIV, JUPILER, PRIMEIRA, SUPERLIG) 2017/18-2026/27 (10 seasons)",
        )
    if mid in CARDS_FT_IDS:
        if mid in ("1096766", "1096778", "1096780"):
            return (
                "cards HY,AY,HR,AR (red cards HR,AR; bench/post-whistle edge cases unrecorded)",
                "5 main leagues 2014/15-2026/27 (13 seasons); 4 new leagues 2017/18-2026/27 (10 seasons)",
            )
        if mid in ("1096764", "1096776"):
            return (
                "no (cards HY,AY,HR,AR do not separate straight red = 2 bookings from 2nd yellow->red = 2 bookings)",
                "none (football-data HY,AY,HR,AR lacks 2nd-yellow vs straight-red split)",
            )
        return (
            "no (rule unverified in marketType explainer; HY,AY,HR,AR also lacks 2nd-yellow split)",
            "none (rule unverified)",
        )
    return "no", "none"


def handicap_meaning(mid: str, handicaps: list) -> str:
    """Format handicap values and their verified meaning (`handicap / 4 = line`)."""
    non_null = [h for h in handicaps if h is not None]
    if not non_null:
        return "None"
    vals = sorted({int(h) if float(h).is_integer() else float(h) for h in non_null})
    lines = [f"{v}->{v / 4:g}" for v in vals]
    if mid in ("28000224", "129110"):
        return f"handicap/4 = goal number ({', '.join(lines)})"
    if mid in ("28000818", "28000819", "28000827"):
        return f"handicap/4 = stat threshold ({', '.join(lines)})"
    if mid in ("4716", "4720", "4724"):
        return f"handicap/4 = 3-way goal handicap ({', '.join(lines)})"
    if mid in ("3747", "3756", "3774", "1096785", "1096786"):
        return f"handicap/4 = Asian handicap line ({', '.join(lines)})"
    return f"handicap/4 = Over/Under line ({', '.join(lines)})"


def build_catalogue(manifest: dict[str, list[dict]] | None = None) -> tuple[list[dict], list[dict]]:
    """Aggregate all marketType entries across the fetched events."""
    if manifest is None:
        manifest = fetch_catalogue_events(refresh=False)
    events_flat = []
    by_id: dict[str, dict] = {}
    for code, evs in manifest.items():
        for ev in evs:
            ev_id = str(ev["id"])
            events_flat.append({"league": code, "id": ev_id, "name": ev.get("name"), "startTime": ev.get("startTime")})
            data = json.loads((CATALOGUE_DIR / f"event_{code}_{ev_id}.json").read_text(encoding="utf-8"))
            for m in data.get("markets", []):
                mt = m["marketType"]
                mid = str(mt["id"])
                entry = by_id.setdefault(mid, {
                    "id": mid,
                    "name": mt.get("name") or "",
                    "displayName": mt.get("displayName") or "",
                    "explainer": mt.get("explainer") or "",
                    "outcomes": set(),
                    "handicaps": set(),
                    "events": [],
                })
                entry["events"].append(f"{code}:{ev_id}")
                for r in m.get("row", []):
                    entry["handicaps"].add(r.get("handicap"))
                    for p in r.get("prices", []):
                        entry["outcomes"].add(p.get("name"))

    rows = []
    for mid in sorted(by_id, key=lambda x: int(x) if x.isdigit() else x):
        e = by_id[mid]
        outcomes_sorted = sorted(e["outcomes"])
        if len(outcomes_sorted) > 10:
            outcomes_str = f"{len(outcomes_sorted)} player/score outcomes ({', '.join(outcomes_sorted[:4])}, ...)"
        else:
            outcomes_str = ", ".join(outcomes_sorted)
        h_meaning = handicap_meaning(mid, list(e["handicaps"]))
        settle_col, hist_col = settlement_classification(mid)
        rows.append({
            "id": mid,
            "name": e["name"],
            "displayName": e["displayName"],
            "explainer": e["explainer"],
            "outcomes": outcomes_str,
            "handicaps": h_meaning,
            "event_count": len(e["events"]),
            "total_events": len(events_flat),
            "events": e["events"],
            "settleable": settle_col,
            "historical": hist_col,
        })
    return rows, events_flat


def write_report(refresh: bool = False) -> Path:
    manifest = fetch_catalogue_events(refresh=refresh)
    rows, events_flat = build_catalogue(manifest)
    total_ev = len(events_flat)

    lines = [
        "# Betpawa market catalogue across all 9 live leagues (PROJECT.md task 18)",
        "",
        f"Fetched **{total_ev}** upcoming events (up to 3 per league across all 9 live leagues, >= 1 s apart, `betpawa.HEADERS`).",
        f"Total distinct `marketType` IDs observed: **{len(rows)}**.",
        "",
        "## 1. Fetched events evidence",
        "| League | Event IDs (`name`, `startTime` UTC) |",
        "|---|---|",
    ]
    for code, evs in manifest.items():
        desc = "; ".join(f"`{e['id']}` ({e['name']}, {e['startTime']})" for e in evs)
        lines.append(f"| {code} | {desc} |")

    lines += [
        "",
        "## 2. Time-interval and goal-sequence markets search",
        "- **Only one clock-interval market exists on Betpawa**: `28000173` (`1X2 - from 1 to 10 minutes` | `1X2 | Interval 10 minutes (00:01-09:59)`), offered on **27/27** fetched events with outcomes `1`, `X`, `2` (`handicap: None`). Its explainer states: *\"Pick 1 (home team), X (draw), or 2 (away team). Only goals scored between 00:01 and 09:59 on the match clock count.\"*",
        "- **No 1-15 minute, 15-30 minute, \"goal before minute X\", or \"first goal time\" market exists** on any of the 27 fetched events across the 9 leagues.",
        "- **Goal-sequence markets offered**:",
        "  - `28000224` (`Goal` | `Next Goal (Goal {handicap})`): offered on **27/27** events with `handicap = 4` (`4 / 4 = 1`, i.e. Goal 1 / First Goal) and outcomes `1` (home scores first), `2` (away scores first), `None` (`displayName: \"No Goal\"`).",
        "  - `4870` (`Team To Score Last (3 way)`): offered on **27/27** events with outcomes `1`, `2`, `No Goal` (`handicap: None`).",
        "  - `129110` (`Goalscorer nr` | `Next Goalscorer - (Goal {handicap})`): player prop for Goal 1 (`handicap = 4`), offered on **27/27** events (not settleable from team-level data).",
        "",
        "## 3. Corners and bookings settlement rules (from Betpawa's published `marketType.explainer`)",
        "- **Corners (`1096783`..`1096804`)**:",
        "  - Betpawa's published `marketType.explainer` on `1096783`, `1096784`, `1096787`, `1096788`, `1096789`, `1096790`, `1096803`, `1096804`: *\"Corners awarded but not taken don't count. Result is based on regular playing time only - Overtime does not count.\"*",
        "  - Full-time corner markets (`1096783`, `1096785`, `1096787`, `1096789`, `1096793`, `1096797`, `1096803`) match football-data's `HC,AC` columns (`5 main leagues 2014/15-2026/27; 4 new leagues 2017/18-2026/27`). First-half corner markets (`1096784`, `1096786`, `1096788`, `1096790`, `1096794`, `1096802`, `1096804`) and Last Corner (`1096795`, `1096796`) cannot be settled from our data (`no`).",
        "- **Bookings and cards (`1096764`..`1096780`)**:",
        "  - On `1096764` (`Total Bookings Over/Under - FT`), `1096765` (`Total Bookings Over/Under - 1H`), `1096776` (`Total Bookings - FT`), and `1096777` (`Total Bookings - 1H`), Betpawa's published `marketType.explainer` states: *\"A yellow card counts as 1 booking and a red as 2 - a second yellow leading to a red still counts as 2, not 3. Cards for substituted players, the bench and the manager don't count.\"*",
        "  - Because football-data's `HY,AY,HR,AR` columns record only total yellow and red cards without distinguishing a straight red (`0Y + 1R = 2 bookings`) from a second-yellow dismissal (`1Y + 1R` in football-data, which Betpawa counts as `2 bookings`, not `1 + 2 = 3`), our historical data **cannot settle** `1096764` or `1096776` exactly (`no`).",
        "  - On `1096768`, `1096769`, `1096770`, `1096771`, `1096774`, `1096775` (`Total Bookings Home/Away` and `Team with most bookings 3 Way`), the `marketType.explainer` does not specify the card-point formula (**rule unverified** in those market explainers, and also unsettleable from `HY,AY,HR,AR`); we do not study them.",
        "  - On `1096766` (`Player Sent Off - FT`), `1096778` (`Player Sent Off Home - FT`), and `1096780` (`Player Sent Off Away - FT`), the explainer states: *\"Two yellow cards leading to a dismissal count. Cards shown at half time, after the match, or to players on the bench don't count. Based on normal time only.\"*",
        "",
        "## 4. Verification of the 10 new `RESEARCH_MARKETS` keys added in Task 18",
        "- `28000224` (`Goal` | `Next Goal (Goal {handicap})`): `row.handicap == 4` (`4 / 4 = 1`, Goal 1), outcomes `\"1\"`, `\"2\"`, `\"None\"` -> `first_goal_home` (`\"1\"`), `first_goal_away` (`\"2\"`).",
        "- `28000173` (`1X2 - from 1 to 10 minutes`): `row.handicap is None`, outcomes `\"1\"`, `\"X\"`, `\"2\"` -> `interval_10_home` (`\"1\"`), `interval_10_away` (`\"2\"`), alongside existing `interval_10_draw` (`\"X\"`).",
        "- `1096807` (`Score in both halves Home - FT`) & `1096814` (`Score in both halves Away - FT`): `row.handicap is None`, outcomes `\"Yes\"`, `\"No\"` -> `home_score_both_halves`, `away_score_both_halves` (`\"Yes\"`).",
        "- `1096805` (`Both halves win Home - FT`) & `1096808` (`Both halves win Away - FT`): `row.handicap is None`, outcomes `\"Yes\"`, `\"No\"` -> `home_win_both_halves`, `away_win_both_halves` (`\"Yes\"`).",
        "- `4964` (`Total Score Over/Under - 1H - Home Team`), `4961` (`Total Score Over/Under - 1H - Away Team`), `4982` (`Total Score Over/Under - 2H - Home Team`), `4979` (`Total Score Over/Under - 2H - Away Team`): `row.handicap == 2` (`2 / 4 = 0.5`), outcome `\"Over\"` -> `home_fh_over_0.5`, `away_fh_over_0.5`, `home_sh_over_0.5`, `away_sh_over_0.5`. (Note: 3 La Liga events also offer duplicate markets `28000110`/`28000113` `Score in First Half - Home/Away`, which are absent on 24/27 events and pay lower odds than `4964`/`4961` Over 0.5 on all 3 La Liga events.)",
        "",
        "## 5. Complete catalogue of all 128 `marketType` IDs",
        "| ID | Name | Display name | Outcome names | Handicap values & meaning (`handicap/4 = line`) | Offered | Evidence event IDs | Can we settle it from our data | Historical outcomes available |",
        "|---:|---|---|---|---|---:|---|---|---|",
    ]
    for r in rows:
        ev_preview = ", ".join(r["events"][:4])
        if len(r["events"]) > 4:
            ev_preview += f", ... ({len(r['events'])} total)"
        name_clean = r["name"].replace("|", "\\|")
        dname_clean = r["displayName"].replace("|", "\\|")
        out_clean = r["outcomes"].replace("|", "\\|")
        hcap_clean = r["handicaps"].replace("|", "\\|")
        lines.append(
            f"| `{r['id']}` | {name_clean} | {dname_clean} | {out_clean} | {hcap_clean} | "
            f"{r['event_count']}/{r['total_events']} | {ev_preview} | {r['settleable']} | {r['historical']} |"
        )
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    path = write_report(refresh=args.refresh)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
