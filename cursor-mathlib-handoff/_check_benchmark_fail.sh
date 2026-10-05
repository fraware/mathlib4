#!/usr/bin/env bash
set -euo pipefail
LOG=/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-3-1791215707344718178.log
echo ===BENCHMARK_CONTEXT===
grep -n -E 'Benchmark|build failed|error:|Some required|Build completed|✖|✔ \[92' "$LOG" | tail -50
echo ===TAIL===
tail -c 1500 "$LOG" | tr '\r' '\n' | tail -30
echo ===STATUS===
cat /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full.json | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["status"], d.get("error","")[:200]); print([(c["argv"][-1] if c["argv"] else c, c.get("exit_code")) for c in d["commands"]])'
ps -eo pid,etime,cmd | grep -E 'workflow.py|lake ' | grep -v grep || echo none
test -f /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.status && cat /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.status || echo no_status
