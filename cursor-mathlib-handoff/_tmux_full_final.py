#!/usr/bin/env python3
"""Final full-gate attempt: tmux isolation, no CPU pinning, warm MathlibTest cache.

Prior failure was MathlibTest.ClickSuggestions.Benchmark wall-clock guard
(all < 60000ms) under taskset -c 0,1 — unrelated to the preferred reducer.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

SESSION = "mathlib-full-gate"
REPO = Path.home() / "mathlib4-cursor"
EV = REPO / ".cursor-handoff" / "evidence"
BIN = REPO / ".cursor-handoff" / "bin"
WRAPPER = EV / "full-tmux.wrapper.log"
STATUS = EV / "full-tmux.status"
TARGET_FP = "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0"
NOTE = EV / "env-mitigations.md"


def main() -> int:
    subprocess.run(["tmux", "kill-session", "-t", SESSION], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", r"workflow\.py run full"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    # Passthrough wrapper only (no taskset). Keep file so PATH layout stays stable.
    BIN.mkdir(parents=True, exist_ok=True)
    real_lake = Path.home() / ".elan" / "bin" / "lake"
    (BIN / "lake").write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'exec "{real_lake}" "$@"\n',
        encoding="utf-8",
    )
    (BIN / "lake").chmod(0o755)

    NOTE.write_text(
        "# Environment mitigations (not source changes)\n\n"
        "- Full gate runs under detached `tmux` so agent disconnects do not kill Lake.\n"
        "- A temporary `taskset -c 0,1` lake wrapper caused "
        "`MathlibTest.ClickSuggestions.Benchmark` to exceed its 60s wall-clock guard; "
        "that wrapper was removed. Failure was environmental, not candidate-related.\n"
        "- `LEAN_NUM_THREADS=2` retained as a soft lean-process hint only.\n"
        "- MathlibTest cache left warm after successful standalone Benchmark rebuild.\n",
        encoding="utf-8",
    )

    import sys

    sys.path.insert(0, str(REPO / ".cursor-handoff"))
    import workflow  # type: ignore

    fp = workflow.fingerprint(REPO)
    print("fingerprint", fp)
    if fp != TARGET_FP:
        print("ERROR fingerprint mismatch", fp)
        return 3

    # Confirm Benchmark is up to date before starting the long gate.
    env = {
        **{k: v for k, v in __import__("os").environ.items()},
        "PATH": f"{Path.home() / '.elan' / 'bin'}:/usr/bin:/bin",
        "LEAN_NUM_THREADS": "2",
    }
    # Prefer real elan lake, not wrapper, for preflight.
    pre = subprocess.run(
        ["lake", "build", "MathlibTest.ClickSuggestions.Benchmark",
         "MathlibTest.ComposableArrowsReduceMap",
         "MathlibTest.ComposableArrowsIntegratedProbe"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    print("preflight exit", pre.returncode)
    print((pre.stdout + pre.stderr)[-500:])
    if pre.returncode != 0:
        return 4

    path = f"{Path.home() / '.elan' / 'bin'}:/usr/bin:/bin"
    inner = (
        f"export PATH={path!r}; "
        f"export LEAN_NUM_THREADS=2; "
        f"cd {REPO}; "
        f"python3 .cursor-handoff/workflow.py run full > {WRAPPER} 2>&1; "
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
