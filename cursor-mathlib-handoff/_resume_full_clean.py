#!/usr/bin/env python3
"""Resume full gate for current fingerprint. No competing builders assumed.

Marks orphaned full.json as interrupted, then starts workflow run full with elan PATH.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

repo = Path.home() / "mathlib4-cursor"
ev = repo / ".cursor-handoff" / "evidence"
env = os.environ.copy()
env["PATH"] = str(Path.home() / ".elan" / "bin") + os.pathsep + env.get("PATH", "")

# Refuse if lake/workflow already running.
procs = subprocess.run(
    ["pgrep", "-af", r"workflow\.py run full|lake (build|test|lint)"],
    capture_output=True,
    text=True,
).stdout.strip()
if procs:
    raise SystemExit(f"REFUSING: competing processes still alive:\n{procs}")

# Annotate orphaned running marker.
full = ev / "full.json"
if full.exists():
    data = json.loads(full.read_text())
    if data.get("status") == "running":
        data["status"] = "interrupted"
        data["error"] = "process died mid-gate; resumable restart by validation owner"
        data["interrupted_unix"] = time.time()
        full.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print("marked previous full.json as interrupted")

# Confirm fingerprint
import sys

sys.path.insert(0, str(repo / ".cursor-handoff"))
import workflow  # type: ignore

fp = workflow.fingerprint(repo)
print("fingerprint", fp)
print("HEAD", subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip())

wrapper = ev / "full-resume.wrapper.log"
pidfile = ev / "full-resume.pid"
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
time.sleep(6)
print(wrapper.read_text(errors="replace")[:2500])
print("poll", proc.poll())
