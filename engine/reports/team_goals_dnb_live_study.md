# Team goals and Draw No Bet with real Betpawa prices (PROJECT.md task 15, pre-registered 2026-11-07)

Settled archived matches with logged pre-kickoff Betpawa prices: **97** matches, **550** scored legs.
Platt calibrators fitted per league x market on seasons before 2026/27 only (`LogisticRegression(C=1.0)` on `logit(raw)`).
Draw No Bet (`dnb_home`, `dnb_away`) is scored on non-drawn matches only (about 13 matches without a DNB leg: drawn, i.e. refunded, or DNB not priced).
Margin column reports mean(`1 / betpawa_odds - probability`) for every market (and for DNB also the exact two-way bookmaker overround `1/odds_home + 1/odds_away - 1` because both sides are logged; Betpawa team-total Under prices are not logged).

| Market | Settled legs | Still needed (to 300) | Our mean p | Actual win rate (95% Wilson CI) | Betpawa mean implied p | Mean margin vs our p (2-way DNB) | Value legs (edge >= 3%) | Value return / unit | Level gap (95% CI) | Status |
|---|---:|---:|---:|---|---:|---|---:|---:|---|---|
| home_over_0.5 | 92 | 208 | 0.7908 | 0.7826 (0.6879-0.8546) | 0.8038 | +0.0130 | 5 | -0.2040 (-1.02u) | -0.0082 (-0.1502, +0.0373) | **INSUFFICIENT** |
| away_over_0.5 | 96 | 204 | 0.7288 | 0.6667 (0.5676-0.7529) | 0.7444 | +0.0156 | 5 | -0.4740 (-2.37u) | -0.0621 (-0.1144, +0.0369) | **INSUFFICIENT** |
| home_over_1.5 | 97 | 203 | 0.4875 | 0.5670 (0.4677-0.6612) | 0.5099 | +0.0224 | 14 | +0.3757 (+5.26u) | +0.0795 (-0.0260, +0.1437) | **INSUFFICIENT** |
| away_over_1.5 | 97 | 203 | 0.3857 | 0.3299 (0.2444-0.4284) | 0.4121 | +0.0264 | 7 | -0.7129 (-4.99u) | -0.0558 (-0.1124, +0.0536) | **INSUFFICIENT** |
| dnb_home | 84 | 216 | 0.5781 | 0.6548 (0.5483-0.7477) | 0.5996 | +0.0215 (2-way +0.0502) | 8 | +0.4175 (+3.34u) | +0.0766 (-0.0740, +0.1283) | **INSUFFICIENT** |
| dnb_away | 84 | 216 | 0.4219 | 0.3452 (0.2523-0.4517) | 0.4506 | +0.0287 (2-way +0.0502) | 10 | +0.2020 (+2.02u) | -0.0766 (-0.1346, +0.0685) | **INSUFFICIENT** |

## Decision

Statuses: INSUFFICIENT. Settled priced legs per market: 84 to 97 (still needing 203 to 216 to reach the 300-leg minimum). No market may enter slips until it has >= 300 settled priced legs and passes the one-sided level check.

Details:
```json
[
  {
    "market": "home_over_0.5",
    "legs": 92,
    "still_needed": 208,
    "mean_probability": 0.7908,
    "mean_raw_probability": 0.7793,
    "actual_win_rate": 0.7826,
    "wilson_ci": [
      0.6879,
      0.8546
    ],
    "betpawa_mean_implied": 0.8038,
    "mean_margin_vs_ours": 0.013,
    "mean_two_way_margin": null,
    "value_legs": 5,
    "value_return_per_unit": -0.204,
    "value_profit_units": -1.02,
    "level_gap": -0.0082,
    "level_ci": [
      -0.1502,
      0.0373
    ],
    "level_pass": true,
    "status": "INSUFFICIENT"
  },
  {
    "market": "away_over_0.5",
    "legs": 96,
    "still_needed": 204,
    "mean_probability": 0.7288,
    "mean_raw_probability": 0.7195,
    "actual_win_rate": 0.6667,
    "wilson_ci": [
      0.5676,
      0.7529
    ],
    "betpawa_mean_implied": 0.7444,
    "mean_margin_vs_ours": 0.0156,
    "mean_two_way_margin": null,
    "value_legs": 5,
    "value_return_per_unit": -0.474,
    "value_profit_units": -2.37,
    "level_gap": -0.0621,
    "level_ci": [
      -0.1144,
      0.0369
    ],
    "level_pass": true,
    "status": "INSUFFICIENT"
  },
  {
    "market": "home_over_1.5",
    "legs": 97,
    "still_needed": 203,
    "mean_probability": 0.4875,
    "mean_raw_probability": 0.4817,
    "actual_win_rate": 0.567,
    "wilson_ci": [
      0.4677,
      0.6612
    ],
    "betpawa_mean_implied": 0.5099,
    "mean_margin_vs_ours": 0.0224,
    "mean_two_way_margin": null,
    "value_legs": 14,
    "value_return_per_unit": 0.3757,
    "value_profit_units": 5.26,
    "level_gap": 0.0795,
    "level_ci": [
      -0.026,
      0.1437
    ],
    "level_pass": true,
    "status": "INSUFFICIENT"
  },
  {
    "market": "away_over_1.5",
    "legs": 97,
    "still_needed": 203,
    "mean_probability": 0.3857,
    "mean_raw_probability": 0.385,
    "actual_win_rate": 0.3299,
    "wilson_ci": [
      0.2444,
      0.4284
    ],
    "betpawa_mean_implied": 0.4121,
    "mean_margin_vs_ours": 0.0264,
    "mean_two_way_margin": null,
    "value_legs": 7,
    "value_return_per_unit": -0.7129,
    "value_profit_units": -4.99,
    "level_gap": -0.0558,
    "level_ci": [
      -0.1124,
      0.0536
    ],
    "level_pass": true,
    "status": "INSUFFICIENT"
  },
  {
    "market": "dnb_home",
    "legs": 84,
    "still_needed": 216,
    "mean_probability": 0.5781,
    "mean_raw_probability": 0.5744,
    "actual_win_rate": 0.6548,
    "wilson_ci": [
      0.5483,
      0.7477
    ],
    "betpawa_mean_implied": 0.5996,
    "mean_margin_vs_ours": 0.0215,
    "mean_two_way_margin": 0.0502,
    "value_legs": 8,
    "value_return_per_unit": 0.4175,
    "value_profit_units": 3.34,
    "level_gap": 0.0766,
    "level_ci": [
      -0.074,
      0.1283
    ],
    "level_pass": true,
    "status": "INSUFFICIENT"
  },
  {
    "market": "dnb_away",
    "legs": 84,
    "still_needed": 216,
    "mean_probability": 0.4219,
    "mean_raw_probability": 0.4256,
    "actual_win_rate": 0.3452,
    "wilson_ci": [
      0.2523,
      0.4517
    ],
    "betpawa_mean_implied": 0.4506,
    "mean_margin_vs_ours": 0.0287,
    "mean_two_way_margin": 0.0502,
    "value_legs": 10,
    "value_return_per_unit": 0.202,
    "value_profit_units": 2.02,
    "level_gap": -0.0766,
    "level_ci": [
      -0.1346,
      0.0685
    ],
    "level_pass": true,
    "status": "INSUFFICIENT"
  }
]
```
