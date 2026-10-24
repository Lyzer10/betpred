"""Does Betpawa's own 1Up price improve our 1Up probability? Pre-registered in PROJECT.md (task 7).

Data: every settled archived prediction (`predict.settled_predictions`) of home_1up / away_1up that has a
Betpawa price. Chronological split by match day: the first 60% of days fit a logistic regression
won ~ logit(our probability) + logit(1 / Betpawa odds) (the intercept absorbs Betpawa's margin); the
last 40% evaluate it against a baseline fitted the same way on our probability alone
(won ~ logit(our probability)), so any gain is Betpawa's information, not a recalibration of ours.
Mean log loss per leg; paired difference (baseline - combined), 95% bootstrap CI over whole days
(2,000, seed 20261025).
Decision: use the combination only if the evaluation has >= 300 legs and the CI is entirely above 0.
Usage: python -m src.betpawa_1up_study
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .calibration import ENGINE_DIR
from .predict import settled_predictions

REPORT_PATH = ENGINE_DIR / "reports" / "betpawa_1up_study.md"
MARKETS = ("home_1up", "away_1up")
MIN_EVAL_LEGS, FIT_SHARE, BOOTSTRAP, SEED = 300, 0.6, 2000, 20261025


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _loss(p, y):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def legs_from_archive(fixtures: list[dict]) -> pd.DataFrame:
    rows = [{"day": f["date"], "market": m["market"], "ours": m["probability"], "odds": m.get("betpawa_odds"),
             "won": float(f["result"]["outcomes"][m["market"]])}
            for f in fixtures for m in f["markets"] if m["market"] in MARKETS and m.get("betpawa_odds")]
    return pd.DataFrame(rows, columns=["day", "market", "ours", "odds", "won"])


def study(legs: pd.DataFrame) -> dict:
    days = sorted(legs.day.unique())
    fit_days = set(days[:int(len(days) * FIT_SHARE)])
    fit, test = legs[legs.day.isin(fit_days)], legs[~legs.day.isin(fit_days)]
    if len(test) < MIN_EVAL_LEGS or fit.won.nunique() < 2:
        return {"status": "insufficient", "legs": len(legs), "evaluation_legs": len(test), "needed": MIN_EVAL_LEGS}
    X = lambda d: sm.add_constant(np.column_stack([_logit(d.ours), _logit(1 / d.odds)]), has_constant="add")
    X0 = lambda d: sm.add_constant(_logit(d.ours).reshape(-1, 1), has_constant="add")
    model = sm.Logit(fit.won.to_numpy(), X(fit)).fit(disp=0)
    baseline = sm.Logit(fit.won.to_numpy(), X0(fit)).fit(disp=0)
    y = test.won.to_numpy()
    diff = _loss(baseline.predict(X0(test)), y) - _loss(model.predict(X(test)), y)
    sums = pd.Series(diff).groupby(test.day.to_numpy()).sum().to_numpy()
    counts = pd.Series(diff).groupby(test.day.to_numpy()).size().to_numpy()
    picks = np.random.default_rng(SEED).integers(0, len(sums), size=(BOOTSTRAP, len(sums)))
    low, high = np.percentile(sums[picks].sum(axis=1) / counts[picks].sum(axis=1), [2.5, 97.5])
    return {"status": "use combination" if low > 0 else "keep ours", "evaluation_legs": len(test),
            "gain": round(float(diff.mean()), 5), "ci": [round(float(low), 5), round(float(high), 5)],
            "coefficients": [round(float(c), 3) for c in model.params]}


def main() -> None:
    result = study(legs_from_archive(settled_predictions()))
    REPORT_PATH.write_text(f"# Betpawa 1Up price study (PROJECT.md task 7, pre-registered)\n\n{result}\n", encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
