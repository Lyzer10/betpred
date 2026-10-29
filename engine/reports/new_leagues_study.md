# New leagues study

Fixed median live-league rho: -0.054288.

## ESPN settlement evidence

Real completed responses from `/scoreboard?dates=20261025`:

- `ned.1`: event 401875570, STATUS_FULL_TIME, Fortuna Sittard 1–0 Excelsior.
- `bel.1`: event 401878963, STATUS_FULL_TIME, Racing Genk 2–1 Standard Liege.
- `por.1`: event 401885418, STATUS_FULL_TIME, Estoril 1–3 Moreirense.
- `tur.1`: event 401888266, STATUS_FULL_TIME, Konyaspor 2–0 Genclerbirligi.

Raw responses are cached alongside the season downloads. The broad date-range request returned
HTTP 400; the single-date requests above succeeded. No scores or fixture values were filled.

## Eredivisie: READY

Markets passing: 7/8. Betpawa Netherlands competitions: [{"id": "12125", "name": "Eredivisie", "slug": "eredivisie", "priority": 1200, "preferred": false}].
ESPN: https://site.api.espn.com/apis/site/v2/sports/soccer/ned.1/scoreboard; 5 events. Example: Fortuna Sittard at Feyenoord Rotterdam

| Season | Played | Complete odds | Source columns |
|---|---:|---:|---|
| 2014/15 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2015/16 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2016/17 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2017/18 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2018/19 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2019/20 | 232 | 232 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2020/21 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2021/22 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2022/23 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2023/24 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2024/25 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2025/26 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2026/27 | 90 | 89 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |

| Market | N | Status | Predicted | Actual |
|---|---:|---|---:|---:|
| home_win | 701 | PASS | 0.4527 | 0.4322 |
| away_win | 701 | PASS | 0.3167 | 0.3081 |
| double_1x | 701 | PASS | 0.6833 | 0.6919 |
| double_x2 | 701 | PASS | 0.5473 | 0.5678 |
| double_12 | 701 | FAIL | 0.7696 | 0.7404 |
| over_0.5 | 701 | PASS | 0.9521 | 0.9672 |
| over_1.5 | 701 | PASS | 0.8281 | 0.8474 |
| over_2.5 | 701 | PASS | 0.6038 | 0.6034 |

Gate details: [{"league": "N1", "market": "home_win", "n": 701, "status": "PASS", "C1_slope": 0.877, "C1_ci": [0.693, 1.06], "C1": true, "C2_level": -0.0204, "C2_ci": [-0.0547, 0.0115], "C2": true, "C3_min_z": -1.57, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": 0.001, "logloss_vs_book_ci": [-0.0017, 0.0038], "mean_p": 0.4527, "actual": 0.4322}, {"league": "N1", "market": "away_win", "n": 701, "status": "PASS", "C1_slope": 1.072, "C1_ci": [0.864, 1.279], "C1": true, "C2_level": -0.0086, "C2_ci": [-0.0404, 0.0208], "C2": true, "C3_min_z": -1.21, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0016, "logloss_vs_book_ci": [-0.0041, 0.0009], "mean_p": 0.3167, "actual": 0.3081}, {"league": "N1", "market": "double_1x", "n": 701, "status": "PASS", "C1_slope": 1.072, "C1_ci": [0.864, 1.279], "C1": true, "C2_level": 0.0086, "C2_ci": [-0.0212, 0.0405], "C2": true, "C3_min_z": -0.73, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0016, "logloss_vs_book_ci": [-0.0041, 0.0009], "mean_p": 0.6833, "actual": 0.6919}, {"league": "N1", "market": "double_x2", "n": 701, "status": "PASS", "C1_slope": 0.877, "C1_ci": [0.693, 1.06], "C1": true, "C2_level": 0.0204, "C2_ci": [-0.0096, 0.052], "C2": true, "C3_min_z": -2.06, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": 0.001, "logloss_vs_book_ci": [-0.0016, 0.0037], "mean_p": 0.5473, "actual": 0.5678}, {"league": "N1", "market": "double_12", "n": 701, "status": "FAIL", "C1_slope": 0.881, "C1_ci": [0.267, 1.494], "C1": true, "C2_level": -0.0292, "C2_ci": [-0.059, -0.0002], "C2": false, "C3_min_z": -2.62, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0009, "logloss_vs_book_ci": [-0.0018, 0.0], "mean_p": 0.7696, "actual": 0.7404}, {"league": "N1", "market": "over_0.5", "n": 701, "status": "PASS", "C1_slope": 1.252, "C1_ci": [-0.107, 2.61], "C1": true, "C2_level": 0.0151, "C2_ci": [0.0032, 0.0286], "C2": true, "C3_min_z": -1.28, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0014, "logloss_vs_book_ci": [-0.0024, -0.0003], "mean_p": 0.9521, "actual": 0.9672}, {"league": "N1", "market": "over_1.5", "n": 701, "status": "PASS", "C1_slope": 1.525, "C1_ci": [0.899, 2.151], "C1": true, "C2_level": 0.0193, "C2_ci": [-0.006, 0.0448], "C2": true, "C3_min_z": -0.77, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0026, "logloss_vs_book_ci": [-0.0044, -0.0008], "mean_p": 0.8281, "actual": 0.8474}, {"league": "N1", "market": "over_2.5", "n": 701, "status": "PASS", "C1_slope": 0.967, "C1_ci": [0.535, 1.398], "C1": true, "C2_level": -0.0004, "C2_ci": [-0.0362, 0.0371], "C2": true, "C3_min_z": -1.49, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0001, "logloss_vs_book_ci": [-0.0018, 0.0017], "mean_p": 0.6038, "actual": 0.6034}]

## Belgian Pro League: READY

Markets passing: 8/8. Betpawa Belgium competitions: [{"id": "12128", "name": "Pro League", "slug": "pro-league", "priority": 1200, "preferred": false}].
ESPN: https://site.api.espn.com/apis/site/v2/sports/soccer/bel.1/scoreboard; 1 events. Example: Club Brugge at Zulte-Waregem

| Season | Played | Complete odds | Source columns |
|---|---:|---:|---|
| 2014/15 | 240 | 240 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2015/16 | 240 | 240 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2016/17 | 240 | 240 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2017/18 | 240 | 240 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2018/19 | 240 | 240 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2019/20 | 232 | 232 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2020/21 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2021/22 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2022/23 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2023/24 | 312 | 312 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2024/25 | 312 | 312 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2025/26 | 311 | 311 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2026/27 | 80 | 80 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |

| Market | N | Status | Predicted | Actual |
|---|---:|---|---:|---:|
| home_win | 703 | PASS | 0.4353 | 0.4324 |
| away_win | 703 | PASS | 0.3168 | 0.3058 |
| double_1x | 703 | PASS | 0.6832 | 0.6942 |
| double_x2 | 703 | PASS | 0.5647 | 0.5676 |
| double_12 | 703 | PASS | 0.7516 | 0.7383 |
| over_0.5 | 703 | PASS | 0.9388 | 0.9218 |
| over_1.5 | 703 | PASS | 0.7841 | 0.7639 |
| over_2.5 | 703 | PASS | 0.5536 | 0.522 |

Gate details: [{"league": "B1", "market": "home_win", "n": 703, "status": "PASS", "C1_slope": 1.232, "C1_ci": [0.971, 1.493], "C1": true, "C2_level": -0.0028, "C2_ci": [-0.0387, 0.0341], "C2": true, "C3_min_z": -1.59, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0015, "logloss_vs_book_ci": [-0.0031, 0.0001], "mean_p": 0.4353, "actual": 0.4324}, {"league": "B1", "market": "away_win", "n": 703, "status": "PASS", "C1_slope": 1.008, "C1_ci": [0.757, 1.258], "C1": true, "C2_level": -0.011, "C2_ci": [-0.0435, 0.0227], "C2": true, "C3_min_z": -2.41, "C3": true, "C4_lifted_legs": 46, "C4_z": null, "C4": true, "logloss_vs_book": -0.0002, "logloss_vs_book_ci": [-0.0029, 0.0025], "mean_p": 0.3168, "actual": 0.3058}, {"league": "B1", "market": "double_1x", "n": 703, "status": "PASS", "C1_slope": 1.008, "C1_ci": [0.757, 1.258], "C1": true, "C2_level": 0.011, "C2_ci": [-0.0265, 0.0452], "C2": true, "C3_min_z": -1.2, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0002, "logloss_vs_book_ci": [-0.0027, 0.0024], "mean_p": 0.6832, "actual": 0.6942}, {"league": "B1", "market": "double_x2", "n": 703, "status": "PASS", "C1_slope": 1.232, "C1_ci": [0.971, 1.493], "C1": true, "C2_level": 0.0028, "C2_ci": [-0.0343, 0.0387], "C2": true, "C3_min_z": -1.8, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0015, "logloss_vs_book_ci": [-0.0031, 0.0003], "mean_p": 0.5647, "actual": 0.5676}, {"league": "B1", "market": "double_12", "n": 703, "status": "PASS", "C1_slope": 1.255, "C1_ci": [0.446, 2.064], "C1": true, "C2_level": -0.0134, "C2_ci": [-0.0432, 0.0158], "C2": true, "C3_min_z": -2.46, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0002, "logloss_vs_book_ci": [-0.0016, 0.0014], "mean_p": 0.7516, "actual": 0.7383}, {"league": "B1", "market": "over_0.5", "n": 703, "status": "PASS", "C1_slope": 1.435, "C1_ci": [0.42, 2.45], "C1": true, "C2_level": -0.017, "C2_ci": [-0.0362, 0.0026], "C2": true, "C3_min_z": -2.55, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": 0.001, "logloss_vs_book_ci": [-0.0003, 0.0027], "mean_p": 0.9388, "actual": 0.9218}, {"league": "B1", "market": "over_1.5", "n": 703, "status": "PASS", "C1_slope": 0.974, "C1_ci": [0.427, 1.522], "C1": true, "C2_level": -0.0203, "C2_ci": [-0.049, 0.0105], "C2": true, "C3_min_z": -1.28, "C3": true, "C4_lifted_legs": 4, "C4_z": null, "C4": true, "logloss_vs_book": -0.0001, "logloss_vs_book_ci": [-0.0028, 0.0031], "mean_p": 0.7841, "actual": 0.7639}, {"league": "B1", "market": "over_2.5", "n": 703, "status": "PASS", "C1_slope": 1.077, "C1_ci": [0.559, 1.595], "C1": true, "C2_level": -0.0316, "C2_ci": [-0.073, 0.0069], "C2": true, "C3_min_z": -1.6, "C3": true, "C4_lifted_legs": 44, "C4_z": null, "C4": true, "logloss_vs_book": 0.0009, "logloss_vs_book_ci": [-0.0016, 0.0035], "mean_p": 0.5536, "actual": 0.522}]

## Primeira Liga: READY

Markets passing: 7/8. Betpawa Portugal competitions: [{"id": "12124", "name": "Liga Portugal", "slug": "liga-portugal", "priority": 1200, "preferred": false}].
ESPN: https://site.api.espn.com/apis/site/v2/sports/soccer/por.1/scoreboard; 1 events. Example: Sporting CP at Casa Pia

| Season | Played | Complete odds | Source columns |
|---|---:|---:|---|
| 2014/15 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2015/16 | 306 | 305 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2016/17 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2017/18 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2018/19 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2019/20 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2020/21 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2021/22 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2022/23 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2023/24 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2024/25 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2025/26 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2026/27 | 81 | 81 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |

| Market | N | Status | Predicted | Actual |
|---|---:|---|---:|---:|
| home_win | 693 | FAIL | 0.4379 | 0.4156 |
| away_win | 693 | PASS | 0.3285 | 0.3247 |
| double_1x | 693 | PASS | 0.6715 | 0.6753 |
| double_x2 | 693 | PASS | 0.5621 | 0.5844 |
| double_12 | 693 | PASS | 0.768 | 0.7403 |
| over_0.5 | 693 | PASS | 0.9298 | 0.938 |
| over_1.5 | 693 | PASS | 0.7293 | 0.7417 |
| over_2.5 | 693 | PASS | 0.4927 | 0.5195 |

Gate details: [{"league": "P1", "market": "home_win", "n": 693, "status": "FAIL", "C1_slope": 0.914, "C1_ci": [0.746, 1.083], "C1": true, "C2_level": -0.0223, "C2_ci": [-0.0557, 0.0105], "C2": true, "C3_min_z": -2.0, "C3": true, "C4_lifted_legs": 235, "C4_z": -2.48, "C4": false, "logloss_vs_book": 0.0002, "logloss_vs_book_ci": [-0.0063, 0.0074], "mean_p": 0.4379, "actual": 0.4156}, {"league": "P1", "market": "away_win", "n": 693, "status": "PASS", "C1_slope": 0.97, "C1_ci": [0.792, 1.148], "C1": true, "C2_level": -0.0038, "C2_ci": [-0.0343, 0.0258], "C2": true, "C3_min_z": -1.13, "C3": true, "C4_lifted_legs": 140, "C4_z": -0.37, "C4": true, "logloss_vs_book": -0.0022, "logloss_vs_book_ci": [-0.0077, 0.0039], "mean_p": 0.3285, "actual": 0.3247}, {"league": "P1", "market": "double_1x", "n": 693, "status": "PASS", "C1_slope": 0.97, "C1_ci": [0.792, 1.148], "C1": true, "C2_level": 0.0038, "C2_ci": [-0.0261, 0.0347], "C2": true, "C3_min_z": -1.16, "C3": true, "C4_lifted_legs": 35, "C4_z": null, "C4": true, "logloss_vs_book": -0.0022, "logloss_vs_book_ci": [-0.0081, 0.0036], "mean_p": 0.6715, "actual": 0.6753}, {"league": "P1", "market": "double_x2", "n": 693, "status": "PASS", "C1_slope": 0.914, "C1_ci": [0.746, 1.083], "C1": true, "C2_level": 0.0223, "C2_ci": [-0.014, 0.0542], "C2": true, "C3_min_z": -0.92, "C3": true, "C4_lifted_legs": 130, "C4_z": -0.4, "C4": true, "logloss_vs_book": 0.0002, "logloss_vs_book_ci": [-0.007, 0.008], "mean_p": 0.5621, "actual": 0.5844}, {"league": "P1", "market": "double_12", "n": 693, "status": "PASS", "C1_slope": 0.807, "C1_ci": [0.461, 1.154], "C1": true, "C2_level": -0.0277, "C2_ci": [-0.0594, 0.0032], "C2": true, "C3_min_z": -2.04, "C3": true, "C4_lifted_legs": 219, "C4_z": -1.4, "C4": true, "logloss_vs_book": 0.0015, "logloss_vs_book_ci": [-0.0045, 0.0083], "mean_p": 0.768, "actual": 0.7403}, {"league": "P1", "market": "over_0.5", "n": 693, "status": "PASS", "C1_slope": 1.173, "C1_ci": [0.482, 1.865], "C1": true, "C2_level": 0.0081, "C2_ci": [-0.009, 0.0246], "C2": true, "C3_min_z": -1.7, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0042, "logloss_vs_book_ci": [-0.0073, -0.0002], "mean_p": 0.9298, "actual": 0.938}, {"league": "P1", "market": "over_1.5", "n": 693, "status": "PASS", "C1_slope": 1.467, "C1_ci": [0.926, 2.008], "C1": true, "C2_level": 0.0124, "C2_ci": [-0.0187, 0.0414], "C2": true, "C3_min_z": -1.18, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0001, "logloss_vs_book_ci": [-0.0018, 0.0016], "mean_p": 0.7293, "actual": 0.7417}, {"league": "P1", "market": "over_2.5", "n": 693, "status": "PASS", "C1_slope": 1.313, "C1_ci": [0.885, 1.742], "C1": true, "C2_level": 0.0267, "C2_ci": [-0.006, 0.0612], "C2": true, "C3_min_z": -1.17, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0013, "logloss_vs_book_ci": [-0.0027, -0.0001], "mean_p": 0.4927, "actual": 0.5195}]

## Super Lig: READY

Markets passing: 8/8. Betpawa Turkey competitions: [{"id": "12182", "name": "Super Lig", "slug": "super-lig", "priority": 1200, "preferred": false}].
ESPN: https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/scoreboard; 1 events. Example: Galatasaray at Konyaspor

| Season | Played | Complete odds | Source columns |
|---|---:|---:|---|
| 2014/15 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2015/16 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2016/17 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2017/18 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2018/19 | 306 | 306 | BbAvH, BbAvD, BbAvA, BbAv>2.5, BbAv<2.5 |
| 2019/20 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2020/21 | 420 | 420 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2021/22 | 380 | 380 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2022/23 | 342 | 313 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2023/24 | 380 | 380 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2024/25 | 342 | 342 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2025/26 | 306 | 306 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |
| 2026/27 | 81 | 81 | AvgH, AvgD, AvgA, Avg>2.5, Avg<2.5 |

| Market | N | Status | Predicted | Actual |
|---|---:|---|---:|---:|
| home_win | 729 | PASS | 0.4527 | 0.4582 |
| away_win | 729 | PASS | 0.3059 | 0.2908 |
| double_1x | 729 | PASS | 0.6941 | 0.7092 |
| double_x2 | 729 | PASS | 0.5473 | 0.5418 |
| double_12 | 729 | PASS | 0.7604 | 0.749 |
| over_0.5 | 729 | PASS | 0.9338 | 0.9218 |
| over_1.5 | 729 | PASS | 0.7751 | 0.7654 |
| over_2.5 | 729 | PASS | 0.5434 | 0.546 |

Gate details: [{"league": "T1", "market": "home_win", "n": 729, "status": "PASS", "C1_slope": 1.09, "C1_ci": [0.878, 1.302], "C1": true, "C2_level": 0.0054, "C2_ci": [-0.0294, 0.0396], "C2": true, "C3_min_z": -1.47, "C3": true, "C4_lifted_legs": 200, "C4_z": 0.4, "C4": true, "logloss_vs_book": -0.0037, "logloss_vs_book_ci": [-0.0078, 0.0012], "mean_p": 0.4527, "actual": 0.4582}, {"league": "T1", "market": "away_win", "n": 729, "status": "PASS", "C1_slope": 1.16, "C1_ci": [0.945, 1.375], "C1": true, "C2_level": -0.0151, "C2_ci": [-0.0425, 0.0155], "C2": true, "C3_min_z": -2.05, "C3": true, "C4_lifted_legs": 114, "C4_z": 0.48, "C4": true, "logloss_vs_book": -0.0089, "logloss_vs_book_ci": [-0.0153, -0.003], "mean_p": 0.3059, "actual": 0.2908}, {"league": "T1", "market": "double_1x", "n": 729, "status": "PASS", "C1_slope": 1.16, "C1_ci": [0.945, 1.375], "C1": true, "C2_level": 0.0151, "C2_ci": [-0.0128, 0.0414], "C2": true, "C3_min_z": -0.81, "C3": true, "C4_lifted_legs": 273, "C4_z": 1.23, "C4": true, "logloss_vs_book": -0.0089, "logloss_vs_book_ci": [-0.0148, -0.0028], "mean_p": 0.6941, "actual": 0.7092}, {"league": "T1", "market": "double_x2", "n": 729, "status": "PASS", "C1_slope": 1.09, "C1_ci": [0.878, 1.302], "C1": true, "C2_level": -0.0054, "C2_ci": [-0.0392, 0.0249], "C2": true, "C3_min_z": -1.71, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0037, "logloss_vs_book_ci": [-0.0082, 0.0012], "mean_p": 0.5473, "actual": 0.5418}, {"league": "T1", "market": "double_12", "n": 729, "status": "PASS", "C1_slope": 0.656, "C1_ci": [0.226, 1.087], "C1": true, "C2_level": -0.0114, "C2_ci": [-0.0432, 0.0193], "C2": true, "C3_min_z": -1.6, "C3": true, "C4_lifted_legs": 141, "C4_z": -0.56, "C4": true, "logloss_vs_book": 0.002, "logloss_vs_book_ci": [-0.0022, 0.0067], "mean_p": 0.7604, "actual": 0.749}, {"league": "T1", "market": "over_0.5", "n": 729, "status": "PASS", "C1_slope": 1.137, "C1_ci": [0.463, 1.812], "C1": true, "C2_level": -0.012, "C2_ci": [-0.0298, 0.0051], "C2": true, "C3_min_z": -2.22, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0011, "logloss_vs_book_ci": [-0.0033, 0.0013], "mean_p": 0.9338, "actual": 0.9218}, {"league": "T1", "market": "over_1.5", "n": 729, "status": "PASS", "C1_slope": 1.459, "C1_ci": [0.891, 2.026], "C1": true, "C2_level": -0.0096, "C2_ci": [-0.0392, 0.0174], "C2": true, "C3_min_z": -2.05, "C3": true, "C4_lifted_legs": 0, "C4_z": null, "C4": true, "logloss_vs_book": -0.0012, "logloss_vs_book_ci": [-0.0026, -0.0], "mean_p": 0.7751, "actual": 0.7654}, {"league": "T1", "market": "over_2.5", "n": 729, "status": "PASS", "C1_slope": 1.224, "C1_ci": [0.822, 1.627], "C1": true, "C2_level": 0.0025, "C2_ci": [-0.0306, 0.0377], "C2": true, "C3_min_z": -1.91, "C3": true, "C4_lifted_legs": 94, "C4_z": 0.79, "C4": true, "logloss_vs_book": -0.0028, "logloss_vs_book_ci": [-0.0059, 0.0004], "mean_p": 0.5434, "actual": 0.546}]
