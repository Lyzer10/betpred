"""PROJECT.md task 27: daily Trial slip design, margin check, eligible list, and offline dry run.

Research and dry run only: nothing here goes live, nothing modifies web/public/data or
engine/data/live, and this module never imports predict.py or anything that publishes.

Usage (from ``engine``):
    python -m src.trial_slip --dry-run
Writes ONLY ``engine/reports/trial_slip_dryrun.md``.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .accumulators import Tier, best_slip, bookmaker_implied
from .betpawa import RESEARCH_MARKETS
from .calibration import ENGINE_DIR
from .fetch_results import current_season_start, season_label
from .half_markets_study import (
    MARKETS as TASK16_MARKETS,
    build_league_legs as build_task16_legs,
    half_market_raw_probabilities,
    load_league_matches as load_htft_matches,
)
from .market_live import league_rho
from .new_markets_study import _logit
from .timing_half_markets_study import (
    HALF_MARKETS as TASK20_TEAM_HALF_MARKETS,
    MAIN_LEAGUES,
    TIMING_MARKETS as TASK20_TIMING_MARKETS,
    build_walkforward_half_legs,
    build_walkforward_timing_legs,
    half_team_raw_probabilities,
    load_timing_matches,
    timing_market_raw_probabilities,
)
from .up_markets_study import (
    MARKETS as TASK17_MARKETS,
    add_raw_probabilities as add_up_raw_probabilities,
    load_league_matches as load_up_matches,
    raw_up_probabilities_from_matrix,
)

REPORTS_DIR = ENGINE_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "trial_slip_dryrun.md"
MAIN_PRICES_DIR = ENGINE_DIR / "data" / "live" / "prices"
RESEARCH_PRICES_DIR = ENGINE_DIR / "data" / "live" / "research" / "prices"
PREDICTIONS_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "predictions.json"

EAT = ZoneInfo("Africa/Dar_es_Salaam")
TRIAL_TIER = Tier("trial", 3.0, 5.0, 2, 4)
TRIAL_STAKE_CAP = 0.01
MIN_ODDS = 1.05
FAIR_KEYS = ("home_win", "draw", "away_win", "over_2.5", "under_2.5")
PAUSE_MIN_SLIPS = 30
PAUSE_Z_THRESHOLD = -2.5

# Complete mutually exclusive & exhaustive outcome sets whose overround is sum(1/odds) - 1.
COMPLETE_OUTCOME_SETS: dict[str, tuple[str, ...]] = {
    "1x2": ("home_win", "draw", "away_win"),
    "over_under_2.5": ("over_2.5", "under_2.5"),
    "dnb": ("dnb_home", "dnb_away"),
    "interval_10_1x2": ("interval_10_home", "interval_10_draw", "interval_10_away"),
    "btts": ("btts_yes", "btts_no"),
    "over_under_3.5": ("over_3.5", "under_3.5"),
}
MARKET_TO_COMPLETE_SET: dict[str, str] = {
    market: set_name for set_name, members in COMPLETE_OUTCOME_SETS.items() for market in members
}

EXCLUDED_DNB_MARKETS = frozenset(("dnb_home", "dnb_away"))


# ---------------------------------------------------------------------------
# Step 2: Read-only Betpawa margin check
# ---------------------------------------------------------------------------

def _load_price_dir(directory: Path) -> pd.DataFrame:
    """Load all price CSVs in a directory (read-only) and keep last snapshot strictly before kickoff."""
    if not directory.exists():
        return pd.DataFrame(columns=["snapshot_utc", "league", "home", "away", "kickoff_utc", "market", "betpawa_odds"])
    files = sorted(directory.glob("*.csv"))
    if not files:
        return pd.DataFrame(columns=["snapshot_utc", "league", "home", "away", "kickoff_utc", "market", "betpawa_odds"])
    parts = [pd.read_csv(f) for f in files]
    frame = pd.concat(parts, ignore_index=True)
    needed = ["snapshot_utc", "league", "home", "away", "kickoff_utc", "market", "betpawa_odds"]
    if not set(needed) <= set(frame.columns):
        return pd.DataFrame(columns=needed)
    frame = frame[needed].copy()
    frame["snapshot_utc"] = pd.to_datetime(frame["snapshot_utc"], utc=True, format="mixed").dt.tz_localize(None)
    frame["kickoff_utc"] = pd.to_datetime(frame["kickoff_utc"], utc=True, format="mixed").dt.tz_localize(None)
    frame["betpawa_odds"] = pd.to_numeric(frame["betpawa_odds"], errors="coerce")
    valid = (
        frame["snapshot_utc"].notna()
        & frame["kickoff_utc"].notna()
        & (frame["snapshot_utc"] < frame["kickoff_utc"])
        & frame["betpawa_odds"].notna()
        & (frame["betpawa_odds"] > 1.0)
    )
    frame = frame[valid].sort_values("snapshot_utc")
    if frame.empty:
        return frame
    return frame.groupby(["league", "home", "away", "kickoff_utc", "market"], as_index=False).last()


def _summarise_margin_group(last_prices: pd.DataFrame) -> dict[str, Any]:
    """Compute overround stats for complete outcome sets and logged match counts for unmeasurable markets."""
    if last_prices.empty:
        return {"complete_sets": {}, "unmeasurable": {}, "total_matches": 0}

    piv = last_prices.pivot(
        index=["league", "home", "away", "kickoff_utc"],
        columns="market",
        values="betpawa_odds",
    )
    total_matches = int(len(piv))
    complete_stats: dict[str, dict[str, Any]] = {}
    measurable_markets: set[str] = set()

    for set_name, members in COMPLETE_OUTCOME_SETS.items():
        if not all(m in piv.columns for m in members):
            continue
        sub = piv[list(members)].dropna()
        if sub.empty:
            continue
        overrounds = (1.0 / sub).sum(axis=1).to_numpy(float) - 1.0
        complete_stats[set_name] = {
            "members": members,
            "n": int(len(overrounds)),
            "mean": float(np.mean(overrounds)),
            "p10": float(np.percentile(overrounds, 10)),
            "p90": float(np.percentile(overrounds, 90)),
        }
        measurable_markets.update(members)

    unmeasurable: dict[str, int] = {}
    for market in sorted(piv.columns):
        if market in measurable_markets:
            continue
        unmeasurable[str(market)] = int(piv[market].notna().sum())

    return {
        "complete_sets": complete_stats,
        "unmeasurable": unmeasurable,
        "total_matches": total_matches,
    }


def run_margin_check(
    main_dir: Path = MAIN_PRICES_DIR,
    research_dir: Path = RESEARCH_PRICES_DIR,
) -> dict[str, Any]:
    """Read-only Betpawa overround check across main nine and research league price logs."""
    main_last = _load_price_dir(main_dir)
    research_last = _load_price_dir(research_dir)
    main_summary = _summarise_margin_group(main_last)
    research_summary = _summarise_margin_group(research_last)

    # Map each individual market to its main-nine mean overround (for Trial leg metadata), else None.
    market_margin_map: dict[str, float | None] = {}
    for set_name, info in main_summary["complete_sets"].items():
        for member in info["members"]:
            market_margin_map[member] = info["mean"]

    return {
        "main_nine": main_summary,
        "research_leagues": research_summary,
        "main_last_prices": main_last,
        "market_margin_map": market_margin_map,
    }


# ---------------------------------------------------------------------------
# Step 3: Eligible list parsed verbatim from existing study reports
# ---------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(r"^\|\s*(.+?)\s*\|$")


def _parse_markdown_table_rows(path: Path) -> list[tuple[int, list[str]]]:
    """Return (1-based line_no, stripped_cells) for data rows of markdown tables."""
    out: list[tuple[int, list[str]]] = []
    if not path.exists():
        return out
    for idx, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or all(set(c) <= set("-: ") for c in cells):
            continue
        if cells[0] == "League" and len(cells) >= 2 and cells[1] == "Market":
            continue
        out.append((idx, cells))
    return out


def _clean_gate(cell: str) -> str:
    return cell.replace("*", "").strip().upper()


def load_eligible_list(reports_dir: Path = REPORTS_DIR) -> dict[str, Any]:
    """Parse exact league x market PASS/FAIL lists from the task 10, 16, 17, 20, and 21 reports.

    A pair is TRIAL-ELIGIBLE iff:
      - it PASSED in both the original study (2024/25+) AND the replication period (2019/20-2023/24)
        ("Strong candidates"),
      - it is not FAIL or INSUFFICIENT in any backtest report, and
      - it is not Draw No Bet (excluded in v1: draw refund slip maths not implemented).
    """
    half_path = reports_dir / "half_markets_study.md"
    up_path = reports_dir / "up_markets_study.md"
    repl_path = reports_dir / "tasks_16_17_replication.md"
    timing_half_path = reports_dir / "timing_half_markets_study.md"
    new_markets_path = reports_dir / "new_markets_study.md"

    orig_status: dict[tuple[str, str], tuple[str, str]] = {}  # (league, market) -> (status, "file:line")
    for path in (half_path, up_path):
        for line_no, cells in _parse_markdown_table_rows(path):
            if len(cells) == 8:
                lg, mkt = cells[0], cells[1]
                orig_status[(lg, mkt)] = (_clean_gate(cells[6]), f"{path.name}:{line_no}")

    eligible: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    # Tasks 16 & 17 with replication in tasks_16_17_replication.md
    for line_no, cells in _parse_markdown_table_rows(repl_path):
        if len(cells) != 12:
            continue
        lg, mkt = cells[0], cells[1]
        g_prim = _clean_gate(cells[6])
        g_repl = _clean_gate(cells[10])
        verdict = cells[11]
        orig = orig_status.get((lg, mkt))
        orig_gate = orig[0] if orig else None
        orig_src = orig[1] if orig else "missing"
        repl_src = f"{repl_path.name}:{line_no}"
        family = "task16_half" if mkt in TASK16_MARKETS else "task17_up"
        if (
            orig_gate == "PASS"
            and g_prim == "PASS"
            and g_repl == "PASS"
            and verdict.startswith("Strong candidate")
        ):
            eligible.append({
                "league": lg,
                "market": mkt,
                "family": family,
                "original_source": orig_src,
                "replication_source": repl_src,
            })
        else:
            excluded.append({
                "league": lg,
                "market": mkt,
                "family": family,
                "reason": f"gate status original={orig_gate}, primary={g_prim}, replication={g_repl}",
                "source": f"{orig_src}; {repl_src}",
            })

    # Task 20 (timing + team-half, both periods in timing_half_markets_study.md)
    for line_no, cells in _parse_markdown_table_rows(timing_half_path):
        if len(cells) != 12:
            continue
        lg, mkt = cells[0], cells[1]
        g_prim = _clean_gate(cells[6])
        g_repl = _clean_gate(cells[10])
        verdict = cells[11]
        src = f"{timing_half_path.name}:{line_no}"
        family = "task20_timing" if mkt in TASK20_TIMING_MARKETS else "task20_team_half"
        if g_prim == "PASS" and g_repl == "PASS" and verdict.startswith("Strong candidate"):
            eligible.append({
                "league": lg,
                "market": mkt,
                "family": family,
                "original_source": src,
                "replication_source": src,
            })
        else:
            excluded.append({
                "league": lg,
                "market": mkt,
                "family": family,
                "reason": f"gate status primary={g_prim}, replication={g_repl}",
                "source": src,
            })

    # Task 10 (new_markets_study.md: team overs + DNB; NO replication period in repo)
    for line_no, cells in _parse_markdown_table_rows(new_markets_path):
        if len(cells) != 8:
            continue
        lg, mkt = cells[0], cells[1]
        gate = _clean_gate(cells[6])
        src = f"{new_markets_path.name}:{line_no}"
        if mkt in EXCLUDED_DNB_MARKETS:
            reason = (
                "excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw "
                f"(slip maths not implemented); task 10 gate={gate}"
            )
        elif gate != "PASS":
            reason = f"task 10 gate={gate} (and no replication-period report in repo)"
        else:
            reason = (
                "excluded in v1: passed 2024/25+ in new_markets_study.md, "
                "but no 2019/20-2023/24 replication report exists in engine/reports/"
            )
        excluded.append({
            "league": lg,
            "market": mkt,
            "family": "task10_team_goals_dnb",
            "reason": reason,
            "source": src,
        })

    eligible_set = {(e["league"], e["market"]) for e in eligible}
    return {
        "eligible": eligible,
        "eligible_set": eligible_set,
        "excluded": excluded,
    }


# ---------------------------------------------------------------------------
# Step 4: Live probability using the studies' exact functions and calibrators
# ---------------------------------------------------------------------------

def fit_league_calibrators(
    league: str,
    target_season: str,
    families: set[str],
) -> tuple[dict[str, Any], list[str]]:
    """Fit walk-forward Platt calibrators and historical shares strictly on seasons < target_season.

    Returns (bundle, dropped_reasons). Uses the exact study functions without creating any new model.
    """
    rho = league_rho(league)
    bundle: dict[str, Any] = {"rho": rho, "models": {}, "shares": {}}
    dropped: list[str] = []

    if "task16_half" in families or "task20_team_half" in families:
        htft = load_htft_matches(league)
        prior_htft = htft[htft["season"] < target_season].copy()
        if prior_htft.empty:
            dropped.append(f"{league}: no historical HT/FT matches before {target_season}")
        else:
            fh_mean = float((prior_htft.ht_home_goals + prior_htft.ht_away_goals).sum())
            ft_mean = float((prior_htft.home_goals + prior_htft.away_goals).sum())
            share_fh = fh_mean / ft_mean
            bundle["shares"]["fh"] = share_fh

            if "task16_half" in families:
                legs16, _ = build_task16_legs(prior_htft, league, rho)
                for mkt in TASK16_MARKETS:
                    past = legs16[legs16["market"] == mkt]
                    if past.empty or past["won"].nunique() < 2:
                        dropped.append(f"{league} {mkt}: insufficient history before {target_season}")
                        continue
                    model = LogisticRegression(C=1.0, max_iter=1000).fit(
                        _logit(past["bookmaker_probability"]).reshape(-1, 1),
                        past["won"],
                    )
                    bundle["models"][mkt] = model

            if "task20_team_half" in families:
                legs20h, _ = build_walkforward_half_legs(prior_htft, league, rho)
                for mkt in TASK20_TEAM_HALF_MARKETS:
                    past = legs20h[legs20h["market"] == mkt]
                    if past.empty or past["won"].nunique() < 2:
                        dropped.append(f"{league} {mkt}: insufficient history before {target_season}")
                        continue
                    model = LogisticRegression(C=1.0, max_iter=1000).fit(
                        _logit(past["bookmaker_probability"]).reshape(-1, 1),
                        past["won"],
                    )
                    bundle["models"][mkt] = model

    if "task17_up" in families:
        if league not in MAIN_LEAGUES:
            dropped.append(f"{league}: task17 UP markets only validated on five main leagues")
        else:
            df_up, _ = load_up_matches(league)
            prior_up = df_up[df_up["season"] < target_season].copy()
            if prior_up.empty:
                dropped.append(f"{league}: no reconciled UP matches before {target_season}")
            else:
                prior_up = add_up_raw_probabilities(prior_up, rho)
                for mkt in TASK17_MARKETS:
                    raw_col, act_col = f"raw_{mkt}", f"actual_{mkt}"
                    if prior_up[act_col].nunique() < 2:
                        dropped.append(f"{league} {mkt}: single outcome class before {target_season}")
                        continue
                    model = LogisticRegression(C=1.0, max_iter=1000).fit(
                        _logit(prior_up[raw_col]).reshape(-1, 1),
                        prior_up[act_col],
                    )
                    bundle["models"][mkt] = model

    if "task20_timing" in families:
        if league not in MAIN_LEAGUES:
            dropped.append(f"{league}: task20 timing markets only validated on five main leagues")
        else:
            df_t, _ = load_timing_matches(league)
            prior_t = df_t[df_t["season"] < target_season].copy()
            if prior_t.empty:
                dropped.append(f"{league}: no reconciled goal-timing matches before {target_season}")
            else:
                share_10 = float(prior_t["goals_10"].sum() / (prior_t["home_goals"] + prior_t["away_goals"]).sum())
                bundle["shares"]["10min"] = share_10
                legs20t, _ = build_walkforward_timing_legs(prior_t, league, rho)
                for mkt in TASK20_TIMING_MARKETS:
                    past = legs20t[legs20t["market"] == mkt]
                    if past.empty or past["won"].nunique() < 2:
                        dropped.append(f"{league} {mkt}: insufficient history before {target_season}")
                        continue
                    model = LogisticRegression(C=1.0, max_iter=1000).fit(
                        _logit(past["bookmaker_probability"]).reshape(-1, 1),
                        past["won"],
                    )
                    bundle["models"][mkt] = model

    return bundle, dropped


def fixture_trial_raw_probabilities(
    fixture: dict[str, Any],
    bundle: dict[str, Any],
) -> dict[str, float] | None:
    """Compute exact study raw probabilities for one upcoming fixture from its fair 1X2 + O/U 2.5 probs."""
    fair_map = {m["market"]: m.get("market_probability") for m in fixture.get("markets", [])}
    if any(fair_map.get(k) is None or float(fair_map[k]) <= 0 for k in FAIR_KEYS):
        return None
    _, (lam_home, lam_away), matrix = bookmaker_implied(
        *(1.0 / float(fair_map[k]) for k in FAIR_KEYS),
        bundle["rho"],
    )
    raw: dict[str, float] = {}
    if "fh" in bundle["shares"]:
        raw.update(half_market_raw_probabilities(lam_home, lam_away, bundle["shares"]["fh"]))
        raw.update(half_team_raw_probabilities(lam_home, lam_away, bundle["shares"]["fh"]))
    if "10min" in bundle["shares"]:
        raw.update(timing_market_raw_probabilities(lam_home, lam_away, bundle["shares"]["10min"]))
    if any(m in bundle["models"] for m in TASK17_MARKETS):
        raw.update(raw_up_probabilities_from_matrix(matrix))
    return raw


# ---------------------------------------------------------------------------
# Step 5: Trial slip construction (isolated from publishing)
# ---------------------------------------------------------------------------

def _main_slip_leg_keys(main_slips: dict[str, dict] | None) -> set[tuple[str, str]]:
    """Extract canonical (match_id_key, market) pairs already on Safe/Medium/Big slips."""
    used: set[tuple[str, str]] = set()
    if not main_slips:
        return used
    for slip in main_slips.values():
        if not slip:
            continue
        for leg in slip.get("legs", []):
            mkt = str(leg["market"])
            if "match_id" in leg and leg["match_id"] is not None:
                used.add((str(leg["match_id"]), mkt))
            lg = leg["league"]["code"] if isinstance(leg.get("league"), dict) else str(leg.get("league", ""))
            date = str(leg.get("date", ""))
            home = str(leg.get("home", ""))
            away = str(leg.get("away", ""))
            if home and away:
                used.add((f"{lg}|{date}|{home}|{away}", mkt))
                used.add((f"{home}|{away}|{date}", mkt))
    return used


def build_trial_slip(
    legs: pd.DataFrame,
    eligible_pairs: set[tuple[str, str]],
    main_slips: dict[str, dict] | None = None,
    market_margins: dict[str, float | None] | None = None,
) -> dict[str, Any] | None:
    """Build the daily Trial slip (3.0-5.0 odds, 2-4 legs, 1 leg/match) with accumulators.best_slip.

    Keeps ONLY legs in `eligible_pairs` with real Betpawa odds >= 1.05, excludes any leg whose
    match + market already appears on Safe/Medium/Big, and stamps `"trial": True` and
    `"stake_cap": 0.01` on the slip and every leg.
    """
    if legs.empty or not eligible_pairs:
        return None
    pool = legs.reset_index(drop=True).copy()
    required = {"match_id", "league", "home", "away", "date", "market", "probability", "odds"}
    if not required <= set(pool.columns):
        missing = sorted(required - set(pool.columns))
        raise ValueError(f"Trial leg pool missing required columns: {missing}")

    used_main = _main_slip_leg_keys(main_slips)
    margin_lookup = market_margins or {}

    keep = []
    for row in pool.itertuples(index=False):
        lg = str(row.league)
        mkt = str(row.market)
        mid = str(row.match_id)
        date = str(row.date)
        home = str(row.home)
        away = str(row.away)
        in_eligible = (lg, mkt) in eligible_pairs
        in_main = (
            (mid, mkt) in used_main
            or (f"{lg}|{date}|{home}|{away}", mkt) in used_main
            or (f"{home}|{away}|{date}", mkt) in used_main
        )
        valid_num = (
            pd.notna(row.odds)
            and float(row.odds) >= MIN_ODDS
            and pd.notna(row.probability)
            and 0.0 < float(row.probability) < 1.0
        )
        keep.append(in_eligible and not in_main and valid_num)

    pool = pool[np.array(keep, dtype=bool)].copy()
    if pool.empty:
        return None
    pool["match_id"] = pool["match_id"].astype(str)

    picks = best_slip(pool, TRIAL_TIER)
    if picks is None:
        return None
    chosen = pool.loc[picks]
    total_odds = float(chosen["odds"].prod())
    win_prob = float(chosen["probability"].prod())

    leg_dicts = []
    for row in chosen.itertuples(index=False):
        mkt = str(row.market)
        raw_p = float(getattr(row, "raw_probability", row.probability))
        margin = margin_lookup.get(mkt)
        leg_dicts.append({
            "match_id": str(row.match_id),
            "date": str(row.date),
            "league": str(row.league),
            "home": str(row.home),
            "away": str(row.away),
            "market": mkt,
            "probability": round(float(row.probability), 4),
            "raw_probability": round(raw_p, 4),
            "betpawa_odds": round(float(row.odds), 2),
            "fair_odds": round(1.0 / float(row.probability), 2),
            "trial": True,
            "stake_cap": TRIAL_STAKE_CAP,
            "margin": None if margin is None else round(float(margin), 4),
        })

    measured_margins = [leg["margin"] for leg in leg_dicts if leg["margin"] is not None]
    slip_margin = round(float(np.mean(measured_margins)), 4) if len(measured_margins) == len(leg_dicts) else None

    return {
        "tier": TRIAL_TIER.name,
        "trial": True,
        "stake_cap": TRIAL_STAKE_CAP,
        "total_odds": round(total_odds, 2),
        "win_probability": round(win_prob, 4),
        "expected_value": round(win_prob * total_odds - 1.0, 4),
        "odds_source": "betpawa",
        "margin": slip_margin,
        "legs": leg_dicts,
    }


# ---------------------------------------------------------------------------
# Step 6: Pre-registered Trial pause check helper (for later settled slips)
# ---------------------------------------------------------------------------

def evaluate_trial_pause(settled_slips: list[dict[str, Any]]) -> dict[str, Any]:
    """Pre-registered Trial pause rule: after >= 30 settled Trial slips, pause if one-sided z < -2.5."""
    n = len(settled_slips)
    if n == 0:
        return {"n": 0, "wins": 0, "expected_wins": 0.0, "z": None, "paused": False, "status": "INSUFFICIENT"}
    wins = sum(int(bool(s["won"])) for s in settled_slips)
    probs = np.array([float(s["win_probability"]) for s in settled_slips], dtype=float)
    exp_wins = float(probs.sum())
    sd = float(np.sqrt(np.sum(probs * (1.0 - probs))))
    z = (wins - exp_wins) / sd if sd > 0 else 0.0
    if n < PAUSE_MIN_SLIPS:
        return {"n": n, "wins": wins, "expected_wins": round(exp_wins, 2), "z": round(z, 3), "paused": False, "status": "COLLECTING"}
    paused = bool(z < PAUSE_Z_THRESHOLD)
    return {"n": n, "wins": wins, "expected_wins": round(exp_wins, 2), "z": round(z, 3), "paused": paused, "status": "PAUSED" if paused else "ACTIVE"}


# ---------------------------------------------------------------------------
# Dry-run driver (read-only inputs, writes ONLY engine/reports/trial_slip_dryrun.md)
# ---------------------------------------------------------------------------

def run_dry_run(
    predictions_path: Path = PREDICTIONS_PATH,
    main_prices_dir: Path = MAIN_PRICES_DIR,
    research_prices_dir: Path = RESEARCH_PRICES_DIR,
    reports_dir: Path = REPORTS_DIR,
    output_path: Path = REPORT_PATH,
) -> dict[str, Any]:
    """Execute Steps 2-5 on cached predictions and logged prices; write dry-run report only."""
    margins = run_margin_check(main_prices_dir, research_prices_dir)
    elig_info = load_eligible_list(reports_dir)
    eligible_set = elig_info["eligible_set"]
    family_by_pair = {(e["league"], e["market"]): e["family"] for e in elig_info["eligible"]}

    published = json.loads(predictions_path.read_text(encoding="utf-8"))
    fixtures_by_id = {f["id"]: f for f in published.get("fixtures", []) if isinstance(f, dict) and "id" in f}
    main_last = margins["main_last_prices"]
    price_lookup: dict[tuple[str, str, str, pd.Timestamp, str], float] = {}
    if not main_last.empty:
        for r in main_last.itertuples(index=False):
            price_lookup[(str(r.league), str(r.home), str(r.away), pd.Timestamp(r.kickoff_utc), str(r.market))] = float(r.betpawa_odds)

    # Fit calibrators lazily per (league, target_season) only for leagues present in cached predictions.
    calibrator_cache: dict[tuple[str, str], dict[str, Any]] = {}
    dropped_prob_reasons: list[str] = []
    day_results: list[dict[str, Any]] = []

    for day_entry in published.get("days", []):
        day_str = str(day_entry.get("date") or day_entry.get("day"))
        raw_fixtures = day_entry.get("fixtures", [])
        fixtures = [
            fixtures_by_id[item] if not isinstance(item, dict) else item
            for item in raw_fixtures
            if isinstance(item, dict) or item in fixtures_by_id
        ]
        main_slips = day_entry.get("slips", {})
        leg_rows: list[dict[str, Any]] = []
        skipped_fixtures: list[str] = []

        for f in fixtures:
            code = f["league"]["code"] if isinstance(f.get("league"), dict) else str(f.get("league", "EPL"))
            kickoff = pd.Timestamp(f["kickoff_utc"]).tz_localize(None)
            target_season = season_label(current_season_start(kickoff.date()))
            league_eligible_mkts = sorted(m for (lg, m) in eligible_set if lg == code)
            if not league_eligible_mkts:
                continue
            families = {family_by_pair[(code, m)] for m in league_eligible_mkts}
            cache_key = (code, target_season)
            if cache_key not in calibrator_cache:
                bundle, dropped = fit_league_calibrators(code, target_season, families)
                calibrator_cache[cache_key] = bundle
                dropped_prob_reasons.extend(dropped)
            bundle = calibrator_cache[cache_key]
            raw_probs = fixture_trial_raw_probabilities(f, bundle)
            if raw_probs is None:
                skipped_fixtures.append(f"{code} {f['home']} v {f['away']} ({f['date']}): missing fair 1X2 or O/U 2.5 probabilities")
                continue

            mid = f"{code}|{f['date']}|{f['home']}|{f['away']}"
            for mkt in league_eligible_mkts:
                if mkt not in raw_probs or mkt not in bundle["models"]:
                    continue
                odds = price_lookup.get((code, f["home"], f["away"], kickoff, mkt))
                if odds is None or odds < MIN_ODDS:
                    continue
                raw_p = float(raw_probs[mkt])
                model = bundle["models"][mkt]
                cal_p = float(np.clip(model.predict_proba(_logit([raw_p]).reshape(-1, 1))[0, 1], 1e-6, 1.0 - 1e-6))
                leg_rows.append({
                    "match_id": mid,
                    "league": code,
                    "home": f["home"],
                    "away": f["away"],
                    "date": f["date"],
                    "market": mkt,
                    "raw_probability": raw_p,
                    "probability": cal_p,
                    "odds": odds,
                })

        pool_df = pd.DataFrame(leg_rows)
        trial_slip = build_trial_slip(
            pool_df,
            eligible_set,
            main_slips=main_slips,
            market_margins=margins["market_margin_map"],
        )
        day_results.append({
            "date": day_str,
            "fixtures_count": len(fixtures),
            "fixtures": [(f["league"]["code"] if isinstance(f.get("league"), dict) else f.get("league"), f["home"], f["away"]) for f in fixtures],
            "priced_eligible_legs": len(leg_rows),
            "priced_eligible_matches": int(pool_df["match_id"].nunique()) if not pool_df.empty else 0,
            "main_slip_tiers": sorted(main_slips.keys()),
            "skipped_fixtures": skipped_fixtures,
            "trial_slip": trial_slip,
        })

    report_text = _format_dryrun_report(
        published=published,
        margins=margins,
        elig_info=elig_info,
        dropped_prob_reasons=dropped_prob_reasons,
        day_results=day_results,
    )
    output_path.write_text(report_text, encoding="utf-8")
    return {
        "margins": margins,
        "eligible": elig_info,
        "dropped_prob_reasons": dropped_prob_reasons,
        "day_results": day_results,
        "report_path": output_path,
    }


def _format_dryrun_report(
    published: dict[str, Any],
    margins: dict[str, Any],
    elig_info: dict[str, Any],
    dropped_prob_reasons: list[str],
    day_results: list[dict[str, Any]],
) -> str:
    now_eat = datetime.now(timezone.utc).astimezone(EAT).strftime("%Y-%m-%d %H:%M EAT")
    gen_eat = pd.Timestamp(published["generated_at"]).tz_convert(EAT).strftime("%Y-%m-%d %H:%M EAT")

    lines = [
        "# Daily Trial slip design, margin check, and dry run (PROJECT.md task 27)",
        "",
        f"Generated: **{now_eat}** | Cached `predictions.json` generated: **{gen_eat}**.",
        "",
        "> **Research & dry run only**: nothing here is live. `web/public/data`, `engine/data/live`, `predict.py`, `accumulators.py`, `market_gates.json`, and `web/` are untouched.",
        "> **Scope & honesty**: the Trial slip does **not** collect more data than research price logging already does, and it does **not** prove profitability or an edge. Stake cap is fixed by the owner at **1% of balance (`0.01`)** per Trial slip.",
        "",
        "## Step 2 — Betpawa margin check (read-only, last snapshot before kick-off)",
        "",
        "Overround = `sum(1 / odds) - 1` computed strictly on complete mutually exclusive outcome sets logged before kick-off (`snapshot_utc < kickoff_utc`, `odds > 1.0`).",
        "",
        "### Complete outcome sets (measurable overround)",
        "",
        "| League group | Outcome set | Logged markets | Matches (n) | Mean overround | 10th pct | 90th pct |",
        "|---|---|---|---:|---:|---:|---:|",
    ]

    for group_label, key in (("Main nine", "main_nine"), ("Research leagues", "research_leagues")):
        g = margins[key]
        if not g["complete_sets"]:
            lines.append(f"| {group_label} | (none) | — | 0 | n/a | n/a | n/a |")
            continue
        for set_name, info in g["complete_sets"].items():
            members_str = ", ".join(f"`{m}`" for m in info["members"])
            lines.append(
                f"| {group_label} | `{set_name}` | {members_str} | {info['n']:,} | "
                f"{info['mean']:+.2%} | {info['p10']:+.2%} | {info['p90']:+.2%} |"
            )

    lines += [
        "",
        "Notes on complete sets:",
        "- `main nine` (`engine/data/live/prices`) logs `SLIP_MARKETS` + `RESEARCH_MARKETS`; `draw` is not in `SLIP_MARKETS`, so full `1x2` overround is not measurable from `engine/data/live/prices` (while `engine/data/live/research/prices` logs `home_win`, `draw`, `away_win`, `over_2.5`, `under_2.5` + `RESEARCH_MARKETS`, making `1x2` measurable there).",
        "- `double_1x`, `double_x2`, `double_12` overlap pairwise (each 1X2 outcome appears in two selections, so probabilities sum to 2, not 1) and are therefore not included in the `sum(1/odds) - 1` table.",
        "- `first_goal_home` / `first_goal_away` omit the third outcome (`None`, 0-0), and `home_2up` / `away_2up` omit draw, so their overrounds are not measurable.",
        "",
        "### Markets without a complete complementary set logged (`margin not measurable`)",
        "",
        "| Market | Main nine logged matches | Research leagues logged matches | Margin status |",
        "|---|---:|---:|---|",
    ]
    all_unmeas = sorted(
        set(margins["main_nine"]["unmeasurable"]) | set(margins["research_leagues"]["unmeasurable"])
    )
    for mkt in all_unmeas:
        m_n = margins["main_nine"]["unmeasurable"].get(mkt, 0)
        r_n = margins["research_leagues"]["unmeasurable"].get(mkt, 0)
        lines.append(f"| `{mkt}` | {m_n:,} | {r_n:,} | margin not measurable |")

    # Step 3
    elig = elig_info["eligible"]
    excl = elig_info["excluded"]
    by_family: dict[str, int] = {}
    for e in elig:
        by_family[e["family"]] = by_family.get(e["family"], 0) + 1

    lines += [
        "",
        "## Step 3 — TRIAL-ELIGIBLE list (Strong candidates only)",
        "",
        f"Total TRIAL-ELIGIBLE pairs: **{len(elig)}** across {len({e['market'] for e in elig})} distinct markets "
        f"(`task16_half`: {by_family.get('task16_half', 0)}, `task17_up`: {by_family.get('task17_up', 0)}, "
        f"`task20_timing`: {by_family.get('task20_timing', 0)}, `task20_team_half`: {by_family.get('task20_team_half', 0)}).",
        "",
        "### Explicit exclusions in v1",
        "- **Draw No Bet (`dnb_home`, `dnb_away`)**: excluded in v1 because a draw refunds the leg at odds `1.00`, and `accumulators.best_slip` / slip win-probability maths do not implement push/refund legs (`new_markets_study.md:9-10, 15-16, 21-22, 27-28, 33-34`).",
        "- **Team overs from Task 10 (`home_over_0.5`, `away_over_0.5`, `home_over_1.5`, `away_over_1.5`)**: excluded in v1 because Task 10 (`new_markets_study.md`) was evaluated on `2024/25+` only and has **no `2019/20-2023/24` replication report** in `engine/reports/` (`19` pairs passed `2024/25+`, `SERIEA home_over_0.5` FAILED at `new_markets_study.md:17`). Per the pre-registered rule, only pairs that passed BOTH original and replication periods (`Strong candidates`) enter v1.",
        f"- **Other excluded pairs (failed original or replication gate)**: {sum(e['family'] != 'task10_team_goals_dnb' for e in excl)} pairs across Tasks 16, 17, and 20.",
        "",
        "### Complete TRIAL-ELIGIBLE table (with source file and line)",
        "",
        "| # | League | Market | Family | Original source | Replication source |",
        "|---:|---|---|---|---|---|",
    ]
    for i, e in enumerate(elig, start=1):
        lines.append(
            f"| {i} | {e['league']} | `{e['market']}` | `{e['family']}` | `{e['original_source']}` | `{e['replication_source']}` |"
        )

    lines += [
        "",
        "### Excluded pairs audit (Tasks 10, 16, 17, 20)",
        "",
        "| League | Market | Family | Reason | Source |",
        "|---|---|---|---|---|",
    ]
    for ex in excl:
        lines.append(f"| {ex['league']} | `{ex['market']}` | `{ex['family']}` | {ex['reason']} | `{ex['source']}` |")

    # Step 4
    lines += [
        "",
        "## Step 4 — Live probability verification",
        "",
        "- Every eligible family (`task16_half`, `task17_up`, `task20_timing`, `task20_team_half`) is scored by reusing its exact study raw-probability function (`half_markets_study.half_market_raw_probabilities`, `up_markets_study.raw_up_probabilities_from_matrix`, `timing_half_markets_study.timing_market_raw_probabilities`, `timing_half_markets_study.half_team_raw_probabilities`) on `accumulators.bookmaker_implied` lambdas/score matrix reconstructed from the cached fixture's fair 1X2 + O/U 2.5 `market_probability` and `league_rho(league)`.",
        "- Historical shares (`s`, `w`) and Platt calibrators (`LogisticRegression(C=1.0)` on `logit(raw)`) are fitted strictly on seasons `< target_season` (`< 2026/27`). No new model is created.",
    ]
    if dropped_prob_reasons:
        lines.append("- Dropped during live probability fitting:")
        for r in dropped_prob_reasons:
            lines.append(f"  - {r}")
    else:
        lines.append("- **0 eligible markets dropped** for live probability reproducibility on the cached fixtures' leagues.")

    # Step 5
    lines += [
        "",
        "## Step 5 — Dry run on cached `web/public/data/predictions.json`",
        "",
        f"Tier: `Tier('trial', min_odds={TRIAL_TIER.min_odds}, max_odds={TRIAL_TIER.max_odds}, "
        f"min_legs={TRIAL_TIER.min_legs}, max_legs={TRIAL_TIER.max_legs})`, `stake_cap = {TRIAL_STAKE_CAP:.2f}` (1%), "
        "`trial = true`, real Betpawa prices only (`odds >= 1.05`), one leg per match, excluding any `match + market` on Safe/Medium/Big.",
        "",
    ]
    for dr in day_results:
        lines += [
            f"### Day `{dr['date']}`",
            "",
            f"- Cached fixtures: **{dr['fixtures_count']}** ("
            + ", ".join(f"{lg}: {h} v {a}" for lg, h, a in dr["fixtures"])
            + ").",
            f"- Main slip tiers present: {', '.join(dr['main_slip_tiers']) if dr['main_slip_tiers'] else 'none'}.",
            f"- Priced TRIAL-ELIGIBLE candidate legs (from `engine/data/live/prices`, pre-kickoff, `odds >= 1.05`): "
            f"**{dr['priced_eligible_legs']} legs** across **{dr['priced_eligible_matches']} matches**.",
        ]
        for sk in dr["skipped_fixtures"]:
            lines.append(f"- Skipped fixture: {sk}")
        slip = dr["trial_slip"]
        if slip is None:
            lines += ["", "**Trial slip result**: No valid Trial slip in `3.0-5.0` odds with `2-4` legs on this day.", ""]
        else:
            margin_txt = "not measurable" if slip["margin"] is None else f"{slip['margin']:+.2%}"
            lines += [
                "",
                f"**Trial slip selected** (`trial: {str(slip['trial']).lower()}`, `stake_cap: {slip['stake_cap']:.2f}`, "
                f"total odds **{slip['total_odds']:.2f}**, predicted win **{slip['win_probability']:.2%}**, "
                f"EV `{slip['expected_value']:+.4f}`, odds source `{slip['odds_source']}`, slip margin: {margin_txt}):",
                "",
                "| League | Match | Market | Raw p | Calibrated p | Betpawa odds | Fair odds | Margin (Step 2) | trial | stake_cap |",
                "|---|---|---|---:|---:|---:|---:|---|---|---:|",
            ]
            for leg in slip["legs"]:
                m_str = "not measurable" if leg["margin"] is None else f"{leg['margin']:+.2%}"
                lines.append(
                    f"| {leg['league']} | {leg['home']} v {leg['away']} | `{leg['market']}` | "
                    f"{leg['raw_probability']:.4f} | {leg['probability']:.4f} | {leg['betpawa_odds']:.2f} | "
                    f"{leg['fair_odds']:.2f} | {m_str} | `{str(leg['trial']).lower()}` | {leg['stake_cap']:.2f} |"
                )
            lines.append("")

    # Step 6
    lines += [
        "## Step 6 — Pre-registered judgement rules (locked before any live Trial slip)",
        "",
        "- **PROMOTION** of a league x market to main slips: unchanged existing rule (`>= 300` settled Betpawa-priced legs, one-sided level check passes, and `pair_monitor` not paused).",
        "- **PAUSE** of the whole Trial: after `>= 30` settled Trial slips, if actual win rate is below predicted with one-sided `z < -2.5` (`z = (wins - sum p) / sqrt(sum p(1 - p))`), pause the Trial.",
        "- **Reporting cadence (every 30 settled Trial slips)**: report predicted vs actual win rate with Wilson 95% CI, return per unit staked, per-market leg results, and the share of days every slip (main + Trial) lost.",
        "",
        "## What was NOT checked",
        "",
        "- **No historical Trial slip backtest at real Betpawa prices**: real Betpawa prices for most Trial markets only started logging on 2026-11-07 (and were paused during the Understat outage until 2026-11-21), so historical slip-level winner's curse cannot yet be measured at real prices.",
        "- **No Task 10 replication**: team overs (`home_over_0.5/1.5`, `away_over_0.5/1.5`) were excluded from v1 because `new_markets_study.md` has no `2019/20-2023/24` replication report; replicating Task 10 is a separate pre-registered task if desired.",
        "- **No Draw No Bet refund slip maths**: `dnb_home`/`dnb_away` are excluded from v1 because `best_slip` and slip win-probability products do not model odds-`1.00` pushes on draws.",
        "- **No live publishing, booking-code generation, or web UI rendering**: this task is strictly offline research and dry run.",
        "- **No margin measurement for single-sided logged markets**: Betpawa complementary prices (e.g. Under 0.5/1.5 halves, No on win/score halves, `None` on first goal, Draw on 2UP) are not logged in `prices/*.csv`, so overround is unknown for 21 of the 24 eligible Trial markets (only `interval_10_*` has a complete 3-way set logged).",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily Trial slip dry run (research only).")
    parser.add_argument("--dry-run", action="store_true", help="Run margin check, eligible list, and dry run on cached predictions.")
    args = parser.parse_args()
    if not args.dry_run:
        parser.error("Only --dry-run is supported in research mode.")
    result = run_dry_run()
    print(f"Wrote {result['report_path']}")
    for dr in result["day_results"]:
        slip = dr["trial_slip"]
        if slip is None:
            print(f"{dr['date']}: no valid Trial slip ({dr['priced_eligible_legs']} candidate legs)")
        else:
            print(
                f"{dr['date']}: Trial slip {len(slip['legs'])} legs @ {slip['total_odds']:.2f} "
                f"(p={slip['win_probability']:.2%}, stake_cap={slip['stake_cap']})"
            )


if __name__ == "__main__":
    main()
