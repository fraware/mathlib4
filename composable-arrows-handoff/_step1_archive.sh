#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-handoff
EV="$PRIMARY/.handoff/evidence"
PRES="$EV/preserved-benchmark-fail"
mkdir -p "$PRES"

# Copy originals without overwriting source files
cp -a "$EV/full-3-1791084123470358418.log" "$PRES/"
cp -a "$EV/benchmark-repro.log" "$PRES/" 2>/dev/null || true
cp -a "$EV/benchmark-rebuild.log" "$PRES/" 2>/dev/null || true
# related nearby full logs from same campaign
for f in \
  full-1-1791084101123146403.log \
  full-2-1791084104331252821.log \
  full-3-1791080146866188221.log \
  full-1-1791080115511383993.log \
  full-2-1791080134219317544.log \
  full-3-1791039579347445388.log \
  full-3-interrupted-before-rerun.log \
  full-3-1791036665172218338.log
do
  if [ -f "$EV/$f" ]; then cp -a "$EV/$f" "$PRES/"; fi
done

# Extract Benchmark.lean:33 context from the key log
python3 - <<'PY'
from pathlib import Path
p = Path("/home/mateo/mathlib4-handoff/.handoff/evidence/full-3-1791084123470358418.log")
text = p.read_text(errors="replace")
out = Path("/home/mateo/mathlib4-handoff/.handoff/evidence/preserved-benchmark-fail/extracted-error.txt")
lines = text.splitlines()
keep = []
for i,l in enumerate(lines):
    if "Benchmark" in l or "error:" in l.lower() or "failed" in l.lower() or "timeout" in l.lower() or "60" in l or "OOM" in l or "Killed" in l or "signal" in l.lower():
        start=max(0,i-2); end=min(len(lines), i+8)
        keep.append((start,end))
# merge ranges
merged=[]
for s,e in keep:
    if merged and s <= merged[-1][1]:
        merged[-1]=(merged[-1][0], max(merged[-1][1], e))
    else:
        merged.append((s,e))
chunks=[]
for s,e in merged:
    chunks.append("\n".join(f"{n+1:5d}| {lines[n]}" for n in range(s,e)))
out.write_text("\n\n==== snippet ====\n".join(chunks) if chunks else "NO MATCHES\n")
print("extracted", out, "bytes", out.stat().st_size, "snippets", len(chunks))
print("log bytes", p.stat().st_size, "lines", len(lines))
print("--- last 30 lines ---")
print("\n".join(lines[-30:]))
PY

echo "===== Benchmark.lean around 33 ====="
sed -n '1,80p' "$PRIMARY/MathlibTest/ClickSuggestions/Benchmark.lean"

echo "===== preserved listing ====="
ls -la "$PRES"
echo "===== orig still exists ====="
ls -l "$EV/full-3-1791084123470358418.log"
