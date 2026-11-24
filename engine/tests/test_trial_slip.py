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
    assert len(result["eligible"]["eligible"]) == 141  # 150 minus the 9 passing 2UP pairs (owner, 2026-11-23)
    assert not any("2up" in e["market"] for e in result["eligible"]["eligible"])
    after = subprocess.check_output(
        ["git", "status", "--porcelain", "web/public/data", "engine/data/live"],
        cwd=repo_root,
        text=True,
    )
    assert before == after


# ---------------------------------------------------------------------------
# Task 28 tests: cached calibrators, pipeline isolation, freeze, settlement, pause
# ---------------------------------------------------------------------------

def test_cached_calibrators_match_live_fit_within_1e_9(tmp_path):
    """Step 1 known-answer test: cached JSON predictions equal fit_league_calibrators to <= 1e-9."""
    import json
    import numpy as np
    from src import trial_slip
    from src.new_markets_study import _logit

    # Fit one real league family (JUPILER task16_half) directly with fit_league_calibrators
    # and compare against the exact numeric JSON cache saved by load_calibrators / predict_calibrated.
    league = "JUPILER"
    season = "2026/27"
    bundle, dropped = trial_slip.fit_league_calibrators(league, season, {"task16_half"})
    assert not dropped
    assert bundle["models"]

    # Persist into a temporary cache file using the exact schema of trial_calibrators.json.
    cache_payload = {
        "season": season,
        "fitted_at_eat": "2026-11-23T15:00:00+03:00",
        "data_last_match_date": bundle.get("data_last_match_date"),
        "market_margins": {},
        "leagues": {
            league: {
                "rho": float(bundle["rho"]),
                "shares": {k: float(v) for k, v in bundle["shares"].items()},
                "data_last_match_date": bundle.get("data_last_match_date"),
                "markets": {
                    mkt: {
                        "coef": float(model.coef_[0, 0]),
                        "intercept": float(model.intercept_[0]),
                    }
                    for mkt, model in bundle["models"].items()
                },
            }
        },
    }
    cache_path = tmp_path / "trial_calibrators.json"
    cache_path.write_text(json.dumps(cache_payload, indent=2), encoding="utf-8")
    loaded = trial_slip.load_calibrators(season, cache_path)
    assert loaded is not None

    fair_map = {"home_win": 0.48, "draw": 0.27, "away_win": 0.25, "over_2.5": 0.54, "under_2.5": 0.46}
    raw_live = trial_slip.fair_probs_to_trial_raw(fair_map, bundle)
    raw_cached = trial_slip.fair_probs_to_trial_raw(fair_map, loaded["leagues"][league])
    assert raw_live is not None and raw_cached is not None

    for mkt, model in bundle["models"].items():
        if mkt not in raw_live:
            continue
        p_live = float(np.clip(model.predict_proba(_logit([raw_live[mkt]]).reshape(-1, 1))[0, 1], 1e-6, 1.0 - 1e-6))
        p_cached = trial_slip.predict_calibrated(raw_cached[mkt], loaded["leagues"][league]["markets"][mkt])
        assert abs(p_live - p_cached) <= 1e-9, f"{mkt}: live={p_live} vs cached={p_cached}"

    # Also verify the committed engine/data/processed/trial_calibrators.json (if present) matches to <= 1e-9.
    if trial_slip.CALIBRATORS_PATH.exists():
        real_loaded = trial_slip.load_calibrators(season, trial_slip.CALIBRATORS_PATH)
        assert real_loaded is not None
        assert league in real_loaded["leagues"]
        for mkt, params in real_loaded["leagues"][league]["markets"].items():
            if mkt in bundle["models"] and mkt in raw_live:
                model = bundle["models"][mkt]
                p_live = float(np.clip(model.predict_proba(_logit([raw_live[mkt]]).reshape(-1, 1))[0, 1], 1e-6, 1.0 - 1e-6))
                raw_real = trial_slip.fair_probs_to_trial_raw(fair_map, real_loaded["leagues"][league])
                p_real = trial_slip.predict_calibrated(raw_real[mkt], params)
                assert abs(p_live - p_real) <= 1e-9, f"Committed cache mismatch for {mkt}: {p_live} vs {p_real}"


def test_load_calibrators_invalid_missing_or_wrong_season(tmp_path):
    import json
    from src import trial_slip

    missing = tmp_path / "missing.json"
    assert trial_slip.load_calibrators("2026/27", missing) is None

    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not valid json", encoding="utf-8")
    assert trial_slip.load_calibrators("2026/27", corrupt) is None

    wrong_season = tmp_path / "wrong.json"
    wrong_season.write_text(json.dumps({
        "season": "2025/26",
        "leagues": {"EPL": {"rho": -0.04, "shares": {"fh": 0.44}, "markets": {"fh_over_0.5": {"coef": 1.0, "intercept": 0.0}}}},
    }), encoding="utf-8")
    assert trial_slip.load_calibrators("2026/27", wrong_season) is None


def test_daily_run_never_refits_and_respects_pause(tmp_path, monkeypatch):
    import json
    from src import trial_slip

    def _forbid_refit(*args, **kwargs):
        raise AssertionError("Daily Trial run must NEVER refit calibrators")

    monkeypatch.setattr(trial_slip, "fit_league_calibrators", _forbid_refit)

    day_legs = pd.DataFrame([
        dict(fixture=0, league="EPL", home_team="Arsenal", away_team="Chelsea",
             date=pd.Timestamp("2026-11-24"), time="15:00", kickoff_utc=pd.Timestamp("2026-11-24 15:00"),
             market=m, bookmaker_probability=p)
        for m, p in [("home_win", 0.50), ("draw", 0.27), ("away_win", 0.23), ("over_2.5", 0.54), ("under_2.5", 0.46)]
    ] + [
        dict(fixture=1, league="LALIGA", home_team="Barcelona", away_team="Sevilla",
             date=pd.Timestamp("2026-11-24"), time="17:30", kickoff_utc=pd.Timestamp("2026-11-24 17:30"),
             market=m, bookmaker_probability=p)
        for m, p in [("home_win", 0.60), ("draw", 0.22), ("away_win", 0.18), ("over_2.5", 0.58), ("under_2.5", 0.42)]
    ])
    betpawa = pd.DataFrame([
        dict(league="EPL", home_team="Arsenal", away_team="Chelsea",
             kickoff_utc=pd.Timestamp("2026-11-24 15:00"), market="fh_over_0.5", betpawa_odds=1.80),
        dict(league="LALIGA", home_team="Barcelona", away_team="Sevilla",
             kickoff_utc=pd.Timestamp("2026-11-24 17:30"), market="dc1up_1x", betpawa_odds=2.00),
    ])
    cache_path = tmp_path / "trial_calibrators.json"
    cache_path.write_text(json.dumps({
        "season": "2026/27",
        "market_margins": {},
        "leagues": {
            "EPL": {"rho": -0.04, "shares": {"fh": 0.44, "10min": 0.08}, "markets": {"fh_over_0.5": {"coef": 1.0, "intercept": 0.0}}},
            "LALIGA": {"rho": -0.04, "shares": {"fh": 0.44, "10min": 0.08}, "markets": {"dc1up_1x": {"coef": 1.0, "intercept": 0.0}}},
        },
    }), encoding="utf-8")
    hist_path = tmp_path / "trial_history.json"
    now = pd.Timestamp("2026-11-24 10:00")

    # Active run succeeds using cached JSON only (never calls fit_league_calibrators).
    slip = trial_slip.run_day_trial(
        "2026-11-24", day_legs, betpawa, {}, "2026/27", now, final=False,
        calibrators_path=cache_path, history_path=hist_path, results_path=tmp_path / "none.csv",
    )
    assert slip is not None
    assert slip["trial"] is True and slip["stake_cap"] == 0.01
    assert len(slip["legs"]) == 2
    assert 3.0 <= slip["total_odds"] <= 5.0

    # Now write 30 settled losing slips (z < -2.5) to trial_history.json -> must PAUSE and return None.
    paused_hist = [
        {"round": f"2026-10-{i + 1:02d}", "tier": "trial", "win_probability": 0.30,
         "status": "won" if i < 2 else "lost",
         "legs": [{"won": i < 2, "market": "fh_over_0.5", "home": "A", "away": "B", "date": "2026-10-01"}]}
        for i in range(30)
    ]
    hist_path.write_text(json.dumps(paused_hist), encoding="utf-8")
    assert trial_slip.evaluate_trial_pause(hist_path)["paused"] is True
    suppressed = trial_slip.run_day_trial(
        "2026-11-24", day_legs, betpawa, {}, "2026/27", now, final=False,
        calibrators_path=cache_path, history_path=hist_path, results_path=tmp_path / "none.csv",
    )
    assert suppressed is None


def test_trial_freeze_after_final_and_after_kickoff(tmp_path):
    from src import trial_slip

    hist_path = tmp_path / "trial_history.json"
    no_results = tmp_path / "missing_results.csv"

    slip_v1 = {
        "tier": "trial", "trial": True, "stake_cap": 0.01, "total_odds": 3.50, "win_probability": 0.32,
        "odds_source": "betpawa", "legs": [
            {"date": "2026-11-24", "kickoff_utc": "2026-11-24T15:00:00Z", "league": {"code": "EPL"},
             "home": "A", "away": "B", "market": "fh_over_0.5", "label": "1st half over 0.5 goals",
             "probability": 0.70, "betpawa_odds": 1.80, "fair_odds": 1.43, "trial": True, "stake_cap": 0.01, "won": None},
            {"date": "2026-11-24", "kickoff_utc": "2026-11-24T18:00:00Z", "league": {"code": "LALIGA"},
             "home": "C", "away": "D", "market": "dc1up_1x", "label": "Home or draw (1Up)",
             "probability": 0.65, "betpawa_odds": 1.94, "fair_odds": 1.54, "trial": True, "stake_cap": 0.01, "won": None},
        ],
    }
    slip_v2 = {**slip_v1, "total_odds": 4.20}

    # Final run at 14:15 freezes slip_v1 permanently.
    hist = trial_slip.update_trial_history("2026-11-24", slip_v1, pd.Timestamp("2026-11-24 14:15"),
                                           final=True, history_path=hist_path, results_path=no_results)
    # Later run at 14:30 tries to pass slip_v2 -> must keep slip_v1 untouched.
    hist2 = trial_slip.update_trial_history("2026-11-24", slip_v2, pd.Timestamp("2026-11-24 14:30"),
                                            final=False, history_path=hist_path, results_path=no_results)
    shown = trial_slip.displayed_trial_slip("2026-11-24", slip_v2, hist2, pd.Timestamp("2026-11-24 14:30"))
    assert shown is not None and shown["total_odds"] == 3.50 and shown["final"] is True and shown["locked"] is False

    # After first kickoff (15:05), locked=True and still slip_v1.
    shown_live = trial_slip.displayed_trial_slip("2026-11-24", slip_v2, hist2, pd.Timestamp("2026-11-24 15:05"))
    assert shown_live is not None and shown_live["total_odds"] == 3.50 and shown_live["locked"] is True


def test_settle_trial_slip_from_real_results_csv_and_outage_safety(tmp_path, monkeypatch):
    """Step 3 test: real rows from engine/data/live/research/results.csv settle legs & outage never resets them."""
    import json
    from src import settle_results, trial_slip

    results_df = trial_slip.load_research_results(trial_slip.RESEARCH_RESULTS_PATH)
    assert not results_df.empty
    # Verify two real rows from results.csv:
    # SERIEA Inter v Fiorentina 2026-10-25T11:30Z FT 2-1 HT 0-0: sh_over_0.5=1, fh_over_0.5=0
    # JUPILER Genk v Standard 2026-10-25T12:30Z FT 2-1 HT 1-0: fh_over_0.5=1, dc1up_1x=1
    won_slip = {
        "tier": "trial", "trial": True, "stake_cap": 0.01, "total_odds": 3.40, "win_probability": 0.35,
        "legs": [
            {"league": {"code": "SERIEA", "name": "Serie A", "country": "Italy"}, "date": "2026-10-25",
             "kickoff_utc": "2026-10-25T11:30:00Z", "home": "Inter", "away": "Fiorentina",
             "market": "sh_over_0.5", "label": "2nd half over 0.5 goals", "probability": 0.72, "betpawa_odds": 1.80, "won": None},
            {"league": {"code": "JUPILER", "name": "Pro League", "country": "Belgium"}, "date": "2026-10-25",
             "kickoff_utc": "2026-10-25T12:30:00Z", "home": "Genk", "away": "Standard",
             "market": "fh_over_0.5", "label": "1st half over 0.5 goals", "probability": 0.68, "betpawa_odds": 1.89, "won": None},
        ],
    }
    trial_slip.settle_trial_slip(won_slip, results_df)
    assert won_slip["status"] == "won"
    assert [leg["won"] for leg in won_slip["legs"]] == [True, True]
    assert [leg["score"] for leg in won_slip["legs"]] == [[2, 1], [2, 1]]

    # Source outage (empty DataFrame) must NEVER reset already-settled leg outcomes.
    trial_slip.settle_trial_slip(won_slip, pd.DataFrame())
    assert won_slip["status"] == "won"
    assert [leg["won"] for leg in won_slip["legs"]] == [True, True]

    # One losing leg (Inter v Fiorentina fh_over_0.5 was 0 since HT 0-0) -> slip status "lost".
    lost_slip = {
        "tier": "trial", "trial": True, "stake_cap": 0.01, "total_odds": 3.40, "win_probability": 0.35,
        "legs": [
            {"league": {"code": "SERIEA"}, "date": "2026-10-25", "kickoff_utc": "2026-10-25T11:30:00Z",
             "home": "Inter", "away": "Fiorentina", "market": "fh_over_0.5", "won": None},
            {"league": {"code": "JUPILER"}, "date": "2026-10-25", "kickoff_utc": "2026-10-25T12:30:00Z",
             "home": "Genk", "away": "Standard", "market": "dc1up_1x", "won": None},
        ],
    }
    trial_slip.settle_trial_slip(lost_slip, results_df)
    assert lost_slip["status"] == "lost"
    assert [leg["won"] for leg in lost_slip["legs"]] == [False, True]

    # Missing match stays pending.
    pending_slip = {
        "tier": "trial", "trial": True, "stake_cap": 0.01, "total_odds": 3.20, "win_probability": 0.35,
        "legs": [
            {"league": {"code": "SERIEA"}, "date": "2026-10-25", "kickoff_utc": "2026-10-25T11:30:00Z",
             "home": "Inter", "away": "Fiorentina", "market": "sh_over_0.5", "won": None},
            {"league": {"code": "EPL"}, "date": "2099-01-01", "kickoff_utc": "2099-01-01T15:00:00Z",
             "home": "FutureA", "away": "FutureB", "market": "fh_over_0.5", "won": None},
        ],
    }
    trial_slip.settle_trial_slip(pending_slip, results_df)
    assert pending_slip["status"] == "pending"
    assert [leg["won"] for leg in pending_slip["legs"]] == [True, None]

    # Also test settle_results.repair hooks settle_trial_files cleanly without altering main slips.
    data_dir = tmp_path / "webdata"
    arch_dir = data_dir / "archive"
    arch_dir.mkdir(parents=True)
    main_slip_orig = {
        "safe": {
            "total_odds": 2.80, "win_probability": 0.45, "status": "pending",
            "legs": [{"league": {"code": "EPL"}, "date": "2099-01-01", "kickoff_utc": "2099-01-01T15:00:00Z",
                      "home": "FutureA", "away": "FutureB", "market": "home_win", "won": None}],
        }
    }
    (arch_dir / "2026-10-25.json").write_text(json.dumps({
        "date": "2026-10-25", "generated_at": "2026-10-25T09:00:00Z", "fixtures": [],
        "slips": main_slip_orig,
        "trial_slip": {**won_slip, "status": "pending", "legs": [{**l, "won": None} for l in won_slip["legs"]]},
    }), encoding="utf-8")
    hist_dir = tmp_path / "live"
    hist_dir.mkdir()
    (hist_dir / "slip_history.json").write_text("[]", encoding="utf-8")
    (hist_dir / "trial_history.json").write_text(json.dumps([
        {"round": "2026-10-25", **won_slip, "status": "pending", "legs": [{**l, "won": None} for l in won_slip["legs"]]}
    ]), encoding="utf-8")
    # Offline: record the fast Trial settlement request instead of calling ESPN / writing the real results.csv.
    from src import research_leagues
    asked = []
    monkeypatch.setattr(research_leagues, "settle_research_events", lambda now, only=None, **k: asked.append(only) or 0)
    settle_results.repair(now="2026-10-26T12:00:00Z", data_dir=data_dir, history_path=hist_dir / "slip_history.json",
                          cache=tmp_path / "espn_cache")
    assert asked and all(asked[0])   # finished unsettled Trial legs asked for their league days
    repaired_arch = json.loads((arch_dir / "2026-10-25.json").read_text(encoding="utf-8"))
    assert repaired_arch["trial_slip"]["status"] == "won"
    assert repaired_arch["slips"] == main_slip_orig
    repaired_hist = json.loads((hist_dir / "trial_history.json").read_text(encoding="utf-8"))
    assert repaired_hist[0]["status"] == "won"


def test_predict_no_refresh_trial_on_vs_off_byte_identical_and_error_isolation(tmp_path, monkeypatch):
    """Step 2 acceptance tests:
    1) predict.py --no-refresh with Trial ON vs OFF produces byte-for-byte identical slips & all other keys.
    2) Extra runtime of Trial ON vs OFF is strictly under 20 seconds.
    3) Forced exception inside Trial still publishes identical main slips without raising.
    """
    import json
    import time
    from datetime import datetime, timezone
    from src import predict, trial_slip

    fixed_now = datetime(2026, 11, 24, 9, 0, 0, tzinfo=timezone.utc)

    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now if tz is not None else fixed_now.replace(tzinfo=None)

    # Synthetic fixtures CSV with 3 matches on 2026-11-24 across EPL/LALIGA/SERIEA so main slips AND Trial build.
    fixtures_df = pd.DataFrame([
        dict(Div="E0", Date="24/11/2026", Time="15:00", HomeTeam="Arsenal", AwayTeam="Brentford",
             AvgH=1.45, AvgD=4.50, AvgA=7.00, **{"Avg>2.5": 1.65, "Avg<2.5": 2.25}),
        dict(Div="SP1", Date="24/11/2026", Time="17:30", HomeTeam="Barcelona", AwayTeam="Getafe",
             AvgH=1.35, AvgD=5.00, AvgA=9.00, **{"Avg>2.5": 1.70, "Avg<2.5": 2.15}),
        dict(Div="I1", Date="24/11/2026", Time="19:45", HomeTeam="Inter", AwayTeam="Torino",
             AvgH=1.40, AvgD=4.60, AvgA=8.00, **{"Avg>2.5": 1.72, "Avg<2.5": 2.12}),
    ])
    # Corresponding Betpawa prices covering both main slip markets and Trial markets.
    bp_by_league = {
        "EPL": pd.DataFrame([
            dict(home_team="Arsenal", away_team="Brentford", kickoff_utc=pd.Timestamp("2026-11-24 15:00"),
                 market="home_win", betpawa_odds=1.50, betpawa_price_id=None),
            dict(home_team="Arsenal", away_team="Brentford", kickoff_utc=pd.Timestamp("2026-11-24 15:00"),
                 market="over_1.5", betpawa_odds=1.22, betpawa_price_id=None),
            dict(home_team="Arsenal", away_team="Brentford", kickoff_utc=pd.Timestamp("2026-11-24 15:00"),
                 market="fh_over_0.5", betpawa_odds=1.80, betpawa_price_id=None),
        ]),
        "LALIGA": pd.DataFrame([
            dict(home_team="Barcelona", away_team="Getafe", kickoff_utc=pd.Timestamp("2026-11-24 17:30"),
                 market="home_win", betpawa_odds=1.40, betpawa_price_id=None),
            dict(home_team="Barcelona", away_team="Getafe", kickoff_utc=pd.Timestamp("2026-11-24 17:30"),
                 market="over_1.5", betpawa_odds=1.25, betpawa_price_id=None),
            dict(home_team="Barcelona", away_team="Getafe", kickoff_utc=pd.Timestamp("2026-11-24 17:30"),
                 market="dc1up_1x", betpawa_odds=1.95, betpawa_price_id=None),
        ]),
        "SERIEA": pd.DataFrame([
            dict(home_team="Inter", away_team="Torino", kickoff_utc=pd.Timestamp("2026-11-24 19:45"),
                 market="home_win", betpawa_odds=1.45, betpawa_price_id=None),
            dict(home_team="Inter", away_team="Torino", kickoff_utc=pd.Timestamp("2026-11-24 19:45"),
                 market="over_1.5", betpawa_odds=1.26, betpawa_price_id=None),
            dict(home_team="Inter", away_team="Torino", kickoff_utc=pd.Timestamp("2026-11-24 19:45"),
                 market="sh_over_0.5", betpawa_odds=1.90, betpawa_price_id=None),
        ]),
    }

    # Lightweight cached calibrators in tmp_path so test runs without needing network or slow refit.
    cache_path = tmp_path / "trial_calibrators.json"
    cache_path.write_text(json.dumps({
        "season": "2026/27",
        "market_margins": {},
        "leagues": {
            "EPL": {"rho": -0.04, "shares": {"fh": 0.44, "10min": 0.08}, "markets": {"fh_over_0.5": {"coef": 1.0, "intercept": 0.0}}},
            "LALIGA": {"rho": -0.04, "shares": {"fh": 0.44, "10min": 0.08}, "markets": {"dc1up_1x": {"coef": 1.0, "intercept": 0.0}}},
            "SERIEA": {"rho": -0.04, "shares": {"fh": 0.44, "10min": 0.08}, "markets": {"sh_over_0.5": {"coef": 1.0, "intercept": 0.0}}},
        },
    }), encoding="utf-8")

    # Keep test offline & fast: stub external downloads + limit LIVE_LEAGUES to EPL/LALIGA/SERIEA.
    monkeypatch.setattr(predict, "datetime", _FixedDatetime)
    monkeypatch.setattr(predict, "_fixtures_csv", lambda: fixtures_df)
    monkeypatch.setattr(predict, "betpawa_prices", lambda code: bp_by_league.get(
        code, pd.DataFrame(columns=["home_team", "away_team", "market", "kickoff_utc", "betpawa_odds", "betpawa_price_id"])
    ))
    monkeypatch.setattr(predict, "understat_results", lambda code, start: pd.DataFrame(
        columns=["date", "home_team", "away_team", "home_goals", "away_goals", "season", "league"]
    ))
    monkeypatch.setattr(predict, "espn_results", lambda code, now: pd.DataFrame(
        columns=["date", "home_team", "away_team", "home_goals", "away_goals", "season", "league"]
    ))
    monkeypatch.setattr(predict, "log_prices", lambda *a, **k: None)
    monkeypatch.setattr(predict, "log_research_prices", lambda *a, **k: None)
    monkeypatch.setattr(predict, "add_booking_codes", lambda shown, now: shown)
    monkeypatch.setattr(predict, "LIVE_LEAGUES", {"EPL": "blended", "LALIGA": "market", "SERIEA": "market"})
    # Offline: current-season matches from the committed tables, never Understat or the gitignored raw cache.
    from src.calibration import paths as _paths
    def _committed_build(refresh_current=False, league="EPL", write=True, start=None):
        m = pd.read_parquet(_paths(league).matches)
        return m[m.season.str[:4].astype(int) >= (start or 0)].reset_index(drop=True), None
    monkeypatch.setattr(predict, "build", _committed_build)
    monkeypatch.setattr(trial_slip, "CALIBRATORS_PATH", cache_path)
    monkeypatch.setattr(trial_slip, "RESEARCH_RESULTS_PATH", tmp_path / "empty_results.csv")
    monkeypatch.setattr(sys, "argv", ["predict", "--no-refresh"])

    def _run_into(tag: str, disable_trial: bool) -> tuple[str, dict, dict, float]:
        base = tmp_path / tag
        live_dir = base / "live"
        web_dir = base / "web"
        monkeypatch.setattr(predict, "LIVE_DIR", live_dir)
        monkeypatch.setattr(predict, "HISTORY_PATH", live_dir / "slip_history.json")
        monkeypatch.setattr(predict, "PAUSED_PATH", live_dir / "paused_pairs.json")
        monkeypatch.setattr(predict, "WEB_DATA_PATH", web_dir / "predictions.json")
        monkeypatch.setattr(predict, "ARCHIVE_DIR", web_dir / "archive")
        if disable_trial:
            monkeypatch.setenv("TRIAL_DISABLED", "1")
        else:
            monkeypatch.delenv("TRIAL_DISABLED", raising=False)
        t0 = time.perf_counter()
        predict.main()
        elapsed = time.perf_counter() - t0
        raw_text = (web_dir / "predictions.json").read_text(encoding="utf-8")
        arch_text = (web_dir / "archive" / "2026-11-24.json").read_text(encoding="utf-8")
        return raw_text, json.loads(raw_text), json.loads(arch_text), elapsed

    raw_off, pred_off, arch_off, t_off = _run_into("off", disable_trial=True)
    raw_on, pred_on, arch_on, t_on = _run_into("on", disable_trial=False)

    # Extra runtime of Trial ON must be strictly under 20 seconds.
    assert (t_on - t_off) < 20.0, f"Trial added {t_on - t_off:.2f}s (limit 20s)"

    # Trial ON actually published a valid trial_slip in both predictions.json and archive, without touching main slips.
    assert "trial_slip" not in pred_off["days"][0]
    # Identity below is only meaningful if main slips were really built.
    assert any(slip and slip.get("legs") for slip in pred_off["days"][0]["slips"].values())
    assert "trial_slip" in pred_on["days"][0] and pred_on["days"][0]["trial_slip"]["trial"] is True
    assert "trial_slip" not in arch_off
    assert "trial_slip" in arch_on and arch_on["trial_slip"]["trial"] is True

    # Strip ONLY the new trial_slip key and verify byte-for-byte identity of predictions.json and archive!
    pred_on_stripped = json.loads(raw_on)
    for d in pred_on_stripped["days"]:
        d.pop("trial_slip", None)
    assert json.dumps(pred_on_stripped, indent=2) == raw_off

    arch_on_stripped = dict(arch_on)
    arch_on_stripped.pop("trial_slip", None)
    assert json.dumps(arch_on_stripped, indent=1) == json.dumps(arch_off, indent=1)

    # Forced exception inside Trial: main slips still publish identically without raising.
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated Trial failure")

    monkeypatch.setattr(trial_slip, "run_day_trial", _boom)
    raw_err, pred_err, _, _ = _run_into("err", disable_trial=False)
    assert "trial_slip" not in pred_err["days"][0]
    assert raw_err == raw_off


def test_pending_trial_targets_only_finished_recent_unsettled_legs(tmp_path):
    import json
    from src.trial_slip import pending_trial_targets
    leg = lambda ko, won=None, code="EPL": {"league": {"code": code}, "kickoff_utc": ko, "won": won}
    history = [{"legs": [leg("2026-11-23T20:00:00Z"),                   # finished, unsettled -> due
                         leg("2026-11-23T19:45:00Z", won=True, code="SERIEA"),   # already settled
                         leg("2026-11-23T22:00:00Z", code="LALIGA"),     # kicked off < 110 min ago
                         leg("2026-11-10T20:00:00Z", code="BUNDES")]}]   # older than 3 days
    path = tmp_path / "trial_history.json"
    path.write_text(json.dumps(history), encoding="utf-8")
    now = pd.Timestamp("2026-11-23 23:00")
    assert pending_trial_targets(path, now) == {("EPL", "2026-11-23"), ("EPL", "2026-11-22")}
    assert pending_trial_targets(tmp_path / "missing.json", now) == set()


def test_targeted_research_settlement_asks_only_for_those_days(tmp_path, monkeypatch):
    from src import research_leagues as rl
    monkeypatch.setattr(rl, "RESEARCH_DIR", tmp_path)
    monkeypatch.setattr(rl, "RESULTS_PATH", tmp_path / "results.csv")
    monkeypatch.setattr(rl, "LAST_SETTLEMENT_PATH", tmp_path / "last_settlement.txt")
    monkeypatch.setattr(rl, "PAUSE_SECONDS", 0)
    asked = []

    class _Session:
        def get(self, url, params=None, **kwargs):
            asked.append((url.rsplit("/", 2)[-2], params.get("dates")))
            return type("R", (), {"ok": True, "json": lambda self: {"events": []}})()

    rl.settle_research_events(pd.Timestamp("2026-11-23 23:00"), session=_Session(), only={("EPL", "2026-11-23")})
    assert asked == [("eng.1", "20261123")]
    assert not (tmp_path / "last_settlement.txt").exists()   # the regular 3-hourly schedule is untouched
