import { useState } from "react";
import { fixtureKey, kickoffLabel, odds, pct } from "../lib";
import type { Fixture, MarketKey, MarketPrediction, SavedPick } from "../types";
import { Card, Legend, OddsInput, ProbBar, VerdictBadge, parseOdds } from "../ui";

const GROUPS: { title: string; markets: MarketKey[] }[] = [
  { title: "Result", markets: ["home_win", "draw", "away_win"] },
  { title: "1Up & first goal", markets: ["home_1up", "away_1up", "home_first", "away_first"] },
  { title: "Goals", markets: ["over_0.5", "over_1.5", "over_2.5", "over_3.5", "under_2.5", "under_3.5", "btts_yes", "btts_no"] },
];

function marketLabel(fixture: Fixture, m: MarketPrediction) {
  return m.label.replace("Home", fixture.home).replace("Away", fixture.away);
}

function MarketRow({ fixture, market, onSave }: { fixture: Fixture; market: MarketPrediction; onSave: (pick: SavedPick) => void }) {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState(false);
  const entered = parseOdds(text);
  const label = marketLabel(fixture, market);
  return (
    <div className="py-3">
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-sm font-bold">{pct(market.probability)}</span>
      </div>
      <ProbBar probability={market.probability} market={market.market_probability} label={label} />
      <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs text-ink-3">Fair odds {odds(market.fair_odds)}</span>
        <div className="flex items-center gap-2">
          {entered && <VerdictBadge probability={market.probability} odds={entered} />}
          <OddsInput label={`Your odds for ${label}`} placeholder="Odds" value={text} onChange={(v) => { setText(v); setSaved(false); }} />
          {entered && (
            <button
              className="rounded-lg bg-accent px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50"
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
            >{saved ? "Saved" : "Save"}</button>
          )}
        </div>
      </div>
    </div>
  );
}

function MatchDetail({ fixture, onBack, onSave }: { fixture: Fixture; onBack: () => void; onSave: (pick: SavedPick) => void }) {
  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-sm font-semibold text-accent">‹ All matches</button>
      <Card className="overflow-hidden">
        <div className="bg-hero px-4 py-5 text-center text-hero-ink">
          <div className="text-xs opacity-75">{kickoffLabel(fixture.kickoff_utc)}</div>
          <div className="mt-2 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
            <div className="text-right text-lg font-bold leading-tight">{fixture.home}</div>
            <div className="rounded-lg bg-white/10 px-3 py-1 text-sm font-semibold">
              {fixture.expected_goals[0].toFixed(1)} – {fixture.expected_goals[1].toFixed(1)}
            </div>
            <div className="text-left text-lg font-bold leading-tight">{fixture.away}</div>
          </div>
          <div className="mt-2 text-xs opacity-75">Expected goals</div>
        </div>
        <div className="flex justify-center gap-2 px-4 py-3">
          {fixture.top_scorelines.map((s) => (
            <div key={s.score} className="rounded-lg bg-surface-2 px-3 py-1.5 text-center">
              <div className="text-sm font-bold">{s.score}</div>
              <div className="text-[11px] text-ink-3">{pct(s.probability)}</div>
            </div>
          ))}
        </div>
      </Card>
      <div className="px-1"><Legend /></div>
      {!fixture.has_market_odds && (
        <Card className="p-3 text-xs text-warning-ink">⚠ No bookmaker odds yet: these are model-only probabilities.</Card>
      )}
      {GROUPS.map((group) => (
        <Card key={group.title} className="px-4 pt-3">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-3">{group.title}</h3>
          <div className="divide-y divide-border">
            {group.markets.map((key) => {
              const market = fixture.markets.find((m) => m.market === key);
              return market ? <MarketRow key={key} fixture={fixture} market={market} onSave={onSave} /> : null;
            })}
          </div>
        </Card>
      ))}
      <p className="px-1 text-xs leading-relaxed text-ink-3">
        Type your bookmaker's odds next to any market. <b>Value bet</b> means the odds pay more than our
        probability says they should (at least 3% expected return).
      </p>
    </div>
  );
}

export function Matches({ fixtures, selected, onSelect, onSave }: {
  fixtures: Fixture[]; selected: number | null; onSelect: (id: number | null) => void; onSave: (pick: SavedPick) => void;
}) {
  const fixture = fixtures.find((f) => f.id === selected);
  if (fixture) return <MatchDetail fixture={fixture} onBack={() => onSelect(null)} onSave={onSave} />;
  return (
    <div className="space-y-3">
      {fixtures.map((f) => {
        const get = (k: MarketKey) => f.markets.find((m) => m.market === k)!;
        const result = [get("home_win"), get("draw"), get("away_win")];
        return (
          <button key={f.id} onClick={() => onSelect(f.id)} className="block w-full text-left">
            <Card className="p-4 transition-colors hover:border-accent">
              <div className="flex items-center justify-between text-xs text-ink-3">
                <span>{kickoffLabel(f.kickoff_utc)}</span>
                <span>xG {f.expected_goals[0].toFixed(1)}–{f.expected_goals[1].toFixed(1)}</span>
              </div>
              <div className="mt-2 grid grid-cols-[1fr_auto] gap-x-3 gap-y-1">
                <span className="truncate font-semibold">{f.home}</span>
                <span className="text-right text-sm font-bold">{pct(result[0].probability)}</span>
                <span className="truncate text-sm text-ink-2">Draw</span>
                <span className="text-right text-sm text-ink-2">{pct(result[1].probability)}</span>
                <span className="truncate font-semibold">{f.away}</span>
                <span className="text-right text-sm font-bold">{pct(result[2].probability)}</span>
              </div>
              <div className="mt-3 flex h-2 gap-[2px] overflow-hidden rounded-full" role="img"
                aria-label={`Home ${pct(result[0].probability)}, draw ${pct(result[1].probability)}, away ${pct(result[2].probability)}`}>
                <div className="bg-model" style={{ width: pct(result[0].probability, 1) }} />
                <div className="bg-track" style={{ width: pct(result[1].probability, 1) }} />
                <div className="bg-ink-3" style={{ width: pct(result[2].probability, 1) }} />
              </div>
              <div className="mt-3 flex gap-4 text-xs text-ink-2">
                <span>Home 1Up <b className="text-ink">{pct(get("home_1up").probability)}</b></span>
                <span>Away 1Up <b className="text-ink">{pct(get("away_1up").probability)}</b></span>
                <span>Over 1.5 <b className="text-ink">{pct(get("over_1.5").probability)}</b></span>
              </div>
            </Card>
          </button>
        );
      })}
    </div>
  );
}
