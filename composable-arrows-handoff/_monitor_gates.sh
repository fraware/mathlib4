#!/usr/bin/env bash
set +e
EV="$HOME/mathlib4-handoff/.handoff/evidence"
echo "time=$(date -Iseconds)"
echo "status=$(cat "$EV/detached-gates.status" 2>/dev/null)"
if [ -f "$EV/detached-gates.pid" ]; then
  PID=$(cat "$EV/detached-gates.pid")
  if ps -p "$PID" >/dev/null 2>&1; then
    echo "pid=$PID alive"
    ps -p "$PID" -o etime= | awk '{print "elapsed="$1}'
  else
    echo "pid=$PID dead"
  fi
fi
echo "---wrapper_tail---"
tail -20 "$EV/detached-gates.wrapper.log"
echo "---full_json---"
python3 - <<'PY'
import json
from pathlib import Path
p=Path.home()/"mathlib4-handoff/.handoff/evidence/full.json"
print(p.read_text() if p.exists() else "missing")
PY
echo "---full4_tail---"
tail -30 "$EV"/full-4-*.log 2>/dev/null | tail -30
echo "---procs---"
ps -eo pid,etime,cmd | grep -E 'runLinter|workflow.py run full|lake lint' | grep -v grep || echo none
