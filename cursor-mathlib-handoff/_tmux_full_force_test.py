#!/usr/bin/env python3
"""Restart full gate under tmux after clearing MathlibTest artifacts for non-empty test logs."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

SESSION = "mathlib-full-gate"
REPO = Path.home() / "mathlib4-cursor"
EV = REPO / ".cursor-handoff" / "evidence"
WRAPPER = EV / "full-tmux.wrapper.log"
STATUS = EV / "full-tmux.status"


def main() -> int:
    # Stop existing tmux full gate cleanly.
    subprocess.run(["tmux", "kill-session", "-t", SESSION], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Also kill any leftover lake/workflow
    subprocess.run(["pkill", "-f", r"workflow\.py run full"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", r"lake --iofail test"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    left = subprocess.run(["pgrep", "-af", r"workflow\.py run full|lake --iofail"], capture_output=True, text=True).stdout.strip()
    if left:
        print("REFUSING: still alive after kill:\n", left)
        return 2

    # Mark orphaned marker
    full = EV / "full.json"
    if full.exists():
        data = json.loads(full.read_text())
        if data.get("status") == "running":
            data["status"] = "interrupted"
            data["error"] = "restarted with forced MathlibTest rebuild for non-empty test log"
            data["interrupted_unix"] = time.time()
            full.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    # Clear MathlibTest build products so lake --iofail test must rebuild.
    roots = [
        REPO / ".lake/build/lib/lean/MathlibTest",
        REPO / ".lake/build/ir/MathlibTest",
    ]
    for root in roots:
        if root.exists():
            shutil.rmtree(root)
            print("removed", root)

    import sys

    sys.path.insert(0, str(REPO / ".cursor-handoff"))
    import workflow  # type: ignore

    fp = workflow.fingerprint(REPO)
    print("fingerprint", fp)
    # Confirm source unchanged by clearing build artifacts only.
    assert fp == "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0", fp

    env_prefix = f'export PATH="{Path.home() / ".elan" / "bin"}:$PATH"'
    inner = (
        f"{env_prefix}; "
        f"cd {REPO}; "
        f"python3 .cursor-handoff/workflow.py run full "
        f"> {WRAPPER} 2>&1; "
        f"ec=$?; "
        f"echo $ec > {STATUS}; "
        f"echo DONE exit=$ec >> {WRAPPER}; "
        f"exit $ec"
    )
    STATUS.write_text("running\n", encoding="utf-8")
    if WRAPPER.exists():
        WRAPPER.unlink()
    subprocess.check_call(["tmux", "new-session", "-d", "-s", SESSION, "bash", "-lc", inner])
    time.sleep(5)
    print("tmux ls:")
    print(subprocess.check_output(["tmux", "ls"], text=True))
    print("wrapper:")
    print(WRAPPER.read_text(errors="replace")[:2000] if WRAPPER.exists() else "(none)")
    print("procs:")
    print(subprocess.run(["pgrep", "-af", r"workflow\.py run full|lake"], capture_output=True, text=True).stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
