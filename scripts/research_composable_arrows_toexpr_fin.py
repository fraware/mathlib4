from pathlib import Path
import runpy

runpy.run_path("scripts/research_composable_arrows_mayer_vietoris_square.py", run_name="__main__")

basic = Path("Mathlib/CategoryTheory/ComposableArrows/Basic.lean")
text = basic.read_text()
start_marker = "open Lean\n\nprivate meta def mkFinCtor"
end_marker = "\n\nlemma map_id"
if text.count(start_marker) != 1:
    raise SystemExit(f"expected exactly one old reducer start, found {text.count(start_marker)}")
start = text.index(start_marker)
end = text.index(end_marker, start)

reducer = r'''open Lean

dsimproc ↓ reduceObj (Precomp.obj _ _ _) := fun e => do
  let_expr Precomp.obj _C _inst _n F X ei := ← Meta.whnfR e | return .continue
  let some ⟨bound, i⟩ ← Meta.getFinValue? ei | return .continue
  if h₀ : i.val = 0 then
    return .visit X
  else if 1 < bound then
    have hi : i.val - 1 < bound - 1 :=
      Nat.sub_lt_sub_right (Nat.one_le_iff_ne_zero.mpr h₀) i.isLt
    let idx := toExpr (⟨i.val - 1, hi⟩ : Fin (bound - 1))
    let result ← Meta.mkAppM ``Functor.obj #[F, idx]
    let result ← Lean.Meta.withTransparency .implicit <| Meta.whnf result
    return .visit result
  else
    return .continue

dsimproc reduceMap (Precomp.map _ _ _ _ _) := fun e => do
  let_expr Precomp.map _C _inst _n F _X f i j _hij := e | return .continue
  let some ⟨boundI, iVal⟩ ← Meta.getFinValue? i | return .continue
  let some ⟨boundJ, jVal⟩ ← Meta.getFinValue? j | return .continue
  unless boundI = boundJ do return .continue
  unless iVal.val ≤ jVal.val do return .continue
  let i' := toExpr iVal
  let j' := toExpr jVal
  let leExpr ← Meta.mkAppM ``LE.le #[i', j']
  let hij ← Meta.mkDecideProof leExpr
  let result ← Meta.mkAppM ``Precomp.map #[F, f, i', j', hij]
  let result ← Lean.Meta.withTransparency .implicit <|
    Meta.whnfHeadPred result fun e => return e.isAppOf ``Precomp.map
  if result == e then
    return .continue
  else
    return .visit result'''

text = text[:start] + reducer + text[end:]
if "mkFinCtor" in text:
    raise SystemExit("old Fin constructor helper remains")
basic.write_text(text)
