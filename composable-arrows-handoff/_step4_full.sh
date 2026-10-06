#!/usr/bin/env bash
set -euo pipefail
# Official full gate after MathlibTest quarantine. Source unchanged: skip focused/downstream.
PRIMARY=/home/mateo/mathlib4-handoff
EV="$PRIMARY/.handoff/evidence"
export PATH="$HOME/.elan/bin:$PATH"
cd "$PRIMARY"

python3 - <<'PY'
import sys, shutil, time
from pathlib import Path
sys.path.insert(0, "/home/mateo/mathlib4-handoff/.handoff")
import workflow
repo = Path("/home/mateo/mathlib4-handoff")
fp = workflow.fingerprint(repo)
print("FINGERPRINT", fp)
if fp != "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0":
    print("SOURCE CHANGED — must run focused then downstream before full", file=sys.stderr)
    sys.exit(3)
print("SOURCE_UNCHANGED skip focused/downstream")
PY

# snapshot current full.json without deleting
if [ -f "$EV/full.json" ]; then
  cp -a "$EV/full.json" "$EV/full.json.pre-quarantine-full-$(date +%s)"
fi

if pgrep -af 'lake |workflow.py' | grep mathlib4-handoff | grep -v grep; then
  echo REFUSING competing
  exit 2
fi

echo "START_FULL $(date -Is)"
set +e
python3 .handoff/workflow.py run full
ec=$?
set -e
echo "FULL_WORKFLOW_EXIT $ec"
echo "END_FULL $(date -Is)"
exit $ec
