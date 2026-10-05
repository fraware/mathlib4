#!/usr/bin/env bash
set -euo pipefail
REPO="${HOME}/mathlib4-cursor"
cd "$REPO"
EV="$REPO/.cursor-handoff/evidence"
mkdir -p "$EV"
nohup python3 "$REPO/.cursor-handoff/workflow.py" run full \
  > "$EV/full-rerun.wrapper.log" 2>&1 &
echo $! | tee "$EV/full-rerun.pid"
echo "started full gate pid=$(cat "$EV/full-rerun.pid")"
