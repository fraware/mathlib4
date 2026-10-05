#!/usr/bin/env python3
"""Launch workflow full inside a detached tmux session (survives agent disconnect)."""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

SESSION = "mathlib-full-gate"
REPO = Path.home() / "mathlib4-cursor"
EV = REPO / ".cursor-handoff" / "evidence"
WRAPPER = EV / "full-tmux.wrapper.log"
STATUS = EV / "full-tmux.status"


def main() -> int:
    # Refuse if already running.
    alive = subprocess.run(["pgrep", "-af", r"workflow\.py run full"], capture_output=True, text=True).stdout.strip()
    if alive:
        print("REFUSING: already running:\n", alive)
        return 2

    # Kill stale session of same name if any.
    subprocess.run(["tmux", "kill-session", "-t", SESSION], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Mark orphaned running full.json.
    full = EV / "full.json"
    if full.exists():
        data = json.loads(full.read_text())
        if data.get("status") == "running":
            data["status"] = "interrupted"
            data["error"] = "orphaned; restarted under tmux"
            data["interrupted_unix"] = time.time()
            full.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print("marked previous full.json interrupted")

    import sys

    sys.path.insert(0, str(REPO / ".cursor-handoff"))
    import workflow  # type: ignore

    print("fingerprint", workflow.fingerprint(REPO))

    env_prefix = f'export PATH="{Path.home() / ".elan" / "bin"}:$PATH"'
    # Run inside tmux: write status file on completion.
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
    cmd = ["tmux", "new-session", "-d", "-s", SESSION, "bash", "-lc", inner]
    subprocess.check_call(cmd)
    time.sleep(4)
    print("tmux ls:")
    print(subprocess.check_output(["tmux", "ls"], text=True))
    print("wrapper head:")
    print(WRAPPER.read_text(errors="replace")[:2000] if WRAPPER.exists() else "(no wrapper yet)")
    print("pgrep:")
    print(subprocess.run(["pgrep", "-af", r"workflow\.py run full|lake"], capture_output=True, text=True).stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
