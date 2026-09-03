/-
Copyright (c) 2026 Mateo Petel. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Mateo Petel
-/
import Mathlib.Algebra.Homology.HomotopyCategory.ShortExact
import Mathlib.CategoryTheory.ComposableArrows.Basic

/-!
# Composable-arrow reduction experiment

Research-only probe for issue #27382. It keeps the upstream reducibility settings unchanged and
uses narrow simplification procedures for concrete `Precomp.obj` and `Precomp.map` calls.
-/

attribute [simp] Fin.reduceFinMk

namespace CategoryTheory.ComposableArrows.PrecompReductionResearch

open Lean

private def mkFinCtor (bound value : Nat) : MetaM Expr := do
  let boundExpr := mkRawNatLit bound
  let valueExpr := mkRawNatLit value
  let ltExpr ← Meta.mkAppM ``LT.lt #[valueExpr, boundExpr]
  let h ← Meta.mkDecideProof ltExpr
  Meta.mkAppM ``Fin.mk #[valueExpr, h]

dsimproc ↓ precompObj (Precomp.obj _ _ _) := fun e => do
  let_expr Precomp.obj _C _inst _n F X ei := ← Meta.whnfR e | return .continue
  let some ⟨bound, i⟩ ← Meta.getFinValue? ei | return .continue
  if i.val = 0 then
    return .visit X
  else if 1 < bound then
    let idx ← mkFinCtor (bound - 1) (i.val - 1)
    let result ← Meta.mkAppM ``Functor.obj #[F, idx]
    let result ← Lean.Meta.withTransparency .implicit <| Meta.whnf result
    return .visit result
  else
    return .continue

dsimproc precompMap (Precomp.map _ _ _ _ _) := fun e => do
  let_expr Precomp.map _C _inst _n F _X f i j _hij := e | return .continue
  let some ⟨boundI, iVal⟩ ← Meta.getFinValue? i | return .continue
  let some ⟨boundJ, jVal⟩ ← Meta.getFinValue? j | return .continue
  unless boundI = boundJ do return .continue
  unless iVal.val ≤ jVal.val do return .continue
  let i' ← mkFinCtor boundI iVal.val
  let j' ← mkFinCtor boundJ jVal.val
  let leExpr ← Meta.mkAppM ``LE.le #[i', j']
  let hij ← Meta.mkDecideProof leExpr
  let result ← Meta.mkAppM ``Precomp.map #[F, f, i', j', hij]
  let result ← Lean.Meta.withTransparency .implicit <|
    Meta.whnfHeadPred result fun e => return e.isAppOf ``Precomp.map
  if result == e then
    return .continue
  else
    return .visit result

variable {C : Type*} [Category* C]
variable {X₀ X₁ X₂ X₃ X₄ X₅ X₆ X₇ : C}
variable (f : X₀ ⟶ X₁) (g : X₁ ⟶ X₂) (h : X₂ ⟶ X₃) (i : X₃ ⟶ X₄)
  (j : X₄ ⟶ X₅) (k : X₅ ⟶ X₆) (l : X₆ ⟶ X₇)

private abbrev mk₆' := (mk₅ g h i j k).precomp f
private abbrev mk₇' := (mk₆' g h i j k l).precomp f

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

example : map' (mk₆' f g h i j k) 0 6 = f ≫ g ≫ h ≫ i ≫ j ≫ k := by dsimp
example : map' (mk₆' f g h i j k) 3 6 = i ≫ j ≫ k := by dsimp
example : map' (mk₆' f g h i j k) 5 6 = k := by dsimp

example : map' (mk₇' f g h i j k l) 0 7 = f ≫ g ≫ h ≫ i ≫ j ≫ k ≫ l := by dsimp
example : map' (mk₇' f g h i j k l) 4 7 = j ≫ k ≫ l := by dsimp
example : map' (mk₇' f g h i j k l) 6 7 = l := by dsimp

end DeeperStress

section SymbolicSmoke

variable {n : ℕ} (F : ComposableArrows C n) (X : C) (u : X ⟶ F.left)
variable (a b : Fin (n + 1 + 1)) (hab : a ≤ b)

example : Precomp.obj F X a = Precomp.obj F X a := by dsimp
example : Precomp.map F u a b hab = Precomp.map F u a b hab := by dsimp

end SymbolicSmoke

section ExactSequenceConsumer

variable {D : Type*} [Category* D] [HasZeroMorphisms D]

set_option backward.isDefEq.respectTransparency false in
example (S : ShortComplex D) : S.toComposableArrows.IsComplex :=
  ComposableArrows.isComplex₂_mk _ (by simp)

end ExactSequenceConsumer

section HomologySequenceConsumer

open HomologicalComplex

variable {D ι : Type*} [Category* D] [Preadditive D] {c : ComplexShape ι}
  (K L : HomologicalComplex D c) (a b : ι)
  [K.HasHomology a] [K.HasHomology b] [L.HasHomology a] [L.HasHomology b]

example : (HomologySequence.composableArrows₃ K a b).map' 2 3 = K.homologyπ b := by dsimp

attribute [local simp] homologyMap_comp cyclesMap_comp opcyclesMap_comp

set_option backward.defeqAttrib.useBackward true in
noncomputable def homologySequenceFunctorProbe [CategoryWithHomology D] :
    HomologicalComplex D c ⥤ ComposableArrows D 3 where
  obj K := HomologySequence.composableArrows₃ K a b
  map {K L} φ := ComposableArrows.homMk₃ (homologyMap φ a) (opcyclesMap φ a) (cyclesMap φ b)
    (homologyMap φ b) (by simp) (by simp) (by simp)

end HomologySequenceConsumer

section HomotopyShortExactConsumer

open CategoryTheory Category ComplexShape HomotopyCategory Limits
  HomologicalComplex.HomologySequence Pretriangulated Preadditive
open CochainComplex.mappingCone

variable {D : Type*} [Category* D] [Abelian D]

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
example {S : ShortComplex (CochainComplex D ℤ)} (hS : S.ShortExact) (n : ℤ) : True := by
  let φ : ((homologyFunctor D (up ℤ) 0).homologySequenceComposableArrows₅
      (triangleh S.f) n _ rfl).δlast ⟶ (composableArrows₅ hS n _ rfl).δlast :=
    homMk₄ ((homologyFunctorFactors D (up ℤ) _).hom.app _)
      ((homologyFunctorFactors D (up ℤ) _).hom.app _)
      ((homologyFunctorFactors D (up ℤ) _).hom.app _ ≫
        HomologicalComplex.homologyMap (descShortComplex S) n)
      ((homologyFunctorFactors D (up ℤ) _).hom.app _)
      ((homologyFunctorFactors D (up ℤ) _).hom.app _)
      ((homologyFunctorFactors D (up ℤ) _).hom.naturality S.f)
      (by
        erw [(homologyFunctorFactors D (up ℤ) n).hom.naturality_assoc]
        dsimp
        rw [← HomologicalComplex.homologyMap_comp, inr_descShortComplex])
      (by
        dsimp
        erw [homologySequenceδ_triangleh hS]
        simp only [Functor.comp_obj, HomologicalComplex.homologyFunctor_obj, Category.assoc,
          Iso.inv_hom_id_app, Category.comp_id])
      ((homologyFunctorFactors D (up ℤ) _).hom.naturality S.f)
  clear φ
  trivial

end HomotopyShortExactConsumer

end CategoryTheory.ComposableArrows.PrecompReductionResearch
