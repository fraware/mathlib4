#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
cd "$HOME/mathlib4-cursor"
log=.cursor-handoff/evidence/full-3-1791039579347445388.log
echo "=== log size ==="
wc -l "$log"
echo "=== fatal markers ==="
grep -nE '✖|error:|failed|Some required targets' "$log" | head -100
echo "=== ComposableArrowsReduceMap ==="
grep -n 'ComposableArrowsReduceMap\|ComposableArrowsIntegrated' "$log" | head -40
echo "=== TacticTimeout ==="
grep -n -A5 -B2 'TacticTimeout' "$log" | head -60
echo "=== end ==="
tail -n 80 "$log"
'''

path = Path("/tmp/diagnose_test_fail.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
