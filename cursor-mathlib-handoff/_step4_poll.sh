#!/usr/bin/env bash
set -euo pipefail
EV=/home/mateo/mathlib4-cursor/.cursor-handoff/evidence
echo "TIME $(date -Is)"
echo "=== procs (summary) ==="
ps -eo pid,etime,cmd | grep -E 'workflow.py|lake --iofail|lake lint|lake build' | grep -v grep || echo 'no workflow/lake'
bench=$(ps -eo pid,etime,cmd | grep 'ClickSuggestions/Benchmark.lean' | grep -v grep || true)
echo "BENCHMARK_PROC: ${bench:-none}"
echo "LEAN_COUNT: $(ps -eo cmd | grep -c '/bin/lean ' || true)"
echo
echo "=== full.json ==="
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full.json").read_text())
print("status", d.get("status"), "error", d.get("error"))
for c in d.get("commands", []):
    print(c.get("exit_code"), c.get("log"), " ".join(c.get("argv", [])[:4]))
PY
echo
echo "=== wrapper tail ==="
tail -20 "$EV/full-official-detached.wrapper.log" 2>/dev/null || true
echo
echo "=== status file ==="
cat "$EV/full-official-detached.status" 2>/dev/null || echo none
echo
latest=$(ls -t "$EV"/full-3-*.log 2>/dev/null | head -1)
echo "LATEST_FULL3 $latest bytes=$(wc -c < "$latest")"
echo "--- grep key ---"
grep -E 'Benchmark|error:|build failed|Build completed|Some required' "$latest" | tail -30 || true
echo "--- tail ---"
tail -c 800 "$latest" || true
echo
echo "=== tmux ==="
tmux ls 2>/dev/null || true
