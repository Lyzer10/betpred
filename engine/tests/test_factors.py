import pandas as pd

from src.factors import _rest_features, _table_features


def _matches():
    rows = [("m1", "2025-08-16", "A", "B", 2, 0), ("m2", "2025-08-16", "C", "D", 1, 1),
            ("m3", "2025-08-23", "A", "C", 0, 3), ("m4", "2025-08-27", "B", "A", 1, 0)]
    frame = pd.DataFrame(rows, columns=["match_id", "date", "home_team", "away_team", "home_goals", "away_goals"])
    frame["date"] = pd.to_datetime(frame.date)
    frame["season"] = "2025/26"
    return frame


def test_table_uses_only_matches_before_kickoff():
    table = _table_features(_matches()).set_index(["match_id", "side"])
    # Opening day: nobody has played, so everyone gets the league-average prior.
    assert table.loc[("m1", "home"), "ppg"] == table.loc[("m1", "away"), "ppg"] == 1.37
    # Before m3, A has 3 points from 1 game and C has 1 point; the m3 result itself is not counted.
    a, c = table.loc[("m3", "home"), "ppg"], table.loc[("m3", "away"), "ppg"]
    assert abs(a - (3 * 1 / 7 + 1.37 * 6 / 7)) < 1e-12
    assert abs(c - (1 * 1 / 7 + 1.37 * 6 / 7)) < 1e-12


def test_rest_days_count_from_previous_league_match():
    rest = _rest_features(_matches()).set_index(["match_id", "side"]).rest
    assert rest[("m1", "home")] == 14            # no previous match: capped default
    assert rest[("m3", "home")] == 7             # A: 16 Aug -> 23 Aug
    assert rest[("m4", "away")] == 4             # A: 23 Aug -> 27 Aug
