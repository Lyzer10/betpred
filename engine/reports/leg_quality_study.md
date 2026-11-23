# Slip leg quality study (PROJECT.md task 25)

**Decision: ADOPT F**. Research only; no live changes made by this study.

## Setup

- Backtest pool: five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`), seasons 2024/25+, gate FAILs and `under_2.5`/`under_3.5` excluded, odds >= 1.05 (31,571 legs, 3,850 matches, 402 calendar days).
- Estimated retail-margin odds are used in the backtest (indicative for comparing rules, never proof of profitability).
- Primary metric: matched `(date, tier)` return per unit staked (`won * total_odds - 1`), challenger minus A, with 95% CI from 2,000 whole-day bootstrap resamples (seed `20261123`).
- Adoption rule: adopt a challenger only if matched return `>= 0` AND 95% CI lower bound `>= -0.01` AND offered-day all-loss share `<= A`'s; otherwise **KEEP A**.

## Primary result: matched-pair return per unit vs A

| Challenger | Rule | Matched slips | Changed slips | Matched days | A return | Challenger return | Diff (V - A) | 95% whole-day CI | Offered days diff | All-loss share (offered days) | Pass? |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| L | minimum leg probability >= 0.70 (independent tiers) | 596 | 585 | 251 | -0.0657 | -0.1517 | -0.0860 | [-0.3148, +0.1406] | -116 | 64.14% (vs A 52.32%) | FAIL |
| F | fewer-legs cap (Safe <= 3, Medium <= 4, Big <= 6) | 955 | 5 | 367 | -0.0756 | -0.0729 | +0.0026 | [-0.0000, +0.0080] | +0 | 52.04% (vs A 52.32%) | PASS |
| D | distinct legs across tiers (live in predict.build_slips since 2026-11-22) | 955 | 483 | 367 | -0.0756 | -0.1013 | -0.0257 | [-0.1474, +0.0922] | +0 | 45.23% (vs A 52.32%) | FAIL |

Note on `F`: in the uniform-margin backtest, `A` exceeded `F`'s leg caps on only 5 of 955 slips (safe > 3: 5, medium > 4: 0, big > 6: 0), changing 5 slip selections and 2 slip payouts. Although `F` formally meets the pre-registered rule, the backtest barely exercises `F` because uniform 7% retail-margin odds already penalise extra legs (`1.07^n`), so `F` is effectively untested for Medium/Big in this pool.

## Variant coverage and all-loss days

| Variant | Pool days | Offered days | Zero-offer days | Slips offered | All-loss days | All-loss share (offered days) | All-loss share (all pool days) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 402 | 367 | 35 | 955 | 192 | 52.32% | 47.76% |
| L | 402 | 251 | 151 | 596 | 161 | 64.14% | 40.05% |
| F | 402 | 367 | 35 | 955 | 191 | 52.04% | 47.51% |
| D | 402 | 367 | 35 | 955 | 166 | 45.23% | 41.29% |

## Per-tier results (predicted vs actual win rate)

| Variant | Tier | Slips | Avg legs | Avg min leg p | Avg odds | Predicted win | Actual win | Wilson 95% CI | Return/unit |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| A | safe | 367 | 2.21 | 55.11% | 2.55 | 38.50% | 37.87% | 33.06% to 42.94% | -0.0351 |
| A | medium | 323 | 3.06 | 52.25% | 3.55 | 27.56% | 28.48% | 23.84% to 33.64% | +0.0124 |
| A | big | 265 | 4.06 | 40.60% | 8.09 | 12.34% | 9.43% | 6.47% to 13.56% | -0.2388 |
| L | safe | 251 | 3.75 | 72.12% | 2.53 | 36.25% | 32.67% | 27.17% to 38.69% | -0.1731 |
| L | medium | 191 | 4.97 | 71.50% | 3.53 | 25.60% | 25.13% | 19.51% to 31.73% | -0.1138 |
| L | big | 154 | 7.85 | 70.71% | 8.05 | 10.18% | 10.39% | 6.50% to 16.21% | -0.1638 |
| F | safe | 367 | 2.20 | 55.04% | 2.55 | 38.50% | 38.15% | 33.32% to 43.22% | -0.0283 |
| F | medium | 323 | 3.06 | 52.25% | 3.55 | 27.56% | 28.48% | 23.84% to 33.64% | +0.0124 |
| F | big | 265 | 4.06 | 40.60% | 8.09 | 12.34% | 9.43% | 6.47% to 13.56% | -0.2388 |
| D | safe | 367 | 2.21 | 55.11% | 2.55 | 38.50% | 37.87% | 33.06% to 42.94% | -0.0351 |
| D | medium | 323 | 3.05 | 50.08% | 3.56 | 26.86% | 28.48% | 23.84% to 33.64% | +0.0114 |
| D | big | 265 | 4.04 | 36.29% | 8.10 | 11.66% | 8.30% | 5.55% to 12.25% | -0.3303 |

## Tier availability under L, F, and D vs A

| Tier | A offered days | L offered (unavailable vs A) | F offered (unavailable vs A) | D offered (unavailable vs A) |
|---|---:|---:|---:|---:|
| safe | 367 | 251 (116 / 31.6% lost) | 367 (0 / 0.0% lost) | 367 (0 / 0.0% lost) |
| medium | 323 | 191 (132 / 40.9% lost) | 323 (0 / 0.0% lost) | 323 (0 / 0.0% lost) |
| big | 265 | 154 (111 / 41.9% lost) | 265 (0 / 0.0% lost) | 265 (0 / 0.0% lost) |

## Leg win rates by probability band (descriptive, not deciding)

### Backtest pool (all eligible legs, 2024/25+ five leagues)

| Probability band | Legs | Wins | Mean predicted | Actual win | Wilson 95% CI | Diff (actual - pred) |
|---|---:|---:|---:|---:|---:|---:|
| <0.50 | 11,684 | 3,873 | 33.37% | 33.15% | 32.30% to 34.01% | -0.23% |
| 0.50-0.60 | 4,346 | 2,400 | 54.91% | 55.22% | 53.74% to 56.70% | +0.31% |
| 0.60-0.70 | 4,636 | 3,059 | 65.45% | 65.98% | 64.61% to 67.33% | +0.53% |
| 0.70-0.80 | 7,234 | 5,439 | 74.60% | 75.19% | 74.18% to 76.17% | +0.58% |
| 0.80-0.90 | 3,484 | 2,918 | 84.21% | 83.75% | 82.49% to 84.94% | -0.46% |
| >=0.90 | 187 | 171 | 91.04% | 91.44% | 86.55% to 94.66% | +0.40% |

### Backtest legs selected by A (chosen slip legs, 2024/25+)

| Probability band | Legs | Wins | Mean predicted | Actual win | Wilson 95% CI | Diff (actual - pred) |
|---|---:|---:|---:|---:|---:|---:|
| <0.50 | 476 | 200 | 42.15% | 42.02% | 37.66% to 46.50% | -0.14% |
| 0.50-0.60 | 578 | 312 | 55.44% | 53.98% | 49.90% to 58.00% | -1.46% |
| 0.60-0.70 | 711 | 451 | 65.33% | 63.43% | 59.83% to 66.89% | -1.90% |
| 0.70-0.80 | 624 | 467 | 74.62% | 74.84% | 71.29% to 78.09% | +0.22% |
| 0.80-0.90 | 424 | 365 | 84.50% | 86.08% | 82.47% to 89.06% | +1.58% |
| >=0.90 | 62 | 58 | 91.17% | 93.55% | 84.55% to 97.46% | +2.38% |

### Live archive check (`web/public/data/archive`, 2026-10-24 to 2026-11-22, read-only)

- Settled archived slips: **43** (13 won, **30 lost**).
- Of the 30 lost slips: **29** contained at least one leg with probability `< 0.70`, and **19** lost on exactly one leg.
- Settled slip legs: 172 across those 43 slips.

### Live archive: settled slip legs (2026-10-24 to 2026-11-22)

| Probability band | Legs | Wins | Mean predicted | Actual win | Wilson 95% CI | Diff (actual - pred) |
|---|---:|---:|---:|---:|---:|---:|
| <0.50 | 10 | 8 | 44.22% | 80.00% | 49.02% to 94.33% | +35.78% |
| 0.50-0.60 | 22 | 10 | 56.42% | 45.45% | 26.92% to 65.34% | -10.97% |
| 0.60-0.70 | 29 | 17 | 65.34% | 58.62% | 40.74% to 74.49% | -6.72% |
| 0.70-0.80 | 34 | 23 | 76.23% | 67.65% | 50.84% to 80.87% | -8.59% |
| 0.80-0.90 | 39 | 35 | 85.68% | 89.74% | 76.42% to 95.94% | +4.07% |
| >=0.90 | 38 | 37 | 92.67% | 97.37% | 86.50% to 99.53% | +4.69% |

### Live archive: all settled fixture predictions for slip markets (2026-10-24 to 2026-11-22, nine live leagues)

| Probability band | Legs | Wins | Mean predicted | Actual win | Wilson 95% CI | Diff (actual - pred) |
|---|---:|---:|---:|---:|---:|---:|
| <0.50 | 776 | 239 | 32.70% | 30.80% | 27.65% to 34.14% | -1.90% |
| 0.50-0.60 | 336 | 173 | 55.20% | 51.49% | 46.16% to 56.78% | -3.71% |
| 0.60-0.70 | 325 | 213 | 64.94% | 65.54% | 60.22% to 70.50% | +0.59% |
| 0.70-0.80 | 538 | 412 | 74.92% | 76.58% | 72.82% to 79.96% | +1.66% |
| 0.80-0.90 | 327 | 280 | 84.37% | 85.63% | 81.41% to 89.02% | +1.26% |
| >=0.90 | 346 | 327 | 94.26% | 94.51% | 91.58% to 96.46% | +0.25% |

## What was NOT checked

- The backtest pool covers the five main leagues only (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`); the live app now also covers four newer leagues (`EREDIV`, `JUPILER`, `PRIMEIRA`, `SUPERLIG`) which have no `accumulator_legs.parquet` history.
- Backtest leg prices are estimated from bookmaker opening/average odds with a fixed 7% retail margin, not historical Betpawa prices.
- Combinations of rules (e.g. `L + D` or `F + D`, or other probability floors such as 0.65 / 0.75) were not pre-registered and were not searched so we avoid post-hoc tuning.
- SportyBet Flexi partial-payout returns for Big slips were not modelled.
