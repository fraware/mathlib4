#!/usr/bin/env bash
set +e
echo "HOME=$HOME"
echo "=== DEST ==="
ls -ld "$HOME/mathlib4-handoff" "$HOME/mathlib4-handoff-2" 2>&1
echo "=== GIT ==="
if [ -d "$HOME/mathlib4-handoff/.git" ]; then
  git -C "$HOME/mathlib4-handoff" rev-parse HEAD
  git -C "$HOME/mathlib4-handoff" status -sb
  echo "=== TOOLCHAIN ==="
  cat "$HOME/mathlib4-handoff/lean-toolchain"
  echo "=== HANDOFF ==="
  ls -la "$HOME/mathlib4-handoff/.handoff" 2>&1 | head -40
  echo "=== EVIDENCE ==="
  EV="$HOME/mathlib4-handoff/.handoff/evidence"
  if [ -d "$EV" ]; then
    ls -la "$EV"
    echo "=== SELECTION ==="
    cat "$EV/selection.json" 2>&1
    echo "=== JSON/STATUS ==="
    find "$EV" -maxdepth 2 -type f | sort
  else
    echo "NO_EVIDENCE_DIR"
  fi
  echo "=== FINGERPRINT/MARKERS ==="
  find "$HOME/mathlib4-handoff/.handoff" -name '*.json' -o -name '*pass*' -o -name '*status*' 2>/dev/null | sort
else
  echo "NO_GIT_OR_MISSING"
fi
echo "=== PROCS ==="
ps -eo pid,etime,cmd 2>/dev/null | grep -E 'lake|lean|workflow|python3' | grep -v grep || echo NO_MATCHING_PROCS
echo "=== TOOLS ==="
command -v git; command -v python3; command -v elan; command -v lake
git --version
python3 --version
elan --version 2>&1
echo "=== DISK ==="
df -h "$HOME" | tail -1
echo "=== DEST FILESYSTEM ==="
df -T "$HOME/mathlib4-handoff" 2>&1 | tail -1
echo "=== IS_LINUX_FS ==="
findmnt -T "$HOME/mathlib4-handoff" 2>&1 | head -5
