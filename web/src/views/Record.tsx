import { edge, odds, pct, settle } from "../lib";
import type { HistoryEntry, Predictions, SavedPick, TierName } from "../types";
import { Card, Stat, TIERS } from "../ui";

const STATUS = {
  won: { icon: "✓", label: "Won", className: "text-good-ink" },
  lost: { icon: "✕", label: "Lost", className: "text-critical-ink" },
  pending: { icon: "•", label: "Pending", className: "text-ink-3" },
} as const;

export function MyPicks({ data, picks, onRemove }: { data: Predictions; picks: SavedPick[]; onRemove: (id: string) => void }) {
  const settled = picks.map((p) => ({ pick: p, won: settle(data.results, p) }));
  const done = settled.filter((s) => s.won !== null);
  const profit = done.reduce((sum, s) => sum + (s.won ? s.pick.odds - 1 : -1) * s.pick.stake, 0);
  const staked = done.reduce((sum, s) => sum + s.pick.stake, 0);
  const expected = picks.reduce((sum, p) => sum + edge(p.probability, p.odds), 0) / Math.max(picks.length, 1);
  return (
    <div className="space-y-4">
      <Card className="grid grid-cols-3 gap-3 p-4">
        <Stat label="Picks" value={String(picks.length)} sub={`${done.length} settled`} />
        <Stat label="Profit" value={`${profit >= 0 ? "+" : ""}${profit.toFixed(2)}`} sub={staked ? `ROI ${pct(profit / staked, 1)}` : "units"} />
        <Stat label="Avg edge" value={picks.length ? `${expected >= 0 ? "+" : ""}${pct(expected, 1)}` : "–"} sub="expected" />
      </Card>
      {!picks.length && (
        <Card className="p-6 text-center text-sm text-ink-2">
          Open a match, type your bookmaker's odds next to a market and tap <b>Save</b>. Picks settle automatically when results come in.
        </Card>
      )}
      {settled.length > 0 && (
        <Card>
          <ul className="divide-y divide-border">
            {settled.map(({ pick, won }) => {
              const s = STATUS[won === null ? "pending" : won ? "won" : "lost"];
              return (
                <li key={pick.id} className="flex items-center gap-3 px-4 py-3">
                  <span className={`w-14 text-xs font-semibold ${s.className}`}><span aria-hidden>{s.icon}</span> {s.label}</span>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-semibold">{pick.label}</div>
                    <div className="truncate text-xs text-ink-3">{pick.home} v {pick.away} · {pct(pick.probability)} @ {odds(pick.odds)}</div>
                  </div>
                  <button onClick={() => onRemove(pick.id)} className="text-xs text-ink-3 hover:text-critical-ink" aria-label="Remove pick">Remove</button>
                </li>
              );
            })}
          </ul>
        </Card>
      )}
      <p className="px-1 text-xs text-ink-3">Picks are stored on this device only.</p>
    </div>
  );
}

function HistoryRow({ entry }: { entry: HistoryEntry }) {
  const s = STATUS[entry.status];
  return (
    <li className="flex items-center gap-3 px-4 py-3">
      <span className={`w-16 text-xs font-semibold ${s.className}`}><span aria-hidden>{s.icon}</span> {s.label}</span>
      <div className="min-w-0 flex-1">
        <div className="text-sm font-semibold">{TIERS[entry.tier].title} · odds {odds(entry.total_odds)}</div>
        <div className="truncate text-xs text-ink-3">{entry.legs.map((l) => `${l.home} v ${l.away}: ${l.label}`).join(" · ")}</div>
      </div>
      <span className="text-xs text-ink-2">{pct(entry.win_probability)}</span>
    </li>
  );
}

export function Record({ data }: { data: Predictions }) {
  const tiers: TierName[] = ["safe", "medium", "big"];
  // Newest round first; within a round, Safe -> Medium -> Big.
  const history = [...data.history].sort((a, b) =>
    b.round.localeCompare(a.round) || tiers.indexOf(a.tier) - tiers.indexOf(b.tier));
  return (
    <div className="space-y-4">
      <Card className="p-4">
        <h3 className="text-sm font-semibold">Backtest · 2024/25 to today</h3>
        <p className="mt-1 text-xs text-ink-3">Every round replayed using only data available before kickoff.</p>
        <table className="mt-3 w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-ink-3">
              <th className="pb-2 font-medium">Tier</th>
              <th className="pb-2 text-right font-medium">Slips</th>
              <th className="pb-2 text-right font-medium">Avg odds</th>
              <th className="pb-2 text-right font-medium">Predicted</th>
              <th className="pb-2 text-right font-medium">Won</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {tiers.map((tier) => {
              const b = data.backtest[tier];
              return b ? (
                <tr key={tier}>
                  <td className="py-2 font-semibold">{TIERS[tier].title}</td>
                  <td className="py-2 text-right">{b.slips}</td>
                  <td className="py-2 text-right">{odds(b.average_odds)}</td>
                  <td className="py-2 text-right text-ink-2">{pct(b.predicted_win_rate, 1)}</td>
                  <td className="py-2 text-right font-bold">{pct(b.win_rate, 1)}</td>
                </tr>
              ) : null;
            })}
          </tbody>
        </table>
      </Card>
      <Card>
        <h3 className="px-4 pt-4 text-sm font-semibold">Live slips</h3>
        <p className="px-4 text-xs text-ink-3">Published before kickoff and never edited afterwards.</p>
        {history.length ? <ul className="mt-2 divide-y divide-border">{history.map((e) => <HistoryRow key={`${e.round}-${e.tier}`} entry={e} />)}</ul>
          : <p className="p-4 text-sm text-ink-2">No live slips yet.</p>}
      </Card>
    </div>
  );
}
