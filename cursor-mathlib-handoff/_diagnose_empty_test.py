#!/usr/bin/env python3
"""Diagnose empty lake --iofail test logs and force a verbose captured rerun."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

repo = Path.home() / "mathlib4-cursor"
ev = repo / ".cursor-handoff" / "evidence"
env = os.environ.copy()
env["PATH"] = str(Path.home() / ".elan" / "bin") + os.pathsep + env.get("PATH", "")

# Show what lake test means.
for cmd in (
    ["lake", "--version"],
    ["lake", "test", "--help"],
):
    print("CMD", cmd)
    subprocess.run(cmd, cwd=repo, env=env)

# Force rebuild of the regression module then run iofail test with unbuffered capture.
olean = repo / ".lake/build/lib/lean/MathlibTest/ComposableArrowsReduceMap.olean"
if olean.exists():
    olean.unlink()
    print("removed", olean)

log = ev / f"manual-iofail-test-{time.time_ns()}.log"
print("logging to", log)
with log.open("wb") as stream:
    # stdbuf if available
    cmd = ["lake", "--iofail", "test"]
    try:
        cmd = ["stdbuf", "-oL", "-eL", *cmd]
    except Exception:
        pass
    proc = subprocess.run(cmd, cwd=repo, env=env, stdout=stream, stderr=subprocess.STDOUT)
print("exit", proc.returncode, "size", log.stat().st_size)
print(log.read_text(errors="replace")[-3000:])
