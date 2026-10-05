#!/usr/bin/env bash
set -euo pipefail
date -Is
echo ===TMUX===
tmux ls 2>&1 || true
echo ===PROCS===
ps -eo pid,etime,pcpu,pmem,cmd | grep -E 'lake |workflow.py|tmux' | grep -v grep || echo none
echo ===FULLJSON===
cat /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full.json 2>&1 || true
echo
echo ===WRAPPER===
tail -30 /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.wrapper.log 2>&1 || true
echo ===PRESERVE===
ls /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/preserved-benchmark-fail 2>&1 | head
echo ===DIAG===
ls /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/benchmark-diagnosis 2>&1 | head
echo ===Q===
ls -ltd /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/quarantine-mathlibtest-* 2>&1 | head -8
echo ===LOGS===
ls -lt /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-*.log 2>&1 | head -8
echo ===MT_COUNT===
python3 -c 'from pathlib import Path; b=Path("/home/mateo/mathlib4-cursor/.lake/build"); print(sum(1 for p in b.rglob("*") if p.is_file() and "MathlibTest" in p.as_posix())); print("mathlib",(b/"lib/lean/Mathlib").exists())'
echo ===FP===
python3 -c 'import sys; from pathlib import Path; sys.path.insert(0,"/home/mateo/mathlib4-cursor/.cursor-handoff"); import workflow; print(workflow.fingerprint(Path("/home/mateo/mathlib4-cursor")))'
echo ===ZIP===
ls -l /home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip* /mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff/cursor-validation-evidence.zip* 2>&1 | head
echo ===SCOPE===
grep -n 'scope\|comparison' /home/mateo/mathlib4-cursor/.cursor-handoff/workflow.py | head -20
