from pathlib import Path
import runpy

runpy.run_path("scripts/research_composable_arrows_explicit_iso_laws.py", run_name="__main__")

four = Path("Mathlib/CategoryTheory/Abelian/DiagramLemmas/Four.lean")
text = four.read_text()
mono_last = "(by\n    change Mono ((homMk₃ _ _ _ _ _ _ _).app ⟨3, by valid⟩)\n    rw [homMk₃_app_three]\n    infer_instance)"
replacements = [
    (
        "(hR₂.exact 0).exact_toComposableArrows h₀ h₁ (by dsimp [ψ]; infer_instance)",
        f"(hR₂.exact 0).exact_toComposableArrows h₀ h₁ {mono_last}",
    ),
    (
        "h₀ h₁ (by dsimp [ψ]; infer_instance)",
        f"h₀ h₁ {mono_last}",
    ),
]
for old, new in replacements:
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one targeted Four obligation: {old!r}")
    text = text.replace(old, new)
four.write_text(text)
