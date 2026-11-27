import pandas as pd

from src.simulation import simulated_account

NOW = pd.Timestamp("2026-11-28 12:00")


def _slip(round_id, tier, status, odds, final=True, kickoff="2026-11-27T17:00:00Z"):
    return {"round": round_id, "tier": tier, "status": status, "total_odds": odds, "final": final,
            "legs": [{"kickoff_utc": kickoff}]}


def test_only_taken_slips_in_the_window_count_with_fixed_stakes():
    history = [
        _slip("2026-11-26", "safe", "won", 3.0),                         # before the start: ignored
        _slip("2026-11-27", "safe", "won", 2.6),                         # +2500*2.6 - 2500
        _slip("2026-11-27", "medium", "lost", 4.0),                      # -1500
        _slip("2026-11-27", "big", "pending", 9.0, final=False),         # kicked off: taken, stake held
        _slip("2026-11-29", "safe", "pending", 2.8, final=False, kickoff="2026-11-29T15:00:00Z"),  # preview: not taken
        _slip("2027-01-01", "safe", "won", 3.0),                         # after the end: ignored
    ]
    trial = [_slip("2026-11-27", "trial", "lost", 3.1)]
    sim = simulated_account(history, trial, NOW)
    assert [(s["tier"], s["stake"], s["status"]) for s in sim["slips"]] == [
        ("trial", 1000, "lost"), ("safe", 2500, "won"), ("medium", 1500, "lost"), ("big", 1000, "pending")]
    assert sim["staked"] == 6000 and sim["returned"] == 6500 and sim["pending_stake"] == 1000
    assert sim["profit"] == 6500 - 5000                    # settled slips only
    assert sim["balance"] == 15000 - 6000 + 6500           # pending stake is out of the account
    assert sim["tiers"]["safe"] == {"slips": 1, "won": 1, "lost": 0, "pending": 0, "staked": 2500,
                                    "returned": 6500, "profit": 4000}


def test_balance_keeps_going_below_zero():
    history = [_slip(f"2026-12-{d:02d}", "safe", "lost", 2.6) for d in range(1, 8)]   # 7 x 2500 = 17500
    sim = simulated_account(history, [], pd.Timestamp("2026-12-31"))
    assert [s["status"] for s in sim["slips"]] == ["lost"] * 7
    assert sim["balance"] == -2500 and sim["staked"] == 17500 and sim["profit"] == -17500
