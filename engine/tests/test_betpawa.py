import numpy as np
import pandas as pd

from src.betpawa import parse_markets
from src.predict import attach_betpawa, kelly_fraction


def _market(type_id, rows):
    return {"marketType": {"id": type_id}, "row": [
        {"handicap": handicap, "prices": [{"name": n, "odds": o, "suspended": False} for n, o in prices]}
        for handicap, prices in rows]}


def test_parse_markets_maps_every_supported_market():
    markets = [
        _market("3743", [(None, [("1", 4.89), ("X", 4.69), ("2", 1.65)])]),
        _market("28000810", [(None, [("1", 2.27), ("X", 4.75), ("2", 1.33)])]),
        _market("28000224", [(4, [("1", 2.74), ("None", 23.95), ("2", 1.53)]), (8, [("1", 3.0), ("2", 2.0)])]),
        _market("3795", [(None, [("Yes", 1.54), ("No", 2.48)])]),
        _market("5000", [(2, [("Over", 1.02), ("Under", 16.1)]), (10, [("Over", 1.47), ("Under", 2.77)]),
                         (14, [("Over", 2.15), ("Under", 1.74)]), (18, [("Over", 3.5), ("Under", 1.3)])]),
        _market("4693", [(None, [("1X", 2.24)])]),  # double chance: not modelled, ignored
    ]
    odds = parse_markets(markets)
    assert odds == {
        "home_win": 4.89, "draw": 4.69, "away_win": 1.65, "home_1up": 2.27, "away_1up": 1.33,
        "home_first": 2.74, "away_first": 1.53, "btts_yes": 1.54, "btts_no": 2.48,
        "over_0.5": 1.02, "over_2.5": 1.47, "under_2.5": 2.77, "over_3.5": 2.15, "under_3.5": 1.74,
    }


def test_parse_markets_skips_suspended_and_empty_prices():
    market = _market("3743", [(None, [("1", 0.0), ("X", 3.2), ("2", 2.1)])])
    market["row"][0]["prices"][2]["suspended"] = True
    assert parse_markets([market]) == {"draw": 3.2}


def test_attach_betpawa_ignores_same_teams_on_another_date():
    legs = pd.DataFrame({"home_team": ["Arsenal", "Arsenal"], "away_team": ["Everton", "Everton"],
                         "market": ["home_win", "draw"], "kickoff_utc": pd.to_datetime(["2026-10-24 14:00"] * 2),
                         "probability": [0.66, 0.22], "bookmaker_probability": [0.66, 0.22], "odds": [1.45, 4.2]})
    betpawa = pd.DataFrame({"home_team": ["Arsenal", "Arsenal"], "away_team": ["Everton", "Everton"],
                            "market": ["home_win", "draw"], "betpawa_odds": [1.60, 5.0],
                            "kickoff_utc": pd.to_datetime(["2026-10-24 14:00", "2027-01-10 15:00"])})
    result = attach_betpawa(legs, betpawa)
    assert result.betpawa_odds.iloc[0] == 1.60 and np.isnan(result.betpawa_odds.iloc[1])
    assert result.odds.tolist() == [1.60, 4.2]          # falls back to the estimate
    assert abs(result.edge.iloc[0] - (0.66 * 1.60 - 1)) < 1e-12
    assert not result.price_warning.iloc[0]             # market says +5.6%: below the 8% warning line
    moved = attach_betpawa(legs.iloc[:1], betpawa.iloc[:1].assign(betpawa_odds=1.70))
    assert bool(moved.price_warning.iloc[0])            # market says +12.2%: likely news, warn


def test_kelly_fraction():
    assert abs(kelly_fraction(0.55, 2.0) - 0.10) < 1e-12   # (0.55*2-1)/(2-1)
    assert kelly_fraction(0.40, 2.0) == 0.0                 # negative edge: no stake
    assert kelly_fraction(0.5, 1.0) == 0.0
