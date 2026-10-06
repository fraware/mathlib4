#!/usr/bin/env python3
"""Honest audit of current handoff state. Prints facts only."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

REPO = Path("/home/mateo/mathlib4-handoff")
EV = REPO / ".handoff" / "evidence"
CLAIMED_FP = "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0"
CLAIMED_ZIP = "66484dfc1f5f3c8d571b243c9817602a3296dda531994a4466fbfa47848ffd03"


def load_wf():
    spec = importlib.util.spec_from_file_location("wf", REPO / ".handoff" / "workflow.py")
    wf = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(wf)
    return wf


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    wf = load_wf()
    fp = wf.fingerprint(REPO)
    print("=== FINGERPRINT ===")
    print("computed", fp)
    print("claimed ", CLAIMED_FP)
    print("match", fp == CLAIMED_FP)

    print("\n=== FILE HASHES ===")
    claimed_files = {
        "Mathlib/CategoryTheory/ComposableArrows/Basic.lean":
            "28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251",
        "MathlibTest/ComposableArrowsReduceMap.lean":
            "3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb",
        "MathlibTest/ComposableArrowsIntegratedProbe.lean":
            "b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e",
    }
    for rel, claimed in claimed_files.items():
        actual = sha256_file(REPO / rel)
        print(f"{rel}\n  actual {actual}\n  claim  {claimed}\n  match  {actual == claimed}")

    head_integrated = subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"HEAD:{wf.INTEGRATED}"]
    )
    cur_integrated = (REPO / wf.INTEGRATED).read_bytes()
    print("\nintegrated byte-identical to HEAD:",
          hashlib.sha256(head_integrated).digest() == hashlib.sha256(cur_integrated).digest())

    print("\n=== FORBIDDEN PATTERNS ===")
    for rel in [wf.BASIC, wf.TEST, wf.INTEGRATED]:
        text = (REPO / rel).read_text(encoding="utf-8")
        for needle in [
            "sorry", "admit", "axiom ", "set_option linter",
            "linter.unusedTactic", "linter.unreachableTactic",
        ]:
            count = text.count(needle)
            if count:
                print(f"{rel}: {needle!r} count={count}")
    print("(end forbidden scan)")

    print("\n=== PREFERRED EXPECTATION COUNTS (rough) ===")
    test = (REPO / wf.TEST).read_text(encoding="utf-8")
    for needle in ["reduceMap_visits", "reduceMap_declines", "example"]:
        print(needle, test.count(needle))

    print("\n=== GATE JSON vs FP ===")
    for stage in ["baseline", "focused", "downstream", "full"]:
        path = EV / f"{stage}.json"
        rec = json.loads(path.read_text())
        print(
            stage,
            "status=", rec.get("status"),
            "fp=", rec.get("source_sha256"),
            "fp_match=", rec.get("source_sha256") == fp,
            "exits=", [c.get("exit_code") for c in rec.get("commands", [])],
        )
        for c in rec.get("commands", []):
            log = EV / c["log"]
            size = log.stat().st_size if log.exists() else None
            print(f"  exit={c['exit_code']} size={size} log={c['log']} argv={c['argv']}")

    print("\n=== ZIP ===")
    for z in [
        REPO / ".handoff" / "validation-evidence.zip",
        Path("/mnt/c/Users/mateo/mathlib4-1/composable-arrows-handoff/validation-evidence.zip"),
    ]:
        if z.exists():
            h = sha256_file(z)
            print(z, h, "match_claimed=", h == CLAIMED_ZIP, "bytes=", z.stat().st_size)
        else:
            print(z, "MISSING")

    print("\n=== SUPPLEMENTAL IOFFAIL ===")
    for p in sorted(EV.glob("supplemental*")) + sorted(EV.glob("*iofail*")):
        print(p.name, p.stat().st_size)
        if p.suffix == ".log" or p.name.endswith(".LATEST"):
            print("--- begin", p.name, "---")
            print(p.read_text(encoding="utf-8", errors="replace")[:4000])
            print("--- end ---")

    print("\n=== PUSH GUARDS ===")
    hooks = subprocess.check_output(
        ["git", "-C", str(REPO), "config", "--get", "core.hooksPath"], text=True
    ).strip()
    pushurl = subprocess.check_output(
        ["git", "-C", str(REPO), "config", "--get", "remote.origin.pushurl"], text=True
    ).strip()
    print("hooksPath", hooks)
    print("pushurl", pushurl)
    hook = Path(hooks) / "pre-push"
    print("pre-push exists", hook.exists())
    if hook.exists():
        print(hook.read_text())

    print("\n=== ADV SUITE MATRIX ===")
    matrix = json.loads((EV / "advsuite_matrix.json").read_text())
    print(json.dumps(matrix, indent=2)[:8000])


if __name__ == "__main__":
    main()
