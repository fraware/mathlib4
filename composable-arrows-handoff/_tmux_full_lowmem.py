#!/usr/bin/env python3
"""Restart full gate under tmux with CPU pinning to avoid WSL memory collapse.

Lake 5.0 on this toolchain has no -j flag. Limit concurrency via:
  - PATH wrapper: taskset -c 0,1 around real lake
  - LEAN_NUM_THREADS=2
Does not modify workflow.py or source fingerprint.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

SESSION = "mathlib-full-gate"
REPO = Path.home() / "mathlib4-handoff"
EV = REPO / ".handoff" / "evidence"
BIN = REPO / ".handoff" / "bin"
WRAPPER = EV / "full-tmux.wrapper.log"
STATUS = EV / "full-tmux.status"
TARGET_FP = "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0"


def main() -> int:
    subprocess.run(["tmux", "kill-session", "-t", SESSION], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", r"workflow\.py run full"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    BIN.mkdir(parents=True, exist_ok=True)
    real_lake = Path.home() / ".elan" / "bin" / "lake"
    wrapper = BIN / "lake"
    # Pin lake (and its children inherit affinity on Linux) to 2 CPUs.
    wrapper.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'REAL="{real_lake}"\n'
        'if command -v taskset >/dev/null 2>&1; then\n'
        '  exec taskset -c 0,1 "$REAL" "$@"\n'
        'else\n'
        '  exec "$REAL" "$@"\n'
        'fi\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    print("wrote", wrapper)

    full = EV / "full.json"
    if full.exists():
        data = json.loads(full.read_text())
        if data.get("status") in {"running", "failed"}:
            # Keep failed record; new run overwrites via workflow.
            pass

    # Ensure candidate regression rebuilds (non-empty test signal).
    for rel in (
        "ComposableArrowsReduceMap.olean",
        "ComposableArrowsIntegratedProbe.olean",
    ):
        p = REPO / ".lake/build/lib/lean/MathlibTest" / rel
        if p.exists():
            p.unlink()
            print("removed", p)

    import sys

    sys.path.insert(0, str(REPO / ".handoff"))
    import workflow  # type: ignore

    fp = workflow.fingerprint(REPO)
    print("fingerprint", fp)
    if fp != TARGET_FP:
        print("ERROR fingerprint mismatch", fp)
        return 3

    # Quick smoke: Mathlib build should be cache-hit.
    env = {
        **dict(**{k: v for k, v in __import__("os").environ.items()}),
        "PATH": f"{BIN}:{Path.home() / '.elan' / 'bin'}:/usr/bin:/bin",
        "LEAN_NUM_THREADS": "2",
    }
    smoke = subprocess.run(
        ["lake", "build", "Mathlib.CategoryTheory.ComposableArrows.Basic"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    print("smoke exit", smoke.returncode, (smoke.stdout + smoke.stderr)[-300:])
    if smoke.returncode != 0:
        return 4

    path = f"{BIN}:{Path.home() / '.elan' / 'bin'}:/usr/bin:/bin"
    inner = (
        f"export PATH={path!r}; "
        f"export LEAN_NUM_THREADS=2; "
        f"cd {REPO}; "
        f"python3 .handoff/workflow.py run full > {WRAPPER} 2>&1; "
        f"ec=$?; echo $ec > {STATUS}; echo DONE exit=$ec >> {WRAPPER}; exit $ec"
    )
    STATUS.write_text("running\n", encoding="utf-8")
    if WRAPPER.exists():
        WRAPPER.unlink()
    subprocess.check_call(["tmux", "new-session", "-d", "-s", SESSION, "bash", "-lc", inner])
    time.sleep(8)
    print("tmux:", subprocess.check_output(["tmux", "ls"], text=True))
    print("wrapper:\n", WRAPPER.read_text(errors="replace")[:2000] if WRAPPER.exists() else "(none)")
    print("procs:\n", subprocess.run(["pgrep", "-af", r"workflow\.py|lake"], capture_output=True, text=True).stdout)
    print(subprocess.check_output(["free", "-h"], text=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
