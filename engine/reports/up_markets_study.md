# Double Chance 1UP and 1X2 2UP study (PROJECT.md task 17, pre-registered 2026-11-07)

Five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`), seasons 2014/15 onwards (`matches.parquet` and `goals.parquet`).
Matches missing average odds or failing exact goal-count reconciliation with `goals.parquet` are dropped (never filled).

## Settlement definitions confirmed from real Betpawa events (Part A & Task 17 correction)
- `dc1up_1x`: wins if the home team led at any point (`home - away >= 1`) OR full-time result is home win or draw (`home >= away`).
- `dc1up_x2`: wins if the away team led at any point (`away - home >= 1`) OR full-time result is away win or draw (`away >= home`).
- `dc1up_12`: wins if either team led at any point OR full-time result is not a draw (equivalently, `home + away > 0`).
- `home_2up`: wins if the home team was ever two goals ahead (`home - away >= 2`) OR the home team won at full time (`home > away`).
- `away_2up`: wins if the away team was ever two goals ahead (`away - home >= 2`) OR the away team won at full time (`away > home`).

### Real Betpawa price inequality verification across all 9 leagues (fetched 2026-11-07)
| League | Event ID | Match | 1X2 `1` / `2` | 2UP `1` / `2` | DC `1X` / `X2` / `12` | DC 1UP `1X` / `X2` / `12` |
|---|---|---|---|---|---|---|
| EPL | 38945042 | Arsenal FC - Hull City | 1.16 / 19.96 | 1.14 / 19.86 | 1.01 / 4.82 / 1.10 | susp (0.0) / 3.47 / susp (0.0) |
| LALIGA | 37360154 | Espanyol Barcelona - RC Deportivo de A Coruna | 2.58 / 3.00 | 2.49 / 2.89 | 1.41 / 1.53 / 1.35 | 1.30 / 1.38 / 1.05 |
| SERIEA | 38292840 | Torino FC - US Lecce | 1.82 / 4.77 | 1.77 / 4.57 | 1.21 / 1.99 / 1.29 | 1.16 / 1.66 / 1.03 |
| BUNDES | 38336446 | SC Paderborn 07 - Eintracht Frankfurt | 2.87 / 2.42 | 2.70 / 2.29 | 1.58 / 1.44 / 1.29 | 1.38 / 1.29 / 1.01 |
| LIGUE1 | 38916210 | AJ Auxerre - Paris FC | 4.76 / 1.76 | 4.54 / 1.71 | 2.09 / 1.20 / 1.26 | 1.70 / 1.15 / 1.03 |
| EREDIV | 38395807 | Fortuna Sittard - SC Telstar | 2.15 / 3.53 | 2.07 / 3.35 | 1.31 / 1.69 / 1.29 | 1.20 / 1.44 / 1.02 |
| JUPILER | 38366400 | KVC Westerlo - Royal Charleroi SC | 3.09 / 2.30 | 2.92 / 2.20 | 1.63 / 1.39 / 1.29 | 1.42 / 1.26 / 1.02 |
| PRIMEIRA | 38916889 | Nacional da Madeira - Academico de Viseu FC | 3.11 / 2.50 | 3.01 / 2.41 | 1.56 / 1.39 / 1.33 | 1.40 / 1.29 / 1.03 |
| SUPERLIG | 37359120 | Goztepe Izmir - Istanbul Basaksehir | 2.03 / 3.75 | 1.96 / 3.55 | 1.29 / 1.78 / 1.27 | 1.19 / 1.50 / 1.03 |

## Exact goal-order enumeration checks on small scores
| Score (h-a) | Total orders | Orders reaching +2 (`P(lead >= 2 given score)`) | `home_2up` weight `[1 if h > a else P(lead >= 2 given score)]` | Enumerated orders (running `home - away`) |
|---|---:|---:|---:|---|
| 1-0 | 1 | 0/1 (0.0000) | 1.0000 | `H` ([1], >=2: False) |
| 2-1 | 3 | 1/3 (0.3333) | 1.0000 | `HHA` ([1, 2, 1], >=2: True); `HAH` ([1, 0, 1], >=2: False); `AHH` ([-1, 0, 1], >=2: False) |
| 3-1 | 4 | 4/4 (1.0000) | 1.0000 | `HHHA` ([1, 2, 3, 2], >=2: True); `HHAH` ([1, 2, 1, 2], >=2: True); `HAHH` ([1, 0, 1, 2], >=2: True); `AHHH` ([-1, 0, 1, 2], >=2: True) |
| 1-3 | 4 | 0/4 (0.0000) | 0.0000 | `HAAA` ([1, 0, -1, -2], >=2: False); `AHAA` ([-1, 0, -1, -2], >=2: False); `AAHA` ([-1, -2, -1, -2], >=2: False); `AAAH` ([-1, -2, -3, -2], >=2: False) |
| 2-2 | 6 | 1/6 (0.1667) | 0.1667 | `HHAA` ([1, 2, 1, 0], >=2: True); `HAHA` ([1, 0, 1, 0], >=2: False); `HAAH` ([1, 0, -1, 0], >=2: False); `AHHA` ([-1, 0, 1, 0], >=2: False); `AHAH` ([-1, 0, -1, 0], >=2: False); `AAHH` ([-1, -2, -1, 0], >=2: False) |
| 2-3 | 10 | 1/10 (0.1000) | 0.1000 | `HHAAA` ([1, 2, 1, 0, -1], >=2: True); `HAHAA` ([1, 0, 1, 0, -1], >=2: False); `HAAHA` ([1, 0, -1, 0, -1], >=2: False); `HAAAH` ([1, 0, -1, -2, -1], >=2: False); `AHHAA` ([-1, 0, 1, 0, -1], >=2: False); `AHAHA` ([-1, 0, -1, 0, -1], >=2: False); ... (10 total) |
| 3-3 | 20 | 6/20 (0.3000) | 0.3000 | `HHHAAA` ([1, 2, 3, 2, 1, 0], >=2: True); `HHAHAA` ([1, 2, 1, 2, 1, 0], >=2: True); `HHAAHA` ([1, 2, 1, 0, 1, 0], >=2: True); `HHAAAH` ([1, 2, 1, 0, -1, 0], >=2: True); `HAHHAA` ([1, 0, 1, 2, 1, 0], >=2: True); `HAHAHA` ([1, 0, 1, 0, 1, 0], >=2: False); ... (20 total) |

## Walk-forward evaluation on 2024/25+ (`market_gates.evaluate` unchanged)
| League | Market | n | Said | Won | Fair odds | Gates | Eligibility |
|---|---|---:|---:|---:|---:|---|---|
| EPL | dc1up_1x | 830 | 0.7410 | 0.7398 | 1.31 | **PASS** | eligible pending real Betpawa prices |
| EPL | dc1up_x2 | 830 | 0.6305 | 0.6627 | 1.55 | **PASS** | eligible pending real Betpawa prices |
| EPL | dc1up_12 | 830 | 0.9462 | 0.9422 | 1.06 | **PASS** | eligible pending real Betpawa prices |
| EPL | home_2up | 830 | 0.4680 | 0.4337 | 2.19 | **FAIL** | stays out |
| EPL | away_2up | 830 | 0.3418 | 0.3434 | 3.10 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | dc1up_1x | 805 | 0.7572 | 0.7801 | 1.29 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | dc1up_x2 | 805 | 0.6192 | 0.6037 | 1.57 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | dc1up_12 | 805 | 0.9209 | 0.9453 | 1.09 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | home_2up | 805 | 0.4628 | 0.4807 | 2.27 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | away_2up | 805 | 0.3027 | 0.3006 | 3.58 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | dc1up_1x | 803 | 0.7351 | 0.7173 | 1.30 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | dc1up_x2 | 803 | 0.6530 | 0.6588 | 1.49 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | dc1up_12 | 803 | 0.9202 | 0.9191 | 1.09 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | home_2up | 803 | 0.4234 | 0.4159 | 2.45 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | away_2up | 803 | 0.3381 | 0.3624 | 3.25 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | dc1up_1x | 638 | 0.7542 | 0.7429 | 1.30 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | dc1up_x2 | 638 | 0.6220 | 0.6458 | 1.57 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | dc1up_12 | 638 | 0.9475 | 0.9404 | 1.05 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | home_2up | 638 | 0.4754 | 0.4561 | 2.17 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | away_2up | 638 | 0.3251 | 0.3589 | 3.23 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | dc1up_1x | 638 | 0.7340 | 0.7304 | 1.31 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | dc1up_x2 | 638 | 0.6408 | 0.6254 | 1.53 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | dc1up_12 | 638 | 0.9430 | 0.9342 | 1.06 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | home_2up | 638 | 0.4559 | 0.4718 | 2.21 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | away_2up | 638 | 0.3452 | 0.3386 | 3.10 | **PASS** | eligible pending real Betpawa prices |

Summary: **24 PASS / 1 FAIL** across 25 league x market pairs.

Match reconciliation coverage by league:
```json
{
  "EPL": {
    "total_rows": 4630,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 0,
    "kept_rows": 4630
  },
  "LALIGA": {
    "total_rows": 4649,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 45,
    "kept_rows": 4604
  },
  "SERIEA": {
    "total_rows": 4630,
    "dropped_missing_odds": 2,
    "dropped_unreconciled_goals": 28,
    "kept_rows": 4600
  },
  "BUNDES": {
    "total_rows": 3726,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 29,
    "kept_rows": 3697
  },
  "LIGUE1": {
    "total_rows": 4300,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 41,
    "kept_rows": 4259
  }
}
```

Gate details:
```json
[
  {
    "league": "EPL",
    "market": "dc1up_1x",
    "n": 830,
    "status": "PASS",
    "C1_slope": 1.05,
    "C1_ci": [
      0.825,
      1.275
    ],
    "C1": true,
    "C2_level": -0.0012,
    "C2_ci": [
      -0.0293,
      0.0258
    ],
    "C2": true,
    "C3_min_z": -1.56,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0008,
    "logloss_vs_book_ci": [
      -0.0033,
      0.0016
    ],
    "mean_p": 0.741,
    "actual": 0.7398,
    "fair_odds": 1.31,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "EPL",
    "market": "dc1up_x2",
    "n": 830,
    "status": "PASS",
    "C1_slope": 0.952,
    "C1_ci": [
      0.732,
      1.172
    ],
    "C1": true,
    "C2_level": 0.0321,
    "C2_ci": [
      -0.0016,
      0.0651
    ],
    "C2": true,
    "C3_min_z": -0.03,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0006,
    "logloss_vs_book_ci": [
      -0.0018,
      0.0007
    ],
    "mean_p": 0.6305,
    "actual": 0.6627,
    "fair_odds": 1.55,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "EPL",
    "market": "dc1up_12",
    "n": 830,
    "status": "PASS",
    "C1_slope": 0.847,
    "C1_ci": [
      0.027,
      1.667
    ],
    "C1": true,
    "C2_level": -0.004,
    "C2_ci": [
      -0.0205,
      0.0127
    ],
    "C2": true,
    "C3_min_z": -1.7,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0002,
    "logloss_vs_book_ci": [
      -0.001,
      0.0016
    ],
    "mean_p": 0.9462,
    "actual": 0.9422,
    "fair_odds": 1.06,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "EPL",
    "market": "home_2up",
    "n": 830,
    "status": "FAIL",
    "C1_slope": 1.048,
    "C1_ci": [
      0.844,
      1.251
    ],
    "C1": true,
    "C2_level": -0.0343,
    "C2_ci": [
      -0.0657,
      -0.0041
    ],
    "C2": false,
    "C3_min_z": -1.8,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0005,
    "logloss_vs_book_ci": [
      -0.0009,
      0.0018
    ],
    "mean_p": 0.468,
    "actual": 0.4337,
    "fair_odds": 2.19,
    "eligibility": "stays out"
  },
  {
    "league": "EPL",
    "market": "away_2up",
    "n": 830,
    "status": "PASS",
    "C1_slope": 0.986,
    "C1_ci": [
      0.782,
      1.191
    ],
    "C1": true,
    "C2_level": 0.0015,
    "C2_ci": [
      -0.0308,
      0.0321
    ],
    "C2": true,
    "C3_min_z": -0.88,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0001,
    "logloss_vs_book_ci": [
      -0.001,
      0.0013
    ],
    "mean_p": 0.3418,
    "actual": 0.3434,
    "fair_odds": 3.1,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LALIGA",
    "market": "dc1up_1x",
    "n": 805,
    "status": "PASS",
    "C1_slope": 1.103,
    "C1_ci": [
      0.851,
      1.355
    ],
    "C1": true,
    "C2_level": 0.023,
    "C2_ci": [
      -0.0032,
      0.0517
    ],
    "C2": true,
    "C3_min_z": -0.43,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0039,
    "logloss_vs_book_ci": [
      -0.0069,
      -0.0009
    ],
    "mean_p": 0.7572,
    "actual": 0.7801,
    "fair_odds": 1.29,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LALIGA",
    "market": "dc1up_x2",
    "n": 805,
    "status": "PASS",
    "C1_slope": 1.072,
    "C1_ci": [
      0.85,
      1.293
    ],
    "C1": true,
    "C2_level": -0.0155,
    "C2_ci": [
      -0.0432,
      0.0145
    ],
    "C2": true,
    "C3_min_z": -1.5,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0014,
    "logloss_vs_book_ci": [
      -0.0044,
      0.0018
    ],
    "mean_p": 0.6192,
    "actual": 0.6037,
    "fair_odds": 1.57,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LALIGA",
    "market": "dc1up_12",
    "n": 805,
    "status": "PASS",
    "C1_slope": 1.354,
    "C1_ci": [
      0.529,
      2.179
    ],
    "C1": true,
    "C2_level": 0.0245,
    "C2_ci": [
      0.0091,
      0.0402
    ],
    "C2": true,
    "C3_min_z": -1.7,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0002,
    "logloss_vs_book_ci": [
      -0.0009,
      0.0005
    ],
    "mean_p": 0.9209,
    "actual": 0.9453,
    "fair_odds": 1.09,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LALIGA",
    "market": "home_2up",
    "n": 805,
    "status": "PASS",
    "C1_slope": 1.159,
    "C1_ci": [
      0.941,
      1.377
    ],
    "C1": true,
    "C2_level": 0.018,
    "C2_ci": [
      -0.0125,
      0.0472
    ],
    "C2": true,
    "C3_min_z": -1.5,
    "C3": true,
    "C4_lifted_legs": 79,
    "C4_z": 1.73,
    "C4": true,
    "logloss_vs_book": -0.0031,
    "logloss_vs_book_ci": [
      -0.0056,
      -0.0005
    ],
    "mean_p": 0.4628,
    "actual": 0.4807,
    "fair_odds": 2.27,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LALIGA",
    "market": "away_2up",
    "n": 805,
    "status": "PASS",
    "C1_slope": 1.049,
    "C1_ci": [
      0.83,
      1.268
    ],
    "C1": true,
    "C2_level": -0.002,
    "C2_ci": [
      -0.0318,
      0.0269
    ],
    "C2": true,
    "C3_min_z": -1.61,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0016,
    "logloss_vs_book_ci": [
      -0.0048,
      0.0015
    ],
    "mean_p": 0.3027,
    "actual": 0.3006,
    "fair_odds": 3.58,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "SERIEA",
    "market": "dc1up_1x",
    "n": 803,
    "status": "PASS",
    "C1_slope": 1.119,
    "C1_ci": [
      0.908,
      1.33
    ],
    "C1": true,
    "C2_level": -0.0178,
    "C2_ci": [
      -0.0475,
      0.0134
    ],
    "C2": true,
    "C3_min_z": -1.29,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0029,
    "logloss_vs_book_ci": [
      -0.0063,
      0.0007
    ],
    "mean_p": 0.7351,
    "actual": 0.7173,
    "fair_odds": 1.3,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "SERIEA",
    "market": "dc1up_x2",
    "n": 803,
    "status": "PASS",
    "C1_slope": 0.945,
    "C1_ci": [
      0.75,
      1.14
    ],
    "C1": true,
    "C2_level": 0.0058,
    "C2_ci": [
      -0.0242,
      0.0354
    ],
    "C2": true,
    "C3_min_z": -1.82,
    "C3": true,
    "C4_lifted_legs": 407,
    "C4_z": 0.05,
    "C4": true,
    "logloss_vs_book": -0.0022,
    "logloss_vs_book_ci": [
      -0.0073,
      0.0027
    ],
    "mean_p": 0.653,
    "actual": 0.6588,
    "fair_odds": 1.49,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "SERIEA",
    "market": "dc1up_12",
    "n": 803,
    "status": "PASS",
    "C1_slope": 1.364,
    "C1_ci": [
      0.39,
      2.339
    ],
    "C1": true,
    "C2_level": -0.0011,
    "C2_ci": [
      -0.0212,
      0.0175
    ],
    "C2": true,
    "C3_min_z": -2.11,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0001,
    "logloss_vs_book_ci": [
      -0.0013,
      0.0015
    ],
    "mean_p": 0.9202,
    "actual": 0.9191,
    "fair_odds": 1.09,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "SERIEA",
    "market": "home_2up",
    "n": 803,
    "status": "PASS",
    "C1_slope": 1.014,
    "C1_ci": [
      0.83,
      1.199
    ],
    "C1": true,
    "C2_level": -0.0074,
    "C2_ci": [
      -0.0359,
      0.0231
    ],
    "C2": true,
    "C3_min_z": -1.38,
    "C3": true,
    "C4_lifted_legs": 61,
    "C4_z": -0.49,
    "C4": true,
    "logloss_vs_book": -0.0032,
    "logloss_vs_book_ci": [
      -0.0077,
      0.0019
    ],
    "mean_p": 0.4234,
    "actual": 0.4159,
    "fair_odds": 2.45,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "SERIEA",
    "market": "away_2up",
    "n": 803,
    "status": "PASS",
    "C1_slope": 1.026,
    "C1_ci": [
      0.839,
      1.213
    ],
    "C1": true,
    "C2_level": 0.0243,
    "C2_ci": [
      -0.0091,
      0.0575
    ],
    "C2": true,
    "C3_min_z": -0.38,
    "C3": true,
    "C4_lifted_legs": 185,
    "C4_z": 1.74,
    "C4": true,
    "logloss_vs_book": -0.0034,
    "logloss_vs_book_ci": [
      -0.0076,
      0.0008
    ],
    "mean_p": 0.3381,
    "actual": 0.3624,
    "fair_odds": 3.25,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "BUNDES",
    "market": "dc1up_1x",
    "n": 638,
    "status": "PASS",
    "C1_slope": 1.135,
    "C1_ci": [
      0.863,
      1.406
    ],
    "C1": true,
    "C2_level": -0.0113,
    "C2_ci": [
      -0.0408,
      0.0192
    ],
    "C2": true,
    "C3_min_z": -1.63,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": -0.0001,
    "logloss_vs_book_ci": [
      -0.002,
      0.0019
    ],
    "mean_p": 0.7542,
    "actual": 0.7429,
    "fair_odds": 1.3,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "BUNDES",
    "market": "dc1up_x2",
    "n": 638,
    "status": "PASS",
    "C1_slope": 1.338,
    "C1_ci": [
      1.035,
      1.64
    ],
    "C1": true,
    "C2_level": 0.0238,
    "C2_ci": [
      -0.0136,
      0.0579
    ],
    "C2": true,
    "C3_min_z": -1.23,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.003,
    "logloss_vs_book_ci": [
      0.001,
      0.0051
    ],
    "mean_p": 0.622,
    "actual": 0.6458,
    "fair_odds": 1.57,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "BUNDES",
    "market": "dc1up_12",
    "n": 638,
    "status": "PASS",
    "C1_slope": 1.174,
    "C1_ci": [
      0.384,
      1.965
    ],
    "C1": true,
    "C2_level": -0.0071,
    "C2_ci": [
      -0.0265,
      0.0102
    ],
    "C2": true,
    "C3_min_z": -1.25,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0001,
    "logloss_vs_book_ci": [
      -0.0024,
      0.0028
    ],
    "mean_p": 0.9475,
    "actual": 0.9404,
    "fair_odds": 1.05,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "BUNDES",
    "market": "home_2up",
    "n": 638,
    "status": "PASS",
    "C1_slope": 1.398,
    "C1_ci": [
      1.111,
      1.684
    ],
    "C1": true,
    "C2_level": -0.0193,
    "C2_ci": [
      -0.0554,
      0.0169
    ],
    "C2": true,
    "C3_min_z": -2.19,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0029,
    "logloss_vs_book_ci": [
      0.001,
      0.0049
    ],
    "mean_p": 0.4754,
    "actual": 0.4561,
    "fair_odds": 2.17,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "BUNDES",
    "market": "away_2up",
    "n": 638,
    "status": "PASS",
    "C1_slope": 0.924,
    "C1_ci": [
      0.69,
      1.157
    ],
    "C1": true,
    "C2_level": 0.0339,
    "C2_ci": [
      -0.0034,
      0.0714
    ],
    "C2": true,
    "C3_min_z": -1.05,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0022,
    "logloss_vs_book_ci": [
      0.0002,
      0.0041
    ],
    "mean_p": 0.3251,
    "actual": 0.3589,
    "fair_odds": 3.23,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LIGUE1",
    "market": "dc1up_1x",
    "n": 638,
    "status": "PASS",
    "C1_slope": 0.922,
    "C1_ci": [
      0.686,
      1.158
    ],
    "C1": true,
    "C2_level": -0.0035,
    "C2_ci": [
      -0.0382,
      0.0311
    ],
    "C2": true,
    "C3_min_z": -1.2,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0002,
    "logloss_vs_book_ci": [
      -0.0031,
      0.0039
    ],
    "mean_p": 0.734,
    "actual": 0.7304,
    "fair_odds": 1.31,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LIGUE1",
    "market": "dc1up_x2",
    "n": 638,
    "status": "PASS",
    "C1_slope": 0.893,
    "C1_ci": [
      0.662,
      1.124
    ],
    "C1": true,
    "C2_level": -0.0154,
    "C2_ci": [
      -0.0501,
      0.0207
    ],
    "C2": true,
    "C3_min_z": -1.9,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0012,
    "logloss_vs_book_ci": [
      -0.0018,
      0.0043
    ],
    "mean_p": 0.6408,
    "actual": 0.6254,
    "fair_odds": 1.53,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LIGUE1",
    "market": "dc1up_12",
    "n": 638,
    "status": "PASS",
    "C1_slope": 1.187,
    "C1_ci": [
      0.212,
      2.161
    ],
    "C1": true,
    "C2_level": -0.0089,
    "C2_ci": [
      -0.0314,
      0.0119
    ],
    "C2": true,
    "C3_min_z": -2.51,
    "C3": true,
    "C4_lifted_legs": 0,
    "C4_z": null,
    "C4": true,
    "logloss_vs_book": 0.0006,
    "logloss_vs_book_ci": [
      -0.0027,
      0.0044
    ],
    "mean_p": 0.943,
    "actual": 0.9342,
    "fair_odds": 1.06,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LIGUE1",
    "market": "home_2up",
    "n": 638,
    "status": "PASS",
    "C1_slope": 0.904,
    "C1_ci": [
      0.693,
      1.115
    ],
    "C1": true,
    "C2_level": 0.0159,
    "C2_ci": [
      -0.0213,
      0.0517
    ],
    "C2": true,
    "C3_min_z": -0.67,
    "C3": true,
    "C4_lifted_legs": 81,
    "C4_z": 0.27,
    "C4": true,
    "logloss_vs_book": 0.0004,
    "logloss_vs_book_ci": [
      -0.0029,
      0.0041
    ],
    "mean_p": 0.4559,
    "actual": 0.4718,
    "fair_odds": 2.21,
    "eligibility": "eligible pending real Betpawa prices"
  },
  {
    "league": "LIGUE1",
    "market": "away_2up",
    "n": 638,
    "status": "PASS",
    "C1_slope": 0.956,
    "C1_ci": [
      0.727,
      1.184
    ],
    "C1": true,
    "C2_level": -0.0067,
    "C2_ci": [
      -0.0388,
      0.0316
    ],
    "C2": true,
    "C3_min_z": -1.36,
    "C3": true,
    "C4_lifted_legs": 56,
    "C4_z": -0.71,
    "C4": true,
    "logloss_vs_book": 0.0001,
    "logloss_vs_book_ci": [
      -0.0024,
      0.0028
    ],
    "mean_p": 0.3452,
    "actual": 0.3386,
    "fair_odds": 3.1,
    "eligibility": "eligible pending real Betpawa prices"
  }
]
```
