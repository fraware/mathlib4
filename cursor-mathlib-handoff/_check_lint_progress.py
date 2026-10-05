#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
cd "$HOME/mathlib4-cursor"
log=.cursor-handoff/evidence/full-4-1791045690805037085.log
echo "size=$(wc -c < "$log") lines=$(wc -l < "$log")"
tail -n 40 "$log"
echo "=== children of lake lint ==="
pstree -p 1237 2>/dev/null || ps --forest -g $(ps -o sid= -p 1237) 2>/dev/null | head -40
ps -ef | grep -E 'lint|lean' | grep -v grep | head -30
'''

path = Path("/tmp/check_lint_progress.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
