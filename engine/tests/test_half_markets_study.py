import math
import numpy as np

from src.half_markets_study import half_market_outcomes, half_market_raw_probabilities


def test_synthetic_known_answer_half_probabilities():
    # Hand-computed known answers for lam_home = 1.6, lam_away = 0.8, first-half share s = 0.45.
    lam_h, lam_a, s = 1.6, 0.8, 0.45
    fh_h, fh_a = s * lam_h, s * lam_a                  # 0.72, 0.36; sum = 1.08
    sh_h, sh_a = (1 - s) * lam_h, (1 - s) * lam_a      # 0.88, 0.44; sum = 1.32
    fh_tot, sh_tot = fh_h + fh_a, sh_h + sh_a

    raw = half_market_raw_probabilities(lam_h, lam_a, s)

    assert abs(raw["fh_over_0.5"] - (1 - math.exp(-fh_tot))) < 1e-12
    assert abs(raw["fh_over_1.5"] - (1 - math.exp(-fh_tot) * (1 + fh_tot))) < 1e-12
    assert abs(raw["sh_over_0.5"] - (1 - math.exp(-sh_tot))) < 1e-12
    assert abs(raw["sh_over_1.5"] - (1 - math.exp(-sh_tot) * (1 + sh_tot))) < 1e-12

    # Direct double-sum over independent Poisson grid for P(H > A) in each half
    def hand_win(mu1, mu2):
        total = 0.0
        for h in range(1, 16):
            p_h = math.exp(-mu1) * (mu1 ** h) / math.factorial(h)
            for a in range(h):
                p_a = math.exp(-mu2) * (mu2 ** a) / math.factorial(a)
                total += p_h * p_a
        return total

    p_h_fh, p_h_sh = hand_win(fh_h, fh_a), hand_win(sh_h, sh_a)
    p_a_fh, p_a_sh = hand_win(fh_a, fh_h), hand_win(sh_a, sh_h)
    assert abs(raw["home_win_either_half"] - (1 - (1 - p_h_fh) * (1 - p_h_sh))) < 1e-12
    assert abs(raw["away_win_either_half"] - (1 - (1 - p_a_fh) * (1 - p_a_sh))) < 1e-12


def test_half_market_outcomes_known_cases():
    # 2-1 FT, 1-1 HT -> 1H has 2 goals (draw), 2H is 1-0 home (1 goal, home wins 2H)
    out = half_market_outcomes(2, 1, 1, 1)
    assert out == {
        "fh_over_0.5": 1, "fh_over_1.5": 1,
        "sh_over_0.5": 1, "sh_over_1.5": 0,
        "home_win_either_half": 1, "away_win_either_half": 0,
    }
    # 1-2 FT, 1-0 HT -> 1H is 1-0 home, 2H is 0-2 away -> BOTH teams win a half
    both = half_market_outcomes(1, 2, 1, 0)
    assert both["home_win_either_half"] == 1 and both["away_win_either_half"] == 1
    assert both["fh_over_0.5"] == 1 and both["fh_over_1.5"] == 0
    assert both["sh_over_0.5"] == 1 and both["sh_over_1.5"] == 1

