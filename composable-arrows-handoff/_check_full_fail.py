#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
cd "$HOME/mathlib4-handoff"
echo "=== full.json ==="
cat .handoff/evidence/full.json
echo
latest=$(ls -t .handoff/evidence/full-3-*.log | head -1)
echo "LATEST_TEST_LOG=$latest"
echo "=== failures / errors ==="
grep -E 'error:|✖|failed|STOP' "$latest" | head -80
echo "=== TacticTimeout context ==="
grep -n -A3 -B3 'TacticTimeout' "$latest" | head -80
echo "=== log end ==="
tail -n 60 "$latest"
'''

path = Path("/tmp/check_full_fail.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
