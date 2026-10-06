#!/usr/bin/env python3
"""Adversarial original-vs-preferred probes in a separate checkout."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
ADV = HOME / "mathlib4-handoff-adv"
PREF = HOME / "mathlib4-handoff"
EV_ADV = ADV / ".handoff" / "evidence"
EV_PREF = PREF / ".handoff" / "evidence"

HELPER = r"""
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
variable (F : ComposableArrows C 2) {X : C} (f : X ⟶ F.left)
"""

PROBES: dict[str, str] = {
    "custom_numeral": r"""
section CustomNumeral
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩

-- Plain meaning check: custom 0 means ⟨1⟩, so map 0 0 should be F.map' 0 0.
example : Precomp.map F f 0 0 (by rfl) = F.map' 0 0 := by
  rfl

-- Direct reducer inspection with preferred-style expectation.
example : Precomp.map F f 0 0 (by rfl) = F.map' 0 0 := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
end CustomNumeral
""",
    "custom_numeral_wrong_sem": r"""
section CustomNumeralWrongSemantics
local instance : OfNat (Fin (2 + 1 + 1)) 0 := ⟨⟨1, by decide⟩⟩

-- If the reducer canonicalizes to standard OfNat 0 (= ⟨0⟩), it yields 𝟙 X.
-- Preferred must NOT make this succeed; original MAY wrongly succeed.
example : Precomp.map F f 0 0 (by rfl) = 𝟙 X := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
end CustomNumeralWrongSemantics
""",
    "shadow_le": r"""
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
""",
    "standard_visit": r"""
example (p : (0 : Fin 4) ≤ 1) : Precomp.map F f 0 1 p = f := by
  check_reduce_map_visit
  dsimp only [Precomp.reduceMap] <;> rfl
""",
}


def run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_elan_env() -> None:
    elan_env = HOME / ".elan" / "env"
    if elan_env.exists():
        # Source-equivalent: prepend elan bin
        elan_bin = str(HOME / ".elan" / "bin")
        path = os.environ.get("PATH", "")
        if elan_bin not in path.split(":"):
            os.environ["PATH"] = elan_bin + ":" + path


def run_probe(repo: Path, name: str, body: str, tag: str, outdir: Path) -> int:
    lean_rel = Path("MathlibTest") / f"AdvProbe_{name}.lean"
    lean_path = repo / lean_rel
    log_path = outdir / f"adv_{tag}_{name}.log"
    src_path = outdir / f"adv_{tag}_{name}.lean"
    text = HELPER + "\n" + body
    lean_path.write_text(text, encoding="utf-8")
    src_path.write_text(text, encoding="utf-8")
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(
            ["lake", "env", "lean", str(lean_rel)],
            cwd=repo,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        log.write(f"\nEXIT:{proc.returncode}\n")
    lean_path.unlink(missing_ok=True)
    print(f"{tag} {name} exit={proc.returncode}", flush=True)
    return proc.returncode


def tail(path: Path, n: int = 40) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-n:])


def main() -> int:
    ensure_elan_env()
    EV_ADV.mkdir(parents=True, exist_ok=True)
    EV_PREF.mkdir(parents=True, exist_ok=True)

    # Confirm adv is clean original
    head = subprocess.check_output(["git", "-C", str(ADV), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(ADV), "status", "--porcelain"], text=True)
    if dirty.strip():
        print("STOP: adversarial checkout is dirty; refusing to proceed", file=sys.stderr)
        print(dirty, file=sys.stderr)
        return 2

    print("=== baseline on adversarial checkout ===", flush=True)
    run(["python3", ".handoff/workflow.py", "run", "baseline"], cwd=ADV)

    results: list[tuple[str, str, int]] = []
    for name, body in PROBES.items():
        ec = run_probe(ADV, name, body, "original", EV_ADV)
        results.append(("original", name, ec))

    for name, body in PROBES.items():
        ec = run_probe(PREF, name, body, "preferred", EV_ADV)
        results.append(("preferred", name, ec))

    summary = EV_ADV / "adversarial-summary.md"
    with summary.open("w", encoding="utf-8") as out:
        out.write("# Adversarial baseline discrimination\n\n")
        out.write(f"- Adv checkout: `{ADV}` (original reducer, clean HEAD)\n")
        out.write(f"- Preferred checkout: `{PREF}` (preferred reducer)\n")
        out.write(f"- Base: `{head}`\n")
        out.write(f"- Timestamp: {datetime.now(timezone.utc).isoformat()}\n\n")
        out.write("## Exit codes\n\n")
        out.write("| tag | probe | exit |\n| --- | --- | --- |\n")
        for tag, name, ec in results:
            out.write(f"| {tag} | {name} | {ec} |\n")
        out.write("\n## Interpretation notes\n\n")
        out.write(
            "- `custom_numeral` success means custom OfNat meaning is preserved "
            "(map equals `F.map' 0 0`).\n"
            "- `custom_numeral_wrong_sem` success means reduction to `𝟙 X` under "
            "custom OfNat `0 := ⟨1⟩` (wrong semantics).\n"
            "- `shadow_le` success means the reducer preserves the stored LE proof "
            "under a shadowed LE instance.\n"
            "- `standard_visit` confirms the reducer is actually invoked.\n\n"
        )
        for tag, name, ec in results:
            log = EV_ADV / f"adv_{tag}_{name}.log"
            out.write(f"## {tag}/{name} (exit {ec})\n\n```\n")
            out.write(tail(log, 50))
            out.write("\n```\n\n")

    # Copy into preferred evidence for export
    for path in EV_ADV.glob("adv_*"):
        shutil.copy2(path, EV_PREF / path.name)
    shutil.copy2(summary, EV_PREF / "adversarial-summary.md")
    print(summary.read_text(encoding="utf-8"))
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
