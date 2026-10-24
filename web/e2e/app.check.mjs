// End-to-end check of the built app in the installed Microsoft Edge at phone width.
// Usage: npm run build && npx vite preview --port 4173 & npm run check:e2e [-- screenshotDir]
import { chromium } from "playwright-core";

const BASE = "http://localhost:4173/";
const shots = process.argv[2];
const browser = await chromium.launch({ channel: "msedge" });
const failures = [];
const check = (ok, message) => { console.log(`${ok ? "PASS" : "FAIL"}  ${message}`); if (!ok) failures.push(message); };
const VERDICT = /(Bet this|Fair, skip|Don't bet)\s*[+-]\d/;
const money = (text) => Number(text.replace(/[^\d]/g, ""));

for (const scheme of ["light", "dark"]) {
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, colorScheme: scheme });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  const noOverflow = async (screen) => check(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `[${scheme}] ${screen}: no horizontal overflow`);
  const snap = async (name) => shots && page.screenshot({ path: `${shots}/${scheme}-${name}.png`, fullPage: true });
  const balanceOf = async (name) => money(await page.locator("section", { hasText: `${name} balance` }).locator(".text-2xl").first().innerText());

  // First visit: Bets asks for balances; set them in Money.
  await page.goto(BASE);
  await page.getByText("Set your Betpawa and SportyBet balances").click();
  for (const [name, amount] of [["Betpawa", "50000"], ["SportyBet", "20000"]]) {
    await page.locator("section", { hasText: `${name} balance` }).getByRole("button", { name: "Set balance" }).click();
    await page.getByLabel("Balance now (TSh)").fill(amount);
    await page.getByRole("button", { name: "Save" }).click();
  }
  check(await balanceOf("Betpawa") === 50000 && await balanceOf("SportyBet") === 20000, `[${scheme}] balances set`);

  // Bets: accumulators only, no odds boxes, stake from the Betpawa balance; record the Safe slip.
  await page.getByRole("button", { name: "Bets", exact: true }).click();
  await page.getByRole("tab", { name: "Safe" }).waitFor();
  check(await page.getByRole("spinbutton").count() === 0, `[${scheme}] no odds boxes on slips`);
  check(await page.getByText(VERDICT).count() === 1, `[${scheme}] slip verdict shown`);
  const stakeShown = await page.getByText(/^Stake on Betpawa$/).count();
  await noOverflow("bets"); await snap("bets");
  await page.getByRole("button", { name: "I placed this bet" }).click();
  await page.getByRole("button", { name: /^Save: I placed/ }).click();
  check(await page.getByRole("button", { name: "✓ Recorded in Money" }).count() === 1, `[${scheme}] safe slip recorded (stake shown: ${stakeShown > 0})`);

  // Big slip on SportyBet with Flexi.
  await page.getByRole("tab", { name: "Big" }).click();
  check(await page.getByText(/SportyBet Flexi:/).count() === 1, `[${scheme}] Flexi chances shown on Big slip`);
  await page.getByRole("button", { name: "I placed this bet" }).click();
  await page.getByRole("tab", { name: "SportyBet" }).click();
  await page.getByLabel("Stake in TSh").fill("200");
  const flexiTab = page.getByRole("tab", { name: /^\d of \d$/ }).first();
  await flexiTab.click();
  await page.getByLabel("Flexi To Win amount").fill("800");
  check(await page.getByText(/Chance at least \d of \d win/).count() === 1, `[${scheme}] Flexi chance and value check shown`);
  await noOverflow("place form"); await snap("place");
  await page.getByRole("button", { name: /^Save: I placed/ }).click();

  // Money: balances follow the bets; deposits and withdrawals never count as profit.
  await page.getByRole("button", { name: "Money", exact: true }).click();
  const betpawaAfter = await balanceOf("Betpawa");
  check(betpawaAfter <= 50000, `[${scheme}] Betpawa balance after safe stake: ${betpawaAfter}`);
  check(await balanceOf("SportyBet") === 19800, `[${scheme}] SportyBet balance after TSh 200 Flexi bet`);
  const betpawaCard = page.locator("section", { hasText: "Betpawa balance" });
  await betpawaCard.getByRole("button", { name: "+ Deposit" }).click();
  await page.getByLabel("Deposit (TSh)").fill("10000");
  await page.getByRole("button", { name: "Save" }).click();
  await betpawaCard.getByRole("button", { name: "− Withdraw" }).click();
  await page.getByLabel("Withdrawal (TSh)").fill("5000");
  await page.getByRole("button", { name: "Save" }).click();
  check(await balanceOf("Betpawa") === betpawaAfter + 5000, `[${scheme}] deposit +10,000 and withdrawal −5,000 applied`);
  check(await page.getByText("Flexi 3/4").count() + await page.getByText(/Flexi \d\/\d/).count() >= 1, `[${scheme}] Flexi bet listed`);

  // A bet on a finished match settles automatically (Tottenham 3-1 Coventry, 19 Oct).
  await page.evaluate(() => {
    const ledger = JSON.parse(localStorage.getItem("pl-predictor:ledger"));
    ledger.entries.push({ id: "settled-test", type: "bet", placedAt: "2026-10-18T10:00:00Z", day: "2026-10-19", bookmaker: "betpawa",
      tier: "safe", stake: 1000, odds: 2.5, winProbability: 0.4,
      legs: [{ home: "Tottenham", away: "Coventry", date: "2026-10-19", market: "home_win", label: "Tottenham win", probability: 0.7 },
             { home: "Tottenham", away: "Coventry", date: "2026-10-19", market: "over_1.5", label: "Over 1.5 goals", probability: 0.8 }] });
    localStorage.setItem("pl-predictor:ledger", JSON.stringify(ledger));
  });
  await page.reload();
  await page.getByText("Placed bets").waitFor();
  check(await page.getByText(/^✓\s*Won$/).count() >= 1, `[${scheme}] finished bet settles as Won`);
  check(await balanceOf("Betpawa") === betpawaAfter + 5000 - 1000 + 2500, `[${scheme}] winnings added to balance`);
  await noOverflow("money"); await snap("money");

  // Matches: information only, Betpawa odds and verdicts, double chance tab.
  await page.getByRole("button", { name: "Matches", exact: true }).click();
  await page.locator("section button").first().click();
  await page.getByText("Likeliest scores").waitFor();
  check(await page.getByRole("spinbutton").count() === 0, `[${scheme}] match has no inputs`);
  await page.getByRole("tab", { name: "Double" }).click();
  check(await page.getByText(/or draw/).count() >= 1, `[${scheme}] double chance markets shown`);
  await noOverflow("match detail"); await snap("detail");

  for (const screen of ["History", "Record"]) {
    await page.getByRole("button", { name: screen, exact: true }).click();
    await page.waitForTimeout(300);
    await noOverflow(screen.toLowerCase());
  }
  check(errors.length === 0, `[${scheme}] no console errors${errors.length ? `: ${errors.join(" | ")}` : ""}`);
  await page.close();
}
await browser.close();
console.log(failures.length ? `\n${failures.length} FAILED` : "\nALL PASSED");
process.exit(failures.length ? 1 : 0);
