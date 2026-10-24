"""Phase 1b evaluation of final blended and calibrated market probabilities."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import xlogy
from sklearn.linear_model import LogisticRegression

from .accumulators import TIERS, _logit, _wilson, backtest_slips, build_leg_table, write_report
from .leagues import LEAGUES, paths

MODES = {"blended": "probability", "market": "market_probability"}
CALIBRATION_MARKETS = {
    "Home 1Up": "home_1up",
    "Over 1.5": "over_1.5",
    "Double chance 1X": "double_1x",
    "Home win": "home_win",
}


def _multiclass_log_loss(legs: pd.DataFrame, column: str) -> tuple[float, float, int]:
    subset = legs[legs.market.isin(["home_win", "draw", "away_win"])]
    probability = subset.pivot(index="match_id", columns="market", values=column)
    actual = subset.pivot(index="match_id", columns="market", values="won")
    columns = ["home_win", "draw", "away_win"]
    joined = probability[columns].join(actual[columns], lsuffix="_p", rsuffix="_y").dropna()
    probability = joined[[f"{value}_p" for value in columns]].to_numpy(float)
    probability /= probability.sum(axis=1, keepdims=True)
    outcome = joined[[f"{value}_y" for value in columns]].to_numpy(int).argmax(axis=1)
    loss = float(-xlogy(np.eye(3)[outcome], np.clip(probability, 1e-15, 1)).sum(axis=1).mean())
    accuracy = float((probability.argmax(axis=1) == outcome).mean())
    return accuracy, loss, len(outcome)


def calibration_diagnostic(legs: pd.DataFrame, market: str, column: str) -> dict[str, float | bool]:
    frame = legs[legs.market == market][[column, "won"]].dropna().copy()
    frame["bin"] = pd.qcut(frame[column].rank(method="first"), 10, labels=False)
    rows = []
    for _, group in frame.groupby("bin"):
        probability = group[column].to_numpy(float)
        difference = float(group.won.mean() - probability.mean())
        standard_error = float(np.sqrt(np.sum(probability * (1 - probability))) / len(group))
        rows.append(abs(difference / standard_error) if standard_error else np.inf)
    model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
    model.fit(_logit(frame[column]).to_numpy().reshape(-1, 1), frame.won)
    slope = float(model.coef_[0, 0])
    max_z = float(max(rows))
    return {"max_z": max_z, "slope": slope, "pass": max_z <= 3 and 0.8 <= slope <= 1.2}


def _slip_results(slips: pd.DataFrame, mode: str) -> dict[str, dict]:
    output = {}
    for tier in TIERS:
        group = slips[(slips["mode"] == mode) & (slips.tier == tier.name)]
        low, high = _wilson(int(group.won.sum()), len(group))
        predicted = float(group.predicted_win.mean())
        output[tier.name] = {
            "count": len(group), "odds": float(group.total_odds.mean()), "predicted": predicted,
            "actual": float(group.won.mean()), "low": low, "high": high,
            "pass": bool(low <= predicted <= high),
        }
    return output


def evaluate_league(code: str, persist: bool = True) -> dict:
    league_paths = paths(code)
    legs = build_leg_table(code)
    slips = backtest_slips(legs, {
        "blended": ("probability", None),
        "market": ("market_probability", None),
    })
    if persist and code != "EPL":
        legs.to_parquet(league_paths.accumulator_legs, index=False)
        slips.to_parquet(league_paths.accumulator_slips, index=False)
        write_report(legs, slips, league_paths.stage4_report)

    opening = _multiclass_log_loss(legs, "bookmaker_probability")
    modes = {}
    for mode, column in MODES.items():
        result = _multiclass_log_loss(legs, column)
        calibration = {label: calibration_diagnostic(legs, market, column)
                       for label, market in CALIBRATION_MARKETS.items()}
        tiers = _slip_results(slips, mode)
        criteria = {
            "A": result[1] <= opening[1] + 0.010,
            "B": all(value["pass"] for value in tiers.values()),
            "C": all(value["pass"] for value in calibration.values()),
        }
        modes[mode] = {"result": result, "calibration": calibration, "tiers": tiers,
                       "criteria": criteria, "go": all(criteria.values())}
    recommendation = "GO-BLENDED" if modes["blended"]["go"] else ("GO-MARKET" if modes["market"]["go"] else "NO-GO")
    return {"opening": opening, "weights": legs.attrs.get("model_weights", {}),
            "modes": modes, "recommendation": recommendation}


def _yes(value: bool) -> str:
    return "PASS" if value else "FAIL"


def write_summary(results: dict[str, dict], output: Path) -> None:
    lines = ["# Phase 1b league summary", "",
             "All metrics use the final probabilities supplied to accumulator selection. The blended mode uses a model weight learned from 2021/22 through 2023/24 for the first test season, then updates from earlier seasons only. The market mode uses Platt calibrated bookmaker consensus with margin removed. No test season is used to tune its own probabilities.", "",
             "Criterion A requires final 1X2 log loss to be no more than bookmaker opening log loss plus 0.010. Criterion B requires every tier's predicted win rate to fall inside the Wilson 95% interval for its actual rate. Criterion C uses 10 equal count bins and requires every absolute calibration z score to be at most 3, plus an overall logistic calibration slope from 0.8 through 1.2.", "",
             "## Final recommendation", "", "| League | Blended A | Blended B | Blended C | Market A | Market B | Market C | Recommendation |", "|---|---|---|---|---|---|---|---|"]
    for code, result in results.items():
        b, m = result["modes"]["blended"], result["modes"]["market"]
        lines.append(f"| {LEAGUES[code].name} | {_yes(b['criteria']['A'])} | {_yes(b['criteria']['B'])} | {_yes(b['criteria']['C'])} | {_yes(m['criteria']['A'])} | {_yes(m['criteria']['B'])} | {_yes(m['criteria']['C'])} | {result['recommendation']} |")

    lines += ["", "## Learned model weights", "", "| League | 2024/25 | 2025/26 | 2026/27 |", "|---|---:|---:|---:|"]
    for code, result in results.items():
        weights = result["weights"]
        lines.append(f"| {LEAGUES[code].name} | {weights.get('2024/25', float('nan')):.2f} | {weights.get('2025/26', float('nan')):.2f} | {weights.get('2026/27', float('nan')):.2f} |")

    for code, result in results.items():
        lines += ["", f"## {LEAGUES[code].name}", "", "### 1X2", "",
                  "| Mode | Accuracy | Log loss | Criterion A |", "|---|---:|---:|---|"]
        opening = result["opening"]
        lines.append(f"| Bookmaker opening | {opening[0]:.2%} | {opening[1]:.4f} | Reference |")
        for mode in MODES:
            data = result["modes"][mode]
            lines.append(f"| {mode.title()} | {data['result'][0]:.2%} | {data['result'][1]:.4f} | {_yes(data['criteria']['A'])} |")
        lines += ["", "### Calibration", "", "| Mode | Market | Maximum absolute z | Slope | Pass |", "|---|---|---:|---:|---|"]
        for mode in MODES:
            for market, data in result["modes"][mode]["calibration"].items():
                lines.append(f"| {mode.title()} | {market} | {data['max_z']:.2f} | {data['slope']:.3f} | {_yes(data['pass'])} |")
        lines += ["", "### Accumulator slips", "", "| Mode | Tier | Count | Average odds | Predicted | Actual | Actual 95% CI | Pass |", "|---|---|---:|---:|---:|---:|---|---|"]
        for mode in MODES:
            for tier in ("safe", "medium", "big"):
                data = result["modes"][mode]["tiers"][tier]
                lines.append(f"| {mode.title()} | {tier.title()} | {data['count']} | {data['odds']:.2f} | {data['predicted']:.1%} | {data['actual']:.1%} | {data['low']:.1%} to {data['high']:.1%} | {_yes(data['pass'])} |")
    lines += ["", "Double chance means home or draw (1X).", ""]
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = {}
    for code in LEAGUES:
        print(f"Evaluating {code}", flush=True)
        results[code] = evaluate_league(code)
    write_summary(results, paths("EPL").reports_dir / "phase1_summary.md")
    for code, result in results.items():
        print(code, result["recommendation"], result["weights"])


if __name__ == "__main__":
    main()
