#!/usr/bin/env python3
"""Launch full gate detached inside WSL so it survives host disconnects."""
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"

# Limit parallelism to reduce WSL memory pressure / crashes.
export LEAN_NUM_THREADS="${LEAN_NUM_THREADS:-2}"

mkdir -p .cursor-handoff/evidence
STATUS=".cursor-handoff/evidence/detached-full.status"
LOG=".cursor-handoff/evidence/detached-full.wrapper.log"
PIDFILE=".cursor-handoff/evidence/detached-full.pid"

# Refuse to start a second concurrent full run.
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "ALREADY_RUNNING pid=$(cat "$PIDFILE")"
  exit 0
fi

nohup bash -c '
  set -euo pipefail
  source "$HOME/.elan/env"
  cd "$HOME/mathlib4-cursor"
  export LEAN_NUM_THREADS="${LEAN_NUM_THREADS:-2}"
  STATUS=".cursor-handoff/evidence/detached-full.status"
  echo running > "$STATUS"
  set +e
  python3 .cursor-handoff/workflow.py run full > .cursor-handoff/evidence/detached-full.wrapper.log 2>&1
  ec=$?
  set -e
  if [ "$ec" -eq 0 ]; then
    echo passed > "$STATUS"
  else
    echo "failed:$ec" > "$STATUS"
  fi
  exit "$ec"
' >/dev/null 2>&1 &

echo $! > "$PIDFILE"
sleep 1
echo "STARTED pid=$(cat "$PIDFILE") status=$(cat "$STATUS") log=$LOG"
'''

path = Path("/tmp/detached_full.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
