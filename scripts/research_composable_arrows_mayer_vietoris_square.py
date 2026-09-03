from pathlib import Path
import runpy

runpy.run_path("scripts/research_composable_arrows_four_simp.py", run_name="__main__")

path = Path("Mathlib/CategoryTheory/Sites/SheafCohomology/MayerVietoris.lean")
text = path.read_text()
old = "    (by dsimp; rw [comp_id, id_comp]; rfl)"
new = """    (by
      change S.δ F n₀ n₁ h ≫ 𝟙 _ = 𝟙 _ ≫ S.δ F n₀ n₁ h
      rw [comp_id, id_comp])"""
if text.count(old) != 1:
    raise SystemExit(f"expected exactly one Mayer-Vietoris middle-square proof, found {text.count(old)}")
text = text.replace(old, new)
path.write_text(text)
