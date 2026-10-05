#!/usr/bin/env python3
"""Build and run elaborating adversarial probes on original vs preferred checkouts.

Probes live under <preferred>/.cursor-handoff/evidence/adversarial/.
Each probe is compiled with `lake env lean` in the chosen checkout after copying
the probe source into MathlibTest/ (cleaned afterward).
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import textwrap
import time
from datetime import datetime, timezone

PREFERRED = pathlib.Path.home() / "mathlib4-cursor"
ADV = pathlib.Path.home() / "mathlib4-cursor-adv"
OUT = PREFERRED / ".cursor-handoff" / "evidence" / "adversarial"
BASE = "a3cfff85f9dfe0b1c6b6e92899febc338687fcc3"

HELPER = r'''
import Mathlib.CategoryTheory.ComposableArrows.Basic

open CategoryTheory CategoryTheory.Category
open CategoryTheory.ComposableArrows
open Lean Meta Elab Tactic

/-- Inspect reducer then close by rfl (same contract as preferred harness). -/
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
  evalTactic (← `(tactic| rfl))

elab "check_reduce_map_visit" : tactic => checkReduceMap true
elab "check_reduce_map_declines" : tactic => checkReduceMap false

universe u v
variable {C : Type u} [Category.{v} C]
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)
'''

# Wrong-semantics probe that ALWAYS elaborates:
# run reduceMap on custom-OfNat map; require visit + type preservation +
# defeq to actual meaning; FAIL if reduced form isDefEq to the standard-zero
# identity on X (only when types allow that comparison).
WRONG_SEM_FIRST = r'''
section WrongSemFirst
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩

open Lean Meta Elab Tactic in
/-- Elaborating discrimination: custom `0 := ⟨1⟩` must not collapse to `𝟙 X`. -/
elab "check_not_std_zero_identity" : tactic => withMainContext do
  let lhs ← elabTerm (← `(Precomp.map F f (0 : Fin (2 + 1 + 1)) (0 : Fin (2 + 1 + 1)) (by rfl))) none
  let expected ← elabTerm (← `(F.map' 0 0)) none
  let idX ← elabTerm (← `(𝟙 X)) none
  let (step, _) ← Simp.SimpM.run (← Simp.Context.mkDefault) (k := Precomp.reduceMap lhs)
  match step with
  | .visit result =>
    unless ← withNewMCtxDepth (isDefEq (← inferType result) (← inferType lhs)) do
      throwError "reducer changed the expression type (wrong-sem / reconstruction)"
    -- Correct preferred meaning.
    unless ← withNewMCtxDepth (isDefEq result expected) do
      throwError "reducer did not produce the custom-OfNat meaning F.map' 0 0"
    -- Wrong meaning under numeral canonicalization to standard 0.
    if ← withNewMCtxDepth (isDefEq result idX) then
      throwError "WRONG SEMANTICS: reduced form is definitionally 𝟙 X under custom OfNat 0:=⟨1⟩"
    let_expr Precomp.map _C _inst _n _F _X _f i _j _hij := lhs |
      throwError "expected Precomp.map application"
    let iWhnf ← whnf i
    -- Prefer constructor projection: getFinValue? can fail on non-decide proofs.
    let_expr Fin.mk _ val _p := iWhnf |
      throwError m!"expected Fin.mk after whnf, got {iWhnf}"
    let some valNat := val.nat? |
      throwError m!"expected nat literal Fin.val, got {val}"
    unless valNat == 1 do
      throwError s!"expected elaborated Fin.val = 1 for custom OfNat 0, got {valNat}"
  | .continue none =>
    throwError "reducer declined; cannot discriminate wrong semantics via reduction result"
  | _ => throwError "unexpected reducer step"
  evalTactic (← `(tactic| trivial))

example : True := by
  check_not_std_zero_identity
end WrongSemFirst
'''

WRONG_SEM_SECOND = r'''
section WrongSemSecond
local instance : OfNat (Fin (2 + 1 + 1)) 2 := ⟨⟨3, by decide⟩⟩

open Lean Meta Elab Tactic in
elab "check_not_std_two_meaning" : tactic => withMainContext do
  let lhs ← elabTerm (← `(Precomp.map F f (1 : Fin (2 + 1 + 1)) (2 : Fin (2 + 1 + 1)) (by decide))) none
  let expected ← elabTerm (← `(F.map' 0 2)) none
  -- Standard numeral 2 would be ⟨2⟩, giving F.map' 0 1 rather than F.map' 0 2.
  let wrong ← elabTerm (← `(F.map' 0 1)) none
  let (step, _) ← Simp.SimpM.run (← Simp.Context.mkDefault) (k := Precomp.reduceMap lhs)
  match step with
  | .visit result =>
    unless ← withNewMCtxDepth (isDefEq (← inferType result) (← inferType lhs)) do
      throwError "reducer changed the expression type (wrong-sem / reconstruction)"
    unless ← withNewMCtxDepth (isDefEq result expected) do
      throwError "reducer did not produce the custom-OfNat meaning F.map' 0 2"
    if ← withNewMCtxDepth (isDefEq result wrong) then
      throwError "WRONG SEMANTICS: reduced form matches standard-numeral meaning F.map' 0 1"
    let_expr Precomp.map _C _inst _n _F _X _f _i j _hij := lhs |
      throwError "expected Precomp.map application"
    let jWhnf ← whnf j
    let_expr Fin.mk _ val _p := jWhnf |
      throwError m!"expected Fin.mk after whnf, got {jWhnf}"
    let some valNat := val.nat? |
      throwError m!"expected nat literal Fin.val, got {val}"
    unless valNat == 3 do
      throwError s!"expected elaborated Fin.val = 3 for custom OfNat 2, got {valNat}"
  | .continue none =>
    throwError "reducer declined; cannot discriminate wrong semantics via reduction result"
  | _ => throwError "unexpected reducer step"
  evalTactic (← `(tactic| trivial))

example : True := by
  check_not_std_two_meaning
end WrongSemSecond
'''
PROBES: dict[str, str] = {
    "standard_visit": HELPER + r'''
example (p : (0 : Fin 4) ≤ 1) : Precomp.map F f 0 1 p = f := by
  check_reduce_map_visit
''',
    "custom_ofnat_first": HELPER + r'''
section CustomNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩
example : Precomp.map F f 0 0 (by rfl) = F.map' 0 0 := by
  check_reduce_map_visit
end CustomNumeral
''',
    "custom_ofnat_first_wrong_sem": HELPER + WRONG_SEM_FIRST,
    "custom_ofnat_second": HELPER + r'''
section CustomSecondNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 2 := ⟨⟨3, by decide⟩⟩
example : Precomp.map F f 1 2 (by decide) = F.map' 0 2 := by
  check_reduce_map_visit
end CustomSecondNumeral
''',
    "custom_ofnat_second_wrong_sem": HELPER + WRONG_SEM_SECOND,
    "equivalent_ofnat": HELPER + r'''
section EquivalentNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨0, by decide⟩⟩
example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  check_reduce_map_visit
end EquivalentNumeral
''',
    "shadow_le": HELPER + r'''
section CustomOrder
local instance (priority := high) : LE (Fin (2 + 1 + 1)) := ⟨fun _ _ => False⟩
local instance (priority := high) (i j : Fin (2 + 1 + 1)) : Decidable (i ≤ j) :=
  inferInstanceAs (Decidable False)
example : Precomp.map F f 0 1 (Nat.zero_le 1) = f := by
  check_reduce_map_visit
end CustomOrder
''',
    "opaque_decline": HELPER + r'''
example (i j : Fin 4) (p : i ≤ j) :
    Precomp.map F f i j p = Precomp.map F f i j p := by
  check_reduce_map_declines
''',
    "successor_constructors": HELPER + r'''
example {n : ℕ} (G : ComposableArrows C n) {Y : C} (g : Y ⟶ G.left)
    (a b : ℕ) (ha : a + 1 < n + 1 + 1) (hb : b + 1 < n + 1 + 1)
    (p : a + 1 ≤ b + 1) :
    Precomp.map G g ⟨a + 1, ha⟩ ⟨b + 1, hb⟩ p = G.map' a b := by
  check_reduce_map_visit
''',
}


def run_probe(repo: pathlib.Path, tag: str, name: str, src: str) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    src_path = OUT / f"{tag}_{name}.lean"
    log_path = OUT / f"{tag}_{name}.log"
    src_path.write_text(src, encoding="utf-8")
    dest = repo / "MathlibTest" / f"AdvProbe_{name}.lean"
    shutil.copyfile(src_path, dest)
    try:
        with log_path.open("wb") as stream:
            proc = subprocess.run(
                ["lake", "env", "lean", str(dest.relative_to(repo))],
                cwd=repo,
                stdout=stream,
                stderr=subprocess.STDOUT,
            )
        stream_text = log_path.read_text(errors="replace")
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(f"\nEXIT:{proc.returncode}\n")
        return {
            "tag": tag,
            "probe": name,
            "exit_code": proc.returncode,
            "log": str(log_path.relative_to(PREFERRED / ".cursor-handoff" / "evidence")),
            "source": str(src_path.relative_to(PREFERRED / ".cursor-handoff" / "evidence")),
            "log_tail": stream_text[-1200:],
        }
    finally:
        if dest.exists():
            dest.unlink()


def check_repo(repo: pathlib.Path, expect_clean_basic: bool) -> None:
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    assert head == BASE, (repo, head)
    diff = subprocess.check_output(
        ["git", "-C", str(repo), "diff", "HEAD", "--",
         "Mathlib/CategoryTheory/ComposableArrows/Basic.lean"]
    )
    if expect_clean_basic:
        assert diff == b"", f"{repo} Basic.lean unexpectedly modified"
    else:
        assert diff != b"", f"{repo} Basic.lean missing preferred patch"


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=("original", "preferred", "all"), default="all")
    args = parser.parse_args()

    targets = []
    if args.only in ("original", "all"):
        check_repo(ADV, expect_clean_basic=True)
        targets.append(("original", ADV))
    if args.only in ("preferred", "all"):
        check_repo(PREFERRED, expect_clean_basic=False)
        targets.append(("preferred", PREFERRED))

    # Ensure selected checkouts can import Basic.
    for _, repo in targets:
        subprocess.run(
            ["lake", "build", "Mathlib.CategoryTheory.ComposableArrows.Basic"],
            cwd=repo, check=True,
        )

    results = []
    # Preserve prior matrix results when running a subset.
    prior_path = OUT / "matrix.json"
    if prior_path.exists() and args.only != "all":
        prior = json.loads(prior_path.read_text())
        results.extend(prior.get("results", []))
        # Drop results that will be replaced.
        replace_tags = {t for t, _ in targets}
        results = [r for r in results if r.get("tag") not in replace_tags]

    for tag, repo in targets:
        for name, src in PROBES.items():
            print(f"RUN {tag}/{name}", flush=True)
            results.append(run_probe(repo, tag, name, src))
            print(f"  exit={results[-1]['exit_code']}", flush=True)

    matrix = {
        "base": BASE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "preferred_repo": str(PREFERRED),
        "original_repo": str(ADV),
        "results": results,
    }
    (OUT / "matrix.json").write_text(json.dumps(matrix, indent=2), encoding="utf-8")

    # Markdown matrix
    lines = [
        "# Adversarial matrix (elaborating probes)",
        "",
        f"- Base: `{BASE}`",
        f"- Timestamp: {matrix['timestamp']}",
        f"- Original checkout: `{ADV}` (clean Basic.lean / original reducer)",
        f"- Preferred checkout: `{PREFERRED}` (preferred reducer)",
        "",
        "| probe | original exit | preferred exit | notes |",
        "| --- | --- | --- | --- |",
    ]
    notes = {
        "standard_visit": "reducer must visit standard numeral",
        "custom_ofnat_first": "preserve custom OfNat 0:=⟨1⟩ as F.map' 0 0",
        "custom_ofnat_first_wrong_sem": "elaborating: reject collapse to 𝟙 X; require Fin.val=1",
        "custom_ofnat_second": "preserve custom OfNat 2:=⟨3⟩ as F.map' 0 2",
        "custom_ofnat_second_wrong_sem": "elaborating: reject std meaning F.map' 0 1; require Fin.val=3",
        "equivalent_ofnat": "equal-value custom OfNat still visits",
        "shadow_le": "must not resynthesize LE under shadowed instance",
        "opaque_decline": "opaque Fin vars decline",
        "successor_constructors": "preferred visits explicit successors; original may differ",
    }
    by = {(r["tag"], r["probe"]): r["exit_code"] for r in results}
    for name in PROBES:
        lines.append(
            f"| {name} | {by[('original', name)]} | {by[('preferred', name)]} | {notes[name]} |"
        )
    lines.append("")
    lines.append("## Log tails")
    for r in results:
        lines.append(f"### {r['tag']}/{r['probe']} (exit {r['exit_code']})")
        lines.append("```")
        lines.append((r["log_tail"] or "").rstrip() or "<empty stdout>")
        lines.append("```")
        lines.append("")
    summary_path = OUT / "SUMMARY.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Also copy a flat pointer into evidence root for export discoverability.
    shutil.copyfile(summary_path, PREFERRED / ".cursor-handoff" / "evidence" / "adversarial-summary.md")
    print(f"Wrote {OUT / 'matrix.json'} and {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
