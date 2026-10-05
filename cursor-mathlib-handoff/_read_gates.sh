#!/usr/bin/env bash
set +e
EV="$HOME/mathlib4-cursor/.cursor-handoff/evidence"
echo "STATUS=$(cat "$EV/detached-gates.status")"
echo "PID=$(cat "$EV/detached-gates.pid")"
ps -p "$(cat "$EV/detached-gates.pid")" -o pid,etime,cmd 2>&1
echo "---WRAPPER_TAIL---"
tail -50 "$EV/detached-gates.wrapper.log"
echo "---SELECTION---"
cat "$HOME/mathlib4-cursor/.cursor-handoff/selection.json"
echo "---BASELINE---"
cat "$EV/baseline.json"
echo "---FOCUSED---"
cat "$EV/focused.json"
echo "---DOWNSTREAM---"
cat "$EV/downstream.json"
echo "---FULL---"
cat "$EV/full.json"
echo "---FULL4---"
cat "$EV/full-4-1791045690805037085.log"
echo "---REPAIRS---"
cat "$EV/harness-repairs.md"
echo "---LINT_CHILDREN---"
pstree -ap "$(cat "$EV/detached-gates.pid")" 2>/dev/null || ps --forest -g "$(ps -o sid= -p "$(cat "$EV/detached-gates.pid")" | tr -d ' ')" -o pid,etime,cmd 2>&1 | head -40
