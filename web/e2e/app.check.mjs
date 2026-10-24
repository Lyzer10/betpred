// End-to-end check of the built app in the installed Microsoft Edge at phone width.
// Usage: npm run build && npx vite preview --port 4173 & npm run check:e2e [-- screenshotDir]
import { chromium } from "playwright-core";

const BASE = process.env.BASE_URL ?? "http://localhost:4173/";
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
  // Today may only have locked slips (all its matches started): then open the last day in the strip.
  // Prefer a day offering all three tiers (a day with few matches may only have a Safe slip).
  const openUpcomingDay = async () => {
    await page.waitForTimeout(300);
    const days = page.getByRole("tab").filter({ hasText: /\d/ });
    for (let i = 0; i < await days.count(); i++) {
      await days.nth(i).click();
      await page.waitForTimeout(200);
      if (await page.getByRole("tab", { name: "Big" }).count()) return;
    }
    await page.getByRole("tab", { name: "Safe" }).waitFor();
  };
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

  // Staking: fixed TSh 2,500 per slip, with an honest risk line.
  await page.getByRole("tab", { name: "Fixed TSh" }).click();
  await page.getByLabel("Fixed stake in TSh").fill("2500");
  check(await page.getByText(/Losing half of it takes \d+ Safe slips lost in a row/).count() === 1, `[${scheme}] staking risk line shown`);
  await page.getByRole("button", { name: "Bets", exact: true }).click();
  await openUpcomingDay();
  // TSh 2,500, or TSh 1,200 when a price warning halves it; "skip" when the slip has no value.
  const fixedShown = await page.getByText(/^TSh (2,500|1,200)$/).count();
  const skipShown = await page.getByText(/skip it/).count();
  check(fixedShown === 1 || skipShown === 1, `[${scheme}] fixed stake used on the Safe slip (${fixedShown ? "stake shown" : "skip"})`);
  // Why this bet: tap the first pick.
  await page.getByRole("button", { name: /^Why / }).first().click();
  check(await page.getByText(/expected/i).count() >= 1, `[${scheme}] why-this-bet explanation opens`);
  await page.getByRole("button", { name: "Money", exact: true }).click();
  await page.getByRole("tab", { name: "Smart" }).click();

  // Bets: accumulators only, no odds boxes, stake from the Betpawa balance; record the Safe slip.
  await page.getByRole("button", { name: "Bets", exact: true }).click();
  await openUpcomingDay();
  check(await page.getByRole("spinbutton").count() === 0, `[${scheme}] no odds boxes on slips`);
  check(await page.getByText(VERDICT).count() === 1, `[${scheme}] slip verdict shown`);
  const stakeShown = await page.getByText(/^Stake on Betpawa$/).count();
  await noOverflow("bets"); await snap("bets");
  await page.getByRole("button", { name: "I placed this bet" }).click();
  // Type the stake: a slip without value has no recommended stake, but you can still record a bet.
  await page.getByLabel("Stake in TSh").fill("900");
  check(await page.getByText(/after this bet/).count() === 1, `[${scheme}] form shows balance after the bet`);
  await page.getByRole("button", { name: /^Save: .* on (Betpawa|SportyBet)$/ }).click();
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
  await page.getByRole("button", { name: /^Save: .* on (Betpawa|SportyBet)$/ }).click();

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
  await page.getByRole("tab").filter({ hasText: /\d/ }).last().click();   // an upcoming day: its matches open
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
  // Theme switch cycles Auto -> Light -> Dark -> Auto and is remembered.
  const themeButton = page.getByRole("button", { name: /^Theme:/ });
  await themeButton.click();
  check(await page.evaluate(() => document.documentElement.dataset.theme) === "light", `[${scheme}] theme switch to light`);
  await themeButton.click();
  check(await page.evaluate(() => document.documentElement.dataset.theme) === "dark", `[${scheme}] theme switch to dark`);
  await page.reload();
  check(await page.evaluate(() => document.documentElement.dataset.theme) === "dark", `[${scheme}] theme remembered after reload`);
  await page.getByRole("button", { name: /^Theme:/ }).click();
  check(await page.evaluate(() => document.documentElement.dataset.theme) === undefined, `[${scheme}] back to auto`);
  await page.getByRole("button", { name: "Matches", exact: true }).click();
  await page.locator("img[src*='premierleague.com']").first().waitFor();
  check(await page.locator("img[src*='premierleague.com']").count() > 0, `[${scheme}] team badges load`);

  check(errors.length === 0, `[${scheme}] no console errors${errors.length ? `: ${errors.join(" | ")}` : ""}`);
  await page.close();
}
await browser.close();
console.log(failures.length ? `\n${failures.length} FAILED` : "\nALL PASSED");
process.exit(failures.length ? 1 : 0);
