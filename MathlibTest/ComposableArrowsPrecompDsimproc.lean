/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow precomposition reduction experiment

Research-only probe for issue #27382. It tests whether an outer dsimproc can restore
`Precomp.obj` reduction after `Fin.reduceFinMk` normalizes the index representation.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.PrecompDsimprocResearch

open Lean Meta

/-- Research-only probe: eta-expand the normalized `Fin` scrutinee before reducing `Precomp.obj`. -/
dsimproc precompObj (Precomp.obj _ _ _) := fun e => do
  let i := e.appArg!
  let val ← Meta.mkAppM ``Fin.val #[i]
  let isLt ← Meta.mkAppM ``Fin.isLt #[i]
  let i' ← Meta.mkAppM ``Fin.mk #[val, isLt]
  let e' := Expr.app e.appFn! i'
  let r ← Meta.whnfR e'
  if r == e then
    return .continue
  else
    return .continue r

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
