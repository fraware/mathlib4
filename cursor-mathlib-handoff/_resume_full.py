#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
echo "=== fingerprint / selection ==="
python3 - <<'PY'
from pathlib import Path
import hashlib, json, subprocess
# mirror workflow fingerprint if possible by importing
import sys
sys.path.insert(0, str(Path('.cursor-handoff').resolve()))
import workflow
print('current_fp', workflow.fingerprint(Path('.').resolve()))
print('focused', json.loads(Path('.cursor-handoff/evidence/focused.json').read_text())['source_sha256'])
print('downstream', json.loads(Path('.cursor-handoff/evidence/downstream.json').read_text())['source_sha256'])
print('full_marker', json.loads(Path('.cursor-handoff/evidence/full.json').read_text()))
print('selection', json.loads(Path('.cursor-handoff/selection.json').read_text()))
PY
echo "=== full-2 log tail ==="
tail -n 40 .cursor-handoff/evidence/full-2-1790981849120333762.log || true
echo "=== rerunning full ==="
python3 .cursor-handoff/workflow.py run full
'''

path = Path("/tmp/resume_full.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
