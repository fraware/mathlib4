from pathlib import Path
import re
import runpy

runpy.run_path("scripts/research_composable_arrows_explicit_iso_laws.py", run_name="__main__")

basic = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean")
text = basic.read_text()
pattern = re.compile(r'open Lean\n\nprivate meta def mkFinCtor.*?(?=lemma map_id)', re.DOTALL)
text, count = pattern.subn('', text, count=1)
if count != 1:
    raise SystemExit(f"expected exactly one research dsimproc block, found {count}")
basic.write_text(text)
