import { chromium } from "playwright-core";
import { mkdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const BASE = process.env.BASE_URL ?? "http://localhost:4173/";
const shots = new URL("./screenshots/lineup-pitch/", import.meta.url);
const lineupFixture = await readFile(new URL("./fixtures/lineups.json", import.meta.url), "utf8");
await mkdir(shots, { recursive: true });

const browser = await chromium.launch({ channel: "msedge" });
const failures = [];
const check = (ok, message) => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${message}`);
  if (!ok) failures.push(message);
};

for (const scheme of ["light", "dark"]) {
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, colorScheme: scheme });
  await page.route("**/data/lineups.json", (route) => route.fulfill({ status: 200, contentType: "application/json", body: lineupFixture }));
  await page.goto(BASE);
  await page.getByRole("button", { name: "Matches", exact: true }).click();
  await page.locator("[data-date='2026-10-25']").click();
  await page.locator("button[data-match-row]", { hasText: "Sunderland" }).click();
  await page.getByRole("tab", { name: "Line-ups", exact: true }).click();
  const card = page.locator("[data-lineups]");
  await card.locator("[data-pitch]").waitFor();
  if (scheme === "dark") await card.getByRole("tab", { name: "Leeds" }).click();

  // Real line-ups (ESPN, Sunderland v Leeds 25 Oct 2026): light shows the home side, dark the away side.
  const fixtureMatch = JSON.parse(lineupFixture).matches[0];
  const formation = (scheme === "light" ? fixtureMatch.home_lineup : fixtureMatch.away_lineup).formation;
  check(await card.locator("[data-player-marker]").count() === 11, `[${scheme}] pitch has exactly 11 player markers`);
  check(await card.getByText(`Formation ${formation}`).count() === 1, `[${scheme}] ${formation} formation is shown`);
  check(await card.locator("[data-lineup-fallback]").count() === 0, `[${scheme}] valid lineup does not use the numbered fallback`);
  check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `[${scheme}] no horizontal overflow at 375px`);
  await page.locator("[data-floating-nav]").evaluate((nav) => { nav.style.visibility = "hidden"; });
  await card.screenshot({ path: fileURLToPath(new URL(`${scheme}-${formation}.png`, shots)) });
  await page.close();
}

await browser.close();
console.log(failures.length ? `\n${failures.length} FAILED` : "\nALL PASSED");
process.exit(failures.length ? 1 : 0);
