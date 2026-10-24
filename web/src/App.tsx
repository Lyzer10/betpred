import { useEffect, useState } from "react";
import { type Ledger, loadLedger, storeLedger } from "./ledger";
import { usePredictions } from "./lib";
import { NEXT_THEME, type Theme, applyTheme, loadTheme } from "./theme";
import { Empty } from "./ui";
import { History } from "./views/History";
import { Matches } from "./views/Matches";
import { Money } from "./views/Money";
import { Record } from "./views/Record";
import { Slips } from "./views/Slips";

const TABS = [
  { id: "bets", label: "Bets", icon: "M5 4h14v16l-3-2-2 2-2-2-2 2-2-2-3 2Z M9 9h6 M9 13h6" },
  { id: "matches", label: "Matches", icon: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 4 3.5 2.5-1.3 4h-4.4l-1.3-4Z" },
  { id: "history", label: "History", icon: "M12 7v5l3 2 M3.5 12a8.5 8.5 0 1 0 2.5-6 M3 4v4h4" },
  { id: "money", label: "Money", icon: "M3 7h18v12H3Z M3 11h18 M16 15h2" },
  { id: "record", label: "Record", icon: "M4 20V10m6 10V4m6 16v-7m4 7H2" },
] as const;

type Tab = (typeof TABS)[number]["id"];

/** Routes live in the URL hash (#matches/3) so screens can be bookmarked and shared. */
function readRoute(): { tab: Tab; fixtureId: number | null } {
  const [name, id] = window.location.hash.replace(/^#\/?/, "").split("/");
  const tab = (TABS.find((t) => t.id === name)?.id ?? "bets") as Tab;
  return { tab, fixtureId: id !== undefined && /^\d+$/.test(id) ? Number(id) : null };
}

const TITLES: Record<Tab, string> = { bets: "Bets", matches: "Matches", history: "History", money: "Money", record: "Record" };

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
  const [ledger, setLedger] = useState<Ledger>(loadLedger);
  const [theme, setTheme] = useState<Theme>(loadTheme);
  const cycleTheme = () => { const next = NEXT_THEME[theme]; setTheme(next); applyTheme(next); };
  const updateLedger = (next: Ledger) => { setLedger(next); storeLedger(next); };

  return (
    <div className="mx-auto min-h-screen max-w-lg px-4 pb-28">
      <header className="sticky top-0 z-10 -mx-4 mb-4 bg-bg/90 px-4 pb-3 pt-5 backdrop-blur-lg">
        <div className="flex items-center gap-3">
          <img src={`${import.meta.env.BASE_URL}icons/icon-192.png`} alt="BetPredz" className="h-9 w-9 rounded-xl" />
          <div className="min-w-0 flex-1">
            <div className="text-xl font-black italic leading-none tracking-tight">
              BET<span className="text-accent">PREDZ</span>
            </div>
            <div className="mt-1 truncate text-[11px] font-medium text-ink-3">
              {TITLES[tab]}{data && ` · updated ${new Date(data.generated_at).toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}`}
            </div>
          </div>
          <button onClick={cycleTheme} aria-label={`Theme: ${theme}. Tap to change.`} title={`Theme: ${theme}`}
            className="flex h-10 items-center gap-1.5 rounded-full bg-surface px-3 text-xs font-semibold text-ink-2 shadow-card">
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              {theme === "dark" ? <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
                : theme === "light" ? <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>
                : <><circle cx="12" cy="12" r="9" /><path d="M12 3v18a9 9 0 0 0 0-18Z" fill="currentColor" /></>}
            </svg>
            {theme === "auto" ? "Auto" : theme === "light" ? "Light" : "Dark"}
          </button>
        </div>
      </header>

      {error && <Empty><span className="text-critical-ink">Could not load predictions ({error}).</span></Empty>}
      {!data && !error && <Empty>Loading predictions…</Empty>}
      {data && tab === "bets" && (
        <Slips data={data} ledger={ledger} onOpenMoney={() => go("money")}
          onPlace={(bet) => updateLedger({ ...ledger, entries: [...ledger.entries, bet] })} />
      )}
      {data && tab === "matches" && <Matches fixtures={data.fixtures} archive={data.archive ?? []} selected={fixtureId}
        onSelect={(id) => go(id === null ? "matches" : `matches/${id}`)} />}
      {data && tab === "history" && <History archive={data.archive ?? []} />}
      {data && tab === "money" && <Money ledger={ledger} results={data.results} onChange={updateLedger} />}
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
