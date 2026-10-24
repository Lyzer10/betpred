"""Model health check: is the live model still performing as backtested?

Runs on every daily update over the most recent settled, published predictions.
Each check needs a minimum sample before it can raise an alarm, and alarms need
statistical evidence (not one unlucky weekend):
  accuracy     1X2 log loss vs the bookmaker's, paired per match   (t > 2: warning)
  calibration  hits vs expected for confident slip-market picks    (z < -2.5: warning)
  slips        published slips won vs their predicted chances      (z < -2.5: warning)
"warning" halves every recommended stake in the app; "watch" only shows a notice.
"""
from __future__ import annotations

import numpy as np

WINDOW_MATCHES = 60
MIN_MATCHES = 30
MIN_SLIPS = 20
RESULT_MARKETS = ("home_win", "draw", "away_win")
STAKE_FACTOR = {"ok": 1.0, "watch": 1.0, "warning": 0.5, "insufficient": 1.0}
_RANK = {"insufficient": 0, "ok": 1, "watch": 2, "warning": 3}


def _accuracy(fixtures: list[dict]) -> dict:
    diffs = []
    for fixture in fixtures:
        markets = {m["market"]: m for m in fixture["markets"]}
        if any(markets.get(k, {}).get("market_probability") is None for k in RESULT_MARKETS):
            continue
        outcome = next(k for k in RESULT_MARKETS if fixture["result"]["outcomes"][k])
        ours = max(markets[outcome]["probability"], 1e-9)
        book = max(markets[outcome]["market_probability"], 1e-9)
        diffs.append(-np.log(ours) + np.log(book))     # > 0: we were worse on this match
    if len(diffs) < MIN_MATCHES:
        return {"name": "accuracy", "status": "insufficient", "detail": f"{len(diffs)} of {MIN_MATCHES} matches needed"}
    diffs = np.array(diffs)
    mean, se = diffs.mean(), diffs.std(ddof=1) / np.sqrt(len(diffs))
    t = mean / se if se > 0 else 0.0
    status = "warning" if t > 2 else "watch" if mean > 0.02 else "ok"
    return {"name": "accuracy", "status": status, "matches": len(diffs),
            "detail": f"log loss {'worse' if mean > 0 else 'better'} than bookmakers by {abs(mean):.3f} (t={t:.1f})"}


def _hits_z(probabilities: list[float], outcomes: list[bool]) -> tuple[float, float, float]:
    p = np.array(probabilities)
    expected, observed = p.sum(), float(np.sum(outcomes))
    sd = np.sqrt(np.sum(p * (1 - p)))
    return observed, expected, (observed - expected) / sd if sd > 0 else 0.0


def _calibration(fixtures: list[dict], slip_markets: tuple[str, ...]) -> dict:
    probabilities, outcomes = [], []
    for fixture in fixtures:
        for m in fixture["markets"]:
            if m["market"] in slip_markets and m["probability"] >= 0.5:
                probabilities.append(m["probability"])
                outcomes.append(bool(fixture["result"]["outcomes"][m["market"]]))
    if len(probabilities) < MIN_MATCHES:
        return {"name": "calibration", "status": "insufficient", "detail": f"{len(probabilities)} of {MIN_MATCHES} picks needed"}
    observed, expected, z = _hits_z(probabilities, outcomes)
    status = "warning" if z < -2.5 else "watch" if z < -1.5 else "ok"
    return {"name": "calibration", "status": status, "picks": len(probabilities),
            "detail": f"{observed:.0f} hits vs {expected:.1f} expected (z={z:.1f})"}


def _slips(slips: list[dict]) -> dict:
    settled = [s for s in slips if s.get("status") in ("won", "lost")][-100:]
    if len(settled) < MIN_SLIPS:
        return {"name": "slips", "status": "insufficient", "detail": f"{len(settled)} of {MIN_SLIPS} settled slips needed"}
    observed, expected, z = _hits_z([s["win_probability"] for s in settled], [s["status"] == "won" for s in settled])
    status = "warning" if z < -2.5 else "watch" if z < -1.5 else "ok"
    return {"name": "slips", "status": status, "slips": len(settled),
            "detail": f"{observed:.0f} won vs {expected:.1f} expected (z={z:.1f})"}


def health_check(fixtures: list[dict], slips: list[dict], slip_markets: tuple[str, ...]) -> dict:
    """fixtures: settled archived predictions (oldest first); slips: published slips with status."""
    recent = fixtures[-WINDOW_MATCHES:]
    checks = [_accuracy(recent), _calibration(recent, slip_markets), _slips(slips)]
    # Worst check wins; "insufficient" ranks lowest, so it only shows when no check has enough data.
    status = max((c["status"] for c in checks), key=_RANK.get)
    return {"status": status, "stake_factor": STAKE_FACTOR[status], "checks": checks}
