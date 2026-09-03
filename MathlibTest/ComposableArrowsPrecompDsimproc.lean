/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow reducibility experiment

Research-only probe for issue #27382. It tests whether ordinary reducibility of `Precomp.obj`
and `Precomp.map` is sufficient to preserve the intended `dsimp` behavior with
`Fin.reduceFinMk` enabled.
-/

attribute [simp] Fin.reduceFinMk

set_option allowUnsafeReducibility true in
attribute [local reducible] CategoryTheory.ComposableArrows.Precomp.obj
  CategoryTheory.ComposableArrows.Precomp.map

namespace CategoryTheory.ComposableArrows.PrecompReducibilityResearch

variable {C : Type*} [Category* C]
variable {X₀ X₁ X₂ X₃ X₄ X₅ : C}
variable (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃) (i : X₃ ⟶ X₄) (j : X₄ ⟶ X₅)

section ObjectReduction

example : ((mk₁ f).precomp (𝟙 X₀)).obj 0 = X₀ := by dsimp
example : ((mk₁ f).precomp (𝟙 X₀)).obj 1 = X₀ := by dsimp
example : ((mk₁ f).precomp (𝟙 X₀)).obj 2 = X₁ := by dsimp

example : ((mk₂ g h).precomp f).obj 0 = X₀ := by dsimp
example : ((mk₂ g h).precomp f).obj 1 = X₁ := by dsimp
example : ((mk₂ g h).precomp f).obj 2 = X₂ := by dsimp
example : ((mk₂ g h).precomp f).obj 3 = X₃ := by dsimp

end ObjectReduction

section UpstreamContract

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

section DeeperStress

example : map' (mk₄ f g h i) 0 4 = f ≫ g ≫ h ≫ i := by dsimp
example : map' (mk₄ f g h i) 2 4 = h ≫ i := by dsimp
example : map' (mk₄ f g h i) 3 3 = 𝟙 _ := by dsimp

example : map' (mk₅ f g h i j) 0 5 = f ≫ g ≫ h ≫ i ≫ j := by dsimp
example : map' (mk₅ f g h i j) 2 5 = h ≫ i ≫ j := by dsimp
example : map' (mk₅ f g h i j) 4 5 = j := by dsimp

end DeeperStress

end CategoryTheory.ComposableArrows.PrecompReducibilityResearch
