import Mathlib.CategoryTheory.ComposableArrows.Basic

open CategoryTheory CategoryTheory.Category
open CategoryTheory.ComposableArrows

open Lean Meta Elab Tactic in
/-- Inspect the reducer directly so a later `rfl` cannot hide a missing rewrite. -/
private def checkReduceMap (expectVisit : Bool) : TacticM Unit := withMainContext do
  let some (_, lhs, rhs) := (← getMainTarget).eq? |
    throwError "expected an equality goal"
  unless lhs.isAppOf ``Precomp.map do
    throwError "expected Precomp.map on the left"
  let (step, _) ← Simp.SimpM.run (← Simp.Context.mkDefault) (k := Precomp.reduceMap lhs)
  match step with
  | .visit result =>
    unless expectVisit do
      throwError "expected the reducer to decline"
    if result.isAppOf ``Precomp.map then
      throwError "reducer did not unfold Precomp.map"
    unless ← withNewMCtxDepth (isDefEq (← inferType result) (← inferType lhs)) do
      throwError "reducer changed the expression type"
    unless ← withNewMCtxDepth (isDefEq result lhs) do
      throwError "reducer violated definitional equality with its input"
    unless ← withNewMCtxDepth (isDefEq result rhs) do
      throwError "reducer returned an unexpected expression"
  | .continue none =>
    if expectVisit then
      throwError "expected the reducer to visit a reduced expression"
  | _ => throwError "unexpected reducer step"

elab "check_reduce_map_visit" : tactic => checkReduceMap true
elab "check_reduce_map_declines" : tactic => checkReduceMap false

universe u v

variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)

-- Cover each defining branch, a diagonal, and a numeral reduced modulo its bound.
example (p : (0 : Fin 4) ≤ 0) : Precomp.map F f 0 0 p = 𝟙 X := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

example (p : (0 : Fin 4) ≤ 1) : Precomp.map F f 0 1 p = f := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

example (p : (0 : Fin 4) ≤ 3) :
    Precomp.map F f 0 3 p = f ≫ F.map' 0 2 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

example (p : (1 : Fin 4) ≤ 3) : Precomp.map F f 1 3 p = F.map' 0 2 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

example (p : (2 : Fin 4) ≤ 2) : Precomp.map F f 2 2 p = F.map' 1 1 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

example (p : (5 : Fin 4) ≤ 3) : Precomp.map F f 5 3 p = F.map' 0 2 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

-- Symbolic constructor arguments must remain supported by definitional reduction.
example {n : ℕ} (G : ComposableArrows C n) {Y : C} (g : Y ⟶ G.left)
    (a b : ℕ) (ha : a + 1 < n + 1 + 1) (hb : b + 1 < n + 1 + 1)
    (p : a + 1 ≤ b + 1) :
    Precomp.map G g ⟨a + 1, ha⟩ ⟨b + 1, hb⟩ p = G.map' a b := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

section CustomNumeral

local instance : OfNat (Fin 4) 0 := ⟨⟨1, by decide⟩⟩

-- The baseline verifies the intended meaning of the nonstandard numeral.
example : Precomp.map F f 0 0 (by rfl) = F.map' 0 0 := by
  rfl

example : Precomp.map F f 0 0 (by rfl) = F.map' 0 0 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

end CustomNumeral

section CustomOrder

local instance : LE (Fin 4) := ⟨fun _ _ => False⟩
local instance (i j : Fin 4) : Decidable (i ≤ j) :=
  inferInstanceAs (Decidable False)

-- Precomp.map still expects the original, standard Fin order.
example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  rfl

example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

end CustomOrder

section CustomSecondNumeral

local instance : OfNat (Fin 4) 2 := ⟨⟨3, by decide⟩⟩

example : Precomp.map F f 1 2 (by decide) = F.map' 0 2 := by
  rfl

example : Precomp.map F f 1 2 (by decide) = F.map' 0 2 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

end CustomSecondNumeral

section EquivalentNumeral

local instance : OfNat (Fin 4) 0 := ⟨⟨0, by decide⟩⟩

example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl

end EquivalentNumeral

-- An opaque symbolic index does not expose a constructor.
example (i j : Fin 4) (p : i ≤ j) :
    Precomp.map F f i j p = Precomp.map F f i j p := by
  check_reduce_map_declines
  rfl
