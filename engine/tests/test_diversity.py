import numpy as np
import pandas as pd
import pytest

from src.accumulators import TIERS, best_slip
from src.diversity_study import daily_log_growth, select_day_slips


def _pool() -> pd.DataFrame:
    probabilities = np.linspace(0.95, 0.55, 15)
    return pd.DataFrame({
        "match_id": [f"m{i}" for i in range(15)],
        "match_key": [f"EPL:m{i}" for i in range(15)],
        "market": ["home_win"] * 15,
        "probability": probabilities,
        "odds": [1.5] * 15,
        "won": [1] * 15,
    })


def test_variant_a_matches_independent_best_slip():
    pool = _pool()
    selected = select_day_slips(pool, "A")

    for tier in TIERS:
        expected = best_slip(pool.assign(match_id=pool.match_key), tier)
        assert expected is not None
        assert list(selected[tier.name].match_key) == list(pool.loc[expected].match_key)


def test_variant_b_never_repeats_a_match_across_tiers():
    selected = select_day_slips(_pool(), "B")

    match_sets = [set(selected[tier.name].match_key) for tier in TIERS]
    assert all(left.isdisjoint(right)
               for index, left in enumerate(match_sets) for right in match_sets[index + 1:])


def test_variant_c_reuses_at_most_one_previous_match():
    selected = select_day_slips(_pool(), "C")

    used = set()
    for tier in TIERS:
        current = set(selected[tier.name].match_key)
        assert len(current & used) <= 1
        used.update(current)


def test_daily_log_growth_matches_hand_computation():
    slips = {
        "safe": {"won": 1, "total_odds": 3.0},
        "medium": {"won": 0, "total_odds": 5.0},
    }

    assert daily_log_growth(slips) == pytest.approx(np.log(1.04))
