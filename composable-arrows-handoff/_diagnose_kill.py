#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return (r.stdout or "") + (r.stderr or "")


def main() -> int:
    print("=== free ===")
    print(run(["free", "-h"]))
    print("=== which isolation tools ===")
    print(run(["bash", "-lc", "which tmux; which screen; which systemd-run; which nohup"]))
    print("=== dmesg tail ===")
    out = run(["bash", "-lc", "dmesg -T 2>/dev/null | tail -80"])
    for line in out.splitlines():
        low = line.lower()
        if any(k in low for k in ("oom", "kill", "lean", "lake", "out of memory")):
            print(line)
    print("=== pidfile ===")
    pidf = Path.home() / "mathlib4-handoff/.handoff/evidence/full-resume.pid"
    print(pidf.read_text().strip() if pidf.exists() else "missing")
    if pidf.exists():
        pid = pidf.read_text().strip()
        print(run(["ps", "-p", pid, "-o", "pid,etime,state,cmd"]))
    print("=== leftover lake ===")
    print(run(["pgrep", "-af", "lake|workflow.py|runLinter"]) or "(none)")
    # Check if MathlibTest nearly complete
    print("=== olean progress sample ===")
    root = Path.home() / "mathlib4-handoff/.lake/build/lib/lean/MathlibTest"
    if root.exists():
        n = sum(1 for _ in root.rglob("*.olean"))
        print("MathlibTest oleans", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
