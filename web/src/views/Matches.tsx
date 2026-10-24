import { useState } from "react";
import { Flag, TeamBadge } from "../badges";
import { kickoffLabel, odds, pct, timeLabel, useArchive } from "../lib";
import { type ArchiveDay, type ArchivedFixture, type Fixture, type League, type MarketKey, type MarketPrediction, PREMIER_LEAGUE } from "../types";
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
};

function MatchRow({ fixture, onOpen }: { fixture: ListFixture; onOpen?: () => void }) {
  const get = (k: MarketKey) => fixture.markets.find((m) => m.market === k);
  const result = [get("home_win"), get("draw"), get("away_win")];
  const known = result.every(Boolean);
  const best = known ? result.indexOf(result.reduce((a, b) => (b!.probability > a!.probability ? b : a))) : -1;
  const outcome = fixture.result?.outcomes;
  const actual = outcome ? (outcome.home_win ? 0 : outcome.draw ? 1 : 2) : -1;
  const body = (
    <>
      <div className="w-11 shrink-0 text-center">
        {fixture.result ? <div className="text-[11px] font-bold text-ink-3">FT</div>
          : <div className="text-[11px] font-medium text-ink-3">{timeLabel(fixture.kickoff_utc)}</div>}
      </div>
      <div className="min-w-0 flex-1 space-y-2">
        {[fixture.home, fixture.away].map((team, i) => (
          <div key={team} className="flex items-center gap-2.5">
            <TeamBadge team={team} size={22} />
            <span className={`flex-1 truncate text-sm ${fixture.result && fixture.result.score[i] > fixture.result.score[1 - i] ? "font-bold" : "font-medium"}`}>{team}</span>
            {fixture.result && <span className="w-5 text-right text-sm font-bold">{fixture.result.score[i]}</span>}
          </div>
        ))}
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
        <LeagueGroups fixtures={fixtures.filter((f) => f.day === day)} onOpen={(f) => onSelect(f.id ?? null)} />
      )}
      {day && !upcomingDays.includes(day) && <PastMatches key={day} date={day} />}
      {!day && <Empty>No matches scheduled yet.</Empty>}
    </div>
  );
}
