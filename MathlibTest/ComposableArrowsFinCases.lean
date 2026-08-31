/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# `Fin.cases` experiment for composable-arrow precomposition

Research-only candidate for issue #27382. Keep the existing transparent `Precomp.obj` definition and
test whether decomposing only the map indices through `Fin.cases` makes the intended reductions
stable when `Fin.reduceFinMk` is enabled.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.FinCasesResearch

open Category

variable {C : Type*} [Category* C]
variable {n : ℕ} (F : ComposableArrows C n)
variable {X : C} (f : X ⟶ F.left)

@[implicit_reducible]
def map : ∀ (i j : Fin (n + 1 + 1)) (_ : i ≤ j),
    Precomp.obj F X i ⟶ Precomp.obj F X j :=
  fun i => Fin.cases
    (fun j => Fin.cases
      (fun _ => 𝟙 X)
      (fun j' => Fin.cases
        (fun _ => f)
        (fun k _ => f ≫ F.map (homOfLE (Nat.zero_le _)))
        j')
      j)
    (fun i' j => Fin.cases
      (fun hij => False.elim (by omega))
      (fun j' hij => F.map (homOfLE (Nat.le_of_succ_le_succ hij)))
      j)
    i

variable {X₀ X₁ X₂ X₃ : C} (f₀ : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃)

example : map (mk₁ g) f₀ 0 0 (by simp) = 𝟙 X₀ := by dsimp
example : map (mk₁ g) f₀ 0 1 (by simp) = f₀ := by dsimp
example : map (mk₁ g) f₀ 1 2 (by simp) = g := by dsimp
example : map (mk₁ g) f₀ 0 2 (by simp) = f₀ ≫ g := by dsimp
example : map (mk₁ g) f₀ 2 2 (by simp) = 𝟙 X₂ := by dsimp

example : map (mk₂ g h) f₀ 1 2 (by simp) = g := by dsimp
example : map (mk₂ g h) f₀ 2 3 (by simp) = h := by dsimp
example : map (mk₂ g h) f₀ 0 3 (by simp) = f₀ ≫ g ≫ h := by dsimp
example : map (mk₂ g h) f₀ 0 2 (by simp) = f₀ ≫ g := by dsimp
example : map (mk₂ g h) f₀ 1 3 (by simp) = g ≫ h := by dsimp

end CategoryTheory.ComposableArrows.FinCasesResearch
