import json
import sys

import numpy as np

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
    predict.archive_snapshot([early, late], {}, "2026-10-24", morning)
    # Afternoon run: the early match has kicked off and is no longer in the fixture list.
    predict.archive_snapshot([_fixture("Chelsea", "Tottenham", "2026-10-24", "2026-10-24T16:30:00Z", 0.55)],
                             {}, "2026-10-24", pd.Timestamp("2026-10-24 13:00"))
    snapshot = json.loads((tmp_path / "2026-10-24.json").read_text())
    probabilities = {f["home"]: f["markets"][0]["probability"] for f in snapshot["fixtures"]}
    assert probabilities == {"Arsenal": 0.60, "Chelsea": 0.55}

    matches = pd.DataFrame([{"home_team": "Arsenal", "away_team": "Everton", "season": "2026/27",
                             "date": pd.Timestamp("2026-10-24 11:30"), "home_goals": 2, "away_goals": 0, "first_scorer": "home",
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


def test_local_day_uses_tanzania_time():
    kickoffs = pd.Series(pd.to_datetime(["2026-10-24 20:00", "2026-10-24 21:30"]))
    # 20:00 UTC = 23:00 EAT (same day); 21:30 UTC = 00:30 EAT next day.
    assert predict.local_day(kickoffs).tolist() == ["2026-10-24", "2026-10-25"]


def test_at_least_matches_brute_force_and_flexi_options():
    import itertools
    probabilities = [0.8, 0.7, 0.6, 0.9]
    brute = sum(np.prod([p if hit else 1 - p for p, hit in zip(probabilities, outcome)])
                for outcome in itertools.product([0, 1], repeat=4) if sum(outcome) >= 3)
    assert abs(predict.at_least(probabilities, 3) - brute) < 1e-12
    assert abs(predict.at_least(probabilities, 4) - np.prod(probabilities)) < 1e-12
    assert [o["min_correct"] for o in predict.flexi_options(probabilities)] == [3, 2]
    assert predict.flexi_options([0.8, 0.7]) == []


def _history_env(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "LIVE_DIR", tmp_path)
    monkeypatch.setattr(predict, "HISTORY_PATH", tmp_path / "history.json")
    return pd.DataFrame(columns=["home_team", "away_team", "season", "home_goals", "away_goals",
                                 "first_scorer", "home_led_at_any_point", "away_led_at_any_point"])


def test_final_slips_are_never_replaced_or_added_to(tmp_path, monkeypatch):
    matches = _history_env(tmp_path, monkeypatch)
    morning, final, evening = (pd.Timestamp(t) for t in ("2026-10-24 04:00", "2026-10-24 13:00", "2026-10-24 15:00"))
    predict.update_history("R1", {"safe": _slip("2026-10-24T18:00:00"), "big": _slip("2026-10-24T18:00:00")},
                           matches, morning)
    # The final run keeps only Safe: the morning's Big preview is dropped, Safe becomes final.
    history = predict.update_history("R1", {"safe": _slip("2026-10-24T18:00:00")}, matches, final, final=True)
    assert [(e["tier"], e["final"]) for e in history] == [("safe", True)]
    # A later run before kickoff proposes new slips: nothing changes for a final day.
    changed = _slip("2026-10-24T19:00:00")
    changed["total_odds"] = 3.1
    history = predict.update_history("R1", {"safe": changed, "medium": changed}, matches, evening)
    assert [(e["tier"], e["total_odds"]) for e in history] == [("safe", 2.6)]
    shown = predict.displayed_slips("R1", {"safe": changed, "medium": changed}, history, evening)
    assert list(shown) == ["safe"] and shown["safe"]["final"] and not shown["safe"]["locked"]
    assert shown["safe"]["total_odds"] == 2.6


def test_preview_slips_still_update_before_final(tmp_path, monkeypatch):
    matches = _history_env(tmp_path, monkeypatch)
    predict.update_history("R1", {"safe": _slip("2026-10-24T18:00:00")}, matches, pd.Timestamp("2026-10-24 04:00"))
    changed = _slip("2026-10-24T18:00:00")
    changed["total_odds"] = 3.1
    history = predict.update_history("R1", {"safe": changed}, matches, pd.Timestamp("2026-10-24 10:00"))
    assert history[0]["total_odds"] == 3.1 and not history[0]["final"]


def test_pipeline_publishes_cleanly_when_there_are_no_fixtures(tmp_path, monkeypatch):
    match_columns = ["match_id", "season", "date", "home_team", "away_team", "home_goals", "away_goals",
                     "first_scorer", "home_led_at_any_point", "away_led_at_any_point"]
    matches = pd.DataFrame(columns=match_columns).astype({"date": "datetime64[ns]"})
    goals = pd.DataFrame(columns=["match_id", "minute", "team"])
    fixture_columns = ["date", "time", "home_team", "away_team", "kickoff_utc", "odds_source"]

    monkeypatch.setattr(sys, "argv", ["predict", "--no-refresh"])
    monkeypatch.setattr(pd, "read_parquet", lambda path: matches.copy() if "matches" in str(path) else goals.copy())
    monkeypatch.setattr(predict, "build", lambda **kwargs: (matches.copy(), goals.copy()))
    monkeypatch.setattr(predict, "load_fixtures", lambda *args, **kwargs: pd.DataFrame(columns=fixture_columns))
    monkeypatch.setattr(predict, "add_betpawa_fixtures", lambda fixtures, *args: fixtures)
    monkeypatch.setattr(predict, "betpawa_prices", lambda *args: pd.DataFrame())
    monkeypatch.setattr(predict, "understat_results", lambda *args: matches.copy())
    monkeypatch.setattr(predict, "settle_archive", lambda *args: [])
    monkeypatch.setattr(predict, "settled_predictions", lambda: [])
    monkeypatch.setattr(predict, "pair_monitor", lambda *args: [])
    monkeypatch.setattr(predict, "load_paused", set)
    monkeypatch.setattr(predict, "save_paused", lambda *args: None)
    monkeypatch.setattr(predict, "update_history", lambda *args, **kwargs: [])
    monkeypatch.setattr(predict, "recent_results", lambda *args: [])
    monkeypatch.setattr(predict, "backtest_summary", lambda: {})
    monkeypatch.setattr(predict, "backfill_archive", lambda *args: 0)
    monkeypatch.setattr(predict, "live_record", lambda: {"matches": 0})
    monkeypatch.setattr(predict, "clv_report", lambda *args: {})
    monkeypatch.setattr(predict, "health_check", lambda *args: {"status": "ok"})
    monkeypatch.setattr(predict, "slip_leg_monitor", lambda *args: [])
    monkeypatch.setattr(predict, "realised_slips", lambda *args: {})
    output_path = tmp_path / "predictions.json"
    monkeypatch.setattr(predict, "WEB_DATA_PATH", output_path)

    predict.main()

    output = json.loads(output_path.read_text())
    assert output["fixtures"] == [] and output["days"] == []


def test_backfill_uses_only_what_was_known_before_the_match(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "ARCHIVE_DIR", tmp_path)
    fixture = {"league": {"code": "EPL"}, "date": "2026-10-24", "kickoff_utc": "2026-10-24T14:00:00Z", "home": "Arsenal",
               "away": "Chelsea", "markets": [{"market": "home_1up", "label": "Home 1Up", "probability": 0.7, "betpawa_odds": 1.3},
                                              {"market": "over_0.5", "label": "Over 0.5 goals", "probability": 0.95, "betpawa_odds": 1.05}],
               "result": {"score": [2, 0]}}
    (tmp_path / "2026-10-24.json").write_text(json.dumps({"date": "2026-10-24", "fixtures": [fixture]}))
    rows = [("2026/27", "2026-09-01", "Arsenal", "Chelsea", 1, 1), ("2026/27", "2026-10-24 14:00", "Arsenal", "Chelsea", 2, 0)]
    history = pd.DataFrame(rows, columns=["season", "date", "home_team", "away_team", "home_goals", "away_goals"])
    history["date"] = pd.to_datetime(history.date, format="mixed")
    assert predict.backfill_archive({"EPL": history}, set(), pd.Timestamp("2026-10-25 12:00")) == 1
    filled = json.loads((tmp_path / "2026-10-24.json").read_text())["fixtures"][0]
    assert filled["context"]["home"]["played"] == 1                       # the match itself is not in its "before" table
    assert [m["date"] for m in filled["head_to_head"]["meetings"]] == ["2026-09-01"]
    assert filled["best_pick"]["market"] == "home_1up" and filled["best_pick"]["odds"] == 1.3
    assert filled["result"] == {"score": [2, 0]}                          # results untouched
