import itertools

import numpy as np
import pandas as pd
import pytest

from src.accumulators import (
    Tier, best_slip, betting_round, blend_with_market, bookmaker_fair_probabilities,
    calibrate_market_probabilities,
)
from src.dixon_coles import market_probabilities, score_matrix
from src.phase1_evaluation import calibration_diagnostic


def _random_legs(seed: int, matches: int = 6, markets: int = 4) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for match in range(matches):
        for market in range(markets):
            probability = rng.uniform(0.3, 0.95)
            rows.append({"match_id": match, "market": f"m{market}", "probability": probability,
                         "odds": float(np.clip(rng.normal(1 / probability, 0.15), 1.05, 6))})
    return pd.DataFrame(rows)


def _brute_force(legs: pd.DataFrame, tier: Tier) -> float:
    best = -np.inf
    per_match = [list(group.index) for _, group in legs.groupby("match_id")]
    for size in range(tier.min_legs, tier.max_legs + 1):
        for matches in itertools.combinations(per_match, size):
            for picks in itertools.product(*matches):
                odds = legs.loc[list(picks), "odds"].prod()
                if tier.min_odds <= odds <= tier.max_odds:
                    best = max(best, legs.loc[list(picks), "probability"].prod())
    return best


@pytest.mark.parametrize("seed", range(5))
def test_best_slip_matches_brute_force(seed):
    legs = _random_legs(seed)
    tier = Tier("t", 2.5, 3.5, 2, 3)
    picks = best_slip(legs, tier)
    expected = _brute_force(legs, tier)
    assert picks is not None
    chosen = legs.loc[picks]
    assert chosen.match_id.is_unique
    assert tier.min_odds <= chosen.odds.prod() <= tier.max_odds
    # Odds bucketing may exclude a combination sitting exactly on the range edge.
    assert chosen.probability.prod() >= expected - 0.01


def test_best_slip_returns_none_when_range_unreachable():
    legs = pd.DataFrame({"match_id": [1, 2], "market": ["a", "b"],
                         "probability": [0.9, 0.9], "odds": [1.1, 1.1]})
    assert best_slip(legs, Tier("t", 2.5, 3.5, 2, 3)) is None


def test_bookmaker_fair_probabilities_round_trip():
    """Odds generated from a known DC matrix must give back that matrix's markets."""
    markets = market_probabilities(score_matrix(1.7, 1.0, -0.06))
    fair = bookmaker_fair_probabilities(1 / markets["prob_home"], 1 / markets["prob_draw"],
                                        1 / markets["prob_away"], 1 / markets["prob_over25"],
                                        1 / (1 - markets["prob_over25"]), -0.06)
    assert abs(fair["over_1.5"] - markets["prob_over15"]) < 0.002
    assert abs(fair["btts_yes"] - markets["prob_btts"]) < 0.002
    assert fair["home_1up"] >= fair["home_win"]
    assert np.isclose(fair["home_win"] + fair["draw"] + fair["away_win"], 1)


def test_betting_round_splits_weekend_and_midweek():
    dates = pd.Series(pd.to_datetime(["2025-03-07", "2025-03-08", "2025-03-10",
                                      "2025-03-11", "2025-03-13", "2025-03-14"]))
    rounds = betting_round(dates).tolist()
    assert rounds[0] == rounds[1] == rounds[2]  # Fri, Sat, Mon
    assert rounds[3] == rounds[4]               # Tue, Thu
    assert len({rounds[0], rounds[3], rounds[5]}) == 3


def test_blend_weight_uses_only_earlier_seasons():
    rng = np.random.default_rng(3)
    truth = rng.uniform(0.2, 0.8, 4000)
    legs = pd.DataFrame({
        "season": np.repeat(["2024/25", "2025/26"], 2000),
        "bookmaker_probability": np.clip(truth + rng.normal(0, 0.02, 4000), 0.01, 0.99),
        "model_probability": np.clip(truth + rng.normal(0, 0.15, 4000), 0.01, 0.99),
        "won": (rng.uniform(size=4000) < truth).astype(int),
    })
    _, weights = blend_with_market(legs)
    assert weights["2024/25"] == 0.5          # no history: default
    assert weights["2025/26"] < 0.5           # noisy model learned to be down-weighted
    # Changing the later season's outcomes must not change the earlier weight.
    legs.loc[legs.season == "2025/26", "won"] = 1 - legs.loc[legs.season == "2025/26", "won"]
    assert blend_with_market(legs)[1]["2024/25"] == 0.5


def test_first_test_weight_is_learned_from_validation_only():
    rng = np.random.default_rng(12)
    validation = pd.DataFrame({
        "season": np.repeat(["2021/22", "2022/23", "2023/24"], 1000),
        "model_probability": np.full(3000, 0.8),
        "market_probability": np.full(3000, 0.5),
        "bookmaker_probability": np.full(3000, 0.5),
        "won": (rng.uniform(size=3000) < 0.5).astype(int),
    })
    test = validation.iloc[:100].copy()
    test["season"] = "2024/25"
    _, weights = blend_with_market(test, validation)
    assert weights["2024/25"] == 0.0


def test_market_calibration_uses_only_prior_seasons():
    rows = []
    for year, (season, won) in enumerate((("2021/22", 0), ("2022/23", 1), ("2023/24", 1)), start=2021):
        rows.extend({"season": season, "date": pd.Timestamp(f"{year}-08-01") + pd.to_timedelta(index, unit="D"),
                     "market": "home_win", "bookmaker_probability": 0.6,
                     "won": won, "model_probability": 0.6} for index in range(20))
    validation = pd.DataFrame(rows)
    test = pd.DataFrame({"season": ["2024/25"], "date": [pd.Timestamp("2024-08-01")], "market": ["home_win"],
                         "bookmaker_probability": [0.6], "won": [1], "model_probability": [0.6]})
    calibrated_validation, calibrated_test = calibrate_market_probabilities(validation, test)
    assert calibrated_validation.loc[calibrated_validation.season == "2021/22", "market_probability"].iloc[0] == 0.6
    assert calibrated_test.market_probability.notna().all()


def test_equal_count_calibration_diagnostic_checks_z_and_slope():
    probability = np.tile(np.linspace(0.1, 0.9, 10), 200)
    rng = np.random.default_rng(44)
    legs = pd.DataFrame({"market": "home_win", "probability": probability,
                         "won": (rng.uniform(size=len(probability)) < probability).astype(int)})
    result = calibration_diagnostic(legs, "home_win", "probability")
    assert result["max_z"] <= 3
    assert 0.8 <= result["slope"] <= 1.2
