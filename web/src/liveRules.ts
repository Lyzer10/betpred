import type { MarketKey } from "./types";

export type MatchState = "pre" | "in" | "post" | "void";
export interface LiveMatch {
  state: MatchState;
  clock: string;
  score: [number, number];
  goals: ("home" | "away")[];
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
  const goals = (competition.details ?? []).filter((d: any) => d.scoringPlay && sideOf[d.team?.id]).map((d: any) => sideOf[d.team.id]);
  const state: MatchState = /POSTPONED|CANCELED|ABANDONED|SUSPENDED|DELAYED/.test(status.name) ? "void" : status.state;
  const clock = state === "post" ? "FT" : status.name === "STATUS_HALFTIME" ? "HT" : state === "in" ? event.status.displayClock : "";
  return { state, clock, score, goals };
}

function goalStates(goals: ("home" | "away")[]) {
  let h = 0, a = 0, homeLed = false, awayLed = false;
  for (const goal of goals) { if (goal === "home") h += 1; else a += 1; homeLed ||= h > a; awayLed ||= a > h; }
  return { homeLed, awayLed, first: goals[0] ?? null };
}

export function legLive(market: MarketKey, match: LiveMatch | undefined): LegLive {
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
    default: return "pending";
  }
}

export const onTrack = (market: MarketKey, match: LiveMatch) => legLive(market, { ...match, state: "post" }) === "won";

export function slipLive(legs: LegLive[], need = legs.length): "won" | "lost" | "live" | "pending" {
  const won = legs.filter((state) => state === "won").length;
  const lost = legs.filter((state) => state === "lost").length;
  if (won >= need) return "won";
  if (legs.length - lost < need) return "lost";
  return legs.some((state) => state === "live" || state === "won" || state === "lost") ? "live" : "pending";
}
