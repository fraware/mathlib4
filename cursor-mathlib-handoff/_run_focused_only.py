#!/usr/bin/env python3
import pathlib, subprocess, sys
repo = pathlib.Path.home() / "mathlib4-cursor"
sys.exit(subprocess.call(
    ["python3", str(repo / ".cursor-handoff" / "workflow.py"), "run", "focused"],
    cwd=repo,
))
