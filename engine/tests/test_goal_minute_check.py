"""Tests for Task 19 goal-minute accuracy check (src/goal_minute_check.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.goal_minute_check import (
    RAW_ESPN_DIR,
    evaluate_goal_minute_accuracy,
    expected_understat_minute_from_espn,
    is_before_10_00_espn,
    is_before_10_00_understat,
    parse_espn_summary_goals,
    sort_understat_goals,
)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "espn_summary_671408.json"


def test_expected_understat_minute_from_espn_conventions() -> None:
    # Regular-time goals: floor(seconds / 60) = display_minute - 1
    assert expected_understat_minute_from_espn(21.0, "1'", 1) == (0, None)
    assert expected_understat_minute_from_espn(577.0, "10'", 1) == (9, None)
    assert expected_understat_minute_from_espn(608.0, "11'", 1) == (10, None)

    # First-half stoppage: 44 + x
    assert expected_understat_minute_from_espn(2700.0, "45'+1'", 1) == (45, 1)
    assert expected_understat_minute_from_espn(2700.0, "45'+3'", 1) == (47, 3)

    # Second-half stoppage: 89 + x
    assert expected_understat_minute_from_espn(5400.0, "90'+1'", 2) == (90, 1)
    assert expected_understat_minute_from_espn(5400.0, "90'+12'", 2) == (101, 12)


def test_parse_real_trimmed_espn_summary_fixture() -> None:
    summary = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    goals = parse_espn_summary_goals(summary)
    assert len(goals) == 6
    # First three goals: 43' (away, 2531s -> 42), 45'+1' (home -> 45), 45'+3' (away -> 47)
    assert goals[0].team == "away"
    assert goals[0].display_value == "43'"
    assert goals[0].expected_understat_minute == 42
    assert goals[1].team == "home"
    assert goals[1].display_value == "45'+1'"
    assert goals[1].expected_understat_minute == 45
    assert goals[2].team == "away"
    assert goals[2].display_value == "45'+3'"
    assert goals[2].expected_understat_minute == 47
    assert all(not is_before_10_00_espn(g) for g in goals)


def test_10_minute_boundary_and_goal_order_sorting() -> None:
    assert is_before_10_00_understat(0) is True
    assert is_before_10_00_understat(9) is True
    assert is_before_10_00_understat(10) is False

    # Raw goals.parquet stores home goals before away goals; sorting by minute restores chronological order
    raw = pd.DataFrame(
        {
            "match_id": ["22266", "22266", "22266"],
            "minute": [38, 46, 36],
            "team": ["home", "home", "away"],
        }
    )
    sorted_df = sort_understat_goals(raw)
    assert list(sorted_df["team"]) == ["away", "home", "home"]
    assert list(sorted_df["minute"]) == [36, 38, 46]


def test_cached_sample_meets_task_19_gates_if_present() -> None:
    if not (RAW_ESPN_DIR / "manifest.json").exists():
        return
    res = evaluate_goal_minute_accuracy(RAW_ESPN_DIR)
    assert res["n_goals"] >= 300
    assert res["n_matches"] >= 60
    assert res["rate_10_le9"] >= 0.98
    assert res["rate_order_sorted"] >= 0.99
    assert res["passes_all"] is True
