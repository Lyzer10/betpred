import pandas as pd
from src.build_dataset import derive_goal_states
from src.fetch_understat import normalize_season


def goals(*events):
    return pd.DataFrame(events, columns=["minute", "team"])


def test_nil_nil():
    assert derive_goal_states(goals()) == ("none", False, False)


def test_comeback_from_one_two_to_two_two():
    events = goals((5, "home"), (20, "away"), (40, "away"), (80, "home"))
    assert derive_goal_states(events) == ("home", True, True)


def test_own_goal_is_credited_to_benefiting_team():
    # The normalized event side is the beneficiary, regardless of scorer identity.
    events = goals((12, "away"))
    assert derive_goal_states(events) == ("away", False, True)


def test_understat_own_goal_side_is_inverted_to_beneficiary():
    match = {"id": "1", "isResult": True, "h": {"title": "Arsenal"},
             "a": {"title": "Chelsea"}, "xG": {"h": "0.1", "a": "0.2"},
             "datetime": "2024-08-01 15:00:00"}
    _, normalized = normalize_season(2024, [match], {"1": {
        "h": [{"minute": "12", "result": "OwnGoal"}], "a": []}})
    assert normalized.to_dict("records") == [{"understat_id": "1", "minute": 12, "team": "away"}]
