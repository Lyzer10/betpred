import { createContext, createElement, type ReactNode, useContext, useEffect, useRef, useState } from "react";
import { cachedJson } from "./lib";
import type { MarketKey } from "./types";
import { legLive as applyLegLive, onTrack as applyOnTrack, parseEvent as parseEspnEvent, slipLive as applySlipLive, type LegLive, type LiveMatch } from "./liveRules";

/** Live scores of the matches on the user's slips, straight from ESPN (display only: the official
 * result still settles overnight). Event ids come from data/lineups.json (`events`), written by the
 * daily run, so no team-name guessing happens on the phone. */

export interface EspnEvent { league: string; home: string; away: string; kickoff_utc: string; slug: string; espn_date: string; event_id: string }
export type { LegLive, LiveMatch, MatchState } from "./liveRules";

const ESPN = "https://site.api.espn.com/apis/site/v2/sports/soccer";
const POLL_MS = 45_000;
export const liveKey = (home: string, away: string) => `${home}|${away}`;

export function parseEvent(event: any): LiveMatch {
  return parseEspnEvent(event);
}

/** A leg's live state, using the same definitions as the official settlement (engine add_actuals). */
export function legLive(market: MarketKey, m: LiveMatch | undefined): LegLive {
  return applyLegLive(market, m);
}

/** Whether a still-live leg would win if the match ended now (for the "on track" hint). */
export function onTrack(market: MarketKey, m: LiveMatch): boolean {
  return applyOnTrack(market, m);
}

/** Slip state from its legs; a Flexi bet needs only `need` legs. */
export function slipLive(legs: LegLive[], need = legs.length): "won" | "lost" | "live" | "pending" {
  return applySlipLive(legs, need);
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
