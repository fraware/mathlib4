from pathlib import Path
import runpy

runpy.run_path("scripts/research_composable_arrows_explicit_iso_laws.py", run_name="__main__")

four = Path("Mathlib/CategoryTheory/Abelian/DiagramLemmas/Four.lean")
text = four.read_text()
old = "(by dsimp [ψ]; infer_instance)"
if text.count(old) != 2:
    raise SystemExit(f"expected exactly two fragile Four obligations, found {text.count(old)}")
text = text.replace(old, "(by simp [ψ]; infer_instance)")
four.write_text(text)
