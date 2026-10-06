#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-handoff
EV="$PRIMARY/.handoff/evidence"
export PATH="$HOME/.elan/bin:$PATH"

# leftover MathlibTest from aborted start
python3 - <<'PY'
import os, shutil, time, json
from pathlib import Path
from datetime import datetime, timezone
repo = Path("/home/mateo/mathlib4-handoff")
build = repo / ".lake/build"
ts = time.strftime("%Y%m%dT%H%M%S")
qroot = repo / ".handoff/evidence" / f"quarantine-mathlibtest-{ts}-wsl-restart"
moved=[]
if build.exists():
    for dirpath, dirnames, filenames in os.walk(build, topdown=True):
        rel = Path(dirpath).relative_to(build).as_posix()
        if rel.startswith("packages/"):
            dirnames[:] = []
            continue
        for name in filenames:
            src = Path(dirpath)/name
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
qroot.mkdir(parents=True, exist_ok=True)
(qroot/"files-moved.txt").write_text("\n".join(moved)+"\n")
(qroot/"QUARANTINE_MANIFEST.json").write_text(json.dumps({
    "reason": "WSL VM idle-restart killed official full; sweep leftovers before tmux rerun",
    "files_moved_count": len(moved),
    "recorded_at": datetime.now(timezone.utc).isoformat(),
}, indent=2)+"\n")
print("MOVED", len(moved))
left=0
if build.exists():
    for dirpath,_,filenames in os.walk(build):
        for name in filenames:
            if "MathlibTest" in (Path(dirpath)/name).relative_to(build).as_posix():
                left += 1
print("LEFT", left)
print("MATHLIB", (repo/".lake/build/lib/lean/Mathlib").exists())
PY

tmux has-session -t keepalive 2>/dev/null || tmux new-session -d -s keepalive "sleep infinity"
# snapshot stale running marker
if [ -f "$EV/full.json" ]; then
  cp -a "$EV/full.json" "$EV/full.json.stale-running-before-tmux-$(date +%s)" || true
fi

tmux has-session -t mathlib-full 2>/dev/null && tmux kill-session -t mathlib-full || true
# copy script unix
tr -d '\r' < /mnt/c/Users/mateo/mathlib4-1/composable-arrows-handoff/_step4_full_detached.sh > /tmp/_step4_full_detached.sh
chmod +x /tmp/_step4_full_detached.sh
tmux new-session -d -s mathlib-full "bash /tmp/_step4_full_detached.sh; echo EXIT:\$? >> $EV/full-official-detached.wrapper.log; exec sleep infinity"
sleep 4
echo TMUX
tmux ls
echo WRAPPER
head -20 "$EV/full-official-detached.wrapper.log" || true
echo PROCS
ps -eo pid,cmd | grep -E 'workflow.py|lake ' | grep -v grep || true
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0,"/home/mateo/mathlib4-handoff/.handoff")
import workflow
print("FINGERPRINT", workflow.fingerprint(Path("/home/mateo/mathlib4-handoff")))
PY
