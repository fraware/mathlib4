#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys

env = os.environ.copy()
elan = str(pathlib.Path.home() / ".elan" / "bin")
env["PATH"] = elan + os.pathsep + env.get("PATH", "")

# Always refresh from the Windows handoff source (authoritative during this run).
win = pathlib.Path("/mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff/_build_adversarial_suite.py")
linux_copy = pathlib.Path.home() / "mathlib4-cursor" / ".cursor-handoff" / "_build_adversarial_suite.py"
text = win.read_bytes().replace(b"\r\n", b"\n")
linux_copy.write_bytes(text)
cmd = [sys.executable, str(linux_copy), *sys.argv[1:]]
print("RUNNING", cmd, flush=True)
sys.exit(subprocess.call(cmd, env=env))
