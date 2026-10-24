"""League x market gates for slip legs, using the rules pre-registered in PROJECT.md (task 1).

For every live league and slip market, on the test seasons, with the exact probability the
slips use (EPL: blended `probability`; market-mode leagues: walk-forward `market_probability`):
  C1 calibration slope: 95% CI upper bound >= 0.8 (not significantly over-spread)
  C2 calibration-in-the-large: 95% bootstrap CI (by matchday) of mean(outcome - p) upper bound >= 0
  C3 10 equal-count bins, every z >= -3
  C4 winner's curse: legs with p - bookmaker p > 0.03 (if >= 50): one-sided z >= -2
Every check guards against over-confidence only (amended 2026-10-25, see PROJECT.md): a market that
wins MORE often than we said makes slips safer than shown, so it is not removed.
Fewer than 300 legs = INSUFFICIENT (kept, flagged). Failing any of C1-C4 = FAIL: the market is
removed from that league's slip legs. Log loss vs the bookmaker is reported with a bootstrap CI.
Usage: python -m src.market_gates   (writes data/processed/market_gates.json and reports/market_gates.md)
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .accumulators import SLIP_MARKETS
from .calibration import ENGINE_DIR
from .leagues import get_league, paths
from .market_live import LIVE_LEAGUES

GATES_PATH = ENGINE_DIR / "data" / "processed" / "market_gates.json"
REPORT_PATH = ENGINE_DIR / "reports" / "market_gates.md"
MIN_LEGS, MIN_CURSE_LEGS, BOOTSTRAP, SEED = 300, 50, 1000, 20261024


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _z(outcome, p) -> float:
    sd = np.sqrt(np.sum(p * (1 - p)))
    return float((np.sum(outcome) - np.sum(p)) / sd) if sd > 0 else 0.0


def _bootstrap_mean_by_day(frame: pd.DataFrame, values: np.ndarray, rng) -> tuple[float, float]:
    """95% CI of the mean of `values`, resampling whole matchdays (legs on one day are correlated).

    The statistic is a mean, so resampling per-day sums and counts gives exactly the same
    bootstrap as resampling the legs of each day, far faster.
    """
    days = frame.date.dt.normalize().to_numpy()
    sums = pd.Series(values).groupby(days).sum().to_numpy()
    counts = pd.Series(values).groupby(days).size().to_numpy()
    picks = rng.integers(0, len(sums), size=(BOOTSTRAP, len(sums)))
    means = sums[picks].sum(axis=1) / counts[picks].sum(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def evaluate(league: str, market: str, legs: pd.DataFrame, column: str, rng) -> dict:
    d = legs[(legs.market == market)].dropna(subset=[column, "bookmaker_probability"]).copy()
    d["p"] = d[column].clip(1e-6, 1 - 1e-6)
    result = {"league": league, "market": market, "n": int(len(d))}
    if len(d) < MIN_LEGS or d.won.nunique() < 2:
        return result | {"status": "INSUFFICIENT"}
    y, p = d.won.to_numpy(float), d.p.to_numpy(float)

    fit = sm.Logit(y, sm.add_constant(_logit(p))).fit(disp=0)
    slope, (lo, hi) = float(fit.params[1]), (float(fit.conf_int()[1][0]), float(fit.conf_int()[1][1]))
    c1 = hi >= 0.8

    level = float(np.mean(y - p))
    level_ci = _bootstrap_mean_by_day(d, y - p, rng)
    c2 = level_ci[1] >= 0

    d["bin"] = pd.qcut(d.p.rank(method="first"), 10, labels=False)
    bin_z = [_z(g.won.to_numpy(float), g.p.to_numpy(float)) for _, g in d.groupby("bin")]
    c3 = min(bin_z) >= -3

    lifted = d[d.p - d.bookmaker_probability > 0.03]
    curse_z = _z(lifted.won.to_numpy(float), lifted.p.to_numpy(float)) if len(lifted) >= MIN_CURSE_LEGS else None
    c4 = curse_z is None or curse_z >= -2

    def leg_loss(q):
        q = np.clip(np.asarray(q, float), 1e-6, 1 - 1e-6)
        return -(y * np.log(q) + (1 - y) * np.log(1 - q))
    loss_diff = leg_loss(p) - leg_loss(d.bookmaker_probability)      # per leg; mean = log-loss difference
    diff = float(loss_diff.mean())
    diff_ci = _bootstrap_mean_by_day(d, loss_diff, rng)

    return result | {
        "status": "PASS" if (c1 and c2 and c3 and c4) else "FAIL",
        "C1_slope": round(slope, 3), "C1_ci": [round(lo, 3), round(hi, 3)], "C1": c1,
        "C2_level": round(level, 4), "C2_ci": [round(level_ci[0], 4), round(level_ci[1], 4)], "C2": c2,
        "C3_min_z": round(min(bin_z), 2), "C3": c3,
        "C4_lifted_legs": int(len(lifted)), "C4_z": None if curse_z is None else round(curse_z, 2), "C4": c4,
        "logloss_vs_book": round(diff, 4), "logloss_vs_book_ci": [round(diff_ci[0], 4), round(diff_ci[1], 4)],
        "mean_p": round(float(p.mean()), 4), "actual": round(float(y.mean()), 4),
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    rows = []
    for code, mode in LIVE_LEAGUES.items():
        legs = pd.read_parquet(paths(code).accumulator_legs)
        legs["date"] = pd.to_datetime(legs.date)
        column = "probability" if mode == "blended" else "market_probability"
        for market in SLIP_MARKETS:
            rows.append(evaluate(code, market, legs, column, rng))
            print(code, market, rows[-1]["status"], flush=True)
    gates = {}
    for r in rows:
        gates.setdefault(r["league"], {})[r["market"]] = r["status"]
    GATES_PATH.write_text(json.dumps({"rules": "PROJECT.md task 1 (pre-registered 2026-10-24)", "gates": gates,
                                      "details": rows}, indent=1), encoding="utf-8")

    lines = ["# League x market gates", "",
             "Rules pre-registered in PROJECT.md (task 1) before any result was computed. Test seasons 2024/25+.",
             "FAIL = removed from that league's slip legs; INSUFFICIENT = fewer than 300 legs (kept, flagged).", "",
             "| League | Market | n | Status | Slope (95% CI) | Level gap (95% CI) | lowest bin z | Lifted legs / z | Log loss vs bookmaker (95% CI) |",
             "|---|---|---:|---|---|---|---:|---|---|"]
    for r in rows:
        if r["status"] == "INSUFFICIENT":
            lines.append(f"| {get_league(r['league']).name} | {r['market']} | {r['n']} | INSUFFICIENT | | | | | |")
            continue
        lines.append(
            f"| {get_league(r['league']).name} | {r['market']} | {r['n']} | **{r['status']}** | "
            f"{r['C1_slope']} ({r['C1_ci'][0]}, {r['C1_ci'][1]}){'' if r['C1'] else ' ✗'} | "
            f"{r['C2_level']:+.4f} ({r['C2_ci'][0]:+.4f}, {r['C2_ci'][1]:+.4f}){'' if r['C2'] else ' ✗'} | "
            f"{r['C3_min_z']}{'' if r['C3'] else ' ✗'} | "
            f"{r['C4_lifted_legs']} / {r['C4_z'] if r['C4_z'] is not None else '-'}{'' if r['C4'] else ' ✗'} | "
            f"{r['logloss_vs_book']:+.4f} ({r['logloss_vs_book_ci'][0]:+.4f}, {r['logloss_vs_book_ci'][1]:+.4f}) |")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {GATES_PATH} and {REPORT_PATH}")


if __name__ == "__main__":
    main()
