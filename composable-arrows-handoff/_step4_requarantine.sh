#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-handoff
EV="$PRIMARY/.handoff/evidence"
export PATH="$HOME/.elan/bin:$PATH"

# If anything is still compiling this checkout, stop.
if pgrep -af 'lake|/lean ' | grep -F mathlib4-handoff | grep -v grep >/dev/null; then
  echo STILL_RUNNING
  pgrep -af 'lake|/lean ' | grep -F mathlib4-handoff || true
  exit 2
fi

python3 - <<'PY'
import json, shutil, os, time
from pathlib import Path
from datetime import datetime, timezone
ev = Path("/home/mateo/mathlib4-handoff/.handoff/evidence")
src = ev / "full.json"
if src.exists():
    dest = ev / f"full.json.interrupted-wrapper-exit15-{time.time_ns()}"
    shutil.copy2(src, dest)
    print("snap", dest)
log = ev / "full-3-1791132670952620620.log"
print("interrupted_full3_bytes", log.stat().st_size if log.exists() else None)
print("interrupted_full3_sha_note_keep_original")
PY

# Re-quarantine MathlibTest produced by the killed official attempt so the next
# official full is again a non-selective MathlibTest rebuild.
python3 - <<'PY'
import os, shutil, time, json
from pathlib import Path
from datetime import datetime, timezone
repo = Path("/home/mateo/mathlib4-handoff")
build = repo / ".lake/build"
ts = time.strftime("%Y%m%dT%H%M%S")
qroot = repo / ".handoff/evidence" / f"quarantine-mathlibtest-{ts}-after-killed-full"
qroot.mkdir(parents=True, exist_ok=True)
moved = []
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
(qroot / "files-moved.txt").write_text("\n".join(moved) + "\n")
(qroot / "QUARANTINE_MANIFEST.json").write_text(json.dumps({
    "timestamp": ts,
    "reason": "Re-quarantine after workflow wrapper SIGTERM (exit 15) during lake --iofail test so official full restarts with cold MathlibTest.",
    "files_moved_count": len(moved),
    "empty_dirs_removed": len(removed_dirs),
    "recorded_at": datetime.now(timezone.utc).isoformat(),
}, indent=2) + "\n")
(Path("/home/mateo/mathlib4-handoff/.handoff/evidence") / f"quarantine-mathlibtest-{ts}-after-killed-full-filelist.txt").write_text("\n".join(moved)+"\n")
print("REQUARANTINE", qroot, "MOVED", len(moved))
left = 0
for dirpath, _, filenames in os.walk(build):
    for name in filenames:
        if "MathlibTest" in (Path(dirpath)/name).relative_to(build).as_posix():
            left += 1
print("remaining_MathlibTest", left)
print("mathlib_dir", (repo/".lake/build/lib/lean/Mathlib").exists())
PY
