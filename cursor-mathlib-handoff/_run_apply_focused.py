#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
python3 .cursor-handoff/workflow.py apply preferred
python3 .cursor-handoff/workflow.py run focused
'''

path = Path("/tmp/run_apply_focused.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
