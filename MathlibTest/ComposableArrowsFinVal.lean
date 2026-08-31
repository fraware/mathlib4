/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Value-based composable-arrow precomposition experiment

Research-only probe for issue #27382. This tests whether dispatching on the underlying natural-number
value of a `Fin` index preserves the intended object reductions when `Fin.reduceFinMk` is enabled.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.FinValResearch

variable {C : Type*} [Category* C]
variable {n : ℕ} (F : ComposableArrows C n)

@[implicit_reducible]
def obj (X : C) (i : Fin (n + 1 + 1)) : C :=
  match i.val with
  | 0 => X
  | k + 1 => F.obj' k (by omega)

variable {X₀ X₁ X₂ X₃ : C} (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃)

example : obj (mk₁ g) X₀ 0 = X₀ := by dsimp
example : obj (mk₁ g) X₀ 1 = X₁ := by dsimp
example : obj (mk₁ g) X₀ 2 = X₂ := by dsimp

example : obj (mk₂ g h) X₀ 0 = X₀ := by dsimp
example : obj (mk₂ g h) X₀ 1 = X₁ := by dsimp
example : obj (mk₂ g h) X₀ 2 = X₂ := by dsimp
example : obj (mk₂ g h) X₀ 3 = X₃ := by dsimp

end CategoryTheory.ComposableArrows.FinValResearch
