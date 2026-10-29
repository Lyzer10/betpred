# Final-slip churn study

## Summary

**Keep F: continue selecting the final slip from final information.**

This is the pre-registered PROJECT.md task 12 result. No model, calibration, gate, odds source or tier was changed. P selects at the preview-implied price, but every variant is evaluated at the same final probabilities and final prices.

## Data coverage

| League | Matches since 2019/20 | With complete early + closing odds | Eligible live-market legs |
|---|---:|---:|---:|
| Premier League | 2,730 | 2,730 | 21,374 |
| La Liga | 2,749 | 2,748 | 24,974 |
| Serie A | 2,730 | 2,728 | 21,704 |
| Bundesliga | 2,196 | 2,195 | 14,992 |
| Ligue 1 | 2,400 | 2,399 | 16,708 |

All five leagues are pooled by calendar day. Under 2.5/3.5 and gate-FAIL league x market pairs are excluded. Final estimated odds below 1.05 are excluded from every variant; preview odds below 1.05 are also ineligible when P is selected.

## Primary result: return per unit staked

| Variant | Rule | Matched slips | Mean return | Difference vs F | 95% whole-day bootstrap CI |
|---|---|---:|---:|---:|---:|
| F | current final selection | 3,106 | -17.4% | +0.0% | reference |
| P | never change preview | 3,106 | -13.7% | +3.6% | -5.4% to +12.8% |
| K | keep unless clearly better | 3,106 | -16.2% | +1.1% | -1.9% to +4.0% |

Intervals use 2,000 bootstrap resamples of whole calendar days with seed 20261029.

## Preview retention

K kept the preview for 510 of 3,106 matched slips (16.4%), on 430 of 1,182 days (36.4%).

Decision reasons: {'preview_final_odds_outside_tier': 1352, 'final_more_than_3pct_better': 1244, 'kept_preview': 510}.

## Per-tier results

| Variant | Tier | Slips | Predicted win | Actual win | Wilson 95% CI | Mean return |
|---|---|---:|---:|---:|---:|---:|
| F | Safe | 1,182 | 34.7% | 34.3% | 31.6% to 37.0% | -13.7% |
| P | Safe | 1,182 | 34.4% | 34.8% | 32.1% to 37.5% | -12.3% |
| K | Safe | 1,182 | 34.6% | 34.8% | 32.1% to 37.5% | -12.2% |
| F | Medium | 1,044 | 23.3% | 23.9% | 21.4% to 26.5% | -16.3% |
| P | Medium | 1,044 | 23.1% | 25.9% | 23.3% to 28.6% | -8.0% |
| K | Medium | 1,044 | 23.2% | 24.0% | 21.5% to 26.7% | -15.5% |
| F | Big | 880 | 9.5% | 9.5% | 7.8% to 11.7% | -23.5% |
| P | Big | 880 | 9.4% | 9.5% | 7.8% to 11.7% | -22.5% |
| K | Big | 880 | 9.5% | 9.7% | 7.9% to 11.8% | -22.4% |

## Decision-rule audit

Adopt K only when K - F is non-negative and its 95% CI lower bound is at least -0.01.

| Check | Required | Result | Pass |
|---|---:|---:|---:|
| K - F point estimate | >= 0 | +0.011 | Yes |
| K - F CI lower bound | >= -0.010 | -0.019 | No |

**Pre-registered decision: KEEP F.**
