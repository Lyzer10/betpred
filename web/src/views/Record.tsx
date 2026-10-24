import { edge, odds, pct, settle } from "../lib";
import type { HistoryEntry, Predictions, SavedPick, TierName } from "../types";
import { Card, Empty, SectionTitle, Stat, StatusPill, TIERS } from "../ui";

export function MyPicks({ data, picks, onRemove }: { data: Predictions; picks: SavedPick[]; onRemove: (id: string) => void }) {
  const settled = picks.map((p) => ({ pick: p, won: settle(data.results, p) }));
  const done = settled.filter((s) => s.won !== null);
  const profit = done.reduce((sum, s) => sum + (s.won ? s.pick.odds - 1 : -1) * s.pick.stake, 0);
  const staked = done.reduce((sum, s) => sum + s.pick.stake, 0);
  const expected = picks.reduce((sum, p) => sum + edge(p.probability, p.odds), 0) / Math.max(picks.length, 1);
  return (
    <div className="space-y-4">
      <Card className="grid grid-cols-3 gap-3 px-5 py-4">
        <Stat label="Picks" value={String(picks.length)} sub={`${done.length} settled`} />
        <Stat label="Profit (units)" value={`${profit >= 0 ? "+" : ""}${profit.toFixed(2)}`} sub={staked ? `ROI ${pct(profit / staked, 1)}` : "1 unit per pick"} />
        <Stat label="Avg edge" value={picks.length ? `${expected >= 0 ? "+" : ""}${pct(expected, 1)}` : "–"} sub="when saved" />
      </Card>
      {!picks.length ? (
        <Empty>Open a match, type your bookmaker's odds next to a market and tap <b>Save to My picks</b>. Picks settle automatically when results come in.</Empty>
      ) : (
        <Card className="overflow-hidden">
          {settled.map(({ pick, won }) => (
            <div key={pick.id} className="flex items-center gap-3 border-t border-border/60 px-5 py-3.5 first:border-t-0">
              <StatusPill status={won === null ? "pending" : won ? "won" : "lost"} />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-semibold">{pick.label}</div>
                <div className="truncate text-xs text-ink-3">{pick.home} v {pick.away} · {pct(pick.probability)} @ {odds(pick.odds)}</div>
              </div>
              <button onClick={() => onRemove(pick.id)} className="text-xs text-ink-3" aria-label={`Remove ${pick.label}`}>Remove</button>
            </div>
          ))}
        </Card>
      )}
      <p className="px-2 text-xs text-ink-3">Picks are stored on this device only.</p>
    </div>
  );
}

function HistoryRow({ entry }: { entry: HistoryEntry }) {
  return (
    <div className="flex items-center gap-3 border-t border-border/60 px-5 py-3.5 first:border-t-0">
      <StatusPill status={entry.status} />
      <div className="min-w-0 flex-1">
        <div className="text-sm font-semibold">{TIERS[entry.tier].title} · odds {odds(entry.total_odds)}</div>
        <div className="truncate text-xs text-ink-3">{entry.legs.map((l) => `${l.home} v ${l.away}`).join(" · ")}</div>
      </div>
      <span className="text-xs font-medium text-ink-2">{pct(entry.win_probability)}</span>
    </div>
  );
}

export function Record({ data }: { data: Predictions }) {
  const tiers: TierName[] = ["safe", "medium", "big"];
  // Newest round first; within a round, Safe -> Medium -> Big.
  const history = [...data.history].sort((a, b) =>
    b.round.localeCompare(a.round) || tiers.indexOf(a.tier) - tiers.indexOf(b.tier));
  const live = data.live_record;
  const settledSlips = data.history.filter((h) => h.status !== "pending");
  return (
    <div>
      <SectionTitle aside={live.matches ? `${live.matches} matches` : undefined}>Live predictions</SectionTitle>
      {live.matches ? (
        <Card className="grid grid-cols-3 gap-3 px-5 py-4">
          <Stat label="Main call right" value={pct(live.result_hit_rate ?? 0)} sub="home / draw / away" />
          <Stat label="70%+ picks hit" value={live.confident_hit_rate != null ? pct(live.confident_hit_rate) : "–"} sub={`${live.confident_picks} picks`} />
          <Stat label="vs bookmaker" value={live.log_loss != null && live.market_log_loss != null ? (live.log_loss <= live.market_log_loss ? "Ahead" : "Behind") : "–"}
            sub={live.log_loss != null ? `log loss ${live.log_loss.toFixed(3)} v ${live.market_log_loss?.toFixed(3)}` : undefined} />
        </Card>
      ) : (
        <Empty>Live accuracy appears here once the first predicted matches have finished.</Empty>
      )}

      <SectionTitle aside={settledSlips.length ? `${settledSlips.filter((h) => h.status === "won").length}/${settledSlips.length} won` : undefined}>
        Live slips
      </SectionTitle>
      {history.length ? <Card className="overflow-hidden">{history.map((e) => <HistoryRow key={`${e.round}-${e.tier}`} entry={e} />)}</Card>
        : <Empty>No live slips yet.</Empty>}

      <SectionTitle aside="2024/25 to today">Backtest</SectionTitle>
      <Card className="px-5 py-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] text-ink-3">
              <th className="pb-2 font-medium">Tier</th>
              <th className="pb-2 text-right font-medium">Slips</th>
              <th className="pb-2 text-right font-medium">Avg odds</th>
              <th className="pb-2 text-right font-medium">Predicted</th>
              <th className="pb-2 text-right font-medium">Won</th>
            </tr>
          </thead>
          <tbody>
            {tiers.map((tier) => {
              const b = data.backtest[tier];
              return b ? (
                <tr key={tier} className="border-t border-border/60">
                  <td className="py-2.5 font-semibold">{TIERS[tier].title}</td>
                  <td className="py-2.5 text-right text-ink-2">{b.slips}</td>
                  <td className="py-2.5 text-right text-ink-2">{odds(b.average_odds)}</td>
                  <td className="py-2.5 text-right text-ink-2">{pct(b.predicted_win_rate, 1)}</td>
                  <td className="py-2.5 text-right font-bold">{pct(b.win_rate, 1)}</td>
                </tr>
              ) : null;
            })}
          </tbody>
        </table>
        <p className="mt-3 text-[11px] leading-relaxed text-ink-3">Every round replayed using only information available before kickoff.</p>
      </Card>
    </div>
  );
}
