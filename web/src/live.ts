import { createContext, createElement, type ReactNode, useContext, useEffect, useRef, useState } from "react";
import { cachedJson } from "./lib";
import type { MarketKey } from "./types";

/** Live scores of the matches on the user's slips, straight from ESPN (display only: the official
 * result still settles overnight). Event ids come from data/lineups.json (`events`), written by the
 * daily run, so no team-name guessing happens on the phone. */

export interface EspnEvent { league: string; home: string; away: string; kickoff_utc: string; slug: string; espn_date: string; event_id: string }
export type MatchState = "pre" | "in" | "post" | "void";
export interface LiveMatch {
  state: MatchState;
  clock: string;                   // "63'", "HT", "FT"
  score: [number, number];
  goals: ("home" | "away")[];      // in order; own goals count for the team that benefits (as ESPN credits them)
}
export type LegLive = "won" | "lost" | "live" | "pending" | "void";

const ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer";
const POLL_MS = 45_000;
export const liveKey = (home: string, away: string) => `${home}|${away}`;

export function parseEvent(event: any): LiveMatch {
  const competition = event.competitions[0];
  const status = event.status.type;
  const sideOf: Record<string, "home" | "away"> = {};
  const score: [number, number] = [0, 0];
  for (const c of competition.competitors) {
    sideOf[c.team.id] = c.homeAway;
    score[c.homeAway === "home" ? 0 : 1] = Number(c.score ?? 0);
  }
  const goals = (competition.details ?? [])
    .filter((d: any) => d.scoringPlay && sideOf[d.team?.id])
    .map((d: any) => sideOf[d.team.id]);
  // Postponed, cancelled or abandoned matches never count as won or lost here.
  const state: MatchState = /POSTPONED|CANCELED|ABANDONED|SUSPENDED|DELAYED/.test(status.name) ? "void" : status.state;
  const clock = state === "post" ? "FT" : status.name === "STATUS_HALFTIME" ? "HT" : state === "in" ? event.status.displayClock : "";
  return { state, clock, score, goals };
}

/** Who led at any point, and who scored first, from the goal order. */
function goalStates(goals: ("home" | "away")[]) {
  let h = 0, a = 0, homeLed = false, awayLed = false;
  for (const g of goals) {
    if (g === "home") h += 1; else a += 1;
    homeLed ||= h > a;
    awayLed ||= a > h;
  }
  return { homeLed, awayLed, first: goals[0] ?? null };
}

/** A leg's live state, using the same definitions as the official settlement (engine add_actuals). */
export function legLive(market: MarketKey, m: LiveMatch | undefined): LegLive {
  if (!m || m.state === "pre") return "pending";
  if (m.state === "void") return "void";
  const [h, a] = m.score;
  const total = h + a;
  const done = m.state === "post";
  const { homeLed, awayLed, first } = goalStates(m.goals);
  // Decided as soon as it happens (can no longer change), or only at full time.
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

/** Whether a still-live leg would win if the match ended now (for the "on track" hint). */
export function onTrack(market: MarketKey, m: LiveMatch): boolean {
  return legLive(market, { ...m, state: "post" }) === "won";
}

/** Slip state from its legs; a Flexi bet needs only `need` legs. */
export function slipLive(legs: LegLive[], need = legs.length): "won" | "lost" | "live" | "pending" {
  const won = legs.filter((l) => l === "won").length;
  const lost = legs.filter((l) => l === "lost").length;
  if (won >= need) return "won";
  if (legs.length - lost < need) return "lost";
  return legs.some((l) => l === "live" || l === "won" || l === "lost") ? "live" : "pending";
}

/** Live scores of every published ESPN event (our five leagues, last 18 h to next 36 h); polls ESPN every
 * 45 s while one of them is about to start or playing, so matches under way keep their score even after
 * they leave the upcoming list. */
export function useLive() {
  const [events, setEvents] = useState<EspnEvent[]>([]);
  const [live, setLive] = useState<Record<string, LiveMatch>>({});
  const finished = useRef(new Set<string>());     // full time: never fetched again
  useEffect(() => {
    cachedJson("data/lineups.json").then((file) => setEvents(file?.events ?? []));
  }, []);
  const wanted = events;

  useEffect(() => {
    if (!wanted.length) return;
    let stopped = false;
    const poll = async () => {
      const now = Date.now();
      const due = wanted.filter((e) => Date.parse(e.kickoff_utc) - now < 15 * 60_000 && !finished.current.has(liveKey(e.home, e.away)));
      if (!due.length || document.visibilityState !== "visible") return;
      const groups = new Map<string, EspnEvent[]>();
      for (const e of due) groups.set(`${e.slug}|${e.espn_date}`, [...(groups.get(`${e.slug}|${e.espn_date}`) ?? []), e]);
      const update: Record<string, LiveMatch> = {};
      await Promise.all([...groups.entries()].map(async ([group, list]) => {
        const [slug, date] = group.split("|");
        try {
          const board = await (await fetch(`${ESPN}/${slug}/scoreboard?dates=${date}`)).json();
          for (const e of list) {
            const event = (board.events ?? []).find((x: any) => x.id === e.event_id);
            if (!event) continue;
            const match = parseEvent(event);
            update[liveKey(e.home, e.away)] = match;
            if (match.state === "post" || match.state === "void") finished.current.add(liveKey(e.home, e.away));
          }
        } catch { /* offline or ESPN down: keep the last known scores */ }
      }));
      if (!stopped && Object.keys(update).length) setLive((old) => ({ ...old, ...update }));
    };
    poll();
    const timer = window.setInterval(poll, POLL_MS);
    const wake = () => document.visibilityState === "visible" && poll();
    document.addEventListener("visibilitychange", wake);
    return () => { stopped = true; window.clearInterval(timer); document.removeEventListener("visibilitychange", wake); };
  }, [wanted]);
  return live;
}

/** ESPN event of one match (from data/lineups.json), or undefined until known. */
export function useEspnEvent(home: string, away: string): EspnEvent | undefined {
  const [events, setEvents] = useState<EspnEvent[]>([]);
  useEffect(() => {
    cachedJson("data/lineups.json").then((file) => setEvents(file?.events ?? []));
  }, []);
  return events.find((e) => e.home === home && e.away === away);
}

const LiveContext = createContext<Record<string, LiveMatch>>({});

/** One live feed for the whole app. */
export function LiveProvider({ children }: { children: ReactNode }) {
  return createElement(LiveContext.Provider, { value: useLive() }, children);
}

export const useLiveMatch = (home: string, away: string): LiveMatch | undefined => useContext(LiveContext)[liveKey(home, away)];
export const useLiveMap = () => useContext(LiveContext);
