import type { ReactNode } from "react";
import { type Verdict, edge, odds as fmtOdds, pct, verdict } from "./lib";
import type { TierName } from "./types";

export const TIERS: Record<TierName, { title: string; range: string; blurb: string }> = {
  safe: { title: "Safe", range: "2–3 matches · odds 2.5–3.5", blurb: "Fewest legs, highest chance" },
  medium: { title: "Medium", range: "3–5 matches · odds 5–8", blurb: "Balanced risk and return" },
  big: { title: "Big", range: "4–8 matches · odds 10+", blurb: "Long shot, bigger payout" },
};

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-border bg-surface ${className}`}>{children}</section>;
}

/** Blended probability bar with the bookmaker's probability as a tick. */
export function ProbBar({ probability, market, label }: { probability: number; market?: number | null; label: string }) {
  const title = `${label}: ${pct(probability, 1)}${market != null ? ` · bookmaker ${pct(market, 1)}` : ""}`;
  return (
    <div className="relative h-2 w-full rounded-full bg-track" title={title} role="img" aria-label={title}>
      <div className="h-2 rounded-full bg-model" style={{ width: `${Math.max(probability * 100, 2)}%` }} />
      {market != null && (
        <div className="absolute -top-1 h-4 w-[3px] rounded-full bg-market ring-2 ring-surface"
          style={{ left: `calc(${market * 100}% - 1.5px)` }} />
      )}
    </div>
  );
}

export function Legend() {
  return (
    <div className="flex items-center gap-4 text-xs text-ink-2">
      <span className="flex items-center gap-1.5"><span className="h-2 w-4 rounded-full bg-model" /> Our probability</span>
      <span className="flex items-center gap-1.5"><span className="h-3 w-[3px] rounded-full bg-market" /> Bookmaker</span>
    </div>
  );
}

const VERDICTS: Record<Verdict, { label: string; icon: string; className: string }> = {
  value: { label: "Value bet", icon: "✓", className: "bg-good/12 text-good-ink border-good/40" },
  fair: { label: "Fair price", icon: "≈", className: "bg-warning/15 text-warning-ink border-warning/50" },
  none: { label: "No value", icon: "✕", className: "bg-critical/10 text-critical-ink border-critical/40" },
};

export function VerdictBadge({ probability, odds }: { probability: number; odds: number }) {
  const v = VERDICTS[verdict(probability, odds)];
  const e = edge(probability, odds);
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${v.className}`}>
      <span aria-hidden>{v.icon}</span>{v.label}
      <span className="font-medium opacity-80">{e >= 0 ? "+" : ""}{pct(e, 1)}</span>
    </span>
  );
}

export function OddsInput({ value, placeholder, onChange, label }: {
  value: string; placeholder: string; onChange: (v: string) => void; label: string;
}) {
  return (
    <input
      type="number" inputMode="decimal" step="0.01" min="1.01" aria-label={label}
      className="w-20 rounded-lg border border-border bg-surface-2 px-2 py-1.5 text-right text-sm font-semibold text-ink outline-none focus:border-accent"
      placeholder={placeholder} value={value} onChange={(e) => onChange(e.target.value)}
    />
  );
}

export function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div>
      <div className="text-[11px] font-medium uppercase tracking-wide text-ink-3">{label}</div>
      <div className="text-xl font-bold text-ink">{value}</div>
      {sub && <div className="text-xs text-ink-2">{sub}</div>}
    </div>
  );
}

export const parseOdds = (text: string) => {
  const value = parseFloat(text);
  return Number.isFinite(value) && value > 1 ? value : null;
};

export { fmtOdds };
