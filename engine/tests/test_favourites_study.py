"""Known-answer synthetic tests for PROJECT.md task 29 (favourites_study)."""
from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from src.favourites_study import (
    BIG_FAV_THRESHOLD,
    CLIP_HIGH,
    CLIP_LOW,
    apply_big_fav_shift,
    assign_favourites,
    evaluate_step1,
    run_step2_walkforward,
    step1_market_passes,
)


def _make_synthetic_pool(
    n_days: int = 120,
    matches_per_day: int = 6,
    big_fav_boost: float = 0.0,
    seed: int = 42,
    seasons: tuple[str, ...] = ("2022/23", "2023/24", "2024/25", "2025/26"),
) -> pd.DataFrame:
    """Build deterministic multi-season synthetic leg pool with controlled big-favourite boost."""
    rng = np.random.default_rng(seed)
    rows = []
    match_idx = 0
    days_per_season = n_days // len(seasons)
    for s_idx, season in enumerate(seasons):
        base_date = pd.Timestamp(f"{2022 + s_idx}-09-01")
        for d in range(days_per_season):
            date = base_date + timedelta(days=d * 2)
            for _ in range(matches_per_day):
                match_idx += 1
                mk = f"EPL:{match_idx}"
                is_home_fav = bool(match_idx % 2 == 0)
                # Half the matches are big favourites (F in [0.72, 0.85]), half are non-big (F in [0.42, 0.65]).
                if match_idx % 2 == 0:
                    f_prob = float(rng.uniform(0.72, 0.85))
                else:
                    f_prob = float(rng.uniform(0.42, 0.65))
                p_draw = float(min(0.28, max(0.08, (1.0 - f_prob) * 0.55)))
                p_under = float(max(0.02, 1.0 - f_prob - p_draw))
                p_1up = float(min(0.95, f_prob + 0.08))
                p_dc = float(min(0.96, f_prob + p_draw))
                p_u_1up = float(min(0.90, p_under + 0.12))
                p_u_dc = float(min(0.95, p_under + p_draw))

                boost = big_fav_boost if f_prob >= BIG_FAV_THRESHOLD else 0.0
                # Single coherent uniform draw ensures exact marginal probability P(won = 1) = p + boost
                # while keeping won_win <= won_1up and won_win <= won_dc.
                u = float(rng.random())
                won_win = int(u < np.clip(f_prob + boost, 0.01, 0.99))
                won_1up = int(u < np.clip(p_1up + boost, 0.01, 0.99))
                won_dc = int(u < np.clip(p_dc + boost, 0.01, 0.99))
                won_under = int(0 if won_win else (rng.random() < p_under / max(1 - f_prob, 1e-6)))
                won_u_1up = int(won_under or rng.random() < 0.15)
                won_u_dc = int(1 - won_win)

                if is_home_fav:
                    mkts = [
                        ("home_win", f_prob, won_win),
                        ("away_win", p_under, won_under),
                        ("home_1up", p_1up, won_1up),
                        ("away_1up", p_u_1up, won_u_1up),
                        ("double_1x", p_dc, won_dc),
                        ("double_x2", p_u_dc, won_u_dc),
                        ("over_1.5", 0.78, int(rng.random() < 0.78)),
                    ]
                else:
                    mkts = [
                        ("home_win", p_under, won_under),
                        ("away_win", f_prob, won_win),
                        ("home_1up", p_u_1up, won_u_1up),
                        ("away_1up", p_1up, won_1up),
                        ("double_1x", p_u_dc, won_u_dc),
                        ("double_x2", p_dc, won_dc),
                        ("over_1.5", 0.78, int(rng.random() < 0.78)),
                    ]
                for mkt, prob, won in mkts:
                    rows.append({
                        "match_key": mk,
                        "match_id": mk,
                        "date": date,
                        "season": season,
                        "league": "EPL",
                        "market": mkt,
                        "probability": prob,
                        "odds": max(1.06, 1.0 / (prob * 1.07)),
                        "won": won,
                        "is_gate_fail": False,
                    })
    return pd.DataFrame(rows)


def test_1_perfectly_calibrated_favourites_fail_step1():
    """(1) Perfectly calibrated synthetic favourites give a gap CI covering 0 and FAIL Step 1."""
    pool = _make_synthetic_pool(n_days=160, matches_per_day=8, big_fav_boost=0.0, seed=101)
    prim = pool[pool["season"].isin(("2024/25", "2025/26"))]
    repl = pool[pool["season"].isin(("2022/23", "2023/24"))]
    prim_fav, _ = assign_favourites(prim)
    repl_fav, _ = assign_favourites(repl)
    s1_prim = evaluate_step1(prim_fav, resamples=500, seed=20261124)
    s1_repl = evaluate_step1(repl_fav, resamples=500, seed=20261124)

    for mkt in ("win", "1up", "win_or_draw"):
        pb = s1_prim["big_fav"][mkt]
        rb = s1_repl["big_fav"][mkt]
        assert pb["ci_low"] <= 0.0 <= pb["ci_high"], f"{mkt} primary CI should cover 0: {pb}"
        assert not step1_market_passes(pb, rb)


def test_2_boosted_favourites_8_points_pass_steps_1_and_2():
    """(2) Synthetic favourites that win 8 points more than predicted PASS Steps 1 and 2."""
    pool = _make_synthetic_pool(n_days=200, matches_per_day=8, big_fav_boost=0.08, seed=202)
    prim = pool[pool["season"].isin(("2024/25", "2025/26"))]
    repl = pool[pool["season"].isin(("2022/23", "2023/24"))]
    prim_fav, _ = assign_favourites(prim)
    repl_fav, _ = assign_favourites(repl)
    s1_prim = evaluate_step1(prim_fav, resamples=500, seed=20261124)
    s1_repl = evaluate_step1(repl_fav, resamples=500, seed=20261124)

    # Big favourites win +8 pts above predicted -> Step 1 PASS and Step 2 log-loss improvement PASS.
    assert step1_market_passes(s1_prim["big_fav"]["win"], s1_repl["big_fav"]["win"]) is True
    s2 = run_step2_walkforward(pool, ("2024/25", "2025/26"), "win", resamples=500, seed=20261124)
    assert s2["passed"] is True
    assert s2["delta_loss"] < 0.0 and s2["ci_high"] < 0.0
    assert all(d > 0.0 for d in s2["shifts"].values())


def test_3_correction_never_changes_non_big_fav_or_other_markets():
    """(3) The correction never changes a leg with F < 0.70 or a non-favourite market."""
    pool = _make_synthetic_pool(n_days=20, matches_per_day=4, big_fav_boost=0.0, seed=303)
    shifted = apply_big_fav_shift(pool, "win", shift_d=0.65)

    fav_map = (
        pool[pool["market"].isin(("home_win", "away_win"))]
        .pivot(index="match_key", columns="market", values="probability")
    )
    fav_side = {mk: ("home" if r.home_win >= r.away_win else "away") for mk, r in fav_map.iterrows()}
    fav_str = {mk: max(r.home_win, r.away_win) for mk, r in fav_map.iterrows()}

    changed_big_win = 0
    for before, after in zip(pool.itertuples(index=False), shifted.itertuples(index=False)):
        side = fav_side[before.match_key]
        strength = fav_str[before.match_key]
        target_mkt = "home_win" if side == "home" else "away_win"
        if strength >= BIG_FAV_THRESHOLD and before.market == target_mkt:
            assert after.probability >= before.probability
            if after.probability > before.probability:
                changed_big_win += 1
        else:
            # F < 0.70, underdog win, 1up, double chance, and over_1.5 must be bit-for-bit untouched.
            assert after.probability == before.probability, (
                f"Unexpected change on {before.match_key} {before.market} (F={strength:.3f})"
            )
    assert changed_big_win > 0


def test_4_unknown_outcomes_are_excluded_never_counted_as_losses():
    """(4) Unknown outcomes (won is None/NaN) are excluded, never counted as losses."""
    legs = pd.DataFrame([
        # Match 1: big home favourite (F=0.80), all outcomes WON
        dict(match_key="EPL:1", date=pd.Timestamp("2025-01-01"), season="2024/25", league="EPL", market="home_win", probability=0.80, won=1),
        dict(match_key="EPL:1", date=pd.Timestamp("2025-01-01"), season="2024/25", league="EPL", market="away_win", probability=0.08, won=0),
        dict(match_key="EPL:1", date=pd.Timestamp("2025-01-01"), season="2024/25", league="EPL", market="home_1up", probability=0.88, won=1),
        dict(match_key="EPL:1", date=pd.Timestamp("2025-01-01"), season="2024/25", league="EPL", market="double_1x", probability=0.92, won=1),
        # Match 2: big home favourite (F=0.80), home_1up outcome UNKNOWN (None), home_win UNKNOWN (NaN)
        dict(match_key="EPL:2", date=pd.Timestamp("2025-01-02"), season="2024/25", league="EPL", market="home_win", probability=0.80, won=None),
        dict(match_key="EPL:2", date=pd.Timestamp("2025-01-02"), season="2024/25", league="EPL", market="away_win", probability=0.08, won=None),
        dict(match_key="EPL:2", date=pd.Timestamp("2025-01-02"), season="2024/25", league="EPL", market="home_1up", probability=0.88, won=np.nan),
        dict(match_key="EPL:2", date=pd.Timestamp("2025-01-02"), season="2024/25", league="EPL", market="double_1x", probability=0.92, won=1),
    ])
    fav, meta = assign_favourites(legs)
    assert meta["dropped_unknown_outcomes"] == 2
    s1 = evaluate_step1(fav, resamples=200, seed=20261124)
    # win: only Match 1 counted (100% won, NOT 50%)
    assert s1["big_fav"]["win"]["n_legs"] == 1
    assert s1["big_fav"]["win"]["actual"] == 1.0
    # 1up: only Match 1 counted (100% won, NOT 50%)
    assert s1["big_fav"]["1up"]["n_legs"] == 1
    assert s1["big_fav"]["1up"]["actual"] == 1.0
    # win_or_draw: both Match 1 and Match 2 have known outcomes -> n=2, 100% won
    assert s1["big_fav"]["win_or_draw"]["n_legs"] == 2
    assert s1["big_fav"]["win_or_draw"]["actual"] == 1.0


def test_5_corrected_probabilities_preserve_coherence_bounds():
    """(5) Corrected probabilities keep win <= win-or-draw, win <= 1Up, and stay in [0.001, 0.999]."""
    legs = pd.DataFrame([
        dict(match_key="EPL:10", date=pd.Timestamp("2025-02-01"), season="2024/25", league="EPL", market="home_win", probability=0.82, won=1),
        dict(match_key="EPL:10", date=pd.Timestamp("2025-02-01"), season="2024/25", league="EPL", market="away_win", probability=0.06, won=0),
        dict(match_key="EPL:10", date=pd.Timestamp("2025-02-01"), season="2024/25", league="EPL", market="home_1up", probability=0.86, won=1),
        dict(match_key="EPL:10", date=pd.Timestamp("2025-02-01"), season="2024/25", league="EPL", market="double_1x", probability=0.90, won=1),
    ])
    # Extreme positive shift on win must still obey win <= 1up and win <= win_or_draw.
    up_win = apply_big_fav_shift(legs, "win", shift_d=2.5).set_index("market")["probability"]
    assert CLIP_LOW <= up_win["home_win"] <= CLIP_HIGH
    assert up_win["home_win"] <= up_win["home_1up"]
    assert up_win["home_win"] <= up_win["double_1x"]

    # Extreme negative shift on 1up or win_or_draw must still keep them >= win.
    dn_1up = apply_big_fav_shift(legs, "1up", shift_d=-2.5).set_index("market")["probability"]
    assert dn_1up["home_win"] <= dn_1up["home_1up"] <= CLIP_HIGH

    dn_dc = apply_big_fav_shift(legs, "win_or_draw", shift_d=-2.5).set_index("market")["probability"]
    assert dn_dc["home_win"] <= dn_dc["double_1x"] <= CLIP_HIGH
