import { odds, pct } from "../lib";
import type { HistoryEntry, Predictions, TierName } from "../types";
import { Card, Empty, SectionTitle, Stat, StatusPill, TIERS } from "../ui";
import { BetTypeChecks, PriceTracking, RealResults } from "../components/RecordChecks";

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
  const health = data.health;
  const HEALTH_LABEL = { ok: "✓ Healthy", watch: "≈ Watch", warning: "⚠ Under review", insufficient: "• Collecting data" } as const;
  const HEALTH_TONE = { ok: "text-good-ink", watch: "text-warning-ink", warning: "text-critical-ink", insufficient: "text-ink-3" } as const;
  return (
    <div>
      {health && (
        <>
          <SectionTitle>Model health</SectionTitle>
          <Card className="px-5 py-4">
            <div className={`text-base font-bold ${HEALTH_TONE[health.status]}`}>{HEALTH_LABEL[health.status]}</div>
            <ul className="mt-2 space-y-1.5">
              {health.checks.map((c) => (
                <li key={c.name} className="flex items-start justify-between gap-3 text-xs">
                  <span className="text-ink-2"><b className="capitalize text-ink">{c.name}</b> · {c.detail}</span>
                  <span className={`shrink-0 font-semibold ${HEALTH_TONE[c.status]}`}>{HEALTH_LABEL[c.status].split(" ").slice(1).join(" ")}</span>
                </li>
              ))}
            </ul>
            <p className="mt-2 text-[11px] text-ink-3">Checked every update against the bookmakers and real results. "Under review" halves every stake automatically.</p>
          </Card>
        </>
      )}
      <PriceTracking clv={data.clv} />
      <BetTypeChecks pairs={health?.pairs} />
      <RealResults realised={data.realised} />

      <SectionTitle aside={live.matches ? `${live.matches} matches` : undefined}>Live predictions</SectionTitle>
      {live.matches ? (
        <Card className="grid grid-cols-3 gap-3 px-5 py-4">
          <Stat label="Main call right" value={pct(live.result_hit_rate ?? 0)} sub="home / draw / away" />
          <Stat label="70%+ picks hit" value={live.confident_hit_rate != null ? pct(live.confident_hit_rate) : "–"} sub={`${live.confident_picks} picks`} />
          <Stat label="vs bookmaker" value={live.log_loss != null && live.market_log_loss != null ? (live.log_loss <= live.market_log_loss ? "Ahead" : "Behind") : "–"}
            sub={live.log_loss != null ? `log loss ${live.log_loss.toFixed(3)} v ${live.market_log_loss?.toFixed(3)}` : undefined} />
          <div className="col-span-3 border-t border-border/60 pt-3">
            <Stat label="Value bets at Betpawa prices (1 unit each)"
              value={live.value_bets ? `${live.value_roi != null && live.value_roi >= 0 ? "+" : ""}${pct(live.value_roi ?? 0, 1)} return` : "–"}
              sub={live.value_bets ? `${live.value_bets_won}/${live.value_bets} won` : "none settled yet"} />
          </div>
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
