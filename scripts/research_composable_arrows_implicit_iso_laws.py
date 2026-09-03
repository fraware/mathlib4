from pathlib import Path
import runpy

runpy.run_path("scripts/research_composable_arrows_four_simp.py", run_name="__main__")

basic = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean")
text = basic.read_text()

law_fields = [
    '''\n  hom_inv_id :=\n    (isoMkSucc app₀ (isoMk₂ app₁ app₂ app₃ w₁ w₂) w₀).hom_inv_id\n  inv_hom_id :=\n    (isoMkSucc app₀ (isoMk₂ app₁ app₂ app₃ w₁ w₂) w₀).inv_hom_id''',
    '''\n  hom_inv_id :=\n    (isoMkSucc app₀ (isoMk₃ app₁ app₂ app₃ app₄ w₁ w₂ w₃) w₀).hom_inv_id\n  inv_hom_id :=\n    (isoMkSucc app₀ (isoMk₃ app₁ app₂ app₃ app₄ w₁ w₂ w₃) w₀).inv_hom_id''',
    '''\n  hom_inv_id :=\n    (isoMkSucc app₀ (isoMk₄ app₁ app₂ app₃ app₄ app₅ w₁ w₂ w₃ w₄) w₀).hom_inv_id\n  inv_hom_id :=\n    (isoMkSucc app₀ (isoMk₄ app₁ app₂ app₃ app₄ app₅ w₁ w₂ w₃ w₄) w₀).inv_hom_id''',
]
for fields in law_fields:
    if text.count(fields) != 1:
        raise SystemExit("expected exactly one explicit iso-law block")
    text = text.replace(fields, "")

basic.write_text(text)
