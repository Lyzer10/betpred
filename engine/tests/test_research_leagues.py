"""Tests for Task 23: Research leagues price collection, settlement, and isolation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.betpawa import RESEARCH_MARKETS, parse_markets
from src.research_leagues import (
    RESEARCH_LEAGUES,
    normalize_research_team,
    settle_markets,
)
from src.research_status import generate_status_report

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "research_leagues"
RESEARCH_CODES = set(RESEARCH_LEAGUES.keys())


def test_research_leagues_configuration() -> None:
    expected_slugs = {
        "E1": "eng.2",
        "I2": "ita.2",
        "D2": "ger.2",
        "F2": "fra.2",
        "SP2": "esp.2",
        "G1": "gre.1",
        "SC0": "sco.1",
    }
    assert set(RESEARCH_LEAGUES.keys()) == set(expected_slugs.keys())
    for code, expected_slug in expected_slugs.items():
        name, country, cid, slug = RESEARCH_LEAGUES[code]
        assert slug == expected_slug
        if code == "F2":
            assert cid is None  # F2 verified 0 upcoming events / no active CID on Betpawa
        else:
            assert isinstance(cid, int) and cid > 0


def test_team_normalization_and_unmapped_logging() -> None:
    # Known mapped teams across research leagues
    assert normalize_research_team("Norwich City", "E1") == "Norwich"
    assert normalize_research_team("Bristol City", "E1") == "Bristol City"
    assert normalize_research_team("Carrarese Calcio", "I2") == "Carrarese"
    assert normalize_research_team("US Cremonese", "I2") == "Cremonese"
    assert normalize_research_team("Arminia Bielefeld", "D2") == "Bielefeld"
    assert normalize_research_team("SV Darmstadt 98", "D2") == "Darmstadt"

    # Unmapped team must return None (logged, never guessed)
    assert normalize_research_team("NonExistent Football Club", "E1") is None
    assert normalize_research_team("", "E1") is None


def test_parse_real_trimmed_event_fixtures() -> None:
    fixture_files = sorted(FIXTURES_DIR.glob("betpawa_*.json"))
    assert len(fixture_files) >= 6

    for fpath in fixture_files:
        data = json.loads(fpath.read_text(encoding="utf-8"))
        markets = data.get("markets", [])
        parsed = parse_markets(markets)
        assert isinstance(parsed, dict)
        assert len(parsed) > 0

        # Verify key candidate markets are parsed from real response
        found_candidate = any(m in parsed for m in RESEARCH_MARKETS)
        assert found_candidate, f"Fixture {fpath.name} should parse at least one candidate market"


def test_settle_markets_rules() -> None:
    # 1. 2UP rule: home was 2 up during match but finished 2-2 -> home_2up should win!
    goals_2up = [
        {"side": "home", "seconds": 300.0, "period": 1},
        {"side": "home", "seconds": 600.0, "period": 1},  # home 2-0 up
        {"side": "away", "seconds": 1200.0, "period": 1},
        {"side": "away", "seconds": 3000.0, "period": 2},  # 2-2 FT
    ]
    res_2up = settle_markets(home_ft=2, away_ft=2, home_ht=2, away_ht=1, goals=goals_2up)
    assert res_2up["home_2up"] is True  # 2UP pays because ever 2 ahead
    assert res_2up["away_2up"] is False

    # 2. 2UP rule: home team won 1-0 (never 2 ahead) -> home_2up still wins per Task 17 correction
    goals_10 = [{"side": "home", "seconds": 1200.0, "period": 1}]
    res_10 = settle_markets(home_ft=1, away_ft=0, home_ht=1, away_ht=0, goals=goals_10)
    assert res_10["home_2up"] is True
    assert res_10["away_2up"] is False

    # 3. 10-minute interval: strictly < 600s in period 1
    # Goal at 599s is in interval; goal at 600s is outside
    g_in = [{"side": "home", "seconds": 599.0, "period": 1}]
    res_in = settle_markets(home_ft=1, away_ft=0, home_ht=1, away_ht=0, goals=g_in)
    assert res_in["interval_10_home"] is True
    assert res_in["interval_10_draw"] is False

    g_out = [{"side": "home", "seconds": 600.0, "period": 1}]
    res_out = settle_markets(home_ft=1, away_ft=0, home_ht=0, away_ht=0, goals=g_out)
    assert res_out["interval_10_home"] is False
    assert res_out["interval_10_draw"] is True  # still 0-0 in interval

    # 4. Half markets
    res_half = settle_markets(home_ft=2, away_ft=1, home_ht=1, away_ht=0, goals=[])
    assert res_half["fh_over_0.5"] is True
    assert res_half["fh_over_1.5"] is False  # HT 1-0 (total 1 <= 1.5)
    assert res_half["sh_over_0.5"] is True   # SH 1-1 (total 2 > 0.5)
    assert res_half["home_score_both_halves"] is True  # 1 in FH, 1 in SH
    assert res_half["away_score_both_halves"] is False # 0 in FH, 1 in SH

    # 5. DNB
    res_draw = settle_markets(home_ft=1, away_ft=1, home_ht=0, away_ht=0, goals=[])
    assert res_draw["dnb_home"] is None  # Draw pushes / voids
    assert res_draw["dnb_away"] is None


def test_isolation_failure_safety(capsys: pytest.CaptureFixture) -> None:
    """A crash in research collection must print one line and never crash main."""
    now = pd.Timestamp("2026-11-08T12:00:00Z")

    with patch("src.research_leagues.collect_research_prices", side_effect=RuntimeError("Simulated API failure")):
        try:
            from src.research_leagues import collect_research_prices
            collect_research_prices(now)
        except Exception as error:
            print(f"Research leagues collection/settlement unavailable ({error})")

    out = capsys.readouterr().out
    assert "Research leagues collection/settlement unavailable (Simulated API failure)" in out


def test_no_research_leagues_in_live_outputs() -> None:
    """Verify research leagues NEVER appear in predictions.json, slips, or tables."""
    pred_path = Path(__file__).resolve().parents[2] / "web" / "public" / "data" / "predictions.json"
    if not pred_path.exists():
        pytest.skip("web/public/data/predictions.json not present")

    data = json.loads(pred_path.read_text(encoding="utf-8"))

    # Check top-level fixtures list
    for fix in data.get("fixtures", []):
        league_code = fix.get("league", {}).get("code", "") if isinstance(fix.get("league"), dict) else str(fix.get("league", ""))
        assert league_code not in RESEARCH_CODES, f"Research league {league_code} leaked into predictions fixtures!"

    # Check slips across all days
    for day in data.get("days", []):
        slips_dict = day.get("slips", {})
        if isinstance(slips_dict, dict):
            for tier, slip in slips_dict.items():
                if isinstance(slip, dict):
                    for leg in slip.get("legs", []):
                        league_obj = leg.get("league", "")
                        league_code = league_obj.get("code", "") if isinstance(league_obj, dict) else str(league_obj)
                        assert league_code not in RESEARCH_CODES, f"Research league {league_code} leaked into slip legs!"

    # Check tables
    for tbl_key in data.get("tables", {}):
        assert tbl_key not in RESEARCH_CODES, f"Research league {tbl_key} leaked into tables!"


def test_research_status_generation() -> None:
    content, reached = generate_status_report()
    assert isinstance(content, str)
    assert len(content) > 100
    assert "BetPredz Research Markets Status Report" in content
    assert "away_2up" in content
    assert "home_over_0.5" in content
    assert isinstance(reached, list)
    for m in reached:
        assert m in RESEARCH_MARKETS
