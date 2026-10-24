import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { TeamBadge } from "./badges";
import { type Verdict, edge, odds as fmtOdds, pct, verdict } from "./lib";
import type { TierName } from "./types";

export const TIERS: Record<TierName, { title: string; range: string; blurb: string }> = {
  safe: { title: "Safe", range: "2–4 matches · odds 2.5–3.5", blurb: "Fewest legs, highest chance" },
  medium: { title: "Medium", range: "3–6 matches · odds 3.5–8", blurb: "Balanced risk and return" },
  big: { title: "Big", range: "4–8 matches · odds 8–12", blurb: "Long shot, bigger payout" },
};

export function Card({ children, className = "", ...props }: ComponentPropsWithoutRef<"section">) {
  return <section {...props} className={`glass-light rounded-3xl ${className}`}>{children}</section>;
}

export function SectionTitle({ children, aside }: { children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-2 mt-6 flex items-baseline justify-between px-1 first:mt-0">
      <h2 className="text-[13px] font-semibold text-ink-2">{children}</h2>
      {aside && <span className="text-xs text-ink-3">{aside}</span>}
    </div>
  );
}

export function Segmented<T extends string>({ options, value, onChange }: {
  options: { id: T; label: string }[]; value: T; onChange: (id: T) => void;
}) {
  return (
    <div className="flex rounded-2xl bg-surface-2 p-1" role="tablist">
      {options.map((o) => (
        <button key={o.id} role="tab" aria-selected={value === o.id} onClick={() => onChange(o.id)}
          className={`flex-1 rounded-xl py-2 text-sm font-semibold transition ${value === o.id ? "bg-surface text-ink shadow-card" : "text-ink-3"}`}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Crest({ team, size = "md" }: { team: string; size?: "sm" | "md" }) {
  return <TeamBadge team={team} size={size === "sm" ? 26 : 40} />;
}

/** Blended probability bar with the bookmaker's probability as a tick. */
export function ProbBar({ probability, market, label }: { probability: number; market?: number | null; label: string }) {
  const title = `${label}: ${pct(probability, 1)}${market != null ? ` · bookmaker ${pct(market, 1)}` : ""}`;
  return (
    <div className="relative h-1.5 w-full rounded-full bg-track" title={title} role="img" aria-label={title}>
      <div className="h-1.5 rounded-full bg-model" style={{ width: `${Math.max(probability * 100, 2)}%` }} />
      {market != null && (
        <div className="absolute -top-[5px] h-4 w-[3px] rounded-full bg-market ring-2 ring-surface"
          style={{ left: `calc(${market * 100}% - 1.5px)` }} />
      )}
    </div>
  );
}

export function Legend() {
  return (
    <div className="flex items-center gap-4 text-xs text-ink-3">
      <span className="flex items-center gap-1.5"><span className="h-1.5 w-4 rounded-full bg-model" /> Our probability</span>
      <span className="flex items-center gap-1.5"><span className="h-3 w-[3px] rounded-full bg-market" /> Bookmaker</span>
    </div>
  );
}

const VERDICTS: Record<Verdict, { label: string; icon: string; className: string }> = {
  value: { label: "Bet this", icon: "✓", className: "bg-good/12 text-good-ink" },
  fair: { label: "Fair, skip", icon: "≈", className: "bg-warning/15 text-warning-ink" },
  none: { label: "Don't bet", icon: "✕", className: "bg-critical/10 text-critical-ink" },
};

export function VerdictBadge({ probability, odds }: { probability: number; odds: number }) {
  const v = VERDICTS[verdict(probability, odds)];
  const e = edge(probability, odds);
  return (
    <span className={`inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ${v.className}`}>
      <span aria-hidden>{v.icon}</span>{v.label}
      <span className="font-medium opacity-75">{e >= 0 ? "+" : ""}{pct(e, 1)}</span>
    </span>
  );
}

export const STATUS = {
  won: { icon: "✓", label: "Won", className: "bg-good/12 text-good-ink" },
  lost: { icon: "✕", label: "Lost", className: "bg-critical/10 text-critical-ink" },
  pending: { icon: "•", label: "Pending", className: "bg-surface-2 text-ink-3" },
} as const;

export function StatusPill({ status }: { status: keyof typeof STATUS }) {
  const s = STATUS[status];
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${s.className}`}>
      <span aria-hidden>{s.icon}</span>{s.label}
    </span>
  );
}

export function OddsInput({ value, placeholder, onChange, label }: {
  value: string; placeholder: string; onChange: (v: string) => void; label: string;
}) {
  return (
    <input
      type="number" inputMode="decimal" step="0.01" min="1.01" aria-label={label}
      className="w-[4.5rem] rounded-xl bg-surface-2 px-2.5 py-2 text-right text-sm font-semibold text-ink outline-none ring-accent placeholder:font-medium placeholder:text-ink-3 focus:ring-2"
      placeholder={placeholder} value={value} onChange={(e) => onChange(e.target.value)}
    />
  );
}

export function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div>
      <div className="text-[11px] font-medium text-ink-3">{label}</div>
      <div className="mt-0.5 whitespace-nowrap text-lg font-bold tracking-tight text-ink">{value}</div>
      {sub && <div className="text-[11px] text-ink-3">{sub}</div>}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <Card className="px-6 py-10 text-center text-sm leading-relaxed text-ink-2">{children}</Card>;
}

export const parseOdds = (text: string) => {
  const value = parseFloat(text);
  return Number.isFinite(value) && value > 1 ? value : null;
};

export { fmtOdds };

const isoDay = (date: Date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

export const todayIso = () => isoDay(new Date());

/** Compact date strip: weekday over date, TODAY highlighted, selected day underlined. */
export type DateMarker = "won" | "lost" | "mixed" | "pending";

export function DateStrip({ dates, selected, onSelect, markers }: {
  dates: string[]; selected?: string; onSelect: (date: string) => void; markers?: Record<string, DateMarker>;
}) {
  const today = todayIso();
  return (
    <div className="no-scrollbar -mx-4 flex overflow-x-auto border-b border-border/70 px-2" role="tablist">
      {dates.map((d) => {
        const date = new Date(`${d}T12:00:00`);
        const active = d === selected;
        return (
          <button key={d} role="tab" data-date={d} aria-selected={active} onClick={() => onSelect(d)}
            className={`relative shrink-0 px-3 pb-2.5 pt-1 text-center ${active ? "text-accent" : "text-ink-3"}`}>
            <div className="text-[11px] font-bold tracking-wide">
              {d === today ? "TODAY" : date.toLocaleDateString(undefined, { weekday: "short" }).toUpperCase()}
            </div>
            <div className="text-[11px] font-medium">{date.toLocaleDateString(undefined, { day: "numeric", month: "short" }).toUpperCase()}</div>
            {markers?.[d] && <span aria-label={`${markers[d]} bets`} className={`date-result-dot date-result-${markers[d]} mt-1`} />}
            {active && <span className="date-active-line absolute inset-x-2 bottom-0 h-[3px] rounded-full" />}
          </button>
        );
      })}
    </div>
  );
}
