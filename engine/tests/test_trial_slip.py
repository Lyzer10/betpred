"""Known-answer tests for PROJECT.md task 27 (trial_slip)."""
from pathlib import Path
import subprocess
import sys

import pandas as pd

from src.trial_slip import (
    TRIAL_STAKE_CAP,
    TRIAL_TIER,
    build_trial_slip,
    evaluate_trial_pause,
    run_dry_run,
)


def _synthetic_legs() -> pd.DataFrame:
    return pd.DataFrame([
        dict(match_id="EPL|2026-11-23|A|B", league="EPL", home="A", away="B", date="2026-11-23",
             market="fh_over_0.5", raw_probability=0.72, probability=0.74, odds=1.40),
        dict(match_id="EPL|2026-11-23|A|B", league="EPL", home="A", away="B", date="2026-11-23",
             market="sh_over_1.5", raw_probability=0.50, probability=0.52, odds=2.05),
        dict(match_id="LALIGA|2026-11-23|C|D", league="LALIGA", home="C", away="D", date="2026-11-23",
             market="dc1up_1x", raw_probability=0.75, probability=0.76, odds=1.35),
        dict(match_id="SERIEA|2026-11-23|E|F", league="SERIEA", home="E", away="F", date="2026-11-23",
             market="home_win_either_half", raw_probability=0.58, probability=0.60, odds=1.80),
        # Ineligible market with absurdly good prob/odds to verify eligibility filter blocks it:
        dict(match_id="BUNDES|2026-11-23|G|H", league="BUNDES", home="G", away="H", date="2026-11-23",
             market="dnb_home", raw_probability=0.95, probability=0.95, odds=2.00),
        dict(match_id="EPL|2026-11-23|I|J", league="EPL", home="I", away="J", date="2026-11-23",
             market="home_2up", raw_probability=0.95, probability=0.95, odds=2.00),
    ])


def test_no_eligible_legs_returns_no_trial_slip():
    legs = _synthetic_legs()
    assert build_trial_slip(legs, eligible_pairs=set()) is None
    assert build_trial_slip(legs, eligible_pairs={("LIGUE1", "fh_over_0.5")}) is None


def test_trial_slip_never_repeats_main_slip_match_and_market():
    legs = _synthetic_legs()
    eligible = {
        ("EPL", "fh_over_0.5"),
        ("EPL", "sh_over_1.5"),
        ("LALIGA", "dc1up_1x"),
        ("SERIEA", "home_win_either_half"),
    }
    # Put EPL A v B fh_over_0.5 and LALIGA C v D dc1up_1x onto Safe/Medium slips; Trial must exclude them.
    main_slips = {
        "safe": {
            "legs": [
                {"league": {"code": "EPL"}, "date": "2026-11-23", "home": "A", "away": "B", "market": "fh_over_0.5"},
            ]
        },
        "medium": {
            "legs": [
                {"league": {"code": "LALIGA"}, "date": "2026-11-23", "home": "C", "away": "D", "market": "dc1up_1x"},
            ]
        },
    }
    slip = build_trial_slip(legs, eligible, main_slips=main_slips)
    assert slip is not None
    picked_keys = {(l["league"], l["home"], l["away"], l["market"]) for l in slip["legs"]}
    assert ("EPL", "A", "B", "fh_over_0.5") not in picked_keys
    assert ("LALIGA", "C", "D", "dc1up_1x") not in picked_keys
    # Remaining eligible pair: EPL A v B sh_over_1.5 (2.05) * SERIEA E v F home_win_either_half (1.80) = 3.69
    assert picked_keys == {
        ("EPL", "A", "B", "sh_over_1.5"),
        ("SERIEA", "E", "F", "home_win_either_half"),
    }


def test_trial_slip_uses_only_eligible_list():
    legs = _synthetic_legs()
    # Notice BUNDES dnb_home and EPL home_2up have p=0.95 @ 2.00 in legs, but are NOT in eligible.
    eligible = {
        ("EPL", "fh_over_0.5"),
        ("LALIGA", "dc1up_1x"),
        ("SERIEA", "home_win_either_half"),
    }
    slip = build_trial_slip(legs, eligible)
    assert slip is not None
    for leg in slip["legs"]:
        assert (leg["league"], leg["market"]) in eligible
        assert leg["market"] != "dnb_home"
        assert (leg["league"], leg["market"]) != ("EPL", "home_2up")


def test_trial_slip_respects_odds_range_leg_count_and_one_leg_per_match():
    legs = _synthetic_legs()
    eligible = {
        ("EPL", "fh_over_0.5"),
        ("EPL", "sh_over_1.5"),
        ("LALIGA", "dc1up_1x"),
        ("SERIEA", "home_win_either_half"),
    }
    slip = build_trial_slip(legs, eligible)
    assert slip is not None
    assert TRIAL_TIER.min_odds <= slip["total_odds"] <= TRIAL_TIER.max_odds
    assert TRIAL_TIER.min_legs <= len(slip["legs"]) <= TRIAL_TIER.max_legs
    match_ids = [leg["match_id"] for leg in slip["legs"]]
    assert len(match_ids) == len(set(match_ids))


def test_trial_flag_stake_cap_and_margin_metadata():
    legs = _synthetic_legs()
    eligible = {
        ("EPL", "fh_over_0.5"),
        ("LALIGA", "dc1up_1x"),
        ("SERIEA", "home_win_either_half"),
    }
    slip = build_trial_slip(legs, eligible, market_margins={"fh_over_0.5": None, "dc1up_1x": None})
    assert slip is not None
    assert slip["trial"] is True
    assert slip["stake_cap"] == TRIAL_STAKE_CAP == 0.01
    for leg in slip["legs"]:
        assert leg["trial"] is True
        assert leg["stake_cap"] == 0.01
        assert leg["margin"] is None


def test_pause_rule_thresholds():
    # Fewer than 30 slips -> never pauses
    small = [{"won": False, "win_probability": 0.30}] * 29
    assert evaluate_trial_pause(small)["paused"] is False
    # 30 slips with p=0.30 (expected 9 wins, sd=2.51): 2 wins -> z = -2.789 < -2.5 -> PAUSED
    bad = [{"won": True, "win_probability": 0.30}] * 2 + [{"won": False, "win_probability": 0.30}] * 28
    res = evaluate_trial_pause(bad)
    assert res["paused"] is True and res["z"] < -2.5
    # 30 slips with 9 wins -> ACTIVE
    ok = [{"won": True, "win_probability": 0.30}] * 9 + [{"won": False, "win_probability": 0.30}] * 21
    assert evaluate_trial_pause(ok)["paused"] is False


def test_module_does_not_import_predict():
    engine_dir = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, "-c", "import sys, src.trial_slip; assert 'src.predict' not in sys.modules"],
        cwd=engine_dir,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_dry_run_leaves_live_data_and_web_data_untouched(tmp_path, monkeypatch):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from src import trial_slip
    from src.market_live import league_rho

    # Lightweight identity Platt stub so CI pytest runs in <2s while exercising all real file reads,
    # margin checks, eligible-list parsing, slip selection, report writing, and git-status checks.
    x = np.linspace(-3.0, 3.0, 40).reshape(-1, 1)
    y = (x.ravel() > 0).astype(int)
    stub_model = LogisticRegression(C=1.0).fit(x, y)

    def _fast_calibrators(league: str, target_season: str, families: set[str]):
        models = {
            m: stub_model
            for m in (
                *trial_slip.TASK16_MARKETS,
                *trial_slip.TASK17_MARKETS,
                *trial_slip.TASK20_TIMING_MARKETS,
                *trial_slip.TASK20_TEAM_HALF_MARKETS,
            )
        }
        return {"rho": league_rho(league), "models": models, "shares": {"fh": 0.44, "10min": 0.08}}, []

    monkeypatch.setattr(trial_slip, "fit_league_calibrators", _fast_calibrators)

    repo_root = Path(__file__).resolve().parents[2]
    before = subprocess.check_output(
        ["git", "status", "--porcelain", "web/public/data", "engine/data/live"],
        cwd=repo_root,
        text=True,
    )
    out_report = tmp_path / "trial_slip_dryrun.md"
    result = run_dry_run(output_path=out_report)
    assert out_report.exists()
    assert len(result["eligible"]["eligible"]) == 150
    after = subprocess.check_output(
        ["git", "status", "--porcelain", "web/public/data", "engine/data/live"],
        cwd=repo_root,
        text=True,
    )
    assert before == after
