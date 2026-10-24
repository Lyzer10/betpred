import json

import pandas as pd

from src import predict
from src.predict import outcome


def _match(home_goals, away_goals, first_scorer="home", home_led=True, away_led=False):
    from src.calibration import add_actuals
    frame = pd.DataFrame([{"home_goals": home_goals, "away_goals": away_goals, "first_scorer": first_scorer,
                           "home_led_at_any_point": home_led, "away_led_at_any_point": away_led}])
    return add_actuals(frame).iloc[0]


def test_outcome_settles_every_market_type():
    comeback = _match(1, 2, first_scorer="home", home_led=True, away_led=True)
    assert outcome(comeback, "away_win")
    assert outcome(comeback, "home_1up")          # led 1-0 before losing
    assert outcome(comeback, "home_first")
    assert outcome(comeback, "btts_yes") and not outcome(comeback, "btts_no")
    assert outcome(comeback, "over_2.5") and not outcome(comeback, "under_2.5")
    assert outcome(comeback, "under_3.5") and not outcome(comeback, "over_3.5")
    goalless = _match(0, 0, first_scorer="none", home_led=False)
    assert outcome(goalless, "draw") and outcome(goalless, "btts_no")
    assert not outcome(goalless, "home_1up") and not outcome(goalless, "over_0.5")


def _slip(kickoff):
    return {"total_odds": 2.6, "win_probability": 0.36,
            "legs": [{"date": kickoff[:10], "kickoff_utc": kickoff + "Z", "home": "Arsenal", "away": "Everton",
                      "market": "home_win"}]}


def test_history_freezes_slips_after_kickoff(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "LIVE_DIR", tmp_path)
    monkeypatch.setattr(predict, "HISTORY_PATH", tmp_path / "history.json")
    matches = pd.DataFrame(columns=["home_team", "away_team", "season", "home_goals", "away_goals",
                                    "first_scorer", "home_led_at_any_point", "away_led_at_any_point"])
    before = pd.Timestamp("2026-10-24 10:00")
    predict.update_history("R1", {"safe": _slip("2026-10-24T14:00:00")}, matches, before)
    # A later run (after kickoff) proposing a different slip must not overwrite it.
    after = pd.Timestamp("2026-10-24 15:00")
    changed = _slip("2026-10-24T14:00:00")
    changed["total_odds"] = 3.1
    history = predict.update_history("R1", {"safe": changed}, matches, after)
    assert len(history) == 1 and history[0]["total_odds"] == 2.6
    assert history[0]["status"] == "pending"
    assert json.loads((tmp_path / "history.json").read_text())[0]["total_odds"] == 2.6


def test_live_model_reproduces_backtested_model():
    """The live pipeline must be the exact model that was validated and backtested."""
    from pathlib import Path
    import pytest
    from src.predict import fit_live_model
    processed = Path(__file__).resolve().parents[1] / "data" / "processed"
    if not (processed / "predictions_dc.parquet").exists():
        pytest.skip("predictions not built")
    matches = pd.read_parquet(processed / "matches.parquet")
    dc = pd.read_parquet(processed / "predictions_dc.parquet")
    dc = dc[dc.variant == "blend"].set_index("match_id")
    date = pd.Timestamp("2025-12-20")
    day = matches[matches.date.dt.normalize() == date]
    model, _ = fit_live_model(matches, day, date)
    for match in day.itertuples():
        live = model.expected_goals(match.home_team, match.away_team)
        assert abs(live[0] - dc.loc[match.match_id, "lambda_home"]) < 1e-3
        assert abs(live[1] - dc.loc[match.match_id, "lambda_away"]) < 1e-3


def _fixture(home, away, date, kickoff, home_p):
    markets = [{"market": m, "label": m, "probability": p, "market_probability": p}
               for m, p in (("home_win", home_p), ("draw", 0.25), ("away_win", 0.75 - home_p))]
    markets += [{"market": "over_1.5", "label": "o", "probability": 0.8, "market_probability": 0.78}]
    return {"date": date, "time": "15:00", "kickoff_utc": kickoff, "home": home, "away": away,
            "expected_goals": [1.5, 1.0], "top_scorelines": [], "markets": markets}


def test_archive_keeps_pre_kickoff_prediction_and_settles(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "ARCHIVE_DIR", tmp_path)
    morning = pd.Timestamp("2026-10-24 06:00")
    early = _fixture("Arsenal", "Everton", "2026-10-24", "2026-10-24T11:30:00Z", 0.60)
    late = _fixture("Chelsea", "Tottenham", "2026-10-24", "2026-10-24T16:30:00Z", 0.50)
    predict.archive_snapshot([early, late], {}, "R1", morning)
    # Afternoon run: the early match has kicked off and is no longer in the fixture list.
    predict.archive_snapshot([_fixture("Chelsea", "Tottenham", "2026-10-24", "2026-10-24T16:30:00Z", 0.55)],
                             {}, "R1", pd.Timestamp("2026-10-24 13:00"))
    snapshot = json.loads((tmp_path / "2026-10-24.json").read_text())
    probabilities = {f["home"]: f["markets"][0]["probability"] for f in snapshot["fixtures"]}
    assert probabilities == {"Arsenal": 0.60, "Chelsea": 0.55}

    matches = pd.DataFrame([{"home_team": "Arsenal", "away_team": "Everton", "season": "2026/27",
                             "home_goals": 2, "away_goals": 0, "first_scorer": "home",
                             "home_led_at_any_point": True, "away_led_at_any_point": False}])
    index = predict.settle_archive(matches)
    assert index == [{"date": "2026-10-24", "fixtures": 2, "settled": 1}]
    record = predict.live_record()
    assert record["matches"] == 1 and record["result_hit_rate"] == 1.0
    assert record["confident_picks"] == 1 and record["confident_hit_rate"] == 1.0


def test_displayed_slips_show_frozen_slip_once_started():
    history = [{"round": "R1", "tier": "big", "status": "pending", "total_odds": 10.0, "win_probability": 0.1,
                "legs": [{"kickoff_utc": "2026-10-24T11:30:00Z"}]}]
    fresh = {"big": {"total_odds": 11.0, "win_probability": 0.09, "legs": []}}
    before = predict.displayed_slips("R1", fresh, history, pd.Timestamp("2026-10-24 10:00"))
    after = predict.displayed_slips("R1", fresh, history, pd.Timestamp("2026-10-24 12:00"))
    assert before["big"]["total_odds"] == 11.0 and not before["big"]["locked"]
    assert after["big"]["total_odds"] == 10.0 and after["big"]["locked"]
