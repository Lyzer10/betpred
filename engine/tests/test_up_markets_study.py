"""Synthetic known-answer tests for Task 17 (Double Chance 1UP and 1X2 2UP study)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.accumulators import PRIORS
from src.dixon_coles import score_matrix
from src.up_markets_study import (
    SCORE_WEIGHTS,
    add_up_actuals,
    derive_up_goal_states,
    enumerate_score_orders,
    raw_up_probabilities_from_matrix,
)


def test_small_score_enumeration_matches_hand_counts():
    """Verify exact goal-order enumeration against hand counts on 1-0, 2-1, 3-1, 1-3, 2-2, 2-3."""
    s10 = enumerate_score_orders(1, 0)
    assert s10["total_orders"] == 1
    assert [o["order"] for o in s10["orders"]] == ["H"]
    assert s10["home_2up_ever_orders"] == 0
    assert s10["p_home_2up_ever"] == 0.0
    assert s10["home_2up_weight"] == 1.0  # 1-0 is a home win, so home_2up weight is 1.0

    s21 = enumerate_score_orders(2, 1)
    assert s21["total_orders"] == 3
    assert [o["order"] for o in s21["orders"]] == ["HHA", "HAH", "AHH"]
    # Only HHA reaches +2 (running diffs [+1, +2, +1]); HAH ([+1, 0, +1]) and AHH ([-1, 0, +1]) do not.
    assert s21["home_2up_ever_orders"] == 1
    assert np.isclose(s21["p_home_2up_ever"], 1.0 / 3.0, atol=1e-12)
    assert s21["home_2up_weight"] == 1.0  # 2-1 is a home win, so home_2up weight is 1.0

    s31 = enumerate_score_orders(3, 1)
    assert s31["total_orders"] == 4
    assert [o["order"] for o in s31["orders"]] == ["HHHA", "HHAH", "HAHH", "AHHH"]
    # All 4 orders end at +2, so all 4 reach a lead of 2.
    assert s31["home_2up_ever_orders"] == 4
    assert s31["p_home_2up_ever"] == 1.0
    assert s31["home_2up_weight"] == 1.0

    # Losing/drawing scores where P(ever 2 ahead | score) determines the non-win weight:
    s13 = enumerate_score_orders(1, 3)
    assert s13["total_orders"] == 4
    assert s13["home_2up_ever_orders"] == 0
    assert s13["p_home_2up_ever"] == 0.0
    assert s13["home_2up_weight"] == 0.0
    assert s13["away_2up_ever_orders"] == 4
    assert s13["away_2up_weight"] == 1.0

    s22 = enumerate_score_orders(2, 2)
    assert s22["total_orders"] == 6
    # Only HHAA reaches +2 out of 6 orders (HHAA, HAHA, HAAH, AHHA, AHAH, AAHH).
    assert s22["home_2up_ever_orders"] == 1
    assert np.isclose(s22["p_home_2up_ever"], 1.0 / 6.0, atol=1e-12)
    assert np.isclose(s22["home_2up_weight"], 1.0 / 6.0, atol=1e-12)
    assert np.isclose(SCORE_WEIGHTS["home_2up"][2, 2], 1.0 / 6.0, atol=1e-12)

    s23 = enumerate_score_orders(2, 3)
    assert s23["total_orders"] == 10
    # Only HHAAA reaches +2 out of 10 orders.
    assert s23["home_2up_ever_orders"] == 1
    assert np.isclose(s23["p_home_2up_ever"], 0.1, atol=1e-12)
    assert np.isclose(s23["home_2up_weight"], 0.1, atol=1e-12)
    assert np.isclose(SCORE_WEIGHTS["home_2up"][2, 3], 0.1, atol=1e-12)


def test_raw_up_probabilities_from_known_matrix():
    """Verify raw_up_probabilities_from_matrix against hand calculation on a known matrix."""
    matrix = score_matrix(1.4, 1.1, -0.05)
    probs = raw_up_probabilities_from_matrix(matrix)

    h, a = np.meshgrid(np.arange(11), np.arange(11), indexing="ij")
    expected_dc1up_1x = float(np.sum(matrix * np.where(h >= a, 1.0, PRIORS["home_1up"])))
    expected_dc1up_x2 = float(np.sum(matrix * np.where(a >= h, 1.0, PRIORS["away_1up"])))
    expected_dc1up_12 = float(1.0 - matrix[0, 0])

    assert np.isclose(probs["dc1up_1x"], expected_dc1up_1x, atol=1e-12)
    assert np.isclose(probs["dc1up_x2"], expected_dc1up_x2, atol=1e-12)
    assert np.isclose(probs["dc1up_12"], expected_dc1up_12, atol=1e-12)

    # home_2up must strictly exceed plain home_win (since 2-2, 2-3, etc. have positive weight)
    home_win = float(np.sum(matrix * (h > a)))
    away_win = float(np.sum(matrix * (a > h)))
    assert probs["home_2up"] > home_win
    assert probs["away_2up"] > away_win


def test_derive_up_goal_states_and_actuals():
    """Verify goal-minute sequence settlement for DC 1UP and 2UP."""
    # Match 1: Home goes 2-0 up (10', 25'), Away comes back to 2-2 (60', 85')
    g1 = pd.DataFrame({"minute": [10, 25, 60, 85], "team": ["home", "home", "away", "away"]})
    h_led1, a_led1, h_2up1, a_2up1 = derive_up_goal_states(g1)
    assert (h_led1, a_led1, h_2up1, a_2up1) == (True, False, True, False)

    # Match 2: Home wins 1-0 (goal at 70') -> never 2 ahead, but won at FT so home_2up = 1
    g2 = pd.DataFrame({"minute": [70], "team": ["home"]})
    h_led2, a_led2, h_2up2, a_2up2 = derive_up_goal_states(g2)
    assert (h_led2, a_led2, h_2up2, a_2up2) == (True, False, False, False)

    # Match 3: 0-0 draw
    g3 = pd.DataFrame(columns=["minute", "team"])
    h_led3, a_led3, h_2up3, a_2up3 = derive_up_goal_states(g3)
    assert (h_led3, a_led3, h_2up3, a_2up3) == (False, False, False, False)

    df = pd.DataFrame({
        "home_goals": [2, 1, 0],
        "away_goals": [2, 0, 0],
        "home_led_ever": [h_led1, h_led2, h_led3],
        "away_led_ever": [a_led1, a_led2, a_led3],
        "home_2up_ever": [h_2up1, h_2up2, h_2up3],
        "away_2up_ever": [a_2up1, a_2up2, a_2up3],
    })
    out = add_up_actuals(df)
    assert out["actual_dc1up_1x"].tolist() == [1, 1, 1]
    assert out["actual_dc1up_x2"].tolist() == [1, 0, 1]
    assert out["actual_dc1up_12"].tolist() == [1, 1, 0]
    assert out["actual_home_2up"].tolist() == [1, 1, 0]
    assert out["actual_away_2up"].tolist() == [0, 0, 0]
