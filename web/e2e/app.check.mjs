// End-to-end check of the built app in the installed Microsoft Edge at phone width.
// Usage: npm run build && npx vite preview --port 4173 & node e2e/app.check.mjs [screenshotDir]
import { chromium } from "playwright-core";

const BASE = "http://localhost:4173/";
const shots = process.argv[2];
const browser = await chromium.launch({ channel: "msedge" });
const failures = [];
const check = (ok, message) => { console.log(`${ok ? "PASS" : "FAIL"}  ${message}`); if (!ok) failures.push(message); };

for (const scheme of ["light", "dark"]) {
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, colorScheme: scheme });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  const noOverflow = async (screen) => check(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `[${scheme}] ${screen}: no horizontal overflow`);
  const snap = async (name) => shots && page.screenshot({ path: `${shots}/${scheme}-${name}.png`, fullPage: true });

  // Slips: switch tiers, enter odds for every leg, expect a verdict.
  await page.goto(BASE);
  await page.getByRole("tab", { name: "Safe" }).waitFor();
  await noOverflow("slips"); await snap("slips");
  for (const tier of ["Medium", "Big", "Safe"]) {
    await page.getByRole("tab", { name: tier }).click();
    check(await page.getByRole("tab", { name: tier }).getAttribute("aria-selected") === "true", `[${scheme}] tier switch to ${tier}`);
  }
  const inputs = page.getByRole("spinbutton");
  const count = await inputs.count();
  for (let i = 0; i < count; i++) await inputs.nth(i).fill("2.00");
  // Only the verdict badge carries a signed percentage; the footnote also says "Value bet".
  // Safe slip ~36% at total odds 2.00^n is clearly positive, so expect "Value bet +x%".
  const badge = await page.getByText(/(Value bet|Fair price|No value)\s*[+-]\d/).allInnerTexts();
  check(badge.length === 1 && /Value bet\s*\+\d/.test(badge[0]),
    `[${scheme}] slip verdict after entering ${count} odds at 2.00: ${badge.join(" ").replace(/\s+/g, " ")}`);

  // Matches: open a match, check value, save the pick.
  await page.getByRole("button", { name: "Matches" }).click();
  await noOverflow("matches"); await snap("matches");
  await page.locator("section button").first().click(); // first match row in the list card
  await page.getByText("Likeliest scores").waitFor();
  await noOverflow("match detail"); await snap("detail");
  const firstOdds = page.getByRole("spinbutton").first();
  await firstOdds.fill("1.10");
  check(await page.getByText("No value").count() >= 1, `[${scheme}] low odds give "No value"`);
  await firstOdds.fill("50");
  check(await page.getByText("Value bet").count() >= 1, `[${scheme}] high odds give "Value bet"`);
  await page.getByRole("button", { name: "Save to My picks" }).click();
  check(await page.getByRole("button", { name: /Saved to My picks/ }).isDisabled(), `[${scheme}] save button confirms`);
  for (const group of ["1Up & first goal", "Goals", "Result"]) await page.getByRole("tab", { name: group }).click();

  // My picks: the saved pick is listed and survives a reload.
  await page.getByRole("button", { name: "My picks" }).click();
  check(await page.getByRole("button", { name: /^Remove / }).count() === 1, `[${scheme}] saved pick listed`);
  await page.reload();
  await page.getByRole("button", { name: /^Remove / }).first().waitFor();
  check(true, `[${scheme}] pick persists after reload`);
  await noOverflow("my picks"); await snap("picks");
  await page.getByRole("button", { name: /^Remove / }).click();
  check(await page.getByRole("button", { name: /^Remove / }).count() === 0, `[${scheme}] pick removed`);

  // History and Record render.
  await page.getByRole("button", { name: "History" }).click();
  await page.getByText("Predictions", { exact: true }).waitFor();
  check(await page.getByText("Our call").count() > 0, `[${scheme}] history shows archived predictions`);
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
