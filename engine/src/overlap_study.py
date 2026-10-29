"""PROJECT.md task 14: research-only matched-return overlap study."""
import numpy as np
import pandas as pd

from .accumulators import TIERS, _wilson
from .diversity_study import _chosen, load_legs, select_day_slips
from .leagues import ENGINE_DIR


def select_variants(pool):
    current = select_day_slips(pool, "A")
    limited = current.copy()
    shared = set(current["safe"].match_key) & set(current["medium"].match_key) if {"safe", "medium"} <= current.keys() else set()
    big = _chosen(pool[~pool.match_key.isin(shared)], TIERS[2])
    limited.pop("big", None)
    if big is not None:
        limited["big"] = big
    return current, limited


def main():
    pool = load_legs()
    pool = pool[~pool.market.isin(("under_2.5", "under_3.5"))]
    rows, days = [], []
    for date, group in pool.groupby(pool.date.dt.strftime("%Y-%m-%d"), sort=True):
        current, limited = select_variants(group)
        triple = bool(set.intersection(*(set(current[t].match_key) for t in ("safe", "medium", "big")))) if len(current) == 3 else False
        for variant, slips in (("A", current), ("M", limited)):
            days.append(dict(date=date, variant=variant, triple=triple,
                             all_lost=bool(slips) and all(not s.won.astype(bool).all() for s in slips.values())))
            for tier, chosen in slips.items():
                won = int(chosen.won.astype(bool).all())
                rows.append(dict(date=date, tier=tier, variant=variant, won=won,
                                 predicted=float(chosen.probability.prod()), value=won * float(chosen.odds.prod()) - 1))
    slips, daily = pd.DataFrame(rows), pd.DataFrame(days)
    paired = slips.pivot(index=["date", "tier"], columns="variant", values="value").dropna()
    diff = (paired.M - paired.A).groupby(level="date").agg(["sum", "size"])
    picks = np.random.default_rng(20261029).integers(0, len(diff), size=(2000, len(diff)))
    estimates = diff["sum"].to_numpy()[picks].sum(axis=1) / diff["size"].to_numpy()[picks].sum(axis=1)
    low, high = np.quantile(estimates, [.025, .975])
    gain = float(diff["sum"].sum() / diff["size"].sum())
    losses = daily.groupby("variant").all_lost.mean()
    decision = "ADOPT M" if gain >= 0 and low >= -.01 and losses.M <= losses.A else "KEEP A"
    lines = ["# Match overlap study", "", f"**{decision}**. Research only; no live changes.", "",
             f"Matched return M-A: {gain:+.6f}, 95% whole-day bootstrap CI [{low:+.6f}, {high:+.6f}].",
             f"Matched slips: {len(paired)}; bootstrap 2,000 whole days, seed 20261029.",
             f"All-loss days: A {losses.A:.2%}, M {losses.M:.2%}.",
             f"Days with a match on all three under A: {int(daily[daily.variant == 'A'].triple.sum())}.", "",
             "| Variant | Tier | Slips | Predicted win | Actual win | Wilson 95% CI |",
             "|---|---|---:|---:|---:|---:|"]
    for (variant, tier), group in slips.groupby(["variant", "tier"]):
        lo, hi = _wilson(int(group.won.sum()), len(group))
        lines.append(f"| {variant} | {tier} | {len(group)} | {group.predicted.mean():.2%} | {group.won.mean():.2%} | {lo:.2%} to {hi:.2%} |")
    report = "\n".join(lines) + "\n"
    (ENGINE_DIR / "reports" / "overlap_study.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
