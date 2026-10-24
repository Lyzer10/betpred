"""Build the joined match and goal parquet data sets."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .elo import add_elo_features
from .fetch_results import fetch_all as fetch_results
from .fetch_understat import fetch_all as fetch_understat
from .team_names import canonical_team

ENGINE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ENGINE_DIR / "data" / "processed"


def derive_goal_states(goals: pd.DataFrame) -> tuple[str, bool, bool]:
    """Derive first scorer and whether either side led, in event order."""
    if goals.empty:
        return "none", False, False
    ordered = goals.reset_index().sort_values(["minute", "index"], kind="stable")
    home = away = 0
    home_led = away_led = False
    first = str(ordered.iloc[0]["team"])
    for team in ordered["team"]:
        if team == "home":
            home += 1
        elif team == "away":
            away += 1
        else:
            raise ValueError(f"Unexpected goal team: {team!r}")
        home_led |= home > away
        away_led |= away > home
    return first, home_led, away_led


def _preferred(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    return frame[columns].bfill(axis=1).iloc[:, 0]


def build(refresh_current: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    results = fetch_results(refresh_current=refresh_current)
    understat, raw_goals = fetch_understat(refresh_current=refresh_current)
    for column in ("home_team", "away_team"):
        results[column] = results[column].map(canonical_team)

    # Dates can differ around midnight, so the stable identity is season plus teams.
    keys = ["season", "home_team", "away_team"]
    if results.duplicated(keys).any() or understat.duplicated(keys).any():
        raise ValueError("Duplicate season/team match keys prevent an unambiguous merge")
    merged = results.merge(understat, on=keys, how="left", suffixes=("", "_understat"), validate="one_to_one", indicator=True)
    date_gap = (merged["date"] - merged["date_understat"].dt.normalize()).abs().dt.days
    bad_dates = merged[date_gap.gt(2) & merged["date_understat"].notna()]
    if not bad_dates.empty:
        raise ValueError(f"Merged matches with dates more than two days apart: {len(bad_dates)}")

    merged["match_id"] = merged.apply(lambda row: str(row["understat_id"]) if pd.notna(row["understat_id"])
                                      else f"fd-{row['season'].replace('/', '')}-{row.name}", axis=1)
    goals = raw_goals.merge(understat[["understat_id"]], on="understat_id", how="inner")
    goals = goals.rename(columns={"understat_id": "match_id"})[["match_id", "minute", "team"]]
    states = goals.groupby("match_id", sort=False).apply(derive_goal_states, include_groups=False).to_dict()
    derived = merged["match_id"].map(lambda match_id: states.get(match_id, ("none", False, False)))

    output = pd.DataFrame({
        "match_id": merged["match_id"], "date": merged["date_understat"].fillna(merged["date"]), "season": merged["season"],
        "home_team": merged["home_team"], "away_team": merged["away_team"],
        "home_goals": merged["fthg"], "away_goals": merged["ftag"],
        "ht_home_goals": merged["hthg"], "ht_away_goals": merged["htag"],
        "home_xg": merged["home_xg"], "away_xg": merged["away_xg"],
        "home_shots": merged["hs"], "away_shots": merged["as"],
        "home_sot": merged["hst"], "away_sot": merged["ast"],
        "odds_home": _preferred(merged, ["psh", "avgh", "b365h"]),
        "odds_draw": _preferred(merged, ["psd", "avgd", "b365d"]),
        "odds_away": _preferred(merged, ["psa", "avga", "b365a"]),
        "odds_over25": _preferred(merged, ["p_over25", "avg_over25", "bbav_over25", "b365_over25"]),
        "odds_under25": _preferred(merged, ["p_under25", "avg_under25", "bbav_under25", "b365_under25"]),
        # Closing odds are for evaluation only and must never be used as model features.
        "close_odds_home": _preferred(merged, ["psch", "avgch"]),
        "close_odds_draw": _preferred(merged, ["pscd", "avgcd"]),
        "close_odds_away": _preferred(merged, ["psca", "avgca"]),
        "close_odds_over25": _preferred(merged, ["pc_over25", "avgc_over25"]),
        "close_odds_under25": _preferred(merged, ["pc_under25", "avgc_under25"]),
        "first_scorer": derived.map(lambda value: value[0]),
        "home_led_at_any_point": derived.map(lambda value: value[1]),
        "away_led_at_any_point": derived.map(lambda value: value[2]),
    })
    output = add_elo_features(output)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output.to_parquet(PROCESSED_DIR / "matches.parquet", index=False)
    goals.to_parquet(PROCESSED_DIR / "goals.parquet", index=False)

    merge_pct = (merged["_merge"] == "both").mean() * 100
    print("Rows per season:")
    print(output.groupby("season", sort=False).size().to_string())
    print(f"Missing xG: {output[['home_xg', 'away_xg']].isna().any(axis=1).mean() * 100:.2f}%")
    print(f"Missing 1X2 odds: {output[['odds_home', 'odds_draw', 'odds_away']].isna().any(axis=1).mean() * 100:.2f}%")
    print("Missing over/under 2.5 odds by season (%):")
    print((output[["odds_over25", "odds_under25"]].isna().any(axis=1)
           .groupby(output["season"], sort=False).mean() * 100).round(2).to_string())
    print(f"Matches merged with Understat: {merge_pct:.2f}%")
    if merge_pct < 98:
        raise RuntimeError(f"Understat merge rate {merge_pct:.2f}% is below the 98% target")
    return output, goals


def main() -> None:
    build()
    from .baselines import generate_report
    generate_report()


if __name__ == "__main__":
    main()
