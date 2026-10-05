#!/usr/bin/env python3
"""Independent rigorous audit of ComposableArrows validation evidence."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import zipfile

REPO = pathlib.Path.home() / "mathlib4-cursor"
EV = REPO / ".cursor-handoff" / "evidence"
HANDOFF = REPO / ".cursor-handoff"
EXPECTED_HEAD = "a3cfff85f9dfe0b1c6b6e92899febc338687fcc3"
EXPECTED_TC = "leanprover/lean4:v4.35.0-rc3"
BASIC = "Mathlib/CategoryTheory/ComposableArrows/Basic.lean"
PROBE = "MathlibTest/ComposableArrowsIntegratedProbe.lean"
REG = "MathlibTest/ComposableArrowsReduceMap.lean"


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fingerprint(repo: pathlib.Path) -> str:
    sys.path.insert(0, str(repo / ".cursor-handoff"))
    import workflow  # type: ignore

    return workflow.fingerprint(repo)


def main() -> int:
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    tc = (REPO / "lean-toolchain").read_text().strip()
    print(f"HEAD={head} match={head == EXPECTED_HEAD}")
    print(f"TOOLCHAIN={tc} match={tc == EXPECTED_TC}")

    current = fingerprint(REPO)
    print(f"current_fingerprint={current}")

    for name in ["baseline", "focused", "downstream", "full", "SUMMARY"]:
        data = json.loads((EV / f"{name}.json").read_text())
        src = data.get("source_sha256") or data.get("final_source_sha256")
        print(f"\n=== {name}.json ===")
        print(json.dumps(data, indent=2)[:2500])
        if src:
            print(f"fingerprint_match_current={src == current}")

    for rel in [BASIC, REG, PROBE]:
        p = REPO / rel
        print(f"file {rel} sha256={sha256_file(p)} exists={p.exists()}")

    # Integrated probe vs git HEAD version (must be unchanged)
    probe_git = subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"HEAD:{PROBE}"],
    )
    probe_wt = (REPO / PROBE).read_bytes()
    print(f"integrated_probe_byte_identical_to_HEAD={probe_git == probe_wt}")
    print(f"integrated_probe_sha256_wt={hashlib.sha256(probe_wt).hexdigest()}")
    print(f"integrated_probe_sha256_git={hashlib.sha256(probe_git).hexdigest()}")

    # Candidate patch vs working tree reducer portion
    cand = (EV / "candidate.patch").read_text(errors="replace")
    print(f"\ncandidate.patch bytes={len(cand.encode())} sha256={sha256_file(EV / 'candidate.patch')}")

    # Count examples in regression
    reg = (REPO / REG).read_text()
    examples = reg.count("\nexample ")
    visits = reg.count("check_reduce_map_visit")
    declines = reg.count("check_reduce_map_declines")
    print(f"\nregression examples={examples} visits={visits} declines={declines}")
    print(f"linter.unusedTactic disabled={'linter.unusedTactic false' in reg}")
    print(f"linter.unreachableTactic disabled={'linter.unreachableTactic false' in reg}")
    print(f"sorry_present={'sorry' in reg}")
    print(f"admit_present={'admit' in reg}")

    # Unpack zip listing
    zpath = HANDOFF / "cursor-validation-evidence.zip"
    print(f"\nzip exists={zpath.exists()} size={zpath.stat().st_size if zpath.exists() else 0}")
    if zpath.exists():
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
            print(f"zip_entries={len(names)}")
            for n in sorted(names):
                info = zf.getinfo(n)
                print(f"  {n} size={info.file_size}")

    # Tail full logs for success markers
    print("\n=== full.json commands / exit codes ===")
    full = json.loads((EV / "full.json").read_text())
    for cmd in full.get("commands", []):
        print(json.dumps(cmd, indent=2)[:800])

    # Find newest full-* logs and tail
    full_logs = sorted(EV.glob("full-*.log"), key=lambda p: p.stat().st_mtime)
    print(f"\nfull_log_count={len(full_logs)}")
    for log in full_logs[-6:]:
        text = log.read_text(errors="replace")
        print(f"\n--- {log.name} size={len(text)} mtime ---")
        print(text[-800:] if text else "<empty>")

    # Detached gates status
    for name in ["detached-gates.status", "detached-full.status", "detached-gates.wrapper.log"]:
        p = EV / name
        if p.exists():
            print(f"\n=== {name} ===\n{p.read_text(errors='replace')[-1500:]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
