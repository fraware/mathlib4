#!/usr/bin/env bash
set -euo pipefail
echo "=== procs ==="
ps -eo pid,cmd | grep -E 'lake|workflow.py|lean ' | grep -v grep || true
echo "=== full.json ==="
cat /home/mateo/mathlib4-handoff/.handoff/evidence/full.json | head -40
echo "=== mathlibtest remaining ==="
python3 - <<'PY'
from pathlib import Path
build=Path("/home/mateo/mathlib4-handoff/.lake/build")
n=0
for p in build.rglob("*"):
    if p.is_file() and "MathlibTest" in p.as_posix():
        n+=1
print("remaining", n)
print("mathlib", (build/"lib/lean/Mathlib").exists())
PY
echo "=== quarantines ==="
ls -d /home/mateo/mathlib4-handoff/.handoff/evidence/quarantine-mathlibtest-* 2>/dev/null
echo "=== nohup ==="
ls -l /home/mateo/mathlib4-handoff/.handoff/evidence/full-official-detached* 2>/dev/null || true
