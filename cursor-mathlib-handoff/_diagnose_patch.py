#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
echo "HEAD=$(git rev-parse HEAD)"
echo "STATUS:"
git status --porcelain
echo "--- file around 356 ---"
nl -ba Mathlib/CategoryTheory/ComposableArrows/Basic.lean | sed -n '340,400p'
echo "--- apply check verbose ---"
git apply --check --verbose .cursor-handoff/patches/preferred.patch || true
echo "--- grep reduceMap ---"
rg -n "reduceMap|getFinValue|dsimproc" Mathlib/CategoryTheory/ComposableArrows/Basic.lean || true
'''

path = Path("/tmp/diagnose_patch.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
