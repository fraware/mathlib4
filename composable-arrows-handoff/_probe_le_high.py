#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
cat > MathlibTest/ProbeLEHigh.lean <<'LEAN'
import Mathlib.CategoryTheory.ComposableArrows.Basic
open CategoryTheory CategoryTheory.Category CategoryTheory.ComposableArrows
universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)
section CustomOrder
local instance (priority := high) : LE (Fin (2 + 1 + 1)) := ⟨fun _ _ => False⟩
local instance (priority := high) (i j : Fin (2 + 1 + 1)) : Decidable (i ≤ j) :=
  inferInstanceAs (Decidable False)
set_option pp.explicit true in
#check Precomp.map F f 0 1
example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  rfl
end CustomOrder
LEAN
set +e
lake env lean MathlibTest/ProbeLEHigh.lean > .handoff/evidence/probe_le_high.log 2>&1
ec=$?
set -e
echo EXIT:$ec
cat .handoff/evidence/probe_le_high.log
rm -f MathlibTest/ProbeLEHigh.lean
'''

path = Path("/tmp/probe_le_high.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
