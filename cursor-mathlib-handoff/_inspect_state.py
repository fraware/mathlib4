#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
source "$HOME/.elan/env" 2>/dev/null || true
echo "=== HOME listings ==="
ls -la "$HOME/mathlib4-cursor" 2>/dev/null | head -20
echo "---"
ls -la "$HOME/.elan" 2>/dev/null | head -20
echo "=== HEAD / selection / status ==="
cd "$HOME/mathlib4-cursor" 2>/dev/null || { echo "NO_CHECKOUT"; exit 0; }
git rev-parse HEAD
git status --porcelain | head -40
echo "=== selection.json ==="
cat .cursor-handoff/selection.json 2>/dev/null || echo "NO_SELECTION"
echo "=== evidence markers ==="
ls -la .cursor-handoff/evidence 2>/dev/null | head -80
echo "=== stage json ==="
for f in baseline focused downstream full; do
  echo "--- $f.json ---"
  if [ -f ".cursor-handoff/evidence/$f.json" ]; then
    python3 - <<PY
import json
from pathlib import Path
p=Path(".cursor-handoff/evidence/$f.json")
d=json.loads(p.read_text())
print("status:", d.get("status"))
print("source:", d.get("source_sha256"))
print("error:", d.get("error"))
print("commands:", [(c.get("argv"), c.get("exit_code")) for c in d.get("commands", [])])
PY
  else
    echo MISSING
  fi
done
echo "=== processes ==="
ps -ef | grep -E 'lake|lean|workflow|python3 .*cursor' | grep -v grep || echo NONE
echo "=== disk ==="
df -h / | head -2
df -h /mnt/c 2>/dev/null | head -2 || true
'''

path = Path("/tmp/inspect_state.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
