#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-cursor
EV="$PRIMARY/.cursor-handoff/evidence"
BIN="$PRIMARY/.cursor-handoff/bin"
export PATH="$HOME/.elan/bin:$PATH"
date -Is

if pgrep -af 'lake ' | grep -F mathlib4-cursor | grep -v grep; then
  echo REFUSING_LAKE_RUNNING; exit 2
fi
if pgrep -af 'workflow.py run full' | grep -v grep; then
  echo REFUSING_WORKFLOW_RUNNING; exit 2
fi
echo NO_COMPETING_BUILD

# Preserve this OOM-interrupted cold run (do NOT overwrite preserved-benchmark-fail)
ARCH="$EV/preserved-oom-interrupted-full-20261005T0825"
mkdir -p "$ARCH"
cp -a "$EV/full.json" "$ARCH/full.json.stale-running" 2>/dev/null || true
cp -a "$EV/full-3-1791213939582217433.log" "$ARCH/" 2>/dev/null || true
cp -a "$EV/full-1-1791213918547756048.log" "$ARCH/" 2>/dev/null || true
cp -a "$EV/full-2-1791213929099418327.log" "$ARCH/" 2>/dev/null || true
{
  echo "recorded_at=$(date -Is)"
  echo "reason=OOM killed lean during cold lake --iofail test; mathlib-full tmux session died; full.json never finalized"
  echo "fingerprint=cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0"
  echo "last_built_line=Built MathlibTest.ClickSuggestions.Unfold (489s) [9194/9212]"
  echo "Benchmark_line=absent_in_log"
  echo "dmesg=lean invoked oom-killer; Killed process lean"
  echo "preserved_benchmark_fail_untouched=true"
} > "$ARCH/PRESERVE_RECORD.txt"
echo ARCHIVED_OOM_RUN "$ARCH"

echo ===QUARANTINE===
python3 - <<'PY'
import os, shutil, time, json
from pathlib import Path
from datetime import datetime, timezone

repo = Path("/home/mateo/mathlib4-cursor")
build = repo / ".lake/build"
ts = time.strftime("%Y%m%dT%H%M%S")
qroot = repo / ".cursor-handoff/evidence" / f"quarantine-mathlibtest-{ts}-after-oom"
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
manifest = {
    "timestamp": ts,
    "reason": "Re-quarantine after OOM-killed cold full; keep Mathlib caches; no prebuild",
    "files_moved_count": len(moved),
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "preserved_failed_logs_untouched": True,
}
(qroot / "QUARANTINE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
(qroot / "files-moved.txt").write_text("\n".join(moved) + "\n")
(Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence") / f"quarantine-mathlibtest-{ts}-after-oom-filelist.txt").write_text("\n".join(moved) + "\n")
left = sum(1 for dirpath, _, filenames in os.walk(build) for name in filenames if "MathlibTest" in (Path(dirpath)/name).relative_to(build).as_posix())
print("MOVED", len(moved))
print("LEFT", left)
print("MATHLIB", (repo/".lake/build/lib/lean/Mathlib").exists())
print("QDIR", qroot)
PY

cp -a "$EV/full.json" "$EV/full.json.stale-running-before-lowmem-$(date +%s)" || true

# taskset lake wrapper (does not change workflow.py or source fingerprint)
mkdir -p "$BIN"
REAL_LAKE="$HOME/.elan/bin/lake"
cat > "$BIN/lake" <<EOF
#!/usr/bin/env bash
set -euo pipefail
REAL="$REAL_LAKE"
if command -v taskset >/dev/null 2>&1; then
  exec taskset -c 0,1 "\$REAL" "\$@"
else
  exec "\$REAL" "\$@"
fi
EOF
chmod +x "$BIN/lake"
echo WROTE_LAKE_WRAPPER "$BIN/lake"

# detached lowmem full
cat > /tmp/_step4_full_lowmem.sh <<EOS
#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-cursor
EV="\$PRIMARY/.cursor-handoff/evidence"
export PATH="\$PRIMARY/.cursor-handoff/bin:\$HOME/.elan/bin:\$PATH"
export LEAN_NUM_THREADS=2
cd "\$PRIMARY"
LOG="\$EV/full-official-detached.wrapper.log"
echo "DETACHED_START \$(date -Is) LOWMEM taskset-0,1 LEAN_NUM_THREADS=2" | tee -a "\$LOG"
python3 - <<'PY' | tee -a "\$LOG"
import sys
from pathlib import Path
sys.path.insert(0, "/home/mateo/mathlib4-cursor/.cursor-handoff")
import workflow
print("FINGERPRINT", workflow.fingerprint(Path("/home/mateo/mathlib4-cursor")))
PY
set +e
python3 .cursor-handoff/workflow.py run full >>"\$LOG" 2>&1
ec=\$?
set -e
echo "FULL_WORKFLOW_EXIT \$ec" | tee -a "\$LOG"
echo "DETACHED_END \$(date -Is)" | tee -a "\$LOG"
echo \$ec > "\$EV/full-official-detached.status"
exit \$ec
EOS
chmod +x /tmp/_step4_full_lowmem.sh

tmux start-server
tmux has-session -t keepalive 2>/dev/null || tmux new-session -d -s keepalive "sleep infinity"
tmux has-session -t mathlib-full 2>/dev/null && tmux kill-session -t mathlib-full || true
tmux new-session -d -s mathlib-full "bash /tmp/_step4_full_lowmem.sh; echo EXIT:\$? >> $EV/full-official-detached.wrapper.log; exec sleep infinity"
sleep 10
echo TMUX
tmux ls
echo WRAPPER_TAIL
tail -20 "$EV/full-official-detached.wrapper.log" || true
echo PROCS
ps -eo pid,etime,cmd | grep -E 'workflow.py|lake ' | grep -v grep || true
echo FULL_JSON
cat "$EV/full.json" || true
echo RAM
free -h | head -2
echo AFFINITY
ps -eo pid,cmd | grep '[l]ake' | head -3
LAKEPID=$(pgrep -n -f 'bin/lake' || true)
if [ -n "${LAKEPID:-}" ]; then
  taskset -p "$LAKEPID" || true
fi
