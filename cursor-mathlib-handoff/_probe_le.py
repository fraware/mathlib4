#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
cat > MathlibTest/ProbeLE.lean <<'LEAN'
import Mathlib.CategoryTheory.ComposableArrows.Basic
open CategoryTheory CategoryTheory.Category CategoryTheory.ComposableArrows
universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)

section CustomOrder
local instance : LE (Fin (2 + 1 + 1)) := ⟨fun _ _ => False⟩
local instance (i j : Fin (2 + 1 + 1)) : Decidable (i ≤ j) :=
  inferInstanceAs (Decidable False)

#check (0 ≤ 1 : Prop)
-- Can we still feed a Nat inequality proof into Precomp.map?
#check Nat.zero_le 1
-- Try with standard Fin LE proof shape via val
example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  rfl
end CustomOrder
LEAN
set +e
lake env lean MathlibTest/ProbeLE.lean > .cursor-handoff/evidence/probe_le.log 2>&1
ec=$?
set -e
echo EXIT:$ec
cat .cursor-handoff/evidence/probe_le.log
cp MathlibTest/ProbeLE.lean .cursor-handoff/evidence/probe_le.lean
rm -f MathlibTest/ProbeLE.lean
'''

path = Path("/tmp/probe_le.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
