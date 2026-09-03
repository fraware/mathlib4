from pathlib import Path
import re
import runpy

runpy.run_path("scripts/research_composable_arrows_four_simp.py", run_name="__main__")

basic = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean")
text = basic.read_text()

old_obj = '''@[implicit_reducible]\ndef obj : Fin (n + 1 + 1) → C\n  | ⟨0, _⟩ => X\n  | ⟨i + 1, hi⟩ => F.obj' i\n'''
new_obj = '''@[implicit_reducible]\ndef obj : Fin (n + 1 + 1) → C := Fin.cases X F.obj\n'''
if text.count(old_obj) != 1:
    raise SystemExit("expected exactly one Precomp.obj pattern definition")
text = text.replace(old_obj, new_obj)

reduce_obj = re.compile(
    r'dsimproc ↓ reduceObj \(Precomp\.obj _ _ _\) := fun e => do\n.*?(?=dsimproc reduceMap)',
    re.DOTALL,
)
if len(reduce_obj.findall(text)) != 1:
    raise SystemExit("expected exactly one reduceObj dsimproc")
text = reduce_obj.sub('', text, count=1)

basic.write_text(text)
