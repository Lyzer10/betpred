# Next-round verification

Branch `codex/next-round`, based on origin/main f28e05d. No push or merge.

## Commands and outcomes

- Final `python -m pytest -q --disable-warnings`: **132 passed**, 6109 existing deprecation warnings,
  58.92 seconds. Final `npm run build`: exit 0, 47 modules transformed, PWA generated.

- `git fetch origin`: initially failed to connect; later succeeded. Branch rebased onto f28e05d;
  subsequent fetch confirmed no newer main. The documentation conflict preserved both deployment
  notes and the original study rules. Original pre-registration 46da3bb became ad9d0bf on rebase;
  no rule was changed after results.
- Identified Betpawa categories/event GETs: HTTP 200, real event 38781890. Team-total handicaps
  2/6 correspond to lines 0.5/1.5; prices named Over. DNB names 1/2. Trimmed values unchanged.
- `python -m pytest -q tests/test_overlap_study.py tests/test_research_prices.py`: 2 passed
  before running the overlap study. Expanded final tests cover research quote selection isolation
  and health/pair monitor isolation using a real archive.
- `python -m src.overlap_study`: exit 0; KEEP A, matched M-A -0.045543,
  95% CI [-0.144478, +0.045067], 884 matched slips.
- `python -m src.new_leagues_study`: exit 0; four READY, full results in new_leagues_study.md.
  The first run was interrupted by a Windows paging-file resource failure; restarted using cached
  real downloads, unchanged rules. No final result from the interrupted run was substituted.
- ESPN range scoreboard request: HTTP 400. Single-date `dates=20261025` requests succeeded for
  all four leagues and confirmed actual completed scores; responses cached.
- `python -m src.predict --no-refresh`: exit 0, health ok, 0 fresh fixtures. football-data/Understat
  returned invalid JSON, disconnected requests or SSL errors for several leagues; those paths were
  safely skipped. Settlement/publishing completed. Tracked generated data restored with
  `git restore --worktree -- web/public/data engine/data`.
- `npm run build`: initial worktree had no dependencies; reused the existing installed node_modules
  through a local junction, without changing packages or lockfiles. Build passed.
- `npx vite preview --port 4173 --host 127.0.0.1 --strictPort`: served the production build.
- `BASE_URL=http://127.0.0.1:4173/ npm run check:e2e -- e2e/screenshots/next-round`: ALL PASSED,
  light/dark 375px. Existing conditional skips remain for already-started slip placement and
  unavailable real settled best-pick fixtures.

## Browser diagnosis

The earlier diagnosis from unused Matches.tsx was incorrect. App imports MatchesRedesign, whose
mergeDay already supports schedules. Real fixture replay was mixed with current production responses
after reload because service workers bypassed Playwright's page routes. Blocking service workers in
the test context fixed this; no app code changed. The replay clock uses the real publication timestamp.

Verified URL `http://127.0.0.1:4173/#matches/2026-10-27`: 3 match rows, 0 best picks in both themes.
Screenshots `web/e2e/screenshots/next-round/light-matches-later.png` and
`dark-matches-later.png` were visually inspected and show Sassuolo–Lazio, Roma–Cagliari and Torino–Como.

No model, calibrator, gate, live slip market, tier, run timing or app component changed.
