from pathlib import Path

import pandas as pd
import pytest

MATCHES = Path(__file__).resolve().parents[1] / "data" / "processed" / "matches.parquet"


@pytest.fixture(scope="module")
def matches():
    if not MATCHES.exists():
        pytest.skip("matches.parquet not built")
    return pd.read_parquet(MATCHES)


def test_opening_odds_are_complete(matches):
    cols = ["odds_home", "odds_draw", "odds_away", "odds_over25", "odds_under25"]
    assert matches[cols].isna().any(axis=1).mean() < 0.02


def test_closing_1x2_odds_are_complete(matches):
    cols = ["close_odds_home", "close_odds_draw", "close_odds_away"]
    assert matches[cols].isna().any(axis=1).mean() < 0.02


def test_odds_are_valid_decimal_prices(matches):
    cols = [c for c in matches.columns if "odds" in c]
    assert (matches[cols].dropna(how="all").stack() > 1.0).all()
