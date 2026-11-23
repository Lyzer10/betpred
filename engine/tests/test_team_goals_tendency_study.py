"""Known-answer synthetic tests for PROJECT.md task 26 (team_goals_tendency_study)."""
from datetime import timedelta

import numpy as np
import pandas as pd

from src.team_goals_tendency_study import add_features, primary


def synthetic(effect: float, seed: int = 1) -> pd.DataFrame:
    """20 teams, 8 seasons of double round robins; each team has a fixed goals tendency `effect` * +-1."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i}" for i in range(20)]
    tendency = dict(zip(teams, effect * rng.choice([-1.0, 1.0], size=20)))
    rows, match = [], 0
    for k, season in enumerate([f"{2014 + i}/{(15 + i) % 100:02d}" for i in range(8)]):
        start = pd.Timestamp(f"{2014 + k}-08-01")
        pairs = [(h, a) for h in teams for a in teams if h != a]
        rng.shuffle(pairs)
        for n, (home, away) in enumerate(pairs):
            date, match = start + timedelta(days=int(n // 10)), match + 1
            p15 = rng.uniform(0.65, 0.85)
            p25 = rng.uniform(0.40, 0.65)
            z15 = np.log(p15 / (1 - p15)) + tendency[home] + tendency[away]
            z25 = np.log(p25 / (1 - p25)) + tendency[home] + tendency[away]
            w15 = float(rng.random() < 1 / (1 + np.exp(-z15)))
            w25 = float(rng.random() < 1 / (1 + np.exp(-z25)))
            rows.append({
                "league": "X", "match_id": str(match), "date": date, "season": season,
                "home_team": home, "away_team": away,
                "over_1.5_won": w15, "over_1.5_p": p15,
                "over_2.5_won": w25, "over_2.5_p": p25,
            })
    return pd.DataFrame(rows)


def test_finds_a_real_team_goals_tendency():
    data = add_features(synthetic(0.5, seed=7))
    assert primary(data, "over_1.5")["ci"][0] > 0
    assert primary(data, "over_2.5")["ci"][0] > 0


def test_no_tendency_is_not_adopted():
    data = add_features(synthetic(0.0, seed=7))
    assert primary(data, "over_1.5")["ci"][0] <= 0
    assert primary(data, "over_2.5")["ci"][0] <= 0


def test_no_lookahead_in_team_features():
    base = synthetic(0.0, seed=3)
    perturbed = base.copy()
    # Flip the very last match's outcomes; no earlier match's rolling features may change.
    last_idx = perturbed.index[-1]
    perturbed.loc[last_idx, "over_1.5_won"] = 1.0 - perturbed.loc[last_idx, "over_1.5_won"]
    perturbed.loc[last_idx, "over_2.5_won"] = 1.0 - perturbed.loc[last_idx, "over_2.5_won"]
    f1 = add_features(base)
    f2 = add_features(perturbed)
    for col in ("over_1.5_r_home", "over_1.5_r_away", "over_2.5_r_home", "over_2.5_r_away"):
        assert np.allclose(f1[col].to_numpy(), f2[col].to_numpy())
