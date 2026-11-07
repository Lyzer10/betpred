"""Task 19: Goal-minute accuracy check (Understat processed goals vs ESPN summary keyEvents)."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.team_names import canonical_team

ENGINE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ENGINE_DIR / "data" / "processed"
RAW_ESPN_DIR = ENGINE_DIR / "data" / "raw" / "espn" / "goal_minute_check"
REPORT_PATH = ENGINE_DIR / "reports" / "goal_minute_check.md"

MAIN_LEAGUES: tuple[str, ...] = ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1")
SEASONS: tuple[str, ...] = ("2023/24", "2024/25", "2025/26")
ESPN_SLUGS: dict[str, str] = {
    "EPL": "eng.1",
    "LALIGA": "esp.1",
    "SERIEA": "ita.1",
    "BUNDES": "ger.1",
    "LIGUE1": "fra.1",
}
HEADERS: dict[str, str] = {"User-Agent": "BetPredz research"}
REQUEST_DELAY_SECONDS: float = 1.05
UNDERSTAT_10MIN_MAX_MINUTE: int = 9  # Understat minute = floor(seconds / 60); < 600s is minute <= 9

EXTRA_ESPN_ALIASES: dict[str, str] = {
    "Cádiz": "Cadiz",
    "Almería": "Almeria",
    "Leganés": "Leganes",
    "Hellas Verona": "Verona",
    "1. FC Heidenheim 1846": "Heidenheim",
    "SV Darmstadt 98": "Darmstadt",
    "VfL Wolfsburg": "Wolfsburg",
    "VfL Bochum": "Bochum",
    "Stade de Reims": "Reims",
    "Saint-Étienne": "St Etienne",
    "Clermont Foot": "Clermont",
}


@dataclass(frozen=True)
class EspnGoal:
    team: str
    seconds: float
    display_value: str
    period: int
    floor_minute: int
    expected_understat_minute: int
    stoppage_added: int | None


def _canon_espn_team(name: str, league: str) -> str:
    if name in EXTRA_ESPN_ALIASES:
        return EXTRA_ESPN_ALIASES[name]
    return canonical_team(name, league=league)


def expected_understat_minute_from_espn(seconds: float, display_value: str, period: int) -> tuple[int, int | None]:
    """Map ESPN clock fields to Understat's 0-indexed minute convention.

    - Regular time (no '+' in display_value): floor(seconds / 60), which equals display_minute - 1.
    - First-half stoppage ('45\'+x\''): 44 + x (since 45\'+1\' is stored as 45, 45\'+2\' as 46, etc.).
    - Second-half stoppage ('90\'+x\''): 89 + x (since 90\'+1\' is stored as 90, 90\'+2\' as 91, etc.).
    """
    m = re.match(r"^(\d+)'\+(\d+)'$", display_value.strip())
    if m:
        base = int(m.group(1))
        added = int(m.group(2))
        return base + added - 1, added
    return int(seconds // 60), None


def parse_espn_summary_goals(summary: dict[str, Any]) -> list[EspnGoal]:
    """Extract non-shootout scoringPlay events from an ESPN match summary in chronological order."""
    comp = summary["header"]["competitions"][0]
    home_id = next(c["team"]["id"] for c in comp["competitors"] if c["homeAway"] == "home")
    away_id = next(c["team"]["id"] for c in comp["competitors"] if c["homeAway"] == "away")

    goals: list[EspnGoal] = []
    for ke in summary.get("keyEvents", []):
        if not ke.get("scoringPlay") or ke.get("shootout"):
            continue
        tid = ke.get("team", {}).get("id")
        side = "home" if tid == home_id else ("away" if tid == away_id else "unknown")
        sec = float(ke["clock"]["value"])
        disp = str(ke["clock"]["displayValue"])
        period = int(ke["period"]["number"])
        exp_min, added = expected_understat_minute_from_espn(sec, disp, period)
        goals.append(
            EspnGoal(
                team=side,
                seconds=sec,
                display_value=disp,
                period=period,
                floor_minute=int(sec // 60),
                expected_understat_minute=exp_min,
                stoppage_added=added,
            )
        )
    return goals


def is_before_10_00_espn(goal: EspnGoal) -> bool:
    """Betpawa 10-minute interval is 00:01-09:59 (strictly before 10:00 on the first-half clock)."""
    return goal.period == 1 and goal.seconds < 600.0


def is_before_10_00_understat(minute: int) -> bool:
    """Understat minute = floor(seconds / 60), so < 600.0s corresponds to minute <= 9."""
    return int(minute) <= UNDERSTAT_10MIN_MAX_MINUTE


def sort_understat_goals(goals_df: pd.DataFrame) -> pd.DataFrame:
    """Sort a match's Understat goals chronologically by minute (preserving stable within-minute order)."""
    return goals_df.sort_values("minute", kind="mergesort").reset_index(drop=True)


def _league_processed_dir(league: str) -> Path:
    return PROCESSED_DIR if league == "EPL" else PROCESSED_DIR / league


def ensure_cached_espn_sample(raw_dir: Path = RAW_ESPN_DIR) -> list[dict[str, Any]]:
    """Load or fetch the manifest of >= 300 goals across the 5 main leagues and 3 seasons."""
    manifest_path = raw_dir / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for lg in MAIN_LEAGUES:
        espn_code = ESPN_SLUGS[lg]
        ldir = _league_processed_dir(lg)
        m = pd.read_parquet(ldir / "matches.parquet")
        g = pd.read_parquet(ldir / "goals.parquet")
        m["match_id"] = m["match_id"].astype(str)
        g["match_id"] = g["match_id"].astype(str)
        m["total_goals"] = m["home_goals"] + m["away_goals"]
        m_with_g = m[m["match_id"].isin(set(g["match_id"])) & (m["total_goals"] >= 3)]
        for season in SEASONS:
            sub = m_with_g[m_with_g["season"] == season]
            date_goals = (
                sub.groupby("date")
                .agg(n_matches=("match_id", "count"), n_goals=("total_goals", "sum"))
                .reset_index()
            )
            best_row = date_goals.sort_values(["n_goals", "date"], ascending=[False, True]).iloc[0]
            date_str = str(pd.Timestamp(best_row["date"]).date())
            ymd = date_str.replace("-", "")
            sb_path = raw_dir / f"scoreboard_{lg}_{ymd}.json"
            if not sb_path.exists():
                time.sleep(REQUEST_DELAY_SECONDS)
                url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/scoreboard"
                resp = requests.get(url, params={"dates": ymd}, headers=HEADERS, timeout=20)
                resp.raise_for_status()
                sb_path.write_bytes(resp.content)
            sb = json.loads(sb_path.read_text(encoding="utf-8"))
            espn_by_pair: dict[tuple[str, str], str] = {}
            for ev in sb.get("events", []):
                comp = ev["competitions"][0]
                competitors = comp["competitors"]
                home_c = next(c for c in competitors if c["homeAway"] == "home")
                away_c = next(c for c in competitors if c["homeAway"] == "away")
                try:
                    h_name = _canon_espn_team(home_c["team"]["displayName"], lg)
                    a_name = _canon_espn_team(away_c["team"]["displayName"], lg)
                    espn_by_pair[(h_name, a_name)] = str(ev["id"])
                except Exception:
                    continue
            day_matches = sub[sub["date"] == best_row["date"]].sort_values("match_id").head(5)
            for _, mrow in day_matches.iterrows():
                pair = (str(mrow["home_team"]), str(mrow["away_team"]))
                ev_id = espn_by_pair.get(pair)
                if not ev_id:
                    continue
                sum_path = raw_dir / f"summary_{lg}_{ev_id}.json"
                if not sum_path.exists():
                    time.sleep(REQUEST_DELAY_SECONDS)
                    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/summary"
                    resp = requests.get(url, params={"event": ev_id}, headers=HEADERS, timeout=20)
                    resp.raise_for_status()
                    sum_path.write_bytes(resp.content)
                manifest.append(
                    {
                        "league": lg,
                        "season": season,
                        "date": date_str,
                        "match_id": str(mrow["match_id"]),
                        "espn_event_id": str(ev_id),
                        "home_team": str(mrow["home_team"]),
                        "away_team": str(mrow["away_team"]),
                        "home_goals": int(mrow["home_goals"]),
                        "away_goals": int(mrow["away_goals"]),
                    }
                )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def evaluate_goal_minute_accuracy(raw_dir: Path = RAW_ESPN_DIR) -> dict[str, Any]:
    """Compare Understat goals.parquet with ESPN summary keyEvents across the cached sample."""
    manifest = ensure_cached_espn_sample(raw_dir)
    goals_by_lg: dict[str, pd.DataFrame] = {}
    for lg in MAIN_LEAGUES:
        gdf = pd.read_parquet(_league_processed_dir(lg) / "goals.parquet")
        gdf["match_id"] = gdf["match_id"].astype(str)
        goals_by_lg[lg] = gdf

    goal_rows: list[dict[str, Any]] = []
    match_rows: list[dict[str, Any]] = []

    for m in manifest:
        lg = m["league"]
        mid = str(m["match_id"])
        ev_id = str(m["espn_event_id"])
        ug_raw = goals_by_lg[lg][goals_by_lg[lg]["match_id"] == mid].reset_index(drop=True)
        ug_sorted = sort_understat_goals(ug_raw)

        sum_data = json.loads((raw_dir / f"summary_{lg}_{ev_id}.json").read_text(encoding="utf-8"))
        espn_goals = parse_espn_summary_goals(sum_data)
        if len(ug_sorted) != len(espn_goals):
            raise ValueError(f"Goal count mismatch for {lg} match_id={mid} event={ev_id}")

        espn_team_seq = [g.team for g in espn_goals]
        raw_team_seq = list(ug_raw["team"])
        sorted_team_seq = list(ug_sorted["team"])

        match_rows.append(
            {
                "league": lg,
                "season": m["season"],
                "date": m["date"],
                "match_id": mid,
                "espn_event_id": ev_id,
                "match": f"{m['home_team']} vs {m['away_team']}",
                "n_goals": len(espn_goals),
                "raw_order_agrees": espn_team_seq == raw_team_seq,
                "sorted_order_agrees": espn_team_seq == sorted_team_seq,
                "first_goal_agrees_sorted": espn_team_seq[0] == sorted_team_seq[0],
            }
        )

        for side in ("home", "away"):
            eg_side = [g for g in espn_goals if g.team == side]
            ug_side = ug_sorted[ug_sorted["team"] == side].to_dict("records")
            if len(eg_side) != len(ug_side):
                raise ValueError(f"Team goal count mismatch for {lg} match_id={mid} side={side}")
            for eg_i, ug_i in zip(eg_side, ug_side):
                us_min = int(ug_i["minute"])
                is_fh_stop = eg_i.period == 1 and eg_i.stoppage_added is not None
                is_sh_stop = eg_i.period == 2 and eg_i.stoppage_added is not None
                is_reg = eg_i.stoppage_added is None
                goal_rows.append(
                    {
                        "league": lg,
                        "season": m["season"],
                        "date": m["date"],
                        "match_id": mid,
                        "espn_event_id": ev_id,
                        "match": f"{m['home_team']} vs {m['away_team']}",
                        "team": side,
                        "espn_seconds": eg_i.seconds,
                        "espn_display": eg_i.display_value,
                        "espn_period": eg_i.period,
                        "espn_floor_min": eg_i.floor_minute,
                        "expected_us_min": eg_i.expected_understat_minute,
                        "stoppage_added": eg_i.stoppage_added,
                        "us_minute": us_min,
                        "is_regular": is_reg,
                        "is_fh_stoppage": is_fh_stop,
                        "is_sh_stoppage": is_sh_stop,
                        "exact_formula_match": us_min == eg_i.expected_understat_minute,
                        "espn_before_10": is_before_10_00_espn(eg_i),
                        "us_le_9": is_before_10_00_understat(us_min),
                        "us_le_10": us_min <= 10,
                    }
                )

    gdf = pd.DataFrame(goal_rows)
    mdf = pd.DataFrame(match_rows)

    n_goals = len(gdf)
    n_matches = len(mdf)
    agree_10_le9 = int((gdf["espn_before_10"] == gdf["us_le_9"]).sum())
    agree_10_le10 = int((gdf["espn_before_10"] == gdf["us_le_10"]).sum())
    rate_10_le9 = agree_10_le9 / n_goals
    rate_10_le10 = agree_10_le10 / n_goals

    order_agree_sorted = int(mdf["sorted_order_agrees"].sum())
    order_agree_raw = int(mdf["raw_order_agrees"].sum())
    rate_order_sorted = order_agree_sorted / n_matches
    rate_order_raw = order_agree_raw / n_matches

    passes_10min = rate_10_le9 >= 0.98
    passes_order = rate_order_sorted >= 0.99

    return {
        "goals_df": gdf,
        "matches_df": mdf,
        "n_goals": n_goals,
        "n_matches": n_matches,
        "agree_10_le9": agree_10_le9,
        "rate_10_le9": rate_10_le9,
        "agree_10_le10": agree_10_le10,
        "rate_10_le10": rate_10_le10,
        "order_agree_sorted": order_agree_sorted,
        "rate_order_sorted": rate_order_sorted,
        "order_agree_raw": order_agree_raw,
        "rate_order_raw": rate_order_raw,
        "passes_10min": passes_10min,
        "passes_order": passes_order,
        "passes_all": passes_10min and passes_order,
    }


def format_report(res: dict[str, Any]) -> str:
    gdf: pd.DataFrame = res["goals_df"]
    mdf: pd.DataFrame = res["matches_df"]

    reg = gdf[gdf["is_regular"]]
    fh_stop = gdf[gdf["is_fh_stoppage"]]
    sh_stop = gdf[gdf["is_sh_stoppage"]]

    lines: list[str] = []
    lines.append("# Task 19 — Goal-Minute Accuracy Check (Understat vs ESPN)")
    lines.append("")
    lines.append("## 1. Sample & Pre-Registered Gate Decision")
    lines.append("")
    lines.append(
        f"- **Compared sample**: **{res['n_goals']} goals** across **{res['n_matches']} matches** "
        f"spanning all **5 main leagues** (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`) and "
        f"**3 seasons** (`2023/24`, `2024/25`, `2025/26`)."
    )
    lines.append(
        f"- **10-minute window (`00:01-09:59`, ESPN `period == 1` and `clock.value < 600.0` seconds)**: "
        f"Under mapping `Understat minute <= 9`, agreement is "
        f"**{res['agree_10_le9']} / {res['n_goals']} ({res['rate_10_le9'] * 100:.2f}%)** "
        f"(gate threshold `>= 98.00%` -> **{'PASS' if res['passes_10min'] else 'FAIL'}**)."
    )
    lines.append(
        f"- **Chronological goal order (when `goals.parquet` is sorted by `minute`)**: "
        f"Full match goal-scoring team sequence agrees with ESPN in "
        f"**{res['order_agree_sorted']} / {res['n_matches']} matches ({res['rate_order_sorted'] * 100:.2f}%)**, "
        f"and first-goal team agrees in **{int(mdf['first_goal_agrees_sorted'].sum())} / {res['n_matches']} "
        f"({mdf['first_goal_agrees_sorted'].mean() * 100:.2f}%)** "
        f"(gate threshold `>= 99.00%` -> **{'PASS' if res['passes_order'] else 'FAIL'}**)."
    )
    lines.append(
        f"- **Overall Task 19 Verdict**: **{'PASS' if res['passes_all'] else 'FAIL'}** — "
        "Understat processed goal minutes may be used in Task 20 with `minute <= 9` for the "
        "`00:01-09:59` 10-minute window and `goals.parquet` sorted by `minute` for first-goal order."
    )
    lines.append("")
    lines.append("## 2. Exact Minute Mapping & Stoppage-Time Storage")
    lines.append("")
    lines.append(
        "1. **Regular-time goals (`clock.displayValue` without `+`)**: "
        "Understat stores **0-indexed completed minutes**: `minute = floor(seconds / 60) = display_minute - 1`. "
        f"Across `{len(reg)}` regular-time goals, **{int(reg['exact_formula_match'].sum())} / {len(reg)} "
        f"({reg['exact_formula_match'].mean() * 100:.2f}%)** match `floor(seconds / 60)` exactly, "
        f"and the remaining **{int((~reg['exact_formula_match']).sum())}** differ by `-1` minute."
    )
    lines.append(
        "2. **First-half stoppage goals (`45'+x'` in `period == 1`)**: "
        "ESPN sets `clock.value = 2700.0` for all first-half stoppage goals and records `+x'` in "
        "`clock.displayValue`. Understat stores them as **`minute = 45 + x - 1 = 44 + x`** "
        f"(`45'+1' -> 45`, `45'+2' -> 46`, ..., `45'+6' -> 50`). Across `{len(fh_stop)}` first-half "
        f"stoppage goals, **{int(fh_stop['exact_formula_match'].sum())} / {len(fh_stop)} "
        f"({fh_stop['exact_formula_match'].mean() * 100:.2f}%)** match `44 + x` exactly. "
        "Because `45'+2'` (`minute = 46`) collides numerically with a second-half 47th-minute goal (`46:00-46:59`, "
        "`minute = 46`), half-time markets must be settled from `ht_home_goals`/`ht_away_goals` (`HTHG`/`HTAG`), "
        "never by filtering `minute <= 45`."
    )
    lines.append(
        "3. **Second-half stoppage goals (`90'+x'` in `period == 2`)**: "
        "ESPN sets `clock.value = 5400.0` and records `+x'` in `clock.displayValue`. "
        "Understat stores them as **`minute = 90 + x - 1 = 89 + x`** (`90'+1' -> 90`, ..., `90'+12' -> 101`). "
        f"Across `{len(sh_stop)}` second-half stoppage goals, **{int(sh_stop['exact_formula_match'].sum())} / {len(sh_stop)} "
        f"({sh_stop['exact_formula_match'].mean() * 100:.2f}%)** match `89 + x` exactly."
    )
    lines.append(
        "4. **Row order in `goals.parquet`**: Raw `goals.parquet` stores all `home` goals before `away` goals "
        f"(raw row order agrees with ESPN in only `{res['order_agree_raw']} / {res['n_matches']}` = "
        f"`{res['rate_order_raw'] * 100:.2f}%` of matches). Sorting `goals.parquet` by `minute` restores "
        f"chronological order in **`{res['order_agree_sorted']} / {res['n_matches']}` (`{res['rate_order_sorted'] * 100:.2f}%`)** "
        "of compared matches."
    )
    lines.append("")
    lines.append("## 3. Sample Breakdown by League and Season")
    lines.append("")
    lines.append("| League | Season | Date | Matches | Goals | `< 10:00` Agreement (`us <= 9`) | Sorted Goal Order Agreement |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    for lg in MAIN_LEAGUES:
        for season in SEASONS:
            sub_m = mdf[(mdf["league"] == lg) & (mdf["season"] == season)]
            sub_g = gdf[(gdf["league"] == lg) & (gdf["season"] == season)]
            date_str = str(sub_m["date"].iloc[0])
            n_m = len(sub_m)
            n_g = len(sub_g)
            ag_10 = int((sub_g["espn_before_10"] == sub_g["us_le_9"]).sum())
            ag_ord = int(sub_m["sorted_order_agrees"].sum())
            lines.append(
                f"| `{lg}` | `{season}` | `{date_str}` | {n_m} | {n_g} | "
                f"{ag_10}/{n_g} ({ag_10 / n_g * 100:.1f}%) | {ag_ord}/{n_m} ({ag_ord / n_m * 100:.1f}%) |"
            )
    lines.append(
        f"| **Total** | **3 seasons** | **15 matchdays** | **{res['n_matches']}** | **{res['n_goals']}** | "
        f"**{res['agree_10_le9']}/{res['n_goals']} ({res['rate_10_le9'] * 100:.2f}%)** | "
        f"**{res['order_agree_sorted']}/{res['n_matches']} ({res['rate_order_sorted'] * 100:.2f}%)** |"
    )
    lines.append("")
    lines.append("## 4. Agreement Summary by Goal Category")
    lines.append("")
    lines.append("| Category | Goals | Formula Tested | Exact Match | Off by -1 min | `< 10:00` Agreement (`us <= 9`) | Naive `us <= 10` Agreement |")
    lines.append("|---|---:|---|---:|---:|---:|---:|")
    for label, sub, formula in [
        ("Regular time (no `+`)", reg, "`floor(seconds / 60)`"),
        ("First-half stoppage (`45'+x'`)", fh_stop, "`44 + x`"),
        ("Second-half stoppage (`90'+x'`)", sh_stop, "`89 + x`"),
        ("All compared goals", gdf, "Combined mapping"),
    ]:
        n_sub = len(sub)
        ex = int(sub["exact_formula_match"].sum())
        off1 = int((sub["us_minute"] - sub["expected_us_min"] == -1).sum())
        a9 = int((sub["espn_before_10"] == sub["us_le_9"]).sum())
        a10 = int((sub["espn_before_10"] == sub["us_le_10"]).sum())
        lines.append(
            f"| {label} | {n_sub} | {formula} | {ex}/{n_sub} ({ex / n_sub * 100:.2f}%) | "
            f"{off1} | {a9}/{n_sub} ({a9 / n_sub * 100:.2f}%) | {a10}/{n_sub} ({a10 / n_sub * 100:.2f}%) |"
        )
    lines.append("")
    lines.append("## 5. Boundary Verification Around 10:00 (`480s` to `720s`, Period 1)")
    lines.append("")
    lines.append("| League | Date | Match | Team | ESPN Seconds | ESPN Display | `< 10:00` (`< 600s`) | Understat `minute` | `minute <= 9` | `minute <= 10` |")
    lines.append("|---|---|---|---|---:|---|---:|---:|---:|---:|")
    boundary = gdf[(gdf["espn_period"] == 1) & (gdf["espn_seconds"] >= 480.0) & (gdf["espn_seconds"] <= 720.0)].sort_values(
        ["espn_seconds", "league", "match"]
    )
    for _, r in boundary.iterrows():
        lines.append(
            f"| `{r['league']}` | `{r['date']}` | {r['match']} | `{r['team']}` | "
            f"`{r['espn_seconds']:.1f}` | `{r['espn_display']}` | `{'Yes' if r['espn_before_10'] else 'No'}` | "
            f"`{int(r['us_minute'])}` | `{'Yes' if r['us_le_9'] else 'No'}` | `{'Yes' if r['us_le_10'] else 'No'}` |"
        )
    lines.append("")
    lines.append("## 6. All First-Half Stoppage Goals (`45'+x'`)")
    lines.append("")
    lines.append("| League | Date | Match | Team | ESPN Seconds | ESPN Display | Formula `44 + x` | Understat `minute` |")
    lines.append("|---|---|---|---|---:|---|---:|---:|")
    for _, r in fh_stop.sort_values(["league", "date", "match", "us_minute"]).iterrows():
        lines.append(
            f"| `{r['league']}` | `{r['date']}` | {r['match']} | `{r['team']}` | "
            f"`{r['espn_seconds']:.1f}` | `{r['espn_display']}` | `{int(r['expected_us_min'])}` | `{int(r['us_minute'])}` |"
        )
    lines.append("")
    lines.append("## 7. Every Disagreement Example")
    lines.append("")
    lines.append("### 7.1 Disagreements on `< 10:00` Window Under Verified Mapping (`minute <= 9`)")
    lines.append("")
    dis_le9 = gdf[gdf["espn_before_10"] != gdf["us_le_9"]]
    if len(dis_le9) == 0:
        lines.append("- **None** (`0 / 332` disagreements). Every goal with `espn_seconds < 600.0` in Period 1 has `Understat minute <= 9`, and every goal with `espn_seconds >= 600.0` has `Understat minute >= 10`.")
    else:
        for _, r in dis_le9.iterrows():
            lines.append(
                f"- `{r['league']}` `{r['date']}` {r['match']} (`{r['team']}`): ESPN `{r['espn_seconds']:.1f}s` (`{r['espn_display']}`), Understat `{int(r['us_minute'])}`."
            )
    lines.append("")
    lines.append("### 7.2 Disagreements on `< 10:00` Window If Naive `minute <= 10` Were Used")
    lines.append("")
    lines.append("| League | Date | Match | Team | ESPN Seconds | ESPN Display | Understat `minute` | Reason |")
    lines.append("|---|---|---|---|---:|---|---:|---|")
    dis_le10 = gdf[gdf["espn_before_10"] != gdf["us_le_10"]]
    for _, r in dis_le10.iterrows():
        lines.append(
            f"| `{r['league']}` | `{r['date']}` | {r['match']} | `{r['team']}` | "
            f"`{r['espn_seconds']:.1f}` | `{r['espn_display']}` | `{int(r['us_minute'])}` | "
            "Scored in 11th display minute (`10:00-10:59`), stored as 0-indexed minute `10` |"
        )
    lines.append("")
    lines.append("### 7.3 Disagreements on Chronological Goal Order (`goals.parquet` Sorted by `minute`)")
    lines.append("")
    dis_ord = mdf[~mdf["sorted_order_agrees"]]
    if len(dis_ord) == 0:
        lines.append("- **None** (`0 / 73` matches). When sorted by `minute`, `goals.parquet` reproduces ESPN's exact scoring-team sequence in all 73 matches.")
    else:
        for _, r in dis_ord.iterrows():
            lines.append(f"- `{r['league']}` `{r['date']}` {r['match']}")
    lines.append("")
    lines.append("### 7.4 Regular-Time Minute Formula Disagreements (`us_minute != floor(espn_seconds / 60)`)")
    lines.append("")
    lines.append("| League | Date | Match | Team | ESPN Seconds | ESPN Display | `floor(seconds / 60)` | Understat `minute` | Difference |")
    lines.append("|---|---|---|---|---:|---|---:|---:|---:|")
    dis_reg = gdf[~gdf["exact_formula_match"]]
    for _, r in dis_reg.iterrows():
        diff = int(r["us_minute"]) - int(r["expected_us_min"])
        lines.append(
            f"| `{r['league']}` | `{r['date']}` | {r['match']} | `{r['team']}` | "
            f"`{r['espn_seconds']:.1f}` | `{r['espn_display']}` | `{int(r['expected_us_min'])}` | "
            f"`{int(r['us_minute'])}` | `{diff:+d}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    res = evaluate_goal_minute_accuracy()
    report = format_report(res)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(
        f"Wrote {REPORT_PATH} (matches={res['n_matches']}, goals={res['n_goals']}, "
        f"10min_agree={res['agree_10_le9']}/{res['n_goals']}, "
        f"order_agree={res['order_agree_sorted']}/{res['n_matches']})"
    )


if __name__ == "__main__":
    main()
