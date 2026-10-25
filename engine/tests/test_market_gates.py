import numpy as np
import pandas as pd

from src.market_gates import evaluate


def _legs(stated: float, true: float, n: int = 1200, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    p = np.clip(stated + rng.normal(0, 0.05, n), 0.05, 0.95)
    return pd.DataFrame({
        "date": pd.date_range("2024-08-10", periods=n // 6, freq="7D").repeat(6),
        "market": "over_1.5", "p_col": p, "bookmaker_probability": p,
        "won": (rng.random(n) < p + (true - stated)).astype(int),
    })


def test_over_confident_market_fails():
    r = evaluate("X", "over_1.5", _legs(0.70, 0.62), "p_col", np.random.default_rng(0))
    assert r["status"] == "FAIL" and not r["C2"]


def test_under_confident_market_is_kept():
    # Wins more often than stated: slips are safer than shown, so it must not be removed.
    r = evaluate("X", "over_1.5", _legs(0.70, 0.78), "p_col", np.random.default_rng(0))
    assert r["status"] == "PASS"


def test_too_few_legs_is_insufficient():
    r = evaluate("X", "over_1.5", _legs(0.70, 0.70, n=120), "p_col", np.random.default_rng(0))
    assert r["status"] == "INSUFFICIENT"


def test_epl_gates_use_the_live_walk_forward_blend_not_the_stored_column():
    from src.accumulators import blend_with_market
    from src.market_gates import gate_column
    legs = pd.DataFrame({"season": ["2024/25"] * 4 + ["2025/26"] * 4, "model_probability": [0.7, 0.4, 0.6, 0.3] * 2,
                         "bookmaker_probability": [0.6, 0.5, 0.5, 0.4] * 2, "won": [1, 0, 1, 0] * 2,
                         "probability": 0.99})                      # stale stored column must be ignored
    column = gate_column(legs, "blended")
    expected, _ = blend_with_market(legs.drop(columns="live_probability"), None)
    assert column == "live_probability" and np.allclose(legs[column], expected)
    assert gate_column(legs, "market") == "market_probability"


def test_live_legs_use_the_published_probability_of_one_league():
    from src.market_gates import live_legs
    fixtures = [{"league": {"code": "SERIEA"}, "kickoff_utc": "2026-10-25T11:30:00Z",
                 "markets": [{"market": "home_1up", "probability": 0.61, "market_probability": 0.58},
                             {"market": "btts_yes", "probability": 0.5, "market_probability": 0.5}],
                 "result": {"outcomes": {"home_1up": True, "btts_yes": False}}},
                {"league": {"code": "EPL"}, "kickoff_utc": "2026-10-25T14:00:00Z",
                 "markets": [{"market": "home_1up", "probability": 0.7, "market_probability": 0.69}],
                 "result": {"outcomes": {"home_1up": False}}}]
    legs = live_legs("SERIEA", "market_probability", fixtures)
    assert legs.market.tolist() == ["home_1up"]                    # slip markets of that league only
    assert legs.market_probability.iloc[0] == 0.61 and legs.bookmaker_probability.iloc[0] == 0.58
    assert legs.won.iloc[0] == 1
