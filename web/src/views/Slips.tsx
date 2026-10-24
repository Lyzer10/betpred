import { useState } from "react";
import { BOOKMAKERS, type Bookmaker, type Ledger, type PlacedBet, type StakingSettings, newId, summarise } from "../ledger";
import { STAKING, VALUE_EDGE, edge, odds, pct, recommendedStake, timeLabel, tsh, useArchive } from "../lib";
import type { ArchiveSnapshot, DayBets, Predictions, Slip, TierName } from "../types";
import { Flag } from "../badges";
import { explainPick } from "../explain";
import { type Fixture, PREMIER_LEAGUE } from "../types";
import { Card, Crest, DateStrip, todayIso, Empty, OddsInput, SectionTitle, Segmented, StatusPill, TIERS, VerdictBadge, parseOdds } from "../ui";

const named = (leg: { label: string; home: string; away: string }) =>
  leg.label.replace("Home", leg.home).replace("Away", leg.away);

/** Where each tier is usually placed; changeable when recording the bet. */
const DEFAULT_BOOKMAKER: Record<TierName, Bookmaker> = { safe: "betpawa", medium: "betpawa", big: "sportybet" };


// ---- Record a placed bet -------------------------------------------------------

function PlaceForm({ tier, slip, day, total, balances, stakeFactor, staking, onPlace, onCancel }: {
  tier: TierName; slip: Slip; day: string; total: number; balances: Record<Bookmaker, number>; stakeFactor: number;
  staking?: StakingSettings;
  onPlace: (bet: PlacedBet) => void; onCancel: () => void;
}) {
  const [bookmaker, setBookmaker] = useState<Bookmaker>(DEFAULT_BOOKMAKER[tier]);
  const suggested = Math.floor(recommendedStake(balances[bookmaker], slip.win_probability, total, { tier, warning: slip.price_warning, staking })
    * stakeFactor / STAKING.roundTo) * STAKING.roundTo;
  const [stakeText, setStakeText] = useState("");
  const [oddsText, setOddsText] = useState("");
  const [flexiK, setFlexiK] = useState<number | null>(null);
  const [toWinText, setToWinText] = useState("");
  const stake = Math.round(Number(stakeText) || suggested);
  const placedOdds = parseOdds(oddsText) ?? total;
  const flexi = slip.flexi?.find((f) => f.min_correct === flexiK);
  const toWin = Number(toWinText) || 0;
  const flexiEdge = flexi && toWin > 0 && stake > 0 ? (flexi.probability * toWin) / stake - 1 : null;
  const ready = stake > 0 && (!flexi || toWin > 0);
  return (
    <div className="space-y-3 border-t border-border/60 bg-surface px-5 py-4">
      <div className="text-sm font-semibold">Record this bet</div>
      <div className="text-xs font-medium text-ink-2">Where did you place it?</div>
      <Segmented options={(Object.keys(BOOKMAKERS) as Bookmaker[]).map((b) => ({ id: b, label: BOOKMAKERS[b] }))}
        value={bookmaker} onChange={(b) => { setBookmaker(b); setFlexiK(null); setStakeText(""); }} />
      <div className="text-xs font-medium text-ink-2">How much did you stake?</div>
      <div className="grid grid-cols-2 gap-2">
        <label className="rounded-xl bg-surface-2 px-3 py-2 text-[11px] text-ink-3">Stake (TSh)
          <input inputMode="numeric" aria-label="Stake in TSh" placeholder={String(suggested || 0)}
            className="block w-full bg-transparent text-base font-bold text-ink outline-none" value={stakeText} onChange={(e) => setStakeText(e.target.value)} />
          {suggested > 0 && !stakeText && <span className="block text-[10px] text-ink-3">recommended</span>}
        </label>
        <label className="rounded-xl bg-surface-2 px-3 py-2 text-[11px] text-ink-3">Total odds on {BOOKMAKERS[bookmaker]}
          <input inputMode="decimal" aria-label="Total odds as placed" placeholder={odds(total)}
            className="block w-full bg-transparent text-base font-bold text-ink outline-none" value={oddsText} onChange={(e) => setOddsText(e.target.value)} />
        </label>
      </div>
      {bookmaker === "sportybet" && (slip.flexi?.length ?? 0) > 0 && (
        <div className="space-y-2">
          <div className="text-[11px] text-ink-3">Flexi (SportyBet)</div>
          <Segmented options={[{ id: "none", label: "Off" }, ...slip.flexi!.map((f) => ({ id: String(f.min_correct), label: `${f.min_correct} of ${slip.legs.length}` }))]}
            value={flexiK === null ? "none" : String(flexiK)} onChange={(id) => setFlexiK(id === "none" ? null : Number(id))} />
          {flexi && (
            <label className="block rounded-xl bg-surface-2 px-3 py-2 text-[11px] text-ink-3">"To Win" shown by SportyBet (TSh)
              <input inputMode="numeric" aria-label="Flexi To Win amount" className="block w-full bg-transparent text-base font-bold text-ink outline-none"
                value={toWinText} onChange={(e) => setToWinText(e.target.value)} />
            </label>
          )}
          {flexi && (
            <p className="text-xs text-ink-2">
              Chance at least {flexi.min_correct} of {slip.legs.length} win: <b>{pct(flexi.probability)}</b>
              {flexiEdge !== null && <> · {flexiEdge >= VALUE_EDGE ? <b className="text-good-ink">✓ worth it ({pct(flexiEdge, 1)})</b> : <b className="text-critical-ink">✕ payout too low ({pct(flexiEdge, 1)})</b>}</>}
            </p>
          )}
        </div>
      )}
      {balances[bookmaker] > 0 ? (
        stake > 0 && (
          <p className="text-xs text-ink-2">
            {BOOKMAKERS[bookmaker]} balance: {tsh(balances[bookmaker])} → <b className="text-ink">{tsh(balances[bookmaker] - stake)}</b> after this bet
            {" "}(wins return {tsh(flexi ? toWin : stake * placedOdds)}).
          </p>
        )
      ) : (
        <p className="text-xs text-warning-ink">Your {BOOKMAKERS[bookmaker]} balance isn't set yet: set it in Money so this bet is counted there.</p>
      )}
      <div className="flex gap-2">
        <button onClick={onCancel} className="flex-1 rounded-xl bg-surface-2 py-2.5 text-sm font-semibold text-ink-2">Cancel</button>
        <button disabled={!ready} className="flex-[2] rounded-xl bg-accent py-2.5 text-sm font-semibold text-white disabled:opacity-40"
          onClick={() => onPlace({
            id: newId(), type: "bet", placedAt: new Date().toISOString(), day, bookmaker, tier, stake,
            odds: placedOdds, winProbability: slip.win_probability,
            flexi: flexi ? { minCorrect: flexi.min_correct, toWin } : undefined,
            legs: slip.legs.map((l) => ({ home: l.home, away: l.away, date: l.date, market: l.market, label: named(l), probability: l.probability })),
          })}>Save: {stake > 0 ? tsh(stake) : "?"} on {BOOKMAKERS[bookmaker]}</button>
      </div>
    </div>
  );
}

// ---- Accumulator card ------------------------------------------------------------

function SlipCard({ tier, slip, day, balances, placed, stakeFactor, staking, fixtures, onPlace }: {
  tier: TierName; slip: Slip; day: string; balances: Record<Bookmaker, number>; placed: boolean; stakeFactor: number;
  staking?: StakingSettings; fixtures: Fixture[];
  onPlace: (bet: PlacedBet) => void;
}) {
  const [entered, setEntered] = useState<Record<number, string>>({});
  const [placing, setPlacing] = useState(false);
  const [open, setOpen] = useState<Record<number, boolean>>({});
  const prices = slip.legs.map((leg, i) => leg.betpawa_odds ?? parseOdds(entered[i] ?? ""));
  const complete = prices.every((p) => p != null);
  const total = complete ? prices.reduce<number>((a, b) => a * (b as number), 1) : 0;
  const bookmaker = DEFAULT_BOOKMAKER[tier];
  const stake = complete ? Math.floor(recommendedStake(balances[bookmaker], slip.win_probability, total, { tier, warning: slip.price_warning, staking })
    * stakeFactor / STAKING.roundTo) * STAKING.roundTo : 0;
  const hasValue = complete && edge(slip.win_probability, total) >= VALUE_EDGE;
  return (
    <Card className="overflow-hidden">
      <div className="bg-hero px-5 pb-5 pt-4 text-hero-ink">
        <div className="flex items-center justify-between text-xs opacity-70">
          <span>{TIERS[tier].range}</span>
          {slip.locked && <span className="rounded-full bg-white/10 px-2 py-0.5 font-semibold">Locked · in play</span>}
        </div>
        <div className="mt-3 flex items-end justify-between">
          <div>
            <div className="text-5xl font-extrabold tracking-tight">{pct(slip.win_probability)}</div>
            <div className="mt-1 text-xs opacity-70">chance all {slip.legs.length} win</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{complete ? odds(total) : "–"}</div>
            <div className="mt-1 text-xs opacity-70">Betpawa odds</div>
          </div>
        </div>
      </div>
      <ul>
        {slip.legs.map((leg, i) => {
          const fixture = fixtures.find((f) => f.home === leg.home && f.away === leg.away);
          const why = fixture ? explainPick(leg.market, fixture) : [];
          return (
            <li key={i} className="border-t border-border/60 first:border-t-0">
              <div className="flex items-center gap-3 px-5 py-3.5">
                <button className="flex min-w-0 flex-1 items-center gap-3 text-left" disabled={!why.length}
                  onClick={() => setOpen({ ...open, [i]: !open[i] })} aria-expanded={!!open[i]} aria-label={`Why ${named(leg)}`}>
                  <Crest team={leg.home} size="sm" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 text-sm font-semibold">
                      <span className="truncate">{named(leg)}</span>
                      {why.length > 0 && <span className="shrink-0 text-[10px] font-semibold text-accent">{open[i] ? "▴ why" : "▾ why"}</span>}
                    </div>
                    <div className="flex items-center gap-1.5 truncate text-xs text-ink-3">
                      <Flag country={(leg.league ?? PREMIER_LEAGUE).country} width={15} />
                      <span className="truncate">{leg.home} v {leg.away} · {timeLabel(leg.kickoff_utc)} · {pct(leg.probability)}</span>
                    </div>
                  </div>
                </button>
                {slip.locked && leg.won != null ? <StatusPill status={leg.won ? "won" : "lost"} />
                  : leg.betpawa_odds != null ? <span className="text-base font-bold">{odds(leg.betpawa_odds)}</span>
                  : <OddsInput label={`Odds for ${named(leg)}`} placeholder="Odds" value={entered[i] ?? ""} onChange={(v) => setEntered({ ...entered, [i]: v })} />}
              </div>
              {open[i] && (
                <ul className="mx-5 mb-3.5 space-y-1 rounded-xl bg-surface-2 px-3.5 py-2.5 text-xs leading-relaxed text-ink-2">
                  {why.map((line) => <li key={line}>• {line}</li>)}
                </ul>
              )}
            </li>
          );
        })}
      </ul>

      {(slip.flexi?.length ?? 0) > 0 && (
        <div className="border-t border-border/60 px-5 py-3 text-xs text-ink-2">
          <span className="font-semibold text-ink">SportyBet Flexi:</span>{" "}
          {slip.flexi!.map((f) => `${f.min_correct} of ${slip.legs.length} → ${pct(f.probability)}`).join(" · ")}
        </div>
      )}

      <div className="bg-surface-2/60 px-5 py-3.5">
        {!complete ? (
          <span className="text-xs text-ink-3">Betpawa has no price for one pick: type it to check.</span>
        ) : (
          <div className="flex items-center justify-between gap-3">
            <div>
              {stake > 0 ? (
                <>
                  <div className="text-[11px] text-ink-3">Stake on {BOOKMAKERS[bookmaker]}</div>
                  <div className="text-base font-bold">{tsh(stake)}</div>
                  <div className="text-[11px] text-ink-3">returns {tsh(stake * total)}</div>
                </>
              ) : (
                <div className="text-xs text-ink-3">
                  {!hasValue ? "Betpawa's odds are too low for this slip: skip it."
                    : balances[bookmaker] > 0 ? `The right stake is under TSh ${STAKING.minStake} for your ${BOOKMAKERS[bookmaker]} balance: skip, or keep it to the minimum.`
                    : `Set your ${BOOKMAKERS[bookmaker]} balance in Money to see the stake.`}
                </div>
              )}
            </div>
            <VerdictBadge probability={slip.win_probability} odds={total} />
          </div>
        )}
        {slip.price_warning && complete && (
          <p className="mt-2 text-[11px] text-warning-ink">⚠ A pick's price is much higher than other bookmakers': check team news first. Stake halved.</p>
        )}
      </div>

      {!slip.locked && complete && !placing && (
        <button onClick={() => setPlacing(true)} disabled={placed}
          className="w-full border-t border-border/60 py-3.5 text-sm font-semibold text-accent disabled:text-good-ink">
          {placed ? "✓ Recorded in Money" : "I placed this bet"}
        </button>
      )}
      {placing && (
        <PlaceForm tier={tier} slip={slip} day={day} total={total} balances={balances} stakeFactor={stakeFactor} staking={staking}
          onCancel={() => setPlacing(false)} onPlace={(bet) => { onPlace(bet); setPlacing(false); }} />
      )}
    </Card>
  );
}

// ---- Days ------------------------------------------------------------------------

function UpcomingDay({ day, data, ledger, onPlace }: { day: DayBets; data: Predictions; ledger: Ledger; onPlace: (bet: PlacedBet) => void }) {
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => day.slips[t]);
  const [tier, setTier] = useState<TierName>(tiers[0] ?? "safe");
  const balances = Object.fromEntries((Object.keys(BOOKMAKERS) as Bookmaker[])
    .map((b) => [b, summarise(ledger, b, data.results).balance])) as Record<Bookmaker, number>;
  const placedKey = (t: TierName) => ledger.entries.some((e) => e.type === "bet" && e.day === day.date && e.tier === t);
  if (!tiers.length) {
    return <Empty>Not enough matches with prices on this day to build an accumulator.</Empty>;
  }
  const record = data.backtest[tier];
  return (
    <div className="space-y-3">
      <Segmented options={tiers.map((t) => ({ id: t, label: TIERS[t].title }))} value={tier} onChange={setTier} />
      <SlipCard key={`${day.date}-${tier}`} tier={tier} slip={day.slips[tier]!} day={day.date} balances={balances}
        placed={placedKey(tier)} stakeFactor={data.health?.stake_factor ?? 1} staking={ledger.staking} fixtures={data.fixtures} onPlace={onPlace} />
      {record && (
        <p className="px-2 text-xs leading-relaxed text-ink-3">
          Track record of {TIERS[tier].title} slips: won <b className="text-ink-2">{pct(record.win_rate, 1)}</b> of {record.slips} past days
          (we predicted {pct(record.predicted_win_rate, 1)}). A slip at odds {odds(record.average_odds)} can't win much more often than that:
          it's what those odds mean.
        </p>
      )}
      <p className="px-2 text-xs text-ink-3">
        Stakes: {ledger.staking?.mode === "fixed" ? `a fixed ${tsh(ledger.staking.fixed)} per slip`
          : ledger.staking?.mode === "percent" ? `${ledger.staking.percent}% of your ${BOOKMAKERS[DEFAULT_BOOKMAKER[tier]]} balance per slip`
          : `a quarter of the Kelly amount, at most ${pct(STAKING.maxTier[tier])} of your ${BOOKMAKERS[DEFAULT_BOOKMAKER[tier]]} balance for ${TIERS[tier].title}`} (change in Money).
        Nothing when the odds are below fair.
      </p>
    </div>
  );
}

function PastDay({ snapshot }: { snapshot: ArchiveSnapshot }) {
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => snapshot.slips[t]);
  if (!tiers.length) return <Empty>No accumulators were offered this day.</Empty>;
  return (
    <Card className="overflow-hidden">
      {tiers.map((t) => {
        const slip = snapshot.slips[t]!;
        return (
          <div key={t} className="border-t border-border/60 px-5 py-4 first:border-t-0">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">{TIERS[t].title} · odds {odds(slip.total_odds)} · {pct(slip.win_probability)}</span>
              <StatusPill status={slip.status ?? "pending"} />
            </div>
            <ul className="mt-2 space-y-1">
              {slip.legs.map((l, i) => (
                <li key={i} className="flex items-center gap-2 text-xs text-ink-2">
                  <span className={`w-3 font-bold ${l.won === true ? "text-good-ink" : l.won === false ? "text-critical-ink" : "text-ink-3"}`}>
                    {l.won === true ? "✓" : l.won === false ? "✕" : "•"}
                  </span>
                  <span className="truncate">{named(l)} · {l.home} v {l.away}</span>
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </Card>
  );
}

function ArchivedDay({ date }: { date: string }) {
  const snapshot = useArchive(date);
  return snapshot ? <PastDay snapshot={snapshot} /> : <p className="mt-6 text-center text-sm text-ink-3">Loading…</p>;
}

export function Slips({ data, ledger, onPlace, onOpenMoney }: {
  data: Predictions; ledger: Ledger; onPlace: (bet: PlacedBet) => void; onOpenMoney: () => void;
}) {
  const today = todayIso();
  const upcoming = new Map(data.days.map((d) => [d.date, d]));
  const past = (data.archive ?? []).map((a) => a.date).filter((d) => d < today && !upcoming.has(d));
  const dates = [...new Set([...past, ...upcoming.keys()])].sort();
  const initial = upcoming.has(today) ? today : [...upcoming.keys()].find((d) => d >= today) ?? dates[dates.length - 1];
  const [selected, setSelected] = useState<string | undefined>(initial);
  const needsBalance = !ledger.start.betpawa && !ledger.start.sportybet;
  const health = data.health;

  return (
    <div>
      {health && (health.status === "warning" || health.status === "watch") && (
        <Card className={`mb-4 px-5 py-4 ${health.status === "warning" ? "bg-critical/10" : "bg-warning/15"}`}>
          <div className={`text-sm font-semibold ${health.status === "warning" ? "text-critical-ink" : "text-warning-ink"}`}>
            {health.status === "warning" ? "⚠ Model under review: stakes halved" : "≈ Model on watch"}
          </div>
          <div className="mt-1 text-xs text-ink-2">
            {health.checks.filter((c) => c.status === "warning" || c.status === "watch").map((c) => c.detail).join(" · ")}
          </div>
        </Card>
      )}
      <div className="mb-4"><DateStrip dates={dates} selected={selected} onSelect={setSelected} /></div>

      {needsBalance && selected && upcoming.has(selected) && (
        <button onClick={onOpenMoney} className="mb-4 block w-full text-left">
          <Card className="px-5 py-4">
            <div className="text-sm font-semibold">Set your Betpawa and SportyBet balances</div>
            <div className="text-xs text-ink-3">Needed to tell you how much to stake. Open Money ›</div>
          </Card>
        </button>
      )}

      {selected && upcoming.has(selected) && (
        <>
          <SectionTitle aside={`${upcoming.get(selected)!.fixtures.length} matches`}>Accumulators</SectionTitle>
          <UpcomingDay key={selected} day={upcoming.get(selected)!} data={data} ledger={ledger} onPlace={onPlace} />
        </>
      )}
      {selected && !upcoming.has(selected) && (
        <>
          <SectionTitle>Slips that day</SectionTitle>
          <ArchivedDay key={selected} date={selected} />
        </>
      )}
      {!selected && <Empty>No matches scheduled yet.</Empty>}
    </div>
  );
}
