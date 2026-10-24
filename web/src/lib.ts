import { useEffect, useState } from "react";
import type { ArchiveSnapshot, MarketKey, Predictions, Result, SavedPick } from "./types";

export function usePredictions() {
  const [data, setData] = useState<Predictions | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/predictions.json`, { cache: "no-cache" })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(setData)
      .catch((reason) => setError(String(reason)));
  }, []);
  return { data, error };
}

export function useArchive(date: string | null) {
  const [snapshot, setSnapshot] = useState<ArchiveSnapshot | null>(null);
  useEffect(() => {
    if (!date) return;
    setSnapshot(null);
    fetch(`${import.meta.env.BASE_URL}data/archive/${date}.json`, { cache: "no-cache" })
      .then((response) => (response.ok ? response.json() : null))
      .then(setSnapshot)
      .catch(() => setSnapshot(null));
  }, [date]);
  return snapshot;
}

const SHORT_NAMES: Record<string, string> = {
  "Manchester City": "MCI", "Manchester United": "MUN", "Nottingham Forest": "NFO", "Crystal Palace": "CRY",
  "Aston Villa": "AVL", "West Ham": "WHU", "Newcastle": "NEW", "Tottenham": "TOT", "Wolves": "WOL",
  "Brighton": "BHA", "Bournemouth": "BOU", "Brentford": "BRE", "Everton": "EVE", "Fulham": "FUL",
  "Leeds": "LEE", "Liverpool": "LIV", "Arsenal": "ARS", "Chelsea": "CHE", "Sunderland": "SUN",
  "Burnley": "BUR", "Coventry": "COV", "Hull": "HUL", "Ipswich": "IPS", "Leicester": "LEI", "Southampton": "SOU",
};

export const shortName = (team: string) => SHORT_NAMES[team] ?? team.slice(0, 3).toUpperCase();

export function dayLabel(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
}

export function timeLabel(iso: string) {
  return new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

/** Expected return per unit staked: probability x odds - 1. */
export const edge = (probability: number, odds: number) => probability * odds - 1;

export type Verdict = "value" | "fair" | "none";

export function verdict(probability: number, odds: number): Verdict {
  const e = edge(probability, odds);
  if (e >= 0.03) return "value";
  if (e > -0.03) return "fair";
  return "none";
}

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
