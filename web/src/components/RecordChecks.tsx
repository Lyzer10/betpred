import { useState } from "react";
import { pct } from "../lib";
import type { ClvReport, ClvSummary, MarketKey, PairCheck, PairStatus, RealisedTier, TierName } from "../types";
import { Card, Empty, SectionTitle, TIERS } from "../ui";

const LEAGUE_NAMES: Record<string, string> = {
  EPL: "Premier League", LALIGA: "La Liga", SERIEA: "Serie A", BUNDES: "Bundesliga", LIGUE1: "Ligue 1",
};
const MARKET_NAMES: Partial<Record<MarketKey, string>> = {
  home_1up: "Home 1Up", away_1up: "Away 1Up", "over_0.5": "Over 0.5", "over_1.5": "Over 1.5", "over_2.5": "Over 2.5",
  "under_2.5": "Under 2.5", "under_3.5": "Under 3.5", home_win: "Home win", away_win: "Away win",
  double_1x: "Home or draw", double_x2: "Away or draw", double_12: "Home or away",
};
const CLV_JUDGE_LEGS = 200;
const signedPct = (x: number) => `${x >= 0 ? "+" : "−"}${pct(Math.abs(x), 1)}`;

/** Are Betpawa's prices moving towards our picks after we publish them? */
export function PriceTracking({ clv }: { clv?: ClvReport }) {
  return (
    <>
      <SectionTitle>Are we beating Betpawa's prices?</SectionTitle>
      {!clv || !("mean_clv" in clv) ? (
        <Empty>Prices are saved before every kick-off. The first results appear after the next matches.</Empty>
      ) : (
        <Card className="px-5 py-4" data-clv>
          <div className="text-base font-bold">
            Betpawa's price dropped after we picked it in {pct(clv.beat_close)} of {clv.legs} bets
          </div>
          <div className="mt-1 text-xs text-ink-2">Average price change in our favour: <b>{signedPct(clv.mean_clv)}</b></div>
          {clv.legs < CLV_JUDGE_LEGS && (
            <p data-clv-early className="mt-2 rounded-xl bg-surface-2 px-3 py-2 text-[11px] text-ink-2">
              Too early to judge: needs {CLV_JUDGE_LEGS} bets ({clv.legs} so far).
            </p>
          )}
          <p className="mt-2 text-[11px] leading-relaxed text-ink-3">
            When the price falls after we pick, the market moved towards us: the strongest early sign of a real edge,
            long before wins and losses can prove it.
          </p>
          <ClvTable title="League" rows={clv.league} name={(k) => LEAGUE_NAMES[k] ?? k} />
          <ClvTable title="Bet type" rows={clv.market} name={(k) => MARKET_NAMES[k as MarketKey] ?? k} />
        </Card>
      )}
    </>
  );
}

function ClvTable({ title, rows, name }: { title: string; rows: Record<string, ClvSummary>; name: (key: string) => string }) {
  const entries = Object.entries(rows).sort((a, b) => b[1].legs - a[1].legs);
  return (
    <table className="mt-3 w-full text-xs">
      <thead>
        <tr className="text-left text-[11px] text-ink-3">
          <th className="pb-1 font-medium">{title}</th><th className="pb-1 text-right font-medium">Bets</th>
          <th className="pb-1 text-right font-medium">Avg</th><th className="pb-1 text-right font-medium">Dropped</th>
        </tr>
      </thead>
      <tbody>
        {entries.map(([key, row]) => (
          <tr key={key} className="border-t border-border/60">
            <td className="py-1.5">{name(key)}</td><td className="py-1.5 text-right">{row.legs}</td>
            <td className="py-1.5 text-right">{signedPct(row.mean_clv)}</td><td className="py-1.5 text-right">{pct(row.beat_close)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const PAIR_PILL: Record<PairStatus, { label: string; className: string }> = {
  ok: { label: "✓ OK", className: "bg-good/15 text-good-ink" },
  watch: { label: "≈ Watch", className: "bg-warning/15 text-warning-ink" },
  paused: { label: "⏸ Paused", className: "bg-critical/15 text-critical-ink" },
  insufficient: { label: "• Collecting", className: "bg-surface-2 text-ink-3" },
};
const is1Up = (market: string) => market.endsWith("1up");

/** Each league x bet type: what we said vs what happened. Paused ones are kept out of slips. */
export function BetTypeChecks({ pairs }: { pairs?: PairCheck[] }) {
  const [all, setAll] = useState(false);
  if (!pairs?.length) return null;
  const sorted = [...pairs].sort((a, b) => Number(is1Up(b.market)) - Number(is1Up(a.market)) || b.n - a.n);
  const shown = all ? sorted : sorted.filter((p) => p.status !== "insufficient");
  return (
    <>
      <SectionTitle>Is each bet type behaving?</SectionTitle>
      <Card className="overflow-hidden" data-bet-types>
        <p className="px-5 pt-4 text-[11px] leading-relaxed text-ink-3">
          Our published chance against what really happened. <b>Paused</b> bet types won clearly less than we said and are
          kept out of slips until they recover. Winning more than predicted is never a problem.
        </p>
        {shown.length === 0 && <p className="px-5 py-3 text-xs text-ink-2">Each bet type needs 30 finished matches first.</p>}
        {shown.map((p) => (
          <div key={`${p.league}-${p.market}`} data-bet-type className="flex items-center justify-between gap-3 border-t border-border/60 px-5 py-3 first:border-t-0">
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold">{LEAGUE_NAMES[p.league] ?? p.league} · {MARKET_NAMES[p.market] ?? p.market}</div>
              <div className="text-[11px] text-ink-3">said {pct(p.predicted)} · won {pct(p.actual)} · {p.n} matches</div>
            </div>
            <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold ${PAIR_PILL[p.status].className}`}>{PAIR_PILL[p.status].label}</span>
          </div>
        ))}
        {sorted.length !== shown.length || all ? (
          <button className="w-full border-t border-border/60 px-5 py-3 text-xs font-semibold text-accent" onClick={() => setAll(!all)}>
            {all ? "Show only bet types with enough data" : `Show all ${sorted.length}`}
          </button>
        ) : null}
      </Card>
    </>
  );
}

/** Settled published slips, 1 unit each at the published odds. */
export function RealResults({ realised }: { realised?: Record<TierName, RealisedTier> }) {
  if (!realised) return null;
  const tiers = (["safe", "medium", "big"] as TierName[]).filter((t) => realised[t]?.settled);
  return (
    <>
      <SectionTitle>Real results (1 unit per slip)</SectionTitle>
      {tiers.length ? (
        <Card className="px-5 py-4" data-realised>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] text-ink-3">
                <th className="pb-2 font-medium">Tier</th><th className="pb-2 text-right font-medium">Won</th>
                <th className="pb-2 text-right font-medium">Expected</th><th className="pb-2 text-right font-medium">Profit</th>
              </tr>
            </thead>
            <tbody>
              {tiers.map((t) => {
                const r = realised[t];
                return (
                  <tr key={t} className="border-t border-border/60">
                    <td className="py-2 font-semibold">{TIERS[t].title}</td>
                    <td className="py-2 text-right">{r.won}/{r.settled}</td>
                    <td className="py-2 text-right">{r.predicted.toFixed(1)}</td>
                    <td className={`py-2 text-right font-semibold ${r.profit >= 0 ? "text-good-ink" : "text-critical-ink"}`}>
                      {r.profit >= 0 ? "+" : "−"}{Math.abs(r.profit).toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p className="mt-2 text-[11px] text-ink-3">"Expected" is how many we should have won by our own chances. Small numbers swing a lot.</p>
        </Card>
      ) : (
        <Empty>Appears once published slips have settled.</Empty>
      )}
    </>
  );
}
