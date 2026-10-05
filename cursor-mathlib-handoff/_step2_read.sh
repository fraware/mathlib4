#!/usr/bin/env bash
set -euo pipefail
D=/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/benchmark-diagnosis
echo "==== comparison ===="
cat "$D/comparison.json"
echo
echo "==== original log grep ===="
grep -E 'error:|Benchmark|Build completed|failed|Killed|✔|✖' "$D/original-lake-build-Benchmark.log" | tail -40
echo
echo "==== preferred log grep ===="
grep -E 'error:|Benchmark|Build completed|failed|Killed|✔|✖' "$D/preferred-lake-build-Benchmark.log" | tail -40
echo
echo "==== original result keys ===="
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/benchmark-diagnosis/original-result.json").read_text())
print("exit", d["exit_code"], "elapsed", d["elapsed_sec"], "removed", len(d["removed_artifacts"]))
print("basic", d["basic_sha256"])
print("status", d["git_status"][:200])
print("errors", d["error_lines"])
print("env_before load", d["env_before"]["loadavg"])
print("env_after free", d["env_after"]["free"])
d=json.loads(Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/benchmark-diagnosis/preferred-result.json").read_text())
print("PREF exit", d["exit_code"], "elapsed", d["elapsed_sec"], "removed", len(d["removed_artifacts"]))
print("basic", d["basic_sha256"])
print("errors", d["error_lines"])
print("env_before load", d["env_before"]["loadavg"])
print("remaining after wipe", d["remaining_after_wipe"])
PY
