# Slip diversity study

## Summary

Adopt variant B, no shared matches.
The pre-registered decision rule selected **B**. Variant B passed and variant C failed the adoption rule.

The pooled test contains 3,850 matches across 402 calendar days. Probabilities, market gates, tier definitions and stakes were fixed before this run.

## Bankroll and correlated-loss results

| Variant | Rule | Mean daily log growth | Difference vs A | 95% bootstrap CI | Every offered slip lost | Maximum drawdown | Days |
|---|---|---:|---:|---:|---:|---:|---:|
| A | current independent | -0.00599 | +0.00000 | reference | 54.0% | 92.2% | 402 |
| B | no shared matches | -0.00580 | +0.00019 | [-0.00383, +0.00442] | 53.7% | 91.6% | 402 |
| C | at most one shared match | -0.00506 | +0.00093 | [-0.00240, +0.00401] | 54.0% | 91.6% | 402 |

Paired 95% intervals use 2,000 bootstrap resamples of whole calendar days with seed 20261025.

## Per-tier results

| Variant | Tier | Offered days | Mean predicted win | Actual win | Wilson 95% CI |
|---|---|---:|---:|---:|---:|
| A | Safe | 367 | 38.6% | 35.7% | 31.0% to 40.7% |
| B | Safe | 367 | 38.6% | 35.7% | 31.0% to 40.7% |
| C | Safe | 367 | 38.6% | 35.7% | 31.0% to 40.7% |
| A | Medium | 323 | 27.7% | 27.2% | 22.7% to 32.3% |
| A | Big | 265 | 12.5% | 10.2% | 7.1% to 14.4% |
| C | Medium | 252 | 27.9% | 26.2% | 21.1% to 31.9% |
| B | Medium | 205 | 27.3% | 25.9% | 20.3% to 32.3% |
| B | Big | 163 | 11.7% | 8.0% | 4.7% to 13.2% |
| C | Big | 170 | 12.6% | 11.2% | 7.3% to 16.8% |

## Decision rule audit

A challenger passes only when its paired difference interval includes zero or is entirely above zero, and its every-slip-lost share is below A.

| Challenger | CI condition | Fewer all-loss days | Pass |
|---|---:|---:|---:|
| B | Yes | Yes | Yes |
| C | Yes | No | No |

## Review (Claude, 2026-10-25): independent tiers kept

Every backtest slip loses money on average (the estimated odds include the bookmaker margin), so a
variant that offers fewer slips shows higher "growth" simply by betting less. B offers 220 fewer
Medium/Big slips. Measured without that bias:

| Check | A | B | C |
|---|---:|---:|---:|
| ROI per unit staked | -8.4% | -11.6% | -8.7% |
| All-loss days (of 402) | 198 | 197 | 198 |

On the 207 days where A and B offer the same tiers, B-A daily log growth is -0.0013 (95% CI -0.0075
to +0.0049). The 220 slips B drops won 19.5% against 19.3% predicted. Decision: keep A.
