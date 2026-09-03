/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.Algebra.Homology.HomotopyCategory.ShortExact

namespace CategoryTheory.ComposableArrows.ProductionProbe

open Category

variable {C : Type*} [Category* C]
variable {X₀ X₁ X₂ X₃ X₄ X₅ X₆ X₇ : C}
variable (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃) (i : X₃ ⟶ X₄)
  (j : X₄ ⟶ X₅) (k : X₅ ⟶ X₆) (l : X₆ ⟶ X₇)

private abbrev mk₆' := (mk₅ g h i j k).precomp f
private abbrev mk₇' := (mk₆' g h i j k l).precomp f

example : map' (mk₄ f g h i) 0 4 = f ≫ g ≫ h ≫ i := by dsimp
example : map' (mk₄ f g h i) 2 4 = h ≫ i := by dsimp
example : map' (mk₅ f g h i j) 0 5 = f ≫ g ≫ h ≫ i ≫ j := by dsimp
example : map' (mk₅ f g h i j) 4 5 = j := by dsimp
example : map' (mk₆' f g h i j k) 0 6 = f ≫ g ≫ h ≫ i ≫ j ≫ k := by dsimp
example : map' (mk₆' f g h i j k) 5 6 = k := by dsimp
example : map' (mk₇' f g h i j k l) 0 7 = f ≫ g ≫ h ≫ i ≫ j ≫ k ≫ l := by dsimp
example : map' (mk₇' f g h i j k l) 6 7 = l := by dsimp

variable {n : ℕ} (F : ComposableArrows C n) (X : C) (u : X ⟶ F.left)
variable (a b : Fin (n + 1 + 1)) (hab : a ≤ b)

example : Precomp.obj F X a = Precomp.obj F X a := by dsimp
example : Precomp.map F u a b hab = Precomp.map F u a b hab := by dsimp

end CategoryTheory.ComposableArrows.ProductionProbe
