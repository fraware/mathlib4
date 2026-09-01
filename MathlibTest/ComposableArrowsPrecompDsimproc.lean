/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow precomposition reduction experiment

Research-only probe for issue #27382. It tests whether a value-aware dsimproc can restore
`Precomp.obj` reduction after `Fin.reduceFinMk` normalizes concrete finite indices.
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

end CategoryTheory.ComposableArrows.PrecompDsimprocResearch
