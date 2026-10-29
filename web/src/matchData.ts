import type { ArchiveDay, League, ScheduledMatch } from "./types";

export const LEAGUES: Record<string, League & { newsSlug: string }> = {
  EREDIV: { code: "EREDIV", name: "Eredivisie", country: "Netherlands", newsSlug: "ned.1" },
  JUPILER: { code: "JUPILER", name: "Belgian Pro League", country: "Belgium", newsSlug: "bel.1" },
  PRIMEIRA: { code: "PRIMEIRA", name: "Primeira Liga", country: "Portugal", newsSlug: "por.1" },
  SUPERLIG: { code: "SUPERLIG", name: "Super Lig", country: "Turkey", newsSlug: "tur.1" },
  EPL: { code: "EPL", name: "Premier League", country: "England", newsSlug: "eng.1" },
  LALIGA: { code: "LALIGA", name: "La Liga", country: "Spain", newsSlug: "esp.1" },
  SERIEA: { code: "SERIEA", name: "Serie A", country: "Italy", newsSlug: "ita.1" },
  BUNDES: { code: "BUNDES", name: "Bundesliga", country: "Germany", newsSlug: "ger.1" },
  LIGUE1: { code: "LIGUE1", name: "Ligue 1", country: "France", newsSlug: "fra.1" },
};

export const localDay = (kickoffUtc: string) => {
  const date = new Date(kickoffUtc);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
};

export function sharedDates(today: string, archive: ArchiveDay[]) {
  const future = Array.from({ length: 15 }, (_, offset) => {
    const date = new Date(`${today}T12:00:00`);
    date.setDate(date.getDate() + offset);
    return localDay(date.toISOString());
  });
  return [...new Set([...archive.map((item) => item.date), ...future])].sort();
}

export const scheduledOn = (matches: ScheduledMatch[], day: string) => matches.filter((match) => localDay(match.kickoff_utc) === day);

export const fixtureId = (home: string, away: string) => `${home}\u0000${away}`;
