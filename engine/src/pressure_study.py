"""Does shots+corners "pressure" (Wheatcroft 2020, GAP ratings) improve over/under 2.5?

Wheatcroft, E. (2020). A profitable model for predicting the over/under market in football.
International Journal of Forecasting. Ratings of attacking/defensive pressure built from
shots + corners feed a logistic regression together with the bookmaker's implied probability.

Compared on the same matches, trained on 2017/18-2023/24 and scored on 2024/25 onwards:
  A  logit(market)
  B  logit(market) + logit(our Dixon-Coles blend)            (our current approach)
  C  logit(market) + pressure                                (the paper's approach)
  D  logit(market) + logit(our model) + pressure
Pressure uses only matches before kickoff. Usage: python -m src.pressure_study [LEAGUE]
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .fetch_results import parse_match_dates
from .leagues import get_league, paths
from .team_names import canonical_team

TRAIN_SEASONS = ("2017/18", "2023/24")
TEST_FROM = "2024/25"


def gap_ratings(frame: pd.DataFrame, lam: float = 0.2, phi1: float = 0.5, phi2: float = 0.5) -> pd.DataFrame:
    """Wheatcroft's GAP ratings (equations 1-2), recorded before each match. Input S = shots + corners."""
    ratings: dict[str, list[float]] = {}            # team -> [Ha, Hd, Aa, Ad]
    start = float(frame[["home_pressure", "away_pressure"]].stack().mean())
    rows = []
    for match in frame.sort_values("date").itertuples():
        hi = ratings.setdefault(match.home_team, [start] * 4)
        aj = ratings.setdefault(match.away_team, [start] * 4)
        rows.append({"match_key": match.match_key, "gap_total": hi[0] + hi[1] + aj[2] + aj[3]})
        sh, sa = match.home_pressure, match.away_pressure
        home_err = sh - (hi[0] + aj[3]) / 2          # home attack vs expectation
        away_err = sa - (aj[2] + hi[1]) / 2          # away attack vs expectation
        hi[0] = max(hi[0] + lam * phi1 * home_err, 0); hi[2] = max(hi[2] + lam * (1 - phi1) * home_err, 0)
        hi[1] = max(hi[1] + lam * phi1 * away_err, 0); hi[3] = max(hi[3] + lam * (1 - phi1) * away_err, 0)
        aj[2] = max(aj[2] + lam * phi2 * away_err, 0); aj[0] = max(aj[0] + lam * (1 - phi2) * away_err, 0)
        aj[3] = max(aj[3] + lam * phi2 * home_err, 0); aj[1] = max(aj[1] + lam * (1 - phi2) * home_err, 0)
    return pd.DataFrame(rows)


def load_pressure(league) -> pd.DataFrame:
    selected, p = get_league(league), paths(league)
    frames = []
    for path in sorted(p.football_data_dir.glob(f"{selected.football_data_code}_*.csv")):
        raw = pd.read_csv(path, encoding="latin-1")
        if not {"HS", "AS", "HC", "AC"} <= set(raw.columns):
            continue
        raw = raw.dropna(subset=["HomeTeam", "AwayTeam", "HS", "AS", "HC", "AC", "FTHG"])
        frames.append(pd.DataFrame({
            "date": parse_match_dates(raw.Date),
            "home_team": raw.HomeTeam.map(lambda n: canonical_team(n, selected)),
            "away_team": raw.AwayTeam.map(lambda n: canonical_team(n, selected)),
            "home_pressure": raw.HS + raw.HC, "away_pressure": raw.AS + raw.AC}))
    frame = pd.concat(frames, ignore_index=True)
    frame["match_key"] = frame.date.dt.strftime("%Y-%m-%d") + "|" + frame.home_team + "|" + frame.away_team
    return frame


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def study(league="EPL") -> pd.DataFrame:
    p = paths(league)
    matches = pd.read_parquet(p.matches)
    dc = pd.concat([pd.read_parquet(path) for path in (p.processed_dir / "predictions_dc_history.parquet", p.predictions_dc)
                    if path.exists()], ignore_index=True)
    dc = dc[dc.variant == "blend"][["match_id", "prob_over25"]].drop_duplicates("match_id")
    data = matches.merge(dc, on="match_id")
    data["match_key"] = data.date.dt.strftime("%Y-%m-%d") + "|" + data.home_team + "|" + data.away_team
    pressure = load_pressure(league)
    gap = gap_ratings(pressure)
    data = data.merge(gap, on="match_key", how="inner").dropna(subset=["avg_odds_over25", "avg_odds_under25"])
    inverse = 1 / data[["avg_odds_over25", "avg_odds_under25"]]
    data["market"] = inverse.avg_odds_over25 / inverse.sum(axis=1)
    data["over"] = (data.home_goals + data.away_goals > 2.5).astype(int)
    data["x_market"], data["x_model"] = _logit(data.market), _logit(data.prob_over25)
    data["x_gap"] = (data.gap_total - data.gap_total.mean()) / data.gap_total.std()
    train = data[(data.season >= TRAIN_SEASONS[0]) & (data.season <= TRAIN_SEASONS[1])]
    test = data[data.season >= TEST_FROM]
    variants = {"A market": ["x_market"], "B market+our model": ["x_market", "x_model"],
                "C market+pressure (paper)": ["x_market", "x_gap"], "D market+model+pressure": ["x_market", "x_model", "x_gap"]}
    rows = []
    for name, columns in variants.items():
        model = LogisticRegression(C=1e6, max_iter=1000).fit(train[columns], train.over)
        prob = np.clip(model.predict_proba(test[columns])[:, 1], 1e-6, 1 - 1e-6)
        loss = -np.mean(test.over * np.log(prob) + (1 - test.over) * np.log(1 - prob))
        rows.append({"variant": name, "log_loss": loss, "brier": np.mean((prob - test.over) ** 2),
                     "coefficients": dict(zip(columns, np.round(model.coef_[0], 3)))})
    result = pd.DataFrame(rows)
    result.attrs["n_train"], result.attrs["n_test"] = len(train), len(test)
    return result


if __name__ == "__main__":
    league = sys.argv[1] if len(sys.argv) > 1 else "EPL"
    result = study(league)
    print(f"{get_league(league).name}: trained on {result.attrs['n_train']} matches, tested on {result.attrs['n_test']}")
    print(result.to_string(index=False))
