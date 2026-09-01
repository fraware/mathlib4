/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow precomposition reduction experiment

Research-only probe for issue #27382. It tests whether value-aware dsimprocs can restore
`Precomp.obj` and `Precomp.map` reduction after `Fin.reduceFinMk` normalizes concrete finite
indices.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.PrecompDsimprocResearch

open Lean

/-- Build a constructor-shaped finite index so recursive definitions can reduce before the
finite-literal normalizer rewrites it. -/
private def mkFinCtor (bound value : Nat) : MetaM Expr := do
  let boundExpr := mkRawNatLit bound
  let valueExpr := mkRawNatLit value
  let ltExpr ← Meta.mkAppM ``LT.lt #[valueExpr, boundExpr]
  let h ← Meta.mkDecideProof ltExpr
  Meta.mkAppM ``Fin.mk #[valueExpr, h]

/-- Research-only probe for concrete `Precomp.obj` indices. -/
dsimproc precompObj (Precomp.obj _ _ _) := fun e => do
  let_expr Precomp.obj _C _inst _n F X ei := ← Meta.whnfR e | return .continue
  let some ⟨bound, i⟩ ← Meta.getFinValue? ei | return .continue
  if i.val = 0 then
    return .continue X
  else if 1 < bound then
    let idx ← mkFinCtor (bound - 1) (i.val - 1)
    let result ← Meta.mkAppM ``Functor.obj #[F, idx]
    let result ← Lean.Meta.withTransparency .all <| Meta.whnf result
    return .continue result
  else
    return .continue

/-- Research-only probe for concrete `Precomp.map` indices. It reconstructs constructor-shaped
indices and lets the existing `Precomp.map` definition select the appropriate branch. -/
dsimproc precompMap (Precomp.map _ _ _ _ _) := fun e => do
  let_expr Precomp.map _C _inst _n F _X f i j _hij := ← Meta.whnfR e | return .continue
  let some ⟨boundI, iVal⟩ ← Meta.getFinValue? i | return .continue
  let some ⟨boundJ, jVal⟩ ← Meta.getFinValue? j | return .continue
  unless boundI = boundJ do return .continue
  unless iVal.val ≤ jVal.val do return .continue
  let i' ← mkFinCtor boundI iVal.val
  let j' ← mkFinCtor boundJ jVal.val
  let leExpr ← Meta.mkAppM ``LE.le #[i', j']
  let hij ← Meta.mkDecideProof leExpr
  let result ← Meta.mkAppM ``Precomp.map #[F, f, i', j', hij]
  let result ← Lean.Meta.withTransparency .all <| Meta.whnf result
  return .continue result

variable {C : Type*} [Category* C]
variable {X₀ X₁ X₂ X₃ : C}
variable (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃)

example : ((mk₁ f).precomp (𝟙 X₀)).obj 0 = X₀ := by dsimp
example : ((mk₁ f).precomp (𝟙 X₀)).obj 1 = X₀ := by dsimp
example : ((mk₁ f).precomp (𝟙 X₀)).obj 2 = X₁ := by dsimp

example : ((mk₂ g h).precomp f).obj 0 = X₀ := by dsimp
example : ((mk₂ g h).precomp f).obj 1 = X₁ := by dsimp
example : ((mk₂ g h).precomp f).obj 2 = X₂ := by dsimp
example : ((mk₂ g h).precomp f).obj 3 = X₃ := by dsimp

section UpstreamContract

variable {X₄ : C} (i : X₃ ⟶ X₄)

example : map' (mk₂ f g) 0 1 = f := by dsimp
example : map' (mk₂ f g) 1 2 = g := by dsimp
example : map' (mk₂ f g) 0 2 = f ≫ g := by dsimp
example : (mk₂ f g).hom = f ≫ g := by dsimp
example : map' (mk₂ f g) 0 0 = 𝟙 _ := by dsimp
example : map' (mk₂ f g) 1 1 = 𝟙 _ := by dsimp
example : map' (mk₂ f g) 2 2 = 𝟙 _ := by dsimp

example : map' (mk₃ f g h) 0 1 = f := by dsimp
example : map' (mk₃ f g h) 1 2 = g := by dsimp
example : map' (mk₃ f g h) 2 3 = h := by dsimp
example : map' (mk₃ f g h) 0 3 = f ≫ g ≫ h := by dsimp
example : (mk₃ f g h).hom = f ≫ g ≫ h := by dsimp
example : map' (mk₃ f g h) 0 2 = f ≫ g := by dsimp
example : map' (mk₃ f g h) 1 3 = g ≫ h := by dsimp

end UpstreamContract

end CategoryTheory.ComposableArrows.PrecompDsimprocResearch
