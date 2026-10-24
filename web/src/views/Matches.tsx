import { useState } from "react";
import { dayLabel, fixtureKey, kickoffLabel, odds, pct, shortName, timeLabel } from "../lib";
import type { Fixture, MarketKey, MarketPrediction, SavedPick } from "../types";
import { Card, Crest, Legend, OddsInput, ProbBar, SectionTitle, Segmented, VerdictBadge, parseOdds } from "../ui";

type Group = "result" | "lead" | "goals";

const GROUPS: { id: Group; label: string; markets: MarketKey[] }[] = [
  { id: "result", label: "Result", markets: ["home_win", "draw", "away_win"] },
  { id: "lead", label: "1Up & first goal", markets: ["home_1up", "away_1up", "home_first", "away_first"] },
  { id: "goals", label: "Goals", markets: ["over_0.5", "over_1.5", "over_2.5", "over_3.5", "under_2.5", "under_3.5", "btts_yes", "btts_no"] },
];

const named = (fixture: { home: string; away: string }, label: string) =>
  label.replace("Home", fixture.home).replace("Away", fixture.away);

function MarketRow({ fixture, market, onSave }: { fixture: Fixture; market: MarketPrediction; onSave: (pick: SavedPick) => void }) {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState(false);
  const entered = parseOdds(text);
  const label = named(fixture, market.label);
  return (
    <div className="border-t border-border/60 px-5 py-4 first:border-t-0">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm font-semibold">{label}</span>
        <span className="text-base font-bold">{pct(market.probability)}</span>
      </div>
      <div className="mt-2"><ProbBar probability={market.probability} market={market.market_probability} label={label} /></div>
      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="text-xs text-ink-3">Fair odds <b className="text-ink-2">{odds(market.fair_odds)}</b></span>
        <div className="flex items-center gap-2">
          {entered && <VerdictBadge probability={market.probability} odds={entered} />}
          <OddsInput label={`Your odds for ${label}`} placeholder="Odds" value={text} onChange={(v) => { setText(v); setSaved(false); }} />
        </div>
      </div>
      {entered && (
        <button
          className="mt-3 w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white transition disabled:bg-surface-2 disabled:text-ink-3"
          disabled={saved}
          onClick={() => {
            onSave({
              id: `${fixture.id}-${market.market}-${Date.now()}`,
              fixtureKey: fixtureKey(fixture.date, fixture.home, fixture.away),
              date: fixture.date, home: fixture.home, away: fixture.away,
              market: market.market, label, probability: market.probability, odds: entered, stake: 1,
              savedAt: new Date().toISOString(),
            });
            setSaved(true);
          }}
        >{saved ? "✓ Saved to My picks" : "Save to My picks"}</button>
      )}
    </div>
  );
}

function MatchDetail({ fixture, onBack, onSave }: { fixture: Fixture; onBack: () => void; onSave: (pick: SavedPick) => void }) {
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
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-white/10 text-xs font-bold">{shortName(fixture.home)}</span>
              <span className="text-sm font-semibold leading-tight">{fixture.home}</span>
            </div>
            <div className="pt-2 text-center">
              <div className="text-2xl font-extrabold tracking-tight">{fixture.expected_goals[0].toFixed(1)}<span className="mx-1 opacity-50">–</span>{fixture.expected_goals[1].toFixed(1)}</div>
              <div className="text-[11px] opacity-60">expected goals</div>
            </div>
            <div className="flex flex-col items-center gap-2 text-center">
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-white/10 text-xs font-bold">{shortName(fixture.away)}</span>
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
          return market ? <MarketRow key={key} fixture={fixture} market={market} onSave={onSave} /> : null;
        })}
      </Card>
      <p className="px-2 text-xs leading-relaxed text-ink-3">
        Type your bookmaker's odds next to a market. <b className="text-good-ink">✓ Value bet</b> means they pay at
        least 3% more than our probability says is fair.
      </p>
    </div>
  );
}

function MatchRow({ fixture, onOpen }: { fixture: Fixture; onOpen: () => void }) {
  const get = (k: MarketKey) => fixture.markets.find((m) => m.market === k)!;
  const result = [get("home_win"), get("draw"), get("away_win")];
  const best = result.indexOf(result.reduce((a, b) => (b.probability > a.probability ? b : a)));
  return (
    <button onClick={onOpen} className="flex w-full items-center gap-3 border-t border-border/60 px-4 py-3.5 text-left first:border-t-0 active:bg-surface-2/60">
      <div className="min-w-0 flex-1 space-y-1.5">
        <div className="text-[11px] font-medium text-ink-3">{timeLabel(fixture.kickoff_utc)}</div>
        <div className="flex items-center gap-2"><Crest team={fixture.home} size="sm" /><span className="truncate text-sm font-semibold">{fixture.home}</span></div>
        <div className="flex items-center gap-2"><Crest team={fixture.away} size="sm" /><span className="truncate text-sm font-semibold">{fixture.away}</span></div>
      </div>
      <div className="flex gap-1">
        {result.map((m, i) => (
          <div key={m.market} className={`w-10 rounded-lg py-1.5 text-center ${i === best ? "bg-model/12" : "bg-surface-2"}`}>
            <div className="text-[10px] font-medium text-ink-3">{["1", "X", "2"][i]}</div>
            <div className={`text-xs font-bold ${i === best ? "text-accent" : "text-ink-2"}`}>{pct(m.probability)}</div>
          </div>
        ))}
      </div>
    </button>
  );
}

export function Matches({ fixtures, selected, onSelect, onSave }: {
  fixtures: Fixture[]; selected: number | null; onSelect: (id: number | null) => void; onSave: (pick: SavedPick) => void;
}) {
  const fixture = fixtures.find((f) => f.id === selected);
  if (fixture) return <MatchDetail fixture={fixture} onBack={() => onSelect(null)} onSave={onSave} />;
  const days = new Map<string, Fixture[]>();
  for (const f of fixtures) {
    const day = dayLabel(f.kickoff_utc);
    days.set(day, [...(days.get(day) ?? []), f]);
  }
  return (
    <div>
      {[...days].map(([day, list]) => (
        <div key={day}>
          <SectionTitle aside={`${list.length} ${list.length === 1 ? "match" : "matches"}`}>{day}</SectionTitle>
          <Card className="overflow-hidden">
            {list.map((f) => <MatchRow key={f.id} fixture={f} onOpen={() => onSelect(f.id)} />)}
          </Card>
        </div>
      ))}
    </div>
  );
}
