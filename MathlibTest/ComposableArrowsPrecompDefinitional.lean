/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow definitional reduction experiment

Research-only probe for issue #27382. This tests whether expressing `Precomp.obj` through
`Fin.cases` is enough to recover the intended `dsimp` behavior with `Fin.reduceFinMk` enabled,
without custom simplification procedures.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.PrecompDefinitionalResearch

open Category

variable {C : Type*} [Category* C]
variable {n : ℕ}

@[implicit_reducible]
def objCases (F : ComposableArrows C n) (X : C) : Fin (n + 1 + 1) → C :=
  Fin.cases X fun i => F.obj i

@[simp]
lemma objCases_zero (F : ComposableArrows C n) (X : C) : objCases F X 0 = X := rfl

@[simp]
lemma objCases_succ (F : ComposableArrows C n) (X : C) (i : Fin (n + 1)) :
    objCases F X i.succ = F.obj i := rfl

@[implicit_reducible]
def precompCases (F : ComposableArrows C n) {X : C} (f : X ⟶ F.left) :
    ComposableArrows C (n + 1) where
  obj := objCases F X
  map g := Precomp.map F f _ _ (leOfHom g)
  map_id := Precomp.map_id F f
  map_comp g g' := Precomp.map_comp F f (leOfHom g) (leOfHom g')

abbrev mk₂Cases {X₀ X₁ X₂ : C} (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) : ComposableArrows C 2 :=
  precompCases (mk₁ g) f

abbrev mk₃Cases {X₀ X₁ X₂ X₃ : C} (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃) :
    ComposableArrows C 3 :=
  precompCases (mk₂Cases g h) f

variable {X₀ X₁ X₂ X₃ : C}
variable (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃)

section ObjectReduction

example : (precompCases (mk₁ f) (𝟙 X₀)).obj 0 = X₀ := by dsimp
example : (precompCases (mk₁ f) (𝟙 X₀)).obj 1 = X₀ := by dsimp
example : (precompCases (mk₁ f) (𝟙 X₀)).obj 2 = X₁ := by dsimp

example : (precompCases (mk₂Cases g h) f).obj 0 = X₀ := by dsimp
example : (precompCases (mk₂Cases g h) f).obj 1 = X₁ := by dsimp
example : (precompCases (mk₂Cases g h) f).obj 2 = X₂ := by dsimp
example : (precompCases (mk₂Cases g h) f).obj 3 = X₃ := by dsimp

end ObjectReduction

section MapReduction

example : map' (mk₂Cases f g) 0 1 = f := by dsimp
example : map' (mk₂Cases f g) 1 2 = g := by dsimp
example : map' (mk₂Cases f g) 0 2 = f ≫ g := by dsimp
example : (mk₂Cases f g).hom = f ≫ g := by dsimp
example : map' (mk₂Cases f g) 0 0 = 𝟙 _ := by dsimp
example : map' (mk₂Cases f g) 1 1 = 𝟙 _ := by dsimp
example : map' (mk₂Cases f g) 2 2 = 𝟙 _ := by dsimp

example : map' (mk₃Cases f g h) 0 1 = f := by dsimp
example : map' (mk₃Cases f g h) 1 2 = g := by dsimp
example : map' (mk₃Cases f g h) 2 3 = h := by dsimp
example : map' (mk₃Cases f g h) 0 3 = f ≫ g ≫ h := by dsimp
example : (mk₃Cases f g h).hom = f ≫ g ≫ h := by dsimp
example : map' (mk₃Cases f g h) 0 2 = f ≫ g := by dsimp
example : map' (mk₃Cases f g h) 1 3 = g ≫ h := by dsimp

end MapReduction

end CategoryTheory.ComposableArrows.PrecompDefinitionalResearch
