#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-handoff"
git status --porcelain
echo "=== lake env lean --version ==="
lake env lean --version
echo "=== SUCCESS ==="
