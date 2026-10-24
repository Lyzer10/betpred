// End-to-end check of the built app in the installed Microsoft Edge at phone width.
// Usage: npm run build && npx vite preview --port 4173 & npm run check:e2e [-- screenshotDir]
import { chromium } from "playwright-core";

const BASE = "http://localhost:4173/";
const shots = process.argv[2];
const browser = await chromium.launch({ channel: "msedge" });
const failures = [];
const check = (ok, message) => { console.log(`${ok ? "PASS" : "FAIL"}  ${message}`); if (!ok) failures.push(message); };
const VERDICT = /(Bet this|Fair, skip|Don't bet)\s*[+-]\d/;

for (const scheme of ["light", "dark"]) {
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, colorScheme: scheme });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  const noOverflow = async (screen) => check(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `[${scheme}] ${screen}: no horizontal overflow`);
  const snap = async (name) => shots && page.screenshot({ path: `${shots}/${scheme}-${name}.png`, fullPage: true });

  // Bets: first visit asks for the balance, then shows TSh stakes.
  await page.goto(BASE);
  await page.getByLabel("How much is in your Betpawa account?").fill("50000");
  await page.getByRole("button", { name: "Save" }).click();
  check(await page.getByText("TSh 50,000").count() === 1, `[${scheme}] balance saved and shown`);
  check(await page.getByRole("spinbutton").count() === 0, `[${scheme}] no odds boxes when Betpawa prices exist`);
  const stakes = await page.getByText(/^Stake$/).count();
  check(stakes > 0 || await page.getByText("No good bets on this day").count() === 1, `[${scheme}] value bets show TSh stakes (${stakes})`);
  check(await page.getByText(VERDICT).count() > 0, `[${scheme}] verdicts shown automatically`);
  await noOverflow("bets"); await snap("bets");

  // Calendar: every day chip opens its own bets.
  const chips = page.locator("button[aria-pressed]");
  const chipCount = await chips.count();
  for (let i = 0; i < chipCount; i++) {
    await chips.nth(i).click();
    check(await chips.nth(i).getAttribute("aria-pressed") === "true", `[${scheme}] day chip ${i + 1}/${chipCount} selectable`);
  }
  await chips.first().click();
  for (const tier of ["Medium", "Big", "Safe"]) {
    if (await page.getByRole("tab", { name: tier }).count()) await page.getByRole("tab", { name: tier }).click();
  }

  // Balance persists across reloads.
  await page.reload();
  await page.getByText("TSh 50,000").waitFor();
  check(true, `[${scheme}] balance persists after reload`);

  // Matches: Betpawa odds and verdicts appear without typing; save a pick with a stake.
  await page.getByRole("button", { name: "Matches" }).click();
  await noOverflow("matches"); await snap("matches");
  await page.locator("section button").first().click();
  await page.getByText("Likeliest scores").waitFor();
  check(await page.getByText(/Betpawa \d/).count() >= 3, `[${scheme}] match shows Betpawa odds per market`);
  check(await page.getByRole("spinbutton").count() === 0, `[${scheme}] match has no odds boxes`);
  await noOverflow("match detail"); await snap("detail");
  let saved = false;
  for (const group of ["Result", "1Up & first goal", "Goals"]) {
    await page.getByRole("tab", { name: group }).click();
    const save = page.getByRole("button", { name: "Save pick" });
    if (!saved && await save.count()) {
      await save.first().click();
      saved = true;
    }
  }
  check(saved, `[${scheme}] a value pick could be saved with its stake`);

  // My picks lists it in TSh and survives a reload.
  await page.getByRole("button", { name: "My picks" }).click();
  if (saved) {
    check(await page.getByRole("button", { name: /^Remove / }).count() === 1, `[${scheme}] saved pick listed`);
    check(await page.getByText(/TSh [\d,]+ @/).count() === 1, `[${scheme}] pick shows its TSh stake`);
    await page.reload();
    await page.getByRole("button", { name: /^Remove / }).first().waitFor();
    await noOverflow("my picks"); await snap("picks");
    await page.getByRole("button", { name: /^Remove / }).click();
    check(await page.getByRole("button", { name: /^Remove / }).count() === 0, `[${scheme}] pick removed`);
  }

  await page.getByRole("button", { name: "History" }).click();
  await page.getByText("Predictions", { exact: true }).waitFor();
  await noOverflow("history"); await snap("history");
  await page.getByRole("button", { name: "Record" }).click();
  await page.getByText("Backtest", { exact: true }).waitFor();
  await noOverflow("record"); await snap("record");

  check(errors.length === 0, `[${scheme}] no console errors${errors.length ? `: ${errors.join(" | ")}` : ""}`);
  await page.close();
}
await browser.close();
console.log(failures.length ? `\n${failures.length} FAILED` : "\nALL PASSED");
process.exit(failures.length ? 1 : 0);
