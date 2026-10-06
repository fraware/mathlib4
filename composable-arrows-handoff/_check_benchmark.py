#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
log=.handoff/evidence/full-3-1791039579347445388.log
echo "=== Benchmark error block ==="
grep -n -A40 'ClickSuggestions.Benchmark' "$log" | head -80
echo "=== file excerpt ==="
nl -ba MathlibTest/ClickSuggestions/Benchmark.lean | sed -n '1,80p'
echo "=== isolated rebuild ==="
set +e
lake build MathlibTest.ClickSuggestions.Benchmark > .handoff/evidence/benchmark-rebuild.log 2>&1
ec=$?
set -e
echo EXIT:$ec
tail -n 40 .handoff/evidence/benchmark-rebuild.log
'''

path = Path("/tmp/check_benchmark.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
