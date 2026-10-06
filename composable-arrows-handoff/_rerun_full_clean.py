#!/usr/bin/env python3
"""Clean candidate MathlibTest artifacts, then run official workflow full gate."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/mateo/mathlib4-handoff")
EV = REPO / ".handoff" / "evidence"
ARTIFACT_GLOBS = [
    "ComposableArrowsReduceMap*",
    "ComposableArrowsIntegratedProbe*",
]


def load_wf():
    spec = importlib.util.spec_from_file_location("wf", REPO / ".handoff" / "workflow.py")
    wf = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(wf)
    return wf


def clean() -> list[str]:
    removed: list[str] = []
    for root in [
        REPO / ".lake" / "build" / "lib" / "lean" / "MathlibTest",
        REPO / ".lake" / "build" / "ir" / "MathlibTest",
    ]:
        if not root.exists():
            continue
        for pattern in ARTIFACT_GLOBS:
            for path in root.glob(pattern):
                if path.is_file():
                    path.unlink()
                    removed.append(str(path))
                elif path.is_dir():
                    shutil.rmtree(path)
                    removed.append(str(path) + "/")
    return removed


def main() -> int:
    wf = load_wf()
    fp = wf.fingerprint(REPO)
    print("fingerprint", fp, flush=True)
    # Ensure prerequisites still match
    for stage in ("focused", "downstream"):
        rec = json.loads((EV / f"{stage}.json").read_text())
        assert rec["status"] == "passed" and rec["source_sha256"] == fp, stage
        print(stage, "ok", flush=True)

    # Backup current full marker
    ts = int(time.time())
    bak = EV / "backups"
    bak.mkdir(exist_ok=True)
    shutil.copy2(EV / "full.json", bak / f"full.json.pre-rerun-{ts}")
    removed = clean()
    note = EV / f"full-rerun-clean-note-{ts}.json"
    note.write_text(
        json.dumps(
            {
                "fingerprint": fp,
                "removed_artifacts": removed,
                "purpose": (
                    "Force non-empty lake --iofail test log in official full gate "
                    "by deleting candidate MathlibTest build artifacts before "
                    "workflow.py run full. Benchmark.olean left intact."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("removed", len(removed), "note", note.name, flush=True)

    result = subprocess.run(
        ["python3", str(REPO / ".handoff" / "workflow.py"), "run", "full"],
        cwd=REPO,
    )
    print("workflow_exit", result.returncode, flush=True)

    full = json.loads((EV / "full.json").read_text())
    print("full_status", full.get("status"), "fp", full.get("source_sha256"), flush=True)
    for cmd in full.get("commands", []):
        log = EV / cmd["log"]
        size = log.stat().st_size if log.exists() else None
        print("cmd", cmd["argv"], "exit", cmd.get("exit_code"), "size", size, "log", cmd["log"])
        if cmd.get("argv") == ["lake", "--iofail", "test"] and log.exists():
            print("--- full-3 content ---")
            print(log.read_text(errors="replace"))
            print("--- end ---")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
