#!/usr/bin/env bash
set -euo pipefail
# Sequential isolated rebuild of MathlibTest.ClickSuggestions.Benchmark on original then preferred.
# Does not start if lake/lean already running on either checkout.

PRIMARY=/home/mateo/mathlib4-cursor
ADV=/home/mateo/mathlib4-cursor-adv
DIAG="$PRIMARY/.cursor-handoff/evidence/benchmark-diagnosis"
mkdir -p "$DIAG"

if pgrep -af 'lake |/lean ' | grep -E 'mathlib4-cursor' | grep -v grep >/dev/null; then
  echo "REFUSING: lake/lean already running on a checkout" >&2
  pgrep -af 'lake |/lean ' || true
  exit 2
fi

export PATH="$HOME/.elan/bin:$PATH"

python3 - <<'PY'
from pathlib import Path
import hashlib, os, subprocess, json, time, shutil
from datetime import datetime, timezone

PRIMARY = Path("/home/mateo/mathlib4-cursor")
ADV = Path("/home/mateo/mathlib4-cursor-adv")
DIAG = PRIMARY / ".cursor-handoff/evidence/benchmark-diagnosis"
DIAG.mkdir(parents=True, exist_ok=True)

def env_snapshot():
    return {
        "unix": time.time(),
        "iso": datetime.now(timezone.utc).isoformat(),
        "nproc": subprocess.check_output(["nproc"], text=True).strip(),
        "free": subprocess.check_output(["free", "-h"], text=True),
        "loadavg": Path("/proc/loadavg").read_text().strip(),
    }

def list_benchmark_artifacts(repo: Path):
    roots = [repo / ".lake/build"]
    found = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            s = str(p)
            if "MathlibTest/ClickSuggestions/Benchmark" in s.replace("\\", "/"):
                found.append(p)
            elif p.name.startswith("Benchmark") and "ClickSuggestions" in s:
                found.append(p)
    return found

def wipe_benchmark_artifacts(repo: Path, label: str):
    found = list_benchmark_artifacts(repo)
    listing = DIAG / f"{label}-artifacts-removed.txt"
    listing.write_text("\n".join(str(p) for p in found) + ("\n" if found else ""))
    for p in found:
        p.unlink()
    return [str(p) for p in found]

def basic_sha(repo: Path):
    return hashlib.sha256((repo / "Mathlib/CategoryTheory/ComposableArrows/Basic.lean").read_bytes()).hexdigest()

def run_one(repo: Path, label: str):
    meta = {
        "label": label,
        "repo": str(repo),
        "git_head": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "git_status": subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True),
        "basic_sha256": basic_sha(repo),
        "env_before": env_snapshot(),
    }
    removed = wipe_benchmark_artifacts(repo, label)
    meta["removed_artifacts"] = removed
    remaining = list_benchmark_artifacts(repo)
    meta["remaining_after_wipe"] = [str(p) for p in remaining]
    log = DIAG / f"{label}-lake-build-Benchmark.log"
    cmd = ["lake", "build", "MathlibTest.ClickSuggestions.Benchmark"]
    meta["argv"] = cmd
    t0 = time.time()
    with log.open("wb") as stream:
        proc = subprocess.run(cmd, cwd=repo, stdout=stream, stderr=subprocess.STDOUT)
    t1 = time.time()
    meta["exit_code"] = proc.returncode
    meta["elapsed_sec"] = t1 - t0
    meta["env_after"] = env_snapshot()
    meta["log"] = str(log)
    meta["log_bytes"] = log.stat().st_size
    text = log.read_text(errors="replace")
    meta["log_tail"] = text[-4000:]
    # extract error lines
    errs = [ln for ln in text.splitlines() if "error:" in ln.lower() or "failed" in ln.lower() or "Killed" in ln or "oom" in ln.lower()]
    meta["error_lines"] = errs[-40:]
    (DIAG / f"{label}-result.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"DONE {label} exit={proc.returncode} elapsed={t1-t0:.1f}s log={log}", flush=True)
    return meta

# Confirm original Basic on adv (clean tree)
st = subprocess.check_output(["git", "-C", str(ADV), "status", "--porcelain"], text=True)
if st.strip():
    raise SystemExit(f"ADV checkout not clean original:\n{st}")

print("ENV_START", json.dumps(env_snapshot()), flush=True)
print("START original", flush=True)
orig = run_one(ADV, "original")
print("START preferred", flush=True)
pref = run_one(PRIMARY, "preferred")

summary = {
    "classification_pending_review": True,
    "original_exit": orig["exit_code"],
    "preferred_exit": pref["exit_code"],
    "original_elapsed_sec": orig["elapsed_sec"],
    "preferred_elapsed_sec": pref["elapsed_sec"],
    "original_error_lines": orig["error_lines"],
    "preferred_error_lines": pref["error_lines"],
}
(DIAG / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
print("DIAGNOSIS_COMPLETE", flush=True)
PY
