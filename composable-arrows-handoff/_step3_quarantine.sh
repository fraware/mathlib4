#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-handoff
DIAG="$PRIMARY/.handoff/evidence/benchmark-diagnosis"

python3 - <<'PY'
import json
from pathlib import Path
from datetime import datetime, timezone
p = Path("/home/mateo/mathlib4-handoff/.handoff/evidence/benchmark-diagnosis")
cls = {
  "recorded_at": datetime.now(timezone.utc).isoformat(),
  "original_failed_suite_run": {
    "log": "/home/mateo/mathlib4-handoff/.handoff/evidence/full-3-1791084123470358418.log",
    "quoted_error": "error: MathlibTest/ClickSuggestions/Benchmark.lean:33:0: failed",
    "lake_summary": "Some required targets logged failures: - MathlibTest.ClickSuggestions.Benchmark; error: build failed",
    "job_wall": "Building MathlibTest.ClickSuggestions.Benchmark (131s)",
    "command": ["lake", "--iofail", "test"],
  },
  "assertion_source": "MathlibTest/ClickSuggestions/Benchmark.lean:33 is `guard (all < 60_000)` after measureImport of all four discrimination trees",
  "isolated_diagnosis": {
    "original_exit": 0,
    "preferred_exit": 0,
    "original_module_build": "Built MathlibTest.ClickSuggestions.Benchmark (30s)",
    "preferred_module_build": "Built MathlibTest.ClickSuggestions.Benchmark (53s)",
    "original_log": str(p/"original-lake-build-Benchmark.log"),
    "preferred_log": str(p/"preferred-lake-build-Benchmark.log"),
    "notes": "Original checkout had no prior Benchmark artifacts so lake also completed remaining Mathlib jobs (8974 jobs, 401s wall). Preferred wiped 16 Benchmark artifacts then rebuilt (53s module, 69s wall). Both isolated rebuilds succeeded; no OOM/Killed/elaboration errors in these logs.",
  },
  "classification": "60-second assertion",
  "not": [
    "memory exhaustion (no Killed/OOM in the failed suite log; isolated runs exit 0)",
    "other hard ulimit (cpu unlimited; isolated pass)",
    "elaboration/type error (message is `failed` at the guard, not a type mismatch)",
    "preferred DESIGN (original reducer also passes isolated; original suite failure is the same guard under concurrent MathlibTest load)",
  ],
  "continue_candidate": "preferred",
}
(p/"CLASSIFICATION.json").write_text(json.dumps(cls, indent=2)+"\n")
print("wrote CLASSIFICATION.json")
print(json.dumps(cls["classification"]))
PY

echo "==== quarantine check no lake ===="
if pgrep -af 'lake |mathlib4-handoff' | grep -E 'lake |/lean ' | grep -v grep; then
  echo REFUSING lake running
  exit 2
fi
echo no competing lake

python3 - <<'PY'
import os, shutil, time, json
from pathlib import Path
from datetime import datetime, timezone

repo = Path("/home/mateo/mathlib4-handoff")
build = repo / ".lake/build"
ts = time.strftime("%Y%m%dT%H%M%S")
qroot = repo / ".handoff/evidence" / f"quarantine-mathlibtest-{ts}"
qroot.mkdir(parents=True, exist_ok=True)
moved = []
skipped_nonfile = []
# Walk .lake/build for MathlibTest artifacts only (Lean + native/IR + traces)
if not build.exists():
    raise SystemExit("no .lake/build")
for dirpath, dirnames, filenames in os.walk(build, topdown=True):
    # do not descend into packages
    rel = Path(dirpath).relative_to(build).as_posix()
    if rel.startswith("packages/") or "/packages/" in ("/"+rel+"/"):
        dirnames[:] = []
        continue
    for name in filenames:
        src = Path(dirpath) / name
        posix = src.relative_to(build).as_posix()
        if "MathlibTest" not in posix:
            continue
        dest = qroot / "from-lake-build" / posix
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        moved.append(posix)

# remove now-empty MathlibTest dirs in active tree (optional cleanliness; record)
removed_dirs = []
for dirpath, dirnames, filenames in os.walk(build, topdown=False):
    posix = Path(dirpath).relative_to(build).as_posix()
    if "MathlibTest" not in posix:
        continue
    try:
        if not os.listdir(dirpath):
            os.rmdir(dirpath)
            removed_dirs.append(posix)
    except OSError:
        pass

manifest = {
    "timestamp": ts,
    "quarantine_dir": str(qroot),
    "files_moved_count": len(moved),
    "empty_dirs_removed_from_active_tree": removed_dirs,
    "files_moved": moved,
    "retained": "ordinary Mathlib and dependency caches under .lake/build were not moved unless their path contains MathlibTest",
    "recorded_at": datetime.now(timezone.utc).isoformat(),
}
(qroot / "QUARANTINE_MANIFEST.json").write_text(json.dumps({k:v for k,v in manifest.items() if k!="files_moved"}, indent=2)+"\n")
(qroot / "files-moved.txt").write_text("\n".join(moved)+"\n")
# also copy a compact list into evidence root for export visibility
(Path("/home/mateo/mathlib4-handoff/.handoff/evidence") / f"quarantine-mathlibtest-{ts}-filelist.txt").write_text("\n".join(moved)+"\n")
print("QUARANTINE_DIR", qroot)
print("MOVED", len(moved))
print("EMPTY_DIRS", len(removed_dirs))
# sanity: Mathlib cache still present
olean = list((repo/".lake/build/lib/lean/Mathlib").glob("*.olean"))[:3] if (repo/".lake/build/lib/lean/Mathlib").exists() else []
print("sample_mathlib_exists", bool(list((repo/".lake/build/lib/lean").glob("Mathlib*"))))
print("mathlib_dir", (repo/".lake/build/lib/lean/Mathlib").exists())
left = []
for dirpath, _, filenames in os.walk(build):
    for name in filenames:
        posix = (Path(dirpath)/name).relative_to(build).as_posix()
        if "MathlibTest" in posix:
            left.append(posix)
print("remaining_MathlibTest_in_build", len(left))
if left[:10]:
    print("remaining sample", left[:10])
PY
