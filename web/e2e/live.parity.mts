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
failures.forEach((f) => console.log(`FAIL  ${f}`));
console.log(failures.length ? `\n${failures.length} FAILED` : "ALL PASSED");
process.exit(failures.length ? 1 : 0);
