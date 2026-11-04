# Pending results repair, 4 November 2026

The original five leagues depended on Understat for prompt settlement. On this
check its `/getLeagueData/EPL/2026` endpoint returned HTTP 200 with an HTML page,
not JSON. The existing cached prediction fallback kept publication working but
could not supply the missing results. ESPN supplied completed scores and goals.

## Scope and safeguards

`python -m src.settle_results` runs independently after full, final and price runs.
It fills published result fields, archive indexes, slip statuses and the results
used by device saved bets. It does not fit anything or select or reprice bets.
Models, calibrators, training data, gates, probabilities, stake settings and health
settings were not changed. Normal health reporting refreshes on the next normal
prediction run, using the newly available outcomes under its existing rules.

The fallback requires the requested ESPN competition, exact canonical teams and
the UTC kickoff date. Only completed `STATUS_FULL_TIME` games qualify. Own goals
use ESPN's benefiting team credit. Both final scores must reconcile to the entire
ordered scoring sequence before 1Up or first scorer settles. Otherwise those
markets stay unknown. Existing official results are not overwritten, including
when sources disagree. Unknown names, postponed matches and unavailable sources
cannot create a settlement. Raw responses are cached in `data/raw/espn_results`.
Timing fields intentionally unknown for the four score-only leagues do not cause
unnecessary backfill requests. A later source outage cannot clear a known history
outcome. The owner explicitly authorized this repair's merge and publication.

## Verification

| Check | Result |
|---|---|
| Missing scores, 1 November | 15 repaired, 32/32 archived matches now scored |
| Missing scores, 2 November | 5 repaired, 8/8 now scored |
| Timing evidence for all 20 repaired matches | Complete, every outcome verified |
| ESPN vs football-data season CSV scores | 21 comparisons, zero disagreements |
| All published probabilities, selected legs, odds and stake/health settings | Exact structural equality outside settlement fields |
| Full engine suite | 162 passed, 4 skipped |
| Web build | Passed |
| Existing browser assertions | All passed in Chrome, light and dark, 375px |
| Actual repaired November pages, with direct ESPN browser requests blocked | Scores and all slip legs settled, light and dark, 375px, no overflow |

The existing browser runner's Edge process exited before opening a page. The same
assertions ran in Chrome by substituting only the browser selection in memory,
with a preview at `http://127.0.0.1:4175/`. No app or existing browser test code was
changed to mask this limitation. The existing placement and absent captured best
pick cases retain their original conditional skips.

The new regression tests use real trimmed ESPN responses for Liverpool v Arsenal,
Union Berlin v Cologne, and Frankfurt v Hamburg (including an own goal).
They cover settlement, missing goal evidence, strict matching, source outages,
cache reuse, score conflicts, repeated repair and unchanged prediction fields.

Local verification helper and inspected screenshots (not deployed):
`.worktrees/results-check.mjs` and `.worktrees/results-screenshots/`.
Screenshots: `light-bets.png`, `dark-bets.png`, `light-matches.png`,
`dark-matches.png`. Scores and leg outcomes were visually inspected.

On 1 November Safe and Medium won; Big lost as a full accumulator but its stored
Flexi option would have paid. On 2 November Safe won, Medium and Big lost.
These are settlement facts for the previously published slips, not new bets or
claims of future profitability. The unfinished 4 November game stays pending.
