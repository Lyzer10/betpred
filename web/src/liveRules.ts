import type { MarketKey } from "./types";

export type MatchState = "pre" | "in" | "post" | "void";
export interface LiveMatch {
  state: MatchState;
  clock: string;
  score: [number, number];
  goals: ("home" | "away")[];
  /** Per goal: its half (from the minute shown, 45'+2' is the first half) and whether it came before 10:00. */
  goalTimes?: { side: "home" | "away"; firstHalf: boolean; first10: boolean }[];
  period?: number;      // 1 or 2 while playing
  elapsed?: number;     // seconds since kick-off
}
export type LegLive = "won" | "lost" | "live" | "pending" | "void";

export function parseEvent(event: any): LiveMatch {
  const competition = event.competitions[0];
  const status = event.status.type;
  const sideOf: Record<string, "home" | "away"> = {};
  const score: [number, number] = [0, 0];
  for (const c of competition.competitors) {
    sideOf[c.team.id] = c.homeAway;
    score[c.homeAway === "home" ? 0 : 1] = Number(c.score ?? 0);
  }
  const scoring = (competition.details ?? []).filter((d: any) => d.scoringPlay && sideOf[d.team?.id]);
  const goals = scoring.map((d: any) => sideOf[d.team.id]);
  const goalTimes = scoring.map((d: any) => ({
    side: sideOf[d.team.id],
    firstHalf: parseInt(String(d.clock?.displayValue ?? ""), 10) <= 45,
    first10: Number(d.clock?.value ?? Infinity) < 600,   // settlement: period 1, under 600 seconds
  }));
  const state: MatchState = /POSTPONED|CANCELED|ABANDONED|SUSPENDED|DELAYED/.test(status.name) ? "void" : status.state;
  const clock = state === "post" ? "FT" : status.name === "STATUS_HALFTIME" ? "HT" : state === "in" ? event.status.displayClock : "";
  return { state, clock, score, goals, goalTimes, period: Number(event.status.period ?? 0), elapsed: Number(event.status.clock ?? 0) };
}

function goalStates(goals: ("home" | "away")[]) {
  let h = 0, a = 0, homeLed = false, awayLed = false;
  for (const goal of goals) { if (goal === "home") h += 1; else a += 1; homeLed ||= h > a; awayLed ||= a > h; }
  return { homeLed, awayLed, first: goals[0] ?? null };
}

export function legLive(market: MarketKey | string, match: LiveMatch | undefined): LegLive {
  if (!match || match.state === "pre") return "pending";
  if (match.state === "void") return "void";
  const [h, a] = match.score;
  const total = h + a;
  const done = match.state === "post";
  const { homeLed, awayLed, first } = goalStates(match.goals);
  const early = (won: boolean, lost: boolean) => (won ? "won" : lost ? "lost" : done ? "lost" : "live");
  const atEnd = (ok: boolean) => (done ? (ok ? "won" : "lost") : "live");
  const line = Number(market.split("_")[1]);
  switch (market) {
    case "over_0.5": case "over_1.5": case "over_2.5": case "over_3.5": return early(total > line, false);
    case "under_2.5": case "under_3.5": return total > line ? "lost" : atEnd(true);
    case "home_1up": return early(homeLed, false);
    case "away_1up": return early(awayLed, false);
    case "home_first": return first ? (first === "home" ? "won" : "lost") : atEnd(false);
    case "away_first": return first ? (first === "away" ? "won" : "lost") : atEnd(false);
    case "btts_yes": return early(h > 0 && a > 0, false);
    case "btts_no": return h > 0 && a > 0 ? "lost" : atEnd(true);
    case "home_win": return atEnd(h > a);
    case "away_win": return atEnd(a > h);
    case "draw": return atEnd(h === a);
    case "double_1x": return atEnd(h >= a);
    case "double_x2": return atEnd(h <= a);
    case "double_12": return atEnd(h !== a);
    default: return trialLegLive(market, match, done);
  }
}

/** Trial bet types, matching engine research_leagues.settle_markets. */
function trialLegLive(market: string, match: LiveMatch, done: boolean): LegLive {
  const [h, a] = match.score;
  const times = match.goalTimes ?? [];
  const count = (side: "home" | "away" | null, first: boolean) =>
    times.filter((g) => g.firstHalf === first && (side === null || g.side === side)).length;
  const [hFH, aFH, hSH, aSH] = [count("home", true), count("away", true), count("home", false), count("away", false)];
  const halfOver = done || (match.period ?? 0) >= 2 || match.clock === "HT";
  const tenOver = halfOver || (match.elapsed ?? 0) >= 600;
  const { homeLed, awayLed, first } = goalStates(match.goals);
  const decided = (over: boolean, ok: boolean): LegLive => (over ? (ok ? "won" : "lost") : "live");
  const reached = (ok: boolean, over: boolean): LegLive => (ok ? "won" : over ? "lost" : "live");
  const side = market.startsWith("home_") ? "home" : market.startsWith("away_") ? "away" : null;
  const [own1, opp1, own2, opp2] = side === "away" ? [aFH, hFH, aSH, hSH] : [hFH, aFH, hSH, aSH];
  switch (market) {
    case "fh_over_0.5": case "fh_over_1.5": return reached(hFH + aFH > Number(market.slice(8)), halfOver);
    case "sh_over_0.5": case "sh_over_1.5": return reached(hSH + aSH > Number(market.slice(8)), done);
    case "home_fh_over_0.5": case "away_fh_over_0.5": return reached(own1 > 0, halfOver);
    case "home_sh_over_0.5": case "away_sh_over_0.5": return reached(own2 > 0, done);
    case "home_win_either_half": case "away_win_either_half":
      return halfOver && own1 > opp1 ? "won" : decided(done, own2 > opp2);
    case "home_win_both_halves": case "away_win_both_halves":
      return halfOver && !(own1 > opp1) ? "lost" : decided(done, own2 > opp2);
    case "home_score_both_halves": case "away_score_both_halves":
      return halfOver && own1 === 0 ? "lost" : reached(own1 > 0 && own2 > 0, done);
    case "dc1up_1x": return homeLed ? "won" : decided(done, h >= a);
    case "dc1up_x2": return awayLed ? "won" : decided(done, a >= h);
    case "dc1up_12": return homeLed || awayLed ? "won" : decided(done, h !== a);
    case "first_goal_home": return first ? (first === "home" ? "won" : "lost") : decided(done, false);
    case "first_goal_away": return first ? (first === "away" ? "won" : "lost") : decided(done, false);
    case "interval_10_home": case "interval_10_draw": case "interval_10_away": {
      const h10 = times.filter((g) => g.first10 && g.side === "home").length;
      const a10 = times.filter((g) => g.first10 && g.side === "away").length;
      const ok = market.endsWith("home") ? h10 > a10 : market.endsWith("away") ? a10 > h10 : h10 === a10;
      return decided(tenOver, ok);
    }
    default: return "pending";
  }
}

export const onTrack = (market: MarketKey | string, match: LiveMatch) => legLive(market, { ...match, state: "post" }) === "won";

export function slipLive(legs: LegLive[], need = legs.length): "won" | "lost" | "live" | "pending" {
  const won = legs.filter((state) => state === "won").length;
  const lost = legs.filter((state) => state === "lost").length;
  if (won >= need) return "won";
  if (legs.length - lost < need) return "lost";
  return legs.some((state) => state === "live" || state === "won" || state === "lost") ? "live" : "pending";
}
