"""PROJECT.md task 24: research-only study of "no identical leg on two slips".

Variant A (live): each tier chosen independently with best_slip.
Variant D: Safe as A; Medium and Big may reuse a match, but never the same match AND market
already on an earlier slip (a match may return with a different bet, e.g. win vs double chance).
Run from ``engine`` with ``python -m src.distinct_legs_study``.
"""
import numpy as np
import pandas as pd

from .accumulators import TIERS, _wilson
from .diversity_study import _chosen, load_legs
from .leagues import ENGINE_DIR


def select(pool: pd.DataFrame, variant: str) -> dict[str, pd.DataFrame]:
    pool = pool.reset_index(drop=True)
    pool["leg_key"] = pool.match_key + "|" + pool.market
    out, used = {}, set()
    for tier in TIERS:
        chosen = _chosen(pool if variant == "A" else pool[~pool.leg_key.isin(used)], tier)
        if chosen is not None:
            out[tier.name] = chosen
            used.update(chosen.leg_key)
    return out


def main():
    pool = load_legs()
    pool = pool[~pool.market.isin(("under_2.5", "under_3.5"))]
    rows, days = [], []
    for date, group in pool.groupby(pool.date.dt.strftime("%Y-%m-%d"), sort=True):
        for variant in ("A", "D"):
            slips = select(group, variant)
            shared = sum(len(set(a.match_key) & set(b.match_key)) for i, a in enumerate(slips.values())
                         for b in list(slips.values())[i + 1:])
            days.append(dict(date=date, variant=variant, shared=shared,
                             all_lost=bool(slips) and all(not s.won.astype(bool).all() for s in slips.values())))
            for tier, chosen in slips.items():
                won = int(chosen.won.astype(bool).all())
                rows.append(dict(date=date, tier=tier, variant=variant, won=won,
                                 predicted=float(chosen.probability.prod()), value=won * float(chosen.odds.prod()) - 1))
    slips, daily = pd.DataFrame(rows), pd.DataFrame(days)
    paired = slips.pivot(index=["date", "tier"], columns="variant", values="value").dropna()
    diff = (paired.D - paired.A).groupby(level="date").agg(["sum", "size"])
    picks = np.random.default_rng(20261122).integers(0, len(diff), size=(2000, len(diff)))
    est = diff["sum"].to_numpy()[picks].sum(axis=1) / diff["size"].to_numpy()[picks].sum(axis=1)
    low, high = np.quantile(est, [.025, .975])
    gain = float(diff["sum"].sum() / diff["size"].sum())
    loss = daily.groupby("variant").all_lost.mean()
    decision = "ADOPT D" if gain >= 0 and low >= -.01 and loss.D <= loss.A else "KEEP A"
    lines = ["# Distinct legs study", "", f"**{decision}**. Research only; no live changes.", "",
             f"Matched return D-A: {gain:+.6f}, 95% whole-day bootstrap CI [{low:+.6f}, {high:+.6f}].",
             f"Matched slips: {len(paired)}; 2,000 whole days, seed 20261122.",
             f"All-loss days: A {loss.A:.2%}, D {loss.D:.2%}.",
             f"Mean matches shared between slips per day: A {daily[daily.variant == 'A'].shared.mean():.2f}, "
             f"D {daily[daily.variant == 'D'].shared.mean():.2f}.", "",
             "| Variant | Tier | Slips | Predicted win | Actual win | Wilson 95% CI |", "|---|---|---:|---:|---:|---:|"]
    for (variant, tier), g in slips.groupby(["variant", "tier"]):
        lo, hi = _wilson(int(g.won.sum()), len(g))
        lines.append(f"| {variant} | {tier} | {len(g)} | {g.predicted.mean():.2%} | {g.won.mean():.2%} | {lo:.2%} to {hi:.2%} |")
    report = "\n".join(lines) + "\n"
    (ENGINE_DIR / "reports" / "distinct_legs_study.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
