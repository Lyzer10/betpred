import { useEffect, useState } from "react";
import { Flag, TeamBadge } from "../badges";
import { kickoffLabel, odds, pct, timeLabel, useArchive, useLineups } from "../lib";
import { useEspnEvent, useLiveMatch } from "../live";
import { type ArchiveDay, type ArchivedFixture, type Fixture, type FormResult, type League, type LineupPlayer, type MarketKey, type MarketPrediction, type MatchContext, type TeamContext, PREMIER_LEAGUE } from "../types";
import { Card, DateStrip, Empty, Legend, ProbBar, Segmented, VerdictBadge, todayIso } from "../ui";

type Group = "result" | "lead" | "double" | "goals";

const GROUPS: { id: Group; label: string; markets: MarketKey[] }[] = [
  { id: "result", label: "Result", markets: ["home_win", "draw", "away_win"] },
  { id: "lead", label: "1Up", markets: ["home_1up", "away_1up", "home_first", "away_first"] },
  { id: "double", label: "Double", markets: ["double_1x", "double_x2", "double_12"] },
  { id: "goals", label: "Goals", markets: ["over_0.5", "over_1.5", "over_2.5", "over_3.5", "under_2.5", "under_3.5", "btts_yes", "btts_no"] },
];

const named = (fixture: { home: string; away: string }, label: string) =>
  label.replace("Home", fixture.home).replace("Away", fixture.away);

const ordinal = (position: number) => {
  const finalTwo = position % 100;
  if (finalTwo >= 11 && finalTwo <= 13) return `${position}th`;
  return `${position}${position % 10 === 1 ? "st" : position % 10 === 2 ? "nd" : position % 10 === 3 ? "rd" : "th"}`;
};

const FORM_STYLES: Record<FormResult, string> = {
  W: "bg-good/15 text-good-ink",
  D: "bg-surface-2 text-ink-2",
  L: "bg-critical/15 text-critical-ink",
};

function FormChips({ team, form }: { team: string; form: FormResult[] }) {
  return (
    <ol aria-label={`${team} recent form, oldest to latest`} className="flex gap-1">
      {form.map((result, index) => (
        <li key={`${index}-${result}`} className="flex flex-col items-center gap-0.5">
          <span data-form-result className={`inline-flex h-6 w-6 items-center justify-center rounded-md text-[11px] font-bold ${FORM_STYLES[result]}`}>
            {result}
          </span>
          <span aria-hidden className={`text-[8px] leading-none text-ink-3 ${index === form.length - 1 ? "" : "invisible"}`}>latest</span>
        </li>
      ))}
    </ol>
  );
}

function TeamContextRow({ team, context }: { team: string; context: TeamContext | null }) {
  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)] gap-3 px-4 py-3.5">
      <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-surface-2 p-1"><TeamBadge team={team} size={28} /></span>
      <div className="min-w-0">
        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
          <span className="min-w-0 truncate text-sm font-semibold">{team}</span>
          {context ? (
            <span className="text-[11px] text-ink-3">
              {ordinal(context.position)} · {context.points} pts · {context.played} played · GD {context.gd >= 0 ? "+" : ""}{context.gd}
            </span>
          ) : <span className="text-[11px] text-ink-3">Table data unavailable</span>}
        </div>
        <div className="mt-2 flex justify-end">
          {context?.form.length ? <FormChips team={team} form={context.form} /> : <span className="text-[11px] text-ink-3">No recent form</span>}
        </div>
      </div>
    </li>
  );
}

function FormAndTable({ fixture }: { fixture: Fixture }) {
  return (
    <Card className="overflow-hidden">
      <h2 className="px-4 pb-2 pt-4 text-[13px] font-semibold text-ink-2">Form &amp; table</h2>
      <ul className="divide-y divide-border/60">
        <TeamContextRow team={fixture.home} context={fixture.context?.home ?? null} />
        <TeamContextRow team={fixture.away} context={fixture.context?.away ?? null} />
      </ul>
    </Card>
  );
}

/** Last league meetings of the two teams (display only: head-to-head is not a model input). */
function HeadToHeadCard({ fixture }: { fixture: Fixture }) {
  const h2h = fixture.head_to_head;
  return (
    <Card className="overflow-hidden" data-h2h>
      <h2 className="px-4 pb-2 pt-4 text-[13px] font-semibold text-ink-2">Head-to-head</h2>
      {!h2h ? (
        <p className="px-4 pb-4 text-xs text-ink-3">No league meetings in our data (top-flight matches since 2014/15).</p>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-2 px-4 pb-2 text-center">
            {[[fixture.home, h2h.home_wins], ["Draws", h2h.draws], [fixture.away, h2h.away_wins]].map(([label, value]) => (
              <div key={String(label)} className="rounded-xl bg-surface-2 px-2 py-2">
                <div className="text-lg font-bold">{value}</div>
                <div className="truncate text-[11px] text-ink-3">{label}</div>
              </div>
            ))}
          </div>
          <p className="px-4 pb-2 text-[11px] text-ink-2">
            Last {h2h.meetings.length}: {h2h.avg_goals.toFixed(1)} goals a game · over 2.5 in {h2h.over_2_5} · both scored in {h2h.btts}
          </p>
          <ul className="divide-y divide-border/60 border-t border-border/60">
            {h2h.meetings.map((m) => (
              <li key={m.date} data-h2h-meeting className="flex items-center gap-2 px-4 py-2 text-xs">
                <span className="w-16 shrink-0 text-ink-3">{new Date(`${m.date}T12:00:00`).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "2-digit" })}</span>
                <span className={`min-w-0 flex-1 truncate text-right ${m.score[0] > m.score[1] ? "font-bold" : ""}`}>{m.home}</span>
                <span className="shrink-0 rounded-md bg-surface-2 px-1.5 font-bold tabular-nums">{m.score[0]}–{m.score[1]}</span>
                <span className={`min-w-0 flex-1 truncate ${m.score[1] > m.score[0] ? "font-bold" : ""}`}>{m.away}</span>
              </li>
            ))}
          </ul>
          <p className="px-4 py-2 text-[10px] text-ink-3">League matches since {h2h.since}. For reading only: our numbers do not use it.</p>
        </>
      )}
    </Card>
  );
}

const STATS: [string, string][] = [["possessionPct", "Possession %"], ["totalShots", "Shots"], ["shotsOnTarget", "On target"],
  ["wonCorners", "Corners"], ["saves", "Saves"], ["foulsCommitted", "Fouls"], ["yellowCards", "Yellow cards"], ["redCards", "Red cards"], ["offsides", "Offsides"]];

/** Team statistics from ESPN once the match has started (refreshed with the live feed). */
function MatchStats({ fixture }: { fixture: Fixture }) {
  const event = useEspnEvent(fixture.home, fixture.away);
  const live = useLiveMatch(fixture.home, fixture.away);
  const started = live && (live.state === "in" || live.state === "post");
  const [stats, setStats] = useState<Record<string, [string, string]> | null>(null);
  useEffect(() => {
    if (!event || !started) return;
    fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${event.slug}/summary?event=${event.event_id}`)
      .then((r) => r.json())
      .then((summary) => {
        const teams = summary.boxscore?.teams ?? [];
        const side = (h: string) => teams.find((t: any) => t.homeAway === h)?.statistics ?? [];
        const value = (list: any[], name: string) => list.find((x) => x.name === name)?.displayValue ?? "–";
        const home = side("home"), away = side("away");
        if (home.length && away.length) setStats(Object.fromEntries(STATS.map(([name]) => [name, [value(home, name), value(away, name)]])));
      })
      .catch(() => undefined);
  }, [event?.event_id, started, live?.clock]);
  if (!started || !stats) return null;
  return (
    <Card className="overflow-hidden" data-match-stats>
      <h2 className="px-4 pb-2 pt-4 text-[13px] font-semibold text-ink-2">Match stats</h2>
      <ul className="space-y-2.5 px-4 pb-4">
        {STATS.map(([name, label]) => {
          const [h, a] = stats[name].map((v) => Number(v));
          const share = h + a > 0 ? (h / (h + a)) * 100 : 50;
          return (
            <li key={name} className="text-xs">
              <div className="flex justify-between"><b className="tabular-nums">{stats[name][0]}</b><span className="text-ink-3">{label}</span><b className="tabular-nums">{stats[name][1]}</b></div>
              <div className="mt-1 flex h-1.5 overflow-hidden rounded-full bg-surface-2">
                <div className="bg-accent" style={{ width: `${share}%` }} /><div className="flex-1 bg-market/70" />
              </div>
            </li>
          );
        })}
      </ul>
      <p className="px-4 pb-3 text-[10px] text-ink-3">Source: ESPN. {live?.state === "in" ? "Updates during the match." : "Full time."}</p>
    </Card>
  );
}

/** Announced starting elevens (ESPN), shown once clubs publish them about an hour before kick-off. */
const POSITION_LINE: Record<string, number> = {
  G: 0, GK: 0,
  B: 1, CB: 1, CD: 1, "CD-L": 1, "CD-R": 1, LB: 1, RB: 1, LWB: 1, RWB: 1, SW: 1,
  M: 2, DM: 2, CM: 2, "CM-L": 2, "CM-R": 2, LM: 2, RM: 2,
  AM: 3, "AM-L": 3, "AM-R": 3,
  F: 4, CF: 4, ST: 4, LF: 4, RF: 4, LW: 4, RW: 4,
};

const positionLine = (position: string, lineCount: number) =>
  position === "CF-L" || position === "CF-R" ? (lineCount >= 4 ? 3 : 4) : POSITION_LINE[position];

/** Left to right across the pitch: wide left (LB, LM, ...) < inner left (CD-L, ...) < centre < inner right < wide right. */
const sideOrder = (position: string) => {
  if (/^(LB|LWB|LM|LW|LF)$/.test(position)) return 0;
  if (position.endsWith("-L")) return 1;
  if (position.endsWith("-R")) return 3;
  if (/^(RB|RWB|RM|RW|RF)$/.test(position)) return 4;
  return 2;
};

function pitchLines(formation: string | null, starters: LineupPlayer[]) {
  if (!formation || starters.length !== 11) return null;
  const counts = formation.split("-").map(Number);
  if (!counts.length || counts.some((count) => !Number.isInteger(count) || count < 1) || counts.reduce((a, b) => a + b, 0) !== 10) return null;
  const keepers = starters.filter((player) => positionLine(player.position ?? "", counts.length) === 0);
  const outfield = starters.filter((player) => positionLine(player.position ?? "", counts.length) !== 0);
  if (keepers.length !== 1 || outfield.some((player) => positionLine(player.position ?? "", counts.length) == null)) return null;
  outfield.sort((a, b) => positionLine(a.position!, counts.length) - positionLine(b.position!, counts.length)
    || sideOrder(a.position!) - sideOrder(b.position!)
    || (a.formation_place ?? 99) - (b.formation_place ?? 99));
  const lines: LineupPlayer[][] = [[keepers[0]]];
  let offset = 0;
  for (const count of counts) {
    const line = outfield.slice(offset, offset + count).sort((a, b) => sideOrder(a.position!) - sideOrder(b.position!)
      || (a.formation_place ?? 99) - (b.formation_place ?? 99));
    lines.push(line);
    offset += count;
  }
  return lines;
}

/** Family name with its particles ("Le Fée", "van Dijk", "De Bruyne"). */
const PARTICLES = new Set(["de", "da", "di", "do", "dos", "das", "del", "della", "van", "von", "der", "den", "le", "la", "ter", "ten", "el", "al", "bin", "ben"]);
const surname = (name: string) => {
  const parts = name.trim().split(/\s+/);
  let start = parts.length - 1;
  while (start > 1 && PARTICLES.has(parts[start - 1].toLowerCase())) start -= 1;
  const last = parts.slice(start).join(" ");
  return last.length > 12 ? `${last.slice(0, 11)}…` : last;
};

function Pitch({ formation, starters }: { formation: string; starters: LineupPlayer[] }) {
  const lines = pitchLines(formation, starters)!;
  const yFor = (index: number) => 119 - index * (106 / (lines.length - 1));
  return (
    <svg viewBox="0 0 100 132" className="block w-full" role="img" aria-label={`Starting eleven in a ${formation} formation`} data-pitch>
      <rect width="100" height="132" rx="3" fill="var(--pitch)" />
      <g fill="none" stroke="var(--pitch-line)" strokeWidth="0.7">
        <rect x="2" y="2" width="96" height="128" rx="2" />
        <path d="M2 66h96" /><circle cx="50" cy="66" r="12" />
        <path d="M29 2v17h42V2M39 2v8h22V2M29 130v-17h42v17M39 130v-8h22v8" />
      </g>
      {lines.flatMap((line, lineIndex) => line.map((player, playerIndex) => {
        const x = 100 * (playerIndex + 1) / (line.length + 1);
        const y = yFor(lineIndex);
        return (
          <g key={`${player.number}-${player.name}`} data-player-marker data-position={player.position} transform={`translate(${x} ${y})`}>
            <circle r="4.4" fill={lineIndex === 0 ? "var(--keeper)" : "var(--player)"} stroke="var(--player-ring)" strokeWidth="0.7" />
            <text y="1.35" textAnchor="middle" fill="var(--player-ink)" fontSize="3.6" fontWeight="700">{player.number ?? ""}</text>
            <text y="8.1" textAnchor="middle" fill="var(--pitch-ink)" stroke="var(--pitch-label-shadow)" strokeWidth="1.2" paintOrder="stroke" fontSize="3.5" fontWeight="650">{surname(player.name)}</text>
          </g>
        );
      }))}
    </svg>
  );
}

function StarterList({ starters }: { starters: LineupPlayer[] }) {
  return (
    <ol className="divide-y divide-border/60" data-lineup-fallback>
      {starters.map((p) => (
        <li key={`${p.number}-${p.name}`} data-starter className="flex items-center gap-3 px-4 py-2 text-sm">
          <span className="w-6 text-right text-xs font-semibold text-ink-3">{p.number ?? ""}</span>
          <span className="min-w-0 flex-1 truncate font-medium">{p.name}</span>
          <span className="text-[11px] text-ink-3">{p.position ?? ""}</span>
        </li>
      ))}
    </ol>
  );
}

function Lineups({ fixture }: { fixture: Fixture }) {
  const lineup = useLineups().find((l) => l.home === fixture.home && l.away === fixture.away);
  const [side, setSide] = useState<"home" | "away">("home");
  const team = lineup?.[side === "home" ? "home_lineup" : "away_lineup"];
  const lines = team ? pitchLines(team.formation, team.starters) : null;
  return (
    <Card className="overflow-hidden" data-lineups>
      <h2 className="px-4 pb-2 pt-4 text-[13px] font-semibold text-ink-2">Line-ups</h2>
      {!lineup || !team ? (
        <p className="px-4 pb-4 text-xs text-ink-3">Line-ups appear here about an hour before kick-off, once the clubs announce them.</p>
      ) : (
        <>
          <div className="px-4 pb-2">
            <Segmented options={[{ id: "home", label: fixture.home }, { id: "away", label: fixture.away }]} value={side} onChange={setSide} />
          </div>
          {team.formation && <div className="px-4 pb-2 text-center text-xs font-semibold text-ink-2">Formation {team.formation}</div>}
          {lines && team.formation ? (
            <div className="lineup-pitch mx-3 overflow-hidden rounded-xl" data-starter-count={team.starters.length}>
              <Pitch formation={team.formation} starters={team.starters} />
            </div>
          ) : <StarterList starters={team.starters} />}
          {team.subs.length > 0 && (
            <div className="px-4 py-3 text-[11px] leading-relaxed text-ink-3">
              <span className="font-semibold text-ink-2">Bench</span>
              <ul className="mt-1 flex flex-wrap gap-x-2 gap-y-1">
                {team.subs.map((p) => <li key={`${p.number}-${p.name}`}>{p.number ? `${p.number} ` : ""}{p.name}</li>)}
              </ul>
            </div>
          )}
        </>
      )}
    </Card>
  );
}

function MarketRow({ fixture, market }: { fixture: Fixture; market: MarketPrediction }) {
  const label = named(fixture, market.label);
  return (
    <div className="border-t border-border/60 px-5 py-4 first:border-t-0">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm font-semibold">{label}</span>
        <span className="text-base font-bold">{pct(market.probability)}</span>
      </div>
      <div className="mt-2"><ProbBar probability={market.probability} market={market.market_probability} label={label} /></div>
      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="text-xs text-ink-3">
          Fair <b className="text-ink-2">{odds(market.fair_odds)}</b>
          {market.betpawa_odds != null && <> · Betpawa <b className="text-ink">{odds(market.betpawa_odds)}</b></>}
        </span>
        {market.betpawa_odds != null && <VerdictBadge probability={market.probability} odds={market.betpawa_odds} />}
      </div>
    </div>
  );
}

function MatchDetail({ fixture, onBack }: { fixture: Fixture; onBack: () => void }) {
  const [group, setGroup] = useState<Group>("result");
  const active = GROUPS.find((g) => g.id === group)!;
  return (
    <div className="space-y-4">
      <button onClick={onBack} className="px-1 text-sm font-semibold text-accent">‹ Matches</button>
      <Card className="overflow-hidden">
        <div className="bg-hero px-5 pb-5 pt-4 text-hero-ink">
          <div className="text-center text-xs opacity-70">{kickoffLabel(fixture.kickoff_utc)}</div>
          <div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-start gap-2">
            <div className="flex flex-col items-center gap-2 text-center">
              <span className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-white p-1.5"><TeamBadge team={fixture.home} size={44} /></span>
              <span className="text-sm font-semibold leading-tight">{fixture.home}</span>
            </div>
            <div className="pt-2 text-center">
              <div className="text-2xl font-extrabold tracking-tight">{fixture.expected_goals[0].toFixed(1)}<span className="mx-1 opacity-50">–</span>{fixture.expected_goals[1].toFixed(1)}</div>
              <div className="text-[11px] opacity-60">expected goals</div>
            </div>
            <div className="flex flex-col items-center gap-2 text-center">
              <span className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-white p-1.5"><TeamBadge team={fixture.away} size={44} /></span>
              <span className="text-sm font-semibold leading-tight">{fixture.away}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between px-5 py-3">
          <span className="text-xs text-ink-3">Likeliest scores</span>
          <div className="flex gap-2">
            {fixture.top_scorelines.map((s) => (
              <span key={s.score} className="rounded-lg bg-surface-2 px-2.5 py-1 text-xs font-bold">
                {s.score} <span className="font-medium text-ink-3">{pct(s.probability)}</span>
              </span>
            ))}
          </div>
        </div>
      </Card>

      <FormAndTable fixture={fixture} />
      <HeadToHeadCard fixture={fixture} />
      <MatchStats fixture={fixture} />
      <Lineups fixture={fixture} />

      <Segmented options={GROUPS.map((g) => ({ id: g.id, label: g.label }))} value={group} onChange={setGroup} />
      <div className="px-1"><Legend /></div>
      {!fixture.has_market_odds && (
        <p className="px-1 text-xs text-warning-ink">⚠ No bookmaker odds yet: model-only probabilities.</p>
      )}
      <Card>
        {active.markets.map((key) => {
          const market = fixture.markets.find((m) => m.market === key);
          return market ? <MarketRow key={key} fixture={fixture} market={market} /> : null;
        })}
      </Card>
      <p className="px-2 text-xs leading-relaxed text-ink-3">
        Betpawa's prices are checked for you. <b className="text-good-ink">✓ Bet this</b> means Betpawa pays at least 3%
        more than the fair price. Blue bar: our chance. Orange mark: what other bookmakers think.
      </p>
    </div>
  );
}

type ListFixture = Pick<Fixture, "home" | "away" | "kickoff_utc" | "league"> & {
  markets: { market: MarketKey; probability: number }[];
  result?: ArchivedFixture["result"];
  id?: number;
  context?: MatchContext;
};

function MatchRow({ fixture, onOpen }: { fixture: ListFixture; onOpen?: () => void }) {
  const get = (k: MarketKey) => fixture.markets.find((m) => m.market === k);
  const result = [get("home_win"), get("draw"), get("away_win")];
  const known = result.every(Boolean);
  const best = known ? result.indexOf(result.reduce((a, b) => (b!.probability > a!.probability ? b : a))) : -1;
  const outcome = fixture.result?.outcomes;
  const actual = outcome ? (outcome.home_win ? 0 : outcome.draw ? 1 : 2) : -1;
  // Live score until the official result is in (display only).
  const live = useLiveMatch(fixture.home, fixture.away);
  const playing = !fixture.result && live && (live.state === "in" || live.state === "post") ? live : undefined;
  const score = fixture.result?.score ?? playing?.score;
  const body = (
    <>
      <div className="w-11 shrink-0 text-center">
        {fixture.result ? <div className="text-[11px] font-bold text-ink-3">FT</div>
          : playing ? <div data-live-minute className={`text-[11px] font-bold ${playing.state === "in" ? "text-good-ink" : "text-ink-3"}`}>
              {playing.state === "in" && <span aria-hidden className="live-dot mr-1" />}{playing.clock}</div>
          : <div className="text-[11px] font-medium text-ink-3">{timeLabel(fixture.kickoff_utc)}</div>}
      </div>
      <div className="min-w-0 flex-1 space-y-2">
        {[fixture.home, fixture.away].map((team, i) => {
          const context = i === 0 ? fixture.context?.home : fixture.context?.away;
          return (
            <div key={team} className="flex items-center gap-2.5">
              <TeamBadge team={team} size={22} />
              <div className="flex min-w-0 flex-1 items-baseline gap-1.5">
                <span className={`min-w-0 truncate text-sm ${score && score[i] > score[1 - i] ? "font-bold" : "font-medium"}`}>{team}</span>
                {context && !score && <span className="shrink-0 text-[10px] text-ink-3">{ordinal(context.position)}</span>}
              </div>
              {score && <span data-score className={`w-5 text-right text-sm font-bold ${playing?.state === "in" ? "text-good-ink" : ""}`}>{score[i]}</span>}
            </div>
          );
        })}
      </div>
      {known && (
        <div className="flex gap-1">
          {result.map((m, i) => (
            <div key={m!.market} className={`w-10 rounded-lg py-1.5 text-center ${i === best ? "bg-model/12" : "bg-surface-2"}`}>
              <div className="text-[10px] font-medium text-ink-3">{["1", "X", "2"][i]}{i === actual ? " ✓" : ""}</div>
              <div className={`text-xs font-bold ${i === best ? "text-accent" : "text-ink-2"}`}>{pct(m!.probability)}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
  return onOpen ? (
    <button onClick={onOpen} className="flex w-full items-center gap-2 border-t border-border/60 px-3 py-3.5 text-left first:border-t-0 active:bg-surface-2/60">{body}</button>
  ) : (
    <div className="flex w-full items-center gap-2 border-t border-border/60 px-3 py-3.5 first:border-t-0">{body}</div>
  );
}

function LeagueGroups({ fixtures, onOpen }: { fixtures: ListFixture[]; onOpen?: (f: ListFixture) => void }) {
  const leagues = new Map<string, { league: League; list: ListFixture[] }>();
  for (const f of [...fixtures].sort((a, b) => a.kickoff_utc.localeCompare(b.kickoff_utc))) {
    const league = f.league ?? PREMIER_LEAGUE;
    const group = leagues.get(league.code) ?? { league, list: [] };
    group.list.push(f);
    leagues.set(league.code, group);
  }
  return (
    <div className="space-y-5">
      {[...leagues.values()].map(({ league, list }) => (
        <section key={league.code}>
          <div className="mb-2 flex items-center gap-3 px-1">
            <Flag country={league.country} width={30} />
            <div>
              <div className="text-sm font-bold leading-tight">{league.name}</div>
              <div className="text-[11px] text-ink-3">{league.country}</div>
            </div>
            <span className="ml-auto text-[11px] text-ink-3">{list.length} {list.length === 1 ? "match" : "matches"}</span>
          </div>
          <Card className="overflow-hidden">
            {list.map((f) => <MatchRow key={`${f.home}-${f.away}`} fixture={f} onOpen={onOpen ? () => onOpen(f) : undefined} />)}
          </Card>
        </section>
      ))}
    </div>
  );
}

/** A day with matches still to come; its matches already under way stay listed (from the archive). */
function UpcomingMatches({ day, fixtures, onOpen }: { day: string; fixtures: Fixture[]; onOpen: (f: ListFixture) => void }) {
  const archived = useArchive(day);
  const upcoming = fixtures.filter((f) => f.day === day);
  const started = (archived?.fixtures ?? []).filter((a) => !upcoming.some((f) => f.home === a.home && f.away === a.away));
  return <LeagueGroups fixtures={[...started, ...upcoming]} onOpen={(f) => f.id != null && onOpen(f)} />;
}

function PastMatches({ date }: { date: string }) {
  const snapshot = useArchive(date);
  if (!snapshot) return <p className="mt-6 text-center text-sm text-ink-3">Loading…</p>;
  return snapshot.fixtures.length ? <LeagueGroups fixtures={snapshot.fixtures} /> : <Empty>No matches this day.</Empty>;
}

export function Matches({ fixtures, archive, selected, onSelect }: {
  fixtures: Fixture[]; archive: ArchiveDay[]; selected: number | null; onSelect: (id: number | null) => void;
}) {
  const today = todayIso();
  const upcomingDays = [...new Set(fixtures.map((f) => f.day))];
  const pastDays = archive.map((a) => a.date).filter((d) => d <= today && !upcomingDays.includes(d));
  const dates = [...new Set([...pastDays, ...upcomingDays])].sort();
  const [day, setDay] = useState<string | undefined>(dates.includes(today) ? today : upcomingDays[0] ?? dates[dates.length - 1]);
  const fixture = fixtures.find((f) => f.id === selected);
  if (fixture) return <MatchDetail fixture={fixture} onBack={() => onSelect(null)} />;
  return (
    <div>
      <div className="mb-4"><DateStrip dates={dates} selected={day} onSelect={setDay} /></div>
      {day && upcomingDays.includes(day) && (
        <UpcomingMatches key={day} day={day} fixtures={fixtures} onOpen={(f) => onSelect(f.id ?? null)} />
      )}
      {day && !upcomingDays.includes(day) && <PastMatches key={day} date={day} />}
      {!day && <Empty>No matches scheduled yet.</Empty>}
    </div>
  );
}
