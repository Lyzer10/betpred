// Generates the visual review sheet and fails if any ESPN badge is unavailable.
// Usage from web/: node e2e/badge-contact-sheet.mjs
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";

const root = fileURLToPath(new URL("..", import.meta.url));
const badgeUrls = JSON.parse(await readFile(new URL("../src/badgeUrls.json", import.meta.url), "utf8"));
const leagues = {
  "La Liga": ["Alaves", "Ath Bilbao", "Ath Madrid", "Barcelona", "Betis", "Celta", "Elche", "Espanol", "Getafe", "La Coruna", "Levante", "Malaga", "Osasuna", "Real Madrid", "Santander", "Sevilla", "Sociedad", "Valencia", "Vallecano", "Villarreal"],
  "Serie A": ["Atalanta", "Bologna", "Cagliari", "Como", "Fiorentina", "Frosinone", "Genoa", "Inter", "Juventus", "Lazio", "Lecce", "Milan", "Monza", "Napoli", "Parma", "Roma", "Sassuolo", "Torino", "Udinese", "Venezia"],
  Bundesliga: ["Augsburg", "Bayern Munich", "Dortmund", "Ein Frankfurt", "Elversberg", "FC Koln", "Freiburg", "Hamburg", "Hoffenheim", "Leverkusen", "M'gladbach", "Mainz", "Paderborn", "RB Leipzig", "Schalke 04", "Stuttgart", "Union Berlin", "Werder Bremen"],
  "Ligue 1": ["Angers", "Auxerre", "Brest", "Le Havre", "Le Mans", "Lens", "Lille", "Lorient", "Lyon", "Marseille", "Monaco", "Nice", "Paris FC", "Paris SG", "Rennes", "Strasbourg", "Toulouse", "Troyes"],
};

const listedTeams = Object.values(leagues).flat();
const mappedTeams = Object.keys(badgeUrls);
const missing = listedTeams.filter((team) => !badgeUrls[team]);
const unexpected = mappedTeams.filter((team) => !listedTeams.includes(team));
if (missing.length || unexpected.length) {
  throw new Error(`Contact sheet mapping mismatch. Missing: ${missing.join(", ") || "none"}. Unexpected: ${unexpected.join(", ") || "none"}.`);
}

const cards = Object.entries(leagues).map(([league, teams]) => `
  <section>
    <h2>${league} <small>${teams.length}</small></h2>
    <div class="grid">${teams.map((team) => `
      <article><img src="${badgeUrls[team]}" alt="${team}"><span>${team}</span></article>`).join("")}
    </div>
  </section>`).join("");

const browser = await chromium.launch({ channel: "msedge" });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
const responses = new Map();
page.on("response", (response) => {
  if (mappedTeams.some((team) => badgeUrls[team] === response.url())) responses.set(response.url(), response.status());
});
await page.setContent(`<!doctype html><html><head><style>
  * { box-sizing: border-box; }
  body { margin: 0; padding: 32px; color: #17202a; background: #eef2f6; font: 16px Arial, sans-serif; }
  h1 { margin: 0 0 24px; font-size: 30px; }
  section { margin: 0 0 24px; padding: 20px; border: 1px solid #d2d9e2; border-radius: 14px; background: white; }
  h2 { margin: 0 0 16px; font-size: 22px; }
  small { color: #667085; font-size: 14px; font-weight: normal; }
  .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; }
  article { min-height: 130px; padding: 12px 8px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; gap: 8px; border: 1px solid #e2e7ed; border-radius: 10px; text-align: center; font-weight: 600; }
  img { width: 82px; height: 82px; object-fit: contain; }
</style></head><body><h1>European club badge review</h1>${cards}</body></html>`, { waitUntil: "networkidle" });
await page.waitForFunction(() => [...document.images].every((image) => image.complete));

const broken = await page.locator("img").evaluateAll((images) => images.filter((image) => image.naturalWidth === 0).map((image) => image.alt));
const badStatuses = mappedTeams.filter((team) => responses.get(badgeUrls[team]) !== 200).map((team) => `${team}: ${responses.get(badgeUrls[team]) ?? "no response"}`);
if (broken.length || badStatuses.length) {
  await browser.close();
  throw new Error(`Badge verification failed. Broken images: ${broken.join(", ") || "none"}. HTTP: ${badStatuses.join(", ") || "all 200"}.`);
}

await page.screenshot({ path: `${root}/badge-contact-sheet.png`, fullPage: true });
await browser.close();
console.log(`Verified ${mappedTeams.length} badge URLs with HTTP 200.`);
console.log(`Contact sheet: ${root}/badge-contact-sheet.png`);
