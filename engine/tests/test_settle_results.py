"""Regression cases captured from actual pending November matches."""
import copy
import json
from pathlib import Path

import pandas as pd
import pytest
import requests

from src import predict, settle_results as repair


@pytest.fixture
def events():
    return json.loads((Path(__file__).parent / "fixtures" / "espn_pending_results.json").read_text())["events"]


def fixture(event, league="EPL"):
    result = repair.parse_result(event, league)
    return {"date": result["date"], "kickoff_utc": event["date"], "home": result["home"],
            "away": result["away"], "league": league, "markets": [{"market": "away_win", "probability": .45}],
            "best_pick": {"market": "away_win", "probability": .45}}


def test_real_completed_result_and_goal_sequence(events):
    result = repair.parse_result(events[0], "EPL")
    assert result["score"] == [0, 1]
    assert result["outcomes"]["away_win"] is True
    assert result["outcomes"]["away_1up"] is True
    assert result["outcomes"]["home_first"] is False
    assert result["outcomes"]["over_1.5"] is False


def test_real_equalizer_does_not_mean_away_led(events):
    outcomes = repair.parse_result(events[1], "BUNDES")["outcomes"]
    assert outcomes["draw"] and outcomes["home_1up"]
    assert not outcomes["away_1up"]


def test_real_own_goal_is_credited_to_beneficiary(events):
    result = repair.parse_result(events[2], "BUNDES")
    assert result["score"] == [3, 1]
    assert result["outcomes"]["home_first"] is True
    assert result["outcomes"]["away_first"] is False
    assert result["outcomes"]["away_1up"] is False


@pytest.mark.parametrize("name", ["STATUS_IN_PROGRESS", "STATUS_POSTPONED", "STATUS_ABANDONED", "STATUS_FINAL_PEN"])
def test_unfinished_or_non_regulation_results_rejected(events, name):
    event = copy.deepcopy(events[0])
    event["status"]["type"]["name"] = name
    assert repair.parse_result(event, "EPL") is None


def test_missing_goals_settles_score_not_timing(events):
    event = copy.deepcopy(events[0])
    event["competitions"][0]["details"] = []
    result = repair.parse_result(event, "EPL")
    assert result["outcomes"]["away_win"] is True
    assert all(result["outcomes"][m] is None for m in repair.TIMING)


def test_unknown_team_is_not_guessed(events):
    event = copy.deepcopy(events[0])
    event["competitions"][0]["competitors"][0]["team"]["displayName"] = "Unknown FC"
    assert repair.parse_result(event, "EPL") is None


class Session:
    def __init__(self, board=None):
        self.board = board
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        if self.board is None:
            raise requests.Timeout("source unavailable")
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return self.board


def test_exact_teams_date_and_league_cached_and_outage_safe(events, tmp_path, monkeypatch):
    monkeypatch.setattr(repair.time, "sleep", lambda _: None)
    f = fixture(events[0])
    session = Session({"leagues": [{"slug": "eng.1"}], "events": [events[0]]})
    found = repair.fetch_pending([f], pd.Timestamp("2026-11-04"), tmp_path, session)
    assert len(found) == 1 and session.calls == 1
    offline = Session()
    assert repair.fetch_pending([f], pd.Timestamp("2026-11-04"), tmp_path, offline) == found
    assert offline.calls == 0
    for altered in ({**f, "home": f["away"], "away": f["home"]},
                    {**f, "kickoff_utc": "2026-11-02T16:30Z"}, {**f, "league": "LALIGA"}):
        assert not repair.fetch_pending([altered], pd.Timestamp("2026-11-04"), tmp_path, session)
    assert not repair.fetch_pending([f], pd.Timestamp("2026-11-04"), tmp_path / "empty", offline)


def test_repair_only_changes_settlement_fields_and_is_idempotent(events, tmp_path, monkeypatch):
    monkeypatch.setattr(repair.time, "sleep", lambda _: None)
    f = fixture(events[0])
    leg = {**{k: f[k] for k in ("home", "away", "date", "kickoff_utc", "league")},
           "market": "away_win", "probability": .45, "odds": 2.3, "won": None}
    slip = {"tier": "safe", "legs": [leg], "total_odds": 2.3, "win_probability": .45, "status": "pending"}
    archive = tmp_path / "archive" / "2026-11-01.json"
    repair.write_changed(archive, {"date": "2026-11-01", "fixtures": [f], "slips": {"safe": slip}})
    output = {"fixtures": [f], "model": {"unchanged": True}, "health": {"stake_factor": .5},
              "days": [{"date": "2026-11-01", "slips": {"safe": slip}}], "history": [slip]}
    repair.write_changed(tmp_path / "predictions.json", output)
    repair.write_changed(tmp_path / "history.json", [slip])
    args = dict(now="2026-11-04", data_dir=tmp_path, history_path=tmp_path / "history.json",
                cache=tmp_path / "cache", session=Session({"leagues": [{"slug": "eng.1"}], "events": [events[0]]}))
    assert repair.repair(**args) == 1
    after = json.loads((tmp_path / "predictions.json").read_text())
    for key in ("fixtures", "model", "health"):
        assert after[key] == output[key]
    assert after["history"][0]["legs"][0] == {**leg, "won": True}
    assert after["days"][0]["slips"]["safe"] == {**slip, "legs": [{**leg, "won": True}], "status": "won"}
    assert json.loads(archive.read_text())["fixtures"][0]["markets"] == f["markets"]
    assert repair.repair(**args) == 0
    assert json.loads((tmp_path / "predictions.json").read_text()) == after


def test_verified_result_survives_later_understat_outage(events, tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "LIVE_DIR", tmp_path)
    monkeypatch.setattr(predict, "HISTORY_PATH", tmp_path / "history.json")
    f = fixture(events[0])
    slip = {"round": f["date"], "tier": "safe", "legs": [{**f, "market": "away_win", "won": True}]}
    repair.write_changed(predict.HISTORY_PATH, [slip])
    empty = pd.DataFrame(columns=["home_team", "away_team", "season", "home_goals", "away_goals",
                                  "first_scorer", "home_led_at_any_point", "away_led_at_any_point"])
    history = predict.update_history(None, {}, empty, pd.Timestamp("2026-11-04"))
    assert history[0]["status"] == "won"
    assert history[0]["legs"][0]["won"] is True


def test_score_conflict_keeps_official_result(events):
    incoming = repair.parse_result(events[0], "EPL")
    official = {"score": [1, 0], "outcomes": {"home_win": True}}
    assert repair.fill_result(official, incoming) == official
