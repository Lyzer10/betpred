"""Betpawa booking codes for the published slips (no account, no login, no money).

Betpawa's own website creates a shareable booking code from a list of price ids
(POST /api/sportsbook/v3/booking-number, checked 2026-11-08 without logging in). The owner copies
the code into their own Betpawa account ("Load Betslip") and places the bet themselves.

Accuracy guard: a code is published only after loading it back from Betpawa and checking that it
holds exactly the slip's price ids, one per match. Any failure means no code (never a wrong one).
Codes are cached by their set of price ids, so an unchanged slip never asks Betpawa again.
"""
from __future__ import annotations

import json
import time

import pandas as pd
import requests

from .betpawa import HEADERS, PAUSE_SECONDS
from .calibration import ENGINE_DIR

BOOKING_URL = "https://www.betpawa.co.tz/api/sportsbook/v3/booking-number"
CACHE_PATH = ENGINE_DIR / "data" / "live" / "booking_codes.json"
KEEP_DAYS = 3


def _key(price_ids: list[str]) -> str:
    return "-".join(sorted(price_ids))


def create_code(price_ids: list[str], session: requests.Session) -> str | None:
    """Ask Betpawa for a booking code, then load it back and confirm it holds exactly these prices."""
    body = {"selections": {"selections": [{"type": "SINGLE", "selections": [int(p)]} for p in price_ids]}}
    response = session.post(BOOKING_URL, json=body, headers=HEADERS | {"content-type": "application/json"}, timeout=30)
    response.raise_for_status()
    code = str(response.json().get("code") or "").strip()
    if not code:
        return None
    time.sleep(PAUSE_SECONDS)
    check = session.get(f"{BOOKING_URL}/{code}", headers=HEADERS, timeout=30)
    check.raise_for_status()
    return code if loaded_price_ids(check.json()) == sorted(price_ids) else None


def loaded_price_ids(betslip: dict) -> list[str] | None:
    """Price ids in a loaded booking code, or None if any match holds other than one selection."""
    ids = []
    for item in betslip.get("items", []):
        selections = item.get("odds", {}).get("selections", [])
        if len(selections) != 1:
            return None
        ids.append(str(selections[0]))
    return sorted(ids)


def add_booking_codes(slips: dict, now: pd.Timestamp, online: bool = True,
                      session: requests.Session | None = None) -> dict:
    """Add `booking_code` to each slip whose legs all have a Betpawa price and none has kicked off."""
    cache = _read_cache()
    before = dict(cache)
    session = session or requests.Session()
    out = {}
    for tier, slip in slips.items():
        slip = {k: v for k, v in slip.items() if k != "booking_code"}
        ids = [leg.get("betpawa_price_id") for leg in slip.get("legs", [])]
        started = any(pd.Timestamp(leg["kickoff_utc"]).tz_localize(None) <= now for leg in slip.get("legs", []))
        if ids and all(ids) and not started:
            key = _key(ids)
            if key not in cache and online:
                try:
                    code = create_code(ids, session)
                    time.sleep(PAUSE_SECONDS)
                except (requests.RequestException, ValueError) as error:
                    print(f"Booking code for {tier} slip unavailable ({error})")
                    code = None
                if code:
                    cache[key] = {"code": code, "created_utc": now.isoformat() + "Z"}
            if key in cache:
                slip["booking_code"] = cache[key]["code"]
        out[tier] = slip
    if cache != before:      # written only when a new code was added (tests and empty runs leave no file)
        _write_cache(cache, now)
    return out


def _read_cache() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_cache(cache: dict, now: pd.Timestamp) -> None:
    cutoff = now - pd.Timedelta(days=KEEP_DAYS)
    kept = {k: v for k, v in cache.items() if pd.Timestamp(v["created_utc"]).tz_localize(None) >= cutoff}
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(kept, indent=2, sort_keys=True), encoding="utf-8")
