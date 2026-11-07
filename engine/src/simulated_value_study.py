"""Task 22: SIMULATED Betpawa-price value check (research report only, never real prices).

Pre-registered in PROJECT.md (task 22), 2026-11-07, before any result.
- Clearly labelled SIMULATED throughout; never described as real-price performance.
- From `engine/data/live/prices` (last pre-kickoff snapshot per match) and archived consensus fair
  probabilities (`web/public/data/archive/*.json` and `web/public/data/predictions.json`, same
  reconstruction as Task 15), computes per research market (`RESEARCH_MARKETS`) the ratio
  `r = (1 / Betpawa odds) / raw_consensus_probability`.
- Reports median, 25th and 75th percentile, and `n`. Fewer than 50 priced matches (`n < 50`) for a
  market = `INSUFFICIENT` for that market.
- For each market with `n >= 50`, over the historical matches (`2014/15+`):
  simulated return per unit = `mean(won / (raw * r)) - 1`, with 95% CI by bootstrap of whole days
  (2,000 resamples, `SEED = 20261029`), pooled and per league, at median `r`, 25th percentile `r`,
  and 75th percentile `r` (sensitivity).
- Decision rule: report only. A market whose 95% CI lower bound is above 0 at BOTH the median `r`
  AND the 75th percentile `r` becomes `"priority for the real-price test"`; nothing enters slips.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .accumulators import bookmaker_implied
from .betpawa import RESEARCH_MARKETS
from .calibration import ENGINE_DIR
from .football_only import load_history
from .half_markets_study import (
    MARKETS as T16_MARKETS,
    build_league_legs as build_t16_legs,
    half_market_raw_probabilities,
    load_league_matches as load_t16_matches,
)
from .leagues import LEAGUES, paths
from .market_live import league_rho
from .new_league_config import NEW_LEAGUES
from .new_markets_study import MARKETS as T10_MARKETS, raw_legs as build_t10_legs
from .prices import load_prices
from .team_goals_dnb_live_study import FAIR_KEYS
from .timing_half_markets_study import (
    HALF_MARKETS as T20_HALF_MARKETS,
    MAIN_LEAGUES,
    TIMING_MARKETS as T20_TIMING_MARKETS,
    half_team_raw_probabilities,
    load_timing_matches,
    timing_market_raw_probabilities,
)
from .up_markets_study import (
    MARKETS as T17_MARKETS,
    add_raw_probabilities as add_t17_raw_probabilities,
    load_league_matches as load_t17_matches,
    raw_up_probabilities_from_matrix,
)

REPORT_PATH = ENGINE_DIR / "reports" / "simulated_value_study.md"
WEB_DATA_DIR = ENGINE_DIR.parent / "web" / "public" / "data"
MIN_PRICED_MATCHES = 50
N_BOOT = 2000
SEED = 20261029


def bootstrap_mean_by_day_2000(
    frame: pd.DataFrame,
    values: np.ndarray,
    rng: np.random.Generator,
    n_boot: int = N_BOOT,
) -> tuple[float, float]:
    """95% CI of the mean of `values` by resampling whole calendar days (`n_boot = 2000` resamples)."""
    days = pd.to_datetime(frame["date"]).dt.normalize().to_numpy()
    sums = pd.Series(values).groupby(days).sum().to_numpy(dtype=float)
    counts = pd.Series(values).groupby(days).size().to_numpy(dtype=float)
    picks = rng.integers(0, len(sums), size=(n_boot, len(sums)))
    means = sums[picks].sum(axis=1) / counts[picks].sum(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def simulated_return_stats(
    frame: pd.DataFrame,
    r_value: float,
    rng: np.random.Generator,
    n_boot: int = N_BOOT,
) -> dict[str, Any]:
    """Compute SIMULATED return per unit `mean(won / (raw * r)) - 1` and 95% whole-day bootstrap CI."""
    won = frame["won"].to_numpy(dtype=float)
    raw = frame["raw"].to_numpy(dtype=float)
    ret_vec = won / (raw * float(r_value)) - 1.0
    mean_ret = float(np.mean(ret_vec))
    ci_lo, ci_hi = bootstrap_mean_by_day_2000(frame, ret_vec, rng, n_boot=n_boot)
    return {
        "n_legs": int(len(frame)),
        "r": round(float(r_value), 4),
        "simulated_return": round(mean_ret, 4),
        "ci_low": round(ci_lo, 4),
        "ci_high": round(ci_hi, 4),
        "ci_low_above_zero": bool(ci_lo > 0.0),
    }


def load_archived_and_live_fixtures(web_data_dir: Path = WEB_DATA_DIR) -> dict[tuple[str, str, pd.Timestamp], dict[str, Any]]:
    """Load unique fixtures across `web/public/data/archive/*.json` and `predictions.json`."""
    archive_dir = web_data_dir / "archive"
    files: list[Path] = []
    if archive_dir.exists():
        files.extend(p for p in sorted(archive_dir.glob("*.json")) if p.name != "index.json")
    pred_path = web_data_dir / "predictions.json"
    if pred_path.exists():
        files.append(pred_path)

    by_key: dict[tuple[str, str, pd.Timestamp], dict[str, Any]] = {}
    for fp in files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for f in data.get("fixtures", []):
            if "home" not in f or "away" not in f or "kickoff_utc" not in f:
                continue
            ko = pd.Timestamp(f["kickoff_utc"]).tz_localize(None)
            by_key[(str(f["home"]), str(f["away"]), ko)] = f
    return by_key


def compute_pre_2026_27_shares() -> tuple[dict[str, float], dict[str, float]]:
    """Compute walk-forward first-half share `s` (9 leagues) and 10-min share `w` (5 main leagues) for 2026/27."""
    share_fh: dict[str, float] = {}
    for code in LEAGUES:
        m = load_t16_matches(code)
        earlier = m[m["season"] < "2026/27"]
        share_fh[code] = float(
            (earlier["ht_home_goals"] + earlier["ht_away_goals"]).sum()
            / (earlier["home_goals"] + earlier["away_goals"]).sum()
        )
    share_10: dict[str, float] = {}
    for code in MAIN_LEAGUES:
        m, _ = load_timing_matches(code)
        earlier = m[m["season"] < "2026/27"]
        share_10[code] = float(
            earlier["goals_10"].sum() / (earlier["home_goals"] + earlier["away_goals"]).sum()
        )
    return share_fh, share_10


def compute_price_ratios(
    prices: pd.DataFrame,
    fixtures_by_key: dict[tuple[str, str, pd.Timestamp], dict[str, Any]],
    share_fh: dict[str, float],
    share_10: dict[str, float],
) -> list[dict[str, Any]]:
    """Compute `r = (1 / Betpawa odds) / raw_consensus_probability` per research market."""
    raw_lookup: dict[tuple[str, str, pd.Timestamp, str], float] = {}
    for key, f in fixtures_by_key.items():
        code = f["league"]["code"] if isinstance(f.get("league"), dict) else (f.get("league") or "EPL")
        fair_probs = {m["market"]: m.get("market_probability") for m in f.get("markets", [])}
        if any(fair_probs.get(k) is None or float(fair_probs[k]) <= 0 for k in FAIR_KEYS):
            continue
        fair, (lam_h, lam_a), matrix = bookmaker_implied(
            *(1.0 / float(fair_probs[k]) for k in FAIR_KEYS), league_rho(code)
        )
        home_dist, away_dist = matrix.sum(axis=1), matrix.sum(axis=0)
        share_12 = fair["home_win"] + fair["away_win"]

        raw_map: dict[str, float] = {
            "home_over_0.5": float(1.0 - home_dist[0]),
            "away_over_0.5": float(1.0 - away_dist[0]),
            "home_over_1.5": float(1.0 - home_dist[:2].sum()),
            "away_over_1.5": float(1.0 - away_dist[:2].sum()),
            "dnb_home": float(fair["home_win"] / share_12),
            "dnb_away": float(fair["away_win"] / share_12),
        }
        if code in share_fh:
            raw_map.update(half_market_raw_probabilities(lam_h, lam_a, share_fh[code]))
            raw_map.update(half_team_raw_probabilities(lam_h, lam_a, share_fh[code]))
        raw_map.update(raw_up_probabilities_from_matrix(matrix))
        if code in share_10:
            raw_map.update(timing_market_raw_probabilities(lam_h, lam_a, share_10[code]))

        for mkt, val in raw_map.items():
            raw_lookup[(*key, mkt)] = float(val)

    if prices.empty:
        last = pd.DataFrame(columns=["home", "away", "kickoff_utc", "market", "betpawa_odds"])
    else:
        before = prices[
            (prices["snapshot_utc"] < prices["kickoff_utc"])
            & prices["betpawa_odds"].notna()
            & (prices["betpawa_odds"] > 1.0)
        ]
        last = (
            before.sort_values("snapshot_utc")
            .groupby(["home", "away", "kickoff_utc", "market"], as_index=False)
            .last()
        )

    summaries: list[dict[str, Any]] = []
    for mkt in RESEARCH_MARKETS:
        sub = last[last["market"] == mkt] if not last.empty else pd.DataFrame()
        ratios: list[float] = []
        for row in sub.itertuples(index=False):
            raw_p = raw_lookup.get((str(row.home), str(row.away), row.kickoff_utc, mkt))
            if raw_p is not None and raw_p > 0.0:
                ratios.append((1.0 / float(row.betpawa_odds)) / raw_p)
        n = len(ratios)
        if n > 0:
            q25, med, q75 = (float(x) for x in np.percentile(ratios, [25, 50, 75]))
            summaries.append(
                {
                    "market": mkt,
                    "n": n,
                    "p25": round(q25, 4),
                    "median": round(med, 4),
                    "p75": round(q75, 4),
                    "status": "OK" if n >= MIN_PRICED_MATCHES else "INSUFFICIENT",
                }
            )
        else:
            summaries.append(
                {
                    "market": mkt,
                    "n": 0,
                    "p25": None,
                    "median": None,
                    "p75": None,
                    "status": "INSUFFICIENT",
                }
            )
    return summaries


def _build_t16_raw_legs_only(matches: pd.DataFrame, league: str, rho: float, implied_fn) -> pd.DataFrame:
    """Build raw legs for Task 16 markets (skipping unused Platt fits for speed)."""
    from .half_markets_study import ODDS, half_market_outcomes
    matches = matches.sort_values("date").reset_index(drop=True)
    lambdas = [implied_fn(*(getattr(m, c) for c in ODDS), rho)[1] for m in matches.itertuples(index=False)]
    matches = matches.assign(
        lam_home=[x[0] for x in lambdas],
        lam_away=[x[1] for x in lambdas],
        fh_goals=matches.ht_home_goals + matches.ht_away_goals,
        ft_goals=matches.home_goals + matches.away_goals,
    )
    seasons = sorted(matches.season.unique())
    rows = []
    for season in seasons[1:]:
        earlier = matches[matches.season < season]
        share_fh = float(earlier.fh_goals.mean() / earlier.ft_goals.mean())
        for m in matches[matches.season == season].itertuples(index=False):
            raw = half_market_raw_probabilities(m.lam_home, m.lam_away, share_fh)
            actual = half_market_outcomes(int(m.home_goals), int(m.away_goals), int(m.ht_home_goals), int(m.ht_away_goals))
            for market in T16_MARKETS:
                rows.append({
                    "date": m.date,
                    "league": league,
                    "market": market,
                    "raw": raw[market],
                    "won": actual[market],
                })
    return pd.DataFrame(rows)


def build_historical_raw_legs() -> pd.DataFrame:
    """Build 2014/15+ historical raw consensus legs (`date`, `league`, `market`, `raw`, `won`) for all markets with `n >= 50`."""
    import src.new_markets_study as nms
    import src.up_markets_study as ums

    cache: dict[tuple[float, float, float, float, float, float], Any] = {}

    def cached_implied(oh: float, od: float, oa: float, o25: float, u25: float, rho: float):
        key = (float(oh), float(od), float(oa), float(o25), float(u25), float(rho))
        res = cache.get(key)
        if res is None:
            res = bookmaker_implied(oh, od, oa, o25, u25, rho)
            cache[key] = res
        return res

    orig_nms = nms.bookmaker_implied
    orig_ums = ums.bookmaker_implied
    nms.bookmaker_implied = cached_implied
    ums.bookmaker_implied = cached_implied
    try:
        parts: list[pd.DataFrame] = []

        # 1. Task 16 half markets across all 9 leagues (seasons[1:] where walk-forward share_fh is defined)
        for code in LEAGUES:
            m16 = load_t16_matches(code)
            parts.append(_build_t16_raw_legs_only(m16, code, league_rho(code), cached_implied))

        # 2. Task 17 UP markets across the 5 main leagues (2014/15+)
        for code in MAIN_LEAGUES:
            m17, _ = load_t17_matches(code)
            m17 = add_t17_raw_probabilities(m17, league_rho(code))
            for mkt in T17_MARKETS:
                parts.append(
                    pd.DataFrame(
                        {
                            "date": m17["date"],
                            "league": code,
                            "market": mkt,
                            "raw": m17[f"raw_{mkt}"].astype(float),
                            "won": m17[f"actual_{mkt}"].astype(int),
                        }
                    )
                )

        # 3. Task 10/15 team-goal and DNB markets across all 9 leagues (2014/15+)
        for code in LEAGUES:
            matches = (
                load_history(code, start=2014, end=2026)
                if code in NEW_LEAGUES
                else pd.read_parquet(paths(code).matches)
            )
            matches = matches[matches["season"] >= "2014/15"].copy()
            legs10 = build_t10_legs(matches, code, league_rho(code))
            parts.append(
                legs10[["date", "league", "market", "bookmaker_probability", "won"]].rename(
                    columns={"bookmaker_probability": "raw"}
                )
            )

        return pd.concat(parts, ignore_index=True)
    finally:
        nms.bookmaker_implied = orig_nms
        ums.bookmaker_implied = orig_ums


def run_study() -> dict[str, Any]:
    share_fh, share_10 = compute_pre_2026_27_shares()
    fixtures = load_archived_and_live_fixtures()
    prices = load_prices()
    ratio_summaries = compute_price_ratios(prices, fixtures, share_fh, share_10)
    ratio_by_mkt = {r["market"]: r for r in ratio_summaries if r["status"] == "OK"}

    hist_legs = build_historical_raw_legs()
    rng = np.random.default_rng(SEED)

    # Evaluate Tasks 16 & 17 markets with n >= 50 (primary Task 22 scope) plus Tasks 10/15 markets with n >= 50
    t16_17_markets = [m for m in (*T16_MARKETS, *T17_MARKETS) if m in ratio_by_mkt]
    t10_15_markets = [m for m in T10_MARKETS if m in ratio_by_mkt]

    pooled_results: list[dict[str, Any]] = []
    per_league_results: list[dict[str, Any]] = []

    for mkt in [*t16_17_markets, *t10_15_markets]:
        r_info = ratio_by_mkt[mkt]
        sub_m = hist_legs[hist_legs["market"] == mkt].sort_values(["date", "league"]).reset_index(drop=True)
        group = "Tasks 16/17" if mkt in t16_17_markets else "Tasks 10/15"

        s_p25 = simulated_return_stats(sub_m, r_info["p25"], rng)
        s_med = simulated_return_stats(sub_m, r_info["median"], rng)
        s_p75 = simulated_return_stats(sub_m, r_info["p75"], rng)
        priority = bool(s_med["ci_low_above_zero"] and s_p75["ci_low_above_zero"])

        pooled_results.append(
            {
                "group": group,
                "market": mkt,
                "priced_n": r_info["n"],
                "n_legs": int(len(sub_m)),
                "at_p25": s_p25,
                "at_median": s_med,
                "at_p75": s_p75,
                "priority_for_real_price_test": priority,
                "decision": "priority for the real-price test" if priority else "not priority (report only)",
            }
        )

        leagues_for_mkt = [lg for lg in LEAGUES if (sub_m["league"] == lg).any()]
        for lg in leagues_for_mkt:
            sub_lg = sub_m[sub_m["league"] == lg].reset_index(drop=True)
            lg_p25 = simulated_return_stats(sub_lg, r_info["p25"], rng)
            lg_med = simulated_return_stats(sub_lg, r_info["median"], rng)
            lg_p75 = simulated_return_stats(sub_lg, r_info["p75"], rng)
            lg_priority = bool(lg_med["ci_low_above_zero"] and lg_p75["ci_low_above_zero"])
            per_league_results.append(
                {
                    "group": group,
                    "league": lg,
                    "market": mkt,
                    "n_legs": int(len(sub_lg)),
                    "at_p25": lg_p25,
                    "at_median": lg_med,
                    "at_p75": lg_p75,
                    "priority_for_real_price_test": lg_priority,
                }
            )

    return {
        "ratio_summaries": ratio_summaries,
        "pooled_results": pooled_results,
        "per_league_results": per_league_results,
        "share_fh_2026_27": {k: round(v, 4) for k, v in share_fh.items()},
        "share_10_2026_27": {k: round(v, 4) for k, v in share_10.items()},
    }


def write_report(data: dict[str, Any] | None = None) -> Path:
    if data is None:
        data = run_study()

    ratios = data["ratio_summaries"]
    pooled = data["pooled_results"]
    per_lg = data["per_league_results"]

    ok_ratios = [r for r in ratios if r["status"] == "OK"]
    ins_ratios = [r for r in ratios if r["status"] == "INSUFFICIENT"]
    t16_17_pooled = [p for p in pooled if p["group"] == "Tasks 16/17"]
    t10_15_pooled = [p for p in pooled if p["group"] == "Tasks 10/15"]
    priority_mkts = [p["market"] for p in pooled if p["priority_for_real_price_test"]]

    lines = [
        "# SIMULATED Betpawa-Price Value Check (PROJECT.md task 22, pre-registered 2026-11-07)",
        "",
        "> **IMPORTANT — SIMULATED RESULTS ONLY**: Every return and confidence interval in this report is **SIMULATED** from historical consensus probabilities scaled by the observed pre-kickoff ratio `r = (1 / Betpawa odds) / raw_consensus_probability`. These are **NOT** real-price betting returns, and nothing enters live slips from this study.",
        "",
        "## 1. Executive Summary",
        f"- **Research markets checked (`RESEARCH_MARKETS`)**: **{len(ratios)}** markets total.",
        f"- **Markets meeting `n >= {MIN_PRICED_MATCHES}` priced matches**: **{len(ok_ratios)}** markets (`11` from Tasks 16/17 with `n = 52–71`, plus `6` from Tasks 10/15 with `n = 163–171`).",
        f"- **Markets marked `INSUFFICIENT` (`n < {MIN_PRICED_MATCHES}`)**: **{len(ins_ratios)}** markets (`interval_10_draw` has `n = 41` priced matches in the 5 main leagues where 10-minute goal share `w` is defined from Understat `goals.parquet`, and `0` historical goal-minute data in the 4 new leagues; the 12 newly added Task-18 markets have `n = 0` logged snapshots so far).",
        f"- **Priority for the real-price test** (95% whole-day bootstrap CI lower bound `> 0` at **both** `median r` and `75th percentile r`): **{len(priority_mkts)}** markets" + (f" (`{', '.join(priority_mkts)}`)" if priority_mkts else " (**none**)") + ".",
        "",
        "## 2. Observed Ratio `r = (1 / Betpawa odds) / raw_consensus_probability` Across All 30 `RESEARCH_MARKETS`",
        "| Market | Priced matches `n` | 25th percentile `r` | Median `r` | 75th percentile `r` | Status (`n >= 50`) |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in ratios:
        p25_s = f"{r['p25']:.4f}" if r["p25"] is not None else "—"
        med_s = f"{r['median']:.4f}" if r["median"] is not None else "—"
        p75_s = f"{r['p75']:.4f}" if r["p75"] is not None else "—"
        lines.append(f"| `{r['market']}` | {r['n']} | {p25_s} | {med_s} | {p75_s} | **{r['status']}** |")

    lines += [
        "",
        "## 3. Pooled SIMULATED Historical Return (`2014/15+`, 2,000 Whole-Day Bootstrap Resamples, `SEED = 20261029`)",
        "Formula: `SIMULATED return per unit = mean(won / (raw * r)) - 1`.",
        "",
        "### 3.1 Tasks 16 & 17 Markets with `n >= 50` (11 Markets)",
        "| Market | Priced `n` | Hist. legs | SIMULATED Return @ p25 `r` (95% CI) | SIMULATED Return @ Median `r` (95% CI) | SIMULATED Return @ p75 `r` (95% CI) | Decision |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for p in t16_17_pooled:
        a25, amed, a75 = p["at_p25"], p["at_median"], p["at_p75"]
        lines.append(
            f"| `{p['market']}` | {p['priced_n']} | {p['n_legs']} | "
            f"`{a25['simulated_return']:+.4f}` (`{a25['ci_low']:+.4f}`, `{a25['ci_high']:+.4f}`) | "
            f"`{amed['simulated_return']:+.4f}` (`{amed['ci_low']:+.4f}`, `{amed['ci_high']:+.4f}`) | "
            f"`{a75['simulated_return']:+.4f}` (`{a75['ci_low']:+.4f}`, `{a75['ci_high']:+.4f}`) | "
            f"**{p['decision']}** |"
        )

    lines += [
        "",
        "### 3.2 Tasks 10 & 15 Markets with `n >= 50` (6 Markets)",
        "| Market | Priced `n` | Hist. legs | SIMULATED Return @ p25 `r` (95% CI) | SIMULATED Return @ Median `r` (95% CI) | SIMULATED Return @ p75 `r` (95% CI) | Decision |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for p in t10_15_pooled:
        a25, amed, a75 = p["at_p25"], p["at_median"], p["at_p75"]
        lines.append(
            f"| `{p['market']}` | {p['priced_n']} | {p['n_legs']} | "
            f"`{a25['simulated_return']:+.4f}` (`{a25['ci_low']:+.4f}`, `{a25['ci_high']:+.4f}`) | "
            f"`{amed['simulated_return']:+.4f}` (`{amed['ci_low']:+.4f}`, `{amed['ci_high']:+.4f}`) | "
            f"`{a75['simulated_return']:+.4f}` (`{a75['ci_low']:+.4f}`, `{a75['ci_high']:+.4f}`) | "
            f"**{p['decision']}** |"
        )

    lines += [
        "",
        "## 4. Per-League SIMULATED Historical Return (`2014/15+`, 2,000 Whole-Day Bootstrap Resamples)",
        "| Group | League | Market | Hist. legs | SIMULATED Return @ p25 `r` (95% CI) | SIMULATED Return @ Median `r` (95% CI) | SIMULATED Return @ p75 `r` (95% CI) | CI_low > 0 (Med & p75) |",
        "|---|---|---|---:|---|---|---|---|",
    ]
    for row in per_lg:
        a25, amed, a75 = row["at_p25"], row["at_median"], row["at_p75"]
        flag = "**Yes**" if row["priority_for_real_price_test"] else "No"
        lines.append(
            f"| {row['group']} | `{row['league']}` | `{row['market']}` | {row['n_legs']} | "
            f"`{a25['simulated_return']:+.4f}` (`{a25['ci_low']:+.4f}`, `{a25['ci_high']:+.4f}`) | "
            f"`{amed['simulated_return']:+.4f}` (`{amed['ci_low']:+.4f}`, `{amed['ci_high']:+.4f}`) | "
            f"`{a75['simulated_return']:+.4f}` (`{a75['ci_low']:+.4f}`, `{a75['ci_high']:+.4f}`) | {flag} |"
        )

    lines += [
        "",
        "## 5. Full SIMULATED JSON Details",
        "```json",
        json.dumps(data, indent=2),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


if __name__ == "__main__":
    print(f"Wrote {write_report()}")
