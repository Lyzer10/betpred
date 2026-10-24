"""Per-market model weights vs one global weight (Premier League, blended mode).

Live today: one model-vs-market weight for every market. If the model is strong on some
markets (e.g. home 1Up) and weak on others (e.g. away 1Up), a weight per market should help.
Walk-forward: for each test season the weights are learned on all earlier seasons
(validation 2021/22-2023/24 plus earlier test seasons), then scored on that season.
Usage: python -m src.market_weight_study
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .accumulators import SLIP_MARKETS, _log_loss, blend, build_validation_leg_table, fit_model_weight
from .leagues import paths

FOCUS = ["home_1up", "away_1up", "over_1.5", "over_2.5", "under_3.5", "home_win", "away_win",
         "double_1x", "double_x2", "double_12"]


def run(league: str = "EPL") -> pd.DataFrame:
    validation = build_validation_leg_table(league)
    test = pd.read_parquet(paths(league).accumulator_legs)
    columns = ["season", "date", "market", "model_probability", "bookmaker_probability", "won"]
    legs = pd.concat([validation[columns], test[columns]], ignore_index=True).dropna(subset=["bookmaker_probability"])
    legs = legs[legs.market.isin(SLIP_MARKETS)]
    rows = []
    for season in sorted(test.season.unique()):
        history, current = legs[legs.season < season], legs[legs.season == season]
        global_weight = fit_model_weight(history)
        for market in FOCUS:
            h, c = history[history.market == market], current[current.market == market]
            if c.empty or h.empty:
                continue
            market_weight = fit_model_weight(h)
            for name, weight in (("market only", 0.0), ("global weight", global_weight), ("per-market weight", market_weight)):
                probability = blend(c.model_probability, c.bookmaker_probability, weight)
                rows.append({"season": season, "market": market, "approach": name, "weight": weight,
                             "n": len(c), "loss_sum": _log_loss(probability, c.won) * len(c)})
    frame = pd.DataFrame(rows)
    table = frame.groupby(["market", "approach"]).agg(n=("n", "sum"), loss=("loss_sum", "sum"),
                                                      weight=("weight", "last"))
    table["log_loss"] = table.loss / table.n
    return table[["n", "weight", "log_loss"]]


if __name__ == "__main__":
    table = run("EPL")
    pivot = table.log_loss.unstack()
    pivot["per-market better by"] = pivot["global weight"] - pivot["per-market weight"]
    print(pivot.round(4).to_string())
    print("\nLatest per-market weights:")
    print(table.weight.unstack()["per-market weight"].round(2).to_string())
    total = table.reset_index().assign(loss=lambda d: d.log_loss * d.n).groupby("approach")[["loss", "n"]].sum()
    print("\nAll focus markets combined:", (total.loss / total.n).round(5).to_dict())
