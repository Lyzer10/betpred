"""Tests for Task 22 SIMULATED Betpawa-price value study (src/simulated_value_study.py)."""

from __future__ import annotations

import math
import numpy as np
import pandas as pd

from src.simulated_value_study import (
    MIN_PRICED_MATCHES,
    SEED,
    bootstrap_mean_by_day_2000,
    compute_price_ratios,
    simulated_return_stats,
)


def test_simulated_return_stats_exact_formula_and_bootstrap() -> None:
    rng = np.random.default_rng(SEED)
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03"]),
            "raw": [0.5, 0.5, 0.5, 0.5],
            "won": [1, 1, 1, 1],
        }
    )
    # With won=1 and raw=0.5, won / (raw * r) - 1 = 2 / r - 1
    res = simulated_return_stats(df, r_value=1.0, rng=rng, n_boot=2000)
    assert math.isclose(res["simulated_return"], 1.0, abs_tol=1e-9)
    assert math.isclose(res["ci_low"], 1.0, abs_tol=1e-9)
    assert math.isclose(res["ci_high"], 1.0, abs_tol=1e-9)
    assert res["ci_low_above_zero"] is True


def test_compute_price_ratios_marks_under_50_insufficient() -> None:
    ko = pd.Timestamp("2026-11-07 15:00:00")
    fixtures = {
        ("TeamA", "TeamB", ko): {
            "home": "TeamA",
            "away": "TeamB",
            "kickoff_utc": "2026-11-07T15:00:00Z",
            "league": {"code": "EPL"},
            "markets": [
                {"market": "home_win", "market_probability": 0.50},
                {"market": "draw", "market_probability": 0.25},
                {"market": "away_win", "market_probability": 0.25},
                {"market": "over_2.5", "market_probability": 0.55},
                {"market": "under_2.5", "market_probability": 0.45},
            ],
        }
    }
    prices = pd.DataFrame(
        [
            {
                "snapshot_utc": pd.Timestamp("2026-11-07 12:00:00"),
                "kickoff_utc": ko,
                "home": "TeamA",
                "away": "TeamB",
                "market": "fh_over_0.5",
                "betpawa_odds": 1.35,
            }
        ]
    )
    summaries = compute_price_ratios(
        prices=prices,
        fixtures_by_key=fixtures,
        share_fh={"EPL": 0.4474},
        share_10={"EPL": 0.0800},
    )
    by_mkt = {s["market"]: s for s in summaries}
    assert by_mkt["fh_over_0.5"]["n"] == 1
    assert by_mkt["fh_over_0.5"]["status"] == "INSUFFICIENT"
    assert by_mkt["fh_over_0.5"]["median"] is not None
    assert MIN_PRICED_MATCHES == 50
