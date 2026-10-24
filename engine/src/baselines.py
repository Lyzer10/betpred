"""Evaluate bookmaker and Elo baselines on the last three seasons."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import xlogy

from .elo import outcome_probabilities
from .leagues import get_league, paths

ENGINE_DIR = Path(__file__).resolve().parents[1]


def metrics(probabilities: np.ndarray, actual: np.ndarray) -> tuple[float, float, float]:
    chosen = probabilities.argmax(axis=1)
    accuracy = float((chosen == actual).mean())
    one_hot = np.eye(3)[actual]
    clipped = np.clip(probabilities, 1e-15, 1)
    log_loss = float(-xlogy(one_hot, clipped).sum(axis=1).mean())
    brier = float(((probabilities - one_hot) ** 2).sum(axis=1).mean())
    return accuracy, log_loss, brier


def generate_report(matches_path: Path | None = None, league="EPL") -> Path:
    selected = get_league(league)
    league_paths = paths(selected)
    matches_path = matches_path or league_paths.matches
    data = pd.read_parquet(matches_path).sort_values("date")
    complete = data[data["home_goals"].notna() & data["away_goals"].notna()].copy()
    seasons = complete["season"].drop_duplicates().tolist()[-3:]
    test = complete[complete["season"].isin(seasons)].copy()
    actual = np.select([test.home_goals > test.away_goals, test.home_goals == test.away_goals], [0, 1], default=2).astype(int)

    odds_ok = test[["odds_home", "odds_draw", "odds_away"]].notna().all(axis=1)
    inverse = 1 / test.loc[odds_ok, ["odds_home", "odds_draw", "odds_away"]].to_numpy(float)
    bookmaker_probs = inverse / inverse.sum(axis=1, keepdims=True)
    bookmaker = metrics(bookmaker_probs, actual[odds_ok.to_numpy()])
    elo_probs = np.array([outcome_probabilities(h, a) for h, a in zip(test.elo_home, test.elo_away)])
    elo = metrics(elo_probs, actual)

    total_goals = test.home_goals + test.away_goals
    over_ok = test[["odds_over25", "odds_under25"]].notna().all(axis=1)
    over_pick = test.loc[over_ok, "odds_over25"] < test.loc[over_ok, "odds_under25"]
    over_actual = total_goals.loc[over_ok] > 2.5
    over_hit = (over_pick == over_actual).mean()
    first_scored = test.first_scorer != "none"
    first_won = ((test.first_scorer == "home") & (test.home_goals > test.away_goals)) | ((test.first_scorer == "away") & (test.away_goals > test.home_goals))

    def pct(value: float) -> str:
        return f"{value * 100:.2f}%"
    lines = ["# Baseline report", "", f"Evaluation seasons: {', '.join(seasons)} ({len(test):,} completed matches).", "",
             "## Result prediction", "", "| Baseline | Accuracy | Log loss | Brier score |", "|---|---:|---:|---:|",
             f"| Bookmaker margin removed | {pct(bookmaker[0])} | {bookmaker[1]:.4f} | {bookmaker[2]:.4f} |",
             f"| Elo | {pct(elo[0])} | {elo[1]:.4f} | {elo[2]:.4f} |", "", "## Market and event rates", "",
             f"* Bookmaker Over 2.5 hit rate: {pct(float(over_hit))}",
             f"* Over 0.5: {pct(float((total_goals > 0.5).mean()))}", f"* Over 1.5: {pct(float((total_goals > 1.5).mean()))}",
             f"* Over 2.5: {pct(float((total_goals > 2.5).mean()))}", f"* Over 3.5: {pct(float((total_goals > 3.5).mean()))}",
             f"* Both teams to score: {pct(float(((test.home_goals > 0) & (test.away_goals > 0)).mean()))}",
             f"* Home 1Up rate: {pct(float(test.home_led_at_any_point.mean()))}",
             f"* Away 1Up rate: {pct(float(test.away_led_at_any_point.mean()))}",
             f"* First scorer wins rate: {pct(float(first_won[first_scored].mean()))}", "",
             "Bookmaker probabilities are normalized inverse decimal odds. The Over 2.5 pick is the lower odds side after comparing Over and Under.", ""]
    report = league_paths.baseline_report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {report}")
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", default="EPL")
    generate_report(league=parser.parse_args().league)
