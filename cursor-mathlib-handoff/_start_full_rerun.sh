#!/usr/bin/env bash
set -euo pipefail
LOG=/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/full-rerun-wrapper.log
exec > >(tee "$LOG") 2>&1
echo "START:$(date -Iseconds)"
python3 /home/mateo/mathlib4-cursor/.cursor-handoff/_rerun_full_clean.py
code=$?
echo "EXIT:${code}"
exit "${code}"
