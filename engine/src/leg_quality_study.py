"""PROJECT.md task 25: research-only slip leg quality study (pre-registered 2026-11-23).

Pool: diversity_study.load_legs() (five main leagues, 2024/25+, gate FAILs excluded, odds >= 1.05),
additionally excluding under_2.5 and under_3.5, grouped by calendar day.

Variants (all per day, tiers via accumulators.best_slip):
  A  current (independent best_slip per tier: Safe 2.5-3.5 / 2-4 legs, Medium 3.5-8 / 3-6, Big 8-12 / 4-8).
  L  legs with probability < 0.70 are excluded; a tier with no valid slip is not offered.
  F  maximum legs capped at Safe 3, Medium 4, Big 6; otherwise as A.
  D  A with the distinct-legs rule live in predict.build_slips (no identical match+market on a later slip).

Primary metric: return per unit staked (won * total_odds - 1) on matched (date, tier) pairs offered by
BOTH variants (challenger minus A), 95% CI from 2,000 whole-day bootstrap resamples, seed 20261123.
Decision: adopt a challenger only if point estimate >= 0 AND CI lower bound >= -0.01 AND all-loss-day
share (on offered days) <= A's; otherwise KEEP A. Research only; no live changes.

Run from ``engine`` with ``python -m src.leg_quality_study``.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .accumulators import SLIP_MARKETS, TIERS, Tier, _wilson
from .diversity_study import _chosen, load_legs
from .leagues import ENGINE_DIR

REPORT_PATH = ENGINE_DIR / "reports" / "leg_quality_study.md"
ARCHIVE_DIR = ENGINE_DIR.parent / "web" / "public" / "data" / "archive"
VARIANTS = ("A", "L", "F", "D")
CHALLENGERS = ("L", "F", "D")
EXCLUDED_MARKETS = ("under_2.5", "under_3.5")
MIN_LEG_PROB = 0.70
FEWER_TIERS = (
    Tier("safe", 2.5, 3.5, 2, 3),
    Tier("medium", 3.5, 8.0, 3, 4),
    Tier("big", 8.0, 12.0, 4, 6),
)
BOOTSTRAP_RESAMPLES = 2_000
BOOTSTRAP_SEED = 20261123
PROB_BANDS = (
    ("<0.50", 0.00, 0.50),
    ("0.50-0.60", 0.50, 0.60),
    ("0.60-0.70", 0.60, 0.70),
    ("0.70-0.80", 0.70, 0.80),
    ("0.80-0.90", 0.80, 0.90),
    (">=0.90", 0.90, 1.01),
)


def load_pool() -> pd.DataFrame:
    """Registered five-league 2024/25+ pool without gate FAILs or under 2.5/3.5."""
    pool = load_legs()
    return pool[~pool.market.isin(EXCLUDED_MARKETS)].reset_index(drop=True)


def select_day_slips(pool: pd.DataFrame, variant: str) -> dict[str, pd.DataFrame]:
    """Select one day's slips for variant A, L, F, or D."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant: {variant}")
    frame = pool.reset_index(drop=True).copy()
    if "match_key" not in frame:
        frame["match_key"] = frame.match_id.astype(str)
    frame["match_id"] = frame.match_key.astype(str)

    if variant == "L":
        eligible = frame[frame.probability >= MIN_LEG_PROB]
        tiers = TIERS
    elif variant == "F":
        eligible = frame
        tiers = FEWER_TIERS
    else:
        eligible = frame
        tiers = TIERS

    out: dict[str, pd.DataFrame] = {}
    if variant == "D":
        leg_key = eligible.match_key.astype(str) + "|" + eligible.market.astype(str)
        used: set[str] = set()
        for tier in tiers:
            open_pool = eligible[~leg_key.isin(used)]
            chosen = _chosen(open_pool, tier)
            if chosen is not None:
                out[tier.name] = chosen
                used.update(leg_key.loc[chosen.index])
        return out

    for tier in tiers:
        chosen = _chosen(eligible, tier)
        if chosen is not None:
            out[tier.name] = chosen
    return out


def run_variants(pool: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run all variants day by day; return (slips, daily, selected_legs_A)."""
    slip_rows: list[dict] = []
    day_rows: list[dict] = []
    a_legs: list[pd.DataFrame] = []
    for date, group in pool.groupby(pool.date.dt.strftime("%Y-%m-%d"), sort=True):
        for variant in VARIANTS:
            slips = select_day_slips(group, variant)
            offered = len(slips)
            all_lost = bool(slips) and all(not s.won.astype(bool).all() for s in slips.values())
            day_rows.append({
                "date": date,
                "variant": variant,
                "offered": offered,
                "has_offer": offered > 0,
                "all_lost": all_lost,
                "has_safe": "safe" in slips,
                "has_medium": "medium" in slips,
                "has_big": "big" in slips,
            })
            for tier, chosen in slips.items():
                won = int(chosen.won.astype(bool).all())
                total_odds = float(chosen.odds.prod())
                slip_rows.append({
                    "date": date,
                    "tier": tier,
                    "variant": variant,
                    "legs": len(chosen),
                    "min_leg_p": float(chosen.probability.min()),
                    "total_odds": total_odds,
                    "predicted": float(chosen.probability.prod()),
                    "won": won,
                    "value": won * total_odds - 1.0,
                    "selection": "|".join(sorted(chosen.match_key.astype(str) + ":" + chosen.market.astype(str))),
                })
                if variant == "A":
                    a_legs.append(chosen[["probability", "won", "market"]].assign(date=date, tier=tier))
    slips_df = pd.DataFrame(slip_rows)
    daily_df = pd.DataFrame(day_rows)
    selected_a = pd.concat(a_legs, ignore_index=True) if a_legs else pd.DataFrame(columns=["probability", "won", "market", "date", "tier"])
    return slips_df, daily_df, selected_a


def paired_return_comparison(
    slips: pd.DataFrame,
    challenger: str,
    baseline: str = "A",
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Matched (date, tier) return per unit difference (challenger - baseline) with whole-day bootstrap 95% CI."""
    if slips.empty:
        return {"matched_slips": 0, "matched_days": 0, "baseline_return": float("nan"),
                "challenger_return": float("nan"), "gain": float("nan"),
                "ci_low": float("nan"), "ci_high": float("nan")}
    pivot = slips.pivot(index=["date", "tier"], columns="variant", values="value")
    if baseline not in pivot or challenger not in pivot:
        return {"matched_slips": 0, "matched_days": 0, "baseline_return": float("nan"),
                "challenger_return": float("nan"), "gain": float("nan"),
                "ci_low": float("nan"), "ci_high": float("nan")}
    paired = pivot[[baseline, challenger]].dropna()
    if paired.empty:
        return {"matched_slips": 0, "matched_days": 0, "baseline_return": float("nan"),
                "challenger_return": float("nan"), "gain": float("nan"),
                "ci_low": float("nan"), "ci_high": float("nan")}
    diff = (paired[challenger] - paired[baseline]).groupby(level="date").agg(["sum", "size"])
    picks = np.random.default_rng(seed).integers(0, len(diff), size=(resamples, len(diff)))
    est = diff["sum"].to_numpy()[picks].sum(axis=1) / diff["size"].to_numpy()[picks].sum(axis=1)
    low, high = np.quantile(est, [0.025, 0.975])
    changed_slips = int((paired[challenger] != paired[baseline]).sum())
    if "selection" in slips:
        sel = slips.pivot(index=["date", "tier"], columns="variant", values="selection").reindex(paired.index)
        changed_selections = int((sel[challenger] != sel[baseline]).sum())
    else:
        changed_selections = changed_slips
    return {
        "matched_slips": int(len(paired)),
        "matched_days": int(len(diff)),
        "changed_selections": changed_selections,
        "changed_payouts": changed_slips,
        "baseline_return": float(paired[baseline].mean()),
        "challenger_return": float(paired[challenger].mean()),
        "gain": float(diff["sum"].sum() / diff["size"].sum()),
        "ci_low": float(low),
        "ci_high": float(high),
    }


def summarise(
    slips: pd.DataFrame,
    daily: pd.DataFrame,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[dict[str, dict], dict[str, dict], str]:
    """Compute variant summaries, paired comparisons vs A, and the pre-registered decision."""
    stats: dict[str, dict] = {}
    for variant in VARIANTS:
        d = daily[daily.variant == variant]
        offered = d[d.has_offer]
        stats[variant] = {
            "pool_days": int(len(d)),
            "offered_days": int(len(offered)),
            "zero_offer_days": int(len(d) - len(offered)),
            "total_slips": int(d.offered.sum()),
            "all_lost_days": int(offered.all_lost.sum()),
            "all_lost_share": float(offered.all_lost.mean()) if len(offered) else float("nan"),
            "all_lost_share_all_days": float(d.all_lost.mean()) if len(d) else float("nan"),
        }

    comparisons: dict[str, dict] = {}
    passing: list[str] = []
    a_loss = stats["A"]["all_lost_share"]
    for challenger in CHALLENGERS:
        comp = paired_return_comparison(slips, challenger, "A", resamples=resamples, seed=seed)
        c_loss = stats[challenger]["all_lost_share"]
        ok_gain = bool(np.isfinite(comp["gain"]) and comp["gain"] >= 0.0)
        ok_ci = bool(np.isfinite(comp["ci_low"]) and comp["ci_low"] >= -0.01)
        ok_loss = bool(np.isfinite(c_loss) and np.isfinite(a_loss) and c_loss <= a_loss)
        passed = ok_gain and ok_ci and ok_loss
        comp["ok_gain"] = ok_gain
        comp["ok_ci"] = ok_ci
        comp["ok_loss"] = ok_loss
        comp["passed"] = passed
        comp["offered_days_diff"] = stats[challenger]["offered_days"] - stats["A"]["offered_days"]
        comparisons[challenger] = comp
        if passed:
            passing.append(challenger)

    if passing:
        best = max(passing, key=lambda v: comparisons[v]["gain"])
        decision = f"ADOPT {best}"
    else:
        decision = "KEEP A"
    return stats, comparisons, decision


def band_summary(probs: pd.Series, wons: pd.Series) -> list[dict]:
    """Win rate and Wilson 95% CI by probability band."""
    probs = pd.Series(probs, dtype=float)
    wons = pd.Series(wons, dtype=float)
    rows = []
    for label, lo, hi in PROB_BANDS:
        mask = (probs >= lo) & (probs < hi)
        n = int(mask.sum())
        wins = int(wons[mask].sum()) if n else 0
        pred = float(probs[mask].mean()) if n else float("nan")
        actual = wins / n if n else float("nan")
        ci_lo, ci_hi = _wilson(wins, n)
        rows.append({
            "band": label, "n": n, "wins": wins,
            "predicted": pred, "actual": actual, "ci_low": ci_lo, "ci_high": ci_hi,
        })
    return rows


def load_live_archive(archive_dir: Path = ARCHIVE_DIR) -> dict:
    """Read-only summary of settled slips and settled slip-market fixture legs in the live archive."""
    allowed_markets = set(SLIP_MARKETS) - set(EXCLUDED_MARKETS)
    slip_records: list[dict] = []
    slip_legs: list[dict] = []
    latest_fixtures: dict[tuple[str, str, str], dict] = {}
    slip_dates: list[str] = []

    for path in sorted(archive_dir.glob("20*.json")) if archive_dir.exists() else []:
        snap = json.loads(path.read_text(encoding="utf-8"))
        day = snap.get("date", path.stem)
        for fixture in snap.get("fixtures", []):
            key = (fixture["date"], fixture["home"], fixture["away"])
            latest_fixtures[key] = fixture
        for tier, slip in snap.get("slips", {}).items():
            legs = slip.get("legs", [])
            statuses = [leg.get("won") for leg in legs]
            if not legs or any(s is None for s in statuses):
                continue
            slip_dates.append(day)
            won = all(bool(s) for s in statuses)
            lost_count = sum(not bool(s) for s in statuses)
            probs = [float(leg["probability"]) for leg in legs]
            slip_records.append({
                "date": day,
                "tier": tier,
                "won": won,
                "n_legs": len(legs),
                "lost_legs": lost_count,
                "min_leg_p": min(probs),
                "has_sub_70": any(p < MIN_LEG_PROB for p in probs),
            })
            for leg in legs:
                slip_legs.append({
                    "date": day,
                    "tier": tier,
                    "market": leg["market"],
                    "probability": float(leg["probability"]),
                    "won": int(bool(leg["won"])),
                })

    fixture_legs: list[dict] = []
    fixture_dates: list[str] = []
    for fixture in latest_fixtures.values():
        result = fixture.get("result")
        if not result or "outcomes" not in result:
            continue
        fixture_dates.append(fixture["date"])
        outcomes = result["outcomes"]
        for m in fixture.get("markets", []):
            name = m.get("market")
            if name not in allowed_markets:
                continue
            won = outcomes.get(name)
            prob = m.get("probability")
            if won is None or prob is None:
                continue
            fixture_legs.append({
                "date": fixture["date"],
                "market": name,
                "probability": float(prob),
                "won": int(bool(won)),
            })

    return {
        "slips": pd.DataFrame(slip_records),
        "slip_legs": pd.DataFrame(slip_legs),
        "fixture_legs": pd.DataFrame(fixture_legs),
        "slip_date_range": (min(slip_dates), max(slip_dates)) if slip_dates else (None, None),
        "fixture_date_range": (min(fixture_dates), max(fixture_dates)) if fixture_dates else (None, None),
    }


def _fmt_pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.2%}"


def _band_table(title: str, rows: list[dict]) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Probability band | Legs | Wins | Mean predicted | Actual win | Wilson 95% CI | Diff (actual - pred) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        if r["n"] == 0:
            lines.append(f"| {r['band']} | 0 | 0 | n/a | n/a | n/a | n/a |")
        else:
            diff = r["actual"] - r["predicted"]
            lines.append(
                f"| {r['band']} | {r['n']:,} | {r['wins']:,} | {r['predicted']:.2%} | {r['actual']:.2%} "
                f"| {r['ci_low']:.2%} to {r['ci_high']:.2%} | {diff:+.2%} |"
            )
    lines.append("")
    return lines


def write_report(
    pool: pd.DataFrame,
    slips: pd.DataFrame,
    daily: pd.DataFrame,
    selected_a: pd.DataFrame,
    stats: dict[str, dict],
    comparisons: dict[str, dict],
    decision: str,
    live: dict,
    path: Path = REPORT_PATH,
) -> str:
    names = {
        "A": "current independent tiers (2-4 / 3-6 / 4-8 legs)",
        "L": "minimum leg probability >= 0.70 (independent tiers)",
        "F": "fewer-legs cap (Safe <= 3, Medium <= 4, Big <= 6)",
        "D": "distinct legs across tiers (live in predict.build_slips since 2026-11-22)",
    }
    pool_days = int(pool.date.dt.strftime("%Y-%m-%d").nunique())
    pool_matches = int(pool.match_key.nunique())
    lines = [
        "# Slip leg quality study (PROJECT.md task 25)",
        "",
        f"**Decision: {decision}**. Research only; no live changes made by this study.",
        "",
        "## Setup",
        "",
        f"- Backtest pool: five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`), seasons 2024/25+, "
        f"gate FAILs and `under_2.5`/`under_3.5` excluded, odds >= 1.05 ({len(pool):,} legs, {pool_matches:,} matches, "
        f"{pool_days:,} calendar days).",
        "- Estimated retail-margin odds are used in the backtest (indicative for comparing rules, never proof of profitability).",
        f"- Primary metric: matched `(date, tier)` return per unit staked (`won * total_odds - 1`), challenger minus A, "
        f"with 95% CI from {BOOTSTRAP_RESAMPLES:,} whole-day bootstrap resamples (seed `{BOOTSTRAP_SEED}`).",
        "- Adoption rule: adopt a challenger only if matched return `>= 0` AND 95% CI lower bound `>= -0.01` "
        "AND offered-day all-loss share `<= A`'s; otherwise **KEEP A**.",
        "",
        "## Primary result: matched-pair return per unit vs A",
        "",
        "| Challenger | Rule | Matched slips | Changed slips | Matched days | A return | Challenger return | Diff (V - A) | 95% whole-day CI | Offered days diff | All-loss share (offered days) | Pass? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|",
    ]
    for v in CHALLENGERS:
        c = comparisons[v]
        lines.append(
            f"| {v} | {names[v]} | {c['matched_slips']:,} | {c['changed_selections']:,} | {c['matched_days']:,} | "
            f"{c['baseline_return']:+.4f} | {c['challenger_return']:+.4f} | {c['gain']:+.4f} | "
            f"[{c['ci_low']:+.4f}, {c['ci_high']:+.4f}] | {c['offered_days_diff']:+d} | "
            f"{stats[v]['all_lost_share']:.2%} (vs A {stats['A']['all_lost_share']:.2%}) | "
            f"{'PASS' if c['passed'] else 'FAIL'} |"
        )

    a_slips = slips[slips.variant == "A"]
    over_cap = {
        t.name: int((a_slips.loc[a_slips.tier == t.name, "legs"] > t.max_legs).sum())
        for t in FEWER_TIERS
    }
    lines += [
        "",
        f"Note on `F`: in the uniform-margin backtest, `A` exceeded `F`'s leg caps on only "
        f"{sum(over_cap.values())} of {len(a_slips):,} slips "
        f"(safe > 3: {over_cap['safe']}, medium > 4: {over_cap['medium']}, big > 6: {over_cap['big']}), "
        f"changing {comparisons['F']['changed_selections']:,} slip selections and "
        f"{comparisons['F']['changed_payouts']:,} slip payouts. Although `F` formally meets the "
        "pre-registered rule, the backtest barely exercises `F` because uniform 7% retail-margin odds "
        "already penalise extra legs (`1.07^n`), so `F` is effectively untested for Medium/Big in this pool.",
    ]

    lines += [
        "",
        "## Variant coverage and all-loss days",
        "",
        "| Variant | Pool days | Offered days | Zero-offer days | Slips offered | All-loss days | All-loss share (offered days) | All-loss share (all pool days) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        s = stats[v]
        lines.append(
            f"| {v} | {s['pool_days']:,} | {s['offered_days']:,} | {s['zero_offer_days']:,} | "
            f"{s['total_slips']:,} | {s['all_lost_days']:,} | {s['all_lost_share']:.2%} | "
            f"{s['all_lost_share_all_days']:.2%} |"
        )

    lines += [
        "",
        "## Per-tier results (predicted vs actual win rate)",
        "",
        "| Variant | Tier | Slips | Avg legs | Avg min leg p | Avg odds | Predicted win | Actual win | Wilson 95% CI | Return/unit |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for variant in VARIANTS:
        for tier in ("safe", "medium", "big"):
            g = slips[(slips.variant == variant) & (slips.tier == tier)]
            if g.empty:
                lines.append(f"| {variant} | {tier} | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
                continue
            lo, hi = _wilson(int(g.won.sum()), len(g))
            lines.append(
                f"| {variant} | {tier} | {len(g):,} | {g.legs.mean():.2f} | {g.min_leg_p.mean():.2%} | "
                f"{g.total_odds.mean():.2f} | {g.predicted.mean():.2%} | {g.won.mean():.2%} | "
                f"{lo:.2%} to {hi:.2%} | {g.value.mean():+.4f} |"
            )

    lines += [
        "",
        "## Tier availability under L, F, and D vs A",
        "",
        "| Tier | A offered days | L offered (unavailable vs A) | F offered (unavailable vs A) | D offered (unavailable vs A) |",
        "|---|---:|---:|---:|---:|",
    ]
    a_days = daily[daily.variant == "A"].set_index("date")
    for tier in ("safe", "medium", "big"):
        col = f"has_{tier}"
        a_n = int(a_days[col].sum())
        cells = []
        for v in CHALLENGERS:
            v_days = daily[daily.variant == v].set_index("date")
            v_n = int(v_days[col].sum())
            lost = int((a_days[col] & ~v_days[col]).sum())
            pct = lost / a_n if a_n else 0.0
            cells.append(f"{v_n:,} ({lost:,} / {pct:.1%} lost)")
        lines.append(f"| {tier} | {a_n:,} | {cells[0]} | {cells[1]} | {cells[2]} |")

    lines += [
        "",
        "## Leg win rates by probability band (descriptive, not deciding)",
        "",
    ]
    lines += _band_table("Backtest pool (all eligible legs, 2024/25+ five leagues)", band_summary(pool.probability, pool.won))
    lines += _band_table("Backtest legs selected by A (chosen slip legs, 2024/25+)", band_summary(selected_a.probability, selected_a.won))

    live_slips = live["slips"]
    live_slip_legs = live["slip_legs"]
    live_fix_legs = live["fixture_legs"]
    if not live_slips.empty:
        d0, d1 = live["slip_date_range"]
        lost_slips = live_slips[~live_slips.won]
        lost_sub70 = int(lost_slips.has_sub_70.sum())
        lost_by_one = int((lost_slips.lost_legs == 1).sum())
        lines += [
            f"### Live archive check (`web/public/data/archive`, {d0} to {d1}, read-only)",
            "",
            f"- Settled archived slips: **{len(live_slips)}** ({int(live_slips.won.sum())} won, **{len(lost_slips)} lost**).",
            f"- Of the {len(lost_slips)} lost slips: **{lost_sub70}** contained at least one leg with probability `< 0.70`, "
            f"and **{lost_by_one}** lost on exactly one leg.",
            f"- Settled slip legs: {len(live_slip_legs):,} across those {len(live_slips)} slips.",
            "",
        ]
        lines += _band_table(f"Live archive: settled slip legs ({d0} to {d1})",
                             band_summary(live_slip_legs.probability, live_slip_legs.won))
    else:
        lines += ["### Live archive check", "", "No settled archived slips found.", ""]

    if not live_fix_legs.empty:
        fd0, fd1 = live["fixture_date_range"]
        lines += _band_table(
            f"Live archive: all settled fixture predictions for slip markets ({fd0} to {fd1}, nine live leagues)",
            band_summary(live_fix_legs.probability, live_fix_legs.won),
        )

    lines += [
        "## What was NOT checked",
        "",
        "- The backtest pool covers the five main leagues only (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`); the live app now also covers four newer leagues (`EREDIV`, `JUPILER`, `PRIMEIRA`, `SUPERLIG`) which have no `accumulator_legs.parquet` history.",
        "- Backtest leg prices are estimated from bookmaker opening/average odds with a fixed 7% retail margin, not historical Betpawa prices.",
        "- Combinations of rules (e.g. `L + D` or `F + D`, or other probability floors such as 0.65 / 0.75) were not pre-registered and were not searched so we avoid post-hoc tuning.",
        "- SportyBet Flexi partial-payout returns for Big slips were not modelled.",
        "",
    ]

    report = "\n".join(lines)
    path.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    pool = load_pool()
    slips, daily, selected_a = run_variants(pool)
    stats, comparisons, decision = summarise(slips, daily)
    live = load_live_archive()
    report = write_report(pool, slips, daily, selected_a, stats, comparisons, decision, live)
    print(report)


if __name__ == "__main__":
    main()
