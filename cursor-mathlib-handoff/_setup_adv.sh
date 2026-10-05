#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
DEST="$HOME/mathlib4-cursor-adv"
if [ -e "$DEST" ]; then
  echo "DEST_EXISTS: $DEST"
  ls -ld "$DEST"
  if [ -d "$DEST/.git" ]; then
    git -C "$DEST" rev-parse HEAD
    git -C "$DEST" status -sb
  fi
  exit 0
fi
cd /mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff
python3 workflow.py setup "$DEST" --source "$HOME/mathlib4-cursor"
echo SETUP_OK
git -C "$DEST" rev-parse HEAD
cat "$DEST/lean-toolchain"
