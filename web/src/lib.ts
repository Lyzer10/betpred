import { useEffect, useState } from "react";
import type { StakingSettings } from "./ledger";
import type { ArchiveSnapshot, MarketKey, MatchLineup, Predictions, Result, SavedPick, ScheduleData, SlipLeg } from "./types";

/** Data files fetched once per minute at most, shared by every screen (going back is instant). */
const jsonCache = new Map<string, { at: number; value: Promise<any> }>();
export function cachedJson(path: string, maxAgeMs = 60_000): Promise<any> {
  const hit = jsonCache.get(path);
  if (hit && Date.now() - hit.at < maxAgeMs) return hit.value;
  const value = fetch(`${import.meta.env.BASE_URL}${path}`, { cache: "no-cache" })
    .then((response) => (response.ok ? response.json() : null))
    .catch(() => null);
  jsonCache.set(path, { at: Date.now(), value });
  return value;
}

/** Announced line-ups; missing file or network error simply means none yet. */
export function useLineups() {
  const [lineups, setLineups] = useState<MatchLineup[]>([]);
  useEffect(() => {
    cachedJson("data/lineups.json").then((file) => setLineups(file?.matches ?? []));
  }, []);
  return lineups;
}

export function useSchedule() {
  const [schedule, setSchedule] = useState<ScheduleData | null>(null);
  useEffect(() => {
    cachedJson("data/schedule.json").then(setSchedule);
  }, []);
  return schedule;
}

export function usePredictions() {
  const [data, setData] = useState<Predictions | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    cachedJson("data/predictions.json", 0)
      .then((value) => value ? setData(value) : setError("predictions unavailable"))
      .catch((reason) => setError(String(reason)));
  }, []);
  return { data, error };
}

export function useArchive(date: string | null) {
  const [snapshot, setSnapshot] = useState<ArchiveSnapshot | null>(null);
  useEffect(() => {
    if (!date) return;
    setSnapshot(null);
    cachedJson(`data/archive/${date}.json`).then(setSnapshot);
  }, [date]);
  return snapshot;
}

export function useArchives(dates: string[]) {
  const [snapshots, setSnapshots] = useState<Record<string, ArchiveSnapshot | null>>({});
  const key = dates.join("|");
  useEffect(() => {
    let active = true;
    Promise.all(dates.map(async (date) => [date, await cachedJson(`data/archive/${date}.json`)] as const))
      .then((entries) => active && setSnapshots(Object.fromEntries(entries)));
    return () => { active = false; };
  }, [key]);
  return snapshots;
}

const SHORT_NAMES: Record<string, string> = {
  "Manchester City": "MCI", "Manchester United": "MUN", "Nottingham Forest": "NFO", "Crystal Palace": "CRY",
  "Aston Villa": "AVL", "West Ham": "WHU", "Newcastle": "NEW", "Tottenham": "TOT", "Wolves": "WOL",
  "Brighton": "BHA", "Bournemouth": "BOU", "Brentford": "BRE", "Everton": "EVE", "Fulham": "FUL",
  "Leeds": "LEE", "Liverpool": "LIV", "Arsenal": "ARS", "Chelsea": "CHE", "Sunderland": "SUN",
  "Burnley": "BUR", "Coventry": "COV", "Hull": "HUL", "Ipswich": "IPS", "Leicester": "LEI", "Southampton": "SOU",
};

export const shortName = (team: string) => SHORT_NAMES[team] ?? team.slice(0, 3).toUpperCase();

/** Team represented by a slip leg's badge; null means the market concerns both teams. */
export function legTeam(leg: Pick<SlipLeg, "market">): "home" | "away" | null {
  switch (leg.market) {
    case "home_win":
    case "home_1up":
    case "home_first":
    case "double_1x":
      return "home";
    case "away_win":
    case "away_1up":
    case "away_first":
    case "double_x2":
      return "away";
    default:
      return null;
  }
}

export function dayLabel(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
}

export function timeLabel(iso: string) {
  return new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

/** Expected return per unit staked: probability x odds - 1. */
export const edge = (probability: number, odds: number) => probability * odds - 1;

export type Verdict = "value" | "fair" | "none";

/** Minimum edge for a value bet. Keep in sync with VALUE_EDGE in engine/src/predict.py. */
export const VALUE_EDGE = 0.03;

export function verdict(probability: number, odds: number): Verdict {
  const e = edge(probability, odds);
  if (e >= VALUE_EDGE) return "value";
  if (e > -VALUE_EDGE) return "fair";
  return "none";
}

// ---- Money management (TSh) -------------------------------------------------
// Quarter-Kelly: full Kelly is optimal only if our probabilities were exact; they are
// estimates, so professionals stake a fraction. Caps keep any one bet small.
export const STAKING = {
  kellyFraction: 0.25,
  maxSingle: 0.02,          // max 2% of bankroll on one single
  // Accumulator caps by tier: longer odds lose more often, so they get less.
  maxTier: { safe: 0.03, medium: 0.02, big: 0.01 } as Record<"safe" | "medium" | "big", number>,
  maxRound: 0.10,           // all stakes for a day together: max 10%
  warningFactor: 0.5,       // halve the stake when the price may be stale
  minStake: 100,            // TSh; stakes below this are skipped
  // Pilot phase: the edge is not yet proven with the user's own bets, so until this many of
  // their slips have settled no slip risks more than pilotCap of the balance, whatever the mode.
  pilotSlips: 30,
  pilotCap: 0.03,
  roundTo: 100,             // TSh
};

export function kellyFraction(probability: number, odds: number) {
  return odds > 1 ? Math.max((probability * odds - 1) / (odds - 1), 0) : 0;
}

/** Recommended stake in TSh (0 = skip). */
export function recommendedStake(bankroll: number, probability: number, odds: number,
  opts: { tier?: "safe" | "medium" | "big"; warning?: boolean; staking?: StakingSettings } = {}) {
  if (!(bankroll > 0) || edge(probability, odds) < VALUE_EDGE) return 0;   // no value: always skip
  const staking = opts.staking;
  let amount: number;
  if (staking?.mode === "fixed") amount = Math.min(staking.fixed, bankroll);
  else if (staking?.mode === "percent") amount = (bankroll * staking.percent) / 100;
  else {
    const cap = opts.tier ? STAKING.maxTier[opts.tier] : STAKING.maxSingle;
    amount = bankroll * Math.min(kellyFraction(probability, odds) * STAKING.kellyFraction, cap);
  }
  if (staking?.pilot) amount = Math.min(amount, bankroll * STAKING.pilotCap);
  if (opts.warning) amount *= STAKING.warningFactor;
  const stake = Math.floor(amount / STAKING.roundTo) * STAKING.roundTo;
  return stake >= STAKING.minStake ? stake : 0;
}

/** Chance of at least one run of `streak` straight losses in `bets` bets (each lost with probability q). */
export function losingStreakChance(q: number, streak: number, bets: number) {
  if (streak <= 0) return 1;
  if (streak > bets) return 0;
  // state[k] = probability the current run of losses has length k, with no full streak yet.
  let state = new Array(streak).fill(0);
  state[0] = 1;
  let hit = 0;
  for (let i = 0; i < bets; i++) {
    const next = new Array(streak).fill(0);
    for (let k = 0; k < streak; k++) {
      next[0] += state[k] * (1 - q);
      if (k + 1 === streak) hit += state[k] * q;
      else next[k + 1] += state[k] * q;
    }
    state = next;
  }
  return hit;
}

/** Scale a round's stakes down proportionally so their total stays within maxRound. */
export function capRound(stakes: number[], bankroll: number) {
  const total = stakes.reduce((a, b) => a + b, 0);
  const limit = bankroll * STAKING.maxRound;
  if (total <= limit || total === 0) return stakes;
  return stakes.map((s) => {
    const scaled = Math.floor((s * limit) / total / STAKING.roundTo) * STAKING.roundTo;
    return scaled >= STAKING.minStake ? scaled : 0;
  });
}

export const tsh = (amount: number) => `TSh ${Math.round(amount).toLocaleString("en-US")}`;


export const pct = (value: number, digits = 0) => `${(value * 100).toFixed(digits)}%`;
export const odds = (value: number) => value.toFixed(2);

export function kickoffLabel(kickoffUtc: string) {
  const date = new Date(kickoffUtc);
  return date.toLocaleString(undefined, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export const fixtureKey = (date: string, home: string, away: string) => `${date}|${home}|${away}`;

/** Find a settled result for a pick; fixtures can shift by a day around midnight. */
export function findResult(results: Result[], home: string, away: string, date: string): Result | undefined {
  const target = new Date(date).getTime();
  return results.find((r) => r.home === home && r.away === away
    && Math.abs(new Date(r.date).getTime() - target) <= 3 * 86_400_000);
}

export function settle(results: Result[], pick: { home: string; away: string; date: string; market: MarketKey }) {
  const result = findResult(results, pick.home, pick.away, pick.date);
  return result ? result.outcomes[pick.market] : null;
}

// Local storage can be unavailable (private mode, blocked site data): never let it break the app.
const PICKS_KEY = "pl-predictor:picks";

export function loadPicks(): SavedPick[] {
  try {
    return JSON.parse(localStorage.getItem(PICKS_KEY) ?? "[]");
  } catch {
    return [];
  }
}

export function storePicks(picks: SavedPick[]) {
  try {
    localStorage.setItem(PICKS_KEY, JSON.stringify(picks));
  } catch {
    /* storage unavailable: picks live for this session only */
  }
}
