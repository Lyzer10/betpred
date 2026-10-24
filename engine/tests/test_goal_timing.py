import numpy as np

from src.goal_timing import simulate_match


def test_first_scorer_matches_analytic_constant_rate_case():
    lam, mu = 1.5, 1.0
    result = simulate_match(lam, mu, np.full(90, 1 / 90), np.ones(5), simulations=100_000, seed=11)
    expected = lam / (lam + mu) * (1 - np.exp(-(lam + mu)))
    assert abs(result["sim_home_first"] - expected) < 0.005


def test_1up_dominates_first_scorer_and_match_win():
    result = simulate_match(1.6, 1.2, np.full(90, 1 / 90), np.ones(5), seed=2)
    assert result["sim_home_1up"] >= result["sim_home_first"]
    assert result["sim_home_1up"] >= result["sim_home_win"]


def test_first_scorer_probabilities_sum_to_one():
    result = simulate_match(1.3, 0.9, np.full(90, 1 / 90), np.ones(5), seed=3)
    assert np.isclose(result["sim_home_first"] + result["sim_away_first"] + result["sim_no_goal"], 1)


def test_fixed_seed_is_identical():
    arguments = (1.4, 1.1, np.full(90, 1 / 90), np.array([1.0, 0.9, 0.8, 1.1, 1.2]))
    assert simulate_match(*arguments, seed=99) == simulate_match(*arguments, seed=99)


def test_dynamic_rates_remain_anchored_to_dc_goal_means():
    result = simulate_match(1.6, 1.2, np.full(90, 1 / 90), np.array([1.0, 0.9, 0.8, 1.1, 1.2]),
                            simulations=100_000, seed=17)
    assert abs(result["sim_mean_home_goals"] / 1.6 - 1) < 0.01
    assert abs(result["sim_mean_away_goals"] / 1.2 - 1) < 0.01
