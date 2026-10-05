#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
git status --porcelain
python3 .cursor-handoff/workflow.py run baseline
'''

path = Path("/tmp/run_baseline.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
