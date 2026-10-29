"""Market mode for leagues where the model adds nothing beyond the bookmakers.

Probabilities are the bookmaker consensus (margin removed, see accumulators.bookmaker_implied)
passed through a per-market Platt calibration fitted on that league's backtest legs. The
calibrations are fitted offline and stored, so the daily run is fast and deterministic:

  python -m src.market_live           # refit calibrators for every market-mode league
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .accumulators import _logit, _select_market_regularization, build_validation_leg_table
from .leagues import get_league, paths
from .new_league_config import NEW_LEAGUES

# Live mode per league, from the Phase 1b evaluation (reports/phase1_summary.md).
LIVE_LEAGUES = {"EPL": "blended", "LALIGA": "market", "SERIEA": "market", "BUNDES": "market", "LIGUE1": "market"}
LIVE_LEAGUES.update({code: "market" for code in NEW_LEAGUES})


# A calibration needs enough evidence and must point the right way; otherwise the raw
# bookmaker probability is used. (Ligue 1 over 0.5 had 36 legs with 3 losses and turned
# 91% into 100%; La Liga's came out with a negative slope.)
MIN_LEGS = 300
MIN_EACH_OUTCOME = 30


def usable(calibrator: dict | None) -> bool:
    return (calibrator is not None and calibrator.get("coef", 0) > 0
            and calibrator.get("legs", 0) >= MIN_LEGS and calibrator.get("minority", MIN_EACH_OUTCOME) >= MIN_EACH_OUTCOME)


def calibrators_path(league):
    return paths(league).processed_dir / "market_calibrators.json"


def fit_market_calibrators(league) -> dict:
    """Per market: logistic calibration of logit(bookmaker probability), exactly as validated.

    As in accumulators.calibrate_market_probabilities: the regularisation is chosen on the
    validation seasons (2021/22-2023/24) only, then the calibration is fitted on validation plus
    test seasons. Fitting on the short test window alone let a two-season pattern (e.g. away
    favourites) inflate probabilities, which the slip search then exploits.
    """
    validation = build_validation_leg_table(league).dropna(subset=["bookmaker_probability"])
    test = pd.read_parquet(paths(league).accumulator_legs).dropna(subset=["bookmaker_probability"])
    columns = ["date", "market", "bookmaker_probability", "won"]
    legs = pd.concat([validation[columns], test[columns]], ignore_index=True)
    calibrators = {}
    for market, group in legs.groupby("market"):
        market_validation = validation[validation.market == market]
        minority = int(min(group.won.sum(), (1 - group.won).sum()))
        if len(group) < MIN_LEGS or minority < MIN_EACH_OUTCOME or market_validation.won.nunique() < 2:
            continue
        regularization = _select_market_regularization(market_validation)
        model = LogisticRegression(C=regularization, solver="lbfgs", max_iter=1000)
        model.fit(_logit(group.bookmaker_probability).to_numpy().reshape(-1, 1), group.won)
        calibrator = {"coef": float(model.coef_[0, 0]), "intercept": float(model.intercept_[0]),
                      "regularization": regularization, "legs": int(len(group)), "minority": minority}
        if usable(calibrator):
            calibrators[market] = calibrator
    return calibrators


def load_calibrators(league) -> dict:
    stored = json.loads(calibrators_path(league).read_text(encoding="utf-8"))
    return {market: c for market, c in stored.items() if usable(c)}


def calibrate(probability: float, calibrator: dict | None) -> float:
    if calibrator is None:
        return float(probability)
    z = calibrator["coef"] * float(_logit(np.array([probability]))[0]) + calibrator["intercept"]
    return float(1 / (1 + np.exp(-z)))


def league_rho(league) -> float:
    """Typical Dixon-Coles low-score correction for the league (used to read the market's score matrix)."""
    if get_league(league).code in NEW_LEAGUES:
        return float(json.loads((paths(league).processed_dir / "rho.json").read_text(encoding="utf-8"))["rho"])
    dc = pd.read_parquet(paths(league).predictions_dc)
    return float(dc.loc[dc.variant == "blend", "rho"].median())


def main() -> None:
    for code, mode in LIVE_LEAGUES.items():
        if mode != "market":
            continue
        if code in NEW_LEAGUES:
            print(f"{code}: use python -m src.new_league_setup for completed-season-only setup")
            continue
        calibrators = fit_market_calibrators(code)
        calibrators_path(code).write_text(json.dumps(calibrators, indent=1), encoding="utf-8")
        print(f"{get_league(code).name}: {len(calibrators)} market calibrators, rho {league_rho(code):+.3f}")


if __name__ == "__main__":
    main()
