import { useState } from "react";
import { BOOKMAKERS, type Bookmaker, DEFAULT_STAKING, type Ledger, type StakingMode, betStatus, isBet, isTransfer, newId, payout, summarise } from "../ledger";
import { STAKING, losingStreakChance, odds, pct, tsh } from "../lib";
import type { Result } from "../types";
import { Card, Empty, SectionTitle, Segmented, Stat, StatusPill, TIERS } from "../ui";

/** Safe-slip win rate from the backtest (about 37%), used for the risk estimate. */
const SAFE_WIN_RATE = 0.37;
const BETS_PER_MONTH = 30;

function StakingCard({ ledger, balance, onChange }: { ledger: Ledger; balance: number; onChange: (ledger: Ledger) => void }) {
  const staking = ledger.staking ?? DEFAULT_STAKING;
  const [text, setText] = useState(String(staking.mode === "fixed" ? staking.fixed : staking.percent));
  const setMode = (mode: StakingMode) => {
    onChange({ ...ledger, staking: { ...staking, mode } });
    setText(String(mode === "fixed" ? staking.fixed : staking.percent));
  };
  const save = (value: string) => {
    setText(value);
    const number = Number(value.replace(/[^\d.]/g, ""));
    if (!(number > 0)) return;
    if (staking.mode === "fixed") onChange({ ...ledger, staking: { ...staking, fixed: Math.round(number) } });
    if (staking.mode === "percent") onChange({ ...ledger, staking: { ...staking, percent: Math.min(number, 50) } });
  };
  const example = staking.mode === "fixed" ? Math.min(staking.fixed, balance)
    : staking.mode === "percent" ? Math.floor((balance * staking.percent) / 100 / STAKING.roundTo) * STAKING.roundTo
    : 0;
  const lossesToHalve = example > 0 ? Math.ceil((balance * 0.5) / example) : 0;
  const risk = lossesToHalve ? losingStreakChance(1 - SAFE_WIN_RATE, lossesToHalve, BETS_PER_MONTH) : 0;
  return (
    <Card className="px-5 py-4">
      <div className="text-sm font-semibold">Stake per slip</div>
      <div className="mt-3">
        <Segmented options={[{ id: "smart", label: "Smart" }, { id: "percent", label: "% of balance" }, { id: "fixed", label: "Fixed TSh" }]}
          value={staking.mode} onChange={(m) => setMode(m as StakingMode)} />
      </div>
      {staking.mode === "smart" ? (
        <p className="mt-3 text-xs leading-relaxed text-ink-2">
          Sized by how much value the slip has (a quarter of the Kelly amount), at most {pct(STAKING.maxTier.safe)} of your balance on Safe.
          Safest for small balances, but stakes can be small.
        </p>
      ) : (
        <>
          <label className="mt-3 flex items-center gap-2 rounded-xl bg-surface-2 px-3 py-2.5">
            <span className="text-xs text-ink-3">{staking.mode === "fixed" ? "TSh" : "%"}</span>
            <input inputMode="numeric" aria-label={staking.mode === "fixed" ? "Fixed stake in TSh" : "Percent of balance"}
              className="w-full bg-transparent text-base font-bold outline-none" value={text} onChange={(e) => save(e.target.value)} />
          </label>
          {balance > 0 && example > 0 && (
            <p className={`mt-3 text-xs leading-relaxed ${risk > 0.5 ? "text-critical-ink" : risk > 0.2 ? "text-warning-ink" : "text-ink-2"}`}>
              {tsh(example)} is {pct(example / balance)} of your Betpawa balance. Losing half of it takes {lossesToHalve} Safe slips lost in a row;
              over a month of {BETS_PER_MONTH} Safe slips that happens at least once about <b>{pct(risk)}</b> of the time.
            </p>
          )}
        </>
      )}
      <p className="mt-2 text-[11px] text-ink-3">Any mode: slips without value still say skip, and stakes are halved on price or model warnings.</p>
    </Card>
  );
}

const signed = (amount: number) => `${amount >= 0 ? "+" : "−"}${tsh(Math.abs(amount))}`;

function AmountForm({ label, onSubmit, onCancel }: { label: string; onSubmit: (amount: number) => void; onCancel: () => void }) {
  const [text, setText] = useState("");
  const amount = Math.round(Number(text.replace(/[^\d.]/g, "")));
  return (
    <form className="mt-3 flex items-center gap-2" onSubmit={(e) => { e.preventDefault(); if (amount > 0) onSubmit(amount); }}>
      <input autoFocus inputMode="numeric" aria-label={label} placeholder={label}
        className="min-w-0 flex-1 rounded-xl bg-surface-2 px-3 py-2.5 text-sm font-bold outline-none ring-accent focus:ring-2"
        value={text} onChange={(e) => setText(e.target.value)} />
      <button type="button" onClick={onCancel} className="rounded-xl px-3 py-2.5 text-sm font-semibold text-ink-3">Cancel</button>
      <button type="submit" disabled={!(amount > 0)} className="rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-40">Save</button>
    </form>
  );
}

function AccountCard({ bookmaker, ledger, results, onChange }: {
  bookmaker: Bookmaker; ledger: Ledger; results: Result[]; onChange: (ledger: Ledger) => void;
}) {
  const [mode, setMode] = useState<"start" | "deposit" | "withdrawal" | null>(null);
  const s = summarise(ledger, bookmaker, results);
  const started = ledger.start[bookmaker] > 0 || ledger.entries.some((e) => e.bookmaker === bookmaker);
  const save = (amount: number) => {
    if (mode === "start") onChange({ ...ledger, start: { ...ledger.start, [bookmaker]: amount } });
    else if (mode) onChange({ ...ledger, entries: [...ledger.entries, { id: newId(), type: mode, placedAt: new Date().toISOString(), bookmaker, amount }] });
    setMode(null);
  };
  return (
    <Card className="px-5 py-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-[11px] font-medium text-ink-3">{BOOKMAKERS[bookmaker]} balance</div>
          <div className="text-2xl font-extrabold tracking-tight">{started ? tsh(s.balance) : "Not set"}</div>
          {s.pendingStakes > 0 && <div className="text-[11px] text-ink-3">{tsh(s.pendingStakes)} in open bets</div>}
        </div>
        {started && (
          <div className="text-right">
            <div className="text-[11px] text-ink-3">Betting profit</div>
            <div className={`text-base font-bold ${s.profit >= 0 ? "text-good-ink" : "text-critical-ink"}`}>{signed(s.profit)}</div>
          </div>
        )}
      </div>
      {mode ? (
        <AmountForm label={mode === "start" ? "Balance now (TSh)" : mode === "deposit" ? "Deposit (TSh)" : "Withdrawal (TSh)"}
          onSubmit={save} onCancel={() => setMode(null)} />
      ) : (
        <div className="mt-3 flex gap-2">
          {!started ? (
            <button onClick={() => setMode("start")} className="flex-1 rounded-xl bg-accent py-2.5 text-sm font-semibold text-white">Set balance</button>
          ) : (
            <>
              <button onClick={() => setMode("deposit")} className="flex-1 rounded-xl bg-surface-2 py-2.5 text-sm font-semibold">+ Deposit</button>
              <button onClick={() => setMode("withdrawal")} className="flex-1 rounded-xl bg-surface-2 py-2.5 text-sm font-semibold">− Withdraw</button>
              <button onClick={() => setMode("start")} className="rounded-xl bg-surface-2 px-3 py-2.5 text-xs font-semibold text-ink-3" aria-label="Correct starting balance">Fix</button>
            </>
          )}
        </div>
      )}
    </Card>
  );
}

export function Money({ ledger, results, onChange }: { ledger: Ledger; results: Result[]; onChange: (ledger: Ledger) => void }) {
  const accounts = Object.keys(BOOKMAKERS) as Bookmaker[];
  const totals = accounts.map((b) => summarise(ledger, b, results));
  const profit = totals.reduce((a, s) => a + s.profit, 0);
  const staked = totals.reduce((a, s) => a + s.staked, 0);
  const won = totals.reduce((a, s) => a + s.won, 0);
  const lost = totals.reduce((a, s) => a + s.lost, 0);
  const bets = ledger.entries.filter(isBet).slice().reverse();
  const transfers = ledger.entries.filter(isTransfer).slice().reverse();
  const month = new Date().toISOString().slice(0, 7);
  const monthProfit = bets.filter((b) => b.placedAt.startsWith(month)).reduce((a, b) => {
    const { status } = betStatus(b, results);
    return status === "pending" ? a : a + (status === "won" ? payout(b) : 0) - b.stake;
  }, 0);
  const remove = (id: string) => onChange({ ...ledger, entries: ledger.entries.filter((e) => e.id !== id) });

  return (
    <div>
      <div className="space-y-3">{accounts.map((b) => <AccountCard key={b} bookmaker={b} ledger={ledger} results={results} onChange={onChange} />)}</div>

      <SectionTitle>Staking</SectionTitle>
      <StakingCard ledger={ledger} balance={totals[0].balance} onChange={onChange} />

      <SectionTitle>Overall</SectionTitle>
      <Card className="grid grid-cols-3 gap-3 px-5 py-4">
        <Stat label="Profit" value={signed(profit)} sub={staked ? `ROI ${pct(profit / staked, 1)}` : "no settled bets"} />
        <Stat label="This month" value={signed(monthProfit)} />
        <Stat label="Slips won" value={won + lost ? `${won}/${won + lost}` : "–"} sub={won + lost ? pct(won / (won + lost)) : undefined} />
      </Card>
      <p className="mt-2 px-2 text-xs leading-relaxed text-ink-3">
        Deposits and withdrawals change your balance but never your profit. A realistic good result is steady growth;
        losing runs of several slips are normal even with an edge.
      </p>

      <SectionTitle aside={bets.length ? `${bets.length}` : undefined}>Placed bets</SectionTitle>
      {bets.length ? (
        <Card className="overflow-hidden">
          {bets.map((bet) => {
            const { status, legs } = betStatus(bet, results);
            return (
              <div key={bet.id} className="border-t border-border/60 px-5 py-4 first:border-t-0">
                <div className="flex items-center justify-between gap-2">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold">{TIERS[bet.tier].title} · {BOOKMAKERS[bet.bookmaker]}{bet.flexi ? ` · Flexi ${bet.flexi.minCorrect}/${bet.legs.length}` : ""}</div>
                    <div className="text-xs text-ink-3">{new Date(`${bet.day}T12:00:00`).toLocaleDateString(undefined, { day: "numeric", month: "short" })} · {tsh(bet.stake)} @ {odds(bet.odds)} · pays {tsh(payout(bet))}</div>
                  </div>
                  <StatusPill status={status} />
                </div>
                <ul className="mt-2 space-y-1">
                  {bet.legs.map((l, i) => (
                    <li key={i} className="flex items-center gap-2 text-xs text-ink-2">
                      <span className={`w-3 font-bold ${legs[i] === true ? "text-good-ink" : legs[i] === false ? "text-critical-ink" : "text-ink-3"}`}>
                        {legs[i] === true ? "✓" : legs[i] === false ? "✕" : "•"}
                      </span>
                      <span className="truncate">{l.label} · {l.home} v {l.away}</span>
                    </li>
                  ))}
                </ul>
                <button onClick={() => remove(bet.id)} className="mt-2 text-[11px] text-ink-3">Delete (entered by mistake)</button>
              </div>
            );
          })}
        </Card>
      ) : (
        <Empty>When you place a slip, tap <b>I placed this bet</b> on it. It appears here and settles automatically.</Empty>
      )}

      {transfers.length > 0 && (
        <>
          <SectionTitle>Deposits &amp; withdrawals</SectionTitle>
          <Card className="overflow-hidden">
            {transfers.map((t) => (
              <div key={t.id} className="flex items-center justify-between border-t border-border/60 px-5 py-3 text-sm first:border-t-0">
                <span>{t.type === "deposit" ? "Deposit" : "Withdrawal"} · {BOOKMAKERS[t.bookmaker]}</span>
                <span className="flex items-center gap-3">
                  <b>{t.type === "deposit" ? "+" : "−"}{tsh(t.amount)}</b>
                  <button onClick={() => remove(t.id)} className="text-[11px] text-ink-3" aria-label="Delete entry">✕</button>
                </span>
              </div>
            ))}
          </Card>
        </>
      )}
      <p className="mt-3 px-2 text-xs text-ink-3">Saved on this device only.</p>
    </div>
  );
}
