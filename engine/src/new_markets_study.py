"""Candidate slip markets: team over 0.5 / 1.5 goals and Draw No Bet. Pre-registered in PROJECT.md
(task 10), 2026-10-29, before any result.

- Matches: all five leagues, 2014/15 onwards, with the bookmaker average 1X2 and over/under 2.5.
- Raw probability: the score matrix the prices imply (`accumulators.bookmaker_implied`, league rho):
  home/away over 0.5 = P(team scores >= 1), over 1.5 = P(>= 2); Draw No Bet home/away =
  P(win) / (P(home) + P(away)), scored on matches that were not drawn (a draw refunds the stake).
- Calibrated probability (what slips would use, as market mode): Platt per league x market
  (`LogisticRegression(C=1.0)` on logit(raw), like `accumulators._platt_market`), fitted on earlier
  seasons only.
- Judged with the task-1 gates unchanged (`market_gates.evaluate`, one-sided C1-C4, >= 300 legs) on
  2024/25 onwards, with `bookmaker_probability` = the raw matrix probability (so C4 checks the
  calibrator's lifts).
- Decision: a league x market that PASSES may enter slips (after implementation and Betpawa price
  logging); FAIL or INSUFFICIENT stays out. Reported, not deciding: the raw matrix calibration, the
  typical fair odds of each market, and log loss of calibrated vs raw.
Usage: python -m src.new_markets_study   (writes reports/new_markets_study.md)
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .accumulators import bookmaker_implied
from .calibration import ENGINE_DIR
from .leagues import paths
from .market_gates import evaluate
from .market_live import league_rho

REPORT_PATH = ENGINE_DIR / "reports" / "new_markets_study.md"
LEAGUES = ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1")
MARKETS = ("home_over_0.5", "away_over_0.5", "home_over_1.5", "away_over_1.5", "dnb_home", "dnb_away")
JUDGED_FROM, SEED = "2024/25", 20261029
ODDS = ["avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25"]


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def raw_legs(matches: pd.DataFrame, league: str, rho: float) -> pd.DataFrame:
    matches = matches.dropna(subset=ODDS + ["home_goals", "away_goals"])
    rows = []
    for m in matches.itertuples(index=False):
        fair, _, matrix = bookmaker_implied(*(getattr(m, c) for c in ODDS), rho)
        home_goals, away_goals = matrix.sum(axis=1), matrix.sum(axis=0)     # rows = home goals
        base = {"league": league, "match_id": str(m.match_id), "date": m.date, "season": m.season}
        values = {"home_over_0.5": (1 - home_goals[0], m.home_goals >= 1),
                  "away_over_0.5": (1 - away_goals[0], m.away_goals >= 1),
                  "home_over_1.5": (1 - home_goals[:2].sum(), m.home_goals >= 2),
                  "away_over_1.5": (1 - away_goals[:2].sum(), m.away_goals >= 2)}
        if m.home_goals != m.away_goals:             # Draw No Bet: a draw is a refund, not a result
            share = fair["home_win"] + fair["away_win"]
            values["dnb_home"] = (fair["home_win"] / share, m.home_goals > m.away_goals)
            values["dnb_away"] = (fair["away_win"] / share, m.away_goals > m.home_goals)
        rows += [base | {"market": k, "bookmaker_probability": float(p), "won": int(w)} for k, (p, w) in values.items()]
    return pd.DataFrame(rows)


def calibrate_walk_forward(legs: pd.DataFrame) -> pd.DataFrame:
    legs = legs.copy()
    legs["probability"] = np.nan
    for (league, market), group in legs.groupby(["league", "market"]):
        for season in sorted(group.season.unique())[1:]:
            history, current = group[group.season < season], group.index[group.season == season]
            model = LogisticRegression(C=1.0, max_iter=1000).fit(_logit(history.bookmaker_probability).reshape(-1, 1), history.won)
            legs.loc[current, "probability"] = model.predict_proba(
                _logit(legs.loc[current, "bookmaker_probability"]).reshape(-1, 1))[:, 1]
    return legs


def main() -> None:
    legs = pd.concat([raw_legs(pd.read_parquet(paths(l).matches), l, league_rho(l)) for l in LEAGUES], ignore_index=True)
    legs = calibrate_walk_forward(legs)
    judged = legs[legs.season >= JUDGED_FROM]
    rng = np.random.default_rng(SEED)
    lines = ["# New markets study (PROJECT.md task 10, pre-registered 2026-10-29)", "",
             "| League | Market | n | Said | Won | Fair odds | Gates | Raw matrix gates |", "|---|---|---|---|---|---|---|---|"]
    results = []
    for league in LEAGUES:
        for market in MARKETS:
            d = judged[(judged.league == league)]
            r = evaluate(league, market, d, "probability", rng)
            raw = evaluate(league, market, d.assign(raw=d.bookmaker_probability), "raw", rng)
            m = d[d.market == market]
            results.append(r | {"raw_status": raw["status"]})
            lines.append(f"| {league} | {market} | {r['n']} | {r.get('mean_p', float('nan')):.3f} | "
                         f"{r.get('actual', float('nan')):.3f} | {float((1 / m.probability).median()):.2f} | "
                         f"**{r['status']}** | {raw['status']} |")
    lines += ["", "Details:", "```", json.dumps(results, indent=1, default=str), "```"]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:4 + len(results)]))


if __name__ == "__main__":
    main()
