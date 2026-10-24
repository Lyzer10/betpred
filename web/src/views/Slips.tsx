import { useState } from "react";
import { kickoffLabel, odds, pct } from "../lib";
import type { Predictions, Slip, TierName } from "../types";
import { Card, OddsInput, Stat, TIERS, VerdictBadge, parseOdds } from "../ui";

function SlipCard({ tier, slip, backtest }: { tier: TierName; slip: Slip; backtest?: Predictions["backtest"][TierName] }) {
  const [entered, setEntered] = useState<Record<number, string>>({});
  const legOdds = slip.legs.map((leg, i) => parseOdds(entered[i] ?? "") ?? leg.estimated_odds);
  const allEntered = slip.legs.every((_, i) => parseOdds(entered[i] ?? "") !== null);
  const total = legOdds.reduce((a, b) => a * b, 1);
  const meta = TIERS[tier];
  return (
    <Card className="overflow-hidden">
      <div className="flex items-start justify-between gap-3 bg-hero px-4 py-4 text-hero-ink">
        <div>
          <div className="text-lg font-bold">{meta.title}</div>
          <div className="text-xs opacity-75">{meta.range}</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-extrabold leading-none">{pct(slip.win_probability)}</div>
          <div className="mt-1 text-xs opacity-75">chance to win</div>
        </div>
      </div>
      <ul className="divide-y divide-border">
        {slip.legs.map((leg, i) => (
          <li key={i} className="flex items-center gap-3 px-4 py-3">
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-semibold">{leg.home} v {leg.away}</div>
              <div className="text-sm text-accent font-medium">{leg.label}</div>
              <div className="text-xs text-ink-3">{kickoffLabel(leg.kickoff_utc)} · {pct(leg.probability)} · fair odds {odds(leg.fair_odds)}</div>
            </div>
            <OddsInput label={`Your odds for ${leg.label}`} placeholder={odds(leg.estimated_odds)}
              value={entered[i] ?? ""} onChange={(v) => setEntered({ ...entered, [i]: v })} />
          </li>
        ))}
      </ul>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border bg-surface-2 px-4 py-3">
        <div className="text-sm">
          <span className="text-ink-2">Total odds </span>
          <span className="font-bold">{odds(total)}</span>
          {!allEntered && <span className="text-xs text-ink-3"> (estimated)</span>}
        </div>
        {allEntered ? <VerdictBadge probability={slip.win_probability} odds={total} />
          : <span className="text-xs text-ink-3">Enter your bookmaker's odds to check value</span>}
      </div>
      {backtest && (
        <div className="px-4 py-2.5 text-xs text-ink-2">
          Backtest: won <b className="text-ink">{pct(backtest.win_rate, 1)}</b> of {backtest.slips} past slips (predicted {pct(backtest.predicted_win_rate, 1)}, avg odds {odds(backtest.average_odds)})
        </div>
      )}
    </Card>
  );
}

export function Slips({ data }: { data: Predictions }) {
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => data.slips[t]);
  if (!tiers.length) {
    return <Card className="p-6 text-center text-ink-2">No slips for the next round yet. Check back once bookmaker odds are published.</Card>;
  }
  return (
    <div className="space-y-4">
      <Card className="grid grid-cols-3 gap-3 p-4">
        <Stat label="Round" value={data.round?.split("-").pop() === "midweek" ? "Midweek" : "Weekend"} />
        <Stat label="Fixtures" value={String(data.fixtures.length)} />
        <Stat label="Data to" value={new Date(data.model.training_last_date).toLocaleDateString(undefined, { day: "numeric", month: "short" })} />
      </Card>
      {tiers.map((tier) => <SlipCard key={tier} tier={tier} slip={data.slips[tier]!} backtest={data.backtest[tier]} />)}
      <p className="px-1 text-xs leading-relaxed text-ink-3">
        Each slip is the most likely combination in its odds range, one pick per match. The chance to win is
        what you should expect over many slips, not a promise for this one. A slip is only worth placing when
        your bookmaker's odds show <b>Value bet</b>.
      </p>
    </div>
  );
}
