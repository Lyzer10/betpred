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


def test_settlement_never_infers_missing_data() -> None:
    # ESPN lists only one of the two goals: goal-time markets must stay unsettled.
    partial = [{"side": "home", "seconds": 300.0, "period": 1}]
    res = settle_markets(home_ft=1, away_ft=1, home_ht=1, away_ht=0, goals=partial)
    for m in ("interval_10_home", "interval_10_draw", "first_goal_home", "home_2up", "dc1up_1x"):
        assert res.get(m) is None, m
    assert res["fh_over_0.5"] is True          # the half-time score is still usable
    # An unknown side (team id not matched) also leaves goal-time markets unsettled.
    unknown = [{"side": "unknown", "seconds": 300.0, "period": 1}]
    assert settle_markets(1, 0, 1, 0, unknown).get("first_goal_home") is None
    # A half-time score above the final score is a data error: half markets unsettled.
    bad_ht = settle_markets(home_ft=1, away_ft=0, home_ht=2, away_ht=0, goals=None)
    assert bad_ht.get("fh_over_0.5") is None and bad_ht.get("sh_over_0.5") is None
    # Goals listed out of order are sorted by period and clock before first goal / leads.
    late_first = [{"side": "away", "seconds": 3000.0, "period": 2}, {"side": "home", "seconds": 100.0, "period": 1}]
    res2 = settle_markets(1, 1, 1, 0, late_first)
    assert res2["first_goal_home"] is True and res2["interval_10_home"] is True
    assert res2["dc1up_1x"] is True and res2["dc1up_x2"] is True  # draw counts for X2 too


def test_dc1up_and_2up_rules() -> None:
    # 0-0: nobody led. 1X and X2 win on the draw; 12 loses.
    nil = settle_markets(0, 0, 0, 0, [])
    assert (nil["dc1up_1x"], nil["dc1up_x2"], nil["dc1up_12"]) == (True, True, False)
    assert nil["home_2up"] is False and nil["away_2up"] is False
    # Away led 1-0, home came back to win 2-1: X2 wins (away led), 12 wins, away_2up loses.
    comeback = [{"side": "away", "seconds": 100.0, "period": 1}, {"side": "home", "seconds": 3000.0, "period": 2},
                {"side": "home", "seconds": 4000.0, "period": 2}]
    r = settle_markets(2, 1, 0, 1, comeback)
    assert r["dc1up_x2"] is True and r["dc1up_12"] is True and r["away_2up"] is False and r["home_2up"] is True


def test_consensus_lookup_keeps_over_under_columns() -> None:
    """itertuples() would rename 'Avg>2.5'; the lookup must keep the over/under averages."""
    from src.research_leagues import consensus_lookup
    df = pd.DataFrame([{"Div": "E1", "HomeTeam": "Norwich", "AwayTeam": "Bristol City", "AvgH": 2.1, "AvgD": 3.4,
                        "AvgA": 3.3, "Avg>2.5": 1.95, "Avg<2.5": 1.85},
                       {"Div": "E0", "HomeTeam": "Arsenal", "AwayTeam": "Chelsea", "AvgH": 2.0, "AvgD": 3.4,
                        "AvgA": 3.5, "Avg>2.5": 1.8, "Avg<2.5": 2.0}])
    look = consensus_lookup(df)
    assert list(look) == [("E1", "Norwich", "Bristol City")]   # live league E0 is never read here
    assert look[("E1", "Norwich", "Bristol City")]["Avg>2.5"] == 1.95
    assert look[("E1", "Norwich", "Bristol City")]["Avg<2.5"] == 1.85


def test_research_failure_never_reaches_main_run(capsys: pytest.CaptureFixture) -> None:
    """run_research_safely (called by predict.main) swallows any research failure with one line each."""
    from src import research_leagues
    now = pd.Timestamp("2026-11-08T12:00:00Z")
    with patch.object(research_leagues, "collect_research_prices", side_effect=RuntimeError("boom 1")), \
         patch.object(research_leagues, "settle_research_events", side_effect=RuntimeError("boom 2")):
        research_leagues.run_research_safely(now, None)      # must not raise
    out = capsys.readouterr().out
    assert "Research collection unavailable (boom 1)" in out
    assert "Research settlement unavailable (boom 2)" in out


def test_predict_calls_research_only_through_safe_wrapper() -> None:
    src_text = (Path(__file__).resolve().parents[1] / "src" / "predict.py").read_text(encoding="utf-8")
    assert "run_research_safely(now, _fixtures_csv())" in src_text
    assert "collect_research_prices" not in src_text and "settle_research_events" not in src_text


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


def test_research_status_counts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Last pre-kickoff price per match x market, matched to results by league, teams and day."""
    from src import research_status as rs
    live, research = tmp_path / "live", tmp_path / "research"
    live.mkdir()
    research.mkdir()
    header = ["snapshot_utc,league,home,away,kickoff_utc,market,betpawa_odds"]
    live_rows = [
        "2026-11-01T10:00:00Z,EPL,Liverpool,Arsenal,2026-11-01T16:30:00Z,interval_10_draw,1.30",
        "2026-11-01T17:00:00Z,EPL,Liverpool,Arsenal,2026-11-01T16:30:00Z,interval_10_draw,1.10",  # after kickoff
        "2026-11-01T10:00:00Z,EPL,Liverpool,Arsenal,2026-11-01T16:30:00Z,dnb_home,2.10",
        "2026-11-01T10:00:00Z,EPL,Chelsea,Spurs,2026-11-01T14:00:00Z,interval_10_draw,0.0",  # suspended
    ]
    research_rows = [
        "2026-11-07T10:00:00Z,SC0,Celtic,Rangers,2026-11-07T15:00:00Z,interval_10_draw,1.35",
        "2026-11-07T10:00:00Z,SC0,Celtic,Hearts,2026-11-07T15:00:00Z,interval_10_draw,1.35",  # no result
    ]
    result_rows = [
        "match_id,league,home,away,kickoff,FT,HT,goals_complete,interval_10_draw,dnb_home",
        "1,EPL,Liverpool,Arsenal,2026-11-01T16:30Z,1-1,0-0,1,1,",   # draw: DNB void
        "2,SC0,Celtic,Rangers,2026-09-01T15:00Z,2-0,1-0,1,0,1",     # same teams, another day
        "3,SC0,Celtic,Rangers,2026-11-07T15:00Z,0-0,0-0,1,1,",
    ]
    (live / "2026-11-01.csv").write_text("\n".join(header + live_rows) + "\n", encoding="utf-8")
    (research / "2026-11-07.csv").write_text("\n".join(header + research_rows) + "\n", encoding="utf-8")
    results = tmp_path / "results.csv"
    results.write_text("\n".join(result_rows) + "\n", encoding="utf-8")
    monkeypatch.setattr(rs, "LIVE_PRICES_DIR", live)
    monkeypatch.setattr(rs, "RESEARCH_PRICES_DIR", research)
    monkeypatch.setattr(rs, "RESULTS_PATH", results)
    counts, _ = rs.build_counts()
    assert counts.at["interval_10_draw", "live"] == 1       # suspended and post-kickoff prices ignored
    assert counts.at["interval_10_draw", "research"] == 1   # September result is not reused
    assert counts.at["dnb_home", "live"] == 0               # void on the draw
    content, reached = rs.generate_status_report(write=False)
    assert "EAT" in content and reached == []
