"""Stage 5: live predictions for upcoming Premier League fixtures.

Runs the same pipeline as the backtests, fitted on everything known today:
  refresh data -> Dixon-Coles blend -> Platt calibration -> goal-timing markets
  -> logit blend with the bookmaker market -> accumulator slips per tier.
Writes web/public/data/predictions.json for the app and keeps a settled history
of every published slip in data/live/slip_history.json.

Usage:  python -m src.predict            (refresh current season, then predict)
        python -m src.predict --no-refresh
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from io import StringIO

import numpy as np
import pandas as pd
import requests

from .accumulators import (
    bookmaker_implied,
    LEG_MARKETS, LEGS_PATH, RETAIL_MARGIN, SLIP_MARKETS, SLIPS_PATH, TIERS, best_slip, betting_round, blend,
    bookmaker_fair_probabilities, fit_model_weight,
)
from .backtest import _promoted_initialization
from .betpawa import fetch_competition_odds
from .health import health_check, pair_monitor, slip_leg_monitor
from .build_dataset import build, understat_results
from .calibration import (
    DC_PATH, ENGINE_DIR, MARKETS, MATCHES_PATH, add_actuals, enforce_probability_constraints, fit_calibrator,
)
from .dixon_coles import fit_dixon_coles, score_matrix, training_window
from .fetch_results import current_season_start, parse_match_dates, season_label
from .goal_timing import (
    GOALS_PATH, TIMING_MARKETS, TIMING_PATH, estimate_time_profile, fit_state_multipliers, simulate_match,
)
from .leagues import get_league, paths
from .market_gates import GATES_PATH
from .prices import clv_report, log_prices
from .market_live import LIVE_LEAGUES, calibrate, league_rho, load_calibrators
from .team_names import canonical_team

FIXTURES_URL = "https://football-data.co.uk/fixtures.csv"
TUNING_PATH = ENGINE_DIR / "reports" / "stage2_tuning.csv"
LIVE_DIR = ENGINE_DIR / "data" / "live"
HISTORY_PATH = LIVE_DIR / "slip_history.json"
PAUSED_PATH = LIVE_DIR / "paused_pairs.json"     # league x bet types the monitor keeps out of slips
WEB_DATA_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "predictions.json"
ARCHIVE_DIR = WEB_DATA_PATH.parent / "archive"
SIMULATIONS = 20_000
# A bet is "value" when probability x odds - 1 >= VALUE_EDGE. Keep in sync with web/src/lib.ts.
VALUE_EDGE = 0.03
# Long shots carry the most model error and variance; value singles need at least this probability.
VALUE_MIN_PROBABILITY = 0.25
# If Betpawa pays this much more than the (older) market-average price implies, the
# "edge" is more likely stale information (team news, line move) than a gift: warn and halve the stake.
PRICE_MOVE_WARNING = 0.08
# Bets are grouped by the user's calendar day (Tanzania, EAT), not by UK date.
LOCAL_TZ = "Africa/Dar_es_Salaam"

MARKET_LABELS = {
    "home_win": "Home win", "draw": "Draw", "away_win": "Away win",
    "over_0.5": "Over 0.5 goals", "over_1.5": "Over 1.5 goals", "over_2.5": "Over 2.5 goals",
    "over_3.5": "Over 3.5 goals", "under_2.5": "Under 2.5 goals", "under_3.5": "Under 3.5 goals",
    "btts_yes": "Both teams score", "btts_no": "Both teams score: No",
    "home_1up": "Home 1Up", "away_1up": "Away 1Up",
    "home_first": "Home scores first", "away_first": "Away scores first",
    "double_1x": "Home or draw", "double_x2": "Away or draw", "double_12": "Home or away",
}


_FIXTURES_CSV: pd.DataFrame | None = None


def _fixtures_csv() -> pd.DataFrame:
    """football-data.co.uk upcoming fixtures for every league, downloaded once per run."""
    global _FIXTURES_CSV
    if _FIXTURES_CSV is None:
        response = requests.get(FIXTURES_URL, timeout=30)
        response.raise_for_status()
        _FIXTURES_CSV = pd.read_csv(StringIO(response.content.decode("utf-8-sig")))
    return _FIXTURES_CSV


def load_fixtures(today: pd.Timestamp, played: pd.DataFrame, league="EPL") -> pd.DataFrame:
    """Upcoming fixtures of one league with average bookmaker odds."""
    selected = get_league(league)
    raw = _fixtures_csv()
    raw = raw[raw.Div == selected.football_data_code].copy()
    fixtures = pd.DataFrame({
        "date": parse_match_dates(raw.Date),
        "time": raw.Time.astype(str),
        "home_team": raw.HomeTeam.map(lambda name: canonical_team(name, selected)),
        "away_team": raw.AwayTeam.map(lambda name: canonical_team(name, selected)),
        # Average market odds; fixtures.csv carries no Pinnacle columns.
        "odds_home": raw.get("AvgH", raw.get("B365H")), "odds_draw": raw.get("AvgD", raw.get("B365D")),
        "odds_away": raw.get("AvgA", raw.get("B365A")),
        "odds_over25": raw.get("Avg>2.5", raw.get("B365>2.5")),
        "odds_under25": raw.get("Avg<2.5", raw.get("B365<2.5")),
    })
    # fixtures.csv times are UK local time.
    local = pd.to_datetime(fixtures.date.dt.strftime("%Y-%m-%d") + " " + fixtures.time, errors="coerce")
    fixtures["kickoff_utc"] = (local.dt.tz_localize("Europe/London", ambiguous="NaT", nonexistent="shift_forward")
                               .dt.tz_convert("UTC").dt.tz_localize(None))
    fixtures["kickoff_utc"] = fixtures.kickoff_utc.fillna(fixtures.date)
    fixtures = fixtures[fixtures.kickoff_utc > today]
    season = season_label(current_season_start(today.date()))
    done = set(zip(played.loc[played.season == season, "home_team"], played.loc[played.season == season, "away_team"]))
    # A boolean array, not a list: an empty list would select no COLUMNS (crash once every match has kicked off).
    fixtures = fixtures[np.array([(h, a) not in done for h, a in zip(fixtures.home_team, fixtures.away_team)], dtype=bool)]
    fixtures["season"] = season
    fixtures["league"] = selected.code
    return fixtures.sort_values(["date", "time"]).reset_index(drop=True)


def chosen_dc_settings() -> tuple[float, float]:
    tuning = pd.read_csv(TUNING_PATH)
    best = tuning[tuning.variant == "blend"].sort_values("validation_log_loss").iloc[0]
    return float(best.xi), float(best.blend_weight)


def fit_live_model(matches: pd.DataFrame, fixtures: pd.DataFrame, today: pd.Timestamp):
    xi, blend_weight = chosen_dc_settings()
    training = training_window(matches, today)
    teams = sorted(set(fixtures.home_team) | set(fixtures.away_team))
    base = fit_dixon_coles(training, today, xi=xi, variant="blend", blend_weight=blend_weight,
                           prediction_teams=teams)
    promoted = _promoted_initialization(matches, fixtures, training, base)
    model = fit_dixon_coles(training, today, xi=xi, variant="blend", blend_weight=blend_weight,
                            warm_start=base, prediction_teams=teams, promoted_values=promoted)
    return model, {"xi": xi, "blend_weight": blend_weight, "training_matches": len(training),
                   "training_last_date": training.date.max().date().isoformat()}


def fit_calibrators(matches: pd.DataFrame) -> tuple[dict, dict]:
    """Platt calibrators on every settled out-of-sample prediction we have."""
    dc = pd.read_parquet(DC_PATH)
    dc = add_actuals(dc[dc.variant == "blend"].merge(matches, on=["match_id", "date"]))
    main = {market: fit_calibrator(dc[raw], dc[actual], "platt") for market, (raw, actual) in MARKETS.items()}
    timing = pd.read_parquet(TIMING_PATH)
    path = {market: fit_calibrator(timing[raw], timing[actual], "platt")
            for market, (raw, actual) in TIMING_MARKETS.items()}
    return main, path


def predict_fixtures(fixtures, model, matches, goals, calibrators, model_weight) -> pd.DataFrame:
    main_cal, timing_cal = calibrators
    dc_history = pd.read_parquet(DC_PATH)
    dc_history = dc_history[dc_history.variant == "blend"]
    _, profile = estimate_time_profile(goals)
    history_matches = matches[matches.match_id.isin(dc_history.match_id)]
    multipliers = fit_state_multipliers(history_matches, goals[goals.match_id.isin(history_matches.match_id)],
                                        dc_history, profile)
    rows = []
    for index, fixture in fixtures.iterrows():
        matrix, raw = model.predict(fixture.home_team, fixture.away_team)
        cal = pd.DataFrame([{f"cal_{market}": main_cal[market].predict([raw[column]])[0]
                             for market, (column, _) in MARKETS.items()}])
        enforce_probability_constraints(cal, "cal")
        cal = cal.iloc[0]
        timing = simulate_match(raw["lambda_home"], raw["lambda_away"], profile, multipliers,
                                simulations=SIMULATIONS, seed=index + 1, matrix=matrix)
        model_probs = {
            "home_win": cal.cal_home, "draw": cal.cal_draw, "away_win": cal.cal_away,
            "over_0.5": cal.cal_over05, "over_1.5": cal.cal_over15, "over_2.5": cal.cal_over25,
            "over_3.5": cal.cal_over35, "under_2.5": 1 - cal.cal_over25, "under_3.5": 1 - cal.cal_over35,
            "btts_yes": cal.cal_btts, "btts_no": 1 - cal.cal_btts,
            "double_1x": cal.cal_home + cal.cal_draw, "double_x2": cal.cal_draw + cal.cal_away,
            "double_12": cal.cal_home + cal.cal_away,
            **{market: float(timing_cal[market].predict([timing[f"sim_{market}"]])[0])
               for market in ("home_1up", "away_1up", "home_first", "away_first")},
        }
        has_odds = fixture[["odds_home", "odds_draw", "odds_away", "odds_over25", "odds_under25"]].notna().all()
        market_probs = (bookmaker_fair_probabilities(fixture.odds_home, fixture.odds_draw, fixture.odds_away,
                                                     fixture.odds_over25, fixture.odds_under25, model.rho)
                        if has_odds else {})
        for market in LEG_MARKETS:
            model_p = float(model_probs[market])
            market_p = market_probs.get(market)
            final = float(blend(model_p, market_p, model_weight)) if market_p is not None else model_p
            rows.append({
                "fixture": index, "date": fixture.date, "time": fixture.time, "season": fixture.season,
                "kickoff_utc": fixture.kickoff_utc,
                "home_team": fixture.home_team, "away_team": fixture.away_team, "market": market,
                "model_probability": model_p, "bookmaker_probability": market_p, "probability": final,
                "odds": 1 / (market_p * (1 + RETAIL_MARGIN)) if market_p is not None else np.nan,
                "lambda_home": raw["lambda_home"], "lambda_away": raw["lambda_away"],
                "top_scorelines": raw["top_scorelines"],
            })
    legs = pd.DataFrame(rows)
    legs["round"] = betting_round(legs.date)
    legs["match_id"] = legs.fixture
    return legs


def predict_market_fixtures(fixtures: pd.DataFrame, league) -> pd.DataFrame:
    """Market mode: calibrated bookmaker consensus for every market (see market_live.py).

    Expected goals and likeliest scores come from the score matrix the prices imply.
    Fixtures without bookmaker odds are skipped: market mode has nothing to go on.
    """
    calibrators, rho, rows = load_calibrators(league), league_rho(league), []
    odds_columns = ["odds_home", "odds_draw", "odds_away", "odds_over25", "odds_under25"]
    for index, fixture in fixtures.iterrows():
        if fixture[odds_columns].isna().any():
            continue
        fair, (lam, mu), matrix = bookmaker_implied(*fixture[odds_columns].astype(float), rho)
        order = np.argsort(matrix.ravel())[-3:][::-1]
        top = json.dumps([{"score": f"{i // 11}-{i % 11}", "probability": float(matrix.ravel()[i])} for i in order])
        for market in LEG_MARKETS:
            probability = calibrate(fair[market], calibrators.get(market))
            rows.append({
                "fixture": index, "date": fixture.date, "time": fixture.time, "season": fixture.season,
                "kickoff_utc": fixture.kickoff_utc, "home_team": fixture.home_team, "away_team": fixture.away_team,
                "market": market, "model_probability": probability, "bookmaker_probability": fair[market],
                "probability": probability, "odds": 1 / (fair[market] * (1 + RETAIL_MARGIN)),
                "lambda_home": lam, "lambda_away": mu, "top_scorelines": top,
            })
    legs = pd.DataFrame(rows)
    if not legs.empty:
        legs["round"] = betting_round(legs.date)
        legs["match_id"] = legs.fixture
    return legs


def league_context(matches: pd.DataFrame, season: str) -> dict[str, dict]:
    """Current-season table and last-5 form per team (display only; not a model input:
    the table was tested as a predictor and did not help, see PROJECT.md section 7)."""
    played = matches[(matches.season == season) & matches.home_goals.notna()].sort_values("date")
    table: dict[str, dict] = {}
    for m in played.itertuples():
        for team, scored, conceded in ((m.home_team, m.home_goals, m.away_goals), (m.away_team, m.away_goals, m.home_goals)):
            row = table.setdefault(team, {"played": 0, "points": 0, "gd": 0, "gf": 0, "form": []})
            result = "W" if scored > conceded else "D" if scored == conceded else "L"
            row["played"] += 1
            row["points"] += {"W": 3, "D": 1, "L": 0}[result]
            row["gd"] += int(scored - conceded)
            row["gf"] += int(scored)
            row["form"] = (row["form"] + [result])[-5:]          # oldest -> newest
    order = sorted(table, key=lambda t: (-table[t]["points"], -table[t]["gd"], -table[t]["gf"], t))
    return {team: {"position": i + 1, "teams": len(order), **{k: v for k, v in table[team].items() if k != "gf"}}
            for i, team in enumerate(order)}


def head_to_head(history: pd.DataFrame | None, home: str, away: str, n: int = 6) -> dict | None:
    """Last `n` league meetings of the two teams (either venue) with a summary from this fixture's
    point of view. Display only: not a model input (untested as a predictor)."""
    if history is None or history.empty:
        return None
    pair = history[(((history.home_team == home) & (history.away_team == away))
                    | ((history.home_team == away) & (history.away_team == home))) & history.home_goals.notna()]
    if pair.empty:
        return None
    recent = pair.sort_values("date", ascending=False).head(n)
    home_goals = np.where(recent.home_team == home, recent.home_goals, recent.away_goals)
    away_goals = np.where(recent.home_team == home, recent.away_goals, recent.home_goals)
    total = recent.home_goals + recent.away_goals
    return {
        "meetings": [{"date": pd.Timestamp(m.date).date().isoformat(), "home": m.home_team, "away": m.away_team,
                      "score": [int(m.home_goals), int(m.away_goals)]} for m in recent.itertuples()],
        "home_wins": int((home_goals > away_goals).sum()), "draws": int((home_goals == away_goals).sum()),
        "away_wins": int((home_goals < away_goals).sum()), "avg_goals": round(float(total.mean()), 2),
        "over_2_5": int((total > 2.5).sum()), "btts": int(((recent.home_goals > 0) & (recent.away_goals > 0)).sum()),
        "since": str(history.season.min()),
    }


def league_json(code: str) -> dict:
    league = get_league(code)
    return {"code": league.code, "name": league.name, "country": league.country}


def attach_betpawa(legs: pd.DataFrame, betpawa: pd.DataFrame) -> pd.DataFrame:
    """Add real Betpawa odds per leg; slips then use real prices where available."""
    legs = legs.copy()
    if betpawa.empty:
        legs["betpawa_odds"] = np.nan
    else:
        merged = legs.merge(betpawa[["home_team", "away_team", "market", "kickoff_utc", "betpawa_odds"]]
                            .rename(columns={"kickoff_utc": "betpawa_kickoff"}),
                            on=["home_team", "away_team", "market"], how="left")
        # Guard against a same-teams fixture on another date (e.g. a cup tie).
        far = (merged.betpawa_kickoff - merged.kickoff_utc).abs() > pd.to_timedelta(1, unit="D")
        merged.loc[far, "betpawa_odds"] = np.nan
        legs = merged.drop(columns="betpawa_kickoff")
    legs["estimated_odds"] = legs.odds
    legs["odds"] = legs.betpawa_odds.fillna(legs.estimated_odds)
    legs["edge"] = legs.probability * legs.betpawa_odds - 1
    legs["price_warning"] = legs.bookmaker_probability * legs.betpawa_odds - 1 > PRICE_MOVE_WARNING
    return legs


def kelly_fraction(probability: float, odds: float) -> float:
    """Full-Kelly stake fraction; the app stakes a quarter of it, capped."""
    return max((probability * odds - 1) / (odds - 1), 0.0) if odds > 1 else 0.0


def value_picks(legs: pd.DataFrame) -> list[dict]:
    """Singles where Betpawa pays more than our fair odds, best edge first."""
    picks = legs[(legs.edge >= VALUE_EDGE) & (legs.probability >= VALUE_MIN_PROBABILITY)]
    picks = picks.sort_values("edge", ascending=False)
    return [_leg_json(row) | {"edge": round(float(row.edge), 4),
                              "kelly": round(kelly_fraction(row.probability, row.betpawa_odds), 4)}
            for row in picks.itertuples()]


def local_day(kickoff_utc: pd.Series) -> pd.Series:
    """Calendar day of each kickoff in the user's time zone, as YYYY-MM-DD."""
    return kickoff_utc.dt.tz_localize("UTC").dt.tz_convert(LOCAL_TZ).dt.strftime("%Y-%m-%d")


def at_least(probabilities, k: int) -> float:
    """P(at least k of the independent legs win): Poisson-binomial tail."""
    distribution = np.array([1.0])
    for p in probabilities:
        distribution = np.convolve(distribution, [1 - p, p])
    return float(distribution[k:].sum())


def flexi_options(probabilities) -> list[dict]:
    """SportyBet Flexi: the ticket wins if at least k of n picks win (fixed, reduced payout)."""
    n = len(probabilities)
    return [{"min_correct": k, "probability": round(at_least(probabilities, k), 4)}
            for k in range(n - 1, max(n - 3, 1), -1)] if n >= 3 else []


def failed_gates() -> set[tuple[str, str]]:
    """League x market pairs that failed the pre-registered gates (PROJECT.md task 1): never slip legs."""
    if not GATES_PATH.exists():
        return set()
    gates = json.loads(GATES_PATH.read_text(encoding="utf-8"))["gates"]
    return {(league, market) for league, markets in gates.items() for market, status in markets.items()
            if status == "FAIL"}


def build_slips(legs: pd.DataFrame, blocked: set[tuple[str, str]] | None = None) -> dict:
    """Tier slips from one day's matches, using only the user's slip markets with a price.

    League x market pairs in `blocked` (default: the failed gates) stay on match pages but never enter a slip.
    """
    blocked = failed_gates() if blocked is None else blocked
    league = legs["league"] if "league" in legs else pd.Series("EPL", index=legs.index)
    allowed = pd.Series([(lg, m) not in blocked for lg, m in zip(league, legs.market)], index=legs.index, dtype=bool)
    pool = legs[legs.market.isin(SLIP_MARKETS) & allowed & legs.odds.notna() & (legs.odds >= 1.05)]
    slips = {}
    for tier in TIERS:
        picks = best_slip(pool, tier) if not pool.empty else None
        if picks is None:
            continue
        chosen = pool.loc[picks]
        total, win = float(chosen.odds.prod()), float(chosen.probability.prod())
        slips[tier.name] = {
            "total_odds": round(total, 2),
            "win_probability": round(win, 4),
            "odds_source": "betpawa" if chosen.betpawa_odds.notna().all() else "estimated",
            "expected_value": round(win * total - 1, 4),
            "kelly": round(kelly_fraction(win, total), 4),
            "price_warning": bool(chosen.price_warning.any()),
            "flexi": flexi_options(chosen.probability.tolist()),
            "legs": [_leg_json(row) for row in chosen.itertuples()],
        }
    return slips


def _leg_json(row) -> dict:
    return {"date": row.date.date().isoformat(), "time": row.time, "kickoff_utc": row.kickoff_utc.isoformat() + "Z",
            "league": league_json(getattr(row, "league", "EPL")),
            "home": row.home_team, "away": row.away_team,
            "market": row.market, "label": MARKET_LABELS[row.market],
            "probability": round(float(row.probability), 4),
            "estimated_odds": round(float(row.estimated_odds), 2) if pd.notna(row.estimated_odds) else None,
            "betpawa_odds": None if pd.isna(row.betpawa_odds) else round(float(row.betpawa_odds), 2),
            "fair_odds": round(1 / float(row.probability), 2),
            "price_warning": bool(getattr(row, "price_warning", False))}


def outcome(match: pd.Series, market: str) -> bool:
    _, actual_column = LEG_MARKETS[market]
    if actual_column.startswith(("actual_under", "actual_btts_no")):
        base = actual_column.replace("under", "over").replace("btts_no", "btts")
        return not bool(match[base])
    return bool(match[actual_column])


def update_history(round_id: str | None, slips: dict, matches: pd.DataFrame, now: pd.Timestamp,
                   final: bool = False) -> list[dict]:
    """Store this round's slips (until final or first kickoff) and settle finished legs.

    `final` is the run shortly before the day's first match: its slips are the ones the owner places,
    so they are marked final and never replaced; earlier (preview) slips it does not keep are dropped.
    """
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    history = json.loads(HISTORY_PATH.read_text(encoding="utf-8")) if HISTORY_PATH.exists() else []
    if round_id and final:
        history = [entry for entry in history if not (entry["round"] == round_id and entry["tier"] not in slips
                                                      and not entry.get("final") and _not_started(entry, now))]
    if round_id and any(entry["round"] == round_id and entry.get("final") for entry in history):
        slips = {}      # the day is final: later runs settle and collect prices but never add or change slips
    if round_id and slips:
        # Each tier's slip is frozen once final or once its first leg kicks off, so the history
        # only ever records slips that were published before any of their matches.
        for tier, slip in slips.items():
            first_kickoff = min(pd.Timestamp(leg["kickoff_utc"]).tz_localize(None) for leg in slip["legs"])
            stored = [entry for entry in history if entry["round"] == round_id and entry["tier"] == tier]
            frozen = stored and (stored[0].get("final") or not _not_started(stored[0], now))
            if now < first_kickoff and not frozen:
                history = [entry for entry in history if not (entry["round"] == round_id and entry["tier"] == tier)]
                history.append({"round": round_id, "tier": tier, "generated_at": now.isoformat() + "Z", **slip,
                                "final": final})
    settled = add_actuals(matches)
    lookup = {(row.home_team, row.away_team, row.season): row for _, row in settled.iterrows()}
    for entry in history:
        for leg in entry["legs"]:
            season = season_label(current_season_start(pd.Timestamp(leg["date"]).date()))
            match = lookup.get((leg["home"], leg["away"], season))
            leg["won"] = None if match is None else outcome(match, leg["market"])
        results = [leg["won"] for leg in entry["legs"]]
        entry["status"] = ("lost" if False in results else "pending" if None in results else "won")
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return history


def _not_started(entry: dict, now: pd.Timestamp) -> bool:
    return all(pd.Timestamp(leg["kickoff_utc"]).tz_localize(None) > now for leg in entry["legs"])


def recent_results(matches: pd.DataFrame, now: pd.Timestamp, days: int = 120) -> list[dict]:
    """Settled outcomes of every leg market for recent matches (the app settles saved picks)."""
    recent = add_actuals(matches[matches.date >= now - pd.to_timedelta(days, unit="D")])
    return [{"date": row.date.date().isoformat(), "home": row.home_team, "away": row.away_team,
             "score": [int(row.home_goals), int(row.away_goals)],
             "outcomes": {market: outcome(row, market) for market in LEG_MARKETS}}
            for _, row in recent.sort_values("date", ascending=False).iterrows()]


def displayed_slips(round_id: str | None, slips: dict, history: list[dict], now: pd.Timestamp) -> dict:
    """Slips to show: once a tier's slip has a match under way, show that frozen slip.

    Later runs re-optimise over the matches not yet started, but those slips are
    never recorded, so showing them would let the app and the record disagree.
    """
    day_final = any(entry["round"] == round_id and entry.get("final") for entry in history)
    shown = {} if day_final else {tier: {**slip, "locked": False, "final": False} for tier, slip in slips.items()}
    for entry in history:
        if entry["round"] != round_id:
            continue
        started = not _not_started(entry, now)
        if started or entry.get("final"):   # the recorded slip, complete (Flexi too, to settle it later)
            shown[entry["tier"]] = {k: v for k, v in entry.items() if k not in ("round", "tier", "generated_at")}
            shown[entry["tier"]] |= {"locked": started, "final": bool(entry.get("final"))}
    return shown


def _fixture_key(fixture: dict) -> tuple:
    return fixture["date"], fixture["home"], fixture["away"]


def archive_snapshot(fixtures: list[dict], slips: dict, day: str, now: pd.Timestamp) -> None:
    """Save a match day's predictions and bets; matches already kicked off keep their earlier prediction."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    path = ARCHIVE_DIR / f"{day}.json"
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"fixtures": []}
    current = {_fixture_key(f): f for f in previous["fixtures"]}
    for fixture in fixtures:
        # The full published record (form, table, head-to-head, every market), so any past or started
        # match can still be opened in the app; only the run-specific id is dropped.
        current[_fixture_key(fixture)] = {key: value for key, value in fixture.items() if key != "id"}
    snapshot = {"date": day, "generated_at": now.isoformat() + "Z",
                "fixtures": sorted(current.values(), key=lambda f: f["kickoff_utc"]),
                # Locked slips are already frozen; unlocked ones are the latest pre-kickoff version.
                "slips": {tier: {k: v for k, v in slip.items() if k != "status"} for tier, slip in slips.items()}}
    path.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")


def settle_archive(matches: pd.DataFrame) -> list[dict]:
    """Attach final scores and per-market outcomes to archived predictions; return the index."""
    if not ARCHIVE_DIR.exists():
        return []
    settled = add_actuals(matches)
    lookup = {(row.home_team, row.away_team, row.season): row for _, row in settled.iterrows()}
    index = []
    for path in sorted(ARCHIVE_DIR.glob("20*.json"), reverse=True):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for fixture in snapshot["fixtures"]:
            if "result" in fixture:
                continue
            season = season_label(current_season_start(pd.Timestamp(fixture["date"]).date()))
            match = lookup.get((fixture["home"], fixture["away"], season))
            if match is not None:
                fixture["result"] = {"score": [int(match.home_goals), int(match.away_goals)],
                                     "outcomes": {m: outcome(match, m) for m in LEG_MARKETS}}
                changed = True
        for slip in snapshot.get("slips", {}).values():
            for leg in slip["legs"]:
                if leg.get("won") is None:
                    season = season_label(current_season_start(pd.Timestamp(leg["date"]).date()))
                    match = lookup.get((leg["home"], leg["away"], season))
                    if match is not None:
                        leg["won"] = outcome(match, leg["market"])
                        changed = True
            results = [leg.get("won") for leg in slip["legs"]]
            slip["status"] = "lost" if False in results else "pending" if None in results else "won"
        if changed:
            path.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")
        done = sum("result" in f for f in snapshot["fixtures"])
        index.append({"date": snapshot["date"], "fixtures": len(snapshot["fixtures"]), "settled": done})
    (ARCHIVE_DIR / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    return index


def settled_predictions() -> list[dict]:
    """Last pre-kickoff published prediction of every settled match, oldest first."""
    latest = {}
    for path in sorted(ARCHIVE_DIR.glob("20*.json")) if ARCHIVE_DIR.exists() else []:
        for fixture in json.loads(path.read_text(encoding="utf-8"))["fixtures"]:
            latest[_fixture_key(fixture)] = fixture
    return sorted((f for f in latest.values() if "result" in f), key=lambda f: f["kickoff_utc"])


def load_paused() -> set[tuple[str, str]]:
    return {tuple(pair) for pair in json.loads(PAUSED_PATH.read_text(encoding="utf-8"))} if PAUSED_PATH.exists() else set()


def save_paused(paused: set[tuple[str, str]]) -> None:
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    PAUSED_PATH.write_text(json.dumps(sorted(paused)), encoding="utf-8")


def realised_slips(history: list[dict]) -> dict:
    """Settled published slips per tier at their published odds, 1 unit each."""
    report = {}
    for tier in ("safe", "medium", "big"):
        settled = [e for e in history if e["tier"] == tier and e.get("status") in ("won", "lost")]
        won = [e for e in settled if e["status"] == "won"]
        profit = sum(e["total_odds"] for e in won) - len(settled)
        report[tier] = {"settled": len(settled), "won": len(won),
                        "predicted": round(sum(e["win_probability"] for e in settled), 2),
                        "profit": round(profit, 2), "roi": round(profit / len(settled), 4) if settled else None}
    return report


def live_record() -> dict:
    """Accuracy of published predictions: last pre-kickoff prediction per settled match."""
    settled = settled_predictions()
    if not settled:
        return {"matches": 0}
    keys = ("home_win", "draw", "away_win")
    ours, market, actual, confident, value_returns = [], [], [], [], []
    for fixture in settled:
        markets = {m["market"]: m for m in fixture["markets"]}
        for m in fixture["markets"]:
            price = m.get("betpawa_odds")
            if price and m["probability"] >= VALUE_MIN_PROBABILITY and m["probability"] * price - 1 >= VALUE_EDGE:
                value_returns.append(price - 1 if fixture["result"]["outcomes"][m["market"]] else -1.0)
        ours.append([markets[k]["probability"] for k in keys])
        market.append([markets[k]["market_probability"] or np.nan for k in keys])
        actual.append([fixture["result"]["outcomes"][k] for k in keys])
        confident += [fixture["result"]["outcomes"][m["market"]] for m in fixture["markets"] if m["probability"] >= 0.7]
    ours, market, actual = np.array(ours), np.array(market, float), np.array(actual, float)
    has_market = ~np.isnan(market).any(axis=1)

    def log_loss(p, rows):
        return float(-np.mean(np.log(np.clip((p[rows] * actual[rows]).sum(axis=1), 1e-9, 1))))

    return {
        "matches": len(settled),
        "result_hit_rate": round(float(np.mean(ours.argmax(axis=1) == actual.argmax(axis=1))), 4),
        "log_loss": round(log_loss(ours, has_market), 4) if has_market.any() else None,
        "market_log_loss": round(log_loss(market, has_market), 4) if has_market.any() else None,
        "confident_picks": len(confident),
        "confident_hit_rate": round(float(np.mean(confident)), 4) if confident else None,
        "value_bets": len(value_returns),
        "value_bets_won": int(sum(r > 0 for r in value_returns)),
        "value_roi": round(float(np.mean(value_returns)), 4) if value_returns else None,
    }


def backtest_summary() -> dict:
    slips = pd.read_parquet(SLIPS_PATH)
    accuracy = slips[slips["mode"] == "accuracy"]
    return {tier: {"slips": int(len(group)), "win_rate": round(float(group.won.mean()), 4),
                   "predicted_win_rate": round(float(group.predicted_win.mean()), 4),
                   "average_odds": round(float(group.total_odds.mean()), 2)}
            for tier, group in accuracy.groupby("tier")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-refresh", action="store_true", help="use cached data, skip downloads")
    parser.add_argument("--final", action="store_true",
                        help="final run before today's first match: today's slips become final (never replaced)")
    args = parser.parse_args()
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)

    if args.no_refresh:
        matches, goals = pd.read_parquet(MATCHES_PATH), pd.read_parquet(GOALS_PATH)
    else:
        matches, goals = build(refresh_current=True)

    # Premier League: our blended model, exactly as validated.
    parts, model_info, model_weight = [], {}, None
    fixtures = load_fixtures(now, matches, "EPL")
    if not fixtures.empty:
        model, model_info = fit_live_model(matches, fixtures, now)
        model_weight = fit_model_weight(pd.read_parquet(LEGS_PATH))
        epl = predict_fixtures(fixtures, model, matches, goals, fit_calibrators(matches), model_weight)
        parts.append(epl.assign(league="EPL", mode="blended"))
    next_fixture_id = len(fixtures)

    # Market-mode leagues: calibrated bookmaker consensus. Only the current season is fetched,
    # to know which matches are played and to settle bets. A failing league is skipped.
    season_start = current_season_start(now.date())
    settle_matches = [matches]
    current_season = season_label(season_start)
    context = league_context(matches, current_season)
    h2h_history = {"EPL": matches}        # all seasons per league, for head-to-head (display only)
    for code, mode in LIVE_LEAGUES.items():
        if mode != "market":
            continue
        try:
            current, _ = build(refresh_current=not args.no_refresh, league=code, write=False, start=season_start)
            settle_matches.append(current)
            context.update(league_context(current, current_season))
            past = pd.read_parquet(paths(code).matches) if paths(code).matches.exists() else current.iloc[0:0]
            h2h_history[code] = (pd.concat([past, current], ignore_index=True)
                                 .drop_duplicates(["season", "home_team", "away_team"], keep="last"))
            league_fixtures = load_fixtures(now, current, code)
            league_fixtures.index = league_fixtures.index + next_fixture_id
            next_fixture_id += len(league_fixtures)
            league_legs = predict_market_fixtures(league_fixtures, code)
            if not league_legs.empty:
                parts.append(league_legs.assign(league=code, mode="market"))
            print(f"{get_league(code).name}: {league_legs.fixture.nunique() if not league_legs.empty else 0} fixtures")
        except Exception as error:
            print(f"{get_league(code).name} skipped this run: {error}")
    if not parts:
        raise SystemExit("No upcoming fixtures in any live league")
    legs = pd.concat(parts, ignore_index=True)
    # Settle from Understat the same night; football-data rows (when they arrive days later) take over.
    fast = []
    for code in LIVE_LEAGUES:
        try:
            fast.append(understat_results(code, season_start))
        except Exception as error:
            print(f"Understat results unavailable for {get_league(code).name} ({error})")
    all_matches = (pd.concat(fast + settle_matches, ignore_index=True)
                   .drop_duplicates(["season", "home_team", "away_team"], keep="last"))

    betpawa_parts = []
    for code in legs.league.unique():
        try:
            betpawa_parts.append(fetch_competition_odds(code))
        except Exception as error:  # Betpawa down or changed: predictions still publish.
            print(f"Betpawa odds unavailable for {get_league(code).name} ({error}); using estimated odds")
    betpawa = (pd.concat(betpawa_parts, ignore_index=True) if betpawa_parts
               else pd.DataFrame(columns=["home_team", "away_team", "market", "kickoff_utc", "betpawa_odds"]))
    print(f"Betpawa: {len(betpawa)} prices across {len(betpawa_parts)} leagues")
    legs = attach_betpawa(legs, betpawa)
    legs["day"] = local_day(legs.kickoff_utc)
    today = local_day(pd.Series([now])).iloc[0]
    log_prices(legs, now)
    # Settle first, so the per bet type monitor sees the newest results before slips are built.
    settle_archive(all_matches)
    pairs = pair_monitor(settled_predictions(), SLIP_MARKETS, load_paused())
    paused = {(row["league"], row["market"]) for row in pairs if row["status"] == "paused"}
    save_paused(paused)
    blocked = failed_gates() | paused
    days = []
    for day, day_legs in legs.groupby("day", sort=True):
        slips = build_slips(day_legs, blocked)
        history = update_history(day, slips, all_matches, now, final=args.final and day == today)
        shown = displayed_slips(day, slips, history, now)
        days.append({"date": day, "fixtures": sorted(int(f) for f in day_legs.fixture.unique()),
                     "first_kickoff_utc": day_legs.kickoff_utc.min().isoformat() + "Z",
                     "final": any(slip["final"] for slip in shown.values()),
                     "value_picks": value_picks(day_legs),
                     "slips": shown})
    if not days:
        history = update_history(None, {}, all_matches, now)

    output = {
        "generated_at": now.isoformat() + "Z",
        "model": {**model_info, "market_blend_model_weight": model_weight, "retail_margin": RETAIL_MARGIN,
                  "league_modes": LIVE_LEAGUES},
        "backtest": backtest_summary(),
        "time_zone": LOCAL_TZ,
        "fixtures": [
            {
                "id": int(fixture_id), "league": league_json(group.league.iloc[0]), "mode": group["mode"].iloc[0],
                "date": group.date.iloc[0].date().isoformat(), "time": group.time.iloc[0],
                "kickoff_utc": group.kickoff_utc.iloc[0].isoformat() + "Z",
                "home": group.home_team.iloc[0], "away": group.away_team.iloc[0],
                "context": {"home": context.get(group.home_team.iloc[0]), "away": context.get(group.away_team.iloc[0])},
                "head_to_head": head_to_head(h2h_history.get(group.league.iloc[0]), group.home_team.iloc[0], group.away_team.iloc[0]),
                "day": group["day"].iloc[0],
                "expected_goals": [round(float(group.lambda_home.iloc[0]), 2), round(float(group.lambda_away.iloc[0]), 2)],
                "top_scorelines": json.loads(group.top_scorelines.iloc[0]),
                "has_market_odds": bool(group.bookmaker_probability.notna().all()),
                "markets": [
                    {"market": row.market, "label": MARKET_LABELS[row.market],
                     "probability": round(float(row.probability), 4),
                     "model_probability": round(float(row.model_probability), 4),
                     "market_probability": None if pd.isna(row.bookmaker_probability) else round(float(row.bookmaker_probability), 4),
                     "fair_odds": round(1 / float(row.probability), 2),
                     "betpawa_odds": None if pd.isna(row.betpawa_odds) else round(float(row.betpawa_odds), 2)}
                    for row in group.itertuples()
                ],
            }
            for fixture_id, group in legs.groupby("fixture", sort=True)
        ],
        "days": days,
        "value_rules": {"min_edge": VALUE_EDGE, "min_probability": VALUE_MIN_PROBABILITY},
        "history": history,
        "results": recent_results(all_matches, now),
    }
    for day in days:
        archive_snapshot([f for f in output["fixtures"] if f["day"] == day["date"]], day["slips"], day["date"], now)
    output["archive"] = settle_archive(all_matches)
    output["live_record"] = live_record()
    output["clv"] = clv_report(history)
    output["health"] = health_check(settled_predictions(), history, SLIP_MARKETS) | {
        "pairs": pairs, "slip_legs": slip_leg_monitor(history)}
    output["realised"] = realised_slips(history)
    print(f"Model health: {output['health']['status']}")
    WEB_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEB_DATA_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"{len(output['fixtures'])} fixtures over {len(days)} days: "
          + "; ".join(f"{d['date']} {len(d['value_picks'])} value picks, slips {'/'.join(d['slips']) or '-'}" for d in days))
    print(f"Wrote {WEB_DATA_PATH}")


if __name__ == "__main__":
    main()
