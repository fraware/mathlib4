#!/usr/bin/env bash
set +e
EV=/home/mateo/mathlib4-handoff/.handoff/evidence
echo ===FAIL_TAIL===
tail -c 4000 "$EV/full-3-1791215707344718178.log"
echo
echo ===FAIL_GREP===
grep -E 'Benchmark|error:|build failed|Killed|oom|Out of memory|guard|Some required' "$EV/full-3-1791215707344718178.log" | tail -50
echo ===OOM_MANIFEST===
cat "$EV/quarantine-mathlibtest-20261005T085416-after-oom/QUARANTINE_MANIFEST.json"
echo ===PRIOR_FAIL_GREP===
grep -E 'Benchmark|error:|build failed|Killed|oom|Out of memory|Some required' "$EV/full-3-1791213939582217433.log" | tail -30
echo ===SIDECAR===
ls /home/mateo/mathlib4-handoff/.handoff/*.sha256 /mnt/c/Users/mateo/mathlib4-1/composable-arrows-handoff/*.sha256 2>&1
echo ===CLASS===
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("/home/mateo/mathlib4-handoff/.handoff/evidence/benchmark-diagnosis/CLASSIFICATION.json").read_text())
print(d.get("classification"), d.get("continue_candidate"))
print("note:", d.get("note","")[:200])
PY
echo ===FOCUSED_DOWN===
python3 - <<'PY'
import json
from pathlib import Path
for n in ("focused","downstream","baseline"):
 p=Path(f"/home/mateo/mathlib4-handoff/.handoff/evidence/{n}.json")
 if p.exists():
  d=json.loads(p.read_text())
  print(n, d.get("status"), (d.get("source_sha256") or "")[:16])
 else:
  print(n, "MISSING")
PY
echo ===LAKE_NOW===
pgrep -af lake || echo no-lake
pgrep -af workflow.py || echo no-workflow
echo ===TMUX_CAPTURE===
tmux capture-pane -t mathlib-full -p -S -30 2>&1 | tail -40
