#!/usr/bin/env bash
set +e
EV="$HOME/mathlib4-handoff/.handoff/evidence"
echo "detached_status=$(cat "$EV/detached-gates.status")"
echo "---wrapper---"
cat "$EV/detached-gates.wrapper.log"
echo "---full.json---"
cat "$EV/full.json"
echo "---full4_tail---"
tail -40 "$EV/full-4-1791045690805037085.log"
echo "---fingerprint_check---"
cd "$HOME/mathlib4-handoff"
python3 - <<'PY'
import hashlib, json
from pathlib import Path
repo = Path.home()/"mathlib4-handoff"
# match workflow fingerprint if possible
import sys
sys.path.insert(0, str(repo/".handoff"))
import workflow
print("current", workflow.fingerprint(repo))
for stage in ["baseline","focused","downstream","full"]:
    p = repo/".handoff/evidence"/f"{stage}.json"
    rec = json.loads(p.read_text())
    print(stage, rec.get("status"), rec.get("source_sha256"))
print("selection", (repo/".handoff/selection.json").read_text())
print("dirty:", __import__("subprocess").check_output(["git","status","--porcelain"], cwd=repo).decode())
PY
