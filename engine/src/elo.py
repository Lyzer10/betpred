"""Leakage safe chronological Premier League Elo features."""
from __future__ import annotations

import math
import pandas as pd


def expected_home(home_rating: float, away_rating: float, home_advantage: float = 60) -> float:
    return 1 / (1 + 10 ** ((away_rating - home_rating - home_advantage) / 400))


def add_elo_features(matches: pd.DataFrame, k: float = 20, home_advantage: float = 60, league="EPL") -> pd.DataFrame:
    """Attach ratings recorded before each game, then update from its result."""
    result = matches.copy()
    result["_order"] = range(len(result))
    result = result.sort_values(["date", "_order"])
    ratings: dict[str, float] = {}
    previous_season = None
    home_values, away_values = {}, {}
    for index, row in result.iterrows():
        if previous_season is not None and row["season"] != previous_season:
            ratings = {team: 1500 + (rating - 1500) * (2 / 3) for team, rating in ratings.items()}
        previous_season = row["season"]
        home = ratings.setdefault(row["home_team"], 1500.0)
        away = ratings.setdefault(row["away_team"], 1500.0)
        home_values[index], away_values[index] = home, away
        expected = expected_home(home, away, home_advantage)
        actual = 1.0 if row["home_goals"] > row["away_goals"] else 0.0 if row["home_goals"] < row["away_goals"] else 0.5
        change = k * (actual - expected)
        ratings[row["home_team"]] = home + change
        ratings[row["away_team"]] = away - change
    result["elo_home"] = pd.Series(home_values)
    result["elo_away"] = pd.Series(away_values)
    return result.sort_values("_order").drop(columns="_order").reset_index(drop=True)


def outcome_probabilities(home_rating: float, away_rating: float, home_advantage: float = 60) -> tuple[float, float, float]:
    """Convert Elo strength into H/D/A using a fixed draw propensity."""
    decisive_home = expected_home(home_rating, away_rating, home_advantage)
    # Draws peak for evenly matched sides and diminish with a rating gap.
    draw = 0.28 * math.exp(-abs((home_rating + home_advantage) - away_rating) / 400)
    return decisive_home * (1 - draw), draw, (1 - decisive_home) * (1 - draw)
