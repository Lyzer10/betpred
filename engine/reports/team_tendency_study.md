# Team tendency study (PROJECT.md task 8, pre-registered 2026-10-29)

## lead: home_1up, away_1up

- Primary (bookmaker price, seasons 2017/18+): 32910 legs, log loss gain -0.00009 (95% CI -0.00018 to -0.00000)
- Per league gain: {'BUNDES': -0.00013, 'EPL': 0.0, 'LALIGA': -6e-05, 'LIGUE1': -0.00015, 'SERIEA': -0.00013}
- Secondary (live probabilities, last 40% of days 2024/25+): 2910 legs, gain -0.00044 (95% CI -0.00080 to -0.00009)
- Season-to-season persistence of a team's residual: r = 0.016 (886 team pairs)
- Coefficients [const, logit p, away, r_for, r_against] by season: {'2017/18': [0.065, 1.079, -0.083, -0.042, 0.34], '2018/19': [0.048, 1.099, -0.058, -0.112, -0.015], '2019/20': [0.037, 1.1, -0.044, -0.145, 0.021], '2020/21': [0.032, 1.103, -0.015, -0.101, -0.109], '2021/22': [0.016, 1.103, 0.019, -0.208, -0.163], '2022/23': [0.019, 1.096, 0.02, -0.237, -0.194], '2023/24': [0.026, 1.09, 0.009, -0.176, 0.059], '2024/25': [0.019, 1.109, 0.025, -0.188, 0.026], '2025/26': [0.012, 1.116, 0.047, -0.132, 0.036], '2026/27': [-0.006, 1.112, 0.049, -0.173, 0.036]}
- Secondary coefficients: [-0.155, 0.972, 0.126, 0.032, 0.248]
- **Decision: DO NOT USE**

## win: home_win, away_win

- Primary (bookmaker price, seasons 2017/18+): 32910 legs, log loss gain -0.00004 (95% CI -0.00013 to +0.00005)
- Per league gain: {'BUNDES': 4e-05, 'EPL': -0.00016, 'LALIGA': -2e-05, 'LIGUE1': -0.0, 'SERIEA': -5e-05}
- Secondary (live probabilities, last 40% of days 2024/25+): 2930 legs, gain -0.00336 (95% CI -0.00618 to -0.00070)
- Season-to-season persistence of a team's residual: r = 0.021 (886 team pairs)
- Coefficients [const, logit p, away, r_for, r_against] by season: {'2017/18': [0.106, 1.102, -0.072, -0.283, 0.205], '2018/19': [0.082, 1.105, -0.034, -0.254, 0.015], '2019/20': [0.067, 1.101, -0.028, -0.253, -0.153], '2020/21': [0.056, 1.085, -0.018, -0.22, -0.087], '2021/22': [0.035, 1.085, 0.02, -0.199, -0.135], '2022/23': [0.026, 1.084, 0.027, -0.276, -0.154], '2023/24': [0.035, 1.075, 0.003, -0.156, -0.012], '2024/25': [0.031, 1.097, 0.019, -0.121, -0.049], '2025/26': [0.022, 1.106, 0.047, -0.281, 0.057], '2026/27': [0.024, 1.11, 0.044, -0.276, -0.06]}
- Secondary coefficients: [-0.006, 1.11, 0.152, -2.233, 0.215]
- **Decision: DO NOT USE**
