"""EPL model weight: test-era-only (V, live) vs validation + test-era (A), as pre-registered (PROJECT.md task 4).

Both procedures are walk-forward: the weight for season S is fitted only on seasons before S. They are
compared on every EPL leg of the slip markets in 2025/26 and later (the seasons where V has history),
so neither can win by selecting fewer bets. Usage: python -m src.weight_study
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .accumulators import LEGS_PATH, SLIP_MARKETS, blend, build_validation_leg_table, fit_model_weight
from .calibration import ENGINE_DIR
from .market_gates import evaluate

REPORT_PATH = ENGINE_DIR / "reports" / "epl_weight_study.md"
FIRST_EVAL_SEASON = "2025/26"
BOOTSTRAP, SEED = 2000, 20261025


def walk_forward(test: pd.DataFrame, validation: pd.DataFrame | None) -> tuple[np.ndarray, dict]:
    """Blended probability per test leg, weight fitted on earlier seasons (plus validation if given)."""
    out, weights = np.full(len(test), np.nan), {}
    for season in sorted(test.season.unique()):
        history = test[test.season < season]
        if validation is not None:
            history = pd.concat([validation, history], ignore_index=True)
        if history.empty:
            continue
        weight = fit_model_weight(history)
        rows = (test.season == season).to_numpy()
        out[rows] = blend(test.model_probability[rows], test.bookmaker_probability[rows], weight)
        weights[season] = weight
    return out, weights


def leg_loss(p, won) -> np.ndarray:
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    y = np.asarray(won, float)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def main() -> None:
    test = pd.read_parquet(LEGS_PATH)
    test["date"] = pd.to_datetime(test.date)
    validation = build_validation_leg_table("EPL")
    p_v, weights_v = walk_forward(test, None)
    p_a, weights_a = walk_forward(test, validation)
    test = test.assign(p_v=p_v, p_a=p_a)
    legs = test[(test.season >= FIRST_EVAL_SEASON) & test.market.isin(SLIP_MARKETS)].dropna(subset=["p_v", "p_a"])

    diff = leg_loss(legs.p_v, legs.won) - leg_loss(legs.p_a, legs.won)     # > 0: A more accurate
    days = legs.date.dt.normalize().to_numpy()
    sums = pd.Series(diff).groupby(days).sum().to_numpy()
    counts = pd.Series(diff).groupby(days).size().to_numpy()
    picks = np.random.default_rng(SEED).integers(0, len(sums), size=(BOOTSTRAP, len(sums)))
    boot = sums[picks].sum(axis=1) / counts[picks].sum(axis=1)
    low, high = np.percentile(boot, [2.5, 97.5])
    decision = "switch to A" if low > 0 else "keep V (current live)"

    rng = np.random.default_rng(SEED)
    gates = {name: {m: evaluate("EPL", m, legs, col, rng)["status"] for m in SLIP_MARKETS}
             for name, col in (("V", "p_v"), ("A", "p_a"))}
    lines = [
        "# EPL model weight study (PROJECT.md task 4, pre-registered)", "",
        f"Legs: {len(legs):,} EPL slip-market legs, {FIRST_EVAL_SEASON} onwards, {len(sums)} match days.", "",
        "| Procedure | Weights by season | Mean log loss |", "|---|---|---:|",
        f"| V (test-era only, live) | {weights_v} | {leg_loss(legs.p_v, legs.won).mean():.5f} |",
        f"| A (validation + test-era) | {weights_a} | {leg_loss(legs.p_a, legs.won).mean():.5f} |", "",
        f"V - A: {diff.mean():+.5f} (95% CI {low:+.5f} to {high:+.5f}). **Decision: {decision}.**", "",
        "Gates (task-1 rules, reported only): " + "; ".join(
            f"{name}: " + (", ".join(f"{m} {s}" for m, s in g.items() if s != "PASS") or "all PASS")
            for name, g in gates.items()),
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
