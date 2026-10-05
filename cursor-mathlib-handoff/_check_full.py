#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
echo "=== full.json ==="
python3 - <<'PY'
import json
from pathlib import Path
p=Path('.cursor-handoff/evidence/full.json')
print(p.read_text() if p.exists() else 'MISSING')
PY
echo "=== latest full logs ==="
ls -t .cursor-handoff/evidence/full-*.log | head -8
for f in $(ls -t .cursor-handoff/evidence/full-*.log | head -4); do
  echo "---- $f (tail) ----"
  tail -n 50 "$f"
done
echo "=== processes ==="
ps -ef | grep -E 'lake|lean|workflow' | grep -v grep || echo NONE
echo "=== disk ==="
df -h / | head -2
'''

path = Path("/tmp/check_full.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
