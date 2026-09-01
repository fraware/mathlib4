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

open Lean Qq

/-- Research-only probe for numeric `Precomp.obj` indices. -/
dsimproc precompObj (Precomp.obj _ _ _) := fun e => do
  let_expr Precomp.obj _C _inst n F X ei := ← Meta.whnfR e | return .continue
  let some i := ei.int? | return .continue
  let n' ← Meta.whnfD n
  let some nInt := n'.int? | return .continue
  let nVal := nInt.toNat
  let wrapped := (i % (nVal + 2)).toNat
  if wrapped = 0 then
    return .continue X
  else
    have : NeZero (nVal + 1) := ⟨Nat.succ_ne_zero _⟩
    let idx := toExpr (Fin.ofNat (nVal + 1) (wrapped - 1))
    let result ← Meta.mkAppM ``Functor.obj #[F, idx]
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

end CategoryTheory.ComposableArrows.PrecompDsimprocResearch
