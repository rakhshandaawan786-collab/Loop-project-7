#!/bin/bash
# Simulates the scheduled heartbeat firing, with an impossible success
# condition ("zero TODOs left") and a hard cap — so a doomed run stops
# cleanly instead of retrying forever.

MAX_TRIES=3
attempt=1
LOGFILE="run.log"

while [ $attempt -le $MAX_TRIES ]; do
  echo "--- scheduled fire: attempt $attempt/$MAX_TRIES ---"
  python3 morning_brief.py

  TODO_COUNT=$(python3 -c "import json; print(len(json.load(open('.brief_state.json'))))" 2>/dev/null || echo "unknown")

  if [ "$TODO_COUNT" == "0" ]; then
    echo "SUCCESS: zero TODOs remaining."
    exit 0
  fi

  echo "Not done: $TODO_COUNT TODOs still remain (condition: must be 0)."
  attempt=$((attempt+1))
done

TS=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$TS] ERROR: hit cap of $MAX_TRIES tries — success condition ('0 TODOs') never met" >> "$LOGFILE"
cat >> progress.md << EOF2

## $(date +%Y-%m-%d)
**⚠️ NEEDS HUMAN — hit retry cap ($MAX_TRIES tries) without meeting success condition.** The repo has real, unresolved TODOs — this condition can only be met by someone fixing them, not by retrying.
EOF2

echo "🛑 Hit the cap. Logged and marked NEEDS HUMAN — not retrying forever."
exit 1
