"""PROJECT.md task 29: Big favourites calibration study (pre-registered 2026-11-23, research only).

Tests whether big favourites (favourite strength F = p(S_win) >= 0.70) win more often than
predicted across win, 1Up, and win-or-draw markets, in:
  - Primary data: diversity_study.load_legs() pool (5 main leagues, 2024/25+), WITHOUT
    removing gate-FAIL pairs (gate-FAIL legs also reported separately).
  - Replication data: 2019/20-2023/24 across all 9 live leagues using exact existing
    walk-forward live methods (EPL blended where available; other 8 leagues calibrated
    bookmaker consensus). Anything that cannot be reproduced exactly is reported as
    NOT AVAILABLE.
  - Live archive (web/public/data/archive): descriptive holdout only (never fitted on).

Step 1 -> Step 2 (walk-forward single logit shift d on F >= 0.70) -> Step 3 (slip-level
check with live task-24 no-identical-leg rule). Steps 2 and 3 run ONLY for markets that
passed the previous step. Research only; no live changes.

Usage (from ``engine``):
    python -m src.favourites_study
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression

from .accumulators import (
    SLIP_MARKETS,
    TIERS,
    _wilson,
    best_slip,
    blend,
    bookmaker_implied,
    build_validation_leg_table,
    calibrate_market_probabilities,
    fit_model_weight,
)
from .diversity_study import MAIN_LEAGUES, failed_gates
from .leagues import ENGINE_DIR, LEAGUES, get_league, paths
from .market_live import league_rho
from .new_league_config import NEW_LEAGUES
from .new_leagues_study import CACHE as NEW_LEAGUES_CACHE, odds_columns

REPORT_PATH = ENGINE_DIR / "reports" / "favourites_study.md"
ARCHIVE_DIR = ENGINE_DIR.parent / "web" / "public" / "data" / "archive"
EAT = ZoneInfo("Africa/Dar_es_Salaam")

BOOTSTRAP_RESAMPLES = 2_000
BOOTSTRAP_SEED = 20261124
BIG_FAV_THRESHOLD = 0.70
CLIP_LOW = 0.001
CLIP_HIGH = 0.999

REPL_SEASONS: tuple[str, ...] = ("2019/20", "2020/21", "2021/22", "2022/23", "2023/24")
PRIMARY_SEASONS: tuple[str, ...] = ("2024/25", "2025/26", "2026/27")
FAV_MARKETS: tuple[str, ...] = ("win", "1up", "win_or_draw")
FAV_MARKET_LABELS: dict[str, str] = {
    "win": "Favourite to win",
    "1up": "Favourite 1Up",
    "win_or_draw": "Favourite win or draw",
}
FAV_BANDS: tuple[tuple[str, float, float], ...] = (
    ("<0.60", 0.00, 0.60),
    ("0.60-0.70", 0.60, 0.70),
    ("0.70-0.80", 0.70, 0.80),
    (">=0.80", 0.80, 1.01),
)
ALL_BANDS: tuple[tuple[str, float, float], ...] = (
    *FAV_BANDS,
    (">=0.70 (big fav)", BIG_FAV_THRESHOLD, 1.01),
)
SIDE_MARKET_MAP: dict[str, dict[str, str]] = {
    "home": {"win": "home_win", "1up": "home_1up", "win_or_draw": "double_1x"},
    "away": {"win": "away_win", "1up": "away_1up", "win_or_draw": "double_x2"},
}
OWNER_EXCLUDED_MARKETS = frozenset(("under_2.5", "under_3.5"))
AVG_ODDS_COLS = ("avg_odds_home", "avg_odds_draw", "avg_odds_away", "avg_odds_over25", "avg_odds_under25")
NEW_LEAGUE_DIV = {"EREDIV": "N1", "JUPILER": "B1", "PRIMEIRA": "P1", "SUPERLIG": "T1"}


# ---------------------------------------------------------------------------
# Core statistics (whole-day bootstrap, Wilson CI, log loss)
# ---------------------------------------------------------------------------

def _clip_prob(p: np.ndarray | pd.Series | float, lo: float = 1e-6, hi: float = 1.0 - 1e-6) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), lo, hi)


def _leg_log_loss(p: np.ndarray, y: np.ndarray) -> np.ndarray:
    q = _clip_prob(p, 1e-6, 1.0 - 1e-6)
    y_arr = np.asarray(y, dtype=float)
    return -(y_arr * np.log(q) + (1.0 - y_arr) * np.log(1.0 - q))


def whole_day_bootstrap_mean(
    dates: pd.Series,
    values: np.ndarray,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float, float]:
    """Mean of `values` and its 95% CI from whole-day ratio bootstrap resamples."""
    vals = np.asarray(values, dtype=float)
    if len(vals) == 0:
        return float("nan"), float("nan"), float("nan")
    day_keys = pd.to_datetime(dates).dt.strftime("%Y-%m-%d")
    grouped = pd.Series(vals).groupby(day_keys.to_numpy(), sort=True).agg(["sum", "size"])
    sums = grouped["sum"].to_numpy(dtype=float)
    counts = grouped["size"].to_numpy(dtype=float)
    point = float(sums.sum() / counts.sum())
    if len(sums) == 1:
        return point, point, point
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(sums), size=(resamples, len(sums)))
    boot = sums[picks].sum(axis=1) / counts[picks].sum(axis=1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    return point, float(lo), float(hi)


# ---------------------------------------------------------------------------
# Favourite identification (fixed definitions)
# ---------------------------------------------------------------------------

def assign_favourites(legs: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Identify per-match favourite side S and strength F = p(S_win), returning favourite legs.

    Rules (PROJECT.md task 29):
      - S = 'home' if p(home_win) >= p(away_win) else 'away' (requires both home_win and away_win).
      - F = p(S_win).
      - Favourite markets: win (S_win), 1up (S_1up), win_or_draw (double_1x / double_x2).
      - Unknown outcomes (won is null/NaN) are excluded and NEVER counted as losses.
    """
    if legs.empty:
        return pd.DataFrame(columns=[
            "match_key", "date", "season", "league", "market", "fav_market",
            "fav_side", "fav_strength", "probability", "won", "is_gate_fail",
        ]), {"matches_missing_win_side": 0, "dropped_unknown_outcomes": 0}

    df = legs.copy()
    if "match_key" not in df.columns:
        if "league" in df.columns:
            df["match_key"] = df["league"].astype(str) + ":" + df["match_id"].astype(str)
        else:
            df["match_key"] = df["match_id"].astype(str)
    if "is_gate_fail" not in df.columns:
        df["is_gate_fail"] = False

    win_rows = df[df["market"].isin(("home_win", "away_win"))].dropna(subset=["probability"])
    piv = win_rows.pivot_table(index="match_key", columns="market", values="probability", aggfunc="first")
    total_win_matches = len(piv)
    if not {"home_win", "away_win"} <= set(piv.columns):
        return pd.DataFrame(columns=[
            "match_key", "date", "season", "league", "market", "fav_market",
            "fav_side", "fav_strength", "probability", "won", "is_gate_fail",
        ]), {"matches_missing_win_side": total_win_matches, "dropped_unknown_outcomes": 0}

    valid_piv = piv.dropna(subset=["home_win", "away_win"])
    missing_win_side = int(total_win_matches - len(valid_piv))
    fav_side = np.where(valid_piv["home_win"] >= valid_piv["away_win"], "home", "away")
    fav_strength = np.where(valid_piv["home_win"] >= valid_piv["away_win"], valid_piv["home_win"], valid_piv["away_win"])
    match_meta = pd.DataFrame({
        "match_key": valid_piv.index,
        "fav_side": fav_side,
        "fav_strength": fav_strength.astype(float),
    })

    merged = df.merge(match_meta, on="match_key", how="inner")
    # Map each row's market to its favourite market category if it belongs to side S.
    is_home = merged["fav_side"] == "home"
    fav_market = np.select(
        [
            (is_home & (merged["market"] == "home_win")) | (~is_home & (merged["market"] == "away_win")),
            (is_home & (merged["market"] == "home_1up")) | (~is_home & (merged["market"] == "away_1up")),
            (is_home & (merged["market"] == "double_1x")) | (~is_home & (merged["market"] == "double_x2")),
        ],
        ["win", "1up", "win_or_draw"],
        default="",
    )
    merged["fav_market"] = fav_market
    fav = merged[merged["fav_market"] != ""].copy()

    # Unknown outcomes (won is null) are dropped, NEVER counted as losses.
    unknown_count = int(fav["won"].isna().sum())
    fav = fav.dropna(subset=["won", "probability", "date"]).copy()
    fav["won"] = fav["won"].astype(int)
    fav["probability"] = fav["probability"].astype(float)
    fav["date"] = pd.to_datetime(fav["date"])
    return fav.reset_index(drop=True), {
        "matches_missing_win_side": missing_win_side,
        "dropped_unknown_outcomes": unknown_count,
    }


def evaluate_gap_slice(
    frame: pd.DataFrame,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Compute n_legs, n_matches, predicted, actual, Wilson CI, gap, and whole-day bootstrap 95% CI."""
    clean = frame.dropna(subset=["won", "probability", "date"])
    n_legs = int(len(clean))
    if n_legs == 0:
        return {
            "n_legs": 0, "n_matches": 0, "n_days": 0,
            "predicted": float("nan"), "actual": float("nan"),
            "wilson_low": float("nan"), "wilson_high": float("nan"),
            "gap": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"),
        }
    n_matches = int(clean["match_key"].nunique())
    n_days = int(pd.to_datetime(clean["date"]).dt.strftime("%Y-%m-%d").nunique())
    y = clean["won"].to_numpy(dtype=float)
    p = clean["probability"].to_numpy(dtype=float)
    wins = int(np.sum(y))
    pred = float(np.mean(p))
    actual = float(np.mean(y))
    w_lo, w_hi = _wilson(wins, n_legs)
    gap, ci_lo, ci_hi = whole_day_bootstrap_mean(clean["date"], y - p, resamples=resamples, seed=seed)
    return {
        "n_legs": n_legs, "n_matches": n_matches, "n_days": n_days,
        "predicted": pred, "actual": actual,
        "wilson_low": float(w_lo), "wilson_high": float(w_hi),
        "gap": gap, "ci_low": ci_lo, "ci_high": ci_hi,
    }


def evaluate_step1(
    fav_legs: pd.DataFrame,
    leagues: tuple[str, ...] | None = None,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run Step 1 across all markets, bands, gate-FAIL split, and per-league F >= 0.70."""
    by_market_band: dict[str, list[dict[str, Any]]] = {}
    big_fav_summary: dict[str, dict[str, Any]] = {}
    gate_fail_rows: list[dict[str, Any]] = []
    per_league_big: dict[str, list[dict[str, Any]]] = {}

    league_list = list(leagues) if leagues is not None else sorted(fav_legs["league"].unique().tolist())

    for mkt in FAV_MARKETS:
        m_df = fav_legs[fav_legs["fav_market"] == mkt]
        band_rows = []
        for label, lo, hi in ALL_BANDS:
            sub = m_df[(m_df["fav_strength"] >= lo) & (m_df["fav_strength"] < hi)]
            row = {"market": mkt, "band": label, **evaluate_gap_slice(sub, resamples=resamples, seed=seed)}
            band_rows.append(row)
            if label == ">=0.70 (big fav)":
                big_fav_summary[mkt] = row
        by_market_band[mkt] = band_rows

        # Gate-FAIL separate row (all F and F >= 0.70)
        if "is_gate_fail" in m_df.columns:
            for scope_label, subset in (("all", m_df), (">=0.70 (big fav)", m_df[m_df["fav_strength"] >= BIG_FAV_THRESHOLD])):
                gf = subset[subset["is_gate_fail"].astype(bool)]
                gp = subset[~subset["is_gate_fail"].astype(bool)]
                gate_fail_rows.append({
                    "market": mkt, "scope": scope_label, "group": "gate_FAIL",
                    **evaluate_gap_slice(gf, resamples=resamples, seed=seed),
                })
                gate_fail_rows.append({
                    "market": mkt, "scope": scope_label, "group": "gate_PASS",
                    **evaluate_gap_slice(gp, resamples=resamples, seed=seed),
                })

        # Per-league rows for F >= 0.70
        lg_rows = []
        big_m = m_df[m_df["fav_strength"] >= BIG_FAV_THRESHOLD]
        for code in league_list:
            sub = big_m[big_m["league"] == code]
            lg_rows.append({"market": mkt, "league": code, **evaluate_gap_slice(sub, resamples=resamples, seed=seed)})
        per_league_big[mkt] = lg_rows

    return {
        "by_market_band": by_market_band,
        "big_fav": big_fav_summary,
        "gate_fail_rows": gate_fail_rows,
        "per_league_big": per_league_big,
    }


def step1_market_passes(primary_big: dict[str, Any], repl_big: dict[str, Any]) -> bool:
    """Step 1 pass condition: primary CI low > 0 AND replication gap > 0 with CI low > 0."""
    return bool(
        primary_big["n_legs"] > 0
        and repl_big["n_legs"] > 0
        and np.isfinite(primary_big["ci_low"])
        and primary_big["ci_low"] > 0.0
        and np.isfinite(repl_big["gap"])
        and repl_big["gap"] > 0.0
        and np.isfinite(repl_big["ci_low"])
        and repl_big["ci_low"] > 0.0
    )


# ---------------------------------------------------------------------------
# Step 2: Walk-forward single logit shift d on F >= 0.70
# ---------------------------------------------------------------------------

def fit_logit_shift(probabilities: np.ndarray | pd.Series, outcomes: np.ndarray | pd.Series) -> float:
    """Fit single scalar logit shift d minimising binary cross-entropy of clip(sigmoid(logit(p) + d))."""
    p = _clip_prob(probabilities, 1e-6, 1.0 - 1e-6)
    y = np.asarray(outcomes, dtype=float)
    if len(p) == 0:
        return 0.0
    base_logit = logit(p)

    def objective(d: float) -> float:
        q = np.clip(expit(base_logit + d), CLIP_LOW, CLIP_HIGH)
        return float(-np.mean(y * np.log(q) + (1.0 - y) * np.log(1.0 - q)))

    res = minimize_scalar(objective, bounds=(-3.0, 3.0), method="bounded")
    return float(res.x)


def apply_big_fav_shift(legs: pd.DataFrame, fav_market: str, shift_d: float) -> pd.DataFrame:
    """Apply logit shift `shift_d` ONLY to `fav_market` legs with F >= 0.70.

    Guarantees:
      - No leg with F < 0.70 or non-favourite market is changed.
      - Clipped to [0.001, 0.999].
      - Per-match probability order preserved: win <= win_or_draw and win <= 1up.
    """
    if fav_market not in FAV_MARKETS:
        raise ValueError(f"Unknown fav_market: {fav_market}")
    out = legs.copy()
    if out.empty or shift_d == 0.0:
        return out

    if "match_key" not in out.columns:
        out["match_key"] = (
            out["league"].astype(str) + ":" + out["match_id"].astype(str)
            if "league" in out.columns else out["match_id"].astype(str)
        )

    win_rows = out[out["market"].isin(("home_win", "away_win"))].dropna(subset=["probability"])
    piv = win_rows.pivot_table(index="match_key", columns="market", values="probability", aggfunc="first")
    if not {"home_win", "away_win"} <= set(piv.columns):
        return out
    valid_piv = piv.dropna(subset=["home_win", "away_win"])
    side_map = {
        mk: ("home" if hw >= aw else "away")
        for mk, hw, aw in zip(valid_piv.index, valid_piv["home_win"], valid_piv["away_win"])
    }
    strength_map = {
        mk: float(max(hw, aw))
        for mk, hw, aw in zip(valid_piv.index, valid_piv["home_win"], valid_piv["away_win"])
    }

    # Pre-index per-match reference probabilities for coherence bounds (same side S).
    ref_probs: dict[tuple[str, str], float] = {}
    for mk, mkt, prob in zip(out["match_key"], out["market"], out["probability"]):
        if pd.notna(prob) and mkt in ("home_win", "away_win", "home_1up", "away_1up", "double_1x", "double_x2"):
            ref_probs[(mk, mkt)] = float(prob)

    new_probs = out["probability"].to_numpy(dtype=float).copy()
    for idx, (mk, mkt, prob) in enumerate(zip(out["match_key"], out["market"], out["probability"])):
        if pd.isna(prob) or mk not in side_map:
            continue
        side = side_map[mk]
        if strength_map[mk] < BIG_FAV_THRESHOLD:
            continue
        target_mkt = SIDE_MARKET_MAP[side][fav_market]
        if mkt != target_mkt:
            continue

        shifted = float(np.clip(expit(logit(_clip_prob(prob, 1e-6, 1.0 - 1e-6)) + shift_d), CLIP_LOW, CLIP_HIGH))
        # Enforce win <= win_or_draw and win <= 1up without modifying untouched markets.
        if fav_market == "win":
            upper_bounds = [CLIP_HIGH]
            for other_key in ("win_or_draw", "1up"):
                other_mkt = SIDE_MARKET_MAP[side][other_key]
                if (mk, other_mkt) in ref_probs:
                    upper_bounds.append(ref_probs[(mk, other_mkt)])
            shifted = min(shifted, min(upper_bounds))
        else:
            win_mkt = SIDE_MARKET_MAP[side]["win"]
            if (mk, win_mkt) in ref_probs:
                shifted = max(shifted, ref_probs[(mk, win_mkt)])
        new_probs[idx] = float(np.clip(shifted, CLIP_LOW, CLIP_HIGH))

    out["probability"] = new_probs
    return out


def run_step2_walkforward(
    all_legs: pd.DataFrame,
    test_seasons: tuple[str, ...] | list[str],
    fav_market: str,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Walk-forward Step 2: fit logit shift d on seasons < S (F >= 0.70), evaluate log-loss change on season S."""
    shifts: dict[str, float] = {}
    train_counts: dict[str, int] = {}
    corrected_parts: list[pd.DataFrame] = []
    eval_rows: list[pd.DataFrame] = []

    fav_all, _ = assign_favourites(all_legs)
    for season in sorted(test_seasons):
        prior_big = fav_all[
            (fav_all["season"] < season)
            & (fav_all["fav_market"] == fav_market)
            & (fav_all["fav_strength"] >= BIG_FAV_THRESHOLD)
        ]
        d_val = fit_logit_shift(prior_big["probability"], prior_big["won"]) if not prior_big.empty else 0.0
        shifts[season] = d_val
        train_counts[season] = int(len(prior_big))

        season_legs = all_legs[all_legs["season"] == season].copy()
        if season_legs.empty:
            continue
        corrected_season = apply_big_fav_shift(season_legs, fav_market, d_val)
        corrected_parts.append(corrected_season)

        # Pair current vs corrected on this season's favourite legs for fav_market (known outcomes only).
        cur_fav, _ = assign_favourites(season_legs)
        cur_mkt = cur_fav[cur_fav["fav_market"] == fav_market][
            ["match_key", "date", "season", "league", "market", "fav_strength", "probability", "won"]
        ].rename(columns={"probability": "p_current"})
        cor_lookup = corrected_season[["match_key", "market", "probability"]].rename(columns={"probability": "p_corrected"})
        paired = cur_mkt.merge(cor_lookup, on=["match_key", "market"], how="inner")
        eval_rows.append(paired)

    if not eval_rows:
        return {
            "market": fav_market, "shifts": shifts, "train_counts": train_counts,
            "n_legs": 0, "n_big_legs": 0, "loss_current": float("nan"), "loss_corrected": float("nan"),
            "delta_loss": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"),
            "big_delta_loss": float("nan"), "big_ci_low": float("nan"), "big_ci_high": float("nan"),
            "passed": False, "corrected_test_legs": pd.DataFrame(),
        }

    paired_df = pd.concat(eval_rows, ignore_index=True)
    y = paired_df["won"].to_numpy(dtype=float)
    loss_cur = _leg_log_loss(paired_df["p_current"].to_numpy(dtype=float), y)
    loss_cor = _leg_log_loss(paired_df["p_corrected"].to_numpy(dtype=float), y)
    diff = loss_cor - loss_cur  # negative = improvement

    delta, ci_lo, ci_hi = whole_day_bootstrap_mean(paired_df["date"], diff, resamples=resamples, seed=seed)

    big_mask = paired_df["fav_strength"] >= BIG_FAV_THRESHOLD
    if big_mask.any():
        b_delta, b_lo, b_hi = whole_day_bootstrap_mean(
            paired_df.loc[big_mask, "date"], diff[big_mask.to_numpy()], resamples=resamples, seed=seed
        )
    else:
        b_delta = b_lo = b_hi = float("nan")

    return {
        "market": fav_market,
        "shifts": shifts,
        "train_counts": train_counts,
        "n_legs": int(len(paired_df)),
        "n_big_legs": int(big_mask.sum()),
        "loss_current": float(np.mean(loss_cur)),
        "loss_corrected": float(np.mean(loss_cor)),
        "delta_loss": delta,
        "ci_low": ci_lo,
        "ci_high": ci_hi,
        "big_delta_loss": b_delta,
        "big_ci_low": b_lo,
        "big_ci_high": b_hi,
        "passed": bool(np.isfinite(ci_hi) and ci_hi < 0.0),
        "corrected_test_legs": pd.concat(corrected_parts, ignore_index=True),
    }


# ---------------------------------------------------------------------------
# Step 3: Slip-level check (live task-24 no-identical-leg rule)
# ---------------------------------------------------------------------------

def select_day_slips_live_rule(day_legs: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Select Safe/Medium/Big with accumulators.best_slip and live task-24 distinct-legs rule."""
    pool = day_legs.reset_index(drop=True).copy()
    if "match_key" not in pool.columns:
        pool["match_key"] = pool["match_id"].astype(str)
    pool["match_id"] = pool["match_key"].astype(str)
    leg_key = pool["match_key"].astype(str) + "|" + pool["market"].astype(str)
    used: set[str] = set()
    selected: dict[str, pd.DataFrame] = {}
    for tier in TIERS:
        open_pool = pool[~leg_key.isin(used)]
        picks = best_slip(open_pool, tier) if not open_pool.empty else None
        if picks is None:
            continue
        chosen = open_pool.loc[picks]
        selected[tier.name] = chosen
        used.update(leg_key.loc[chosen.index])
    return selected


def run_step3_slips(
    pool_a: pd.DataFrame,
    pool_c: pd.DataFrame,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Compare corrected probabilities (C) vs current (A) at slip level using identical odds."""
    slip_rows: list[dict[str, Any]] = []
    day_rows: list[dict[str, Any]] = []
    for variant, pool in (("A", pool_a), ("C", pool_c)):
        for day, group in pool.groupby(pd.to_datetime(pool["date"]).dt.strftime("%Y-%m-%d"), sort=True):
            slips = select_day_slips_live_rule(group)
            offered = len(slips)
            all_lost = bool(slips) and all(not s["won"].astype(bool).all() for s in slips.values())
            day_rows.append({"date": day, "variant": variant, "offered": offered, "has_offer": offered > 0, "all_lost": all_lost})
            for tier, chosen in slips.items():
                won = int(chosen["won"].astype(bool).all())
                total_odds = float(chosen["odds"].prod())
                slip_rows.append({
                    "date": day, "tier": tier, "variant": variant,
                    "won": won, "total_odds": total_odds,
                    "value": won * total_odds - 1.0,
                    "selection": "|".join(sorted(chosen["match_key"].astype(str) + ":" + chosen["market"].astype(str))),
                })
    slips_df = pd.DataFrame(slip_rows)
    daily_df = pd.DataFrame(day_rows)

    def _day_stats(v: str) -> dict[str, Any]:
        d = daily_df[daily_df["variant"] == v]
        off = d[d["has_offer"]]
        return {
            "offered_days": int(len(off)),
            "total_slips": int(d["offered"].sum()),
            "all_lost_days": int(off["all_lost"].sum()),
            "all_lost_share": float(off["all_lost"].mean()) if len(off) else float("nan"),
        }

    stats_a, stats_c = _day_stats("A"), _day_stats("C")
    if slips_df.empty:
        return {
            "matched_slips": 0, "matched_days": 0, "changed_selections": 0,
            "return_a": float("nan"), "return_c": float("nan"),
            "gain": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"),
            "stats_a": stats_a, "stats_c": stats_c, "passed": False,
        }

    pivot = slips_df.pivot(index=["date", "tier"], columns="variant", values="value")
    paired = pivot[["A", "C"]].dropna() if {"A", "C"} <= set(pivot.columns) else pd.DataFrame()
    if paired.empty:
        return {
            "matched_slips": 0, "matched_days": 0, "changed_selections": 0,
            "return_a": float("nan"), "return_c": float("nan"),
            "gain": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"),
            "stats_a": stats_a, "stats_c": stats_c, "passed": False,
        }
    sel_piv = slips_df.pivot(index=["date", "tier"], columns="variant", values="selection").reindex(paired.index)
    changed_selections = int((sel_piv["A"] != sel_piv["C"]).sum())
    diff_series = paired["C"] - paired["A"]
    gain, ci_lo, ci_hi = whole_day_bootstrap_mean(
        pd.Series(paired.index.get_level_values("date")),
        diff_series.to_numpy(dtype=float),
        resamples=resamples,
        seed=seed,
    )
    passed = bool(
        np.isfinite(gain) and gain >= 0.0
        and np.isfinite(ci_lo) and ci_lo >= -0.01
        and np.isfinite(stats_c["all_lost_share"]) and np.isfinite(stats_a["all_lost_share"])
        and stats_c["all_lost_share"] <= stats_a["all_lost_share"]
    )
    return {
        "matched_slips": int(len(paired)),
        "matched_days": int(paired.index.get_level_values("date").nunique()),
        "changed_selections": changed_selections,
        "return_a": float(paired["A"].mean()),
        "return_c": float(paired["C"].mean()),
        "gain": gain, "ci_low": ci_lo, "ci_high": ci_hi,
        "stats_a": stats_a, "stats_c": stats_c,
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# Data loaders: Primary (5 leagues, 2024/25+), Replication (9 leagues, 2019/20-2023/24), Live archive
# ---------------------------------------------------------------------------

def load_primary_legs() -> pd.DataFrame:
    """diversity_study.load_legs() pool (5 main leagues, 2024/25+) WITHOUT removing gate-FAIL pairs."""
    blocked = failed_gates()
    frames = []
    for code in MAIN_LEAGUES:
        frame = pd.read_parquet(paths(code).accumulator_legs).copy()
        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame[frame["season"].str[:4].astype(int) >= 2024]
        prob_col = "probability" if code == "EPL" else "market_probability"
        frame["probability"] = frame[prob_col]
        frame["league"] = code
        frame["match_key"] = code + ":" + frame["match_id"].astype(str)
        frames.append(frame)

    legs = pd.concat(frames, ignore_index=True)
    legs = legs[legs["market"].isin(SLIP_MARKETS)].copy()
    legs["is_gate_fail"] = [(lg, m) in blocked for lg, m in zip(legs["league"], legs["market"])]
    legs = legs.dropna(subset=["date", "probability", "odds", "won"])
    legs = legs[(legs["odds"] >= 1.05) & legs["probability"].between(0, 1, inclusive="neither")].copy()
    legs["source_match_id"] = legs["match_id"]
    legs["match_id"] = legs["match_key"]
    return legs.reset_index(drop=True)


def _walkforward_market_league_replication(
    matches: pd.DataFrame,
    code: str,
    markets: tuple[str, ...],
    memo: dict[tuple[float, float, float, float, float, float], dict[str, float]],
) -> pd.DataFrame:
    """Exact tasks 13/20/21/27 walk-forward Platt calibration on bookmaker_implied for one league."""
    rho = float(league_rho(code))
    df = matches.copy()
    df["date"] = pd.to_datetime(df["date"])
    valid = (df[list(AVG_ODDS_COLS)].notna() & df[list(AVG_ODDS_COLS)].gt(0)).all(axis=1)
    valid &= df["home_goals"].notna() & df["away_goals"].notna()
    df = df[valid].sort_values(["season", "date"]).reset_index(drop=True)

    raw_rows: list[dict[str, Any]] = []
    for row in df.to_dict("records"):
        key = (
            float(row["avg_odds_home"]),
            float(row["avg_odds_draw"]),
            float(row["avg_odds_away"]),
            float(row["avg_odds_over25"]),
            float(row["avg_odds_under25"]),
            rho,
        )
        fair = memo.get(key)
        if fair is None:
            fair = bookmaker_implied(*key)[0]
            memo[key] = fair

        hg, ag = int(row["home_goals"]), int(row["away_goals"])
        hl = row.get("home_led_at_any_point")
        al = row.get("away_led_at_any_point")
        outcomes = {
            "home_win": int(hg > ag),
            "away_win": int(ag > hg),
            "double_1x": int(hg >= ag),
            "double_x2": int(ag >= hg),
            "home_1up": None if (hl is None or pd.isna(hl)) else int(bool(hl)),
            "away_1up": None if (al is None or pd.isna(al)) else int(bool(al)),
        }
        mk = f"{code}:{row['match_id']}"
        for mkt in markets:
            raw_rows.append({
                "match_key": mk,
                "match_id": mk,
                "date": row["date"],
                "season": str(row["season"]),
                "league": code,
                "market": mkt,
                "bookmaker_probability": float(fair[mkt]),
                "won": outcomes[mkt],
            })

    legs = pd.DataFrame(raw_rows)
    if legs.empty:
        return legs
    legs["probability"] = np.nan

    seasons = sorted(legs["season"].unique())
    for idx, season in enumerate(seasons):
        if idx == 0 or season not in REPL_SEASONS:
            continue
        for mkt in markets:
            past = legs[(legs["season"] < season) & (legs["market"] == mkt)].dropna(subset=["won", "bookmaker_probability"])
            cur_mask = (legs["season"] == season) & (legs["market"] == mkt)
            if past.empty or past["won"].nunique() < 2 or not cur_mask.any():
                continue
            model = LogisticRegression(C=1.0, max_iter=1000)
            model.fit(logit(_clip_prob(past["bookmaker_probability"])).reshape(-1, 1), past["won"].astype(int))
            cur_raw = logit(_clip_prob(legs.loc[cur_mask, "bookmaker_probability"]))
            legs.loc[cur_mask, "probability"] = np.clip(expit(model.intercept_[0] + model.coef_[0, 0] * cur_raw), 1e-6, 1.0 - 1e-6)

    repl = legs[legs["season"].isin(REPL_SEASONS)].dropna(subset=["probability"]).copy()
    repl["is_gate_fail"] = False
    return repl.reset_index(drop=True)


def _load_new_league_csv_history(code: str) -> pd.DataFrame:
    """Load cached football-data CSVs (2014/15-2023/24) for one of the 4 new leagues (no network)."""
    div = NEW_LEAGUE_DIV[code]
    rows: list[dict[str, Any]] = []
    for year in range(2014, 2024):
        season_str = f"{year}/{str(year + 1)[2:]}"
        scode = f"{year % 100:02d}{(year + 1) % 100:02d}"
        candidates = [
            NEW_LEAGUES_CACHE / f"{div}_{scode}.csv",
            paths(code).football_csv(scode),
        ]
        csv_path = next((p for p in candidates if p.exists()), None)
        if csv_path is None:
            continue
        frame = pd.read_csv(StringIO(csv_path.read_bytes().decode("utf-8-sig", errors="replace")))
        cols = odds_columns(frame)
        if cols is None:
            continue
        played = frame.dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]).copy()
        valid = played[(played[cols].notna() & played[cols].gt(0)).all(axis=1)]
        for idx, rec in enumerate(valid.to_dict("records")):
            rows.append({
                "match_id": f"{year}:{idx}",
                "date": pd.to_datetime(rec["Date"], dayfirst=True),
                "season": season_str,
                "home_goals": int(rec["FTHG"]),
                "away_goals": int(rec["FTAG"]),
                "avg_odds_home": float(rec[cols[0]]),
                "avg_odds_draw": float(rec[cols[1]]),
                "avg_odds_away": float(rec[cols[2]]),
                "avg_odds_over25": float(rec[cols[3]]),
                "avg_odds_under25": float(rec[cols[4]]),
                "home_led_at_any_point": None,
                "away_led_at_any_point": None,
            })
    return pd.DataFrame(rows)


def _load_epl_replication() -> tuple[pd.DataFrame, list[str]]:
    """Reproduce EPL blended replication legs using exact accumulators/method_retest_study walk-forward code."""
    not_avail = [
        "EPL `2019/20`, `2020/21` (all 3 markets): `predictions_goal_timing_validation.parquet` starts at `2021/22` (`predictions_dc_history.parquet` has raw DC outputs only, no calibrated/goal-timing/blended legs).",
        "EPL `2021/22` (all 3 markets): first validation season has no earlier blended-leg season to fit `model_weight` walk-forward (same rule as `method_retest_study.py`).",
    ]
    val_path = paths("EPL").predictions_goal_timing_validation
    if not val_path.exists():
        return pd.DataFrame(), [*not_avail, "EPL `2022/23`, `2023/24`: validation timing parquet missing."]

    val = build_validation_leg_table("EPL")
    val, _ = calibrate_market_probabilities(val, val.iloc[:0])
    val = val[val["market"].isin(SLIP_MARKETS)].copy()
    val["probability"] = np.nan
    for season in ("2022/23", "2023/24"):
        prior = val[val["season"] < season].dropna(subset=["model_probability", "market_probability", "won"])
        cur = val["season"] == season
        if prior.empty or not cur.any():
            continue
        w = fit_model_weight(prior)
        val.loc[cur, "probability"] = blend(
            val.loc[cur, "model_probability"], val.loc[cur, "market_probability"], w
        )
    scored = val[val["season"].isin(("2022/23", "2023/24"))].dropna(subset=["probability", "won"]).copy()
    scored["league"] = "EPL"
    scored["match_key"] = "EPL:" + scored["match_id"].astype(str)
    scored["match_id"] = scored["match_key"]
    scored["is_gate_fail"] = False
    return scored.reset_index(drop=True), not_avail


def load_replication_legs() -> tuple[pd.DataFrame, list[str]]:
    """Load 2019/20-2023/24 walk-forward replication legs across all 9 live leagues + NOT AVAILABLE notes."""
    memo: dict[tuple[float, float, float, float, float, float], dict[str, float]] = {}
    parts: list[pd.DataFrame] = []
    not_available: list[str] = []

    # 1. EPL (live method = blended model)
    epl_df, epl_notes = _load_epl_replication()
    if not epl_df.empty:
        parts.append(epl_df)
    not_available.extend(epl_notes)

    # 2. Four main market-mode leagues (LALIGA, SERIEA, BUNDES, LIGUE1) — all 3 markets, 2019/20-2023/24
    main_mkts = ("home_win", "away_win", "home_1up", "away_1up", "double_1x", "double_x2")
    for code in ("LALIGA", "SERIEA", "BUNDES", "LIGUE1"):
        matches = pd.read_parquet(paths(code).matches)
        parts.append(_walkforward_market_league_replication(matches, code, main_mkts, memo))

    # 3. Four football-data-only market-mode leagues (EREDIV, JUPILER, PRIMEIRA, SUPERLIG)
    new_mkts = ("home_win", "away_win", "double_1x", "double_x2")
    for code in ("EREDIV", "JUPILER", "PRIMEIRA", "SUPERLIG"):
        matches = _load_new_league_csv_history(code)
        parts.append(_walkforward_market_league_replication(matches, code, new_mkts, memo))
        not_available.append(
            f"{code} `1up` (`home_1up`/`away_1up`, `2019/20–2023/24`): football-data-only league has no Understat goal-minute / led-at-any-point outcomes (`football_only.score_actuals` sets 1Up to `None`)."
        )

    all_repl = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    return all_repl, not_available


def load_live_archive_descriptive(archive_dir: Path = ARCHIVE_DIR) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read-only descriptive holdout summary from web/public/data/archive (never fitted on)."""
    latest_fixtures: dict[tuple[str, str, str], dict[str, Any]] = {}
    for path in sorted(archive_dir.glob("20*.json")) if archive_dir.exists() else []:
        snap = json.loads(path.read_text(encoding="utf-8"))
        for f in snap.get("fixtures", []):
            key = (f["date"], f["home"], f["away"])
            latest_fixtures[key] = f

    rows: list[dict[str, Any]] = []
    dates_seen: list[str] = []
    target_mkts = {"home_win", "away_win", "home_1up", "away_1up", "double_1x", "double_x2"}
    for f in latest_fixtures.values():
        result = f.get("result")
        if not result or "outcomes" not in result:
            continue
        lg = f["league"]["code"] if isinstance(f.get("league"), dict) else str(f.get("league") or "EPL")
        mk = f"{lg}:{f['date']}:{f['home']}:{f['away']}"
        dates_seen.append(f["date"])
        for m in f.get("markets", []):
            if m["market"] not in target_mkts:
                continue
            outcome = result["outcomes"].get(m["market"])
            rows.append({
                "match_key": mk,
                "date": pd.Timestamp(f["date"]),
                "season": "2026/27",
                "league": lg,
                "market": m["market"],
                "probability": float(m["probability"]),
                "won": None if outcome is None else int(bool(outcome)),
                "is_gate_fail": False,
            })

    df = pd.DataFrame(rows)
    fav_df, meta = assign_favourites(df)
    summary = evaluate_step1(fav_df)
    meta["date_min"] = min(dates_seen) if dates_seen else None
    meta["date_max"] = max(dates_seen) if dates_seen else None
    meta["settled_fixtures"] = len(dates_seen)
    return fav_df, {"summary": summary, "meta": meta}


# ---------------------------------------------------------------------------
# Full orchestrator & report writer
# ---------------------------------------------------------------------------

def _fmt_pct(v: float) -> str:
    return "n/a" if not np.isfinite(v) else f"{v:.2%}"


def _fmt_gap(v: float) -> str:
    return "n/a" if not np.isfinite(v) else f"{v:+.2%}"


def _fmt_ci(lo: float, hi: float, signed: bool = True) -> str:
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "n/a"
    return f"[{lo:+.2%}, {hi:+.2%}]" if signed else f"[{lo:.2%}, {hi:.2%}]"


def run_study(output_path: Path = REPORT_PATH) -> dict[str, Any]:
    primary_legs = load_primary_legs()
    primary_fav, primary_meta = assign_favourites(primary_legs)
    primary_step1 = evaluate_step1(primary_fav, leagues=MAIN_LEAGUES)

    repl_legs, not_available = load_replication_legs()
    repl_fav, repl_meta = assign_favourites(repl_legs)
    repl_step1 = evaluate_step1(repl_fav, leagues=tuple(LEAGUES.keys()))

    _, archive_info = load_live_archive_descriptive()

    step1_pass: dict[str, bool] = {}
    step2_results: dict[str, dict[str, Any] | None] = {}
    step3_results: dict[str, dict[str, Any] | None] = {}
    decisions: dict[str, str] = {}

    # Pool for Step 2 walk-forward training (replication + primary) and Step 3 live slip pool.
    common_cols = ["match_key", "match_id", "date", "season", "league", "market", "probability", "won"]
    combined_for_step2 = pd.concat(
        [repl_legs[common_cols], primary_legs[common_cols]],
        ignore_index=True,
    )
    live_slip_pool = primary_legs[
        (~primary_legs["is_gate_fail"]) & (~primary_legs["market"].isin(OWNER_EXCLUDED_MARKETS))
    ].reset_index(drop=True)

    for mkt in FAV_MARKETS:
        p1 = step1_market_passes(primary_step1["big_fav"][mkt], repl_step1["big_fav"][mkt])
        step1_pass[mkt] = p1
        if not p1:
            step2_results[mkt] = None
            step3_results[mkt] = None
            decisions[mkt] = "KEEP current method (failed Step 1)"
            continue

        s2 = run_step2_walkforward(combined_for_step2, PRIMARY_SEASONS, mkt)
        step2_results[mkt] = s2
        if not s2["passed"]:
            step3_results[mkt] = None
            decisions[mkt] = "KEEP current method (failed Step 2)"
            continue

        # Build Step 3 corrected slip pool by applying the exact Step 2 walk-forward shifts per test season.
        cor_pool = live_slip_pool.copy()
        for season, d_val in s2["shifts"].items():
            s_mask = cor_pool["season"] == season
            if s_mask.any():
                cor_pool.loc[s_mask, "probability"] = apply_big_fav_shift(
                    cor_pool.loc[s_mask], mkt, d_val
                )["probability"].to_numpy()
        s3 = run_step3_slips(live_slip_pool, cor_pool)
        step3_results[mkt] = s3
        if s3["passed"]:
            decisions[mkt] = "ADOPT (research pass; requires separate live task & owner approval)"
        else:
            decisions[mkt] = "KEEP current method (failed Step 3)"

    report = _format_report(
        primary_legs=primary_legs,
        primary_meta=primary_meta,
        primary_step1=primary_step1,
        repl_legs=repl_legs,
        repl_meta=repl_meta,
        repl_step1=repl_step1,
        not_available=not_available,
        archive_info=archive_info,
        step1_pass=step1_pass,
        step2_results=step2_results,
        step3_results=step3_results,
        decisions=decisions,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return {
        "primary_step1": primary_step1,
        "repl_step1": repl_step1,
        "not_available": not_available,
        "archive_info": archive_info,
        "step1_pass": step1_pass,
        "step2_results": step2_results,
        "step3_results": step3_results,
        "decisions": decisions,
        "report_path": output_path,
    }


def _format_report(
    primary_legs: pd.DataFrame,
    primary_meta: dict[str, int],
    primary_step1: dict[str, Any],
    repl_legs: pd.DataFrame,
    repl_meta: dict[str, int],
    repl_step1: dict[str, Any],
    not_available: list[str],
    archive_info: dict[str, Any],
    step1_pass: dict[str, bool],
    step2_results: dict[str, dict[str, Any] | None],
    step3_results: dict[str, dict[str, Any] | None],
    decisions: dict[str, str],
) -> str:
    now_eat = datetime.now(timezone.utc).astimezone(EAT).strftime("%Y-%m-%d %H:%M EAT")
    lines = [
        "# Big favourites calibration study (PROJECT.md task 29)",
        "",
        f"Generated: **{now_eat}** | Pre-registered: `2026-11-23` | Research only (no live changes).",
        "",
        "## Summary & locked decisions",
        "",
        "| Market | Primary `F >= 0.70` gap (95% CI) | Replication `F >= 0.70` gap (95% CI) | Step 1 | Step 2 | Step 3 | Decision |",
        "|---|---|---|---|---|---|---|",
    ]
    for mkt in FAV_MARKETS:
        pb = primary_step1["big_fav"][mkt]
        rb = repl_step1["big_fav"][mkt]
        s1_txt = "PASS" if step1_pass[mkt] else "FAIL"
        s2 = step2_results[mkt]
        s2_txt = "Not run (failed Step 1)" if s2 is None else ("PASS" if s2["passed"] else "FAIL")
        s3 = step3_results[mkt]
        s3_txt = (
            "Not run (failed Step 1)" if s2 is None
            else "Not run (failed Step 2)" if s3 is None
            else ("PASS" if s3["passed"] else "FAIL")
        )
        lines.append(
            f"| `{mkt}` ({FAV_MARKET_LABELS[mkt]}) | {_fmt_gap(pb['gap'])} {_fmt_ci(pb['ci_low'], pb['ci_high'])} (n={pb['n_legs']}) | "
            f"{_fmt_gap(rb['gap'])} {_fmt_ci(rb['ci_low'], rb['ci_high'])} (n={rb['n_legs']}) | "
            f"**{s1_txt}** | {s2_txt} | {s3_txt} | **{decisions[mkt]}** |"
        )

    lines += [
        "",
        "## Data scope & NOT AVAILABLE audit",
        "",
        f"- **Primary (`2024/25+`, 5 main leagues)**: `diversity_study.load_legs()` pool WITHOUT removing gate-FAIL pairs "
        f"({primary_legs['match_key'].nunique():,} matches, {len(primary_legs):,} legs; "
        f"{primary_meta['matches_missing_win_side']} matches lacked one `*_win` side because Stage 4 dropped `odds < 1.05` legs and were excluded from favourite assignment; "
        f"{primary_meta['dropped_unknown_outcomes']} unknown-outcome legs excluded).",
        f"- **Replication (`2019/20–2023/24`, 9 live leagues)**: walk-forward probabilities using each league's exact live method "
        f"({repl_legs['match_key'].nunique():,} matches, {len(repl_legs):,} legs; "
        f"{repl_meta['matches_missing_win_side']} matches missing one win side; "
        f"{repl_meta['dropped_unknown_outcomes']} unknown-outcome legs excluded). "
        "Note: unlike `accumulator_legs.parquet`, tasks 13/20/21/27 walk-forward market tables do not drop `odds < 1.05` legs, so `win_or_draw` covers every complete-odds match in the 8 market-mode leagues.",
        "- **Bootstrap**: 2,000 whole-day resamples, seed `20261124`.",
        "",
        "### Explicitly NOT AVAILABLE (never substituted)",
    ]
    for item in not_available:
        lines.append(f"- **NOT AVAILABLE**: {item}")

    # Step 1 tables: Primary and Replication per market & band
    for title, step1_data in (
        ("Step 1A — Primary data (5 main leagues, 2024/25+)", primary_step1),
        ("Step 1B — Replication data (9 live leagues, 2019/20–2023/24)", repl_step1),
    ):
        lines += ["", f"## {title}", ""]
        for mkt in FAV_MARKETS:
            lines += [
                f"### {FAV_MARKET_LABELS[mkt]} (`{mkt}`)",
                "",
                "| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |",
                "|---|---:|---:|---:|---:|---|---:|---|",
            ]
            for r in step1_data["by_market_band"][mkt]:
                lines.append(
                    f"| {r['band']} | {r['n_legs']:,} | {r['n_matches']:,} | {_fmt_pct(r['predicted'])} | "
                    f"{_fmt_pct(r['actual'])} | {_fmt_ci(r['wilson_low'], r['wilson_high'], signed=False)} | "
                    f"{_fmt_gap(r['gap'])} | {_fmt_ci(r['ci_low'], r['ci_high'])} |"
                )
            lines.append("")

    # Gate-FAIL separate rows in Primary
    lines += [
        "## Primary gate-FAIL vs gate-PASS breakdown",
        "",
        "| Market | Scope | Group | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |",
        "|---|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for r in primary_step1["gate_fail_rows"]:
        lines.append(
            f"| `{r['market']}` | {r['scope']} | `{r['group']}` | {r['n_legs']:,} | {r['n_matches']:,} | "
            f"{_fmt_pct(r['predicted'])} | {_fmt_pct(r['actual'])} | {_fmt_ci(r['wilson_low'], r['wilson_high'], signed=False)} | "
            f"{_fmt_gap(r['gap'])} | {_fmt_ci(r['ci_low'], r['ci_high'])} |"
        )

    # Per-league rows for F >= 0.70 (Primary and Replication)
    for title, step1_data, is_repl in (
        ("Per-league big favourites (`F >= 0.70`) — Primary (2024/25+)", primary_step1, False),
        ("Per-league big favourites (`F >= 0.70`) — Replication (2019/20–2023/24)", repl_step1, True),
    ):
        lines += ["", f"## {title}", ""]
        for mkt in FAV_MARKETS:
            lines += [
                f"### `{mkt}` ({FAV_MARKET_LABELS[mkt]})",
                "",
                "| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |",
                "|---|---|---:|---:|---:|---:|---|---:|---|",
            ]
            for r in step1_data["per_league_big"][mkt]:
                code = r["league"]
                if is_repl and mkt == "1up" and code in NEW_LEAGUES:
                    lines.append(f"| `{code}` | **NOT AVAILABLE** (football-data only) | 0 | 0 | n/a | n/a | n/a | n/a | n/a |")
                    continue
                avail = "2022/23–2023/24 only (blended)" if (is_repl and code == "EPL") else ("2019/20–2023/24" if is_repl else "2024/25+")
                lines.append(
                    f"| `{code}` | {avail} | {r['n_legs']:,} | {r['n_matches']:,} | {_fmt_pct(r['predicted'])} | "
                    f"{_fmt_pct(r['actual'])} | {_fmt_ci(r['wilson_low'], r['wilson_high'], signed=False)} | "
                    f"{_fmt_gap(r['gap'])} | {_fmt_ci(r['ci_low'], r['ci_high'])} |"
                )
            lines.append("")

    # Step 2 & Step 3 sections
    lines += ["## Step 2 — Walk-forward logit shift (`F >= 0.70`)", ""]
    for mkt in FAV_MARKETS:
        s2 = step2_results[mkt]
        if s2 is None:
            lines.append(f"- `{mkt}`: **Not run** (did not pass Step 1).")
        else:
            lines += [
                f"- `{mkt}` (**{'PASS' if s2['passed'] else 'FAIL'}**): shifts by season `{s2['shifts']}` (training big-fav counts `{s2['train_counts']}`).",
                f"  - All test-season `{mkt}` legs (`n={s2['n_legs']:,}`): log loss `{s2['loss_current']:.5f}` -> `{s2['loss_corrected']:.5f}`, "
                f"change `{s2['delta_loss']:+.5f}` (95% CI `[{s2['ci_low']:+.5f}, {s2['ci_high']:+.5f}]`).",
                f"  - Big-favourite subset (`F >= 0.70`, `n={s2['n_big_legs']:,}`): log-loss change `{s2['big_delta_loss']:+.5f}` "
                f"(95% CI `[{s2['big_ci_low']:+.5f}, {s2['big_ci_high']:+.5f}]`).",
            ]

    lines += ["", "## Step 3 — Slip-level check (live task-24 no-identical-leg rule)", ""]
    for mkt in FAV_MARKETS:
        s3 = step3_results[mkt]
        if step2_results[mkt] is None:
            lines.append(f"- `{mkt}`: **Not run** (failed Step 1).")
        elif s3 is None:
            lines.append(f"- `{mkt}`: **Not run** (failed Step 2).")
        else:
            lines += [
                f"- `{mkt}` (**{'PASS' if s3['passed'] else 'FAIL'}**): matched slips `{s3['matched_slips']}` across `{s3['matched_days']}` days "
                f"(`{s3['changed_selections']}` selections changed).",
                f"  - Matched return per unit: A `{s3['return_a']:+.4f}`, C `{s3['return_c']:+.4f}`, "
                f"C − A `{s3['gain']:+.4f}` (95% CI `[{s3['ci_low']:+.4f}, {s3['ci_high']:+.4f}]`).",
                f"  - All-loss offered-day share: A `{s3['stats_a']['all_lost_share']:.2%}` ({s3['stats_a']['offered_days']} days) vs "
                f"C `{s3['stats_c']['all_lost_share']:.2%}` ({s3['stats_c']['offered_days']} days).",
            ]

    # Live archive descriptive holdout
    ameta = archive_info["meta"]
    asum = archive_info["summary"]
    lines += [
        "",
        "## Live archive descriptive check (untouched holdout — NEVER fitted on)",
        "",
        f"Settled archived fixtures: **{ameta['settled_fixtures']:,}** ({ameta['date_min']} to {ameta['date_max']}; "
        f"unknown outcomes excluded: {ameta['dropped_unknown_outcomes']}). Reported descriptively only.",
        "",
        "| Market | Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |",
        "|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for mkt in FAV_MARKETS:
        for r in asum["by_market_band"][mkt]:
            lines.append(
                f"| `{mkt}` | {r['band']} | {r['n_legs']:,} | {r['n_matches']:,} | {_fmt_pct(r['predicted'])} | "
                f"{_fmt_pct(r['actual'])} | {_fmt_ci(r['wilson_low'], r['wilson_high'], signed=False)} | "
                f"{_fmt_gap(r['gap'])} | {_fmt_ci(r['ci_low'], r['ci_high'])} |"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    res = run_study()
    print(f"Wrote {res['report_path']}")
    for mkt in FAV_MARKETS:
        pb = res["primary_step1"]["big_fav"][mkt]
        rb = res["repl_step1"]["big_fav"][mkt]
        print(
            f"{mkt:11s} | primary gap {pb['gap']:+.4f} [{pb['ci_low']:+.4f}, {pb['ci_high']:+.4f}] (n={pb['n_legs']}) | "
            f"repl gap {rb['gap']:+.4f} [{rb['ci_low']:+.4f}, {rb['ci_high']:+.4f}] (n={rb['n_legs']}) | "
            f"{res['decisions'][mkt]}"
        )


if __name__ == "__main__":
    main()
