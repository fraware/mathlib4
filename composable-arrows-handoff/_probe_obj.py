#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
python3 - <<'PY'
from pathlib import Path
text = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean").read_text().splitlines()
for i,l in enumerate(text,1):
    if "namespace Precomp" in l or l.strip().startswith("def obj") or l.strip().startswith("def map") or "abbrev obj" in l or "Protected" in l and "obj" in l:
        print(f"{i}:{l}")
# broader search
for i,l in enumerate(text,1):
    if "obj" in l and ("def " in l or "abbrev " in l or "let " in l) and "Precomp" in "".join(text[max(0,i-30):i]):
        if i>250 and i<340:
            print(f"ctx {i}:{l}")
PY
echo '==== Precomp section ===='
nl -ba Mathlib/CategoryTheory/ComposableArrows/Basic.lean | sed -n '250,340p'
cat > MathlibTest/ProbeObj.lean <<'LEAN'
import Mathlib.CategoryTheory.ComposableArrows.Basic
open CategoryTheory CategoryTheory.Category CategoryTheory.ComposableArrows
universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)
section CustomNumeral
local instance : OfNat (Fin 4) 0 := ⟨⟨1, by decide⟩⟩
#reduce Precomp.obj F X 0
#reduce (0 : Fin 4)
#check (0 : Fin 4)
#print prefix Precomp.obj
example : (0 : Fin 4) = ⟨1, by decide⟩ := rfl
end CustomNumeral
LEAN
set +e
lake env lean MathlibTest/ProbeObj.lean > .handoff/evidence/probe_obj.log 2>&1
ec=$?
set -e
echo EXIT:$ec
cat .handoff/evidence/probe_obj.log
rm -f MathlibTest/ProbeObj.lean
'''

path = Path("/tmp/probe_obj.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
