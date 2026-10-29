// Real pipeline output only. Run after src.predict, before restoring generated data.
import { chromium } from "playwright-core";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const base = process.env.BASE_URL ?? "http://127.0.0.1:4173/";
const data = JSON.parse(readFileSync("public/data/predictions.json", "utf8"));
const codes = ["EREDIV", "JUPILER", "PRIMEIRA", "SUPERLIG"];
for (const code of codes) {
  if (!data.fixtures.some((fixture) => fixture.league.code === code)) throw new Error(`No real upcoming ${code} prediction`);
  if (!data.tables[code]?.length) throw new Error(`No real ${code} table`);
}
const browser = await chromium.launch({ channel: "msedge" });
for (const scheme of ["light", "dark"]) {
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, colorScheme: scheme,
    serviceWorkers: "block", userAgent: "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36" });
  await page.clock.setFixedTime(new Date(data.generated_at));
  await page.route("**/data/**", async (route) => {
    const name = new URL(route.request().url()).pathname.split("/data/")[1];
    const file = resolve("public/data", name);
    if (!file.startsWith(resolve("public/data") + "/") && !file.startsWith(resolve("public/data") + "\\")) throw new Error("Unexpected data path");
    try { await route.fulfill({ body: readFileSync(file), contentType: "application/json" }); }
    catch { await route.fulfill({ body: "null", contentType: "application/json" }); }
  });
  for (const code of codes) {
    await page.goto(`${base}#league/${code}/matches`);
    await page.locator("button[data-match-row]").first().waitFor();
    if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error(`${code} matches overflow`);
    await page.screenshot({ path: `e2e/screenshots/new-leagues/${scheme}-${code}-matches.png`, fullPage: true });
    await page.goto(`${base}#league/${code}/table`);
    await page.locator("tbody tr").first().waitFor();
    const count = await page.locator("tbody tr").count();
    if (count !== data.tables[code].length) throw new Error(`${code} table: ${count} rows`);
    if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error(`${code} table overflow`);
    await page.screenshot({ path: `e2e/screenshots/new-leagues/${scheme}-${code}-table.png`, fullPage: true });
    console.log(`PASS ${scheme} ${code} real match list and ${count}-team table`);
  }
  await page.close();
}
await browser.close();
