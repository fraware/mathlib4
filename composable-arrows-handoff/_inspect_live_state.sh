#!/usr/bin/env bash
set -uo pipefail
EV=/home/mateo/mathlib4-handoff/.handoff/evidence
PRIMARY=/home/mateo/mathlib4-handoff

echo "=== HOST ==="
uname -a
nproc
free -h
uptime

echo "=== PROCS lake/lean/workflow/python/tmux ==="
ps -eo pid,etime,cmd | grep -E 'lake|lean |workflow.py|python|tmux' | grep -v grep || echo NONE

echo "=== TMUX ==="
tmux ls 2>&1 || echo no-tmux-server

echo "=== preserved-benchmark-fail ==="
ls -la "$EV/preserved-benchmark-fail" 2>&1 | head -40

echo "=== benchmark-diagnosis ==="
ls -la "$EV/benchmark-diagnosis" 2>&1 | head -40
if [ -f "$EV/benchmark-diagnosis/CLASSIFICATION.json" ]; then
  echo "--- CLASSIFICATION ---"
  cat "$EV/benchmark-diagnosis/CLASSIFICATION.json"
fi
if [ -f "$EV/benchmark-diagnosis/comparison.json" ]; then
  echo "--- comparison ---"
  cat "$EV/benchmark-diagnosis/comparison.json"
fi

echo "=== quarantine dirs ==="
ls -lad "$EV"/quarantine-mathlibtest-* 2>&1 | head -40

echo "=== MathlibTest remaining in .lake/build ==="
python3 - <<'PY'
from pathlib import Path
build=Path("/home/mateo/mathlib4-handoff/.lake/build")
n=0
if build.exists():
    for p in build.rglob("*"):
        if p.is_file() and "MathlibTest" in p.as_posix():
            n+=1
print("remaining_MathlibTest_files", n)
print("mathlib_dir", (build/"lib/lean/Mathlib").exists())
PY

echo "=== markers ==="
for f in baseline.json focused.json downstream.json full.json SUMMARY.json; do
  if [ -f "$EV/$f" ]; then
    echo "--- $f ---"
    cat "$EV/$f"
    echo
  else
    echo "MISSING $f"
  fi
done

echo "=== latest full logs ==="
ls -lt "$EV"/full-* 2>/dev/null | head -25
echo "=== detached ==="
ls -la "$EV"/full-official-detached* 2>/dev/null || echo none
if [ -f "$EV/full-official-detached.wrapper.log" ]; then
  echo "--- wrapper ---"
  cat "$EV/full-official-detached.wrapper.log"
fi
if [ -f "$EV/full-official-detached.status" ]; then
  echo "--- status ---"
  cat "$EV/full-official-detached.status"
fi

echo "=== fingerprint ==="
export PATH="$HOME/.elan/bin:$PATH"
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "/home/mateo/mathlib4-handoff/.handoff")
import workflow
fp = workflow.fingerprint(Path("/home/mateo/mathlib4-handoff"))
print("FINGERPRINT", fp)
print("EXPECTED", "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0")
print("MATCH", fp == "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0")
PY

echo "=== HEAD / status ==="
cd "$PRIMARY"
git rev-parse HEAD
git status --porcelain | head -30

echo "=== export patch check (comparison in SUMMARY writer) ==="
grep -n 'comparison\|MEMBER_SHA256\|sidecar\|baseline discrimination' "$PRIMARY/.handoff/workflow.py" | head -40

echo "=== latest full-3 tail ==="
latest=$(ls -t "$EV"/full-3-*.log 2>/dev/null | head -1 || true)
if [ -n "${latest:-}" ]; then
  echo "LATEST $latest bytes $(wc -c < "$latest")"
  tail -c 1200 "$latest"
  echo
  grep -E 'Benchmark|error:|build failed|Build completed|PASS|FAIL' "$latest" | tail -30 || true
fi

echo "INSPECT_DONE"
