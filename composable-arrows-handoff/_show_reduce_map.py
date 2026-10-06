#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/mathlib4-handoff"
echo "=== ReduceMap.lean ==="
nl -ba MathlibTest/ComposableArrowsReduceMap.lean
echo
echo "=== reduceMap impl ==="
nl -ba Mathlib/CategoryTheory/ComposableArrows/Basic.lean | sed -n '357,380p'
'''

path = Path("/tmp/show_reduce_map.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
