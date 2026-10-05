#!/usr/bin/env python3
"""Inspect primary/adversarial WSL checkouts without mutating state."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

REPO = Path.home() / "mathlib4-cursor"
ADV = Path.home() / "mathlib4-cursor-adv"
EV = REPO / ".cursor-handoff" / "evidence"
HANDOFF_WIN = Path("/mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff")
BASE = "a3cfff85f9dfe0b1c6b6e92899febc338687fcc3"
BASIC = "Mathlib/CategoryTheory/ComposableArrows/Basic.lean"
REG = "MathlibTest/ComposableArrowsReduceMap.lean"
PROBE = "MathlibTest/ComposableArrowsIntegratedProbe.lean"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes()) if p.exists() else "MISSING"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def pgrep(pattern: str) -> str:
    r = subprocess.run(["pgrep", "-af", pattern], capture_output=True, text=True)
    return r.stdout.strip() or "(none)"


def main() -> int:
    env = os.environ.copy()
    env["PATH"] = str(Path.home() / ".elan" / "bin") + os.pathsep + env.get("PATH", "")

    print("=== PRIMARY HEAD / STATUS ===")
    print("HEAD", git(REPO, "rev-parse", "HEAD"))
    print("status:\n", git(REPO, "status", "-sb"))
    print("dirty files:\n", git(REPO, "status", "--porcelain") or "(clean porcelain empty)")
    print("toolchain", (REPO / "lean-toolchain").read_text().strip())

    # Fingerprint via workflow if available
    print("\n=== FINGERPRINT ===")
    sys_path_hint = REPO / ".cursor-handoff"
    import sys

    sys.path.insert(0, str(sys_path_hint))
    try:
        import workflow  # type: ignore

        fp = workflow.fingerprint(REPO)
        print("workflow.fingerprint", fp)
    except Exception as e:
        print("workflow.fingerprint failed:", e)
        # fallback: hash tracked sources used by gates
        parts = []
        for rel in (BASIC, REG, PROBE):
            p = REPO / rel
            h = sha256_file(p)
            parts.append(f"{rel}={h}")
            print(parts[-1])
        fp = sha256_bytes("\n".join(parts).encode())
        print("fallback_combo", fp)

    print("\n=== GATE MARKERS ===")
    for name in ("baseline.json", "focused.json", "downstream.json", "full.json", "SUMMARY.json"):
        p = EV / name
        if not p.exists():
            print(name, "MISSING")
            continue
        d = json.loads(p.read_text())
        keys = {k: d.get(k) for k in ("status", "source_sha256", "candidate", "error", "finished_unix", "started_unix") if k in d or True}
        # trim None-heavy
        keys = {k: v for k, v in keys.items() if v is not None or k in ("status", "source_sha256")}
        print(name, json.dumps(keys, sort_keys=True)[:500])
        if "commands" in d:
            for c in d["commands"]:
                log = EV / c.get("log", "")
                size = log.stat().st_size if log.exists() else -1
                print("  cmd", c.get("exit_code"), f"logsize={size}", c.get("log"), c.get("argv", [])[:6])

    print("\n=== INTEGRATED PROBE ===")
    probe_wt = (REPO / PROBE).read_bytes()
    probe_git = subprocess.check_output(["git", "-C", str(REPO), "show", f"HEAD:{PROBE}"])
    print("byte_identical_to_HEAD", probe_wt == probe_git)
    print("sha256_wt", sha256_bytes(probe_wt))
    print("sha256_git", sha256_bytes(probe_git))

    print("\n=== REGRESSION / LINTER DISABLES ===")
    reg = (REPO / REG).read_text(errors="replace")
    print("exists", (REPO / REG).exists(), "bytes", len(reg.encode()))
    print("sha256", sha256_file(REPO / REG))
    print("examples", reg.count("\nexample "))
    print("visit", reg.count("check_reduce_map_visit"))
    print("decline", reg.count("check_reduce_map_declines"))
    print("unusedTactic_disabled", "linter.unusedTactic false" in reg or "linter.unusedTactic" in reg and "set_option linter.unusedTactic false" in reg)
    print("unreachableTactic_disabled", "set_option linter.unreachableTactic false" in reg)
    print("any_set_option_linter", [ln.strip() for ln in reg.splitlines() if "set_option linter" in ln])
    print("sorry", "sorry" in reg)
    print("admit", "admit" in reg)
    print("has_rfl_close_inside_tactic", "evalTactic (← `(tactic| rfl))" in reg or "evalTactic (← `(tactic| rfl))" in reg)

    print("\n=== BASIC.lean reducer ===")
    print("sha256", sha256_file(REPO / BASIC))
    diff = subprocess.check_output(["git", "-C", str(REPO), "diff", "HEAD", "--", BASIC])
    print("diff_bytes", len(diff))
    # show reduceMap presence
    basic = (REPO / BASIC).read_text(errors="replace")
    print("has_reduceMap", "reduceMap" in basic)
    print("has_getFinValue", "getFinValue?" in basic)
    print("has_sorry", "sorry" in basic)

    print("\n=== PROCESSES ===")
    print("lake:\n", pgrep("lake"))
    print("workflow:\n", pgrep("workflow.py"))
    print("lean:\n", pgrep("lean"))
    print("runLinter:\n", pgrep("runLinter"))

    for pidf in ("full-rerun.pid", "full-rerun2.pid", "detached-full.pid", "detached-gates.pid"):
        p = EV / pidf
        if p.exists():
            pid = p.read_text().strip()
            alive = subprocess.run(["ps", "-p", pid], capture_output=True).returncode == 0
            print(f"{pidf}={pid} alive={alive}")

    for wrap in ("full-rerun.wrapper.log", "full-rerun2.wrapper.log", "detached-full.wrapper.log"):
        p = EV / wrap
        if p.exists():
            t = p.read_text(errors="replace")
            print(f"\n--- {wrap} size={len(t)} tail ---")
            print(t[-800:])

    print("\n=== ADVERSARIAL CHECKOUT ===")
    if ADV.exists():
        print("HEAD", git(ADV, "rev-parse", "HEAD"))
        print("status:\n", git(ADV, "status", "-sb"))
        bdiff = subprocess.check_output(["git", "-C", str(ADV), "diff", "HEAD", "--", BASIC])
        print("Basic.lean diff_bytes", len(bdiff), "(0 means original reducer)")
        adv_dir = EV / "adversarial"
        print("adv evidence dir exists", adv_dir.exists())
        if adv_dir.exists():
            print("entries", len(list(adv_dir.iterdir())))
            matrix = adv_dir / "matrix.json"
            if matrix.exists():
                m = json.loads(matrix.read_text())
                print("matrix timestamp", m.get("timestamp"), "results", len(m.get("results", [])))
                for r in m.get("results", []):
                    print(f"  {r['tag']}/{r['probe']} exit={r['exit_code']}")
            summary = adv_dir / "SUMMARY.md"
            if summary.exists():
                print("\nSUMMARY.md head:\n", summary.read_text()[:2000])
    else:
        print("NO ADV CHECKOUT")

    print("\n=== ZIP ===")
    for zpath in (EV / "cursor-validation-evidence.zip", HANDOFF_WIN / "cursor-validation-evidence.zip", REPO / ".cursor-handoff" / "cursor-validation-evidence.zip"):
        print(zpath, "exists", zpath.exists(), "size", zpath.stat().st_size if zpath.exists() else 0)
        if zpath.exists():
            with zipfile.ZipFile(zpath) as zf:
                names = zf.namelist()
                print("  entries", len(names))
                for n in sorted(names)[:40]:
                    print("   ", n, zf.getinfo(n).file_size)

    print("\n=== FINAL_REPORT / harness-repairs ===")
    for name in ("FINAL_REPORT.md", "harness-repairs.md", "adversarial-summary.md"):
        p = EV / name
        print(name, "exists", p.exists(), "bytes", p.stat().st_size if p.exists() else 0)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
