#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
python3 - <<'PY'
from pathlib import Path
path = Path("MathlibTest/ComposableArrowsReduceMap.lean")
text = path.read_text(encoding="utf-8")
needle = "import Mathlib.CategoryTheory.ComposableArrows.Basic\n\n"
insert = """import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
`check_reduce_map_*` intentionally inspects without changing the goal, and
`dsimp only [Precomp.reduceMap]` often closes the goal before `rfl`. Disable
unused/unreachable tactic linters so `lake --iofail test` does not treat those
expected no-ops as failures.
-/
set_option linter.unusedTactic false
set_option linter.unreachableTactic false

"""
if "set_option linter.unusedTactic false" in text:
    print("already patched")
else:
    if needle not in text:
        raise SystemExit("import needle missing")
    text = text.replace(needle, insert, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("patched", path)

# Append rationale to harness-repairs.md
rep = Path(".handoff/evidence/harness-repairs.md")
extra = """

## unused/unreachable tactic linters under `--iofail`

Symptom: `lake --iofail test` failed listing `MathlibTest.ComposableArrowsReduceMap`
after only unused/unreachable tactic warnings from `check_reduce_map_*` and from
`dsimp ... <;> rfl` when `dsimp` already closed the goal.

Cause: the inspection tactics are designed not to modify the goal; `--iofail`
treats those linter warnings as failures.

Change: disable `linter.unusedTactic` and `linter.unreachableTactic` in the
regression file with an explanatory module comment. Expectations and reducer
checks are unchanged.
"""
if "under `--iofail`" not in rep.read_text(encoding="utf-8"):
    rep.write_text(rep.read_text(encoding="utf-8") + extra, encoding="utf-8")
    print("updated harness-repairs.md")
PY

# Fingerprint will change; focused/downstream markers become stale for full.
# Re-run focused then downstream then full as required by the runner.
python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.handoff').resolve()))
import workflow
print('new_fp', workflow.fingerprint(Path('.').resolve()))
PY
'''

path = Path("/tmp/fix_harness_iofail.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
