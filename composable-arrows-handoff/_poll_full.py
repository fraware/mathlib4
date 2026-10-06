#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ev = Path("/home/mateo/mathlib4-handoff/.handoff/evidence")
full = json.loads((ev / "full.json").read_text())
print("status", full.get("status"))
print("error", full.get("error"))
print("finished", full.get("finished_unix"))
print("fp", full.get("source_sha256"))
for c in full.get("commands", []):
    log = ev / c["log"]
    size = log.stat().st_size if log.exists() else None
    print(f"exit={c.get('exit_code')} size={size} log={c['log']} argv={c['argv']}")
    if c.get("argv") == ["lake", "--iofail", "test"] and log.exists():
        print("---TEST LOG---")
        print(log.read_text(errors="replace"))
ps = subprocess.run(["pgrep", "-af", "lake"], capture_output=True, text=True)
print("pgrep_lake:")
print(ps.stdout or "(none)")
lint_log = None
for c in full.get("commands", []):
    if c.get("argv") and c["argv"][0:2] == ["lake", "lint"]:
        lint_log = ev / c["log"]
if lint_log and lint_log.exists():
    text = lint_log.read_text(errors="replace")
    print("lint_log_size", len(text))
    print("---LINT TAIL---")
    print(text[-1500:])
wrapper = ev / "full-rerun-wrapper.log"
if wrapper.exists():
    print("---WRAPPER TAIL---")
    print(wrapper.read_text(errors="replace")[-1000:])
