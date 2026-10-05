#!/usr/bin/env python3
"""Spot-check one preferred and one original adversarial probe. Does not mutate sources."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

EV = Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence")
PREF = Path("/home/mateo/mathlib4-cursor")
ORIG = Path("/home/mateo/mathlib4-cursor-adv")


def run_probe(repo: Path, lean_rel: str, tag: str, name: str) -> dict:
    src = EV / "adversarial" / lean_rel
    # Prefer nested adversarial sources; fall back to flattened
    if not src.exists():
        src = EV / lean_rel
    # Probes in adv checkout may live under MathlibTest
    # The suite used lake env lean on a copied path. Reuse existing .lean next to log.
    candidates = [
        EV / "adversarial" / f"{tag}_{name}.lean",
        EV / f"advsuite_{tag}_{name}.lean",
    ]
    lean = next((p for p in candidates if p.exists()), None)
    if lean is None:
        raise FileNotFoundError(name)
    # Copy into repo MathlibTest for imports if needed
    dest = repo / "MathlibTest" / f"_SpotCheck_{tag}_{name}.lean"
    dest.write_text(lean.read_text(encoding="utf-8"), encoding="utf-8")
    log = EV / f"spotcheck_{tag}_{name}-{time.time_ns()}.log"
    with log.open("wb") as stream:
        stream.write(f"REPO:{repo}\nSRC:{lean}\nDEST:{dest}\n".encode())
        result = subprocess.run(
            ["lake", "env", "lean", str(dest.relative_to(repo))],
            cwd=repo,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
        stream.write(f"\nEXIT:{result.returncode}\n".encode())
    # Clean untracked spotcheck file so fingerprint/export stay clean on preferred
    dest.unlink(missing_ok=True)
    return {
        "tag": tag,
        "probe": name,
        "exit_code": result.returncode,
        "log": log.name,
        "log_size": log.stat().st_size,
        "source": str(lean),
    }


def main() -> None:
    results = []
    # Preferred should pass custom_ofnat_first; original should fail.
    results.append(run_probe(PREF, "preferred_custom_ofnat_first.lean", "preferred", "custom_ofnat_first"))
    results.append(run_probe(ORIG, "original_custom_ofnat_first.lean", "original", "custom_ofnat_first"))
    out = EV / f"spotcheck-adv-{time.time_ns()}.json"
    payload = {
        "note": "Live spot-check after full-gate rerun; temporary probe files deleted.",
        "results": results,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
