#!/usr/bin/env bash
set -euo pipefail
EV=/home/mateo/mathlib4-cursor/.cursor-handoff/evidence
date -Is
echo ===TMUX===
tmux ls 2>&1 || true
echo ===PROCS===
ps -eo pid,etime,pcpu,pmem,cmd | grep -E 'workflow.py|lake |lean ' | grep -v grep || echo none
echo ===FULLJSON===
python3 - <<'PY'
import json
from pathlib import Path
p = Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full.json")
r = json.loads(p.read_text())
print("status", r.get("status"), "err", r.get("error", "")[:120])
for c in r.get("commands", []):
    print(c["argv"], "exit=", c.get("exit_code"), "log=", c.get("log"))
print("finished", r.get("finished_unix"))
PY
echo ===WRAPPER_TAIL===
tail -15 "$EV/full-official-detached.wrapper.log" 2>&1 || true
echo ===LATEST_LOG===
latest=$(ls -t "$EV"/full-[1234]-*.log 2>/dev/null | head -1 || true)
if [ -n "${latest:-}" ]; then
  echo "file=$latest bytes=$(wc -c < "$latest")"
  tail -c 800 "$latest" | tr '\r' '\n' | tail -20
fi
echo ===STATUS_FILE===
cat "$EV/full-official-detached.status" 2>&1 || echo no_status_yet
echo ===RAM===
free -h | head -2
