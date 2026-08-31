/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable arrows with `Fin.reduceFinMk` enabled

Diagnostic test for issue #27382. The production module currently disables `Fin.reduceFinMk`.
This test re-enables it after import and replays the definitional-property examples for `precomp`.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows

open Category

variable {C : Type*} [Category* C]
variable {X₀ X₁ X₂ X₃ : C} (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃)

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

end CategoryTheory.ComposableArrows
