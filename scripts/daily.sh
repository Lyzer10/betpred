#!/usr/bin/env bash
# Daily update, run by Windows Task Scheduler on this PC:
# refresh data, predict upcoming matches with live Betpawa odds, publish to GitHub
# (Vercel then redeploys the app). Output goes to engine/data/live/daily.log.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
git pull --rebase --autostash origin main
(cd engine && .venv/Scripts/python.exe -m src.predict)
git add web/public/data/predictions.json web/public/data/archive engine/data/live/slip_history.json
if git diff --cached --quiet; then
  echo "No changes to publish"
else
  git commit -q -m "Daily predictions $(date -u +%F)"
  git push -q origin main
  echo "Published"
fi
