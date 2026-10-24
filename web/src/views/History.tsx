import { useState } from "react";
import { odds, pct, timeLabel, useArchive } from "../lib";
import type { ArchiveDay, ArchivedFixture, MarketKey, TierName } from "../types";
import { Card, Crest, Empty, SectionTitle, StatusPill, TIERS } from "../ui";

const RESULT: MarketKey[] = ["home_win", "draw", "away_win"];

/** Our main call for a match: the likeliest of home / draw / away. */
function mainCall(fixture: ArchivedFixture) {
  const result = fixture.markets.filter((m) => RESULT.includes(m.market));
  return result.reduce((a, b) => (b.probability > a.probability ? b : a));
}

function ArchivedRow({ fixture }: { fixture: ArchivedFixture }) {
  const call = mainCall(fixture);
  const confident = fixture.markets.filter((m) => m.probability >= 0.7);
  const outcome = fixture.result?.outcomes;
  const label = (text: string) => text.replace("Home", fixture.home).replace("Away", fixture.away);
  return (
    <div className="border-t border-border/60 px-4 py-4 first:border-t-0">
      <div className="flex items-center gap-3">
        <span className="w-11 shrink-0 text-xs font-medium text-ink-3">{timeLabel(fixture.kickoff_utc)}</span>
        <div className="min-w-0 flex-1 space-y-1.5">
          {[fixture.home, fixture.away].map((team, i) => (
            <div key={team} className="flex items-center gap-2">
              <Crest team={team} size="sm" />
              <span className="flex-1 truncate text-sm font-semibold">{team}</span>
              {fixture.result && <span className="w-5 text-right text-sm font-bold">{fixture.result.score[i]}</span>}
            </div>
          ))}
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2 pl-14">
        <span className="text-xs text-ink-3">Our call</span>
        <span className="text-xs font-semibold">{label(call.label)} {pct(call.probability)}</span>
        {outcome ? <StatusPill status={outcome[call.market] ? "won" : "lost"} /> : <StatusPill status="pending" />}
      </div>
      {confident.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5 pl-14">
          {confident.map((m) => {
            const state = outcome ? (outcome[m.market] ? "won" : "lost") : "pending";
            const tone = state === "won" ? "bg-good/12 text-good-ink" : state === "lost" ? "bg-critical/10 text-critical-ink" : "bg-surface-2 text-ink-2";
            return (
              <span key={m.market} className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${tone}`}>
                {state === "won" ? "✓ " : state === "lost" ? "✕ " : ""}{label(m.label)} {pct(m.probability)}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function History({ archive }: { archive: ArchiveDay[] }) {
  const [date, setDate] = useState<string | null>(archive[0]?.date ?? null);
  const snapshot = useArchive(date);
  if (!archive.length) return <Empty>Predictions are saved here every day. Come back after the next update.</Empty>;
  const slips = snapshot ? (["safe", "medium", "big"] as TierName[]).filter((t) => snapshot.slips[t]) : [];
  return (
    <div>
      <div className="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 pb-1">
        {archive.map((day) => {
          const d = new Date(`${day.date}T12:00:00`); // midday: same calendar day in every time zone
          const active = day.date === date;
          return (
            <button key={day.date} onClick={() => setDate(day.date)}
              className={`flex w-16 shrink-0 flex-col items-center rounded-2xl py-2.5 transition ${active ? "bg-hero text-hero-ink" : "bg-surface text-ink shadow-card"}`}>
              <span className="text-[11px] opacity-70">{d.toLocaleDateString(undefined, { weekday: "short" })}</span>
              <span className="text-lg font-bold">{d.getDate()}</span>
              <span className="text-[10px] opacity-70">{day.settled ? `${day.settled}/${day.fixtures} ✓` : `${day.fixtures} games`}</span>
            </button>
          );
        })}
      </div>
      {!snapshot && <p className="mt-6 text-center text-sm text-ink-3">Loading…</p>}
      {snapshot && (
        <>
          <SectionTitle aside={`saved ${new Date(snapshot.generated_at).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}`}>
            Predictions
          </SectionTitle>
          <Card className="overflow-hidden">
            {snapshot.fixtures.map((f) => <ArchivedRow key={`${f.home}-${f.away}`} fixture={f} />)}
          </Card>
          {slips.length > 0 && <SectionTitle>Slips that day</SectionTitle>}
          {slips.length > 0 && (
            <Card className="overflow-hidden">
              {slips.map((tier) => {
                const slip = snapshot.slips[tier]!;
                return (
                  <div key={tier} className="border-t border-border/60 px-4 py-3.5 first:border-t-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold">{TIERS[tier].title}</span>
                      <span className="text-xs text-ink-3">{pct(slip.win_probability)} · odds {odds(slip.total_odds)}</span>
                    </div>
                    <div className="mt-1 text-xs text-ink-2">
                      {slip.legs.map((l) => `${l.label.replace("Home", l.home).replace("Away", l.away)} (${l.home} v ${l.away})`).join(" · ")}
                    </div>
                  </div>
                );
              })}
            </Card>
          )}
        </>
      )}
    </div>
  );
}
