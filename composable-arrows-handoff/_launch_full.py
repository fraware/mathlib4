#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import time

repo = Path.home() / "mathlib4-handoff"
ev = repo / ".handoff" / "evidence"
ev.mkdir(parents=True, exist_ok=True)
wrapper = ev / "full-rerun.wrapper.log"
pidfile = ev / "full-rerun.pid"
env = os.environ.copy()
elan = str(Path.home() / ".elan" / "bin")
env["PATH"] = elan + os.pathsep + env.get("PATH", "")
logf = wrapper.open("wb")
proc = subprocess.Popen(
    ["python3", str(repo / ".handoff" / "workflow.py"), "run", "full"],
    cwd=repo,
    stdout=logf,
    stderr=subprocess.STDOUT,
    start_new_session=True,
    env=env,
)
pidfile.write_text(str(proc.pid) + "\n", encoding="utf-8")
print(f"started pid={proc.pid}")
time.sleep(5)
print(wrapper.read_text(errors="replace")[:2500])
print("poll", proc.poll())
