#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
cat > MathlibTest/ProbeObj3.lean <<'LEAN'
import Mathlib.CategoryTheory.ComposableArrows.Basic
open CategoryTheory CategoryTheory.Category CategoryTheory.ComposableArrows
universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)

section CustomNumeral
-- Match the index type Precomp.map actually uses.
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩

set_option pp.explicit true in
#check (0 : Fin (2 + 1 + 1))
#check Precomp.map F f 0 0

#reduce (0 : Fin (2 + 1 + 1))
#reduce Precomp.obj F X 0
example : Precomp.obj F X 0 = F.obj' 0 := rfl
example : Precomp.map F f 0 0 (by rfl) = F.map' 0 0 := by
  rfl
end CustomNumeral

section CustomSecondNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 2 := ⟨⟨3, by decide⟩⟩
example : Precomp.map F f 1 2 (by decide) = F.map' 0 2 := by
  rfl
end CustomSecondNumeral

section EquivalentNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨0, by decide⟩⟩
example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  rfl
end EquivalentNumeral
LEAN
set +e
lake env lean MathlibTest/ProbeObj3.lean > .cursor-handoff/evidence/probe_obj3.log 2>&1
ec=$?
set -e
echo EXIT:$ec
cat .cursor-handoff/evidence/probe_obj3.log
cp MathlibTest/ProbeObj3.lean .cursor-handoff/evidence/probe_obj3.lean
rm -f MathlibTest/ProbeObj3.lean
'''

path = Path("/tmp/probe_obj3.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
