from io import StringIO

import pandas as pd
import pytest

from src.new_leagues_study import CACHE, odds_columns, outcomes


def test_real_downloaded_schema_and_outcomes():
    files = sorted(CACHE.glob("N1_*.csv"))
    if not files:
        pytest.skip("Real research downloads not cached")
    for path in files:
        frame = pd.read_csv(StringIO(path.read_text(encoding="utf-8-sig", errors="replace")))
        assert odds_columns(frame) is not None
        match = frame.dropna(subset=["FTHG", "FTAG"]).iloc[0]
        actual = outcomes(match.FTHG, match.FTAG)
        assert actual["double_1x"] == 1 - actual["away_win"]
        assert actual["double_x2"] == 1 - actual["home_win"]
        assert actual["over_0.5"] >= actual["over_1.5"] >= actual["over_2.5"]
