#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
# Extract relevant definitions
python3 - <<'PY'
from pathlib import Path
text = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean").read_text()
for key in ["def obj", "def map ", "def map'", "dsimproc reduceMap"]:
    i = text.find(key)
    print(f"==== {key} @ {i} ====")
    if i >= 0:
        print(text[i:i+500])
        print()
PY
'''

path = Path("/tmp/probe_types.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
