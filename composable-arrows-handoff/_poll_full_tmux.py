#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

EV = Path.home() / "mathlib4-handoff/.handoff/evidence"


def main() -> int:
    d = json.loads((EV / "full.json").read_text())
    print("full.status", d.get("status"), "error", d.get("error"))
    print("fp", d.get("source_sha256"))
    for c in d.get("commands", []):
        log = EV / c["log"]
        size = log.stat().st_size if log.exists() else -1
        print(c.get("exit_code"), f"size={size}", " ".join(c["argv"][:5]), c["log"])
    print("tmux.status", (EV / "full-tmux.status").read_text().strip() if (EV / "full-tmux.status").exists() else "missing")
    print("wrapper:\n", (EV / "full-tmux.wrapper.log").read_text(errors="replace")[-800:])
    print("tmux ls:\n", subprocess.run(["tmux", "ls"], capture_output=True, text=True).stdout or "(no sessions)")
    print("procs:\n", subprocess.run(["pgrep", "-af", r"workflow\.py|lake |runLinter"], capture_output=True, text=True).stdout[:2000] or "(none)")
    for c in d.get("commands", []):
        if c.get("exit_code") is None:
            t = (EV / c["log"]).read_text(errors="replace")
            print("CURRENT TAIL len", len(t))
            print(t[-1000:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
