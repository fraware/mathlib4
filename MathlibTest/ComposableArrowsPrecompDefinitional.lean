/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow value-based reduction experiment

Research-only probe for issue #27382. This tests whether matching on the numeric value of a
`Fin` index, instead of destructuring its constructor, remains definitionally reducible after
`Fin.reduceFinMk` canonicalizes concrete indices.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.PrecompDefinitionalResearch

variable {C : Type*} [Category* C]
variable {n : ℕ}

@[implicit_reducible]
def objVal (F : ComposableArrows C n) (X : C) (i : Fin (n + 1 + 1)) : C :=
  match h : i.val with
  | 0 => X
  | k + 1 => F.obj' k (by
      have hi := i.isLt
      omega)

variable {X₀ X₁ X₂ : C}
variable (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂)

example : objVal (mk₁ f) X₀ 0 = X₀ := by dsimp
example : objVal (mk₁ f) X₀ 1 = X₀ := by dsimp
example : objVal (mk₁ f) X₀ 2 = X₁ := by dsimp

example : objVal (mk₂ f g) X₀ 0 = X₀ := by dsimp
example : objVal (mk₂ f g) X₀ 1 = X₀ := by dsimp
example : objVal (mk₂ f g) X₀ 2 = X₁ := by dsimp
example : objVal (mk₂ f g) X₀ 3 = X₂ := by dsimp

variable (F : ComposableArrows C n) (X : C) (i : Fin (n + 1 + 1))
example : objVal F X i = objVal F X i := by dsimp

end CategoryTheory.ComposableArrows.PrecompDefinitionalResearch
