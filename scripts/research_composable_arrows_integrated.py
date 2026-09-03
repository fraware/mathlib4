from pathlib import Path
import re

basic = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean")
text = basic.read_text()

workaround = '''/-!\nNew `simprocs` that run even in `dsimp` have caused breakages in this file.\n\n(e.g. `dsimp` can now simplify `2 + 3` to `5`)\n\nFor now, we just turn off the offending simprocs in this file.\n\n*However*, hopefully it is possible to refactor the material here so that no disabling of\nsimprocs is needed.\n\nSee issue https://github.com/leanprover-community/mathlib4/issues/27382.\n-/\nattribute [-simp] Fin.reduceFinMk\n\n'''
if text.count(workaround) != 1:
    raise SystemExit("expected exactly one file-wide Fin.reduceFinMk workaround")
text = text.replace(workaround, "")

marker = '''@[simp]\nlemma map_one_succ (j : ℕ) (hj : j + 1 < n + 1 + 1) :\n    map F f 1 ⟨j + 1, hj⟩ (by simp [Fin.le_def]) = F.map' 0 j := rfl\n\n'''
if text.count(marker) != 1:
    raise SystemExit("expected exactly one Precomp.map_one_succ marker")

reducer = r'''open Lean

private meta def mkFinCtor (bound value : Nat) : MetaM Expr := do
  let boundExpr := mkRawNatLit bound
  let valueExpr := mkRawNatLit value
  let ltExpr ← Meta.mkAppM ``LT.lt #[valueExpr, boundExpr]
  let h ← Meta.mkDecideProof ltExpr
  Meta.mkAppM ``Fin.mk #[valueExpr, h]

dsimproc ↓ reduceObj (Precomp.obj _ _ _) := fun e => do
  let_expr Precomp.obj _C _inst _n F X ei := ← Meta.whnfR e | return .continue
  let some ⟨bound, i⟩ ← Meta.getFinValue? ei | return .continue
  if i.val = 0 then
    return .visit X
  else if 1 < bound then
    let idx ← mkFinCtor (bound - 1) (i.val - 1)
    let result ← Meta.mkAppM ``Functor.obj #[F, idx]
    let result ← Lean.Meta.withTransparency .implicit <| Meta.whnf result
    return .visit result
  else
    return .continue

dsimproc reduceMap (Precomp.map _ _ _ _ _) := fun e => do
  let_expr Precomp.map _C _inst _n F _X f i j _hij := e | return .continue
  let some ⟨boundI, iVal⟩ ← Meta.getFinValue? i | return .continue
  let some ⟨boundJ, jVal⟩ ← Meta.getFinValue? j | return .continue
  unless boundI = boundJ do return .continue
  unless iVal.val ≤ jVal.val do return .continue
  let i' ← mkFinCtor boundI iVal.val
  let j' ← mkFinCtor boundJ jVal.val
  let leExpr ← Meta.mkAppM ``LE.le #[i', j']
  let hij ← Meta.mkDecideProof leExpr
  let result ← Meta.mkAppM ``Precomp.map #[F, f, i', j', hij]
  let result ← Lean.Meta.withTransparency .implicit <|
    Meta.whnfHeadPred result fun e => return e.isAppOf ``Precomp.map
  if result == e then
    return .continue
  else
    return .visit result

'''
text = text.replace(marker, marker + reducer)

iso3 = '''/-- Constructor for isomorphisms in `ComposableArrows C 3`. -/\n@[simps]\ndef isoMk₃ {f g : ComposableArrows C 3}\n    (app₀ : f.obj' 0 ≅ g.obj' 0) (app₁ : f.obj' 1 ≅ g.obj' 1) (app₂ : f.obj' 2 ≅ g.obj' 2)\n    (app₃ : f.obj' 3 ≅ g.obj' 3)\n    (w₀ : f.map' 0 1 ≫ app₁.hom = app₀.hom ≫ g.map' 0 1)\n    (w₁ : f.map' 1 2 ≫ app₂.hom = app₁.hom ≫ g.map' 1 2)\n    (w₂ : f.map' 2 3 ≫ app₃.hom = app₂.hom ≫ g.map' 2 3) : f ≅ g :=\n  isoMkSucc app₀ (isoMk₂ app₁ app₂ app₃ w₁ w₂) w₀\n'''
iso4 = '''/-- Constructor for isomorphisms in `ComposableArrows C 4`. -/\n@[simps]\ndef isoMk₄ {f g : ComposableArrows C 4}\n    (app₀ : f.obj' 0 ≅ g.obj' 0) (app₁ : f.obj' 1 ≅ g.obj' 1) (app₂ : f.obj' 2 ≅ g.obj' 2)\n    (app₃ : f.obj' 3 ≅ g.obj' 3) (app₄ : f.obj' 4 ≅ g.obj' 4)\n    (w₀ : f.map' 0 1 ≫ app₁.hom = app₀.hom ≫ g.map' 0 1)\n    (w₁ : f.map' 1 2 ≫ app₂.hom = app₁.hom ≫ g.map' 1 2)\n    (w₂ : f.map' 2 3 ≫ app₃.hom = app₂.hom ≫ g.map' 2 3)\n    (w₃ : f.map' 3 4 ≫ app₄.hom = app₃.hom ≫ g.map' 3 4) : f ≅ g :=\n  isoMkSucc app₀ (isoMk₃ app₁ app₂ app₃ app₄ w₁ w₂ w₃) w₀\n'''
iso5 = '''/-- Constructor for isomorphisms in `ComposableArrows C 5`. -/\n@[simps]\ndef isoMk₅ {f g : ComposableArrows C 5}\n    (app₀ : f.obj' 0 ≅ g.obj' 0) (app₁ : f.obj' 1 ≅ g.obj' 1) (app₂ : f.obj' 2 ≅ g.obj' 2)\n    (app₃ : f.obj' 3 ≅ g.obj' 3) (app₄ : f.obj' 4 ≅ g.obj' 4) (app₅ : f.obj' 5 ≅ g.obj' 5)\n    (w₀ : f.map' 0 1 ≫ app₁.hom = app₀.hom ≫ g.map' 0 1)\n    (w₁ : f.map' 1 2 ≫ app₂.hom = app₁.hom ≫ g.map' 1 2)\n    (w₂ : f.map' 2 3 ≫ app₃.hom = app₂.hom ≫ g.map' 2 3)\n    (w₃ : f.map' 3 4 ≫ app₄.hom = app₃.hom ≫ g.map' 3 4)\n    (w₄ : f.map' 4 5 ≫ app₅.hom = app₄.hom ≫ g.map' 4 5) : f ≅ g :=\n  isoMkSucc app₀ (isoMk₄ app₁ app₂ app₃ app₄ app₅ w₁ w₂ w₃ w₄) w₀\n'''

for n, replacement in [(3, iso3), (4, iso4), (5, iso5)]:
    pattern = re.compile(
        rf'/-- Constructor for isomorphisms in `ComposableArrows C {n}`\. -/\n@\[simps\]\ndef isoMk{chr(8320 + n) if False else ""}',
    )
    # Match by the stable declaration header and the following ext lemma rather than proof internals.
    block = re.compile(
        rf'/-- Constructor for isomorphisms in `ComposableArrows C {n}`\. -/\n@\[simps\]\ndef isoMk[{"₃₄₅"[n-3]}].*?(?=\nlemma ext[{"₃₄₅"[n-3]}])',
        re.DOTALL,
    )
    text, count = block.subn(replacement.rstrip(), text, count=1)
    if count != 1:
        raise SystemExit(f"expected exactly one isoMk{n} declaration")

basic.write_text(text)

consumers = [
    Path("Mathlib/Algebra/Homology/ExactSequence.lean"),
    Path("Mathlib/Algebra/Homology/HomologySequence.lean"),
    Path("Mathlib/Algebra/Homology/HomotopyCategory/ShortExact.lean"),
]
for path in consumers:
    source = path.read_text()
    source = re.sub(r'^\s*-- Disable `Fin\.reduceFinMk`[^\n]*\n', '', source, flags=re.MULTILINE)
    source = source.replace("dsimp [-Fin.reduceFinMk]", "dsimp")
    source = source.replace("simp [-Fin.reduceFinMk]", "simp")
    path.write_text(source)

for path in [basic, *consumers]:
    source = path.read_text()
    if "[-Fin.reduceFinMk]" in source or "attribute [-simp] Fin.reduceFinMk" in source:
        raise SystemExit(f"remaining Fin.reduceFinMk suppression in {path}")
