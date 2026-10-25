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
  // A normal Android Chrome user agent: ESPN's network turns away "Headless" browsers, which real phones never are.
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, colorScheme: scheme,
    userAgent: "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36" });
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
  const menuClearsPageEnd = async (screen) => {
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    const clear = await page.evaluate(() => {
      const end = document.querySelector("[data-page-end]")?.getBoundingClientRect();
      const menu = document.querySelector("[data-floating-nav]")?.getBoundingClientRect();
      return Boolean(end && menu && end.bottom <= menu.top);
    });
    check(clear, `[${scheme}] ${screen}: floating menu does not cover the page end`);
  };
  const snap = async (name) => {
    if (!shots) return;
    await page.waitForFunction(() => Array.from(document.images)
      .filter((image) => {
        const box = image.getBoundingClientRect();
        return box.bottom > 0 && box.top < window.innerHeight;
      })
      .every((image) => image.complete));
    await page.screenshot({ path: `${shots}/${scheme}-${name}.png`, fullPage: true });
  };
  const balanceOf = async (name) => money(await page.locator("section", { hasText: `${name} balance` }).locator(".text-2xl").first().innerText());

  // First visit: Bets asks for balances; set them in Money.
  await page.goto(`${BASE}#history`);
  await page.locator("main[data-page='bets']").waitFor();
  check(await page.getByRole("navigation", { name: "Primary" }).getByRole("button").count() === 4,
    `[${scheme}] floating menu has exactly four destinations`);
  check(await page.getByRole("button", { name: "History", exact: true }).count() === 0 && await page.locator("main[data-page='bets']").count() === 1,
    `[${scheme}] old history route opens Bets and History is removed`);
  for (const [label, id] of [["Bets", "bets"], ["Matches", "matches"], ["Money", "money"], ["Record", "record"]]) {
    await page.getByRole("navigation", { name: "Primary" }).getByRole("button", { name: label, exact: true }).click();
    check(await page.locator(`main[data-page='${id}']`).count() === 1, `[${scheme}] ${label} menu destination opens`);
  }
  await page.getByRole("button", { name: "Bets", exact: true }).click();
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
  check(await page.locator("[data-day-status]").filter({ hasText: /Preview\.|Final slips\./ }).count() === 1, `[${scheme}] day shows preview or final status`);
  // "skip" when the slip has no value. Pilot phase caps TSh 2,500 at 3% of the TSh 50,000 balance (TSh 1,500); a price warning halves it (TSh 700).
  const fixedShown = await page.getByText(/^TSh (1,500|700)$/).count();
  check(await page.getByText(/Pilot phase: max 3%/).count() === 1, `[${scheme}] pilot cap explained on the slip`);
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
  const awayLegs = page.locator("[data-slip-leg][data-market='away_win'], [data-slip-leg][data-market='away_1up'], [data-slip-leg][data-market='away_first'], [data-slip-leg][data-market='double_x2']");
  const awayLegCount = await awayLegs.count();
  check(awayLegCount > 0, `[${scheme}] slip includes an away-team leg`);
  for (let i = 0; i < awayLegCount; i++) {
    const leg = awayLegs.nth(i);
    const badge = leg.locator("img[alt$=' badge']");
    if (await badge.count() !== 1) {
      check(false, `[${scheme}] away leg has one team badge image`);
      continue;
    }
    const alt = await badge.getAttribute("alt");
    const team = alt?.replace(/ badge$/, "") ?? "";
    const lines = (await leg.innerText()).split(/\r?\n/);
    const label = lines[0] ?? "";
    const fixture = lines.find((line) => line.includes(" v ")) ?? "";
    check(label.includes(team) && fixture.includes(` v ${team} ·`),
      `[${scheme}] ${label || "away leg"}: badge belongs to the named away team`);
  }
  const stakeShown = await page.getByText(/^Stake on Betpawa$/).count();
  await noOverflow("bets today"); await snap("bets-today");
  await page.getByRole("button", { name: "I placed this bet" }).click();
  // Type the stake: a slip without value has no recommended stake, but you can still record a bet.
  await page.getByLabel("Stake in TSh").fill("900");
  check(await page.getByText(/after this bet/).count() === 1, `[${scheme}] form shows balance after the bet`);
  await page.getByRole("button", { name: /^Save: .* on (Betpawa|SportyBet)$/ }).click();
  check(await page.getByRole("button", { name: "✓ Recorded in Money" }).count() === 1, `[${scheme}] safe slip recorded (stake shown: ${stakeShown > 0})`);

  // Big slip on SportyBet with Flexi.
  await page.getByRole("tab", { name: "Big" }).click();
  const matchWideLeg = page.locator("[data-slip-leg][data-market='under_3.5']").first();
  check(await matchWideLeg.locator("img[alt$=' badge']").count() === 2, `[${scheme}] match-wide leg shows both team badges`);
  check(await page.getByText(/SportyBet Flexi:/).count() === 1, `[${scheme}] Flexi chances shown on Big slip`);
  // Once the Big slip's first match has kicked off it is locked and cannot be placed: skip, don't fail.
  const bigOpen = await page.getByRole("button", { name: "I placed this bet" }).count() > 0;
  if (!bigOpen) console.log(`SKIP  [${scheme}] Big slip already in play: Flexi placement not checked`);
  if (bigOpen) {
    await page.getByRole("button", { name: "I placed this bet" }).click();
    await page.getByRole("tab", { name: "SportyBet" }).click();
    await page.getByLabel("Stake in TSh").fill("200");
    const flexiTab = page.getByRole("tab", { name: /^\d of \d$/ }).first();
    await flexiTab.click();
    await page.getByLabel("Flexi To Win amount").fill("800");
    check(await page.getByText(/Chance at least \d of \d win/).count() === 1, `[${scheme}] Flexi chance and value check shown`);
    await noOverflow("place form");
    await page.getByRole("button", { name: /^Save: .* on (Betpawa|SportyBet)$/ }).click();
  }

  // Past results now live on Bets: each settled slip expands to leg statuses and final scores.
  await page.locator("[data-date='2026-10-24']").click();
  const pastSlips = page.locator("[data-past-slip]");
  await pastSlips.first().waitFor();
  const pastBlue = await page.locator("[data-past-slip-header]").first().evaluate((el) => getComputedStyle(el).backgroundColor);
  check(pastBlue === "rgb(0, 19, 57)", `[${scheme}] past slip card uses the owner's #001339 (${pastBlue})`);
  check(await pastSlips.first().getByText(/Won|Lost/, { exact: true }).count() === 1, `[${scheme}] past slip shows its final status`);
  await pastSlips.first().getByRole("button").click();
  check(await pastSlips.first().getByRole("button").getAttribute("aria-expanded") === "true", `[${scheme}] past slip expands`);
  const settledLegs = pastSlips.first().locator("[data-past-leg][data-leg-status='won'], [data-past-leg][data-leg-status='lost']");
  const settledLegCount = await settledLegs.count();
  check(settledLegCount > 0, `[${scheme}] expanded past slip contains settled legs`);
  let allSettledLegsHaveScores = settledLegCount > 0;
  for (let i = 0; i < settledLegCount; i++) {
    allSettledLegsHaveScores &&= await settledLegs.nth(i).locator("[data-final-score]").count() === 1;
  }
  check(allSettledLegsHaveScores, `[${scheme}] every settled leg shows a final score`);
  await noOverflow("past Bets"); await snap("bets-past");
  const pastBigSlip = pastSlips.filter({ hasText: "Big slip" });
  await pastBigSlip.getByRole("button").click();
  check(await pastBigSlip.getByText(/SportyBet Flexi: \d+ of \d+ won · Flexi \d+ of \d+: would (not )?have paid/).count() === 1,
    `[${scheme}] settled Big slip shows its Flexi result`);

  // Money: balances follow the bets; deposits and withdrawals never count as profit.
  await page.getByRole("button", { name: "Money", exact: true }).click();
  const betpawaAfter = await balanceOf("Betpawa");
  check(betpawaAfter <= 50000, `[${scheme}] Betpawa balance after safe stake: ${betpawaAfter}`);
  if (bigOpen) check(await balanceOf("SportyBet") === 19800, `[${scheme}] SportyBet balance after TSh 200 Flexi bet`);
  const betpawaCard = page.locator("section", { hasText: "Betpawa balance" });
  await betpawaCard.getByRole("button", { name: "+ Deposit" }).click();
  await page.getByLabel("Deposit (TSh)").fill("10000");
  await page.getByRole("button", { name: "Save" }).click();
  await betpawaCard.getByRole("button", { name: "− Withdraw" }).click();
  await page.getByLabel("Withdrawal (TSh)").fill("5000");
  await page.getByRole("button", { name: "Save" }).click();
  check(await balanceOf("Betpawa") === betpawaAfter + 5000, `[${scheme}] deposit +10,000 and withdrawal −5,000 applied`);
  if (bigOpen) check(await page.getByText("Flexi 3/4").count() + await page.getByText(/Flexi \d\/\d/).count() >= 1, `[${scheme}] Flexi bet listed`);

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
  const placed = page.locator("[data-placed-bets]");
  // Month totals equal the sum of that month's bets in the saved ledger.
  const monthStake = await page.evaluate(() => {
    const ledger = JSON.parse(localStorage.getItem("pl-predictor:ledger"));
    const bets = ledger.entries.filter((e) => e.type === "bet");
    const month = bets.map((b) => b.day).sort().at(-1).slice(0, 7);
    return bets.filter((b) => b.day.startsWith(month)).reduce((a, b) => a + b.stake, 0);
  });
  const stakedShown = Number((await placed.locator("[data-month-summary]").getByText(/^TSh/).nth(0).textContent()).replace(/[^\d]/g, ""));
  check(stakedShown === monthStake, `[${scheme}] month summary staked equals the month's bets (${stakedShown} vs ${monthStake})`);
  // Choosing a day in the strip shows only that day's bets.
  await placed.locator("[data-date='2026-10-19']").click();
  check(await placed.locator("[data-bet-row]").count() === 1, `[${scheme}] Money day strip shows only that day's bets`);
  check(await placed.getByText(/^✓\s*Won$/).count() >= 1, `[${scheme}] finished bet settles as Won`);
  // Deposits and withdrawals live in their own section, never among bets.
  check(await placed.locator("[data-transfer-row]").count() === 0, `[${scheme}] no transfers among bets`);
  await page.locator("[data-transfers] > button").click();
  check(await page.locator("[data-transfers] [data-transfer-row]").count() === 2, `[${scheme}] deposits and withdrawals listed separately`);
  check(await balanceOf("Betpawa") === betpawaAfter + 5000 - 1000 + 2500, `[${scheme}] winnings added to balance`);
  check(await page.locator("[data-notifications]").getByRole("button", { name: /Turn on notifications|Copy code/ }).count() === 1,
    `[${scheme}] Money offers phone notifications`);
  await noOverflow("money"); await snap("money");

  // Matches: information only, Betpawa odds and verdicts, double chance tab.
  await page.getByRole("button", { name: "Matches", exact: true }).click();
  await noOverflow("matches list");
  await page.getByRole("tab").filter({ hasText: /\d/ }).last().click();   // an upcoming day: its matches open
  await page.locator("section button").first().click();
  await page.getByText("Likeliest scores").waitFor();
  check(await page.getByRole("spinbutton").count() === 0, `[${scheme}] match has no inputs`);
  check(await page.getByRole("heading", { name: "Form & table" }).count() === 1, `[${scheme}] match shows form and table context`);
  const lineupCard = page.locator("[data-lineups]");
  check(await lineupCard.count() === 1 && (await lineupCard.locator("[data-starter]").count() === 11
    || await lineupCard.getByText(/about an hour before kick-off/).count() === 1), `[${scheme}] match shows line-ups or when they come`);
  const recentForm = page.getByLabel(/recent form, oldest to latest/).first();
  check(await recentForm.locator("[data-form-result]").count() === 5, `[${scheme}] match shows five form chips`);
  await page.getByRole("tab", { name: "Double" }).click();
  check(await page.getByText(/or draw/).count() >= 1, `[${scheme}] double chance markets shown`);
  await noOverflow("match detail"); await snap("matches");

  for (const [screen, id] of [["Bets", "bets"], ["Matches", "matches"], ["Money", "money"], ["Record", "record"]]) {
    await page.getByRole("navigation", { name: "Primary" }).getByRole("button", { name: screen, exact: true }).click();
    await page.locator(`main[data-page='${id}']`).waitFor();
    await noOverflow(screen.toLowerCase());
    await menuClearsPageEnd(screen);
    if (id === "record") {
      check(await page.getByText("Are we beating Betpawa's prices?").count() === 1, `[${scheme}] record shows price tracking`);
      const clvLegs = await page.evaluate(async () => (await (await fetch("/data/predictions.json")).json()).clv?.legs ?? 0);
      if (clvLegs > 0) {
        check(await page.locator("[data-clv]").getByText(/Betpawa's price dropped after we picked it in/).count() === 1, `[${scheme}] price tracking headline`);
        check(await page.locator("[data-clv-early]").count() === (clvLegs < 200 ? 1 : 0), `[${scheme}] "too early" shown only under 200 bets`);
      }
      const published = await page.evaluate(async () => (await (await fetch("/data/predictions.json")).json()));
      if (published.health?.pairs?.length) {
        check(await page.locator("[data-bet-types]").count() === 1, `[${scheme}] record shows the bet-type checks`);
        await page.locator("[data-bet-types] button").last().click();     // show all, including those still collecting
        check(await page.locator("[data-bet-type]").count() >= 1, `[${scheme}] bet-type rows render`);
      }
      if (published.realised && Object.values(published.realised).some((t) => t.settled)) {
        check(await page.locator("[data-realised]").count() === 1, `[${scheme}] record shows real slip results`);
      }
      await snap("record");
    }
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
