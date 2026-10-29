import numpy as np
import pandas as pd

from src.team_tendency_study import add_features, primary


def synthetic(effect: float, seed: int = 1) -> pd.DataFrame:
    """20 teams, 8 seasons of double round robins; each team has a fixed lead tendency `effect` * +-1."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i}" for i in range(20)]
    tendency = dict(zip(teams, effect * rng.choice([-1, 1], size=20)))
    rows, match = [], 0
    for k, season in enumerate([f"{2014 + i}/{(15 + i) % 100:02d}" for i in range(8)]):
        start = pd.Timestamp(f"{2014 + k}-08-01")
        pairs = [(h, a) for h in teams for a in teams if h != a]
        rng.shuffle(pairs)
        for n, (home, away) in enumerate(pairs):
            date, match = start + pd.Timedelta(days=int(n // 10)), match + 1
            for side, team, opp in (("home", home, away), ("away", away, home)):
                p = rng.uniform(0.3, 0.7)
                z = np.log(p / (1 - p)) + tendency[team]
                won = float(rng.random() < 1 / (1 + np.exp(-z)))
                rows.append({"league": "X", "match_id": str(match), "date": date, "season": season, "side": side,
                             "team": team, "opp": opp, "lead_won": won, "lead_p": p, "win_won": won, "win_p": p})
    return pd.DataFrame(rows)


def test_finds_a_real_team_tendency():
    result = primary(add_features(synthetic(0.5)), "lead")
    assert result["ci"][0] > 0


def test_no_tendency_is_not_adopted():
    result = primary(add_features(synthetic(0.0)), "lead")
    assert result["ci"][0] <= 0
