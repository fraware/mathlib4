#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/mathlib4-cursor"
echo "=== focused.json ==="
cat .cursor-handoff/evidence/focused.json
echo
echo "=== latest focused logs ==="
ls -t .cursor-handoff/evidence/focused-*.log | head -5
latest=$(ls -t .cursor-handoff/evidence/focused-*.log | head -1)
echo "LATEST=$latest"
tail -n 120 "$latest"
'''

path = Path("/tmp/read_focused_fail.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
