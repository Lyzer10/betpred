import pandas as pd
from src.elo import add_elo_features


def test_elo_features_are_pre_match_and_do_not_leak_result():
    base = pd.DataFrame([
        {"date": pd.Timestamp("2024-08-01"), "season": "2024/25", "home_team": "Arsenal", "away_team": "Chelsea", "home_goals": 5, "away_goals": 0},
        {"date": pd.Timestamp("2024-08-08"), "season": "2024/25", "home_team": "Chelsea", "away_team": "Arsenal", "home_goals": 0, "away_goals": 1},
    ])
    changed = base.copy()
    changed.loc[0, ["home_goals", "away_goals"]] = [0, 5]
    original_features = add_elo_features(base)
    changed_features = add_elo_features(changed)
    assert original_features.loc[0, ["elo_home", "elo_away"]].tolist() == [1500, 1500]
    assert changed_features.loc[0, ["elo_home", "elo_away"]].tolist() == [1500, 1500]
    assert original_features.loc[1, "elo_home"] != changed_features.loc[1, "elo_home"]

