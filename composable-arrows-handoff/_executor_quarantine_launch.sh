#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-handoff
EV="$PRIMARY/.handoff/evidence"
export PATH="$HOME/.elan/bin:$PATH"
date -Is

# Refuse competing builds
if pgrep -af 'lake ' | grep -F mathlib4-handoff | grep -v grep; then
  echo REFUSING_LAKE_RUNNING
  exit 2
fi
if pgrep -af 'workflow.py run full' | grep -v grep; then
  echo REFUSING_WORKFLOW_RUNNING
  exit 2
fi
echo NO_COMPETING_BUILD

echo ===PRE_QUARANTINE_COUNT===
python3 - <<'PY'
from pathlib import Path
b = Path("/home/mateo/mathlib4-handoff/.lake/build")
n = sum(1 for p in b.rglob("*") if p.is_file() and "MathlibTest" in p.as_posix())
print("mathlibtest_files", n)
print("mathlib_cache", (b / "lib/lean/Mathlib").exists())
PY

echo ===FOCUSED_DOWNSTREAM===
python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/mateo/mathlib4-handoff/.handoff")
import workflow
repo = Path("/home/mateo/mathlib4-handoff")
fp = workflow.fingerprint(repo)
print("FINGERPRINT", fp)
for name in ("focused", "downstream"):
    r = json.loads((repo / ".handoff/evidence" / f"{name}.json").read_text())
    ok = r.get("status") == "passed" and r.get("source_sha256") == fp
    print(name, r.get("status"), "match" if ok else "STALE", r.get("source_sha256", "")[:16])
    if not ok:
        raise SystemExit(4)
PY

echo ===QUARANTINE===
python3 - <<'PY'
import os, shutil, time, json
from pathlib import Path
from datetime import datetime, timezone

repo = Path("/home/mateo/mathlib4-handoff")
build = repo / ".lake/build"
ts = time.strftime("%Y%m%dT%H%M%S")
qroot = repo / ".handoff/evidence" / f"quarantine-mathlibtest-{ts}-cold-rerun"
qroot.mkdir(parents=True, exist_ok=True)
moved = []
if not build.exists():
    raise SystemExit("no .lake/build")
for dirpath, dirnames, filenames in os.walk(build, topdown=True):
    rel = Path(dirpath).relative_to(build).as_posix()
    if rel.startswith("packages/"):
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
    "reason": "Re-quarantine before cold official full after interrupted full-3; keep Mathlib caches; no prebuild",
    "quarantine_dir": str(qroot),
    "files_moved_count": len(moved),
    "empty_dirs_removed_count": len(removed_dirs),
    "retained": "ordinary Mathlib and dependency caches under .lake/build were not moved unless path contains MathlibTest",
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "preserved_failed_logs_untouched": True,
}
(qroot / "QUARANTINE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
(qroot / "files-moved.txt").write_text("\n".join(moved) + "\n")
flist = Path("/home/mateo/mathlib4-handoff/.handoff/evidence") / f"quarantine-mathlibtest-{ts}-cold-rerun-filelist.txt"
flist.write_text("\n".join(moved) + "\n")
print("QUARANTINE_DIR", qroot)
print("MOVED", len(moved))
print("EMPTY_DIRS", len(removed_dirs))
print("mathlib_dir", (repo / ".lake/build/lib/lean/Mathlib").exists())
left = 0
for dirpath, _, filenames in os.walk(build):
    for name in filenames:
        if "MathlibTest" in (Path(dirpath) / name).relative_to(build).as_posix():
            left += 1
print("remaining_MathlibTest_in_build", left)
PY

# Snapshot stale running marker only; do not touch preserved fail logs
if [ -f "$EV/full.json" ]; then
  cp -a "$EV/full.json" "$EV/full.json.stale-running-before-cold-$(date +%s)"
  echo SNAPSHOTTED_STALE_FULL_JSON
fi

# Patch WSL workflow export scope if still old disclaimer
python3 - <<'PY'
from pathlib import Path
p = Path("/home/mateo/mathlib4-handoff/.handoff/workflow.py")
text = p.read_text(encoding="utf-8")
old = '"scope": "Local command evidence; baseline discrimination still needs its separate report.",'
new = (
    '"scope": "Local command evidence plus recorded original-vs-preferred adversarial comparison.",\n'
    '        "comparison": {\n'
    '            "classification": "evidence/benchmark-diagnosis/CLASSIFICATION.json",\n'
    '            "preserved_failed_suite": "evidence/preserved-benchmark-fail/",\n'
    '            "diagnosis_dir": "evidence/benchmark-diagnosis/",\n'
    '            "note": "Isolated Benchmark passed for original and preferred; suite-load 60s guard failure is recorded separately.",\n'
    '        },'
)
if old in text:
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("PATCHED_EXPORT_SCOPE")
elif "recorded original-vs-preferred adversarial comparison" in text:
    print("EXPORT_SCOPE_ALREADY_PATCHED")
else:
    print("EXPORT_SCOPE_UNEXPECTED")
    raise SystemExit(3)
PY

echo ===LAUNCH_TMUX===
tmux start-server
tmux has-session -t keepalive 2>/dev/null || tmux new-session -d -s keepalive "sleep infinity"
if tmux has-session -t mathlib-full 2>/dev/null; then
  echo mathlib-full_ALREADY_EXISTS
  tmux ls
  exit 2
fi

tr -d '\r' < /mnt/c/Users/mateo/mathlib4-1/composable-arrows-handoff/_step4_full_detached.sh > /tmp/_step4_full_detached.sh
chmod +x /tmp/_step4_full_detached.sh
tmux new-session -d -s mathlib-full "bash /tmp/_step4_full_detached.sh; echo EXIT:\$? >> $EV/full-official-detached.wrapper.log; exec sleep infinity"
sleep 6
echo TMUX
tmux ls
echo WRAPPER_TAIL
tail -20 "$EV/full-official-detached.wrapper.log" || true
echo PROCS
ps -eo pid,etime,cmd | grep -E 'workflow.py|lake ' | grep -v grep || true
echo FULL_JSON
cat "$EV/full.json" || true
