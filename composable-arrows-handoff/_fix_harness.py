#!/usr/bin/env python3
"""Repair preferred regression harness: OfNat (Fin 4) does not apply to Fin (n+1+1)."""
from pathlib import Path
import subprocess

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
python3 - <<'PY'
from pathlib import Path
path = Path("MathlibTest/ComposableArrowsReduceMap.lean")
text = path.read_text(encoding="utf-8")
old = text
# Replace concrete Fin 4 OfNat/LE instances with the index type Precomp.map uses.
replacements = [
    ("local instance : OfNat (Fin 4) 0 := ⟨⟨1, by decide⟩⟩",
     "local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩"),
    ("local instance : LE (Fin 4) := ⟨fun _ _ => False⟩",
     "local instance (priority := high) : LE (Fin (2 + 1 + 1)) := ⟨fun _ _ => False⟩"),
    ("local instance (i j : Fin 4) : Decidable (i ≤ j) :=\n  inferInstanceAs (Decidable False)",
     "local instance (priority := high) (i j : Fin (2 + 1 + 1)) : Decidable (i ≤ j) :=\n  inferInstanceAs (Decidable False)"),
    ("local instance : OfNat (Fin 4) 2 := ⟨⟨3, by decide⟩⟩",
     "local instance : OfNat (Fin (2 + 1 + 1)) 2 := ⟨⟨3, by decide⟩⟩"),
    ("local instance : OfNat (Fin 4) 0 := ⟨⟨0, by decide⟩⟩",
     "local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨0, by decide⟩⟩"),
]
for a,b in replacements:
    if a not in text:
        raise SystemExit(f"missing expected snippet:\n{a}")
    text = text.replace(a,b)
if text == old:
    raise SystemExit("no changes made")
path.write_text(text, encoding="utf-8", newline="\n")
print("Updated", path)
print(path.read_text(encoding="utf-8"))
PY
# Persist rationale in evidence
mkdir -p .handoff/evidence
cat > .handoff/evidence/harness-repairs.md <<'MD'
# Harness repairs

## OfNat instance type (preferred regression)

Symptom: `CustomNumeral` / `CustomSecondNumeral` examples failed to elaborate with
`F.map' ...` type mismatches against `Precomp.obj F X ...`.

Cause: `local instance : OfNat (Fin 4) _` does not apply when elaborating
`Precomp.map` indices of type `Fin (n + 1 + 1)` (here `n = 2`). Instance search
uses `Fin.instOfNat` instead, so numeral `0` keeps standard meaning `⟨0,_⟩` while
the expected RHS assumes the custom meaning. Probes under
`.handoff/evidence/probe_obj3.*` confirm `OfNat (Fin (2 + 1 + 1))`
selects the custom instance and makes the examples typecheck.

Change: use `OfNat (Fin (2 + 1 + 1))` for custom/equivalent numeral sections.

## LE / Decidable shadowing

Also retargeted to `Fin (2 + 1 + 1)` with `priority := high` so the local
instances can override `instLEFin` during these examples. If that proves too
strong for `Nat.zero_le` proofs, further adjust with documented rationale.
MD
'''

path = Path("/tmp/fix_harness.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
