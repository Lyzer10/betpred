import { useEffect, useState } from "react";
import { Flag, TeamBadge } from "../badges";
import { odds, pct, timeLabel, useArchive, useArchives } from "../lib";
import { legLive, useEspnEvent, useLiveMatch } from "../live";
import { fixtureId, LEAGUES, localDay, scheduledOn } from "../matchData";
import type { ArchivedFixture, ExpectedLineup, Fixture, League, LeagueTableRow, MarketKey, MarketPrediction, Predictions, ScheduleData, ScheduledMatch } from "../types";
import { PREMIER_LEAGUE } from "../types";
import { Card, DateStrip, Empty, Legend, ProbBar, Segmented, VerdictBadge } from "../ui";
import { FormAndTable, HeadToHeadCard, Lineups, MatchStats } from "./Matches";

type MatchTab = "insights" | "form" | "stats" | "lineups" | "overview" | "h2h";   // "h2h": old links, shown as Stats
type LeagueTab = "matches" | "table" | "news";
type DisplayFixture = Fixture & { result?: ArchivedFixture["result"] };
type Group = "result" | "lead" | "double" | "goals";

const GROUPS: { id: Group; label: string; markets: MarketKey[] }[] = [
  { id: "result", label: "Result", markets: ["home_win", "draw", "away_win"] },
  { id: "lead", label: "1Up", markets: ["home_1up", "away_1up", "home_first", "away_first"] },
  { id: "double", label: "Double", markets: ["double_1x", "double_x2", "double_12"] },
  { id: "goals", label: "Goals", markets: ["over_0.5", "over_1.5", "over_2.5", "over_3.5", "under_2.5", "under_3.5", "btts_yes", "btts_no"] },
];

const named = (fixture: { home: string; away: string }, label: string) => label.replace("Home", fixture.home).replace("Away", fixture.away);

function fromArchive(item: ArchivedFixture, day: string): DisplayFixture {
  return { ...(item as Fixture), id: -1, day, top_scorelines: item.top_scorelines ?? [],
    has_market_odds: item.has_market_odds ?? item.markets.every((market) => market.market_probability != null),
    markets: item.markets.map((market) => ({ ...market,
      model_probability: (market as Partial<MarketPrediction>).model_probability ?? market.probability,
      fair_odds: (market as Partial<MarketPrediction>).fair_odds ?? 1 / market.probability,
      betpawa_odds: market.betpawa_odds ?? null })) };
}

function fromSchedule(match: ScheduledMatch): DisplayFixture {
  const day = localDay(match.kickoff_utc);
  return { id: -1, league: LEAGUES[match.league], date: day, time: timeLabel(match.kickoff_utc), kickoff_utc: match.kickoff_utc,
    home: match.home, away: match.away, day, expected_goals: [0, 0], top_scorelines: [], has_market_odds: false, markets: [] };
}

function mergeDay(day: string, predicted: Fixture[], schedule: ScheduledMatch[], archived: ArchivedFixture[] = []) {
  const fixtures = new Map<string, DisplayFixture>();
  for (const match of scheduledOn(schedule, day)) fixtures.set(fixtureId(match.home, match.away), fromSchedule(match));
  for (const match of predicted.filter((fixture) => fixture.day === day)) fixtures.set(fixtureId(match.home, match.away), match);
  for (const match of archived) fixtures.set(fixtureId(match.home, match.away), fromArchive(match, day));
  return [...fixtures.values()].sort((a, b) => a.kickoff_utc.localeCompare(b.kickoff_utc));
}

function MarketRow({ fixture, market }: { fixture: Fixture; market: MarketPrediction }) {
  const label = named(fixture, market.label);
  return <div className="border-t border-border/60 px-5 py-4 first:border-t-0"><div className="flex items-baseline justify-between gap-2"><b className="text-sm">{label}</b><b>{pct(market.probability)}</b></div>
    <div className="mt-2"><ProbBar probability={market.probability} market={market.market_probability} label={label} /></div>
    <div className="mt-3 flex items-center justify-between gap-2"><span className="text-xs text-ink-3">Fair <b className="text-ink-2">{odds(market.fair_odds)}</b>{market.betpawa_odds != null && <> · Betpawa <b className="text-ink">{odds(market.betpawa_odds)}</b></>}</span>{market.betpawa_odds != null && <VerdictBadge probability={market.probability} odds={market.betpawa_odds} />}</div></div>;
}

function BestPick({ fixture, compact = false }: { fixture: DisplayFixture; compact?: boolean }) {
  const live = useLiveMatch(fixture.home, fixture.away);
  const pick = fixture.best_pick;
  let state: "neutral" | "won" | "lost" | "later" = pick ? "neutral" : "later";
  if (pick && fixture.result) state = fixture.result.outcomes[pick.market] ? "won" : "lost";
  else if (pick) { const result = legLive(pick.market, live); if (result === "won" || result === "lost") state = result; }
  if (!pick) return <div data-best-pick-state="later" className="best-pick best-pick-later"><b>Later</b></div>;
  return <div data-best-pick-state={state} className={`best-pick best-pick-${state} ${compact ? "best-pick-compact" : ""}`}><b className="block truncate">{named(fixture, pick.label)}</b><span>{pct(pick.probability)} · {pick.odds_source === "estimated" ? "est. " : ""}{odds(pick.odds)}</span></div>;
}

/** Short code of a pick for the narrow column: O1.5, U3.5, H1UP, A1UP, 1X, X2, 12, 1, 2. */
const SHORT: Partial<Record<MarketKey, string>> = {
  "over_0.5": "O0.5", "over_1.5": "O1.5", "over_2.5": "O2.5", "over_3.5": "O3.5", "under_2.5": "U2.5", "under_3.5": "U3.5",
  home_1up: "H1UP", away_1up: "A1UP", home_win: "1", away_win: "2", draw: "X", double_1x: "1X", double_x2: "X2", double_12: "12",
};

/** The match's best pick in a slim column: code, %, Betpawa odds; solid green when won, solid red when lost.
 * Empty when the match has no pick (never a placeholder). */
function PickPill({ fixture }: { fixture: DisplayFixture }) {
  const live = useLiveMatch(fixture.home, fixture.away);
  const pick = fixture.best_pick;
  if (!pick) return <span className="w-[3.15rem] shrink-0" aria-hidden />;
  const settled = fixture.result ? (fixture.result.outcomes[pick.market] ? "won" : "lost") : legLive(pick.market, live);
  const state = settled === "won" || settled === "lost" ? settled : "open";
  // Same two lines and padding as the 1 / X / 2 boxes, so every box in the row has the same height.
  // Won: bold light blue (our highlight colour); lost: faint grey; not settled yet: neutral.
  const box = state === "won" ? "bg-model/25 ring-1 ring-accent/40" : state === "lost" ? "bg-surface-2 opacity-55" : "bg-surface-2";
  const top = state === "won" ? "text-accent" : "text-ink-3";
  const bottom = state === "won" ? "text-accent" : state === "lost" ? "text-ink-3 line-through decoration-1" : "text-ink";
  return (
    <span data-best-pick-state={state} title={named(fixture, pick.label)}
      className={`w-[3.15rem] shrink-0 rounded-lg py-1.5 text-center ${box}`}>
      <span className={`block whitespace-nowrap text-[10px] font-semibold leading-[15px] tracking-tight ${top}`}>{SHORT[pick.market] ?? pick.market} {pick.odds_source === "estimated" ? "~" : ""}{odds(pick.odds)}</span>
      <span className={`block text-xs font-bold ${bottom}`}>{state === "won" ? "✓ " : state === "lost" ? "✕ " : ""}{pct(pick.probability)}</span>
    </span>
  );
}

/** Home / draw / away chances as before: our likeliest outcome in blue, ✓ on what happened. */
function ResultBoxes({ fixture }: { fixture: DisplayFixture }) {
  const result = (["home_win", "draw", "away_win"] as MarketKey[]).map((key) => fixture.markets.find((m) => m.market === key));
  if (!result.every(Boolean)) return null;
  const best = result.indexOf(result.reduce((a, b) => (b!.probability > a!.probability ? b : a)));
  const outcomes = fixture.result?.outcomes;
  const actual = outcomes ? (outcomes.home_win ? 0 : outcomes.draw ? 1 : 2) : -1;
  return (
    <span className="ml-auto flex shrink-0 gap-1">
      {result.map((m, i) => (
        <span key={m!.market} className={`w-[2.2rem] rounded-lg py-1.5 text-center ${i === best ? "bg-model/12" : "bg-surface-2"}`}>
          <span className="block text-[10px] font-medium text-ink-3">{["1", "X", "2"][i]}{i === actual ? " ✓" : ""}</span>
          <span className={`block text-xs font-bold ${i === best ? "text-accent" : "text-ink-2"}`}>{pct(m!.probability)}</span>
        </span>
      ))}
    </span>
  );
}

/** Common short forms for the few names too long for a list row (full names on the match page). */
const LIST_NAMES: Record<string, string> = {
  "Manchester United": "Man Utd", "Manchester City": "Man City", "Crystal Palace": "Palace", "Bournemouth": "B'mouth",
  "Bayern Munich": "Bayern", "Nottingham Forest": "Forest", "Ein Frankfurt": "Frankfurt", "Wolverhampton": "Wolves",
};
const listName = (team: string) => LIST_NAMES[team] ?? team;

function MatchRow({ fixture, onOpen }: { fixture: DisplayFixture; onOpen: () => void }) {
  const live = useLiveMatch(fixture.home, fixture.away);
  const playing = !fixture.result && live && (live.state === "in" || live.state === "post") ? live : undefined;
  const score = fixture.result?.score ?? playing?.score;
  return <button data-match-row onClick={onOpen} className="flex w-full items-center gap-1 border-t border-border/60 px-2 py-3.5 text-left first:border-t-0 active:bg-surface-2/60">
    <span className="w-8 shrink-0 text-center text-[11px] font-semibold text-ink-3">{fixture.result ? "FT" : playing ? <span data-live-minute className={playing.state === "in" ? "text-good-ink" : ""}>{playing.state === "in" && <span className="live-dot mr-1" />}{playing.clock}</span> : timeLabel(fixture.kickoff_utc)}</span>
    {/* Names take only the width they need; the score sits right after them and the free space goes to the boxes. */}
    <span className="min-w-0 shrink space-y-2">{[fixture.home, fixture.away].map((team, index) => <span key={team} className="flex items-center gap-1"><TeamBadge team={team} size={18} /><span title={team} className={`min-w-0 truncate text-[13px] ${score && score[index] > score[1 - index] ? "font-bold" : "font-medium"}`}>{listName(team)}</span></span>)}</span>
    {score && <span className="shrink-0 space-y-2 pl-0.5 text-right">{score.map((goals, index) => <b key={index} data-score className={`block text-[13px] leading-5 ${playing?.state === "in" ? "text-good-ink" : ""}`}>{goals}</b>)}</span>}
    <ResultBoxes fixture={fixture} />
    <PickPill fixture={fixture} />
  </button>;
}

function LeagueGroups({ fixtures, onOpen, onLeague }: { fixtures: DisplayFixture[]; onOpen: (fixture: DisplayFixture) => void; onLeague: (code: string) => void }) {
  const groups = new Map<string, { league: League; fixtures: DisplayFixture[] }>();
  for (const fixture of fixtures) { const league = fixture.league ?? PREMIER_LEAGUE; const group = groups.get(league.code) ?? { league, fixtures: [] }; group.fixtures.push(fixture); groups.set(league.code, group); }
  return <div className="space-y-5">{[...groups.values()].map(({ league, fixtures: list }) => <section key={league.code}>
    <button onClick={() => onLeague(league.code)} className="mb-2 flex w-full items-center gap-3 px-1 text-left"><Flag country={league.country} width={30} /><span><b className="block text-sm">{league.name}</b><span className="text-[11px] text-ink-3">{league.country}</span></span><span className="ml-auto text-xs font-semibold text-accent">View league ›</span></button>
    <Card className="overflow-hidden">{list.map((fixture) => <MatchRow key={fixtureId(fixture.home, fixture.away)} fixture={fixture} onOpen={() => onOpen(fixture)} />)}</Card>
  </section>)}</div>;
}

function Insights({ fixture }: { fixture: DisplayFixture }) {
  const [group, setGroup] = useState<Group>("result");
  if (!fixture.markets.length) return <Empty>Predictions appear on the morning of the match day.</Empty>;
  const active = GROUPS.find((item) => item.id === group)!;
  return <div className="space-y-4"><BestPick fixture={fixture} /><Segmented options={GROUPS.map(({ id, label }) => ({ id, label }))} value={group} onChange={setGroup} /><div className="px-1"><Legend /></div><Card>{active.markets.map((key) => { const market = fixture.markets.find((item) => item.market === key); return market ? <MarketRow key={key} fixture={fixture} market={market} /> : null; })}</Card></div>;
}

function MatchPage({ fixture, tab, expected, onBack, onTab, onLeague }: { fixture: DisplayFixture; tab: MatchTab; expected: { home: ExpectedLineup; away: ExpectedLineup } | null; onBack: () => void; onTab: (tab: MatchTab) => void; onLeague: () => void }) {
  const started = Date.parse(fixture.kickoff_utc) <= Date.now();
  const tabs: { id: MatchTab; label: string }[] = [{ id: "insights", label: "Insights" }, { id: "form", label: "Form & table" },
    { id: "stats", label: "Stats" }, { id: "lineups", label: "Line-ups" }, ...(started ? [{ id: "overview" as MatchTab, label: "Overview" }] : [])];
  const shown: MatchTab = tab === "h2h" ? "stats" : tab === "overview" && !started ? "insights" : tab;
  return <div className="space-y-4"><button onClick={onBack} className="text-sm font-semibold text-accent">‹ Matches</button>
    <Card className="overflow-hidden"><div className="bg-hero px-5 pb-5 pt-4 text-hero-ink"><div className="text-center text-xs opacity-70">{new Date(fixture.kickoff_utc).toLocaleString(undefined, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}</div><div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-start gap-2"><TeamHero team={fixture.home} /><div className="pt-3 text-center">{fixture.markets.length ? <><b className="text-2xl">{fixture.expected_goals[0].toFixed(1)}–{fixture.expected_goals[1].toFixed(1)}</b><span className="block text-[11px] opacity-60">expected goals</span></> : <b className="text-sm">Prediction later</b>}</div><TeamHero team={fixture.away} /></div></div>{fixture.top_scorelines.length > 0 && <div className="flex items-center justify-between gap-2 px-4 py-3"><span className="text-xs text-ink-3">Likeliest scores</span><span className="flex gap-1.5">{fixture.top_scorelines.map((score) => <span key={score.score} className="rounded-lg bg-surface-2 px-2 py-1 text-xs font-bold">{score.score} <i className="not-italic text-ink-3">{pct(score.probability)}</i></span>)}</span></div>}</Card>
    <div role="tablist" aria-label="Match sections" className="no-scrollbar -mx-1 flex overflow-x-auto border-b border-border/70">{tabs.map((item) => <button key={item.id} role="tab" aria-selected={shown === item.id} onClick={() => onTab(item.id)} className={`shrink-0 border-b-2 px-3 py-2 text-xs font-semibold ${shown === item.id ? "border-accent text-accent" : "border-transparent text-ink-3"}`}>{item.label}</button>)}</div>
    {shown === "insights" && <Insights fixture={fixture} />}
    {shown === "form" && <FormAndTable fixture={fixture} onFullTable={onLeague} />}
    {shown === "stats" && <div className="space-y-4"><HeadToHeadCard fixture={fixture} /><MatchStats fixture={fixture} /></div>}
    {shown === "lineups" && <Lineups fixture={fixture} expected={expected} />}
    {shown === "overview" && <Overview fixture={fixture} />}
  </div>;
}

/** After kick-off: score, goals and cards with minutes (ESPN), and how our pick did. */
function Overview({ fixture }: { fixture: DisplayFixture }) {
  const event = useEspnEvent(fixture.home, fixture.away);
  const live = useLiveMatch(fixture.home, fixture.away);
  const [events, setEvents] = useState<{ minute: string; side: "home" | "away"; kind: string; player: string }[] | null>(null);
  useEffect(() => {
    if (!event) { setEvents([]); return; }
    fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${event.slug}/summary?event=${event.event_id}`)
      .then((r) => r.json())
      .then((summary) => {
        const sideOf: Record<string, "home" | "away"> = {};
        for (const c of summary.header?.competitions?.[0]?.competitors ?? []) sideOf[c.team?.id] = c.homeAway;
        const wanted = (k: any) => k.scoringPlay || /Card/.test(k.type?.text ?? "");
        setEvents((summary.keyEvents ?? []).filter(wanted).filter((k: any) => sideOf[k.team?.id]).map((k: any) => ({
          minute: k.clock?.displayValue ?? "",
          side: sideOf[k.team.id],
          kind: k.scoringPlay ? (/Own Goal/.test(k.type?.text ?? "") ? "Own goal" : /Penalty/.test(k.type?.text ?? "") ? "Penalty" : "Goal") : k.type.text,
          player: k.participants?.[0]?.athlete?.displayName ?? "",
        })));
      })
      .catch(() => setEvents([]));
  }, [event?.event_id, live?.clock]);
  const score = fixture.result?.score ?? live?.score;
  const pick = fixture.best_pick;
  const pickState = pick ? (fixture.result ? (fixture.result.outcomes[pick.market] ? "won" : "lost") : legLive(pick.market, live)) : null;
  const icon = (kind: string) => (kind === "Goal" || kind === "Penalty" ? "⚽" : kind === "Own goal" ? "⚽ OG" : /Red/.test(kind) ? "🟥" : "🟨");
  return (
    <div className="space-y-4" data-overview>
      <Card className="px-5 py-4 text-center">
        <div className="text-xs text-ink-3">{fixture.result || live?.state === "post" ? "Full time" : live?.state === "in" ? `Live · ${live.clock}` : "Kick-off"}</div>
        <div className="mt-1 text-3xl font-black tabular-nums">{score ? `${score[0]} – ${score[1]}` : "–"}</div>
        {pick && pickState && (
          <div className="mt-2 text-xs text-ink-2">
            Our pick <b>{named(fixture, pick.label)}</b> ({pct(pick.probability)}): {pickState === "won" ? "✓ won" : pickState === "lost" ? "✕ lost" : "in play"}
          </div>
        )}
      </Card>
      <Card className="overflow-hidden">
        <h2 className="px-4 pb-2 pt-4 text-[13px] font-semibold text-ink-2">Goals and cards</h2>
        {events === null ? <p className="px-4 pb-4 text-xs text-ink-3">Loading…</p> : !events.length ? <p className="px-4 pb-4 text-xs text-ink-3">No goals or cards yet.</p> : (
          <ul className="divide-y divide-border/60">
            {events.map((e, i) => (
              <li key={i} className={`flex items-center gap-2 px-4 py-2 text-xs ${e.side === "away" ? "flex-row-reverse text-right" : ""}`}>
                <span className="w-10 shrink-0 font-semibold text-ink-3">{e.minute}</span>
                <span className="shrink-0">{icon(e.kind)}</span>
                <span className="min-w-0 truncate font-medium">{e.player}</span>
              </li>
            ))}
          </ul>
        )}
        <p className="px-4 py-2 text-[10px] text-ink-3">Source: ESPN. Home team on the left, away team on the right.</p>
      </Card>
    </div>
  );
}

function TeamHero({ team }: { team: string }) { return <div className="flex min-w-0 flex-col items-center gap-2 text-center"><span className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-white p-1.5"><TeamBadge team={team} size={44} /></span><b className="text-sm leading-tight">{team}</b></div>; }

/** Full table; `highlight` (the two teams of the match it was opened from) get the light blue row. */
function LeagueTable({ rows, highlight = [] }: { rows: LeagueTableRow[]; highlight?: string[] }) {
  return <Card className="overflow-hidden"><div className="overflow-x-auto"><table className="w-full min-w-[343px] text-[11px]"><thead className="bg-surface-2 text-ink-3"><tr>{["#", "Team", "P", "W", "D", "L", "GD", "Pts"].map((label) => <th key={label} className={`px-1 py-2 ${label === "Team" ? "text-left" : "text-center"}`}>{label}</th>)}</tr></thead><tbody>{[...rows].sort((a,b) => a.position-b.position).map((row) => <tr key={row.team} data-highlight={highlight.includes(row.team) || undefined} className={`border-t border-border/60 ${highlight.includes(row.team) ? "bg-model/15" : ""}`}><td className="text-center">{row.position}</td><td className="py-2"><div className="flex items-center gap-1"><TeamBadge team={row.team} size={19} /><b className="max-w-[105px] truncate">{row.team}</b></div><div className="mt-1 flex gap-0.5">{row.form.map((result,index) => <span key={`${result}-${index}`} className={`h-3.5 w-3.5 rounded-sm text-center text-[8px] font-bold leading-[14px] ${result === "W" ? "bg-good/15 text-good-ink" : result === "L" ? "bg-critical/15 text-critical-ink" : "bg-surface-2 text-ink-2"}`}>{result}</span>)}</div></td>{[row.played,row.won,row.drawn,row.lost,`${row.gd>0?"+":""}${row.gd}`,row.points].map((value,index) => <td key={index} className={`px-0.5 text-center tabular-nums ${index===5?"font-bold":""}`}>{value}</td>)}</tr>)}</tbody></table></div></Card>;
}

function LeagueNews({ slug }: { slug: string }) {
  const [articles, setArticles] = useState<any[] | null>(null);
  useEffect(() => { let active = true; fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${slug}/news?limit=20`).then((response) => response.ok ? response.json() : Promise.reject()).then((json) => active && setArticles(json.articles ?? [])).catch(() => active && setArticles([])); return () => { active = false; }; }, [slug]);
  if (articles === null) return <Empty>Loading news…</Empty>; if (!articles.length) return <Empty>News unavailable</Empty>;
  return <div className="space-y-3">{articles.slice(0,12).map((article) => <a key={article.id ?? article.links?.web?.href} href={article.links?.web?.href} target="_blank" rel="noreferrer" className="glass-light flex gap-3 rounded-2xl p-3">{article.images?.[0]?.url && <img src={article.images[0].url} alt="" className="h-20 w-24 shrink-0 rounded-xl object-cover" />}<span className="min-w-0"><b className="line-clamp-3 text-sm leading-snug">{article.headline}</b><span className="mt-2 block text-[11px] text-ink-3">{new Date(article.published).toLocaleString()}</span></span></a>)}</div>;
}

function LeaguePage({ code, tab, data, schedule, highlight, onNavigate }: { code: string; tab: LeagueTab; data: Predictions; schedule: ScheduleData | null; highlight: string[]; onNavigate: (path: string) => void }) {
  const league = LEAGUES[code]; const past = data.archive.map((item) => item.date).slice(-7); const snapshots = useArchives(past);
  if (!league) return <Empty>League not found</Empty>;
  const previous = past.flatMap((date) => (snapshots[date]?.fixtures ?? []).filter((item) => (item.league?.code ?? "EPL") === code).map((item) => fromArchive(item,date)));
  const future = (schedule?.matches ?? []).filter((item) => item.league === code).map(fromSchedule);
  const unique = new Map<string, DisplayFixture>();
  for (const fixture of future) unique.set(`${fixture.day}|${fixtureId(fixture.home,fixture.away)}`, fixture);
  for (const fixture of data.fixtures.filter((item) => (item.league?.code ?? "EPL") === code)) unique.set(`${fixture.day}|${fixtureId(fixture.home,fixture.away)}`, fixture);
  for (const fixture of previous) unique.set(`${fixture.day}|${fixtureId(fixture.home,fixture.away)}`, fixture);
  const grouped = new Map<string, DisplayFixture[]>();
  for (const fixture of unique.values()) { const group = grouped.get(fixture.day) ?? []; group.push(fixture); grouped.set(fixture.day,group); }
  return <div className="space-y-4"><button onClick={() => history.back()} className="text-sm font-semibold text-accent">‹ Back</button><div className="flex items-center gap-3"><Flag country={league.country} width={40} /><div><h1 className="text-xl font-black">{league.name}</h1><p className="text-xs text-ink-3">{league.country}</p></div></div><Segmented options={[{id:"matches",label:"Matches"},{id:"table",label:"Table"},{id:"news",label:"News"}]} value={tab} onChange={(next) => onNavigate(`league/${code}/${next}`)} />
    {tab === "matches" && ([...grouped].length ? <div className="space-y-5">{[...grouped].sort(([a],[b]) => a.localeCompare(b)).map(([date,fixtures]) => <section key={date}><h2 className="mb-2 text-xs font-bold uppercase text-ink-3">{new Date(`${date}T12:00:00`).toLocaleDateString(undefined,{weekday:"long",day:"numeric",month:"long"})}</h2><Card className="overflow-hidden">{fixtures.map((fixture) => <MatchRow key={fixtureId(fixture.home,fixture.away)} fixture={fixture} onOpen={() => onNavigate(`matches/${date}/${encodeURIComponent(fixture.home)}/${encodeURIComponent(fixture.away)}`)} />)}</Card></section>)}</div> : <Empty>No matches</Empty>)}
    {tab === "table" && <LeagueTable rows={data.tables[code] ?? []} highlight={highlight} />}{tab === "news" && <LeagueNews slug={league.newsSlug} />}</div>;
}

export function MatchesRedesign({ data, schedule, dates, day, match, matchTab, leagueCode, leagueTab, highlight = [], markers, onNavigate }: { data: Predictions; schedule: ScheduleData | null; dates: string[]; day: string; match: { home: string; away: string } | null; matchTab: MatchTab; leagueCode: string | null; leagueTab: LeagueTab; highlight?: string[]; markers: Record<string,"won"|"lost"|"mixed"|"pending">; onNavigate: (path: string) => void }) {
  const snapshot = useArchive(day); const archived = data.archive.some((item) => item.date === day); const fixtures = mergeDay(day,data.fixtures,schedule?.matches ?? [],snapshot?.fixtures ?? []);
  if (leagueCode) return <LeaguePage code={leagueCode} tab={leagueTab} data={data} schedule={schedule} highlight={highlight} onNavigate={onNavigate} />;
  if (match) { const fixture = fixtures.find((item) => item.home===match.home && item.away===match.away); if (!fixture && archived && !snapshot) return <p className="text-center text-sm text-ink-3">Loading…</p>; if (!fixture) return <Empty>Match not found</Empty>; const expected = schedule?.expected_lineups[fixture.home] && schedule.expected_lineups[fixture.away] ? {home:schedule.expected_lineups[fixture.home],away:schedule.expected_lineups[fixture.away]} : null; const base=`matches/${day}/${encodeURIComponent(fixture.home)}/${encodeURIComponent(fixture.away)}`; return <MatchPage fixture={fixture} tab={matchTab} expected={expected} onBack={() => onNavigate(`matches/${day}`)} onTab={(tab) => onNavigate(`${base}/${tab}`)} onLeague={() => onNavigate(`league/${fixture.league?.code ?? "EPL"}/table/${encodeURIComponent(fixture.home)}/${encodeURIComponent(fixture.away)}`)} />; }
  return <div><div className="mb-4"><DateStrip dates={dates} selected={day} markers={markers} onSelect={(next) => onNavigate(`matches/${next}`)} /></div>{archived&&!snapshot ? <p className="text-center text-sm text-ink-3">Loading…</p> : fixtures.length ? <LeagueGroups fixtures={fixtures} onOpen={(fixture) => onNavigate(`matches/${day}/${encodeURIComponent(fixture.home)}/${encodeURIComponent(fixture.away)}`)} onLeague={(code) => onNavigate(`league/${code}/matches`)} /> : <Empty>No matches</Empty>}</div>;
}
