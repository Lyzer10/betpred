"""Blended model vs market mode for La Liga, Serie A, Bundesliga, Ligue 1, with more seasons.
Pre-registered in PROJECT.md (task 9), 2026-10-29.

The original choice compared 1X2 log loss on test seasons 2024/25 onwards only. This re-test adds the
validation seasons and every slip market:
- Legs: validation (2021/22-2023/24, `build_validation_leg_table`) + test (stored legs table), the 12
  `SLIP_MARKETS`, odds >= 1.05. Market: walk-forward `market_probability` (Platt on earlier days only).
- Blended: `blend(model_probability, market_probability, w)` with w fitted (`fit_model_weight`) on all
  legs of earlier seasons only; 2021/22 has no history and is not scored. Scored seasons 2022/23 onwards.
- Metric: mean per-leg log loss, paired difference (market - blended); 95% CI by bootstrap of whole days
  (2,000, seed 20261029).
- Decision per league: switch to blended only if the CI is entirely above 0. Otherwise keep market mode.
  Reported, not deciding: per-season and per-market differences, weights chosen.
Note: the goal model's settings were tuned on validation seasons, which can only flatter the blend.
Usage: python -m src.method_retest_study   (writes reports/method_retest_study.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .accumulators import (SLIP_MARKETS, _log_loss, blend, build_validation_leg_table,
                           calibrate_market_probabilities, fit_model_weight)
from .calibration import ENGINE_DIR
from .leagues import paths

REPORT_PATH = ENGINE_DIR / "reports" / "method_retest_study.md"
LEAGUES = ("LALIGA", "SERIEA", "BUNDES", "LIGUE1")
BOOTSTRAP, SEED = 2000, 20261029


def _loss(p, y):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def all_legs(league: str) -> pd.DataFrame:
    validation = build_validation_leg_table(league)
    test = pd.read_parquet(paths(league).accumulator_legs)
    validation, _ = calibrate_market_probabilities(validation, test.iloc[:0])   # validation uses only itself
    columns = ["match_id", "date", "season", "market", "model_probability", "market_probability", "won"]
    legs = pd.concat([validation[columns], test[columns]], ignore_index=True)
    return legs[legs.market.isin(SLIP_MARKETS)].reset_index(drop=True)


def compare(legs: pd.DataFrame) -> dict:
    legs = legs.copy()
    seasons = sorted(legs.season.unique())
    weights = {}
    legs["blended"] = np.nan
    for season in seasons[1:]:
        weights[season] = fit_model_weight(legs[legs.season < season])
        current = legs.season == season
        legs.loc[current, "blended"] = blend(legs.model_probability[current], legs.market_probability[current], weights[season])
    scored = legs[legs.season > seasons[0]].copy()
    scored["diff"] = _loss(scored.market_probability, scored.won) - _loss(scored.blended, scored.won)
    grouped = scored.groupby(scored.date.dt.normalize())["diff"]
    sums, counts = grouped.sum().to_numpy(), grouped.size().to_numpy()
    picks = np.random.default_rng(SEED).integers(0, len(sums), size=(BOOTSTRAP, len(sums)))
    low, high = np.percentile(sums[picks].sum(axis=1) / counts[picks].sum(axis=1), [2.5, 97.5])
    return {"legs": len(scored), "days": len(sums), "market": _log_loss(scored.market_probability, scored.won),
            "blended": _log_loss(scored.blended, scored.won), "gain": float(scored["diff"].mean()),
            "ci": (float(low), float(high)), "weights": weights,
            "per_season": scored.groupby("season")["diff"].mean().round(5).to_dict(),
            "per_market": scored.groupby("market")["diff"].mean().round(5).to_dict()}


def main() -> None:
    lines = ["# Blended vs market re-test (PROJECT.md task 9, pre-registered 2026-10-29)", "",
             "Gain = market log loss - blended log loss (positive = blended better).", ""]
    for league in LEAGUES:
        r = compare(all_legs(league))
        verdict = "SWITCH TO BLENDED" if r["ci"][0] > 0 else "KEEP MARKET"
        lines += [f"## {league}: **{verdict}**", "",
                  f"- {r['legs']} legs on {r['days']} days; log loss market {r['market']:.5f}, blended {r['blended']:.5f}",
                  f"- Gain {r['gain']:+.5f} (95% CI {r['ci'][0]:+.5f} to {r['ci'][1]:+.5f})",
                  f"- Model weight by season: {r['weights']}",
                  f"- Per season: {r['per_season']}", f"- Per market: {r['per_market']}", ""]
        print("\n".join(lines[-7:]), flush=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
