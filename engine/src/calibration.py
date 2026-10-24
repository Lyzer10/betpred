"""Leakage safe seasonal probability calibration for Stage 3."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit, xlogy
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from .leagues import get_league, paths

ENGINE_DIR = Path(__file__).resolve().parents[1]
MATCHES_PATH = ENGINE_DIR / "data" / "processed" / "matches.parquet"
DC_PATH = ENGINE_DIR / "data" / "processed" / "predictions_dc.parquet"
OUTPUT_PATH = ENGINE_DIR / "data" / "processed" / "predictions_calibrated.parquet"
METHODS_PATH = ENGINE_DIR / "data" / "processed" / "calibration_methods.json"
TEST_SEASONS = ["2024/25", "2025/26", "2026/27"]

MARKETS = {
    "home": ("prob_home", "actual_home"),
    "draw": ("prob_draw", "actual_draw"),
    "away": ("prob_away", "actual_away"),
    "over05": ("prob_over05", "actual_over05"),
    "over15": ("prob_over15", "actual_over15"),
    "over25": ("prob_over25", "actual_over25"),
    "over35": ("prob_over35", "actual_over35"),
    "btts": ("prob_btts", "actual_btts"),
    "home_clean_sheet": ("prob_home_clean_sheet", "actual_home_clean_sheet"),
    "away_clean_sheet": ("prob_away_clean_sheet", "actual_away_clean_sheet"),
}


def binary_metrics(probability, actual) -> tuple[float, float]:
    probability = np.clip(np.asarray(probability, float), 1e-12, 1 - 1e-12)
    actual = np.asarray(actual, int)
    loss = float(-(xlogy(actual, probability) + xlogy(1 - actual, 1 - probability)).mean())
    return loss, float(np.mean((probability - actual) ** 2))


@dataclass
class ProbabilityCalibrator:
    method: str
    model: object
    constant: float | None = None

    def predict(self, probability) -> np.ndarray:
        values = np.clip(np.asarray(probability, float), 1e-6, 1 - 1e-6)
        if self.constant is not None:
            return np.full(values.shape, self.constant)
        if self.method == "platt":
            return self.model.predict_proba(logit(values).reshape(-1, 1))[:, 1]
        return np.asarray(self.model.predict(values), float)


def fit_calibrator(probability, actual, method: str) -> ProbabilityCalibrator:
    probability = np.clip(np.asarray(probability, float), 1e-6, 1 - 1e-6)
    actual = np.asarray(actual, int)
    if len(np.unique(actual)) < 2:
        return ProbabilityCalibrator(method, None, float(actual.mean()))
    if method == "platt":
        model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        model.fit(logit(probability).reshape(-1, 1), actual)
    elif method == "isotonic":
        model = IsotonicRegression(out_of_bounds="clip").fit(probability, actual)
    else:
        raise ValueError(f"Unknown calibration method: {method}")
    return ProbabilityCalibrator(method, model)


def add_actuals(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    total = result.home_goals + result.away_goals
    result["actual_home"] = (result.home_goals > result.away_goals).astype(int)
    result["actual_draw"] = (result.home_goals == result.away_goals).astype(int)
    result["actual_away"] = (result.home_goals < result.away_goals).astype(int)
    result["actual_dc_1x"] = (result.home_goals >= result.away_goals).astype(int)
    result["actual_dc_x2"] = (result.home_goals <= result.away_goals).astype(int)
    result["actual_dc_12"] = (result.home_goals != result.away_goals).astype(int)
    for line, suffix in ((0.5, "05"), (1.5, "15"), (2.5, "25"), (3.5, "35")):
        result[f"actual_over{suffix}"] = (total > line).astype(int)
    result["actual_btts"] = ((result.home_goals > 0) & (result.away_goals > 0)).astype(int)
    result["actual_home_clean_sheet"] = (result.away_goals == 0).astype(int)
    result["actual_away_clean_sheet"] = (result.home_goals == 0).astype(int)
    result["actual_home_first"] = (result.first_scorer == "home").astype(int)
    result["actual_away_first"] = (result.first_scorer == "away").astype(int)
    result["actual_no_goal"] = (result.first_scorer == "none").astype(int)
    result["actual_home_1up"] = result.home_led_at_any_point.astype(int)
    result["actual_away_1up"] = result.away_led_at_any_point.astype(int)
    return result


def enforce_probability_constraints(frame: pd.DataFrame, prefix: str) -> None:
    result_columns = [f"{prefix}_home", f"{prefix}_draw", f"{prefix}_away"]
    values = frame[result_columns].to_numpy(float)
    frame[result_columns] = values / values.sum(axis=1, keepdims=True)
    over_columns = [f"{prefix}_over05", f"{prefix}_over15", f"{prefix}_over25", f"{prefix}_over35"]
    frame[over_columns] = np.minimum.accumulate(frame[over_columns].to_numpy(float), axis=1)


def walk_forward_calibration(
    source: pd.DataFrame,
    markets: dict[str, tuple[str, str]],
    seasons: list[str] = TEST_SEASONS,
) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    """Calibrate each season using only rows strictly before that season."""
    outputs = []
    audit: dict[str, dict[str, float]] = {}
    for season in seasons:
        fold = source[source.season == season].copy()
        first_date = fold.date.min()
        training = source[source.date < first_date]
        if training.empty:
            raise ValueError(f"No calibration history before {season}")
        for market, (raw_column, actual_column) in markets.items():
            for method in ("platt", "isotonic"):
                calibrator = fit_calibrator(training[raw_column], training[actual_column], method)
                fold[f"{method}_{market}"] = calibrator.predict(fold[raw_column])
            audit[f"{season}:{market}"] = {
                "training_max_date": training.date.max().isoformat(),
                "first_prediction_date": first_date.isoformat(),
            }
        enforce_probability_constraints(fold, "platt") if {"home", "draw", "away", "over05", "over15", "over25", "over35"}.issubset(markets) else None
        enforce_probability_constraints(fold, "isotonic") if {"home", "draw", "away", "over05", "over15", "over25", "over35"}.issubset(markets) else None
        outputs.append(fold)
    return pd.concat(outputs, ignore_index=True), audit


def choose_methods(calibrated: pd.DataFrame, markets: dict[str, tuple[str, str]], tolerance: float = 0.001):
    chosen, scores = {}, {}
    for market, (_, actual_column) in markets.items():
        platt = binary_metrics(calibrated[f"platt_{market}"], calibrated[actual_column])
        isotonic = binary_metrics(calibrated[f"isotonic_{market}"], calibrated[actual_column])
        method = "platt" if platt[0] <= isotonic[0] + tolerance else "isotonic"
        chosen[market] = method
        scores[market] = {"platt_log_loss": platt[0], "platt_brier": platt[1],
                          "isotonic_log_loss": isotonic[0], "isotonic_brier": isotonic[1]}
        calibrated[f"cal_{market}"] = calibrated[f"{method}_{market}"]
    if {"home", "draw", "away", "over05", "over15", "over25", "over35"}.issubset(markets):
        enforce_probability_constraints(calibrated, "cal")
    return chosen, scores


def build_calibrated_predictions(league="EPL") -> tuple[pd.DataFrame, dict, dict]:
    league_paths = paths(get_league(league))
    matches = pd.read_parquet(league_paths.matches)
    predictions = pd.read_parquet(league_paths.predictions_dc)
    predictions = predictions[predictions.variant.isin(["blend", "xg"])]
    source = add_actuals(predictions.merge(matches, on=["match_id", "date"], validate="many_to_one"))
    calibrated_parts, all_audits, all_methods, all_scores = [], {}, {}, {}
    for variant in ("blend", "xg"):
        variant_source = source[source.variant == variant].copy()
        calibrated, audit = walk_forward_calibration(variant_source, MARKETS)
        methods, scores = choose_methods(calibrated, MARKETS)
        calibrated_parts.append(calibrated)
        all_audits[variant], all_methods[variant], all_scores[variant] = audit, methods, scores
    output = pd.concat(calibrated_parts, ignore_index=True)
    keep = [column for column in output.columns if column in predictions.columns or column.startswith(("platt_", "isotonic_", "cal_"))]
    league_paths.predictions_calibrated.parent.mkdir(parents=True, exist_ok=True)
    output[keep].to_parquet(league_paths.predictions_calibrated, index=False)
    league_paths.calibration_methods.write_text(json.dumps({"methods": all_methods, "scores": all_scores, "audit": all_audits}, indent=2), encoding="utf-8")
    return output, all_methods, all_scores


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="EPL")
    args = parser.parse_args()
    league_paths = paths(get_league(args.league))
    output, methods, _ = build_calibrated_predictions(args.league)
    print(f"Wrote {len(output):,} calibrated rows to {league_paths.predictions_calibrated}")
    print("Chosen methods:", methods)


if __name__ == "__main__":
    main()

