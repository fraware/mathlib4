#!/usr/bin/env bash
set -euo pipefail
# Re-quarantine remaining MathlibTest, then start detached full with PID file.
PRIMARY=/home/mateo/mathlib4-cursor
EV="$PRIMARY/.cursor-handoff/evidence"
if pgrep -af 'lake |workflow.py' | grep mathlib4-cursor | grep -v grep >/dev/null; then
  echo REFUSING
  pgrep -af 'lake |workflow.py' || true
  exit 2
fi

python3 - <<'PY'
import os, shutil, time, json
from pathlib import Path
from datetime import datetime, timezone
repo = Path("/home/mateo/mathlib4-cursor")
build = repo / ".lake/build"
ts = time.strftime("%Y%m%dT%H%M%S")
qroot = repo / ".cursor-handoff/evidence" / f"quarantine-mathlibtest-{ts}-remaining"
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
for dirpath, dirnames, filenames in os.walk(build, topdown=False):
    posix = Path(dirpath).relative_to(build).as_posix()
    if "MathlibTest" not in posix:
        continue
    try:
        if not os.listdir(dirpath):
            os.rmdir(dirpath)
    except OSError:
        pass
(qroot / "files-moved.txt").write_text("\n".join(moved) + "\n")
(qroot / "QUARANTINE_MANIFEST.json").write_text(json.dumps({
    "timestamp": ts,
    "reason": "Second sweep: leftover MathlibTest after killed full / first re-quarantine",
    "files_moved_count": len(moved),
    "recorded_at": datetime.now(timezone.utc).isoformat(),
}, indent=2)+"\n")
print("MOVED", len(moved), "DIR", qroot)
left=0
for dirpath,_,filenames in os.walk(build):
    for name in filenames:
        if "MathlibTest" in (Path(dirpath)/name).relative_to(build).as_posix():
            left += 1
print("LEFT", left)
print("MATHLIB", (repo/".lake/build/lib/lean/Mathlib").exists())
PY

# Detach using setsid so a later Windows wrapper death cannot take the job.
tr -d '\r' < /mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff/_step4_full_detached.sh > /tmp/_step4_full_detached.sh
chmod +x /tmp/_step4_full_detached.sh
setsid bash /tmp/_step4_full_detached.sh </dev/null >/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.nohup.out 2>&1 &
echo $! > /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.launcher.pid
sleep 3
echo LAUNCHER_PID_FILE
cat /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.launcher.pid
echo WRAPPER
head -30 /home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-official-detached.wrapper.log || true
echo PROCS
ps -eo pid,cmd | grep -E 'workflow.py|lake ' | grep -v grep || true
