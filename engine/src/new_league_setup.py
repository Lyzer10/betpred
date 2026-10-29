"""Offline setup for the four verified market-only leagues. Never run by the daily workflow."""
import argparse
import json

import numpy as np
from scipy.special import logit
from sklearn.linear_model import LogisticRegression

from .accumulators import bookmaker_implied
from .fetch_results import current_season_start
from .football_only import load_history, season_file
from .leagues import paths
from .market_live import usable
from .new_league_config import NEW_LEAGUES, VALIDATED_MARKETS, FIXED_RHO
from .new_leagues_study import outcomes


def install_gates(target=None):
    from .market_gates import GATES_PATH, new_league_gates
    target = GATES_PATH if target is None else target
    stored = json.loads(target.read_text(encoding="utf-8"))
    stored["gates"].update(new_league_gates())
    target.write_text(json.dumps(stored, indent=1), encoding="utf-8")


def setup(league):
    current = current_season_start()
    history = load_history(league, end=current - 1)
    if history.season.str[:4].astype(int).ge(current).any():
        raise AssertionError("Current-season rows cannot fit calibrators")
    odds = [f"avg_odds_{field}" for field in ("home", "draw", "away", "over25", "under25")]
    history = history[(history[odds].notna() & history[odds].gt(0)).all(axis=1)]
    probabilities, results = {m: [] for m in VALIDATED_MARKETS}, {m: [] for m in VALIDATED_MARKETS}
    for row in history.itertuples():
        fair = bookmaker_implied(*(getattr(row, field) for field in odds), FIXED_RHO)[0]
        actual = outcomes(row.home_goals, row.away_goals)
        for market in VALIDATED_MARKETS:
            probabilities[market].append(fair[market])
            results[market].append(actual[market])
    calibrators = {}
    for market in VALIDATED_MARKETS:
        y = np.asarray(results[market])
        minority = int(min(y.sum(), len(y) - y.sum()))
        if not len(y) or minority < 30:
            continue
        fit = LogisticRegression(C=1.0).fit(logit(np.clip(probabilities[market], 1e-6, 1-1e-6)).reshape(-1, 1), y)
        calibrator = {"coef": float(fit.coef_[0, 0]), "intercept": float(fit.intercept_[0]),
                      "regularization": 1.0, "legs": len(y), "minority": minority}
        if usable(calibrator):
            calibrators[market] = calibrator
    directory = paths(league).processed_dir
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "market_calibrators.json").write_text(json.dumps(calibrators, indent=2), encoding="utf-8")
    (directory / "rho.json").write_text(json.dumps({"rho": FIXED_RHO, "source": "PROJECT.md task 13 fixed five-league median"}, indent=2), encoding="utf-8")
    counts = {}
    for year in range(2014, current + 1):
        raw = season_file(year, league)
        counts[str(year)] = len(set(raw.HomeTeam.dropna()) | set(raw.AwayTeam.dropna()))
    (directory / "setup.json").write_text(json.dumps({"training_seasons": sorted(history.season.unique()),
                "training_max_date": str(history.date.max()), "teams_by_season": counts}, indent=2), encoding="utf-8")
    print(f"{league}: {len(history)} completed-season matches; {len(calibrators)} usable calibrators", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", choices=tuple(NEW_LEAGUES))
    args = parser.parse_args()
    for league in ([args.league] if args.league else NEW_LEAGUES):
        setup(league)
    install_gates()


if __name__ == "__main__":
    main()
