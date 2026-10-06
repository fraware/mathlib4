#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
# Keep a copy of the interrupted test log for evidence before marker overwrite.
cp -f .handoff/evidence/full-3-1791036665172218338.log \
  .handoff/evidence/full-3-interrupted-before-rerun.log 2>/dev/null || true
python3 .handoff/workflow.py run full
'''

path = Path("/tmp/rerun_full.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
