// Live leg states must agree with the official settlement. Recorded real data: ESPN scoreboards of
// 69 matches (16-25 Oct 2026, five leagues) and the engine's outcome() for the same matches.
// Run: npm run check:live
import { readFileSync } from "node:fs";
import { legLive, parseEvent } from "../src/liveRules.ts";

const fixture = JSON.parse(readFileSync(new URL("./fixtures/live_parity.json", import.meta.url), "utf8"));
let legs = 0;
const failures: string[] = [];
for (const expected of fixture.expected) {
  const recorded = fixture.matches.find((m: any) => m.home === expected.home && m.away === expected.away);
  if (!recorded) continue;
  const live = parseEvent(recorded.event);
  if (live.score[0] !== expected.score[0] || live.score[1] !== expected.score[1]) {
    failures.push(`${expected.home} v ${expected.away}: score ${live.score} vs official ${expected.score}`);
  }
  for (const [market, won] of Object.entries(expected.outcomes)) {
    legs += 1;
    const state = legLive(market as any, live);
    if (state !== (won ? "won" : "lost")) failures.push(`${expected.home} v ${expected.away} ${market}: live ${state}, official ${won}`);
  }
}
console.log(`${fixture.matches.length} matches, ${legs} legs checked against the official settlement`);
// Trial bet types (halves, first 10 minutes, DC 1Up, first goal) against engine research_leagues.settle_markets.
const trial = JSON.parse(readFileSync(new URL("./fixtures/live_parity_trial.json", import.meta.url), "utf8"));
let trialLegs = 0;
for (const recorded of trial.matches) {
  const live = parseEvent(recorded.event);
  for (const [market, won] of Object.entries(recorded.outcomes)) {
    trialLegs += 1;
    const state = legLive(market, live);
    if (state !== (won ? "won" : "lost")) failures.push(`Trial ${recorded.home} v ${recorded.away} (${recorded.FT}, HT ${recorded.HT}) ${market}: live ${state}, official ${won}`);
  }
}
console.log(`${trial.matches.length} matches, ${trialLegs} Trial legs checked against the official Trial settlement`);
// In-play: decided as soon as it is certain, "live" until then.
const inPlay = (name: string, period: number, seconds: number, goals: [string, string, number][]) => parseEvent({
  status: { type: { name, state: "in" }, displayClock: `${Math.floor(seconds / 60)}'`, period, clock: seconds },
  competitions: [{ competitors: [{ team: { id: "1" }, homeAway: "home", score: goals.filter((g) => g[0] === "1").length },
                                 { team: { id: "2" }, homeAway: "away", score: goals.filter((g) => g[0] === "2").length }],
                   details: goals.map(([id, shown, value]) => ({ scoringPlay: true, team: { id }, clock: { displayValue: shown, value } })) }] });
const expectState = (label: string, market: string, match: ReturnType<typeof parseEvent>, want: string) => {
  const got = legLive(market, match);
  if (got !== want) failures.push(`In-play ${label} ${market}: ${got}, expected ${want}`);
};
const halfTime = inPlay("STATUS_HALFTIME", 1, 2820, [["1", "45'+2'", 2820]]);   // 1-0, goal in first-half stoppage
expectState("HT 1-0", "fh_over_0.5", halfTime, "won");
expectState("HT 1-0", "home_fh_over_0.5", halfTime, "won");
expectState("HT 1-0", "away_fh_over_0.5", halfTime, "lost");
expectState("HT 1-0", "sh_over_0.5", halfTime, "live");
expectState("HT 1-0", "home_win_either_half", halfTime, "won");
expectState("HT 1-0", "away_win_both_halves", halfTime, "lost");
expectState("HT 1-0", "away_score_both_halves", halfTime, "lost");
expectState("HT 1-0", "interval_10_draw", halfTime, "won");
const early = inPlay("STATUS_FIRST_HALF", 1, 300, []);                          // 5', 0-0
expectState("5' 0-0", "interval_10_draw", early, "live");
expectState("5' 0-0", "fh_over_0.5", early, "live");
const second = inPlay("STATUS_SECOND_HALF", 2, 3300, [["2", "55'", 3300]]);     // 55', 0-1
expectState("55' 0-1", "away_sh_over_0.5", second, "won");
expectState("55' 0-1", "dc1up_x2", second, "won");
expectState("55' 0-1", "first_goal_home", second, "lost");
expectState("55' 0-1", "fh_over_0.5", second, "lost");
failures.forEach((f) => console.log(`FAIL  ${f}`));
console.log(failures.length ? `\n${failures.length} FAILED` : "ALL PASSED");
process.exit(failures.length ? 1 : 0);
