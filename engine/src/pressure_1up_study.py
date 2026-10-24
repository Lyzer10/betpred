"""Does shots+corners pressure (Wheatcroft 2020 GAP ratings) improve 1Up predictions?

Trained on the validation seasons (2021/22-2023/24), scored on 2024/25 onwards, per league:
  A  logit(bookmaker 1Up probability)
  B  A + logit(our model's 1Up probability)
  C  A + pressure difference (expected attacking pressure of the side minus the opponent's)
  D  A + B + C
Usage: python -m src.pressure_1up_study
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .accumulators import build_validation_leg_table
from .leagues import paths
from .pressure_study import load_pressure


def gap_components(frame: pd.DataFrame, lam: float = 0.1, phi: float = 0.5) -> pd.DataFrame:
    """Expected home and away attacking pressure before each match (GAP ratings, Wheatcroft eq. 1-2)."""
    ratings: dict[str, list[float]] = {}
    start = float(frame[["home_pressure", "away_pressure"]].stack().mean())
    rows = []
    for m in frame.sort_values("date").itertuples():
        hi = ratings.setdefault(m.home_team, [start] * 4)    # [Ha, Hd, Aa, Ad]
        aj = ratings.setdefault(m.away_team, [start] * 4)
        home_exp, away_exp = (hi[0] + aj[3]) / 2, (aj[2] + hi[1]) / 2
        rows.append({"date_key": m.date.strftime("%Y-%m-%d"), "home_team": m.home_team, "away_team": m.away_team,
                     "pressure_diff": home_exp - away_exp})
        he, ae = m.home_pressure - home_exp, m.away_pressure - away_exp
        hi[0] = max(hi[0] + lam * phi * he, 0); hi[2] = max(hi[2] + lam * (1 - phi) * he, 0)
        hi[1] = max(hi[1] + lam * phi * ae, 0); hi[3] = max(hi[3] + lam * (1 - phi) * ae, 0)
        aj[2] = max(aj[2] + lam * phi * ae, 0); aj[0] = max(aj[0] + lam * (1 - phi) * ae, 0)
        aj[3] = max(aj[3] + lam * phi * he, 0); aj[1] = max(aj[1] + lam * (1 - phi) * he, 0)
    return pd.DataFrame(rows)


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def study(league: str) -> list[dict]:
    pressure = gap_components(load_pressure(league))
    legs = pd.concat([build_validation_leg_table(league), pd.read_parquet(paths(league).accumulator_legs)], ignore_index=True)
    legs["date_key"] = pd.to_datetime(legs.date).dt.strftime("%Y-%m-%d")
    legs = legs.merge(pressure, on=["date_key", "home_team", "away_team"], how="inner")
    out = []
    for market, sign in (("home_1up", 1), ("away_1up", -1)):
        d = legs[legs.market == market].dropna(subset=["bookmaker_probability", "model_probability"]).copy()
        d["x_book"], d["x_model"] = _logit(d.bookmaker_probability), _logit(d.model_probability)
        d["x_press"] = sign * d.pressure_diff / legs.pressure_diff.std()
        train, test = d[d.season <= "2023/24"], d[d.season >= "2024/25"]
        for name, cols in {"A book": ["x_book"], "B book+model": ["x_book", "x_model"],
                           "C book+pressure": ["x_book", "x_press"], "D all": ["x_book", "x_model", "x_press"]}.items():
            prob = LogisticRegression(C=1e6, max_iter=1000).fit(train[cols], train.won).predict_proba(test[cols])[:, 1]
            prob = np.clip(prob, 1e-6, 1 - 1e-6)
            out.append({"league": league, "market": market, "variant": name, "n_test": len(test),
                        "log_loss": float(-np.mean(test.won * np.log(prob) + (1 - test.won) * np.log(1 - prob)))})
    return out


if __name__ == "__main__":
    rows = []
    for league in ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1"):
        rows += study(league)
    table = pd.DataFrame(rows).pivot_table(index=["league", "market"], columns="variant", values="log_loss")
    print(table.round(4).to_string())
