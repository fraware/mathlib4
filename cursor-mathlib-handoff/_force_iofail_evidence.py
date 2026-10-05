#!/usr/bin/env python3
"""Force non-empty lake --iofail rebuild of candidate test modules (supplemental evidence)."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

REPO = Path.home() / "mathlib4-cursor"
EV = REPO / ".cursor-handoff" / "evidence"
TARGET_FP = "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0"


def main() -> int:
    import sys

    sys.path.insert(0, str(REPO / ".cursor-handoff"))
    import workflow  # type: ignore

    fp = workflow.fingerprint(REPO)
    print("fingerprint", fp)
    assert fp == TARGET_FP, fp

    for rel in (
        "ComposableArrowsReduceMap.olean",
        "ComposableArrowsIntegratedProbe.olean",
    ):
        p = REPO / ".lake/build/lib/lean/MathlibTest" / rel
        if p.exists():
            p.unlink()
            print("removed", p)

    env = os.environ.copy()
    env["PATH"] = str(Path.home() / ".elan" / "bin") + os.pathsep + env.get("PATH", "")
    env["LEAN_NUM_THREADS"] = "2"
    log = EV / f"supplemental-iofail-candidate-{time.time_ns()}.log"
    cmd = [
        "lake",
        "--iofail",
        "build",
        "MathlibTest.ComposableArrowsReduceMap",
        "MathlibTest.ComposableArrowsIntegratedProbe",
    ]
    print("running", cmd, "->", log)
    with log.open("wb") as stream:
        proc = subprocess.run(cmd, cwd=REPO, env=env, stdout=stream, stderr=subprocess.STDOUT)
    text = log.read_text(errors="replace")
    with log.open("a", encoding="utf-8") as stream:
        stream.write(f"\nEXIT:{proc.returncode}\nFINGERPRINT:{fp}\n")
    print("exit", proc.returncode, "size", log.stat().st_size)
    print(text[-1500:])
    assert proc.returncode == 0
    assert "ComposableArrowsReduceMap" in text
    assert fp == workflow.fingerprint(REPO)
    # Pointer file for export discoverability
    (EV / "supplemental-iofail-candidate.LATEST").write_text(log.name + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
