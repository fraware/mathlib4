#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-cursor
EV="$PRIMARY/.cursor-handoff/evidence"
export PATH="$HOME/.elan/bin:$PATH"
cd "$PRIMARY"
LOG="$EV/full-official-detached.wrapper.log"
echo "DETACHED_START $(date -Is)" | tee -a "$LOG"
python3 - <<'PY' | tee -a "$LOG"
import sys
from pathlib import Path
sys.path.insert(0, "/home/mateo/mathlib4-cursor/.cursor-handoff")
import workflow
print("FINGERPRINT", workflow.fingerprint(Path("/home/mateo/mathlib4-cursor")))
PY
set +e
python3 .cursor-handoff/workflow.py run full >>"$LOG" 2>&1
ec=$?
set -e
echo "FULL_WORKFLOW_EXIT $ec" | tee -a "$LOG"
echo "DETACHED_END $(date -Is)" | tee -a "$LOG"
echo $ec > "$EV/full-official-detached.status"
exit $ec
