import pandas as pd
import pytest
from pathlib import Path

from src.backtest import assert_no_leakage
from src.dixon_coles import training_window


def test_every_training_match_is_strictly_before_prediction():
    data = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"])})
    for prediction_date in data.date.unique():
        training = training_window(data, prediction_date)
        assert_no_leakage(training, prediction_date)
        assert training.empty or training.date.max() < prediction_date


def test_same_calendar_day_is_excluded_as_one_prediction_batch():
    data = pd.DataFrame({"date": pd.to_datetime(["2024-01-01 15:00", "2024-01-02 12:00", "2024-01-02 20:00"])})
    prediction_day = pd.Timestamp("2024-01-02")
    training = training_window(data, prediction_day)
    assert training.date.tolist() == [pd.Timestamp("2024-01-01 15:00")]


def test_leakage_assertion_rejects_same_date():
    training = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"])})
    with pytest.raises(AssertionError):
        assert_no_leakage(training, pd.Timestamp("2024-01-02"))


def test_every_saved_prediction_has_strict_training_cutoff():
    path = Path(__file__).resolve().parents[1] / "data" / "processed" / "predictions_dc.parquet"
    if not path.exists():
        pytest.skip("predictions have not been built")
    predictions = pd.read_parquet(path)
    assert (predictions.training_max_date < predictions.prediction_date).all()
