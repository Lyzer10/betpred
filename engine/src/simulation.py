"""Simulated Betpawa account (owner request 2026-11-27): every slip the app finalises is "taken".

From START to END each final slip (or one whose first match has kicked off: frozen, so the one the
owner would have placed) is staked at a fixed amount at its published Betpawa odds. A win returns
stake x odds, a loss returns nothing, a pending slip holds its stake. Real Money records are untouched.
"""
from __future__ import annotations

import pandas as pd

START, END = "2026-11-27", "2026-12-31"
START_BALANCE = 15000
STAKES = {"trial": 1000, "safe": 2500, "medium": 1500, "big": 1000}   # TSh per slip, all on Betpawa
TIER_ORDER = ("trial", "safe", "medium", "big")


def _taken(entry: dict, now: pd.Timestamp) -> bool:
    if entry.get("final"):
        return True
    kickoffs = [pd.Timestamp(leg["kickoff_utc"]).tz_localize(None) for leg in entry.get("legs", []) if leg.get("kickoff_utc")]
    return bool(kickoffs) and min(kickoffs) <= now


def simulated_account(history: list[dict], trial_history: list[dict], now: pd.Timestamp) -> dict:
    entries = [e for e in [*history, *trial_history]
               if e.get("tier") in STAKES and START <= str(e.get("round", "")) <= END and _taken(e, now)]
    entries.sort(key=lambda e: (e["round"], TIER_ORDER.index(e["tier"])))
    # Owner 2026-11-27: every slip is always staked, even below zero, so the balance shows the true result.
    balance, slips = float(START_BALANCE), []
    tiers = {t: {"slips": 0, "won": 0, "lost": 0, "pending": 0, "staked": 0, "returned": 0.0} for t in TIER_ORDER}
    for e in entries:
        stake, status = STAKES[e["tier"]], e.get("status", "pending")
        returned = round(stake * e["total_odds"]) if status == "won" else 0
        balance += returned - stake
        row = tiers[e["tier"]]
        row["slips"] += 1
        row[status if status in ("won", "lost") else "pending"] += 1
        row["staked"] += stake
        row["returned"] += returned
        slips.append({"round": e["round"], "tier": e["tier"], "stake": stake, "odds": e["total_odds"],
                      "status": status if status in ("won", "lost") else "pending", "returned": returned})
    staked = sum(r["staked"] for r in tiers.values())
    returned = sum(r["returned"] for r in tiers.values())
    pending = sum(s["stake"] for s in slips if s["status"] == "pending")
    for row in tiers.values():
        row["profit"] = round(row["returned"] - row["staked"])
    return {"start": START, "end": END, "start_balance": START_BALANCE, "stakes": STAKES, "bookmaker": "betpawa",
            "balance": round(balance), "staked": staked, "returned": round(returned), "pending_stake": pending,
            # profit counts settled slips only; pending stakes are still out
            "profit": round(returned - (staked - pending)), "tiers": tiers, "slips": slips}
