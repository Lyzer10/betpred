import pandas as pd

from src.accumulators import Tier
from src.final_churn_study import select_variants


TIER = Tier("test", 2.5, 3.5, 2, 2)


def _pool(rows):
    return pd.DataFrame([
        {"match_id": match, "leg_key": f"{match}:over_1.5", "preview_probability": preview_probability,
         "final_probability": final_probability, "preview_odds": preview_odds, "final_odds": final_odds,
         "won": 1}
        for match, preview_probability, final_probability, preview_odds, final_odds in rows
    ])


def _keys(frame):
    return tuple(frame.leg_key)


def test_identical_preview_and_final_make_all_variants_identical():
    pool = _pool([("A", 0.80, 0.80, 1.60, 1.60), ("B", 0.75, 0.75, 1.70, 1.70)])
    selected = select_variants(pool, TIER)
    assert _keys(selected["F"]) == _keys(selected["P"]) == _keys(selected["K"])
    assert selected["reason"] == "kept_preview"


def test_keep_rule_takes_final_when_it_is_more_than_three_percent_better():
    pool = _pool([
        ("A", 0.90, 0.60, 1.60, 1.60), ("B", 0.90, 0.60, 1.60, 1.60),
        ("C", 0.60, 0.90, 1.60, 1.60), ("D", 0.60, 0.90, 1.60, 1.60),
    ])
    selected = select_variants(pool, TIER)
    assert set(_keys(selected["P"])) == {"A:over_1.5", "B:over_1.5"}
    assert set(_keys(selected["F"])) == {"C:over_1.5", "D:over_1.5"}
    assert _keys(selected["K"]) == _keys(selected["F"])
    assert selected["reason"] == "final_more_than_3pct_better"


def test_keep_rule_takes_final_when_preview_slip_leaves_tier_at_final_prices():
    pool = _pool([
        ("A", 0.90, 0.70, 1.60, 2.00), ("B", 0.90, 0.70, 1.60, 2.00),
        ("C", 0.60, 0.80, 1.70, 1.60), ("D", 0.60, 0.80, 1.70, 1.60),
    ])
    selected = select_variants(pool, TIER)
    assert set(_keys(selected["P"])) == {"A:over_1.5", "B:over_1.5"}
    assert float(selected["P"].final_odds.prod()) > TIER.max_odds
    assert _keys(selected["K"]) == _keys(selected["F"])
    assert selected["reason"] == "preview_final_odds_outside_tier"


def test_preview_selection_excludes_legs_below_minimum_price():
    pool = _pool([
        ("A", 0.99, 0.70, 1.01, 1.60), ("B", 0.99, 0.70, 1.01, 1.60),
        ("C", 0.80, 0.80, 1.60, 1.60), ("D", 0.75, 0.75, 1.70, 1.70),
    ])
    selected = select_variants(pool, TIER)
    assert set(_keys(selected["P"])) == {"C:over_1.5", "D:over_1.5"}
