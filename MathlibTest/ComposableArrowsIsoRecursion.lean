/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.CategoryTheory.ComposableArrows.Basic

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.IsoRecursionResearch

variable {C : Type*} [Category* C]

/-- Research-only recursive form of `isoMk₃`. -/
def isoMk₃' {f g : ComposableArrows C 3}
    (app₀ : f.obj' 0 ≅ g.obj' 0) (app₁ : f.obj' 1 ≅ g.obj' 1) (app₂ : f.obj' 2 ≅ g.obj' 2)
    (app₃ : f.obj' 3 ≅ g.obj' 3)
    (w₀ : f.map' 0 1 ≫ app₁.hom = app₀.hom ≫ g.map' 0 1)
    (w₁ : f.map' 1 2 ≫ app₂.hom = app₁.hom ≫ g.map' 1 2)
    (w₂ : f.map' 2 3 ≫ app₃.hom = app₂.hom ≫ g.map' 2 3) : f ≅ g :=
  isoMkSucc app₀ (isoMk₂ app₁ app₂ app₃ w₁ w₂) w₀

/-- Research-only recursive form of `isoMk₄`. -/
def isoMk₄' {f g : ComposableArrows C 4}
    (app₀ : f.obj' 0 ≅ g.obj' 0) (app₁ : f.obj' 1 ≅ g.obj' 1) (app₂ : f.obj' 2 ≅ g.obj' 2)
    (app₃ : f.obj' 3 ≅ g.obj' 3) (app₄ : f.obj' 4 ≅ g.obj' 4)
    (w₀ : f.map' 0 1 ≫ app₁.hom = app₀.hom ≫ g.map' 0 1)
    (w₁ : f.map' 1 2 ≫ app₂.hom = app₁.hom ≫ g.map' 1 2)
    (w₂ : f.map' 2 3 ≫ app₃.hom = app₂.hom ≫ g.map' 2 3)
    (w₃ : f.map' 3 4 ≫ app₄.hom = app₃.hom ≫ g.map' 3 4) : f ≅ g :=
  isoMkSucc app₀ (isoMk₃' app₁ app₂ app₃ app₄ w₁ w₂ w₃) w₀

/-- Research-only recursive form of `isoMk₅`. -/
def isoMk₅' {f g : ComposableArrows C 5}
    (app₀ : f.obj' 0 ≅ g.obj' 0) (app₁ : f.obj' 1 ≅ g.obj' 1) (app₂ : f.obj' 2 ≅ g.obj' 2)
    (app₃ : f.obj' 3 ≅ g.obj' 3) (app₄ : f.obj' 4 ≅ g.obj' 4) (app₅ : f.obj' 5 ≅ g.obj' 5)
    (w₀ : f.map' 0 1 ≫ app₁.hom = app₀.hom ≫ g.map' 0 1)
    (w₁ : f.map' 1 2 ≫ app₂.hom = app₁.hom ≫ g.map' 1 2)
    (w₂ : f.map' 2 3 ≫ app₃.hom = app₂.hom ≫ g.map' 2 3)
    (w₃ : f.map' 3 4 ≫ app₄.hom = app₃.hom ≫ g.map' 3 4)
    (w₄ : f.map' 4 5 ≫ app₅.hom = app₄.hom ≫ g.map' 4 5) : f ≅ g :=
  isoMkSucc app₀ (isoMk₄' app₁ app₂ app₃ app₄ app₅ w₁ w₂ w₃ w₄) w₀

end CategoryTheory.ComposableArrows.IsoRecursionResearch
