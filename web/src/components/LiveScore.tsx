import { type LegLive, type LiveMatch, legLive, onTrack, slipLive, useLiveMap, useLiveMatch, liveKey } from "../live";
import type { MarketKey } from "../types";

/** "● 63' 1–0" while playing, "FT 2–1" after; nothing before kick-off. */
export function LiveScoreChip({ match }: { match?: LiveMatch }) {
  if (!match || match.state === "pre") return null;
  if (match.state === "void") return <span data-live-chip className="text-[11px] font-semibold text-ink-3">Postponed</span>;
  return (
    <span data-live-chip className={`inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[11px] font-bold tabular-nums ${
      match.state === "in" ? "bg-good/15 text-good-ink" : "bg-surface-2 text-ink-2"}`}>
      {match.state === "in" && <span aria-hidden className="live-dot" />}
      {match.clock} {match.score[0]}–{match.score[1]}
    </span>
  );
}

const ICON: Record<LegLive, { text: string; label: string; className: string } | null> = {
  won: { text: "✓", label: "won", className: "bg-good text-white" },
  lost: { text: "✕", label: "lost", className: "bg-critical text-white" },
  live: null, pending: null, void: null,
};

/** A leg's live state: score chip plus ✓ / ✕, or a dot showing whether it is on track right now. */
export function LiveLeg({ home, away, market }: { home: string; away: string; market: MarketKey }) {
  const match = useLiveMatch(home, away);
  const state = legLive(market, match);
  if (!match || state === "pending") return null;
  const icon = ICON[state];
  return (
    <span data-live-leg data-live-state={state} className="inline-flex items-center gap-1.5">
      <LiveScoreChip match={match} />
      {icon ? (
        <span aria-label={icon.label} className={`inline-flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-bold ${icon.className}`}>{icon.text}</span>
      ) : state === "live" && (
        <span className={`text-[10px] font-semibold ${onTrack(market, match) ? "text-good-ink" : "text-warning-ink"}`}>
          {onTrack(market, match) ? "on track" : "not yet"}
        </span>
      )}
    </span>
  );
}

/** Live state of a whole slip (Flexi: `need` legs), or null when none of its matches has started. */
export function useSlipLive(legs: { home: string; away: string; market: MarketKey }[], need?: number) {
  const live = useLiveMap();
  const states = legs.map((l) => legLive(l.market, live[liveKey(l.home, l.away)]));
  const status = slipLive(states, need);
  return status === "pending" ? null : { status, won: states.filter((s) => s === "won").length, total: legs.length };
}

export function SlipLivePill({ legs, need, onDark = false }: { legs: { home: string; away: string; market: MarketKey }[]; need?: number; onDark?: boolean }) {
  const live = useSlipLive(legs, need);
  if (!live) return null;
  const tone = live.status === "won" ? "bg-good text-white" : live.status === "lost" ? "bg-critical text-white"
    : onDark ? "bg-white/15 text-white" : "bg-good/15 text-good-ink";
  const text = live.status === "won" ? "✓ Won" : live.status === "lost" ? "✕ Lost" : `● Live · ${live.won}/${live.total} won`;
  return <span data-slip-live={live.status} className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${tone}`}>{text}</span>;
}
