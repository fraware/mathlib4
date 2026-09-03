from pathlib import Path
import runpy

runpy.run_path("scripts/research_composable_arrows_explicit_iso_laws.py", run_name="__main__")

four = Path("Mathlib/CategoryTheory/Abelian/DiagramLemmas/Four.lean")
text = four.read_text()
replacements = [
    (
        "(hR₂.exact 0).exact_toComposableArrows h₀ h₁ (by dsimp [ψ]; infer_instance)",
        "(hR₂.exact 0).exact_toComposableArrows h₀ h₁ (by simp [ψ]; infer_instance)",
    ),
    (
        "(exact₂_mk _ (by simp) ?_) (by dsimp [ψ]; infer_instance) h₀ h₁",
        "(exact₂_mk _ (by simp) ?_) (by simp [ψ]; infer_instance) h₀ h₁",
    ),
]
for old, new in replacements:
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one targeted Four obligation: {old!r}")
    text = text.replace(old, new)
four.write_text(text)
