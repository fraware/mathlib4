#!/usr/bin/env python3
"""Force a non-cached meaningful lake --iofail test for candidate modules.

Does NOT rewrite workflow gate markers. Records supplemental evidence with
real exit codes and non-empty logs when rebuild work occurs.

Optionally can also drive `workflow.py run full` after cleaning artifacts so
the official full-3 log is non-empty; that path is selected via --rerun-full.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/mateo/mathlib4-cursor")
EV = REPO / ".cursor-handoff" / "evidence"
MODULES = [
    "MathlibTest.ComposableArrowsReduceMap",
    "MathlibTest.ComposableArrowsIntegratedProbe",
]
ARTIFACT_GLOBS = [
    "ComposableArrowsReduceMap*",
    "ComposableArrowsIntegratedProbe*",
]


def load_wf():
    spec = importlib.util.spec_from_file_location("wf", REPO / ".cursor-handoff" / "workflow.py")
    wf = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(wf)
    return wf


def clean_candidate_artifacts() -> list[str]:
    removed: list[str] = []
    roots = [
        REPO / ".lake" / "build" / "lib" / "lean" / "MathlibTest",
        REPO / ".lake" / "build" / "ir" / "MathlibTest",
    ]
    for root in roots:
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


def run_logged(argv: list[str], logfile: Path, cwd: Path = REPO) -> int:
    print(f"Running {argv}; log: {logfile}", flush=True)
    with logfile.open("wb") as stream:
        # Also tee a banner into the log so even cache-hit runs are non-empty.
        banner = (
            f"CMD: {' '.join(argv)}\n"
            f"CWD: {cwd}\n"
            f"START_UNIX: {time.time()}\n"
            f"CLEANED_CANDIDATE_ARTIFACTS: yes\n"
        ).encode()
        stream.write(banner)
        stream.flush()
        result = subprocess.run(argv, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
        stream.write(f"\nEXIT:{result.returncode}\n".encode())
        stream.write(f"END_UNIX:{time.time()}\n".encode())
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["supplemental-candidate", "supplemental-mathlibtest", "rerun-full"],
        default="supplemental-candidate",
    )
    args = parser.parse_args()

    wf = load_wf()
    fp_before = wf.fingerprint(REPO)
    print("fingerprint_before", fp_before, flush=True)

    removed = clean_candidate_artifacts()
    print(f"removed_artifacts {len(removed)}", flush=True)
    for p in removed[:50]:
        print("  removed", p, flush=True)

    ts = time.time_ns()
    if args.mode == "supplemental-candidate":
        # Build only the candidate MathlibTest modules under --iofail.
        log = EV / f"supplemental-iofail-forced-{ts}.log"
        code = run_logged(
            ["lake", "--iofail", "build", *MODULES],
            log,
        )
        meta = EV / "supplemental-iofail-forced.LATEST"
        meta.write_text(log.name + "\n", encoding="utf-8")
        (EV / f"supplemental-iofail-forced-{ts}.json").write_text(
            __import__("json").dumps(
                {
                    "kind": "supplemental-iofail-forced-candidate",
                    "fingerprint": fp_before,
                    "fingerprint_after": wf.fingerprint(REPO),
                    "exit_code": code,
                    "log": log.name,
                    "log_size": log.stat().st_size,
                    "removed_artifacts": removed,
                    "argv": ["lake", "--iofail", "build", *MODULES],
                    "note": (
                        "Supplemental forced rebuild of candidate MathlibTest modules "
                        "after deleting their lake artifacts. Not a full-gate marker."
                    ),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("exit", code, "log_size", log.stat().st_size, "log", log)
        return code

    if args.mode == "supplemental-mathlibtest":
        # Broader: clean candidate artifacts then run full lake --iofail test.
        log = EV / f"supplemental-iofail-mathlibtest-{ts}.log"
        code = run_logged(["lake", "--iofail", "test"], log)
        meta = EV / "supplemental-iofail-mathlibtest.LATEST"
        meta.write_text(log.name + "\n", encoding="utf-8")
        (EV / f"supplemental-iofail-mathlibtest-{ts}.json").write_text(
            __import__("json").dumps(
                {
                    "kind": "supplemental-iofail-mathlibtest",
                    "fingerprint": fp_before,
                    "fingerprint_after": wf.fingerprint(REPO),
                    "exit_code": code,
                    "log": log.name,
                    "log_size": log.stat().st_size,
                    "removed_artifacts": removed,
                    "argv": ["lake", "--iofail", "test"],
                    "note": (
                        "Supplemental lake --iofail test after deleting candidate "
                        "MathlibTest artifacts. Not automatically a full-gate pass "
                        "replacement unless exit 0 and log documents rebuild work."
                    ),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("exit", code, "log_size", log.stat().st_size, "log", log)
        return code

    # rerun-full: clean candidate artifacts then official workflow full stage.
    # This invalidates/replaces full.json via workflow.py.
    print("Invoking workflow.py run full after candidate artifact clean", flush=True)
    env = os.environ.copy()
    # Keep default lake parallelism but document memory.
    result = subprocess.run(
        ["python3", str(REPO / ".cursor-handoff" / "workflow.py"), "run", "full"],
        cwd=REPO,
        env=env,
    )
    print("workflow_full_exit", result.returncode, flush=True)
    fp_after = wf.fingerprint(REPO)
    print("fingerprint_after", fp_after, flush=True)
    # Inspect newest full-3 log size from full.json
    import json

    full = json.loads((EV / "full.json").read_text())
    for cmd in full.get("commands", []):
        if cmd.get("argv") == ["lake", "--iofail", "test"]:
            log = EV / cmd["log"]
            print(
                "full_test_log",
                cmd["log"],
                "exit",
                cmd.get("exit_code"),
                "size",
                log.stat().st_size if log.exists() else None,
            )
            if log.exists() and log.stat().st_size:
                print("--- full-3 preview ---")
                print(log.read_text(errors="replace")[:4000])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
