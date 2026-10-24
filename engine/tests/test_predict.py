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
