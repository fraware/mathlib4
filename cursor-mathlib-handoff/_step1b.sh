#!/usr/bin/env bash
set -euo pipefail
echo "==== json refs ===="
grep -l 1791084123470358418 /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/* 2>/dev/null || true
echo "==== find Benchmark primary ===="
find /home/mateo/mathlib4-cursor/.lake -iname '*Benchmark*' 2>/dev/null | head -80
echo "==== find Benchmark adv ===="
find /home/mateo/mathlib4-cursor-adv/.lake -iname '*Benchmark*' 2>/dev/null | head -80
echo "==== ClickSuggestions dirs ===="
find /home/mateo/mathlib4-cursor/.lake/build -type d -name 'ClickSuggestions' 2>/dev/null
find /home/mateo/mathlib4-cursor-adv/.lake/build -type d -name 'ClickSuggestions' 2>/dev/null
echo "==== workflow helpers ===="
python3 - <<'PY'
import sys
sys.path.insert(0, "/home/mateo/mathlib4-cursor/.cursor-handoff")
import workflow
print([n for n in dir(workflow) if any(k in n.lower() for k in ("sha","finger","source","hash"))])
print("source_sha256", workflow.source_sha256() if hasattr(workflow, "source_sha256") else "no")
PY
