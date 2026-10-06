#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
cat > MathlibTest/ProbeObj2.lean <<'LEAN'
import Mathlib.CategoryTheory.ComposableArrows.Basic
open CategoryTheory CategoryTheory.Category CategoryTheory.ComposableArrows
universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X � v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)

section CustomNumeral
local instance : OfNat (Fin 4) 0 := ⟨⟨1, by decide⟩⟩

#reduce (0 : Fin 4)
#reduce Precomp.obj F X (0 : Fin 4)
#reduce Precomp.obj F X ⟨1, by decide⟩
#reduce Precomp.map F f (0 : Fin 4) (0 : Fin 4) (by rfl)

set_option pp.explicit true in
#check Precomp.obj F X 0

example : Precomp.obj F X ⟨1, by decide⟩ = F.obj' 0 := rfl
example : Precomp.obj F X (0 : Fin 4) = F.obj' 0 := rfl
example : Precomp.map F f ⟨1, by decide⟩ ⟨1, by decide⟩ (by decide) = F.map' 0 0 := by
  rfl
example : Precomp.map F f (0 : Fin 4) (0 : Fin 4) (by rfl) = F.map' 0 0 := by
  rfl
end CustomNumeral
LEAN
set +e
lake env lean MathlibTest/ProbeObj2.lean > .handoff/evidence/probe_obj2.log 2>&1
ec=$?
set -e
echo EXIT:$ec
cat .handoff/evidence/probe_obj2.log
cp MathlibTest/ProbeObj2.lean .handoff/evidence/probe_obj2.lean
rm -f MathlibTest/ProbeObj2.lean
'''

path = Path("/tmp/probe_obj2.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
