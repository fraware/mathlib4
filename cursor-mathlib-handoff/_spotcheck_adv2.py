#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import time
from pathlib import Path

EV = Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence")


def load_wf():
    spec = importlib.util.spec_from_file_location(
        "wf", "/home/mateo/mathlib4-cursor/.cursor-handoff/workflow.py"
    )
    wf = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(wf)
    return wf


def run_one(repo: Path, tag: str, name: str) -> dict:
    lean = EV / "adversarial" / f"{tag}_{name}.lean"
    dest = repo / "MathlibTest" / f"_SpotCheck_{tag}_{name}.lean"
    dest.write_text(lean.read_text(encoding="utf-8"), encoding="utf-8")
    log = EV / f"spotcheck_{tag}_{name}-{time.time_ns()}.log"
    with log.open("wb") as stream:
        stream.write(f"REPO:{repo}\nLEAN:{lean}\n".encode())
        result = subprocess.run(
            ["lake", "env", "lean", str(dest.relative_to(repo))],
            cwd=repo,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
        stream.write(f"\nEXIT:{result.returncode}\n".encode())
    dest.unlink(missing_ok=True)
    return {
        "tag": tag,
        "probe": name,
        "exit_code": result.returncode,
        "log": log.name,
        "log_size": log.stat().st_size,
        "log_tail": log.read_text(errors="replace")[-500:],
    }


def main() -> None:
    wf = load_wf()
    pref = Path("/home/mateo/mathlib4-cursor")
    orig = Path("/home/mateo/mathlib4-cursor-adv")
    fp_before = wf.fingerprint(pref)
    results = [
        run_one(pref, "preferred", "custom_ofnat_first"),
        run_one(orig, "original", "custom_ofnat_first"),
        run_one(pref, "preferred", "custom_ofnat_first_wrong_sem"),
        run_one(orig, "original", "custom_ofnat_first_wrong_sem"),
    ]
    fp_after = wf.fingerprint(pref)
    payload = {
        "fingerprint_before": fp_before,
        "fingerprint_after": fp_after,
        "fingerprint_unchanged": fp_before == fp_after,
        "results": results,
        "note": "Live spot-check; temporary MathlibTest/_SpotCheck_*.lean deleted after each run.",
    }
    out = EV / f"spotcheck-adv-{time.time_ns()}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print("wrote", out.name)
    if fp_before != fp_after:
        raise SystemExit("FINGERPRINT CHANGED — stop and inspect preferred tree")


if __name__ == "__main__":
    main()
