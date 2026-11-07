"""Task 16: goals by half and win either half (backtest, all nine live leagues).

Pre-registered in PROJECT.md (task 16), 2026-11-07, before any result.
- Data: football-data season files 2014/15 onwards (FTHG/FTAG/HTHG/HTAG and the average odds
  as in `new_leagues_study.odds_columns`); five main leagues from their `matches.parquet`
  (`ht_home_goals`, `ht_away_goals` and `avg_odds_*`), the four new leagues from their cached
  raw CSVs. Drop matches missing any needed value; never fill.
- Raw probability: `lambda_home` and `lambda_away` from `bookmaker_implied` (league rho);
  first-half goal share `s` per league = mean first-half goals / mean total goals over EARLIER
  seasons only; each team's goals per half Poisson with mean `s * lambda` (first) and
  `(1 - s) * lambda` (second), independent.
- Markets: `fh_over_0.5`, `fh_over_1.5`, `sh_over_0.5`, `sh_over_1.5`, `home_win_either_half`,
  `away_win_either_half`.
- Calibration: Platt (`LogisticRegression(C=1.0)` on `logit(raw)`) per league x market,
  walk-forward by season.
- Judgement: `market_gates.evaluate` unchanged (one-sided C1-C4, >= 300 legs) on 2024/25
  onwards with `bookmaker_probability = raw`. A PASS pair is only "eligible pending real
  Betpawa prices" (same 300-leg rule as Part B); FAIL or INSUFFICIENT stays out. Report the
  typical fair odds.
Usage: python -m src.half_markets_study
"""
from __future__ import annotations

from io import StringIO
import json

import numpy as np
import pandas as pd
from scipy.stats import poisson
from sklearn.linear_model import LogisticRegression

from .accumulators import bookmaker_implied
from .calibration import ENGINE_DIR
from .fetch_results import parse_match_dates, season_code, season_label
from .leagues import LEAGUES, get_league, paths
from .market_gates import evaluate
from .market_live import league_rho
from .new_league_config import NEW_LEAGUES
from .new_leagues_study import CACHE, odds_columns
from .new_markets_study import ODDS, _logit

REPORT_PATH = ENGINE_DIR / "reports" / "half_markets_study.md"
MARKETS = (
    "fh_over_0.5", "fh_over_1.5",
    "sh_over_0.5", "sh_over_1.5",
    "home_win_either_half", "away_win_either_half",
)
JUDGED_FROM = "2024/25"
SEED = 20261029
MAX_HALF_GOALS = 15


def _poisson_win_prob(lam_team: float, lam_opp: float) -> float:
    """Exact P(X > Y) for independent X ~ Poisson(lam_team), Y ~ Poisson(lam_opp)."""
    k = np.arange(MAX_HALF_GOALS + 1)
    p_team = poisson.pmf(k, lam_team)
    p_opp = poisson.pmf(k, lam_opp)
    # P(X > Y) = sum_{x=1..K} p_team[x] * sum_{y=0..x-1} p_opp[y]
    cum_opp = np.concatenate(([0.0], np.cumsum(p_opp)[:-1]))
    return float(np.sum(p_team * cum_opp))


def half_market_raw_probabilities(lam_home: float, lam_away: float, share_fh: float) -> dict[str, float]:
    """Raw probabilities for half totals and win-either-half under independent Poisson halves."""
    lam_fh_h = share_fh * lam_home
    lam_fh_a = share_fh * lam_away
    lam_sh_h = (1.0 - share_fh) * lam_home
    lam_sh_a = (1.0 - share_fh) * lam_away
    lam_fh = lam_fh_h + lam_fh_a
    lam_sh = lam_sh_h + lam_sh_a

    fh_over_05 = 1.0 - np.exp(-lam_fh)
    fh_over_15 = 1.0 - np.exp(-lam_fh) * (1.0 + lam_fh)
    sh_over_05 = 1.0 - np.exp(-lam_sh)
    sh_over_15 = 1.0 - np.exp(-lam_sh) * (1.0 + lam_sh)

    p_home_fh = _poisson_win_prob(lam_fh_h, lam_fh_a)
    p_home_sh = _poisson_win_prob(lam_sh_h, lam_sh_a)
    p_away_fh = _poisson_win_prob(lam_fh_a, lam_fh_h)
    p_away_sh = _poisson_win_prob(lam_sh_a, lam_sh_h)

    return {
        "fh_over_0.5": float(fh_over_05),
        "fh_over_1.5": float(fh_over_15),
        "sh_over_0.5": float(sh_over_05),
        "sh_over_1.5": float(sh_over_15),
        "home_win_either_half": float(1.0 - (1.0 - p_home_fh) * (1.0 - p_home_sh)),
        "away_win_either_half": float(1.0 - (1.0 - p_away_fh) * (1.0 - p_away_sh)),
    }


def half_market_outcomes(fthg: int, ftag: int, hthg: int, htag: int) -> dict[str, int]:
    """Actual outcomes from full-time and half-time goals."""
    sh_h = fthg - hthg
    sh_a = ftag - htag
    fh_total = hthg + htag
    sh_total = sh_h + sh_a
    return {
        "fh_over_0.5": int(fh_total >= 1),
        "fh_over_1.5": int(fh_total >= 2),
        "sh_over_0.5": int(sh_total >= 1),
        "sh_over_1.5": int(sh_total >= 2),
        "home_win_either_half": int((hthg > htag) or (sh_h > sh_a)),
        "away_win_either_half": int((htag > hthg) or (sh_a > sh_h)),
    }


def load_league_matches(league: str) -> pd.DataFrame:
    """Load 2014/15+ matches with FTHG/FTAG/HTHG/HTAG and average odds, dropping any missing rows."""
    if league not in NEW_LEAGUES:
        frame = pd.read_parquet(paths(league).matches)
        needed = ["date", "season", "home_goals", "away_goals", "ht_home_goals", "ht_away_goals", *ODDS]
        valid = frame.dropna(subset=needed).copy()
        valid = valid[(valid[ODDS] > 0).all(axis=1) & (valid.home_goals >= valid.ht_home_goals)
                      & (valid.away_goals >= valid.ht_away_goals)]
        valid["date"] = pd.to_datetime(valid["date"])
        return valid.reset_index(drop=True)

    div = get_league(league).football_data_code
    rows = []
    for year in range(2014, 2027):
        code = season_code(year)
        csv_path = paths(league).football_csv(code)
        if not csv_path.exists():
            csv_path = CACHE / f"{div}_{code}.csv"
        raw = pd.read_csv(StringIO(csv_path.read_text(encoding="utf-8-sig", errors="replace")))
        cols = odds_columns(raw)
        if cols is None or not {"Date", "FTHG", "FTAG", "HTHG", "HTAG"} <= set(raw):
            continue
        sub = raw.dropna(subset=["Date", "FTHG", "FTAG", "HTHG", "HTAG", *cols]).copy()
        sub = sub[(sub[cols] > 0).all(axis=1) & (sub["FTHG"] >= sub["HTHG"]) & (sub["FTAG"] >= sub["HTAG"])]
        dates = parse_match_dates(sub["Date"])
        for idx, m in sub.iterrows():
            rows.append({
                "match_id": f"{league}:{year}:{idx}",
                "date": dates.loc[idx],
                "season": season_label(year),
                "home_goals": int(m["FTHG"]),
                "away_goals": int(m["FTAG"]),
                "ht_home_goals": int(m["HTHG"]),
                "ht_away_goals": int(m["HTAG"]),
                "avg_odds_home": float(m[cols[0]]),
                "avg_odds_draw": float(m[cols[1]]),
                "avg_odds_away": float(m[cols[2]]),
                "avg_odds_over25": float(m[cols[3]]),
                "avg_odds_under25": float(m[cols[4]]),
            })
    return pd.DataFrame(rows)


def build_league_legs(matches: pd.DataFrame, league: str, rho: float) -> tuple[pd.DataFrame, dict[str, float]]:
    """Build raw and walk-forward Platt-calibrated legs for one league."""
    matches = matches.sort_values("date").reset_index(drop=True)
    # Precompute implied lambdas once per match
    lambdas = [
        bookmaker_implied(*(getattr(m, c) for c in ODDS), rho)[1]
        for m in matches.itertuples(index=False)
    ]
    matches = matches.assign(
        lam_home=[x[0] for x in lambdas],
        lam_away=[x[1] for x in lambdas],
        fh_goals=matches.ht_home_goals + matches.ht_away_goals,
        ft_goals=matches.home_goals + matches.away_goals,
    )
    seasons = sorted(matches.season.unique())
    rows = []
    shares: dict[str, float] = {}
    # First season has no earlier seasons to compute s from; s is defined for season index >= 1
    for season in seasons[1:]:
        earlier = matches[matches.season < season]
        share_fh = float(earlier.fh_goals.mean() / earlier.ft_goals.mean())
        shares[season] = share_fh
        for m in matches[matches.season == season].itertuples(index=False):
            raw = half_market_raw_probabilities(m.lam_home, m.lam_away, share_fh)
            actual = half_market_outcomes(int(m.home_goals), int(m.away_goals), int(m.ht_home_goals), int(m.ht_away_goals))
            for market in MARKETS:
                rows.append({
                    "league": league,
                    "date": m.date,
                    "season": m.season,
                    "market": market,
                    "bookmaker_probability": raw[market],
                    "won": actual[market],
                })
    legs = pd.DataFrame(rows)
    legs["probability"] = np.nan
    cal_seasons = sorted(legs.season.unique())
    for season in cal_seasons[1:]:
        for market in MARKETS:
            past = legs[(legs.season < season) & (legs.market == market)]
            current = (legs.season == season) & (legs.market == market)
            model = LogisticRegression(C=1.0, max_iter=1000).fit(
                _logit(past.bookmaker_probability).reshape(-1, 1), past.won
            )
            legs.loc[current, "probability"] = model.predict_proba(
                _logit(legs.loc[current, "bookmaker_probability"]).reshape(-1, 1)
            )[:, 1]
    return legs, shares


def main() -> None:
    all_legs = []
    share_summary = {}
    for code in LEAGUES:
        matches = load_league_matches(code)
        legs, shares = build_league_legs(matches, code, league_rho(code))
        all_legs.append(legs)
        share_summary[code] = {"matches": len(matches), "share_2024_25": round(shares.get("2024/25", float("nan")), 4),
                               "share_2026_27": round(shares.get("2026/27", float("nan")), 4)}
        print(f"{code}: {len(matches)} valid matches, 2026/27 FH share {shares.get('2026/27', float('nan')):.4f}", flush=True)

    legs = pd.concat(all_legs, ignore_index=True)
    judged = legs[legs.season >= JUDGED_FROM]
    rng = np.random.default_rng(SEED)

    lines = [
        "# Goals by half and win either half study (PROJECT.md task 16, pre-registered 2026-11-07)",
        "",
        "All nine live leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`, `EREDIV`, `JUPILER`, `PRIMEIRA`, `SUPERLIG`), seasons 2014/15 onwards.",
        "First-half goal share `s` per league = `mean(HTHG + HTAG) / mean(FTHG + FTAG)` over earlier seasons only; each team's goals per half are independent Poisson with means `s * lambda` (1H) and `(1 - s) * lambda` (2H).",
        "Platt calibration (`LogisticRegression(C=1.0)` on `logit(raw)`) fitted per league x market on earlier seasons only; judged on 2024/25+ with `market_gates.evaluate` unchanged (`bookmaker_probability = raw`).",
        "A `PASS` pair is **eligible pending real Betpawa prices** (>= 300 settled priced legs and one-sided level check passing, as in task 15); `FAIL` or `INSUFFICIENT` stays out.",
        "",
        "| League | Market | n | Said | Won | Fair odds | Gates | Eligibility |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    results = []
    pass_count = 0
    for code in LEAGUES:
        d = judged[judged.league == code]
        for market in MARKETS:
            r = evaluate(code, market, d, "probability", rng)
            m = d[d.market == market]
            fair_odds = float((1.0 / m.probability).median())
            r["fair_odds"] = round(fair_odds, 2)
            elig = "eligible pending real Betpawa prices" if r["status"] == "PASS" else "stays out"
            r["eligibility"] = elig
            pass_count += int(r["status"] == "PASS")
            results.append(r)
            lines.append(
                f"| {code} | {market} | {r['n']} | {r.get('mean_p', float('nan')):.4f} | "
                f"{r.get('actual', float('nan')):.4f} | {fair_odds:.2f} | **{r['status']}** | {elig} |"
            )

    lines += [
        "",
        f"Summary: **{pass_count} PASS / {len(results) - pass_count} FAIL** across {len(results)} league x market pairs.",
        "",
        "First-half goal shares by league:",
        "```json",
        json.dumps(share_summary, indent=2),
        "```",
        "",
        "Gate details:",
        "```json",
        json.dumps(results, indent=1, default=str),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Summary: {pass_count}/{len(results)} PASS. Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()

