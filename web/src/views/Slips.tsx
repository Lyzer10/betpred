import { useState } from "react";
import { STAKING, VALUE_EDGE, capRound, edge, odds, pct, recommendedStake, timeLabel, tsh, useArchive } from "../lib";
import type { ArchiveSnapshot, DayBets, Predictions, Slip, TierName } from "../types";
import { Card, Crest, Empty, OddsInput, SectionTitle, Segmented, StatusPill, TIERS, VerdictBadge, parseOdds } from "../ui";

const named = (leg: { label: string; home: string; away: string }) =>
  leg.label.replace("Home", leg.home).replace("Away", leg.away);

/** Local calendar day (YYYY-MM-DD) of a date, in the device's time zone. */
const isoDay = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

function dayName(day: string) {
  const today = new Date();
  const offset = (n: number) => isoDay(new Date(today.getFullYear(), today.getMonth(), today.getDate() + n));
  if (day === offset(0)) return "Today";
  if (day === offset(-1)) return "Yesterday";
  if (day === offset(1)) return "Tomorrow";
  return new Date(`${day}T12:00:00`).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
}

// ---- Balance -----------------------------------------------------------------

function BalanceCard({ bankroll, onChange }: { bankroll: number; onChange: (amount: number) => void }) {
  const [editing, setEditing] = useState(bankroll <= 0);
  const [text, setText] = useState(bankroll > 0 ? String(bankroll) : "");
  const [showRules, setShowRules] = useState(false);
  const save = () => {
    const amount = Math.round(Number(text.replace(/[^\d.]/g, "")));
    if (amount > 0) { onChange(amount); setEditing(false); }
  };
  return (
    <Card className="px-5 py-4">
      {editing ? (
        <form onSubmit={(e) => { e.preventDefault(); save(); }}>
          <label className="text-sm font-semibold" htmlFor="balance">How much is in your Betpawa account?</label>
          <p className="text-xs text-ink-3">Stakes for every bet are worked out from this.</p>
          <div className="mt-3 flex items-center gap-2">
            <span className="text-sm font-semibold text-ink-3">TSh</span>
            <input id="balance" autoFocus inputMode="numeric" placeholder="e.g. 50000"
              className="min-w-0 flex-1 rounded-xl bg-surface-2 px-3 py-2.5 text-base font-bold outline-none ring-accent focus:ring-2"
              value={text} onChange={(e) => setText(e.target.value)} />
            <button type="submit" className="rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white">Save</button>
          </div>
        </form>
      ) : (
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-ink-3">Betpawa balance</div>
            <div className="text-2xl font-extrabold tracking-tight">{tsh(bankroll)}</div>
          </div>
          <button onClick={() => setEditing(true)} className="rounded-xl bg-surface-2 px-3 py-2 text-sm font-semibold text-accent">Update</button>
        </div>
      )}
      <button onClick={() => setShowRules(!showRules)} className="mt-3 text-xs font-medium text-ink-3">
        How stakes are worked out {showRules ? "▴" : "▾"}
      </button>
      {showRules && (
        <ul className="mt-2 space-y-1 text-xs leading-relaxed text-ink-2">
          <li>• We only stake when Betpawa pays at least {pct(VALUE_EDGE)} more than the fair price.</li>
          <li>• Size: a quarter of the Kelly amount, the professional standard when probabilities are estimates.</li>
          <li>• Never more than {pct(STAKING.maxSingle)} of your balance on a single, {pct(STAKING.maxMulti)} on an accumulator, {pct(STAKING.maxRound)} on a whole day.</li>
          <li>• Half stake if Betpawa's price looks suspiciously high (possible team news).</li>
        </ul>
      )}
    </Card>
  );
}

// ---- One bet ---------------------------------------------------------------

function BetCard({ leg, stake, price }: {
  leg: { label: string; home: string; away: string; kickoff_utc: string; probability: number; fair_odds: number; price_warning?: boolean };
  stake: number; price: number;
}) {
  const e = edge(leg.probability, price);
  return (
    <Card className="px-5 py-4">
      <div className="flex items-center gap-2 text-xs text-ink-3">
        <Crest team={leg.home} size="sm" />
        <span className="truncate">{leg.home} v {leg.away} · {timeLabel(leg.kickoff_utc)}</span>
      </div>
      <div className="mt-2 flex items-end justify-between gap-3">
        <div className="min-w-0">
          <div className="text-lg font-bold leading-tight">{named(leg)}</div>
          <div className="mt-0.5 text-xs text-ink-2">{pct(leg.probability)} chance</div>
        </div>
        <div className="text-right">
          <div className="text-[11px] text-ink-3">Betpawa</div>
          <div className="text-2xl font-extrabold">{odds(price)}</div>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between gap-3 rounded-2xl bg-surface-2 px-4 py-3">
        {stake > 0 ? (
          <div>
            <div className="text-[11px] text-ink-3">Stake</div>
            <div className="text-base font-bold">{tsh(stake)}</div>
            <div className="text-[11px] text-ink-3">returns {tsh(stake * price)}</div>
          </div>
        ) : (
          <div className="text-xs text-ink-3">Add your balance above to see the stake</div>
        )}
        <VerdictBadge probability={leg.probability} odds={price} />
      </div>
      <p className="mt-2 text-xs leading-relaxed text-ink-3">
        Why: fair odds are {odds(leg.fair_odds)}, Betpawa pays {odds(price)}, so you get {pct(e, 1)} more than the risk is worth.
      </p>
      {leg.price_warning && (
        <p className="mt-1 text-xs font-medium text-warning-ink">⚠ This price is much higher than other bookmakers'. Check team news before betting; stake is halved.</p>
      )}
    </Card>
  );
}

// ---- Accumulator -------------------------------------------------------------

function SlipCard({ tier, slip, stake }: { tier: TierName; slip: Slip; stake: (total: number) => number }) {
  // Only legs without a Betpawa price need typed odds.
  const [entered, setEntered] = useState<Record<number, string>>({});
  const prices = slip.legs.map((leg, i) => leg.betpawa_odds ?? parseOdds(entered[i] ?? ""));
  const complete = prices.every((p) => p != null);
  const total = complete ? prices.reduce<number>((a, b) => a * (b as number), 1) : 0;
  const amount = complete ? stake(total) : 0;
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
            <div className="mt-1 text-xs opacity-70">chance to win</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{complete ? odds(total) : "–"}</div>
            <div className="mt-1 text-xs opacity-70">Betpawa odds</div>
          </div>
        </div>
      </div>
      <ul>
        {slip.legs.map((leg, i) => (
          <li key={i} className="flex items-center gap-3 border-t border-border/60 px-5 py-3.5 first:border-t-0">
            <Crest team={leg.home} size="sm" />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-semibold">{named(leg)}</div>
              <div className="truncate text-xs text-ink-3">{leg.home} v {leg.away} · {timeLabel(leg.kickoff_utc)} · {pct(leg.probability)}</div>
            </div>
            {slip.locked && leg.won != null ? <StatusPill status={leg.won ? "won" : "lost"} />
              : leg.betpawa_odds != null ? <span className="text-base font-bold">{odds(leg.betpawa_odds)}</span>
              : <OddsInput label={`Odds for ${named(leg)}`} placeholder="Odds" value={entered[i] ?? ""} onChange={(v) => setEntered({ ...entered, [i]: v })} />}
          </li>
        ))}
      </ul>
      <div className="flex items-center justify-between gap-3 bg-surface-2/60 px-5 py-3.5">
        {!complete ? <span className="text-xs text-ink-3">Betpawa has no price for one pick: type it to check.</span>
          : amount > 0 ? <span className="text-sm">Stake <b>{tsh(amount)}</b> <span className="text-xs text-ink-3">→ returns {tsh(amount * total)}</span></span>
          : <span className="text-xs text-ink-3">{edge(slip.win_probability, total) >= VALUE_EDGE ? "Add your balance to see the stake" : "Betpawa's odds are too low for this slip"}</span>}
        {complete && <VerdictBadge probability={slip.win_probability} odds={total} />}
      </div>
    </Card>
  );
}

// ---- Upcoming day ----------------------------------------------------------

function UpcomingDay({ day, data, bankroll }: { day: DayBets; data: Predictions; bankroll: number }) {
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => day.slips[t]);
  const [tier, setTier] = useState<TierName>(tiers[0] ?? "safe");
  const picks = day.value_picks.filter((p) => p.betpawa_odds != null);

  // One 10% cap across the whole day: singles plus each accumulator at Betpawa prices.
  const slipTotal = (s: Slip) => s.legs.every((l) => l.betpawa_odds != null) ? s.legs.reduce((a, l) => a * l.betpawa_odds!, 1) : 0;
  const slipStake = (s: Slip, total: number) =>
    s.locked || !total ? 0 : recommendedStake(bankroll, s.win_probability, total, { legs: s.legs.length, warning: s.price_warning });
  const raw = [
    ...picks.map((p) => recommendedStake(bankroll, p.probability, p.betpawa_odds!, { warning: p.price_warning })),
    ...tiers.map((t) => slipStake(day.slips[t]!, slipTotal(day.slips[t]!))),
  ];
  const capped = capRound(raw, bankroll);
  const scale = raw.reduce((a, b) => a + b, 0) ? capped.reduce((a, b) => a + b, 0) / raw.reduce((a, b) => a + b, 0) : 1;
  const dayTotal = capped.reduce((a, b) => a + b, 0);

  return (
    <div>
      <SectionTitle aside={`${day.fixtures.length} ${day.fixtures.length === 1 ? "match" : "matches"}`}>Best single bets</SectionTitle>
      {picks.length ? (
        <div className="space-y-3">{picks.map((p, i) => <BetCard key={`${p.home}-${p.market}`} leg={p} price={p.betpawa_odds!} stake={capped[i]} />)}</div>
      ) : (
        <Empty>
          <div className="text-base font-semibold text-ink">No good bets on this day</div>
          <div className="mt-1">Betpawa's prices are at or below fair for every match. Not betting is the right move.</div>
        </Empty>
      )}

      {tiers.length > 0 && (
        <>
          <SectionTitle>Accumulators</SectionTitle>
          <div className="space-y-3">
            <Segmented options={tiers.map((t) => ({ id: t, label: TIERS[t].title }))} value={tier} onChange={setTier} />
            <SlipCard key={`${day.date}-${tier}`} tier={tier} slip={day.slips[tier]!}
              stake={(total) => Math.floor((slipStake(day.slips[tier]!, total) * scale) / STAKING.roundTo) * STAKING.roundTo} />
            {data.backtest[tier] && (
              <p className="px-2 text-xs text-ink-3">
                Past record for {TIERS[tier].title}: won {pct(data.backtest[tier].win_rate, 1)} of {data.backtest[tier].slips} slips (predicted {pct(data.backtest[tier].predicted_win_rate, 1)}).
              </p>
            )}
          </div>
        </>
      )}

      {bankroll > 0 && dayTotal > 0 && (
        <Card className="mt-4 flex items-center justify-between px-5 py-3.5">
          <span className="text-sm text-ink-2">Total to stake this day</span>
          <span className="text-sm font-bold">{tsh(dayTotal)} <span className="font-medium text-ink-3">({pct(dayTotal / bankroll, 1)})</span></span>
        </Card>
      )}
    </div>
  );
}

// ---- Past day ----------------------------------------------------------------

function PastDay({ snapshot, rules }: { snapshot: ArchiveSnapshot; rules: { min_edge: number; min_probability: number } }) {
  const bets = snapshot.fixtures.flatMap((f) => f.markets
    .filter((m) => m.betpawa_odds && m.probability >= rules.min_probability && edge(m.probability, m.betpawa_odds) >= rules.min_edge)
    .map((m) => ({ fixture: f, market: m, won: f.result ? f.result.outcomes[m.market] : null })));
  const settled = bets.filter((b) => b.won !== null);
  const units = settled.reduce((a, b) => a + (b.won ? b.market.betpawa_odds! - 1 : -1), 0);
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => snapshot.slips[t]);
  return (
    <div>
      <SectionTitle aside={settled.length ? `${units >= 0 ? "+" : ""}${units.toFixed(2)} units` : undefined}>Single bets that day</SectionTitle>
      {bets.length ? (
        <Card className="overflow-hidden">
          {bets.map(({ fixture, market, won }) => (
            <div key={`${fixture.home}-${market.market}`} className="flex items-center gap-3 border-t border-border/60 px-5 py-3.5 first:border-t-0">
              <StatusPill status={won === null ? "pending" : won ? "won" : "lost"} />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-semibold">{named({ label: market.label, home: fixture.home, away: fixture.away })}</div>
                <div className="truncate text-xs text-ink-3">
                  {fixture.home} v {fixture.away}{fixture.result ? ` · ${fixture.result.score.join("-")}` : ""} · {pct(market.probability)}
                </div>
              </div>
              <span className="text-sm font-bold">{odds(market.betpawa_odds!)}</span>
            </div>
          ))}
        </Card>
      ) : <Empty>No single bets were recommended this day.</Empty>}
      {tiers.length > 0 && <SectionTitle>Accumulators that day</SectionTitle>}
      {tiers.length > 0 && (
        <Card className="overflow-hidden">
          {tiers.map((t) => {
            const slip = snapshot.slips[t]!;
            return (
              <div key={t} className="border-t border-border/60 px-5 py-3.5 first:border-t-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold">{TIERS[t].title} · odds {odds(slip.total_odds)}</span>
                  <StatusPill status={slip.status ?? "pending"} />
                </div>
                <div className="mt-1 text-xs text-ink-3">{slip.legs.map((l) => `${l.won === true ? "✓" : l.won === false ? "✕" : "•"} ${named(l)}`).join("  ")}</div>
              </div>
            );
          })}
        </Card>
      )}
    </div>
  );
}

function ArchivedDay({ date, rules }: { date: string; rules: { min_edge: number; min_probability: number } }) {
  const snapshot = useArchive(date);
  return snapshot ? <PastDay snapshot={snapshot} rules={rules} /> : <p className="mt-6 text-center text-sm text-ink-3">Loading…</p>;
}

// ---- Screen ------------------------------------------------------------------

export function Slips({ data, bankroll, onBankroll }: { data: Predictions; bankroll: number; onBankroll: (amount: number) => void }) {
  const today = isoDay(new Date());
  const upcoming = new Map(data.days.map((d) => [d.date, d]));
  const past = (data.archive ?? []).map((a) => a.date).filter((d) => d < today && !upcoming.has(d));
  const dates = [...new Set([...past, ...upcoming.keys()])].sort();
  const initial = upcoming.has(today) ? today : [...upcoming.keys()].find((d) => d >= today) ?? dates[dates.length - 1];
  const [selected, setSelected] = useState<string | undefined>(initial);
  const rules = data.value_rules ?? { min_edge: VALUE_EDGE, min_probability: 0.25 };

  return (
    <div>
      <div className="no-scrollbar -mx-4 mb-4 flex gap-2 overflow-x-auto px-4 pb-1">
        {dates.map((d) => {
          const active = d === selected;
          const count = upcoming.get(d)?.value_picks.length;
          return (
            <button key={d} onClick={() => setSelected(d)} aria-pressed={active}
              className={`shrink-0 rounded-2xl px-4 py-2.5 text-left transition ${active ? "bg-hero text-hero-ink" : "bg-surface text-ink shadow-card"}`}>
              <div className="text-sm font-bold">{dayName(d)}</div>
              <div className="text-[11px] opacity-70">{count != null ? `${count} ${count === 1 ? "bet" : "bets"}` : "results"}</div>
            </button>
          );
        })}
      </div>

      {selected && upcoming.has(selected) && <BalanceCard bankroll={bankroll} onChange={onBankroll} />}
      {selected && upcoming.has(selected) && <UpcomingDay key={selected} day={upcoming.get(selected)!} data={data} bankroll={bankroll} />}
      {selected && !upcoming.has(selected) && <ArchivedDay key={selected} date={selected} rules={rules} />}
      {!selected && <Empty>No matches scheduled yet.</Empty>}
    </div>
  );
}
