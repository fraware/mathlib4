#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"

ADV="$HOME/mathlib4-handoff-adv"
PREF="$HOME/mathlib4-handoff"
EV_ADV="$ADV/.handoff/evidence"
EV_PREF="$PREF/.handoff/evidence"
mkdir -p "$EV_ADV"

HELPER='
import Mathlib.CategoryTheory.ComposableArrows.Basic

set_option linter.unusedTactic false
set_option linter.unreachableTactic false

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
variable (F : ComposableArrows C 2) {X : C} (f : X � C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)
'

run_probe() {
  local repo="$1"
  local name="$2"
  local body="$3"
  local tag="$4"
  local outdir="$5"
  local leanpath="MathlibTest/AdvProbe_${name}.lean"
  local logfile="$outdir/adv_${tag}_${name}.log"
  local srcfile="$outdir/adv_${tag}_${name}.lean"

  cd "$repo"
  printf '%s\n%s\n' "$HELPER" "$body" > "$leanpath"
  cp "$leanpath" "$srcfile"
  set +e
  lake env lean "$leanpath" > "$logfile" 2>&1
  local ec=$?
  set -e
  echo "EXIT:$ec" | tee -a "$logfile"
  echo "$tag $name exit=$ec"
  rm -f "$leanpath"
  return 0
}

echo "=== ensure adv has cache + Basic ==="
cd "$ADV"
# Prefer reusing oleans from preferred if present (same SHA base for Mathlib deps)
if [ ! -d "$ADV/.lake/packages" ] && [ -d "$PREF/.lake/packages" ]; then
  echo "linking lake packages from preferred checkout"
  mkdir -p "$ADV/.lake"
  # copy lake-manifest built artifacts via cache get is safer
fi
python3 .handoff/workflow.py run baseline

SUMMARY="$EV_ADV/adversarial-summary.md"
{
  echo "# Adversarial baseline discrimination"
  echo
  echo "- Adv checkout: \`$ADV\` (original reducer, clean HEAD)"
  echo "- Preferred checkout: \`$PREF\` (preferred reducer)"
  echo "- Base: \`$(git -C "$ADV" rev-parse HEAD)\`"
  echo "- Timestamp: $(date -Iseconds)"
  echo
  echo "## Probes (original reducer)"
  echo
} > "$SUMMARY"

# Probe A: custom numeral — wrong semantics vs non-reduction
BODY_CUSTOM='
section CustomNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩

-- Plain meaning check: custom 0 means ⟨1⟩, so map 0 0 should be F.map'\'' 0 0.
example : Precomp.map F f 0 0 (by rfl) = F.map'\'' 0 0 := by
  rfl

-- Direct reducer inspection with preferred-style expectation.
example : Precomp.map F f 0 0 (by rfl) = F.map'\'' 0 0 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
end CustomNumeral
'
run_probe "$ADV" "custom_numeral" "$BODY_CUSTOM" "original" "$EV_ADV"
echo "- custom_numeral: EXIT=$(grep -E '^EXIT:' "$EV_ADV/adv_original_custom_numeral.log" | tail -1 | cut -d: -f2)" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
tail -40 "$EV_ADV/adv_original_custom_numeral.log" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
echo >> "$SUMMARY"

# Probe B: wrong-semantics discriminator — if original reduces using standard 0, it becomes 𝟙 X
BODY_CUSTOM_WRONG='
section CustomNumeralWrongSemantics
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩

-- If the reducer canonicalizes to standard OfNat 0 (= ⟨0⟩), it yields 𝟙 X.
-- Preferred must NOT make this succeed; original MAY wrongly succeed.
example : Precomp.map F f 0 0 (by rfl) = 𝟙 X := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
end CustomNumeralWrongSemantics
'
run_probe "$ADV" "custom_numeral_wrong_sem" "$BODY_CUSTOM_WRONG" "original" "$EV_ADV"
echo "- custom_numeral_wrong_sem: EXIT=$(grep -E '^EXIT:' "$EV_ADV/adv_original_custom_numeral_wrong_sem.log" | tail -1 | cut -d: -f2)" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
tail -40 "$EV_ADV/adv_original_custom_numeral_wrong_sem.log" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
echo >> "$SUMMARY"

# Probe C: shadowing LE
BODY_LE='
section CustomOrder
local instance (priority := high) : LE (Fin (2 + 1 + 1)) := ⟨fun _ _ => False⟩
local instance (priority := high) (i j : Fin (2 + 1 + 1)) : Decidable (i ≤ j) :=
  inferInstanceAs (Decidable False)

example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  rfl

example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
end CustomOrder
'
run_probe "$ADV" "shadow_le" "$BODY_LE" "original" "$EV_ADV"
echo "- shadow_le: EXIT=$(grep -E '^EXIT:' "$EV_ADV/adv_original_shadow_le.log" | tail -1 | cut -d: -f2)" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
tail -40 "$EV_ADV/adv_original_shadow_le.log" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
echo >> "$SUMMARY"

# Probe D: confirm reducer invoked on a standard case under original
BODY_STD='
example (p : (0 : Fin 4) ≤ 1) : Precomp.map F f 0 1 p = f := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
'
run_probe "$ADV" "standard_visit" "$BODY_STD" "original" "$EV_ADV"
echo "- standard_visit: EXIT=$(grep -E '^EXIT:' "$EV_ADV/adv_original_standard_visit.log" | tail -1 | cut -d: -f2)" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
tail -20 "$EV_ADV/adv_original_standard_visit.log" >> "$SUMMARY"
echo '```' >> "$SUMMARY"
echo >> "$SUMMARY"

echo "## Probes (preferred reducer, same sources)" >> "$SUMMARY"
echo >> "$SUMMARY"

for name in custom_numeral custom_numeral_wrong_sem shadow_le standard_visit; do
  case "$name" in
    custom_numeral) body="$BODY_CUSTOM" ;;
    custom_numeral_wrong_sem) body="$BODY_CUSTOM_WRONG" ;;
    shadow_le) body="$BODY_LE" ;;
    standard_visit) body="$BODY_STD" ;;
  esac
  run_probe "$PREF" "$name" "$body" "preferred" "$EV_ADV"
  echo "- preferred/$name: EXIT=$(grep -E '^EXIT:' "$EV_ADV/adv_preferred_${name}.log" | tail -1 | cut -d: -f2)" >> "$SUMMARY"
  echo '```' >> "$SUMMARY"
  tail -30 "$EV_ADV/adv_preferred_${name}.log" >> "$SUMMARY"
  echo '```' >> "$SUMMARY"
  echo >> "$SUMMARY"
done

{
  echo "## Interpretation notes"
  echo
  echo "- custom_numeral success means the candidate/original preserves custom OfNat meaning (map equals F.map'\'' 0 0)."
  echo "- custom_numeral_wrong_sem success means reduction to 𝟙 X under custom OfNat 0:=⟨1⟩ (wrong semantics)."
  echo "- shadow_le success means reducer preserves stored LE proof / does not resynthesize under shadowed LE."
  echo "- standard_visit confirms the reducer is actually invoked on a routine case."
  echo
} >> "$SUMMARY"

# Copy into preferred evidence for export
cp -a "$EV_ADV"/adv_*.lean "$EV_ADV"/adv_*.log "$EV_ADV"/adversarial-summary.md "$EV_PREF"/
cp "$SUMMARY" "$EV_PREF/adversarial-summary.md"
echo "DONE"
cat "$SUMMARY"
