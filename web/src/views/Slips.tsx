import { useState } from "react";
import { kickoffLabel, odds, pct } from "../lib";
import type { Predictions, Slip, TierName } from "../types";
import { Card, Crest, Empty, OddsInput, Segmented, StatusPill, TIERS, VerdictBadge, parseOdds } from "../ui";

function SlipCard({ tier, slip, backtest }: { tier: TierName; slip: Slip; backtest?: Predictions["backtest"][TierName] }) {
  const [entered, setEntered] = useState<Record<number, string>>({});
  const legOdds = slip.legs.map((leg, i) => parseOdds(entered[i] ?? "") ?? leg.estimated_odds);
  const allEntered = slip.legs.every((_, i) => parseOdds(entered[i] ?? "") !== null);
  const total = legOdds.reduce((a, b) => a * b, 1);
  const meta = TIERS[tier];
  return (
    <div className="space-y-3">
      <Card className="overflow-hidden">
        <div className="bg-hero px-5 pb-5 pt-4 text-hero-ink">
          <div className="flex items-center justify-between text-xs opacity-70">
            <span>{meta.range}</span>
            {slip.locked && <span className="rounded-full bg-white/10 px-2 py-0.5 font-semibold">Locked · in play</span>}
          </div>
          <div className="mt-3 flex items-end justify-between">
            <div>
              <div className="text-5xl font-extrabold tracking-tight">{pct(slip.win_probability)}</div>
              <div className="mt-1 text-xs opacity-70">chance this slip wins</div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{odds(total)}</div>
              <div className="mt-1 text-xs opacity-70">{allEntered ? "your odds" : "est. odds"}</div>
            </div>
          </div>
        </div>
        <ul>
          {slip.legs.map((leg, i) => (
            <li key={i} className="flex items-center gap-3 border-t border-border/60 px-5 py-3.5 first:border-t-0">
              <Crest team={leg.home} size="sm" />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-semibold">{leg.label.replace("Home", leg.home).replace("Away", leg.away)}</div>
                <div className="truncate text-xs text-ink-3">{leg.home} v {leg.away} · {kickoffLabel(leg.kickoff_utc)}</div>
                <div className="mt-0.5 text-xs text-ink-2">{pct(leg.probability)} likely · fair odds {odds(leg.fair_odds)}</div>
              </div>
              {slip.locked && leg.won != null ? <StatusPill status={leg.won ? "won" : "lost"} />
                : <OddsInput label={`Your odds for ${leg.label}`} placeholder={odds(leg.estimated_odds)}
                    value={entered[i] ?? ""} onChange={(v) => setEntered({ ...entered, [i]: v })} />}
            </li>
          ))}
        </ul>
        <div className="flex min-h-12 items-center justify-between gap-3 bg-surface-2/60 px-5 py-3">
          {allEntered ? (
            <>
              <span className="text-xs text-ink-2">With your odds</span>
              <VerdictBadge probability={slip.win_probability} odds={total} />
            </>
          ) : (
            <span className="text-xs text-ink-3">Enter your bookmaker's odds for each pick to check value</span>
          )}
        </div>
      </Card>
      {backtest && (
        <p className="px-2 text-xs leading-relaxed text-ink-3">
          In the backtest this tier won <b className="text-ink-2">{pct(backtest.win_rate, 1)}</b> of {backtest.slips} slips
          (we predicted {pct(backtest.predicted_win_rate, 1)}) at average odds of {odds(backtest.average_odds)}.
        </p>
      )}
    </div>
  );
}

export function Slips({ data }: { data: Predictions }) {
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => data.slips[t]);
  const [tier, setTier] = useState<TierName>(tiers[0] ?? "safe");
  if (!tiers.length) return <Empty>No slips for the next round yet. They appear once bookmaker odds are published.</Empty>;
  return (
    <div className="space-y-4">
      <Segmented options={tiers.map((t) => ({ id: t, label: TIERS[t].title }))} value={tier} onChange={setTier} />
      <SlipCard key={tier} tier={tier} slip={data.slips[tier]!} backtest={data.backtest[tier]} />
      <p className="px-2 text-xs leading-relaxed text-ink-3">
        Each slip is the most likely combination in its odds range, one pick per match. Only place it when your
        bookmaker's odds show <b className="text-good-ink">✓ Value bet</b>.
      </p>
    </div>
  );
}
