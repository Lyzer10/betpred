"""Walk forward tuning, evaluation, prediction export, and Stage 2 report."""
from __future__ import annotations

from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.special import xlogy

from .baselines import metrics
from .dixon_coles import fit_dixon_coles, promoted_team_values, training_window
from .elo import outcome_probabilities
from .leagues import get_league, paths

ENGINE_DIR = Path(__file__).resolve().parents[1]
MATCHES_PATH = ENGINE_DIR / "data" / "processed" / "matches.parquet"
PREDICTIONS_PATH = ENGINE_DIR / "data" / "processed" / "predictions_dc.parquet"
REPORT_PATH = ENGINE_DIR / "reports" / "stage2_report.md"
VALIDATION_SEASONS = ["2021/22", "2022/23", "2023/24"]
TEST_SEASONS = ["2024/25", "2025/26", "2026/27"]
XI_VALUES = [0.0010, 0.0019, 0.0030, 0.0050]


def assert_no_leakage(training: pd.DataFrame, prediction_date: pd.Timestamp) -> None:
    if not training.empty and not training.date.max() < prediction_date:
        raise AssertionError(f"Training date {training.date.max()} is not before {prediction_date}")


def _promoted_initialization(data: pd.DataFrame, day_matches: pd.DataFrame, training: pd.DataFrame, warm_model):
    prediction_teams = set(day_matches.home_team) | set(day_matches.away_team)
    unseen = sorted(prediction_teams - (set(training.home_team) | set(training.away_team)))
    if not unseen:
        return {}
    year = int(day_matches.season.iloc[0][:4])
    current = set(data.loc[data.season == f"{year}/{str(year + 1)[-2:]}", "home_team"]) | set(data.loc[data.season == f"{year}/{str(year + 1)[-2:]}", "away_team"])
    previous_label = f"{year - 1}/{str(year)[-2:]}"
    previous = set(data.loc[data.season == previous_label, "home_team"]) | set(data.loc[data.season == previous_label, "away_team"])
    if warm_model is None:
        return {}
    return promoted_team_values(unseen, sorted(previous - current), warm_model.attack_map, warm_model.defence_map)


def walk_forward(
    data: pd.DataFrame,
    seasons: list[str],
    xi: float,
    variant: str,
    blend_weight: float = 0.5,
) -> pd.DataFrame:
    """Refit before each unique kickoff time and predict every match at that time."""
    target = data[data.season.isin(seasons)].sort_values(["date", "match_id"]).copy()
    target["_prediction_day"] = target.date.dt.normalize()
    warm_model = None
    rows = []
    for prediction_date, day_matches in target.groupby("_prediction_day", sort=True):
        training = training_window(data, prediction_date)
        assert_no_leakage(training, prediction_date)
        prediction_teams = sorted(set(day_matches.home_team) | set(day_matches.away_team))
        unseen = set(prediction_teams) - (set(training.home_team) | set(training.away_team))
        initialization_model = warm_model
        if unseen and initialization_model is None:
            initialization_model = fit_dixon_coles(training, prediction_date, xi=xi, variant=variant,
                                                    blend_weight=blend_weight)
        initialization = _promoted_initialization(data, day_matches, training, initialization_model)
        model = fit_dixon_coles(training, prediction_date, xi=xi, variant=variant,
                                blend_weight=blend_weight, warm_start=warm_model,
                                prediction_teams=prediction_teams, promoted_values=initialization)
        training_max = training.date.max()
        for match in day_matches.itertuples(index=False):
            _, prediction = model.predict(match.home_team, match.away_team)
            rows.append({"match_id": match.match_id, "date": match.date, "variant": variant,
                         "split": "validation" if match.season in VALIDATION_SEASONS else "test",
                         "prediction_date": prediction_date, "training_max_date": training_max, **prediction})
        warm_model = model
    return pd.DataFrame(rows)


def _actual_outcomes(matches: pd.DataFrame) -> np.ndarray:
    return np.select([matches.home_goals > matches.away_goals, matches.home_goals == matches.away_goals], [0, 1], default=2).astype(int)


def _log_loss_1x2(predictions: pd.DataFrame, matches: pd.DataFrame) -> float:
    joined = predictions.merge(matches[["match_id", "home_goals", "away_goals"]], on="match_id", validate="one_to_one")
    probabilities = joined[["prob_home", "prob_draw", "prob_away"]].to_numpy(float)
    actual = _actual_outcomes(joined)
    return metrics(probabilities, actual)[1]


def tune(data: pd.DataFrame) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    candidates = [("goals", None), ("xg", None)] + [("blend", weight) for weight in (0.3, 0.5, 0.7)]
    records = []
    for variant, weight in candidates:
        for xi in XI_VALUES:
            started = time.perf_counter()
            predictions = walk_forward(data, VALIDATION_SEASONS, xi, variant, weight or 0.5)
            loss = _log_loss_1x2(predictions, data)
            records.append({"variant": variant, "blend_weight": weight, "xi": xi,
                            "validation_log_loss": loss, "seconds": time.perf_counter() - started})
            print(f"Tuned {variant} w={weight} xi={xi:.4f}: log loss={loss:.5f}")
    results = pd.DataFrame(records)
    chosen = {}
    for variant in ("goals", "xg", "blend"):
        best = results[results.variant == variant].sort_values("validation_log_loss").iloc[0]
        chosen[variant] = {"xi": float(best.xi), "blend_weight": float(best.blend_weight) if pd.notna(best.blend_weight) else 0.5,
                           "validation_log_loss": float(best.validation_log_loss)}
    return chosen, results


def _binary_metrics(probability, actual):
    probability = np.clip(np.asarray(probability, float), 1e-15, 1 - 1e-15)
    actual = np.asarray(actual, int)
    loss = float(-(xlogy(actual, probability) + xlogy(1 - actual, 1 - probability)).mean())
    return loss, float(np.mean((probability - actual) ** 2))


def _normalized_odds(frame: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, np.ndarray]:
    valid = (frame[columns].notna() & frame[columns].gt(0)).all(axis=1).to_numpy()
    inverse = 1 / frame.loc[valid, columns].to_numpy(float)
    return inverse / inverse.sum(axis=1, keepdims=True), valid


def _calibration_table(probability: pd.Series, actual: pd.Series) -> list[str]:
    bins = pd.cut(probability, bins=np.linspace(0, 1, 11), include_lowest=True, labels=False)
    table = pd.DataFrame({"probability": probability, "actual": actual, "bin": bins}).groupby("bin", observed=False).agg(
        mean_predicted=("probability", "mean"), actual_rate=("actual", "mean"), count=("actual", "size"))
    lines = ["| Bin | Mean predicted | Actual rate | Count |", "|---|---:|---:|---:|"]
    for i in range(10):
        row = table.loc[i] if i in table.index else None
        lines.append(f"| {i / 10:.1f} to {(i + 1) / 10:.1f} | " +
                     (f"{row.mean_predicted:.3f} | {row.actual_rate:.3f} | {int(row['count'])} |" if row is not None else "NA | NA | 0 |"))
    return lines


def _value_rows(frame: pd.DataFrame, probability_columns: list[str], odds_columns: list[str],
                close_columns: list[str], outcomes: list[np.ndarray], label: str) -> list[str]:
    rows = []
    for probability_column, odds_column, close_column, actual in zip(probability_columns, odds_columns, close_columns, outcomes):
        valid = frame[[probability_column, odds_column, close_column]].notna().all(axis=1).to_numpy()
        bet = valid & (frame[probability_column].to_numpy() * frame[odds_column].to_numpy() > 1.05)
        count = int(bet.sum())
        if count:
            won = np.asarray(actual)[bet]
            profit = np.where(won, frame[odds_column].to_numpy()[bet] - 1, -1).sum()
            clv = (frame[odds_column].to_numpy()[bet] > frame[close_column].to_numpy()[bet]).mean()
            rows.append(f"| {label} {probability_column.removeprefix('prob_')} | {count} | {won.mean():.2%} | {profit / count:.2%} | {clv:.2%} |")
    return rows


def write_report(data: pd.DataFrame, predictions: pd.DataFrame, chosen: dict[str, dict[str, float]], report_path=REPORT_PATH) -> Path:
    test_matches = data[data.season.isin(TEST_SEASONS)].copy()
    actual_1x2 = _actual_outcomes(test_matches)
    result_rows = []
    for name, columns in (("Bookmaker opening", ["odds_home", "odds_draw", "odds_away"]),
                          ("Bookmaker closing", ["close_odds_home", "close_odds_draw", "close_odds_away"])):
        probs, valid = _normalized_odds(test_matches, columns)
        result_rows.append((name, *metrics(probs, actual_1x2[valid])))
    elo_probs = np.array([outcome_probabilities(h, a) for h, a in zip(test_matches.elo_home, test_matches.elo_away)])
    result_rows.append(("Elo", *metrics(elo_probs, actual_1x2)))
    joined_variants = {}
    for variant, label in (("goals", "DC goals"), ("xg", "DC xG"), ("blend", "DC best blend")):
        pred = predictions[(predictions.split == "test") & (predictions.variant == variant)]
        joined = test_matches.merge(pred, on=["match_id", "date"], validate="one_to_one")
        joined_variants[variant] = joined
        result_rows.append((label, *metrics(joined[["prob_home", "prob_draw", "prob_away"]].to_numpy(), _actual_outcomes(joined))))
    best_variant = min(chosen, key=lambda key: chosen[key]["validation_log_loss"])
    best = joined_variants[best_variant]
    total = best.home_goals + best.away_goals

    lines = ["# Stage 2 report", "", f"Test seasons: {', '.join(TEST_SEASONS)} ({len(test_matches):,} matches).",
             "2014/15 is used only as model history and is excluded from evaluation.", "", "## Chosen validation settings", "",
             "| Variant | Xi | Blend weight | Validation 1X2 log loss |", "|---|---:|---:|---:|"]
    for variant in ("goals", "xg", "blend"):
        setting = chosen[variant]
        weight = f"{setting['blend_weight']:.1f}" if variant == "blend" else "NA"
        lines.append(f"| {variant} | {setting['xi']:.4f} | {weight} | {setting['validation_log_loss']:.4f} |")
    lines += ["", "## 1X2", "", "| Method | Accuracy | Log loss | Brier score |", "|---|---:|---:|---:|"]
    lines += [f"| {name} | {accuracy:.2%} | {loss:.4f} | {brier:.4f} |" for name, accuracy, loss, brier in result_rows]

    lines += ["", "## Goal markets", "", "| Method | Market | Log loss | Brier score |", "|---|---|---:|---:|"]
    actual_markets = {**{f"over {line}": (total > line).astype(int) for line in (0.5, 1.5, 2.5, 3.5)},
                      "BTTS": ((best.home_goals > 0) & (best.away_goals > 0)).astype(int)}
    for variant, joined in joined_variants.items():
        variant_total = joined.home_goals + joined.away_goals
        for market, probability_column, actual in [
            ("over 0.5", "prob_over05", variant_total > 0.5), ("over 1.5", "prob_over15", variant_total > 1.5),
            ("over 2.5", "prob_over25", variant_total > 2.5), ("over 3.5", "prob_over35", variant_total > 3.5),
            ("BTTS", "prob_btts", (joined.home_goals > 0) & (joined.away_goals > 0))]:
            loss, brier = _binary_metrics(joined[probability_column], actual)
            lines.append(f"| DC {variant} | {market} | {loss:.4f} | {brier:.4f} |")
    for name, over_col, under_col in (("Bookmaker opening", "odds_over25", "odds_under25"),
                                      ("Bookmaker closing", "close_odds_over25", "close_odds_under25")):
        probs, valid = _normalized_odds(test_matches, [over_col, under_col])
        loss, brier = _binary_metrics(probs[:, 0], (test_matches.home_goals + test_matches.away_goals).to_numpy()[valid] > 2.5)
        lines.append(f"| {name} | over 2.5 | {loss:.4f} | {brier:.4f} |")

    lines += ["", f"## Calibration, best variant: {best_variant}", ""]
    calibration = [("Home win", best.prob_home, best.home_goals > best.away_goals),
                   ("Away win", best.prob_away, best.home_goals < best.away_goals),
                   ("Over 1.5", best.prob_over15, total > 1.5), ("Over 2.5", best.prob_over25, total > 2.5),
                   ("BTTS", best.prob_btts, (best.home_goals > 0) & (best.away_goals > 0))]
    for name, probability, actual in calibration:
        lines += [f"### {name}", "", *_calibration_table(probability, actual), ""]

    confidence_markets = [("Home win", "prob_home", best.home_goals > best.away_goals),
                          ("Away win", "prob_away", best.home_goals < best.away_goals),
                          ("Over 0.5", "prob_over05", total > 0.5), ("Over 1.5", "prob_over15", total > 1.5),
                          ("Over 2.5", "prob_over25", total > 2.5),
                          ("BTTS yes", "prob_btts", (best.home_goals > 0) & (best.away_goals > 0)),
                          ("Home clean sheet", "prob_home_clean_sheet", best.away_goals == 0),
                          ("Away clean sheet", "prob_away_clean_sheet", best.home_goals == 0)]
    lines += ["## Confidence buckets", "", "| Market | Threshold | Hit rate | Count |", "|---|---:|---:|---:|"]
    for name, probability_column, actual in confidence_markets:
        for threshold in (0.70, 0.75, 0.80, 0.85, 0.90):
            selected = best[probability_column] >= threshold
            hit = float(np.asarray(actual)[selected].mean()) if selected.any() else np.nan
            lines.append(f"| {name} | {threshold:.2f} | {hit:.2%} | {int(selected.sum())} |" if selected.any()
                         else f"| {name} | {threshold:.2f} | NA | 0 |")

    outcomes_1x2 = [best.home_goals > best.away_goals, best.home_goals == best.away_goals, best.home_goals < best.away_goals]
    value_rows = _value_rows(best, ["prob_home", "prob_draw", "prob_away"],
                             ["odds_home", "odds_draw", "odds_away"],
                             ["close_odds_home", "close_odds_draw", "close_odds_away"], outcomes_1x2, "1X2")
    value_rows += _value_rows(best, ["prob_over25", "prob_under25"], ["odds_over25", "odds_under25"],
                              ["close_odds_over25", "close_odds_under25"], [total > 2.5, total < 2.5], "Goals")
    lines += ["", "## Value test", "", "One unit is staked when model probability multiplied by opening odds exceeds 1.05.", "",
              "| Bet | Bets | Hit rate | ROI | Positive closing line value |", "|---|---:|---:|---:|---:|", *value_rows, ""]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="EPL")
    selected = get_league(parser.parse_args().league)
    league_paths = paths(selected)
    data = pd.read_parquet(league_paths.matches).sort_values(["date", "match_id"]).reset_index(drop=True)
    evaluation = VALIDATION_SEASONS + TEST_SEASONS
    if set(evaluation) - set(data.season):
        raise ValueError("Required validation or test seasons are missing")
    chosen, tuning_results = tune(data)
    print("Chosen settings:", chosen)
    predictions = []
    for variant in ("goals", "xg", "blend"):
        setting = chosen[variant]
        predictions.append(walk_forward(data, evaluation, setting["xi"], variant, setting["blend_weight"]))
    output = pd.concat(predictions, ignore_index=True)
    output["prob_under25"] = 1 - output["prob_over25"]
    if not (output.training_max_date < output.prediction_date).all():
        raise AssertionError("Walk forward leakage detected")
    league_paths.predictions_dc.parent.mkdir(parents=True, exist_ok=True)
    output.to_parquet(league_paths.predictions_dc, index=False)
    report = write_report(data, output, chosen, league_paths.stage2_report)
    tuning_results.to_csv(league_paths.reports_dir / "stage2_tuning.csv", index=False)
    print(f"Wrote {len(output):,} predictions to {league_paths.predictions_dc}")
    print(f"Wrote {report}")


if __name__ == "__main__":
    main()
