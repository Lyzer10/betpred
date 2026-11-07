import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.new_markets_study import MARKETS, _logit
from src.team_goals_dnb_live_study import build_settled_priced_legs, last_pre_kickoff_prices, summarize_markets


def _identity_models():
    models = {}
    x = np.linspace(0.1, 0.9, 50)
    y = (np.arange(50) % 2).astype(int)
    for m in MARKETS:
        models[("EPL", m)] = LogisticRegression(C=1.0).fit(_logit(x).reshape(-1, 1), y)
    return models


def test_last_pre_kickoff_prices_takes_latest_before_kickoff_and_skips_in_play_or_zero():
    prices = pd.DataFrame([
        {"snapshot_utc": pd.Timestamp("2026-10-30 10:00"), "home": "Arsenal", "away": "Everton",
         "kickoff_utc": pd.Timestamp("2026-10-30 15:00"), "market": "home_over_0.5", "betpawa_odds": 1.20},
        {"snapshot_utc": pd.Timestamp("2026-10-30 14:30"), "home": "Arsenal", "away": "Everton",
         "kickoff_utc": pd.Timestamp("2026-10-30 15:00"), "market": "home_over_0.5", "betpawa_odds": 1.18},
        {"snapshot_utc": pd.Timestamp("2026-10-30 15:05"), "home": "Arsenal", "away": "Everton",
         "kickoff_utc": pd.Timestamp("2026-10-30 15:00"), "market": "home_over_0.5", "betpawa_odds": 1.05},
        {"snapshot_utc": pd.Timestamp("2026-10-30 14:30"), "home": "Arsenal", "away": "Everton",
         "kickoff_utc": pd.Timestamp("2026-10-30 15:00"), "market": "dnb_home", "betpawa_odds": 0.0},
    ])
    lookup = last_pre_kickoff_prices(prices)
    assert lookup[("Arsenal", "Everton", pd.Timestamp("2026-10-30 15:00"), "home_over_0.5")] == 1.18
    assert ("Arsenal", "Everton", pd.Timestamp("2026-10-30 15:00"), "dnb_home") not in lookup


def test_dnb_skips_drawn_matches_and_summaries_report_needed_legs():
    fixtures = [
        {
            "date": "2026-10-30", "kickoff_utc": "2026-10-30T15:00:00Z",
            "league": {"code": "EPL"}, "home": "Arsenal", "away": "Everton",
            "markets": [
                {"market": "home_win", "market_probability": 0.50},
                {"market": "draw", "market_probability": 0.25},
                {"market": "away_win", "market_probability": 0.25},
                {"market": "over_2.5", "market_probability": 0.55},
                {"market": "under_2.5", "market_probability": 0.45},
            ],
            "result": {"score": [1, 1], "outcomes": {}},
        },
        {
            "date": "2026-10-31", "kickoff_utc": "2026-10-31T15:00:00Z",
            "league": {"code": "EPL"}, "home": "Chelsea", "away": "Tottenham",
            "markets": [
                {"market": "home_win", "market_probability": 0.50},
                {"market": "draw", "market_probability": 0.25},
                {"market": "away_win", "market_probability": 0.25},
                {"market": "over_2.5", "market_probability": 0.55},
                {"market": "under_2.5", "market_probability": 0.45},
            ],
            "result": {"score": [2, 0], "outcomes": {}},
        },
    ]
    prices = pd.DataFrame([
        {"snapshot_utc": pd.Timestamp("2026-10-30 14:00"), "home": home, "away": away,
         "kickoff_utc": pd.Timestamp(ko), "market": m, "betpawa_odds": 2.10}
        for home, away, ko in (("Arsenal", "Everton", "2026-10-30 15:00"), ("Chelsea", "Tottenham", "2026-10-31 15:00"))
        for m in MARKETS
    ])
    legs = build_settled_priced_legs(fixtures, prices, _identity_models(), rho_lookup=lambda _: -0.05)
    assert len(legs[legs.market == "home_over_0.5"]) == 2
    assert len(legs[legs.market == "dnb_home"]) == 1  # drawn match excluded from DNB
    summaries = {s["market"]: s for s in summarize_markets(legs)}
    assert summaries["home_over_0.5"]["legs"] == 2 and summaries["home_over_0.5"]["still_needed"] == 298
    assert summaries["dnb_home"]["legs"] == 1 and summaries["dnb_home"]["still_needed"] == 299
    assert all(s["status"] == "INSUFFICIENT" for s in summaries.values())

