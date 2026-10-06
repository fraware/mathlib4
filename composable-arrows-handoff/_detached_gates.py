#!/usr/bin/env python3
"""Detached focused -> downstream -> full after source fingerprint change."""
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"

STATUS=".handoff/evidence/detached-gates.status"
PIDFILE=".handoff/evidence/detached-gates.pid"
LOG=".handoff/evidence/detached-gates.wrapper.log"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "ALREADY_RUNNING pid=$(cat "$PIDFILE")"
  exit 0
fi

# Keep Benchmark under its 60s wall-clock guard by reducing Lean threads.
export LEAN_NUM_THREADS=1

nohup bash -c '
  set -euo pipefail
  source "$HOME/.elan/env"
  cd "$HOME/mathlib4-handoff"
  export LEAN_NUM_THREADS=1
  STATUS=".handoff/evidence/detached-gates.status"
  LOG=".handoff/evidence/detached-gates.wrapper.log"
  echo running > "$STATUS"
  set +e
  {
    echo "=== focused ==="
    python3 .handoff/workflow.py run focused || exit 11
    echo "=== downstream ==="
    python3 .handoff/workflow.py run downstream || exit 12
    echo "=== full ==="
    python3 .handoff/workflow.py run full || exit 13
  } > "$LOG" 2>&1
  ec=$?
  set -e
  if [ "$ec" -eq 0 ]; then echo passed > "$STATUS"; else echo "failed:$ec" > "$STATUS"; fi
  exit "$ec"
' >/dev/null 2>&1 &

echo $! > "$PIDFILE"
sleep 1
echo "STARTED pid=$(cat "$PIDFILE") status=$(cat "$STATUS")"
'''

path = Path("/tmp/detached_gates.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
