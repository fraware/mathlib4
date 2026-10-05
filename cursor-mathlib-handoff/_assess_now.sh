#!/usr/bin/env bash
set +e
date -Is
echo "=== PRESERVE / DIAG ==="
ls -la /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/preserved-benchmark-fail 2>&1 | head -20
ls -la /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/benchmark-diagnosis 2>&1 | head -20
echo "=== QUARANTINE (latest) ==="
ls -ltd /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/quarantine-mathlibtest-* 2>/dev/null | head -8
echo "=== QUARANTINE NAMES HEAD ==="
ls /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/quarantine-* 2>/dev/null | head
echo "=== FULL.JSON ==="
python3 - <<'PY'
import json
from pathlib import Path
p = Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full.json")
print(json.loads(p.read_text()) if p.exists() else "MISSING")
PY
echo "=== ZIP ==="
ls -la /home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip* 2>&1
ls -la /mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff/cursor-validation-evidence.zip* 2>&1
echo "=== PROCS ==="
pgrep -af lake | head -5
pgrep -af tmux | head -5
pgrep -af 'workflow.py' | head -5
ps -eo pid,etime,pcpu,pmem,cmd | grep -E '[l]ake|[l]ean |[w]orkflow.py|[t]mux' | head -20
echo "=== TMUX ==="
tmux ls 2>&1 || echo no-tmux
echo "=== MT COUNT / FP ==="
python3 - <<'PY'
import sys
from pathlib import Path
b = Path("/home/mateo/mathlib4-cursor/.lake/build")
n = sum(1 for p in b.rglob("*") if p.is_file() and "MathlibTest" in p.as_posix()) if b.exists() else -1
print("mathlibtest_files", n)
print("mathlib_cache", (b / "lib/lean/Mathlib").exists() if b.exists() else False)
sys.path.insert(0, "/home/mateo/mathlib4-cursor/.cursor-handoff")
import workflow
print("FINGERPRINT", workflow.fingerprint(Path("/home/mateo/mathlib4-cursor")))
PY
echo "=== LATEST FULL LOGS ==="
ls -lt /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-*.log 2>/dev/null | head -8
echo "=== WRAPPER ==="
tail -40 /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.wrapper.log 2>&1
echo "=== COLD RERUN MANIFEST ==="
ls -ltd /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/quarantine-mathlibtest-*-cold-rerun 2>/dev/null | head -3
for d in /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/quarantine-mathlibtest-*-cold-rerun; do
  [ -d "$d" ] || continue
  echo "DIR $d"
  cat "$d/QUARANTINE_MANIFEST.json" 2>/dev/null
done
echo "=== SUMMARY SCOPE ==="
python3 - <<'PY'
import json
from pathlib import Path
p = Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/SUMMARY.json")
if p.exists():
    d = json.loads(p.read_text())
    print("scope", d.get("scope"))
    print("full", d.get("gates", d).get("full") if isinstance(d.get("gates"), dict) else d.get("full"))
    print("keys", list(d.keys())[:20])
else:
    print("SUMMARY MISSING")
PY
echo "=== EXECUTOR SCRIPT ==="
ls -la /mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff/_executor_step3_4.sh 2>&1
