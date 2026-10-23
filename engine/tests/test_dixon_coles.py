import numpy as np
import pandas as pd

from src.dixon_coles import (
    fit_dixon_coles, market_probabilities, promoted_team_values, tau_values,
)


def test_tau_values_for_low_scores():
    lam, mu, rho = 1.4, 1.1, -0.08
    assert tau_values(0, 0, lam, mu, rho) == 1 - lam * mu * rho
    assert tau_values(0, 1, lam, mu, rho) == 1 + lam * rho
    assert tau_values(1, 0, lam, mu, rho) == 1 + mu * rho
    assert tau_values(1, 1, lam, mu, rho) == 1 - rho
    assert tau_values(2, 1, lam, mu, rho) == 1


def test_score_matrix_sums_to_one():
    from src.dixon_coles import DixonColesModel
    model = DixonColesModel(["A", "B"], np.array([0.1, -0.1]), np.array([0.0, 0.1]), 0.2, -0.05, 0.0019, "goals")
    matrix, _ = model.predict("A", "B")
    assert abs(matrix.sum() - 1) < 1e-6


def test_market_probabilities_from_hand_built_matrix():
    matrix = np.zeros((3, 3))
    matrix[0, 0], matrix[1, 0], matrix[0, 2], matrix[2, 2] = 0.1, 0.2, 0.3, 0.4
    markets = market_probabilities(matrix)
    assert markets["prob_home"] == 0.2
    assert markets["prob_draw"] == 0.5
    assert markets["prob_away"] == 0.3
    assert markets["prob_over15"] == 0.7
    assert markets["prob_over25"] == 0.4
    assert markets["prob_btts"] == 0.4
    assert np.isclose(markets["prob_home_clean_sheet"], 0.3)
    assert np.isclose(markets["prob_away_clean_sheet"], 0.4)


def test_promoted_team_initialization_uses_relegated_mean():
    values = promoted_team_values(["New"], ["R1", "R2", "R3"],
                                  {"R1": -0.1, "R2": -0.2, "R3": -0.3},
                                  {"R1": 0.2, "R2": 0.3, "R3": 0.4})
    assert np.allclose(values["New"], (-0.2, 0.3))


def test_fit_recovers_known_parameters_on_synthetic_data():
    rng = np.random.default_rng(42)
    teams = ["A", "B", "C", "D"]
    attack = np.array([0.22, 0.08, -0.10, -0.20])
    defence = np.array([-0.15, 0.05, 0.12, -0.02])
    home_adv = 0.24
    rows = []
    for i in range(2000):
        home, away = rng.choice(4, 2, replace=False)
        lam = np.exp(home_adv + attack[home] + defence[away])
        mu = np.exp(attack[away] + defence[home])
        rows.append({"date": pd.Timestamp("2024-01-01") + pd.Timedelta(i, unit="h"),
                     "home_team": teams[home], "away_team": teams[away],
                     "home_goals": rng.poisson(lam), "away_goals": rng.poisson(mu),
                     "home_xg": lam, "away_xg": mu})
    fitted = fit_dixon_coles(pd.DataFrame(rows), pd.Timestamp("2025-01-01"), xi=0, variant="goals")
    fitted_attack = np.array([fitted.attack_map[t] for t in teams])
    fitted_defence = np.array([fitted.defence_map[t] for t in teams])
    assert np.allclose(fitted_attack, attack, atol=0.1)
    assert np.allclose(fitted_defence, defence, atol=0.1)
    assert abs(fitted.home_advantage - home_adv) < 0.1
