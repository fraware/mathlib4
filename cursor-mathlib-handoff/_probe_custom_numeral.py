#!/usr/bin/env python3
import subprocess
from pathlib import Path

lean = r'''
import Mathlib.CategoryTheory.ComposableArrows.Basic

open CategoryTheory CategoryTheory.Category
open CategoryTheory.ComposableArrows

universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)

section CustomNumeral
local instance : OfNat (Fin 4) 0 := ⟨⟨1, by decide⟩⟩

#check Precomp.map F f 0 0
#check (Precomp.map F f 0 0 (by rfl) : Precomp.obj F X 0 ⟶ Precomp.obj F X 0)
#check (F.map' 0 0 : F.obj ⟨0, by decide⟩ ⟶ F.obj ⟨0, by decide⟩)

example : Precomp.obj F X 0 = F.obj ⟨0, by decide⟩ := rfl
example : Precomp.map F f 0 0 (by rfl) = (𝟙 (F.obj ⟨0, by decide⟩) : _) := by
  rfl
example : Precomp.map F f 0 0 (by rfl) =
    (F.map' 0 0 : F.obj ⟨0, by decide⟩ ⟶ F.obj ⟨0, by decide⟩) := by
  rfl
end CustomNumeral
'''

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
cat > /tmp/probe_custom.lean <<'LEAN'
''' + lean + r'''
LEAN
cp /tmp/probe_custom.lean MathlibTest/ProbeCustomNumeral.lean
# keep evidence of probe
mkdir -p .cursor-handoff/evidence
cp MathlibTest/ProbeCustomNumeral.lean .cursor-handoff/evidence/probe_custom_numeral.lean
set +e
lake env lean MathlibTest/ProbeCustomNumeral.lean > .cursor-handoff/evidence/probe_custom_numeral.log 2>&1
ec=$?
set -e
echo EXIT:$ec
tail -n 80 .cursor-handoff/evidence/probe_custom_numeral.log
rm -f MathlibTest/ProbeCustomNumeral.lean
'''

path = Path("/tmp/probe_custom_numeral.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
