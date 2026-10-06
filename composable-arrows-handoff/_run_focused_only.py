#!/usr/bin/env python3
import pathlib, subprocess, sys
repo = pathlib.Path.home() / "mathlib4-handoff"
sys.exit(subprocess.call(
    ["python3", str(repo / ".handoff" / "workflow.py"), "run", "focused"],
    cwd=repo,
))
