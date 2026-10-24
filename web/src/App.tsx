import { useEffect, useState } from "react";
import { loadPicks, storePicks, usePredictions } from "./lib";
import type { SavedPick } from "./types";
import { Empty } from "./ui";
import { History } from "./views/History";
import { Matches } from "./views/Matches";
import { MyPicks, Record } from "./views/Record";
import { Slips } from "./views/Slips";

const TABS = [
  { id: "slips", label: "Slips", icon: "M5 4h14v16l-3-2-2 2-2-2-2 2-2-2-3 2Z M9 9h6 M9 13h6" },
  { id: "matches", label: "Matches", icon: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 4 3.5 2.5-1.3 4h-4.4l-1.3-4Z" },
  { id: "history", label: "History", icon: "M12 7v5l3 2 M3.5 12a8.5 8.5 0 1 0 2.5-6 M3 4v4h4" },
  { id: "picks", label: "My picks", icon: "M5 12l4 4L19 6" },
  { id: "record", label: "Record", icon: "M4 20V10m6 10V4m6 16v-7m4 7H2" },
] as const;

type Tab = (typeof TABS)[number]["id"];

/** Routes live in the URL hash (#matches/3) so screens can be bookmarked and shared. */
function readRoute(): { tab: Tab; fixtureId: number | null } {
  const [name, id] = window.location.hash.replace(/^#\/?/, "").split("/");
  const tab = (TABS.find((t) => t.id === name)?.id ?? "slips") as Tab;
  return { tab, fixtureId: id !== undefined && /^\d+$/.test(id) ? Number(id) : null };
}

const TITLES: Record<Tab, string> = {
  slips: "This round", matches: "Matches", history: "History", picks: "My picks", record: "Record",
};

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
    <div className="mx-auto min-h-screen max-w-lg px-4 pb-28">
      <header className="pb-5 pt-7">
        <div className="flex items-center gap-2 text-xs font-semibold text-ink-3">
          <img src={`${import.meta.env.BASE_URL}icons/icon.svg`} alt="" className="h-5 w-5 rounded-md" />
          PL Predictor
          {data && (
            <span className="ml-auto font-medium">
              Updated {new Date(data.generated_at).toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
        </div>
        <h1 className="mt-3 text-3xl font-extrabold tracking-tight">{TITLES[tab]}</h1>
      </header>

      {error && <Empty><span className="text-critical-ink">Could not load predictions ({error}).</span></Empty>}
      {!data && !error && <Empty>Loading predictions…</Empty>}
      {data && tab === "slips" && <Slips data={data} />}
      {data && tab === "matches" && <Matches fixtures={data.fixtures} selected={fixtureId}
        onSelect={(id) => go(id === null ? "matches" : `matches/${id}`)} onSave={(p) => updatePicks([p, ...picks])} />}
      {data && tab === "history" && <History archive={data.archive ?? []} />}
      {data && tab === "picks" && <MyPicks data={data} picks={picks} onRemove={(id) => updatePicks(picks.filter((p) => p.id !== id))} />}
      {data && tab === "record" && <Record data={data} />}

      <p className="mt-10 text-center text-[11px] leading-relaxed text-ink-3">
        Probabilities, not guarantees. Only stake what you can afford to lose. 18+.
      </p>

      <nav className="fixed inset-x-0 bottom-0 border-t border-border/70 bg-surface/90 backdrop-blur-lg" style={{ paddingBottom: "env(safe-area-inset-bottom)" }}>
        <div className="mx-auto grid max-w-lg grid-cols-5">
          {TABS.map((t) => (
            <button key={t.id} onClick={() => go(t.id)}
              className={`flex flex-col items-center gap-1 pb-2 pt-2.5 text-[10px] font-semibold ${tab === t.id ? "text-accent" : "text-ink-3"}`}
              aria-current={tab === t.id ? "page" : undefined}>
              <svg viewBox="0 0 24 24" className="h-[22px] w-[22px]" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
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
