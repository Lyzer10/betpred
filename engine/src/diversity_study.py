"""Pre-registered study of match overlap across accumulator tiers.

Run from ``engine`` with ``python -m src.diversity_study``.  This module is
research only unless the pre-registered decision rule selects a challenger.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import numpy as np
import pandas as pd

from .accumulators import SLIP_MARKETS, TIERS, Tier, _wilson, best_slip
from .leagues import ENGINE_DIR, LEAGUES, paths

GATES_PATH = ENGINE_DIR / "data" / "processed" / "market_gates.json"
REPORT_PATH = ENGINE_DIR / "reports" / "slip_diversity.md"
VARIANTS = ("A", "B", "C")
STAKES = {"safe": 0.03, "medium": 0.02, "big": 0.01}
BOOTSTRAP_RESAMPLES = 2_000
BOOTSTRAP_SEED = 20261025


def failed_gates(path: Path = GATES_PATH) -> set[tuple[str, str]]:
    gates = json.loads(path.read_text(encoding="utf-8"))["gates"]
    return {(league, market) for league, markets in gates.items()
            for market, status in markets.items() if status == "FAIL"}


def load_legs() -> pd.DataFrame:
    """Load the registered five-league test pool with its live probability."""
    blocked = failed_gates()
    frames = []
    for code in LEAGUES:
        frame = pd.read_parquet(paths(code).accumulator_legs).copy()
        frame["date"] = pd.to_datetime(frame.date)
        frame = frame[frame.season.str[:4].astype(int) >= 2024]
        probability_column = "probability" if code == "EPL" else "market_probability"
        frame["probability"] = frame[probability_column]
        frame["league"] = code
        frame["match_key"] = code + ":" + frame.match_id.astype(str)
        frames.append(frame)

    legs = pd.concat(frames, ignore_index=True)
    allowed = [(league, market) not in blocked for league, market in zip(legs.league, legs.market)]
    legs = legs[legs.market.isin(SLIP_MARKETS) & pd.Series(allowed, index=legs.index)]
    legs = legs.dropna(subset=["date", "probability", "odds", "won"])
    legs = legs[(legs.odds >= 1.05) & legs.probability.between(0, 1, inclusive="neither")].copy()
    # best_slip groups on match_id. IDs overlap between leagues, so give it the
    # registered composite key while retaining match_key for reporting/tests.
    legs["source_match_id"] = legs.match_id
    legs["match_id"] = legs.match_key
    return legs.reset_index(drop=True)


def _chosen(pool: pd.DataFrame, tier: Tier) -> pd.DataFrame | None:
    picks = best_slip(pool, tier) if not pool.empty else None
    return None if picks is None else pool.loc[picks]


def _best_with_one_reuse(pool: pd.DataFrame, tier: Tier,
                         used_matches: set[str]) -> pd.DataFrame | None:
    """Return the exact best slip that reuses at most one used match."""
    candidates: list[pd.DataFrame] = []
    unused = ~pool.match_key.isin(used_matches)
    for reusable in [None, *sorted(used_matches)]:
        eligible = pool[unused] if reusable is None else pool[unused | (pool.match_key == reusable)]
        chosen = _chosen(eligible, tier)
        if chosen is not None:
            candidates.append(chosen)
    if not candidates:
        return None
    return max(candidates, key=lambda frame: float(frame.probability.prod()))


def select_day_slips(legs: pd.DataFrame, variant: str) -> dict[str, pd.DataFrame]:
    """Select one day's slips for registered variant A, B, or C."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown diversity variant: {variant}")
    pool = legs.reset_index(drop=True).copy()
    if "match_key" not in pool:
        pool["match_key"] = pool.match_id.astype(str)
    # Ensure best_slip uses the composite or caller supplied match key.
    pool["match_id"] = pool.match_key
    selected: dict[str, pd.DataFrame] = {}
    used_matches: set[str] = set()
    for tier in TIERS:
        if variant == "A":
            chosen = _chosen(pool, tier)
        elif variant == "B":
            chosen = _chosen(pool[~pool.match_key.isin(used_matches)], tier)
        else:
            chosen = _best_with_one_reuse(pool, tier, used_matches)
        if chosen is None:
            continue
        selected[tier.name] = chosen
        used_matches.update(chosen.match_key.astype(str))
    return selected


def daily_log_growth(slips: Mapping[str, Mapping[str, float]]) -> float:
    """Log bankroll change for one day using the registered fixed fractions."""
    change = sum(STAKES[tier] * (float(slip["won"]) * float(slip["total_odds"]) - 1)
                 for tier, slip in slips.items())
    return float(np.log1p(change))


def run_variants(legs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Select and settle all variants, returning slip and daily records."""
    slip_rows, day_rows = [], []
    grouped = legs.groupby(legs.date.dt.strftime("%Y-%m-%d"), sort=True)
    for day, day_legs in grouped:
        for variant in VARIANTS:
            selections = select_day_slips(day_legs, variant)
            day_slips: dict[str, dict[str, float]] = {}
            for tier, chosen in selections.items():
                record = {
                    "date": day, "variant": variant, "tier": tier,
                    "legs": len(chosen), "total_odds": float(chosen.odds.prod()),
                    "predicted_win": float(chosen.probability.prod()),
                    "won": int(chosen.won.astype(bool).all()),
                    "match_keys": tuple(chosen.match_key.astype(str)),
                }
                slip_rows.append(record)
                day_slips[tier] = record
            day_rows.append({
                "date": day, "variant": variant,
                "log_growth": daily_log_growth(day_slips),
                "offered": len(day_slips),
                "every_lost": bool(day_slips) and not any(row["won"] for row in day_slips.values()),
            })
    return pd.DataFrame(slip_rows), pd.DataFrame(day_rows)


def bootstrap_difference(daily: pd.DataFrame, challenger: str,
                         resamples: int = BOOTSTRAP_RESAMPLES,
                         seed: int = BOOTSTRAP_SEED) -> tuple[float, float, float]:
    pivot = daily.pivot(index="date", columns="variant", values="log_growth")
    differences = (pivot[challenger] - pivot["A"]).to_numpy(float)
    rng = np.random.default_rng(seed)
    sampled = differences[rng.integers(0, len(differences), size=(resamples, len(differences)))]
    bootstrap_means = sampled.mean(axis=1)
    low, high = np.quantile(bootstrap_means, [0.025, 0.975])
    return float(differences.mean()), float(low), float(high)


def maximum_drawdown(log_growth: pd.Series) -> float:
    bankroll = np.exp(log_growth.cumsum().to_numpy(float))
    peaks = np.maximum.accumulate(np.r_[1.0, bankroll])
    balances = np.r_[1.0, bankroll]
    return float(np.max(1 - balances / peaks))


def summarise(slips: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, bool], str]:
    variant_rows = []
    differences = {"A": (0.0, 0.0, 0.0)}
    for challenger in ("B", "C"):
        differences[challenger] = bootstrap_difference(daily, challenger)
    for variant in VARIANTS:
        days = daily[daily.variant == variant]
        offered = days[days.offered > 0]
        difference, low, high = differences[variant]
        variant_rows.append({
            "variant": variant,
            "mean_daily_log_growth": days.log_growth.mean(),
            "difference_vs_A": difference,
            "ci_low": low,
            "ci_high": high,
            "every_lost_share": offered.every_lost.mean(),
            "maximum_drawdown": maximum_drawdown(days.log_growth),
            "days": len(days),
        })
    variants = pd.DataFrame(variant_rows).set_index("variant")

    tier_rows = []
    for (variant, tier), group in slips.groupby(["variant", "tier"], sort=False):
        low, high = _wilson(int(group.won.sum()), len(group))
        tier_rows.append({
            "variant": variant, "tier": tier, "offered_days": len(group),
            "predicted_win": group.predicted_win.mean(), "actual_win": group.won.mean(),
            "ci_low": low, "ci_high": high,
        })
    tiers = pd.DataFrame(tier_rows)

    passes = {
        challenger: bool(variants.loc[challenger, "ci_high"] >= 0
                         and variants.loc[challenger, "every_lost_share"]
                         < variants.loc["A", "every_lost_share"])
        for challenger in ("B", "C")
    }
    eligible = [variant for variant, passed in passes.items() if passed]
    decision = (max(eligible, key=lambda variant: variants.loc[variant, "mean_daily_log_growth"])
                if eligible else "A")
    return variants, tiers, passes, decision


def write_report(legs: pd.DataFrame, variants: pd.DataFrame, tiers: pd.DataFrame,
                 passes: dict[str, bool], decision: str, path: Path = REPORT_PATH) -> None:
    names = {"A": "current independent", "B": "no shared matches", "C": "at most one shared match"}
    action = ("Keep the current independent tier selection."
              if decision == "A" else f"Adopt variant {decision}, {names[decision]}.")
    lines = [
        "# Slip diversity study", "", "## Summary", "", action,
        f"The pre-registered decision rule selected **{decision}**. "
        f"Variant B {'passed' if passes['B'] else 'failed'} and variant C "
        f"{'passed' if passes['C'] else 'failed'} the adoption rule.", "",
        f"The pooled test contains {legs.match_key.nunique():,} matches across "
        f"{legs.date.dt.strftime('%Y-%m-%d').nunique():,} calendar days. "
        "Probabilities, market gates, tier definitions and stakes were fixed before this run.", "",
        "## Bankroll and correlated-loss results", "",
        "| Variant | Rule | Mean daily log growth | Difference vs A | 95% bootstrap CI | Every offered slip lost | Maximum drawdown | Days |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, row in variants.iterrows():
        ci = "reference" if variant == "A" else f"[{row.ci_low:+.5f}, {row.ci_high:+.5f}]"
        lines.append(f"| {variant} | {names[variant]} | {row.mean_daily_log_growth:+.5f} | "
                     f"{row.difference_vs_A:+.5f} | {ci} | {row.every_lost_share:.1%} | "
                     f"{row.maximum_drawdown:.1%} | {int(row.days)} |")

    lines += ["", "Paired 95% intervals use 2,000 bootstrap resamples of whole calendar days "
              "with seed 20261025.", "", "## Per-tier results", "",
              "| Variant | Tier | Offered days | Mean predicted win | Actual win | Wilson 95% CI |",
              "|---|---|---:|---:|---:|---:|"]
    for row in tiers.itertuples(index=False):
        lines.append(f"| {row.variant} | {row.tier.title()} | {row.offered_days} | "
                     f"{row.predicted_win:.1%} | {row.actual_win:.1%} | "
                     f"{row.ci_low:.1%} to {row.ci_high:.1%} |")

    lines += ["", "## Decision rule audit", "",
              "A challenger passes only when its paired difference interval includes zero or is "
              "entirely above zero, and its every-slip-lost share is below A.", "",
              "| Challenger | CI condition | Fewer all-loss days | Pass |",
              "|---|---:|---:|---:|"]
    for challenger in ("B", "C"):
        ci_ok = variants.loc[challenger, "ci_high"] >= 0
        loss_ok = variants.loc[challenger, "every_lost_share"] < variants.loc["A", "every_lost_share"]
        lines.append(f"| {challenger} | {'Yes' if ci_ok else 'No'} | {'Yes' if loss_ok else 'No'} | "
                     f"{'Yes' if passes[challenger] else 'No'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    legs = load_legs()
    slips, daily = run_variants(legs)
    variants, tiers, passes, decision = summarise(slips, daily)
    write_report(legs, variants, tiers, passes, decision)
    print(variants.to_string())
    print(f"Decision: {decision}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
