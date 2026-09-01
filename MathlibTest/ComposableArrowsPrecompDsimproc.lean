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
  let_expr Precomp.obj C inst n F X ei := ← Meta.whnfR e | return .continue
  let some i := ei.int? | return .continue
  let n' : Q(ℕ) ← Meta.whnfD n
  let some nVal := n'.nat? | return .continue
  let wrapped := (i % (nVal + 2)).toNat
  if wrapped = 0 then
    return .continue X
  else
    let _ ← synthInstanceQ q(NeZero ($n + 1))
    have k : Q(ℕ) := mkRawNatLit (wrapped - 1)
    return .continue q($F.obj (OfNat.ofNat $k : Fin ($n + 1)))

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
