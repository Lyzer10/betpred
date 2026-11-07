"""Synthetic known-answer tests for Task 20 (src/timing_half_markets_study.py)."""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
from scipy.stats import skellam

from src.timing_half_markets_study import (
    HALF_MARKETS,
    TIMING_MARKETS,
    build_walkforward_half_legs,
    build_walkforward_timing_legs,
    derive_timing_outcomes_from_goals,
    half_team_outcomes,
    half_team_raw_probabilities,
    timing_market_raw_probabilities,
)


def test_fixed_lambdas_exact_known_answers() -> None:
    lam_h = 1.6
    lam_a = 1.2
    s = 0.45
    w = 0.09

    t_raw = timing_market_raw_probabilities(lam_h, lam_a, w)
    h_raw = half_team_raw_probabilities(lam_h, lam_a, s)

    # 1. First goal exact formulas: lambda_i / (lambda_h + lambda_a) * (1 - exp(-(lambda_h + lambda_a)))
    p_no_goal = math.exp(-(lam_h + lam_a))
    exp_fg_h = (lam_h / (lam_h + lam_a)) * (1.0 - p_no_goal)
    exp_fg_a = (lam_a / (lam_h + lam_a)) * (1.0 - p_no_goal)
    assert math.isclose(t_raw["first_goal_home"], exp_fg_h, rel_tol=1e-12)
    assert math.isclose(t_raw["first_goal_away"], exp_fg_a, rel_tol=1e-12)
    assert math.isclose(t_raw["first_goal_home"] + t_raw["first_goal_away"] + p_no_goal, 1.0, abs_tol=1e-12)

    # 2. 10-minute interval 1X2 matches exact Skellam distribution for X - Y with X ~ Pois(w*lam_h), Y ~ Pois(w*lam_a)
    mu1 = w * lam_h
    mu2 = w * lam_a
    assert math.isclose(t_raw["interval_10_home"], float(1.0 - skellam.cdf(0, mu1, mu2)), abs_tol=1e-10)
    assert math.isclose(t_raw["interval_10_draw"], float(skellam.pmf(0, mu1, mu2)), abs_tol=1e-10)
    assert math.isclose(t_raw["interval_10_away"], float(skellam.cdf(-1, mu1, mu2)), abs_tol=1e-10)
    assert math.isclose(
        t_raw["interval_10_home"] + t_raw["interval_10_draw"] + t_raw["interval_10_away"],
        1.0,
        abs_tol=1e-10,
    )

    # 3. Team half totals and both-halves markets match closed-form independent Poisson formulas
    p_h_fh = 1.0 - math.exp(-s * lam_h)
    p_a_fh = 1.0 - math.exp(-s * lam_a)
    p_h_sh = 1.0 - math.exp(-(1.0 - s) * lam_h)
    p_a_sh = 1.0 - math.exp(-(1.0 - s) * lam_a)
    assert math.isclose(h_raw["home_fh_over_0.5"], p_h_fh, rel_tol=1e-12)
    assert math.isclose(h_raw["away_fh_over_0.5"], p_a_fh, rel_tol=1e-12)
    assert math.isclose(h_raw["home_sh_over_0.5"], p_h_sh, rel_tol=1e-12)
    assert math.isclose(h_raw["away_sh_over_0.5"], p_a_sh, rel_tol=1e-12)
    assert math.isclose(h_raw["home_score_both_halves"], p_h_fh * p_h_sh, rel_tol=1e-12)
    assert math.isclose(h_raw["away_score_both_halves"], p_a_fh * p_a_sh, rel_tol=1e-12)

    p_h_win_fh = float(1.0 - skellam.cdf(0, s * lam_h, s * lam_a))
    p_h_win_sh = float(1.0 - skellam.cdf(0, (1.0 - s) * lam_h, (1.0 - s) * lam_a))
    p_a_win_fh = float(1.0 - skellam.cdf(0, s * lam_a, s * lam_h))
    p_a_win_sh = float(1.0 - skellam.cdf(0, (1.0 - s) * lam_a, (1.0 - s) * lam_h))
    assert math.isclose(h_raw["home_win_both_halves"], p_h_win_fh * p_h_win_sh, abs_tol=1e-10)
    assert math.isclose(h_raw["away_win_both_halves"], p_a_win_fh * p_a_win_sh, abs_tol=1e-10)


def test_simulated_league_known_answer_and_no_leakage() -> None:
    rng = np.random.default_rng(20261029)
    lam_h = 1.5
    lam_a = 1.1
    true_s = 0.44
    true_w = 0.10
    seasons = ["2020/21", "2021/22", "2022/23", "2023/24"]
    n_per_season = 500

    rows = []
    for s_idx, season in enumerate(seasons):
        fh_h = rng.poisson(true_s * lam_h, size=n_per_season)
        fh_a = rng.poisson(true_s * lam_a, size=n_per_season)
        sh_h = rng.poisson((1.0 - true_s) * lam_h, size=n_per_season)
        sh_a = rng.poisson((1.0 - true_s) * lam_a, size=n_per_season)

        g10_h = rng.poisson(true_w * lam_h, size=n_per_season)
        g10_a = rng.poisson(true_w * lam_a, size=n_per_season)
        g_rest_h = rng.poisson((1.0 - true_w) * lam_h, size=n_per_season)
        g_rest_a = rng.poisson((1.0 - true_w) * lam_a, size=n_per_season)

        for i in range(n_per_season):
            fthg = int(fh_h[i] + sh_h[i])
            ftag = int(fh_a[i] + sh_a[i])
            tot_w = int(g10_h[i] + g10_a[i] + g_rest_h[i] + g_rest_a[i])
            if tot_w == 0:
                fg_h = 0
                fg_a = 0
            else:
                fg_h = int(rng.random() < (lam_h / (lam_h + lam_a)))
                fg_a = 1 - fg_h
            rows.append(
                {
                    "date": pd.Timestamp("2020-08-01") + pd.to_timedelta(int(s_idx * 400 + i), unit="D"),
                    "season": season,
                    "lam_home": lam_h,
                    "lam_away": lam_a,
                    "home_goals": fthg,
                    "away_goals": ftag,
                    "ht_home_goals": int(fh_h[i]),
                    "ht_away_goals": int(fh_a[i]),
                    "goals_10": int(g10_h[i] + g10_a[i]),
                    "first_goal_home": fg_h,
                    "first_goal_away": fg_a,
                    "interval_10_home": int(g10_h[i] > g10_a[i]),
                    "interval_10_draw": int(g10_h[i] == g10_a[i]),
                    "interval_10_away": int(g10_a[i] > g10_h[i]),
                }
            )
    sim_df = pd.DataFrame(rows)

    half_legs, shares_fh = build_walkforward_half_legs(sim_df, "SIM", rho=0.0)
    timing_legs, shares_10 = build_walkforward_timing_legs(sim_df, "SIM", rho=0.0)

    # First season has no earlier seasons; shares are defined for seasons[1:]
    assert set(shares_fh.keys()) == {"2021/22", "2022/23", "2023/24"}
    assert set(shares_10.keys()) == {"2021/22", "2022/23", "2023/24"}
    for s_val in shares_fh.values():
        assert abs(s_val - true_s) < 0.025
    for w_val in shares_10.values():
        assert abs(w_val - true_w) < 0.015

    # Check empirical win rates match raw probabilities closely on the simulated data
    for mkt in HALF_MARKETS:
        sub = half_legs[half_legs["market"] == mkt]
        assert abs(sub["won"].mean() - sub["bookmaker_probability"].mean()) < 0.035
    for mkt in TIMING_MARKETS:
        sub = timing_legs[timing_legs["market"] == mkt]
        assert abs(sub["won"].mean() - sub["bookmaker_probability"].mean()) < 0.035

    # Verify walk-forward calibration only populates seasons from 2022/23 onwards (since 2021/22 is first raw season)
    assert half_legs[half_legs["season"] == "2021/22"]["probability"].isna().all()
    assert half_legs[half_legs["season"].isin(["2022/23", "2023/24"])]["probability"].notna().all()


def test_derive_timing_outcomes_from_goals_and_half_outcomes() -> None:
    goals = pd.DataFrame(
        {
            "minute": [46, 9, 10],
            "team": ["home", "away", "home"],
        }
    )
    out = derive_timing_outcomes_from_goals(goals)
    assert out is not None
    assert out["first_goal_home"] == 0
    assert out["first_goal_away"] == 1
    assert out["interval_10_home"] == 0
    assert out["interval_10_draw"] == 0
    assert out["interval_10_away"] == 1
    assert out["goals_10"] == 1

    # Tied earliest minute between home and away returns None
    tied = pd.DataFrame({"minute": [12, 12], "team": ["home", "away"]})
    assert derive_timing_outcomes_from_goals(tied) is None

    # Half outcomes: FTHG=3, FTAG=1, HTHG=1, HTAG=0 -> SH is 2-1
    ho = half_team_outcomes(3, 1, 1, 0)
    assert ho["home_score_both_halves"] == 1
    assert ho["away_score_both_halves"] == 0
    assert ho["home_win_both_halves"] == 1
    assert ho["away_win_both_halves"] == 0
    assert ho["home_fh_over_0.5"] == 1
    assert ho["away_fh_over_0.5"] == 0
    assert ho["home_sh_over_0.5"] == 1
    assert ho["away_sh_over_0.5"] == 1
