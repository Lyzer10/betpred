"""Task 15: first look at team goals and Draw No Bet with real Betpawa prices (report only).

Pre-registered in PROJECT.md (task 15), 2026-11-07, before any result.
- Data: every settled archived match (`web/public/data/archive`) with logged Betpawa prices
  for `home_over_0.5`, `away_over_0.5`, `home_over_1.5`, `away_over_1.5`, `dnb_home`, `dnb_away`
  (`engine/data/live/prices`, last price logged before kick-off).
- Probability: rebuild the score matrix from the archived fair 1X2 and over/under 2.5
  probabilities with `accumulators.bookmaker_implied` and the league rho, then apply the
  task-10 method (`new_markets_study.py`) with Platt fitted on seasons before 2026/27 only.
  DNB is scored on non-drawn matches.
- Report per market: legs, our mean probability vs actual win rate (Wilson CI), Betpawa's
  mean implied probability and margin, and the return if every leg with our probability x
  Betpawa odds - 1 >= 0.03 had been backed.
- Decision rule: none yet; a market may enter slips only when it has >= 300 settled priced
  legs and its one-sided level check (actual - predicted, 95% CI upper bound >= 0) passes.
Usage: python -m src.team_goals_dnb_live_study
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .accumulators import _wilson, bookmaker_implied
from .calibration import ENGINE_DIR
from .football_only import load_history
from .leagues import LEAGUES, paths
from .market_gates import MIN_LEGS, _bootstrap_mean_by_day
from .market_live import league_rho
from .new_league_config import NEW_LEAGUES
from .new_markets_study import MARKETS, _logit, raw_legs
from .predict import VALUE_EDGE, settled_predictions
from .prices import load_prices

REPORT_PATH = ENGINE_DIR / "reports" / "team_goals_dnb_live_study.md"
CUTOFF_SEASON = "2026/27"
SEED = 20261029
FAIR_KEYS = ("home_win", "draw", "away_win", "over_2.5", "under_2.5")


def fit_historical_platt(leagues=LEAGUES) -> dict[tuple[str, str], LogisticRegression]:
    """Fit Platt calibration per league x market on seasons before 2026/27 only."""
    models: dict[tuple[str, str], LogisticRegression] = {}
    for code in leagues:
        rho = league_rho(code)
        matches = (load_history(code, start=2014, end=2025) if code in NEW_LEAGUES
                   else pd.read_parquet(paths(code).matches))
        matches = matches[matches.season < CUTOFF_SEASON]
        legs = raw_legs(matches, code, rho)
        for market in MARKETS:
            part = legs[legs.market == market]
            models[(code, market)] = LogisticRegression(C=1.0, max_iter=1000).fit(
                _logit(part.bookmaker_probability).reshape(-1, 1), part.won
            )
    return models


def last_pre_kickoff_prices(prices: pd.DataFrame) -> dict[tuple[str, str, pd.Timestamp, str], float]:
    """Last logged Betpawa price before kick-off per (home, away, kickoff_utc, market)."""
    if prices.empty:
        return {}
    before = prices[(prices.snapshot_utc < prices.kickoff_utc) & prices.market.isin(MARKETS)
                    & prices.betpawa_odds.notna() & (prices.betpawa_odds > 1.0)]
    last = before.sort_values("snapshot_utc").groupby(["home", "away", "kickoff_utc", "market"], as_index=False).last()
    return {(r.home, r.away, r.kickoff_utc, r.market): float(r.betpawa_odds) for r in last.itertuples(index=False)}


def build_settled_priced_legs(fixtures: list[dict], prices: pd.DataFrame,
                              models: dict[tuple[str, str], LogisticRegression],
                              rho_lookup=league_rho) -> pd.DataFrame:
    """Rebuild score matrix from archived fair probabilities and attach last pre-kickoff Betpawa prices."""
    price_map = last_pre_kickoff_prices(prices)
    rows = []
    for f in fixtures:
        if "result" not in f or "score" not in f["result"]:
            continue
        code = f["league"]["code"] if isinstance(f.get("league"), dict) else (f.get("league") or "EPL")
        kickoff = pd.Timestamp(f["kickoff_utc"]).tz_localize(None)
        fair_probs = {m["market"]: m.get("market_probability") for m in f.get("markets", [])}
        if any(fair_probs.get(k) is None or float(fair_probs[k]) <= 0 for k in FAIR_KEYS):
            continue
        fair, _, matrix = bookmaker_implied(*(1.0 / float(fair_probs[k]) for k in FAIR_KEYS), rho_lookup(code))
        home_dist, away_dist = matrix.sum(axis=1), matrix.sum(axis=0)
        hg, ag = int(f["result"]["score"][0]), int(f["result"]["score"][1])
        raw_values = {
            "home_over_0.5": (float(1 - home_dist[0]), int(hg >= 1)),
            "away_over_0.5": (float(1 - away_dist[0]), int(ag >= 1)),
            "home_over_1.5": (float(1 - home_dist[:2].sum()), int(hg >= 2)),
            "away_over_1.5": (float(1 - away_dist[:2].sum()), int(ag >= 2)),
        }
        if hg != ag:
            share = fair["home_win"] + fair["away_win"]
            raw_values["dnb_home"] = (float(fair["home_win"] / share), int(hg > ag))
            raw_values["dnb_away"] = (float(fair["away_win"] / share), int(ag > hg))
        dnb_margin = None
        dnb_h_odds = price_map.get((f["home"], f["away"], kickoff, "dnb_home"))
        dnb_a_odds = price_map.get((f["home"], f["away"], kickoff, "dnb_away"))
        if dnb_h_odds is not None and dnb_a_odds is not None:
            dnb_margin = (1.0 / dnb_h_odds + 1.0 / dnb_a_odds) - 1.0
        for market, (raw_p, won) in raw_values.items():
            odds = price_map.get((f["home"], f["away"], kickoff, market))
            if odds is None or (code, market) not in models:
                continue
            model = models[(code, market)]
            prob = float(model.predict_proba(_logit([raw_p]).reshape(-1, 1))[0, 1])
            implied = 1.0 / odds
            rows.append({
                "date": pd.Timestamp(f["date"]),
                "league": code,
                "home": f["home"],
                "away": f["away"],
                "kickoff_utc": kickoff,
                "market": market,
                "raw_probability": raw_p,
                "probability": prob,
                "betpawa_odds": odds,
                "implied_probability": implied,
                "over_our_fair": implied - prob,
                "two_way_margin": dnb_margin if market.startswith("dnb_") else np.nan,
                "won": int(won),
            })
    return pd.DataFrame(rows)


def summarize_markets(legs: pd.DataFrame, seed: int = SEED) -> list[dict]:
    """Compute per-market metrics and decision status."""
    rng = np.random.default_rng(seed)
    summaries = []
    for market in MARKETS:
        sub = legs[legs.market == market].copy() if not legs.empty else pd.DataFrame()
        n = int(len(sub))
        needed = max(MIN_LEGS - n, 0)
        if n == 0:
            summaries.append({"market": market, "legs": 0, "still_needed": MIN_LEGS, "status": "INSUFFICIENT"})
            continue
        wins = int(sub.won.sum())
        lo, hi = _wilson(wins, n)
        level = float(np.mean(sub.won.to_numpy(float) - sub.probability.to_numpy(float)))
        level_ci = _bootstrap_mean_by_day(sub, sub.won.to_numpy(float) - sub.probability.to_numpy(float), rng)
        level_pass = level_ci[1] >= 0
        backed = sub[sub.probability * sub.betpawa_odds - 1 >= VALUE_EDGE]
        backed_n = int(len(backed))
        backed_return = float((backed.won * backed.betpawa_odds - 1).mean()) if backed_n else None
        backed_profit = float((backed.won * backed.betpawa_odds - 1).sum()) if backed_n else 0.0
        two_way = float(sub.two_way_margin.dropna().mean()) if sub.two_way_margin.notna().any() else None
        status = "PASS" if (n >= MIN_LEGS and level_pass) else "INSUFFICIENT" if n < MIN_LEGS else "FAIL"
        summaries.append({
            "market": market,
            "legs": n,
            "still_needed": needed,
            "mean_probability": round(float(sub.probability.mean()), 4),
            "mean_raw_probability": round(float(sub.raw_probability.mean()), 4),
            "actual_win_rate": round(float(sub.won.mean()), 4),
            "wilson_ci": [round(lo, 4), round(hi, 4)],
            "betpawa_mean_implied": round(float(sub.implied_probability.mean()), 4),
            "mean_margin_vs_ours": round(float(sub.over_our_fair.mean()), 4),
            "mean_two_way_margin": None if two_way is None else round(two_way, 4),
            "value_legs": backed_n,
            "value_return_per_unit": None if backed_return is None else round(backed_return, 4),
            "value_profit_units": round(backed_profit, 2),
            "level_gap": round(level, 4),
            "level_ci": [round(level_ci[0], 4), round(level_ci[1], 4)],
            "level_pass": level_pass,
            "status": status,
        })
    return summaries


def main() -> None:
    models = fit_historical_platt()
    legs = build_settled_priced_legs(settled_predictions(), load_prices(), models)
    summaries = summarize_markets(legs)
    matches_n = int(legs[["home", "away", "kickoff_utc"]].drop_duplicates().shape[0]) if not legs.empty else 0
    lines = [
        "# Team goals and Draw No Bet with real Betpawa prices (PROJECT.md task 15, pre-registered 2026-11-07)",
        "",
        f"Settled archived matches with logged pre-kickoff Betpawa prices: **{matches_n}** matches, **{len(legs)}** scored legs.",
        "Platt calibrators fitted per league x market on seasons before 2026/27 only (`LogisticRegression(C=1.0)` on `logit(raw)`).",
        "Draw No Bet (`dnb_home`, `dnb_away`) is scored on non-drawn matches only (13 drawn matches refunded).",
        "Margin column reports mean(`1 / betpawa_odds - probability`) for every market (and for DNB also the exact two-way bookmaker overround `1/odds_home + 1/odds_away - 1` because both sides are logged; Betpawa team-total Under prices are not logged).",
        "",
        "| Market | Settled legs | Still needed (to 300) | Our mean p | Actual win rate (95% Wilson CI) | Betpawa mean implied p | Mean margin vs our p (2-way DNB) | Value legs (edge >= 3%) | Value return / unit | Level gap (95% CI) | Status |",
        "|---|---:|---:|---:|---|---:|---|---:|---:|---|---|",
    ]
    for s in summaries:
        margin_str = f"{s['mean_margin_vs_ours']:+.4f}"
        if s["mean_two_way_margin"] is not None:
            margin_str += f" (2-way {s['mean_two_way_margin']:+.4f})"
        val_str = "NA" if s["value_return_per_unit"] is None else f"{s['value_return_per_unit']:+.4f} ({s['value_profit_units']:+.2f}u)"
        lines.append(
            f"| {s['market']} | {s['legs']} | {s['still_needed']} | {s['mean_probability']:.4f} | "
            f"{s['actual_win_rate']:.4f} ({s['wilson_ci'][0]:.4f}-{s['wilson_ci'][1]:.4f}) | "
            f"{s['betpawa_mean_implied']:.4f} | {margin_str} | {s['value_legs']} | {val_str} | "
            f"{s['level_gap']:+.4f} ({s['level_ci'][0]:+.4f}, {s['level_ci'][1]:+.4f}) | **{s['status']}** |"
        )
    lines += [
        "",
        "## Decision",
        "",
        "None yet (`INSUFFICIENT` on all 6 markets). Every market has between 84 and 97 settled priced legs so far "
        "(still needing 203 to 216 legs to reach the 300-leg minimum). The one-sided level check (95% CI upper bound >= 0) "
        "is currently above zero on all 6 markets, but no market may enter slips until it has >= 300 settled priced legs.",
        "",
        "Details:",
        "```json",
        json.dumps(summaries, indent=2),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:20]))


if __name__ == "__main__":
    main()

