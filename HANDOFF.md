# BetPredz handoff (read after PROJECT.md)

PROJECT.md is the full handbook. This file adds what a fresh chat needs to continue exactly where
the long Claude session of 8-19 Nov 2026 stopped: current state, decisions made since PROJECT.md
section 5 was last rewritten, standing rules, and where everything lives.
The repo is PUBLIC: this file never contains a secret value, only where each one is kept.

Last updated: 2026-11-19 (EAT).

## 1. Start of a new chat

Say: "Continue BetPredz. Read CLAUDE.md, PROJECT.md and HANDOFF.md first." The repo's CLAUDE.md
already forces that, and Claude's memory folder for this project holds the owner's rules and profile.
Always quote times in EAT (UTC+3). Explain things plainly. Owner is in Tanzania and bets in TSh.

## 2. Where everything lives

| Thing | Location |
|---|---|
| Repo (moved 2026-11-19 from C: to D:) | `D:\FOOTBALL` (main), plus git worktrees `D:\FOOTBALL-codex`, `D:\FOOTBALL-public-overs-churn` and `D:\FOOTBALL\.worktrees\*` (Codex/Gemini branches) |
| GitHub | `Lyzer10/betpred`, branch `main`, public |
| App | https://betpredz.vercel.app (Vercel redeploys on every push) |
| Python | `engine\.venv\Scripts\python.exe` (rebuilt after the move; if broken: `python -m venv engine\.venv` then `pip install -r engine\requirements.txt`) |
| Web | `cd web; npm ci; npm run dev` |
| Timer | cron-job.org job 8716884 "BetPredz" (owner's account) calls the workflow every 15 min |
| Workflow | `.github/workflows/daily-predictions.yml`; modes final / full / prices / skip chosen by `scripts/run_mode.py` |
| Windows task | "PL Predictor daily update" is DISABLED on purpose. Never enable it while GitHub runs. |

Secrets (values are NOT here and are never needed in a chat):
- GitHub repo secrets: `VAPID_PRIVATE_KEY`, `PUSH_SUBSCRIPTION` (app notifications), `NTFY_TOPIC` (ntfy).
- cron-job.org holds the fine-grained GitHub token limited to Actions on this repo.
- The public VAPID key is in `web/src/push.ts`.
- GitHub push access: Git Credential Manager (`git credential fill`), never print the token.
- An OddsPapi API key was pasted into an old chat on 2026-11-08. It is unused. Treat it as exposed
  and rotate it if the owner ever uses that account.
- To re-enable app notifications on a new phone: Money -> Notifications shows the subscription code;
  put it in the `PUSH_SUBSCRIPTION` secret. "Run workflow" with mode `test-notify` tests the chain.

## 3. Where the system is now (2026-11-19)

- Pipeline healthy: a commit "Predictions (full)" about every 6 h at 04:05, 10:05, 15:05 UTC.
  No matches in the live leagues from 9 to 19 Nov (international break); the next ones are on
  Fri 20 Nov 2026, first kick-off 22:30 EAT in the schedule file.
- Live accuracy (206 matches): log loss 0.8861 vs market 0.8949. Beat closing line 46%, mean CLV
  +0.28%. Value-bet ROI -5.6%: profitability is NOT proven. Never promise wins.
- Closing-odds vs pre-match Avg: -0.0025 log loss (CI -0.0037..-0.0013). Pinnacle vs Avg: not
  significant. So the only data-backed lever left is FRESHER PRICES as model input (test below).
- Notification bug fixed 2026-11-19: the 16 Nov check-in reminder never arrived because the
  international break had no final-odds notification to carry it. Check-in dates without matches now
  send their own reminder (first run after 07:00 EAT, `notify.py --morning`). The missed 16 Nov
  reminder rides on the 20 Nov final notification.

### Checkpoints (reminders are in `scripts/notify.py` CHECKINS)
1. Fri 20 Nov (carries the missed 16 Nov one): weekly leg-count check of the new markets,
   `python -m src.research_status`, report in `engine/reports/research_status.md`.
2. Sat 28 Nov: team overs / Draw No Bet decision, plus closing-line test with fresh Betpawa prices
   as model input (needs 200 CLV legs; 115 on 8 Nov).
3. Sat 5 Dec: new markets real-price test (300 legs).

## 4. Decisions since the last PROJECT.md status rewrite

- **Betpawa booking codes** (live): `POST https://www.betpawa.co.tz/api/sportsbook/v3/booking-number`
  body `{"selections":{"selections":[{"type":"SINGLE","selections":[<price id>]}]}}` returns
  `{"code":"..."}`. No login. `GET .../booking-number/<code>` loads it back. Code in
  `engine/src/booking_codes.py`, cache `engine/data/live/booking_codes.json`. Codes show on slips and
  in the final notification.
- **SportyBet codes: declined** (anti-bot rule). Never automate SportyBet or 1xBet, never use the
  owner's login details.
- **Task 23 merged**: research-only Betpawa price logging for E1, I2, D2, F2, SP2, G1, SC0
  (`engine/data/live/research/`), never in slips.
- **UI refresh**: glassmorphism, SOLID colours (no gradients), brand blue, light and dark, Inter
  font, today centred in the date strip, short straightforward text. Slip cards fully glass.
- **Declined or parked**: OddsPapi (Cameroon prices only), bet-bot repo, Apify (free tier is $5/month
  of usage), basketball (no free odds history), Train slip, Champions League. Candidate: tennis
  research track using tennis-data.co.uk free xlsx plus Betpawa tennis price logging.
  Kaggle UCL data: owner to check the Data tab for odds columns.
- **GitHub failures** on 9 Nov 18:15 UTC and 11 Nov 20:30/20:45 UTC were GitHub incidents
  (startup_failure), not code.
- **Claude inside the app**: a claude.ai subscription cannot be embedded; only the paid API can, and
  it would not improve accuracy. Decision: not now.
- **PWA vs APK**: stay PWA (auto-updates, push works). A Trusted Web Activity is the only APK worth
  considering, and only for a Play Store listing.
- Understat was in maintenance on 8 Nov; full runs fall back to `--no-refresh` (cached data).

## 5. Standing rules (do not break)

- Accuracy first, data-backed decisions, no made-up data, test before claiming, stay free (at most about $2).
- Sources allowed: ESPN, Betpawa public API (identified User-Agent, at least 1 s apart),
  football-data, Understat. Off-limits: SportyBet, 1xBet, SofaScore, Scores24, PredictZ, FootyStats,
  OddsPortal, FlashScore, FBref, LiveScore /api/. Never bypass bot protection.
- Overs only in slips, no unders. Excluded leagues are research-only. Do not change live models without data.
- Codex and Gemini never push or merge to `main`. Claude reviews and merges.
- Never commit `web/public/data` or `engine/data/live` from a local run. GitHub Actions publishes them.
- The owner's email is never sent to external services.

## 6. Pitfalls that cost time

- Use `engine\.venv\Scripts\python.exe`; system Python has no pytest.
- Many files use CRLF. Git Bash heredocs strip backslashes: write files with the editor tools.
- `itertuples()` renames columns like `Avg>2.5`; use dict records.
- ESPN scoreboard takes one day per request (date ranges return 400).
- `gh` CLI is not installed; use the GitHub REST API with curl.
- `--no-refresh` must make no network calls except where documented (booking codes, Betpawa prices).
- Windows console cannot print emoji by default: set `PYTHONIOENCODING=utf-8`.
- Browser check "past slip card is frosted glass" fails on this PC only because Windows
  "Transparency effects" is off, so the app (correctly) shows solid panels. Not an app bug.
