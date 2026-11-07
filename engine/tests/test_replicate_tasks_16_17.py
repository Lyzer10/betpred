"""Tests for Task 21 replication of Tasks 16 and 17 (src/replicate_tasks_16_17.py)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.replicate_tasks_16_17 import REPL_SEASONS, _summarize, walk_forward_t17_seasons
from src.up_markets_study import MARKETS as T17_MARKETS


def test_walk_forward_t17_seasons_uses_only_earlier_seasons() -> None:
    rng = np.random.default_rng(20261029)
    seasons = ["2017/18", "2018/19", "2019/20", "2020/21"]
    rows = []
    for s_idx, season in enumerate(seasons):
        for i in range(60):
            row = {
                "date": pd.Timestamp("2017-08-01") + pd.to_timedelta(int(s_idx * 365 + i), unit="D"),
                "season": season,
                "home_team": f"H{i % 10}",
                "away_team": f"A{(i + 1) % 10}",
            }
            for mkt in T17_MARKETS:
                p = float(rng.uniform(0.35, 0.85))
                row[f"raw_{mkt}"] = p
                row[f"actual_{mkt}"] = int(rng.random() < p)
            rows.append(row)
    df = pd.DataFrame(rows)
    legs = walk_forward_t17_seasons(df, target_seasons=REPL_SEASONS)
    assert set(legs["season"].unique()) == {"2019/20", "2020/21"}
    assert set(legs["market"].unique()) == set(T17_MARKETS)
    assert len(legs) == 2 * 60 * len(T17_MARKETS)
    assert legs["probability"].between(1e-6, 1.0 - 1e-6).all()


def test_summarize_counts_strong_candidates_correctly() -> None:
    sample = [
        {
            "primary_2024_25_plus": {"status": "PASS"},
            "replication_2019_20_to_2023_24": {"status": "PASS"},
            "strong_candidate": True,
        },
        {
            "primary_2024_25_plus": {"status": "PASS"},
            "replication_2019_20_to_2023_24": {"status": "FAIL"},
            "strong_candidate": False,
        },
        {
            "primary_2024_25_plus": {"status": "FAIL"},
            "replication_2019_20_to_2023_24": {"status": "PASS"},
            "strong_candidate": False,
        },
    ]
    s = _summarize(sample)
    assert s == {"total": 3, "p_pass": 2, "p_fail": 1, "r_pass": 2, "r_fail": 1, "strong": 1}
