import { useEffect, useState } from "react";
import { loadPicks, storePicks, usePredictions } from "./lib";
import type { SavedPick } from "./types";
import { Card } from "./ui";
import { Matches } from "./views/Matches";
import { MyPicks, Record } from "./views/Record";
import { Slips } from "./views/Slips";

const TABS = [
  { id: "slips", label: "Slips", icon: "M4 6h16M4 12h16M4 18h10" },
  { id: "matches", label: "Matches", icon: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 4 3.5 2.5-1.3 4h-4.4l-1.3-4Z" },
  { id: "picks", label: "My picks", icon: "M5 12l4 4L19 6" },
  { id: "record", label: "Record", icon: "M4 19V9m6 10V5m6 14v-7m4 7H2" },
] as const;

type Tab = (typeof TABS)[number]["id"];

/** Routes live in the URL hash (#matches/3) so screens can be bookmarked and shared. */
function readRoute(): { tab: Tab; fixtureId: number | null } {
  const [name, id] = window.location.hash.replace(/^#\/?/, "").split("/");
  const tab = (TABS.find((t) => t.id === name)?.id ?? "slips") as Tab;
  return { tab, fixtureId: id !== undefined && /^\d+$/.test(id) ? Number(id) : null };
}

export default function App() {
  const { data, error } = usePredictions();
  const [route, setRoute] = useState(readRoute);
  useEffect(() => {
    const onHash = () => setRoute(readRoute());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  const { tab, fixtureId } = route;
  const go = (hash: string) => { window.location.hash = hash; window.scrollTo(0, 0); };
  const [picks, setPicks] = useState<SavedPick[]>(loadPicks);
  const updatePicks = (next: SavedPick[]) => { setPicks(next); storePicks(next); };

  return (
    <div className="mx-auto min-h-screen max-w-xl px-4 pb-28">
      <header className="flex items-end justify-between pb-4 pt-6">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">PL Predictor</h1>
          <p className="text-xs text-ink-3">
            {data ? `Updated ${new Date(data.generated_at).toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}` : "Premier League"}
          </p>
        </div>
        <span className="rounded-full border border-border px-2.5 py-1 text-[11px] font-medium text-ink-2">Premier League</span>
      </header>

      {error && <Card className="p-6 text-center text-sm text-critical-ink">Could not load predictions ({error}).</Card>}
      {!data && !error && <Card className="p-6 text-center text-sm text-ink-3">Loading predictions…</Card>}
      {data && tab === "slips" && <Slips data={data} />}
      {data && tab === "matches" && <Matches fixtures={data.fixtures} selected={fixtureId} onSelect={(id) => go(id === null ? "matches" : `matches/${id}`)}
        onSave={(p) => updatePicks([p, ...picks])} />}
      {data && tab === "picks" && <MyPicks data={data} picks={picks} onRemove={(id) => updatePicks(picks.filter((p) => p.id !== id))} />}
      {data && tab === "record" && <Record data={data} />}

      <p className="mt-8 text-center text-[11px] leading-relaxed text-ink-3">
        Probabilities, not guarantees. No model removes risk: only stake what you can afford to lose. 18+.
      </p>

      <nav className="fixed inset-x-0 bottom-0 border-t border-border bg-surface/95 backdrop-blur" style={{ paddingBottom: "env(safe-area-inset-bottom)" }}>
        <div className="mx-auto grid max-w-xl grid-cols-4">
          {TABS.map((t) => (
            <button key={t.id} onClick={() => go(t.id)}
              className={`flex flex-col items-center gap-1 py-2.5 text-[11px] font-semibold ${tab === t.id ? "text-accent" : "text-ink-3"}`}
              aria-current={tab === t.id ? "page" : undefined}>
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <path d={t.icon} />
              </svg>
              {t.label}
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}
