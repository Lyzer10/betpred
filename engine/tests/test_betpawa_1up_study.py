import numpy as np
import pandas as pd

from src.betpawa_1up_study import study


def _legs(n_days, per_day, informative, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for d in range(n_days):
        for _ in range(per_day):
            truth = rng.uniform(0.3, 0.7)
            ours = np.clip(truth + rng.normal(0, 0.15), 0.05, 0.95)          # noisy
            odds = 0.95 / (truth if informative else rng.uniform(0.3, 0.7))
            rows.append({"day": f"2026-11-{d + 1:02d}", "market": "home_1up", "ours": ours, "odds": odds,
                         "won": float(rng.random() < truth)})
    return pd.DataFrame(rows)


def test_too_little_data_is_reported_not_decided():
    assert study(_legs(5, 10, True))["status"] == "insufficient"


def test_an_informative_price_is_adopted_and_a_useless_one_is_not():
    assert study(_legs(30, 60, True))["status"] == "use combination"
    assert study(_legs(30, 60, False))["status"] == "keep ours"
