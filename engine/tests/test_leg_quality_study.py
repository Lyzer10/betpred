"""Known-answer synthetic tests for PROJECT.md task 25 (leg_quality_study)."""
import pandas as pd

from src.leg_quality_study import (
    FEWER_TIERS,
    MIN_LEG_PROB,
    paired_return_comparison,
    select_day_slips,
)


def _synthetic_day_pool() -> pd.DataFrame:
    """Synthetic day with enough matches for Safe, Medium, and Big under A, L, F, and D.

    Contains both high-probability legs (>= 0.70, odds 1.38-1.45) and sub-0.70 legs (0.58-0.65,
    odds 1.55-1.70) so A and F can pick weaker legs while L must ignore them.
    """
    rows = []
    for m in range(8):
        rows.append(dict(
            date=pd.Timestamp("2025-01-10"), match_id=f"M{m}", match_key=f"M{m}",
            market="over_1.5", probability=0.76, odds=1.40, won=1,
        ))
        rows.append(dict(
            date=pd.Timestamp("2025-01-10"), match_id=f"M{m}", match_key=f"M{m}",
            market="double_1x", probability=0.72, odds=1.46, won=1,
        ))
        rows.append(dict(
            date=pd.Timestamp("2025-01-10"), match_id=f"M{m}", match_key=f"M{m}",
            market="home_win", probability=0.62, odds=1.65, won=0,
        ))
    return pd.DataFrame(rows)


def test_l_never_selects_leg_below_070():
    # Pool where A strongly prefers a 2-leg slip with a 0.65 leg (p=0.65*0.80=0.52, odds=1.70*1.55=2.635),
    # while L can only use >=0.70 legs.
    rows = [
        dict(match_id="M1", match_key="M1", market="home_win", probability=0.65, odds=1.75, won=1),
        dict(match_id="M2", match_key="M2", market="over_1.5", probability=0.80, odds=1.50, won=1),
        dict(match_id="M3", match_key="M3", market="double_1x", probability=0.72, odds=1.35, won=1),
        dict(match_id="M4", match_key="M4", market="over_1.5", probability=0.71, odds=1.35, won=1),
        dict(match_id="M5", match_key="M5", market="double_x2", probability=0.71, odds=1.40, won=1),
    ]
    pool = pd.DataFrame(rows)
    a = select_day_slips(pool, "A")
    l_slips = select_day_slips(pool, "L")
    assert "safe" in a and (a["safe"].probability < MIN_LEG_PROB).any()
    assert "safe" in l_slips
    for slip in l_slips.values():
        assert (slip.probability >= MIN_LEG_PROB).all()


def test_l_omits_tier_when_no_valid_slip_above_070():
    # Only two matches; reaching Safe odds [2.5, 3.5] requires the sub-0.70 leg.
    pool = pd.DataFrame([
        dict(match_id="M1", match_key="M1", market="home_win", probability=0.60, odds=1.80, won=1),
        dict(match_id="M2", match_key="M2", market="over_1.5", probability=0.75, odds=1.45, won=1),
    ])
    a = select_day_slips(pool, "A")
    l_slips = select_day_slips(pool, "L")
    assert "safe" in a
    assert l_slips == {}


def test_f_never_exceeds_leg_cap():
    # 8 matches each with a low-odds high-probability leg (odds=1.38, p=0.85) and a higher-odds leg (odds=1.60, p=0.62).
    # Under A, Safe can use 4 low-odds legs? 1.38^3=2.628, 1.38^4=3.627 (>3.5). Use 1.28 so 1.28^4=2.684 fits Safe 4 legs,
    # 1.28^5=3.436, 1.28^6=4.398 fits Medium 6 legs, 1.28^8=7.206; use 1.32 so:
    # 1.32^4 = 3.036 (4 legs, p=0.88^4=0.600) vs 3 legs @ 1.40 (2.744, p=0.70^3=0.343) -> A picks 4 legs for Safe!
    # 1.32^6 = 5.291 (6 legs, p=0.88^6=0.464) vs 4 legs @ 1.40 (3.842, p=0.70^4=0.240) -> A picks 6 legs for Medium!
    # 1.32^8 = 9.219 (8 legs, p=0.88^8=0.360) vs 6 legs @ 1.45 (9.294, p=0.65^6=0.075) -> A picks 8 legs for Big!
    rows = []
    for m in range(8):
        rows.append(dict(match_id=f"M{m}", match_key=f"M{m}", market="over_1.5", probability=0.88, odds=1.32, won=1))
        rows.append(dict(match_id=f"M{m}", match_key=f"M{m}", market="double_1x", probability=0.70, odds=1.40, won=1))
        rows.append(dict(match_id=f"M{m}", match_key=f"M{m}", market="home_win", probability=0.65, odds=1.45, won=1))
    pool = pd.DataFrame(rows)
    a = select_day_slips(pool, "A")
    f = select_day_slips(pool, "F")
    caps = {t.name: t.max_legs for t in FEWER_TIERS}
    # Under A, every tier strictly exceeds F's cap (4 > 3, 5 > 4, 8 > 6).
    for name in ("safe", "medium", "big"):
        assert len(a[name]) > caps[name]
    assert set(f.keys()) == {"safe", "medium", "big"}
    for name, slip in f.items():
        assert len(slip) <= caps[name]


def test_identical_variants_give_identical_slips_and_zero_diff():
    pool = _synthetic_day_pool()
    a1 = select_day_slips(pool, "A")
    a2 = select_day_slips(pool, "A")
    assert list(a1.keys()) == list(a2.keys()) == ["safe", "medium", "big"]
    for tier in a1:
        assert a1[tier].reset_index(drop=True).equals(a2[tier].reset_index(drop=True))

    # When all legs have p >= 0.70 and optimal slips stay within F's caps, A, L, and F are identical.
    clean = pd.DataFrame([
        dict(match_id=f"M{m}", match_key=f"M{m}", market="over_1.5", probability=0.80, odds=1.60, won=1)
        for m in range(5)
    ])
    a_clean = select_day_slips(clean, "A")
    l_clean = select_day_slips(clean, "L")
    f_clean = select_day_slips(clean, "F")
    for tier in a_clean:
        assert a_clean[tier].reset_index(drop=True).equals(l_clean[tier].reset_index(drop=True))
        assert a_clean[tier].reset_index(drop=True).equals(f_clean[tier].reset_index(drop=True))

    # Identical slip values across two variants produce exact 0 difference and [0, 0] CI.
    slips_df = pd.DataFrame([
        dict(date="2025-01-10", tier="safe", variant="A", value=1.8),
        dict(date="2025-01-10", tier="safe", variant="L", value=1.8),
        dict(date="2025-01-11", tier="safe", variant="A", value=-1.0),
        dict(date="2025-01-11", tier="safe", variant="L", value=-1.0),
    ])
    comp = paired_return_comparison(slips_df, "L", "A", resamples=200, seed=20261123)
    assert comp["gain"] == 0.0
    assert comp["ci_low"] == 0.0 and comp["ci_high"] == 0.0


def test_d_never_repeats_identical_match_and_market():
    pool = _synthetic_day_pool()
    d = select_day_slips(pool, "D")
    seen: set[str] = set()
    for slip in d.values():
        keys = set(slip.match_key + "|" + slip.market)
        assert not (seen & keys)
        seen |= keys
