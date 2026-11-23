"""Do teams have a lasting over 1.5 / over 2.5 goals tendency the prices miss?
Pre-registered in PROJECT.md (task 26), 2026-11-23.

Method mirrors src/team_tendency_study.py:
  Markets (decided separately): over_1.5 and over_2.5 (one row per match).
  Bookmaker probability = de-margined average odds read through the score matrix
  (accumulators.bookmaker_implied, league rho).
  Features (strictly no look-ahead): each team's previous TEAM_WINDOW (38) league matches
  (home and away combined; 0 if fewer than MIN_HISTORY = 10) mean(outcome - bookmaker probability),
  yielding r_home (home team's own past residual) and r_away (away team's / opponent's past residual).
  Primary (five leagues pooled, 2014/15+): for each evaluation season S from 2017/18, fit on
  2015/16 .. S-1:
    baseline   won ~ 1 + logit(p)
    challenger won ~ 1 + logit(p) + r_home + r_away
  and score season S. Paired per-match log-loss gain (baseline - challenger); 95% CI by
  whole-day bootstrap (2,000 resamples, seed 20261123).
  Secondary (live-era probabilities, 2024/25+): EPL blended (market_gates.gate_column),
  market leagues market_probability; first 60% of days fit, last 40% score, same models.
  Decision per market: USE only if primary 95% CI lower bound > 0 AND secondary gain > 0;
  otherwise DO NOT USE.

Usage: python -m src.team_goals_tendency_study   (writes reports/team_goals_tendency_study.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .accumulators import bookmaker_implied
from .calibration import ENGINE_DIR
from .leagues import paths
from .market_live import league_rho

REPORT_PATH = ENGINE_DIR / "reports" / "team_goals_tendency_study.md"
LEAGUES = ("EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1")
MARKETS = ("over_1.5", "over_2.5")
LINES = {"over_1.5": 1.5, "over_2.5": 2.5}
TEAM_WINDOW, MIN_HISTORY = 38, 10
FIRST_FIT_SEASON, FIRST_EVAL_SEASON, LIVE_FROM = "2015/16", "2017/18", "2024/25"
FIT_SHARE, BOOTSTRAP, SEED = 0.6, 2000, 20261123
ODDS = ["avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25"]


def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _loss(p, y):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def match_rows(matches: pd.DataFrame, league: str, rho: float) -> pd.DataFrame:
    """One row per match with outcomes and bookmaker-implied probabilities for over_1.5 and over_2.5."""
    valid = matches.dropna(subset=ODDS + ["home_goals", "away_goals"]).copy()
    valid = valid[(valid[ODDS] > 0).all(axis=1)]
    rows = []
    for m in valid.to_dict("records"):
        fair = bookmaker_implied(*(float(m[c]) for c in ODDS), rho)[0]
        total = float(m["home_goals"]) + float(m["away_goals"])
        rows.append({
            "league": league,
            "match_id": str(m["match_id"]),
            "date": pd.Timestamp(m["date"]),
            "season": str(m["season"]),
            "home_team": str(m["home_team"]),
            "away_team": str(m["away_team"]),
            "over_1.5_won": float(total > 1.5),
            "over_1.5_p": float(fair["over_1.5"]),
            "over_2.5_won": float(total > 2.5),
            "over_2.5_p": float(fair["over_2.5"]),
        })
    return pd.DataFrame(rows)


def add_features(rows: pd.DataFrame) -> pd.DataFrame:
    """Attach strictly past 38-match team residual means r_home and r_away for each market."""
    rows = rows.sort_values(["date", "match_id"]).reset_index(drop=True).copy()
    for market in MARKETS:
        rows[f"{market}_res"] = rows[f"{market}_won"] - rows[f"{market}_p"]
        home_side = rows[["league", "match_id", "date", "home_team", f"{market}_res"]].rename(
            columns={"home_team": "team", f"{market}_res": "res"}
        )
        away_side = rows[["league", "match_id", "date", "away_team", f"{market}_res"]].rename(
            columns={"away_team": "team", f"{market}_res": "res"}
        )
        panel = pd.concat([home_side, away_side], ignore_index=True)
        panel = panel.sort_values(["date", "match_id", "team"]).reset_index(drop=True)
        panel["rolling_res"] = (
            panel.groupby(["league", "team"])["res"]
            .transform(lambda s: s.shift(1).rolling(TEAM_WINDOW, min_periods=MIN_HISTORY).mean())
            .fillna(0.0)
        )
        lookup = pd.Series(
            panel["rolling_res"].to_numpy(),
            index=pd.MultiIndex.from_arrays([panel["league"], panel["match_id"], panel["team"]]),
        )
        rows[f"{market}_r_home"] = lookup.reindex(
            pd.MultiIndex.from_arrays([rows["league"], rows["match_id"], rows["home_team"]])
        ).to_numpy()
        rows[f"{market}_r_away"] = lookup.reindex(
            pd.MultiIndex.from_arrays([rows["league"], rows["match_id"], rows["away_team"]])
        ).to_numpy()
    return rows


def _design(frame: pd.DataFrame, p: np.ndarray, market: str, with_team: bool) -> np.ndarray:
    columns = [_logit(p)]
    if with_team:
        columns += [frame[f"{market}_r_home"].to_numpy(float), frame[f"{market}_r_away"].to_numpy(float)]
    return sm.add_constant(np.column_stack(columns), has_constant="add")


def _paired(fit: pd.DataFrame, test: pd.DataFrame, fit_p, test_p, market: str):
    y_fit = fit[f"{market}_won"].to_numpy(float)
    y = test[f"{market}_won"].to_numpy(float)
    base = sm.Logit(y_fit, _design(fit, fit_p, market, False)).fit(disp=0)
    chal = sm.Logit(y_fit, _design(fit, fit_p, market, True)).fit(disp=0)
    diff = _loss(base.predict(_design(test, test_p, market, False)), y) - _loss(
        chal.predict(_design(test, test_p, market, True)), y
    )
    return diff, chal.params


def _ci(diff: np.ndarray, days: np.ndarray) -> tuple[float, float]:
    frame = pd.DataFrame({"d": diff, "day": days})
    grouped = frame.groupby("day").d
    sums, counts = grouped.sum().to_numpy(), grouped.size().to_numpy()
    picks = np.random.default_rng(SEED).integers(0, len(sums), size=(BOOTSTRAP, len(sums)))
    low, high = np.percentile(sums[picks].sum(axis=1) / counts[picks].sum(axis=1), [2.5, 97.5])
    return float(low), float(high)


def primary(rows: pd.DataFrame, market: str) -> dict:
    """Walk-forward by season (2017/18+ scored, 2015/16..S-1 fit)."""
    seasons = sorted(rows.season.unique())
    frames, params = [], {}
    for season in [s for s in seasons if s >= FIRST_EVAL_SEASON]:
        fit = rows[(rows.season >= FIRST_FIT_SEASON) & (rows.season < season)]
        test = rows[rows.season == season]
        if fit.empty or test.empty:
            continue
        diff, coef = _paired(fit, test, fit[f"{market}_p"], test[f"{market}_p"], market)
        frames.append(test.assign(diff=diff))
        params[season] = [round(float(c), 3) for c in coef]
    scored = pd.concat(frames, ignore_index=True)
    days = scored.date.dt.normalize()
    low, high = _ci(scored["diff"].to_numpy(), days.to_numpy())
    per_league = {league: round(float(g["diff"].mean()), 5) for league, g in scored.groupby("league")}
    return {
        "legs": int(len(scored)),
        "days": int(days.nunique()),
        "gain": float(scored["diff"].mean()),
        "ci": (low, high),
        "per_league": per_league,
        "coefficients": params,
    }


def secondary(rows: pd.DataFrame, live: pd.DataFrame, market: str) -> dict:
    """Live-era (2024/25+) check using exact live probabilities; 60% of days fit, 40% scored."""
    legs = live[live.market == market].copy()
    legs = legs.merge(
        rows[["league", "match_id", f"{market}_r_home", f"{market}_r_away"]],
        on=["league", "match_id"],
        how="inner",
        validate="one_to_one",
    )
    legs[f"{market}_won"] = legs.won.astype(float)
    days = sorted(legs.date.dt.normalize().unique())
    fit_days = set(days[: int(len(days) * FIT_SHARE)])
    in_fit = legs.date.dt.normalize().isin(fit_days)
    fit, test = legs[in_fit], legs[~in_fit]
    diff, coef = _paired(fit, test, fit.live_p, test.live_p, market)
    test_days = test.date.dt.normalize()
    low, high = _ci(diff, test_days.to_numpy())
    return {
        "legs": int(len(test)),
        "days": int(test_days.nunique()),
        "gain": float(diff.mean()),
        "ci": (low, high),
        "coefficients": [round(float(c), 3) for c in coef],
    }


def persistence(rows: pd.DataFrame, market: str) -> tuple[float, int]:
    """Season-to-season correlation of a team's mean residual (>= 30 league matches in both seasons)."""
    home_side = rows[["league", "season", "home_team", f"{market}_res"]].rename(
        columns={"home_team": "team", f"{market}_res": "res"}
    )
    away_side = rows[["league", "season", "away_team", f"{market}_res"]].rename(
        columns={"away_team": "team", f"{market}_res": "res"}
    )
    panel = pd.concat([home_side, away_side], ignore_index=True)
    season = panel.groupby(["league", "team", "season"])["res"].agg(["mean", "size"])
    season = season[season["size"] >= 30]["mean"].reset_index()
    order = {s: i for i, s in enumerate(sorted(rows.season.unique()))}
    season["k"] = season.season.map(order)
    nxt = season.assign(k=season.k - 1).rename(columns={"mean": "next"})
    pairs = season.merge(nxt[["league", "team", "k", "next"]], on=["league", "team", "k"])
    return float(np.corrcoef(pairs["mean"], pairs["next"])[0, 1]), int(len(pairs))


def live_legs() -> pd.DataFrame:
    from .market_gates import gate_column

    parts = []
    for league in LEAGUES:
        legs = pd.read_parquet(paths(league).accumulator_legs)
        column = gate_column(legs, "blended" if league == "EPL" else "market")
        legs = legs[legs.market.isin(MARKETS)]
        parts.append(legs.assign(league=league, match_id=legs.match_id.astype(str), live_p=legs[column]))
    return pd.concat(parts, ignore_index=True)[["league", "match_id", "date", "market", "won", "live_p"]]


def decide(first: dict, second: dict) -> str:
    return "USE" if first["ci"][0] > 0 and second["gain"] > 0 else "DO NOT USE"


def main() -> None:
    rows = add_features(
        pd.concat(
            [match_rows(pd.read_parquet(paths(lg).matches), lg, league_rho(lg)) for lg in LEAGUES],
            ignore_index=True,
        )
    )
    live = live_legs()
    lines = [
        "# Team goals tendency study: over 1.5 and over 2.5 (PROJECT.md task 26, pre-registered 2026-11-23)",
        "",
        "Research only; no live changes. Evaluates whether teams have a lasting tendency to beat bookmaker "
        "over 1.5 or over 2.5 prices using each team's previous 38 league matches (home and away combined, "
        "minimum 10 matches, strictly no look-ahead).",
        "",
    ]
    decisions = {}
    for market in MARKETS:
        first = primary(rows, market)
        second = secondary(rows, live, market)
        corr, n_pairs = persistence(rows, market)
        decision = decide(first, second)
        decisions[market] = decision
        lines += [
            f"## {market}",
            "",
            f"- Primary (bookmaker price, seasons {FIRST_EVAL_SEASON}+, five leagues pooled): "
            f"**{first['legs']:,} matches** across {first['days']:,} days, paired log-loss gain "
            f"**{first['gain']:+.5f}** (95% whole-day bootstrap CI **{first['ci'][0]:+.5f} to {first['ci'][1]:+.5f}**, "
            f"2,000 resamples, seed `{SEED}`).",
            f"- Per-league primary gain: {first['per_league']}",
            f"- Secondary (live probabilities, last 40% of days {LIVE_FROM}+): "
            f"**{second['legs']:,} matches** across {second['days']:,} days, gain "
            f"**{second['gain']:+.5f}** (95% CI **{second['ci'][0]:+.5f} to {second['ci'][1]:+.5f}**).",
            f"- Season-to-season persistence of a team's residual (>= 30 matches/season): "
            f"**r = {corr:.3f}** ({n_pairs:,} team-season pairs).",
            f"- Primary coefficients `[const, logit(p), r_home, r_away]` by season: {first['coefficients']}",
            f"- Secondary coefficients `[const, logit(p), r_home, r_away]`: {second['coefficients']}",
            f"- **Decision: {decision}**",
            "",
        ]

    lines += ["## Interpretation of social-media 'profitable team' claims", ""]
    if all(d == "DO NOT USE" for d in decisions.values()):
        lines.append(
            "Both `over_1.5` and `over_2.5` fail the pre-registered out-of-sample test (**DO NOT USE**). "
            "Lists of teams claimed on social media to be 'profitable' for over 1.5 or over 2.5 goals are "
            "in-sample artefacts (cherry-picking teams that happened to beat the odds in a past window); "
            "bookmaker prices already incorporate teams' lasting scoring rates, so past residuals do not "
            "reliably beat the odds out of sample. Their claimed figures are not reproduced here."
        )
    else:
        lines.append("At least one market passed the pre-registered rule; review coefficients and live-era gain carefully before any live change.")

    lines += [
        "",
        "## What was NOT checked",
        "",
        "- Smaller leagues outside the five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`) were not included.",
        "- Window lengths other than 38 league matches (or home-only / away-only rolling splits) were not searched to avoid post-hoc tuning.",
        "- Bookmaker prices are football-data average opening/pre-match odds rather than Betpawa live odds or closing lines.",
        "",
    ]
    report = "\n".join(lines)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
