import numpy as np
import pandas as pd

from src.calibration import enforce_probability_constraints, walk_forward_calibration


def test_calibration_training_dates_are_strictly_before_fold():
    rows = []
    for season, start in (("2023/24", "2023-08-01"), ("2024/25", "2024-08-01"), ("2025/26", "2025-08-01")):
        for i in range(20):
            rows.append({"season": season, "date": pd.Timestamp(start) + pd.Timedelta(i, unit="D"),
                         "prob_home": 0.1 + i * 0.04, "actual_home": i % 2})
    source = pd.DataFrame(rows)
    _, audit = walk_forward_calibration(source, {"home": ("prob_home", "actual_home")}, ["2024/25", "2025/26"])
    for values in audit.values():
        assert pd.Timestamp(values["training_max_date"]) < pd.Timestamp(values["first_prediction_date"])


def test_result_renormalization_and_over_line_monotonicity():
    frame = pd.DataFrame({"cal_home": [0.4], "cal_draw": [0.4], "cal_away": [0.4],
                          "cal_over05": [0.8], "cal_over15": [0.9],
                          "cal_over25": [0.5], "cal_over35": [0.6]})
    enforce_probability_constraints(frame, "cal")
    assert np.isclose(frame[["cal_home", "cal_draw", "cal_away"]].sum(axis=1).iloc[0], 1)
    assert frame[["cal_over05", "cal_over15", "cal_over25", "cal_over35"]].iloc[0].tolist() == [0.8, 0.8, 0.5, 0.5]
