#!/usr/bin/env bash
set -euo pipefail
EV=/home/mateo/mathlib4-cursor/.cursor-handoff/evidence
echo "===== full-3-1791084123470358418.log ====="
cat "$EV/full-3-1791084123470358418.log"
echo
echo "===== benchmark-repro.log ====="
cat "$EV/benchmark-repro.log"
echo
echo "===== benchmark-rebuild.log ====="
cat "$EV/benchmark-rebuild.log"
echo
echo "===== full-3-1791080146866188221.log tail ====="
tail -c 8000 "$EV/full-3-1791080146866188221.log"
echo
echo "===== full-rerun-clean-note ====="
cat "$EV/full-rerun-clean-note-1791105555.json"
echo
echo "===== SUMMARY ====="
cat "$EV/SUMMARY.json"
echo
echo "===== FINAL_REPORT ====="
cat "$EV/FINAL_REPORT.md"
echo
echo "===== ulimit ====="
ulimit -a
echo
echo "===== git fingerprint primary ====="
cd /home/mateo/mathlib4-cursor
git rev-parse HEAD
git status --porcelain
echo "===== hashes ====="
sha256sum Mathlib/CategoryTheory/ComposableArrows/Basic.lean MathlibTest/ComposableArrowsReduceMap.lean 2>/dev/null || true
echo "===== lake/lean ====="
cat lean-toolchain
~/.elan/bin/lake --version || lake --version
~/.elan/bin/lean --version || lean --version
