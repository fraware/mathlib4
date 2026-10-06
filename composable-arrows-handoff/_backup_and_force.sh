#!/usr/bin/env bash
set -euo pipefail
REPO=/home/mateo/mathlib4-handoff
EV="$REPO/.handoff/evidence"
TS=$(date +%s)
mkdir -p "$EV/backups"
cp -a "$EV/full.json" "$EV/backups/full.json.bak-$TS"
cp -a "$EV/focused.json" "$EV/backups/focused.json.bak-$TS"
cp -a "$EV/downstream.json" "$EV/backups/downstream.json.bak-$TS"
echo "Backed up gate markers to $EV/backups/*-$TS"
# Confirm Benchmark olean present (so full MathlibTest need not rebuild it)
BENCH="$REPO/.lake/build/lib/lean/MathlibTest/ClickSuggestions/Benchmark.olean"
if [[ -f "$BENCH" ]]; then
  echo "Benchmark.olean PRESENT ($(wc -c < "$BENCH") bytes)"
else
  echo "WARNING: Benchmark.olean MISSING — full lake test may hit wall-clock flaky failure"
fi
python3 "$REPO/.handoff/_force_iofail_test.py" --mode supplemental-mathlibtest
echo "=== supplemental result json ==="
ls -lt "$EV"/supplemental-iofail-mathlibtest-*.json | head -3
LATEST=$(cat "$EV"/supplemental-iofail-mathlibtest.LATEST)
echo "LATEST log: $LATEST"
wc -c "$EV/$LATEST"
echo "--- log content ---"
cat "$EV/$LATEST"
