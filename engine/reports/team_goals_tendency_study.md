# Team goals tendency study: over 1.5 and over 2.5 (PROJECT.md task 26, pre-registered 2026-11-23)

Research only; no live changes. Evaluates whether teams have a lasting tendency to beat bookmaker over 1.5 or over 2.5 prices using each team's previous 38 league matches (home and away combined, minimum 10 matches, strictly no look-ahead).

## over_1.5

- Primary (bookmaker price, seasons 2017/18+, five leagues pooled): **16,455 matches** across 1,695 days, paired log-loss gain **-0.00002** (95% whole-day bootstrap CI **-0.00033 to +0.00031**, 2,000 resamples, seed `20261123`).
- Per-league primary gain: {'BUNDES': -0.00038, 'EPL': -0.0003, 'LALIGA': 0.00047, 'LIGUE1': 7e-05, 'SERIEA': -0.0}
- Secondary (live probabilities, last 40% of days 2024/25+): **1,422 matches** across 161 days, gain **-0.00061** (95% CI **-0.00190 to +0.00065**).
- Season-to-season persistence of a team's residual (>= 30 matches/season): **r = 0.004** (886 team-season pairs).
- Primary coefficients `[const, logit(p), r_home, r_away]` by season: {'2017/18': [-0.041, 1.081, 0.958, -0.538], '2018/19': [-0.081, 1.074, 0.781, 0.011], '2019/20': [-0.055, 1.054, 0.521, -0.256], '2020/21': [-0.051, 1.063, 0.539, -0.44], '2021/22': [-0.017, 1.041, 0.778, -0.276], '2022/23': [-0.011, 1.031, 0.565, -0.251], '2023/24': [-0.006, 1.025, 0.616, -0.257], '2024/25': [-0.034, 1.055, 0.739, -0.317], '2025/26': [-0.019, 1.042, 0.724, -0.378], '2026/27': [-0.018, 1.04, 0.618, -0.422]}
- Secondary coefficients `[const, logit(p), r_home, r_away]`: [0.15, 0.858, 0.717, -0.539]
- **Decision: DO NOT USE**

## over_2.5

- Primary (bookmaker price, seasons 2017/18+, five leagues pooled): **16,455 matches** across 1,695 days, paired log-loss gain **-0.00018** (95% whole-day bootstrap CI **-0.00039 to +0.00001**, 2,000 resamples, seed `20261123`).
- Per-league primary gain: {'BUNDES': 0.00021, 'EPL': 0.00025, 'LALIGA': -0.00047, 'LIGUE1': -0.00058, 'SERIEA': -0.00029}
- Secondary (live probabilities, last 40% of days 2024/25+): **1,466 matches** across 161 days, gain **-0.00011** (95% CI **-0.00089 to +0.00066**).
- Season-to-season persistence of a team's residual (>= 30 matches/season): **r = 0.085** (886 team-season pairs).
- Primary coefficients `[const, logit(p), r_home, r_away]` by season: {'2017/18': [0.082, 1.223, -0.358, -0.716], '2018/19': [0.039, 1.197, -0.258, -0.185], '2019/20': [0.029, 1.127, -0.22, -0.196], '2020/21': [0.032, 1.141, -0.043, -0.126], '2021/22': [0.026, 1.094, 0.155, -0.081], '2022/23': [0.018, 1.097, 0.144, -0.113], '2023/24': [0.015, 1.112, 0.081, -0.217], '2024/25': [0.016, 1.129, 0.13, -0.183], '2025/26': [0.013, 1.123, 0.15, -0.221], '2026/27': [0.014, 1.112, 0.1, -0.225]}
- Secondary coefficients `[const, logit(p), r_home, r_away]`: [-0.012, 0.98, 0.276, -0.217]
- **Decision: DO NOT USE**

## Interpretation of social-media 'profitable team' claims

Both `over_1.5` and `over_2.5` fail the pre-registered out-of-sample test (**DO NOT USE**). Lists of teams claimed on social media to be 'profitable' for over 1.5 or over 2.5 goals are in-sample artefacts (cherry-picking teams that happened to beat the odds in a past window); bookmaker prices already incorporate teams' lasting scoring rates, so past residuals do not reliably beat the odds out of sample. Their claimed figures are not reproduced here.

## What was NOT checked

- Smaller leagues outside the five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`) were not included.
- Window lengths other than 38 league matches (or home-only / away-only rolling splits) were not searched to avoid post-hoc tuning.
- Bookmaker prices are football-data average opening/pre-match odds rather than Betpawa live odds or closing lines.
