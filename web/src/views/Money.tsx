import { useEffect, useState } from "react";
import { currentPushCode, enablePush, pushSupported } from "../push";
import { BOOKMAKERS, type Bookmaker, DEFAULT_STAKING, type Ledger, type PlacedBet, type StakingMode, type Transfer, betStatus, isBet, isTransfer, newId, payout, settledSlips, summarise } from "../ledger";
import { STAKING, losingStreakChance, odds, pct, tsh } from "../lib";
import type { Result } from "../types";
import { Card, type DateMarker, DateStrip, Empty, SectionTitle, Segmented, Stat, StatusPill, TIERS } from "../ui";

/** Safe-slip win rate from the backtest (about 37%), used for the risk estimate. */
const SAFE_WIN_RATE = 0.37;
const BETS_PER_MONTH = 30;

function StakingCard({ ledger, balance, pilotSettled, onChange }: { ledger: Ledger; balance: number; pilotSettled: number; onChange: (ledger: Ledger) => void }) {
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
      {pilotSettled < STAKING.pilotSlips && (
        <p className="mt-2 rounded-xl bg-warning/15 px-3 py-2 text-[11px] leading-relaxed text-warning-ink">
          Pilot phase: until {STAKING.pilotSlips} of your slips have settled ({pilotSettled}/{STAKING.pilotSlips} so far), no slip stakes more than {pct(STAKING.pilotCap)} of your balance,
          whatever you choose above. The system's edge is not yet proven with your own bets.
        </p>
      )}
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

const monthLabel = (month: string) =>
  new Date(`${month}-15T12:00:00`).toLocaleDateString(undefined, { month: "long", year: "numeric" });
const shiftMonth = (month: string, by: number) => {
  const d = new Date(`${month}-15T12:00:00`);
  d.setMonth(d.getMonth() + by);
  return d.toISOString().slice(0, 7);
};

/** One month of placed bets: totals, a strip of days with bets, and the chosen day's bets as a table. */
function PlacedBets({ bets, results, onDelete }: { bets: PlacedBet[]; results: Result[]; onDelete: (id: string) => void }) {
  const sortedDays = bets.map((b) => b.day).sort();
  const latest = sortedDays[sortedDays.length - 1];
  const [month, setMonth] = useState(latest.slice(0, 7));
  const inMonth = bets.filter((b) => b.day.startsWith(month));
  const days = [...new Set(inMonth.map((b) => b.day))].sort();
  const [picked, setPicked] = useState<string | undefined>();
  const day = picked && days.includes(picked) ? picked : days[days.length - 1];
  const [open, setOpen] = useState<string | null>(null);
  const status = (bet: PlacedBet) => betStatus(bet, results).status;

  const settled = inMonth.filter((b) => status(b) !== "pending");
  const staked = inMonth.reduce((a, b) => a + b.stake, 0);
  const returned = inMonth.filter((b) => status(b) === "won").reduce((a, b) => a + payout(b), 0);
  const profit = returned - settled.reduce((a, b) => a + b.stake, 0);
  const pending = inMonth.length - settled.length;
  const markers: Record<string, DateMarker> = Object.fromEntries(days.map((d) => {
    const s = inMonth.filter((b) => b.day === d).map(status);
    const marker: DateMarker = s.includes("pending") ? "pending" : s.every((x) => x === "won") ? "won" : s.every((x) => x === "lost") ? "lost" : "mixed";
    return [d, marker];
  }));
  const changeMonth = (by: number) => { setMonth(shiftMonth(month, by)); setPicked(undefined); setOpen(null); };

  return (
    <div data-placed-bets>
      <Card className="px-5 py-4" data-month-summary>
        <div className="flex items-center justify-between">
          <button aria-label="Previous month" disabled={month <= sortedDays[0].slice(0, 7)} onClick={() => changeMonth(-1)}
            className="rounded-full px-3 py-1 text-lg font-bold text-ink-2 disabled:opacity-30">‹</button>
          <div className="text-sm font-semibold">{monthLabel(month)}</div>
          <button aria-label="Next month" disabled={month >= latest.slice(0, 7)} onClick={() => changeMonth(1)}
            className="rounded-full px-3 py-1 text-lg font-bold text-ink-2 disabled:opacity-30">›</button>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-3">
          <Stat label="Bets placed" value={String(inMonth.length)} sub={pending ? `${pending} pending` : undefined} />
          <Stat label="Staked" value={tsh(staked)} />
          <Stat label="Returned" value={tsh(returned)} />
          <Stat label="Profit (settled)" value={signed(profit)}
            sub={settled.length ? `${settled.filter((b) => status(b) === "won").length} of ${settled.length} won` : "nothing settled"} />
        </div>
      </Card>

      {days.length ? (
        <>
          <div className="mt-3"><DateStrip dates={days} selected={day} onSelect={setPicked} markers={markers} /></div>
          <Card className="mt-3 overflow-hidden" data-day-bets>
            <div className="grid grid-cols-[minmax(0,1fr)_auto_4.75rem] gap-x-3 border-b border-border/60 px-4 py-2 text-[10px] font-semibold uppercase tracking-wide text-ink-3">
              <span>Slip</span><span className="text-right">Stake · odds</span><span className="text-right">Result</span>
            </div>
            {inMonth.filter((b) => b.day === day).map((bet) => {
              const { status: s, legs } = betStatus(bet, results);
              return (
                <div key={bet.id} data-bet-row className="border-t border-border/60 first:border-t-0">
                  <button className="grid w-full grid-cols-[minmax(0,1fr)_auto_4.75rem] items-center gap-x-3 px-4 py-3 text-left"
                    aria-expanded={open === bet.id} onClick={() => setOpen(open === bet.id ? null : bet.id)}>
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-semibold">{TIERS[bet.tier].title}</span>
                      <span className="block truncate text-[11px] text-ink-3">{BOOKMAKERS[bet.bookmaker]}{bet.flexi ? ` · Flexi ${bet.flexi.minCorrect}/${bet.legs.length}` : ""}</span>
                    </span>
                    <span className="text-right">
                      <span data-bet-stake={bet.stake} className="block text-sm font-semibold">{tsh(bet.stake)}</span>
                      <span className="block text-[11px] text-ink-3">@ {odds(bet.odds)}</span>
                    </span>
                    <span className="flex flex-col items-end gap-0.5">
                      <StatusPill status={s} />
                      <span className="whitespace-nowrap text-[11px] font-semibold text-ink-2">
                        {s === "won" ? `+${tsh(payout(bet))}` : s === "lost" ? "–" : `pays ${tsh(payout(bet))}`}
                      </span>
                    </span>
                  </button>
                  {open === bet.id && (
                    <div className="px-4 pb-3">
                      <ul className="space-y-1">
                        {bet.legs.map((l, i) => (
                          <li key={i} className="flex items-center gap-2 text-xs text-ink-2">
                            <span className={`w-3 font-bold ${legs[i] === true ? "text-good-ink" : legs[i] === false ? "text-critical-ink" : "text-ink-3"}`}>
                              {legs[i] === true ? "✓" : legs[i] === false ? "✕" : "•"}
                            </span>
                            <span className="truncate">{l.label} · {l.home} v {l.away}</span>
                          </li>
                        ))}
                      </ul>
                      <button onClick={() => onDelete(bet.id)} className="mt-2 text-[11px] text-ink-3">Delete (entered by mistake)</button>
                    </div>
                  )}
                </div>
              );
            })}
          </Card>
        </>
      ) : (
        <div className="mt-3"><Empty>No bets placed in {monthLabel(month)}.</Empty></div>
      )}
    </div>
  );
}

/** Deposits and withdrawals, kept apart from bets, newest month first. */
function Transfers({ transfers, onDelete }: { transfers: Transfer[]; onDelete: (id: string) => void }) {
  const [shown, setShown] = useState(false);
  const months = [...new Set(transfers.map((t) => t.placedAt.slice(0, 7)))].sort().reverse();
  const [month, setMonth] = useState(months[0]);
  const list = transfers.filter((t) => t.placedAt.startsWith(month)).slice().reverse();
  return (
    <Card className="mt-3 overflow-hidden" data-transfers>
      <button className="flex w-full items-center justify-between px-5 py-3.5 text-sm font-semibold" aria-expanded={shown} onClick={() => setShown(!shown)}>
        <span>Deposits &amp; withdrawals</span><span className="text-ink-3">{shown ? "▴" : `${transfers.length} ▾`}</span>
      </button>
      {shown && (
        <>
          {months.length > 1 && (
            <div className="px-5 pb-2">
              <Segmented options={months.slice(0, 3).map((m) => ({ id: m, label: monthLabel(m).split(" ")[0] }))} value={month} onChange={setMonth} />
            </div>
          )}
          {list.map((t) => (
            <div key={t.id} data-transfer-row className="flex items-center justify-between border-t border-border/60 px-5 py-3 text-sm">
              <span>{t.type === "deposit" ? "Deposit" : "Withdrawal"} · {BOOKMAKERS[t.bookmaker]}
                <span className="block text-[11px] text-ink-3">{new Date(t.placedAt).toLocaleDateString(undefined, { day: "numeric", month: "short" })}</span>
              </span>
              <span className="flex items-center gap-3">
                <b>{t.type === "deposit" ? "+" : "−"}{tsh(t.amount)}</b>
                <button onClick={() => onDelete(t.id)} className="text-[11px] text-ink-3" aria-label="Delete entry">✕</button>
              </span>
            </div>
          ))}
        </>
      )}
    </Card>
  );
}

/** Turn on phone notifications ("today's bets are final"); the code links this phone to the daily run. */
function NotificationsCard() {
  const [code, setCode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  useEffect(() => { currentPushCode().then(setCode).catch(() => setCode(null)); }, []);
  const turnOn = async () => {
    setError(null);
    const result = await enablePush().catch((reason) => ({ error: String(reason), code: undefined }));
    if (result.code) setCode(result.code); else setError(result.error ?? "Could not turn on notifications.");
  };
  const copy = async () => {
    if (!code) return;
    await navigator.clipboard.writeText(code).then(() => setCopied(true)).catch(() => setCopied(false));
  };
  return (
    <Card className="px-5 py-4" data-notifications>
      <div className="text-sm font-semibold">Notifications</div>
      {code ? (
        <>
          <p className="mt-1 text-xs leading-relaxed text-ink-2">✓ On for this phone. One last step, only once: copy this code and send it to Claude, so the daily run knows where to notify you.</p>
          <textarea readOnly value={code} aria-label="Notification code" className="mt-2 h-16 w-full resize-none rounded-xl bg-surface-2 px-3 py-2 text-[10px] text-ink-2 outline-none" />
          <button onClick={copy} className="mt-2 w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white">{copied ? "Copied ✓" : "Copy code"}</button>
        </>
      ) : (
        <>
          <p className="mt-1 text-xs leading-relaxed text-ink-2">Get a message when today's slips are final, about 45 minutes before the first match.
            {pushSupported() ? "" : " On iPhone, add BetPredz to the Home Screen first."}</p>
          <button onClick={turnOn} className="mt-3 w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white">Turn on notifications</button>
        </>
      )}
      {error && <p className="mt-2 text-xs text-critical-ink">{error}</p>}
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
  const transfers = ledger.entries.filter(isTransfer);
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
      <StakingCard ledger={ledger} balance={totals[0].balance} pilotSettled={settledSlips(ledger, results)} onChange={onChange} />

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
        <PlacedBets bets={bets} results={results} onDelete={remove} />
      ) : (
        <Empty>When you place a slip, tap <b>I placed this bet</b> on it. It appears here and settles automatically.</Empty>
      )}
      {transfers.length > 0 && <Transfers transfers={transfers} onDelete={remove} />}
      <SectionTitle>Notifications</SectionTitle>
      <NotificationsCard />
      <p className="mt-3 px-2 text-xs text-ink-3">Saved on this device only.</p>
    </div>
  );
}
