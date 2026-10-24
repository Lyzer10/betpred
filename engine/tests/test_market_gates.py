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
