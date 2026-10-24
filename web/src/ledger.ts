// Money ledger: bookmaker accounts, placed slips, deposits and withdrawals.
// Stored on this device only. Balances are derived from the entries, never typed
// twice: start + deposits - withdrawals - stakes + returns of won slips.
import type { MarketKey, Result, TierName } from "./types";
import { settle } from "./lib";

export type Bookmaker = "betpawa" | "sportybet";
export const BOOKMAKERS: Record<Bookmaker, string> = { betpawa: "Betpawa", sportybet: "SportyBet" };

export interface PlacedLeg { home: string; away: string; date: string; market: MarketKey; label: string; probability: number }

export interface PlacedBet {
  id: string;
  type: "bet";
  placedAt: string;
  day: string;
  bookmaker: Bookmaker;
  tier: TierName;
  stake: number;
  odds: number;                   // total odds as placed
  winProbability: number;         // our probability at placement (for the record)
  flexi?: { minCorrect: number; toWin: number };  // SportyBet Flexi: fixed payout if >= minCorrect legs win
  legs: PlacedLeg[];
}

export interface Transfer {
  id: string;
  type: "deposit" | "withdrawal";
  placedAt: string;
  bookmaker: Bookmaker;
  amount: number;
}

export type Entry = PlacedBet | Transfer;

/** How stakes are sized. "smart" = quarter Kelly with tier caps (the default). */
export type StakingMode = "smart" | "percent" | "fixed";
export interface StakingSettings {
  mode: StakingMode; percent: number; fixed: number;
  pilot?: boolean;   // runtime only: fewer than STAKING.pilotSlips settled slips, so stakes are capped
}

/** Number of the user's slips that have settled (won or lost). */
export function settledSlips(ledger: Ledger, results: Result[]) {
  return ledger.entries.filter((e): e is PlacedBet => e.type === "bet").filter((b) => betStatus(b, results).status !== "pending").length;
}
export const DEFAULT_STAKING: StakingSettings = { mode: "smart", percent: 10, fixed: 2500 };

export interface Ledger {
  start: Record<Bookmaker, number>;   // balance when you started tracking
  entries: Entry[];
  staking?: StakingSettings;
}

const LEDGER_KEY = "pl-predictor:ledger";
const OLD_BANKROLL_KEY = "pl-predictor:bankroll";

export function loadLedger(): Ledger {
  try {
    const raw = localStorage.getItem(LEDGER_KEY);
    if (raw) return JSON.parse(raw);
    // Carry over a balance saved by the earlier version of the app.
    const old = Number(localStorage.getItem(OLD_BANKROLL_KEY)) || 0;
    return { start: { betpawa: old, sportybet: 0 }, entries: [] };
  } catch {
    return { start: { betpawa: 0, sportybet: 0 }, entries: [] };
  }
}

export function storeLedger(ledger: Ledger) {
  try {
    localStorage.setItem(LEDGER_KEY, JSON.stringify(ledger));
  } catch {
    /* storage unavailable: the ledger lives for this session only */
  }
}

export type BetStatus = "won" | "lost" | "pending";

/** Settle a placed slip from results; Flexi wins once enough legs can no longer fail. */
export function betStatus(bet: PlacedBet, results: Result[]): { status: BetStatus; legs: (boolean | null)[] } {
  const legs = bet.legs.map((leg) => settle(results, leg));
  const won = legs.filter((l) => l === true).length;
  const lost = legs.filter((l) => l === false).length;
  const need = bet.flexi?.minCorrect ?? bet.legs.length;
  if (won >= need) return { status: "won", legs };
  if (bet.legs.length - lost < need) return { status: "lost", legs };
  return { status: "pending", legs };
}

export const payout = (bet: PlacedBet) => (bet.flexi ? bet.flexi.toWin : bet.stake * bet.odds);

export interface AccountSummary {
  balance: number;       // money in the account now (pending stakes already taken out)
  staked: number;
  returned: number;
  profit: number;        // settled bets only
  deposits: number;
  withdrawals: number;
  pendingStakes: number;
  won: number;
  lost: number;
  pending: number;
}

export function summarise(ledger: Ledger, bookmaker: Bookmaker, results: Result[]): AccountSummary {
  const s: AccountSummary = { balance: ledger.start[bookmaker] ?? 0, staked: 0, returned: 0, profit: 0,
    deposits: 0, withdrawals: 0, pendingStakes: 0, won: 0, lost: 0, pending: 0 };
  for (const entry of ledger.entries) {
    if (entry.bookmaker !== bookmaker) continue;
    if (entry.type !== "bet") {
      const sign = entry.type === "deposit" ? 1 : -1;
      if (sign > 0) s.deposits += entry.amount; else s.withdrawals += entry.amount;
      s.balance += sign * entry.amount;
      continue;
    }
    const { status } = betStatus(entry, results);
    s.balance -= entry.stake;
    if (status === "pending") { s.pending += 1; s.pendingStakes += entry.stake; continue; }
    s.staked += entry.stake;
    if (status === "won") { s.won += 1; s.returned += payout(entry); s.balance += payout(entry); }
    else s.lost += 1;
  }
  s.profit = s.returned - s.staked;
  return s;
}

export const isBet = (entry: Entry): entry is PlacedBet => entry.type === "bet";
export const isTransfer = (entry: Entry): entry is Transfer => entry.type !== "bet";

export const newId = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
