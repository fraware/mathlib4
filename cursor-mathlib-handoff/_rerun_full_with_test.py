#!/usr/bin/env python3
"""Clear MathlibTest build products, then rerun workflow full with elan PATH.

Ensures lake --iofail test produces a non-empty log by forcing rebuild work.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

repo = Path.home() / "mathlib4-cursor"
ev = repo / ".cursor-handoff" / "evidence"
env = os.environ.copy()
env["PATH"] = str(Path.home() / ".elan" / "bin") + os.pathsep + env.get("PATH", "")

# Remove MathlibTest build artifacts so `lake --iofail test` must rebuild.
roots = [
    repo / ".lake/build/lib/lean/MathlibTest",
    repo / ".lake/build/ir/MathlibTest",
]
for root in roots:
    if root.exists():
        shutil.rmtree(root)
        print("removed", root)

# Confirm fingerprint unchanged (source-only).
import sys
sys.path.insert(0, str(repo / ".cursor-handoff"))
import workflow  # type: ignore
fp = workflow.fingerprint(repo)
print("fingerprint", fp)

wrapper = ev / "full-rerun2.wrapper.log"
pidfile = ev / "full-rerun2.pid"
logf = wrapper.open("wb")
proc = subprocess.Popen(
    ["python3", str(repo / ".cursor-handoff" / "workflow.py"), "run", "full"],
    cwd=repo,
    stdout=logf,
    stderr=subprocess.STDOUT,
    start_new_session=True,
    env=env,
)
pidfile.write_text(str(proc.pid) + "\n", encoding="utf-8")
print("started", proc.pid)
time.sleep(8)
print(wrapper.read_text(errors="replace")[:2000])
print("poll", proc.poll())
