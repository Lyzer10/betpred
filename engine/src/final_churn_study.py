"""Pre-registered study of preview-to-final accumulator churn (PROJECT.md task 12).

Research only unless the decision rule adopts variant K. Run from ``engine`` with
``python -m src.final_churn_study``.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .accumulators import LEG_MARKETS, RETAIL_MARGIN, SLIP_MARKETS, TIERS, Tier, _wilson, best_slip, bookmaker_implied
from .calibration import add_actuals
from .leagues import ENGINE_DIR, LEAGUES, get_league, paths
from .market_live import league_rho
from .predict import OWNER_EXCLUDED_MARKETS

GATES_PATH = ENGINE_DIR / "data" / "processed" / "market_gates.json"
REPORT_PATH = ENGINE_DIR / "reports" / "final_churn_study.md"
EARLY_ODDS = ("avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25")
FINAL_ODDS = ("close_odds_home", "close_odds_draw", "close_odds_away", "close_odds_over25", "close_odds_under25")
LIVE_MARKETS = tuple(market for market in SLIP_MARKETS if market not in OWNER_EXCLUDED_MARKETS)
START_SEASON = 2019
KEEP_THRESHOLD = 1.03
BOOTSTRAP_RESAMPLES = 2_000
BOOTSTRAP_SEED = 20261029


def failed_gates(path: Path = GATES_PATH) -> set[tuple[str, str]]:
    gates = json.loads(path.read_text(encoding="utf-8"))["gates"]
    return {(league, market) for league, markets in gates.items()
            for market, status in markets.items() if status == "FAIL"}


def build_league_legs(code: str, blocked: set[tuple[str, str]]) -> tuple[pd.DataFrame, dict]:
    """Build paired early/final market legs for one league from settled matches."""
    matches = pd.read_parquet(paths(code).matches).copy()
    matches["date"] = pd.to_datetime(matches.date)
    historical = matches[matches.season.str[:4].astype(int) >= START_SEASON].copy()
    odds_columns = [*EARLY_ODDS, *FINAL_ODDS]
    valid = (historical[odds_columns].notna() & historical[odds_columns].gt(0)).all(axis=1)
    valid &= historical[["home_goals", "away_goals"]].notna().all(axis=1)
    scored = add_actuals(historical[valid].copy())
    rho = league_rho(code)
    rows = []
    allowed_markets = [market for market in LIVE_MARKETS if (code, market) not in blocked]
    for match in scored.itertuples(index=False):
        preview = bookmaker_implied(*(float(getattr(match, column)) for column in EARLY_ODDS), rho)[0]
        final = bookmaker_implied(*(float(getattr(match, column)) for column in FINAL_ODDS), rho)[0]
        match_key = f"{code}:{match.match_id}"
        for market in allowed_markets:
            preview_probability = float(preview[market])
            final_probability = float(final[market])
            preview_odds = 1 / (preview_probability * (1 + RETAIL_MARGIN))
            final_odds = 1 / (final_probability * (1 + RETAIL_MARGIN))
            if not np.isfinite([preview_probability, final_probability, preview_odds, final_odds]).all():
                continue
            if final_odds < 1.05:
                continue
            rows.append({
                "league": code, "match_id": match_key, "source_match_id": match.match_id,
                "leg_key": f"{match_key}:{market}", "date": match.date, "season": match.season,
                "home_team": match.home_team, "away_team": match.away_team, "market": market,
                "preview_probability": preview_probability, "final_probability": final_probability,
                "preview_odds": preview_odds, "final_odds": final_odds,
                "won": int(getattr(match, LEG_MARKETS[market][1])),
            })
    coverage = {
        "league": code, "name": get_league(code).name, "historical_matches": len(historical),
        "eligible_matches": len(scored), "legs": len(rows),
    }
    return pd.DataFrame(rows), coverage


def load_legs() -> tuple[pd.DataFrame, pd.DataFrame]:
    blocked = failed_gates()
    frames, coverage = [], []
    for code in LEAGUES:
        frame, league_coverage = build_league_legs(code, blocked)
        frames.append(frame)
        coverage.append(league_coverage)
        print(f"{league_coverage['name']}: {league_coverage['eligible_matches']:,} matches, "
              f"{league_coverage['legs']:,} legs", flush=True)
    legs = pd.concat(frames, ignore_index=True)
    return legs, pd.DataFrame(coverage)


def _choose(pool: pd.DataFrame, tier: Tier, probability: str, odds: str) -> pd.DataFrame | None:
    candidates = pool.assign(probability=pool[probability], odds=pool[odds])
    candidates = candidates[candidates.odds >= 1.05]
    picks = best_slip(candidates, tier) if not candidates.empty else None
    return None if picks is None else pool.loc[picks]


def select_variants(pool: pd.DataFrame, tier: Tier) -> dict[str, object]:
    """Select F, P and K for one day/tier and explain K's choice.

    P is selected using preview probabilities and their implied preview prices. Its
    return and tier validity are then evaluated at final prices, as pre-registered.
    """
    final = _choose(pool, tier, "final_probability", "final_odds")
    if final is None:
        return {"F": None, "P": None, "K": None, "reason": "no_final_slip"}
    preview = _choose(pool, tier, "preview_probability", "preview_odds")
    if preview is None:
        return {"F": final, "P": None, "K": final, "reason": "no_preview_slip"}

    preview_final_odds = float(preview.final_odds.prod())
    final_probability = float(final.final_probability.prod())
    preview_final_probability = float(preview.final_probability.prod())
    outside = not tier.min_odds <= preview_final_odds <= tier.max_odds
    clearly_better = final_probability > KEEP_THRESHOLD * preview_final_probability
    if outside:
        keep, reason = final, "preview_final_odds_outside_tier"
    elif clearly_better:
        keep, reason = final, "final_more_than_3pct_better"
    else:
        keep, reason = preview, "kept_preview"
    return {"F": final, "P": preview, "K": keep, "reason": reason}


def _slip_record(date: str, tier: str, variant: str, chosen: pd.DataFrame, reason: str) -> dict:
    won = int(chosen.won.astype(bool).all())
    total_odds = float(chosen.final_odds.prod())
    return {
        "date": date, "tier": tier, "variant": variant, "legs": len(chosen),
        "total_odds": total_odds, "predicted_win": float(chosen.final_probability.prod()),
        "won": won, "return": won * total_odds - 1,
        "selection": tuple(chosen.leg_key), "reason": reason if variant == "K" else "",
    }


def run_variants(legs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Select and settle matched F/P/K slips for every calendar day and tier."""
    slips, decisions = [], []
    for date, day_legs in legs.groupby(legs.date.dt.strftime("%Y-%m-%d"), sort=True):
        for tier in TIERS:
            selected = select_variants(day_legs, tier)
            if selected["F"] is None:
                continue
            if selected["P"] is None:
                raise ValueError(f"Final offered {tier.name} on {date}, but preview offered no matched slip")
            for variant in ("F", "P", "K"):
                slips.append(_slip_record(date, tier.name, variant, selected[variant], selected["reason"]))
            decisions.append({"date": date, "tier": tier.name, "reason": selected["reason"],
                              "kept_preview": selected["reason"] == "kept_preview"})
    return pd.DataFrame(slips), pd.DataFrame(decisions)


def bootstrap_difference(slips: pd.DataFrame, challenger: str, resamples: int = BOOTSTRAP_RESAMPLES,
                         seed: int = BOOTSTRAP_SEED) -> tuple[float, float, float]:
    """Mean return difference with whole calendar days as bootstrap clusters."""
    pivot = slips.pivot(index=["date", "tier"], columns="variant", values="return")
    pivot["difference"] = pivot[challenger] - pivot["F"]
    by_day = pivot.groupby(level="date").difference.agg(["sum", "size"])
    sums, sizes = by_day["sum"].to_numpy(float), by_day["size"].to_numpy(float)
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(by_day), size=(resamples, len(by_day)))
    means = sums[picks].sum(axis=1) / sizes[picks].sum(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return float(sums.sum() / sizes.sum()), float(low), float(high)


def summarise(slips: pd.DataFrame, decisions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict, str]:
    differences = {"F": (0.0, 0.0, 0.0),
                   "P": bootstrap_difference(slips, "P"),
                   "K": bootstrap_difference(slips, "K")}
    overall_rows = []
    for variant in ("F", "P", "K"):
        group = slips[slips.variant == variant]
        difference, low, high = differences[variant]
        overall_rows.append({"variant": variant, "slips": len(group), "mean_return": group["return"].mean(),
                             "difference_vs_F": difference, "ci_low": low, "ci_high": high})
    overall = pd.DataFrame(overall_rows).set_index("variant")

    tier_rows = []
    for (variant, tier), group in slips.groupby(["variant", "tier"], sort=False):
        low, high = _wilson(int(group.won.sum()), len(group))
        tier_rows.append({"variant": variant, "tier": tier, "slips": len(group),
                          "predicted_win": group.predicted_win.mean(), "actual_win": group.won.mean(),
                          "ci_low": low, "ci_high": high, "mean_return": group["return"].mean()})
    tiers = pd.DataFrame(tier_rows)
    retention = {
        "matched_slips": len(decisions), "kept_slips": int(decisions.kept_preview.sum()),
        "days": int(decisions.date.nunique()),
        "days_with_preview_kept": int(decisions.loc[decisions.kept_preview, "date"].nunique()),
        "reasons": decisions.reason.value_counts().to_dict(),
    }
    decision = "K" if overall.loc["K", "difference_vs_F"] >= 0 and overall.loc["K", "ci_low"] >= -0.01 else "F"
    return overall, tiers, retention, decision


def write_report(coverage: pd.DataFrame, overall: pd.DataFrame, tiers: pd.DataFrame, retention: dict,
                 decision: str, path: Path = REPORT_PATH) -> None:
    action = ("Adopt K: keep the preview unless the final slip is clearly better."
              if decision == "K" else "Keep F: continue selecting the final slip from final information.")
    lines = [
        "# Final-slip churn study", "", "## Summary", "", f"**{action}**", "",
        "This is the pre-registered PROJECT.md task 12 result. No model, calibration, gate, odds source or "
        "tier was changed. P selects at the preview-implied price, but every variant is evaluated at the "
        "same final probabilities and final prices.", "", "## Data coverage", "",
        "| League | Matches since 2019/20 | With complete early + closing odds | Eligible live-market legs |",
        "|---|---:|---:|---:|",
    ]
    for row in coverage.itertuples(index=False):
        lines.append(f"| {row.name} | {row.historical_matches:,} | {row.eligible_matches:,} | {row.legs:,} |")
    lines += ["", "All five leagues are pooled by calendar day. Under 2.5/3.5 and gate-FAIL league x "
              "market pairs are excluded. Final estimated odds below 1.05 are excluded from every variant; "
              "preview odds below 1.05 are also ineligible when P is selected.", "",
              "## Primary result: return per unit staked", "",
              "| Variant | Rule | Matched slips | Mean return | Difference vs F | 95% whole-day bootstrap CI |",
              "|---|---|---:|---:|---:|---:|"]
    names = {"F": "current final selection", "P": "never change preview", "K": "keep unless clearly better"}
    for variant, row in overall.iterrows():
        ci = "reference" if variant == "F" else f"{row.ci_low:+.1%} to {row.ci_high:+.1%}"
        lines.append(f"| {variant} | {names[variant]} | {int(row.slips):,} | {row.mean_return:+.1%} | "
                     f"{row.difference_vs_F:+.1%} | {ci} |")
    k = overall.loc["K"]
    lines += ["", "Intervals use 2,000 bootstrap resamples of whole calendar days with seed 20261029.", "",
              "## Preview retention", "",
              f"K kept the preview for {retention['kept_slips']:,} of {retention['matched_slips']:,} matched "
              f"slips ({retention['kept_slips'] / retention['matched_slips']:.1%}), on "
              f"{retention['days_with_preview_kept']:,} of {retention['days']:,} days "
              f"({retention['days_with_preview_kept'] / retention['days']:.1%}).", "",
              f"Decision reasons: {retention['reasons']}.", "", "## Per-tier results", "",
              "| Variant | Tier | Slips | Predicted win | Actual win | Wilson 95% CI | Mean return |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for row in tiers.itertuples(index=False):
        lines.append(f"| {row.variant} | {row.tier.title()} | {row.slips:,} | {row.predicted_win:.1%} | "
                     f"{row.actual_win:.1%} | {row.ci_low:.1%} to {row.ci_high:.1%} | {row.mean_return:+.1%} |")
    passes = k.difference_vs_F >= 0 and k.ci_low >= -0.01
    lines += ["", "## Decision-rule audit", "",
              "Adopt K only when K - F is non-negative and its 95% CI lower bound is at least -0.01.", "",
              "| Check | Required | Result | Pass |", "|---|---:|---:|---:|",
              f"| K - F point estimate | >= 0 | {k.difference_vs_F:+.3f} | "
              f"{'Yes' if k.difference_vs_F >= 0 else 'No'} |",
              f"| K - F CI lower bound | >= -0.010 | {k.ci_low:+.3f} | "
              f"{'Yes' if k.ci_low >= -0.01 else 'No'} |", "",
              f"**Pre-registered decision: {'ADOPT K' if passes else 'KEEP F'}.**"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    legs, coverage = load_legs()
    slips, decisions = run_variants(legs)
    overall, tiers, retention, decision = summarise(slips, decisions)
    write_report(coverage, overall, tiers, retention, decision)
    print(overall.to_string())
    print(f"Decision: {decision}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
