#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
cd "$HOME/mathlib4-cursor"
STATUS=".cursor-handoff/evidence/detached-full.status"
PIDFILE=".cursor-handoff/evidence/detached-full.pid"
echo "status=$(cat "$STATUS" 2>/dev/null || echo missing)"
echo "pidfile=$(cat "$PIDFILE" 2>/dev/null || echo missing)"
if [ -f "$PIDFILE" ]; then
  pid=$(cat "$PIDFILE")
  if kill -0 "$pid" 2>/dev/null; then echo "alive=yes"; else echo "alive=no"; fi
fi
ps -ef | grep -E 'workflow.py run full|lake' | grep -v grep | head -20 || echo "no lake/workflow"
echo "=== wrapper tail ==="
tail -n 30 .cursor-handoff/evidence/detached-full.wrapper.log 2>/dev/null || true
echo "=== full.json summary ==="
python3 - <<'PY'
import json
from pathlib import Path
p=Path('.cursor-handoff/evidence/full.json')
if not p.exists():
    print('missing'); raise SystemExit
d=json.loads(p.read_text())
print('status', d.get('status'), 'error', d.get('error'))
for c in d.get('commands', []):
    print(c.get('exit_code'), c.get('argv'))
PY
'''

path = Path("/tmp/poll_detached_full.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
