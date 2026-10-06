#!/usr/bin/env bash
set -euo pipefail
PRIMARY=/home/mateo/mathlib4-handoff
ADV=/home/mateo/mathlib4-handoff-adv
EV="$PRIMARY/.handoff/evidence"
PRES="$EV/preserved-benchmark-fail"
python3 - <<'PY'
import json, hashlib, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

primary = Path("/home/mateo/mathlib4-handoff")
sys.path.insert(0, str(primary / ".handoff"))
import workflow
fp_now = workflow.fingerprint(primary)
ev = primary / ".handoff/evidence"
pres = ev / "preserved-benchmark-fail"
log = ev / "full-3-1791084123470358418.log"
text = log.read_text(errors="replace")

def sha256(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

env = {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "wsl": {
        "uname": subprocess.check_output(["uname","-a"], text=True).strip(),
        "nproc": subprocess.check_output(["nproc"], text=True).strip(),
        "free_h": subprocess.check_output(["free","-h"], text=True),
        "ulimit": subprocess.check_output(["bash","-lc","ulimit -a"], text=True),
    },
    "toolchain": {
        "lean-toolchain": (primary/"lean-toolchain").read_text().strip(),
        "lake": subprocess.check_output(["bash","-lc","lake --version"], text=True).strip(),
        "lean": subprocess.check_output(["bash","-lc","lean --version"], text=True).strip(),
    },
    "failed_run": {
        "log": str(log),
        "log_sha256": sha256(log),
        "log_bytes": log.stat().st_size,
        "mtime_unix": log.stat().st_mtime,
        "exact_command": ["lake", "--iofail", "test"],
        "cwd": str(primary),
        "invoked_by": "python3 .handoff/workflow.py run full (stage command 3)",
        "quoted_error": "error: MathlibTest/ClickSuggestions/Benchmark.lean:33:0: failed",
        "lake_summary": "Some required targets logged failures: MathlibTest.ClickSuggestions.Benchmark; error: build failed",
        "job_wall_clock_in_log": "Building MathlibTest.ClickSuggestions.Benchmark (131s)",
        "exit_code": "numeric exit not preserved in a stage JSON for run id 1791084123470358418; log proves lake reported build failed (non-zero). Surviving full.json is a later successful run and must not be treated as this failure's marker.",
        "source_fingerprint_at_failure_time": "unknown / not bound to this log in JSON. Current preferred fingerprint is recorded separately as current_primary_fingerprint. Do not backfill.",
        "assertion_site": "MathlibTest/ClickSuggestions/Benchmark.lean:33 run_meta guard (all < 60_000)",
    },
    "current_primary_fingerprint": fp_now,
    "originals_not_deleted": True,
}
(pres/"PRESERVE_RECORD.json").write_text(json.dumps(env, indent=2)+"\n")
print("fingerprint", fp_now)
print("wrote PRESERVE_RECORD.json")
PY
cp -a "$EV/backups/full.json.bak-1791105436" "$PRES/" || true
echo STEP1_RECORD_OK
ls -la "$PRES"
