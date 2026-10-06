#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
cd "$HOME/mathlib4-handoff"
echo "status=$(cat .handoff/evidence/detached-gates.status 2>/dev/null || echo missing)"
echo "pid=$(cat .handoff/evidence/detached-gates.pid 2>/dev/null || echo missing)"
pid=$(cat .handoff/evidence/detached-gates.pid 2>/dev/null || true)
if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then echo alive=yes; else echo alive=no; fi
ps -ef | grep -E 'workflow.py run|bin/lake' | grep -v grep | head -15 || echo none
echo "=== wrapper tail ==="
tail -n 25 .handoff/evidence/detached-gates.wrapper.log 2>/dev/null || true
echo "=== markers ==="
python3 - <<'PY'
import json
from pathlib import Path
for name in ['focused','downstream','full']:
    p=Path(f'.handoff/evidence/{name}.json')
    if not p.exists():
        print(name, 'missing'); continue
    d=json.loads(p.read_text())
    print(name, d.get('status'), d.get('source_sha256','')[:16], 'err=', d.get('error'))
PY
'''

path = Path("/tmp/poll_detached_gates.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
