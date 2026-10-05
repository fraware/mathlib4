#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
echo "Free disk (Windows host managed separately)"
df -h / | head -2
echo "Removing corrupted build artifacts..."
rm -rf .lake/build
echo "Re-fetching mathlib cache..."
lake exe cache get
echo "Smoke-building Basic..."
lake build Mathlib.CategoryTheory.ComposableArrows.Basic
echo "CACHE_REPAIR_OK"
'''

path = Path("/tmp/repair_cache.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
