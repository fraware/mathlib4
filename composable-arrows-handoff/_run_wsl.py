#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import sys

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
git status --porcelain
echo "=== lake env lean --version ==="
lake env lean --version
echo "=== SUCCESS ==="
'''

path = Path("/tmp/run_wsl.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
