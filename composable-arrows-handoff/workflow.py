#!/usr/bin/env python3
"""Local-only setup and evidence collection for the pinned ComposableArrows experiment.

Python 3.9+, Git and a working pinned Lean/Lake toolchain are required.
This runner never installs software, commits, pushes or dispatches remote jobs.
Evidence records exact command exit codes and a source fingerprint for each stage.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

BASE = "a3cfff85f9dfe0b1c6b6e92899febc338687fcc3"
TOOLCHAIN = "leanprover/lean4:v4.35.0-rc3"
REMOTE = "https://github.com/fraware/mathlib4.git"
BASIC = "Mathlib/CategoryTheory/ComposableArrows/Basic.lean"
TEST = "MathlibTest/ComposableArrowsReduceMap.lean"
INTEGRATED = "MathlibTest/ComposableArrowsIntegratedProbe.lean"
BUNDLE = Path(__file__).resolve().parent


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def check_repo(repo):
    require(git(repo, "rev-parse", "HEAD").decode().strip() == BASE,
            "HEAD differs from the pinned baseline; use a fresh setup checkout.")
    require((repo / "lean-toolchain").read_text().strip() == TOOLCHAIN,
            "Toolchain differs from the pinned version.")


def fingerprint(repo):
    """Hash tracked changes plus every nonignored untracked file, without staging."""
    digest = hashlib.sha256(BASE.encode())
    digest.update(git(repo, "diff", "--binary", "HEAD", "--"))
    for raw in sorted(git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")):
        if raw:
            digest.update(raw + b"\0")
            digest.update((repo / os.fsdecode(raw)).read_bytes())
    return digest.hexdigest()


def setup(destination, source):
    repo = Path(destination).expanduser().resolve()
    require(not repo.exists(), "Destination already exists. Choose a new directory; nothing overwritten.")
    repo.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--no-checkout", source, str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "--detach", BASE], check=True)
    check_repo(repo)
    require(not (repo / "AGENTS.md").exists(), "Existing AGENTS.md needs manual integration.")
    target = repo / ".handoff"
    shutil.copytree(BUNDLE, target, ignore=shutil.ignore_patterns("__pycache__", "evidence", "*.zip"))
    shutil.copyfile(target / "AGENTS.md", repo / "AGENTS.md")
    git_dir = Path(git(repo, "rev-parse", "--absolute-git-dir").decode().strip())
    with (git_dir / "info" / "exclude").open("a", encoding="utf-8") as stream:
        stream.write("\n# Local handoff, deliberately excluded from submissions.\n/AGENTS.md\n/.handoff/\n")
    hooks = git_dir / "mateo-local-hooks"
    hooks.mkdir()
    hook = hooks / "pre-push"
    hook.write_text('#!/bin/sh\nprintf "%s\\n" "Push blocked: explicit Mateo approval required." >&2\nexit 1\n')
    hook.chmod(0o755)
    subprocess.run(["git", "-C", str(repo), "config", "core.hooksPath", str(hooks)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "remote.origin.pushurl",
                    "disabled://mateo-approval-required"], check=True)
    require(not git(repo, "status", "--porcelain"), "Setup unexpectedly changed tracked source.")
    print(f"Ready: {repo}\nOpen that folder in your editor and read .handoff/START_HERE.md")


def require_pass(evidence, stage, source_hash):
    marker = evidence / f"{stage}.json"
    require(marker.exists(), f"Run the {stage} stage first.")
    record = json.loads(marker.read_text())
    require(record.get("status") == "passed" and record.get("source_sha256") == source_hash,
            f"The {stage} stage has not passed for the current source. Rerun it.")


def run_stage(repo, evidence, stage):
    source_hash = fingerprint(repo)
    if stage == "baseline":
        require(not git(repo, "status", "--porcelain"), "Baseline stage requires a clean checkout.")
    else:
        require((BUNDLE / "selection.json").exists(), "Apply a candidate first.")
        if stage in ("downstream", "full"):
            require_pass(evidence, "focused", source_hash)
        if stage == "full":
            require_pass(evidence, "downstream", source_hash)
    downstream = [
        "Mathlib.Algebra.Homology.ExactSequence",
        "Mathlib.Algebra.Homology.HomologySequence",
        "Mathlib.Algebra.Homology.HomotopyCategory.ShortExact",
        "Mathlib.CategoryTheory.ComposableArrows.Four",
        "Mathlib.Algebra.Homology.ExactSequenceFour",
        "Mathlib.CategoryTheory.Abelian.DiagramLemmas.Four",
        "Mathlib.CategoryTheory.Sites.SheafCohomology.MayerVietoris",
        "Mathlib.Topology.Sheaves.MayerVietoris",
    ]
    stages = {
        "baseline": [["lake", "--version"], ["lake", "env", "lean", "--version"],
                     ["lake", "exe", "cache", "get"],
                     ["lake", "build", "Mathlib.CategoryTheory.ComposableArrows.Basic",
                      "MathlibTest.ComposableArrowsIntegratedProbe"]],
        "focused": [["lake", "build", "Mathlib.CategoryTheory.ComposableArrows.Basic"],
                    ["lake", "build", "MathlibTest.ComposableArrowsReduceMap",
                     "MathlibTest.ComposableArrowsIntegratedProbe"]],
        "downstream": [["lake", "build", *downstream]],
        "full": [["lake", "exe", "mk_all", "--check"],
                 ["lake", "build", "Mathlib", "Archive", "Counterexamples", "Wanted"],
                 ["lake", "--iofail", "test"], ["lake", "lint", "--", "--trace"]],
    }
    record = {"stage": stage, "status": "running", "base": BASE,
              "source_sha256": source_hash, "commands": [], "started_unix": time.time()}
    marker = evidence / f"{stage}.json"
    # Invalidate an older successful marker before starting a new attempt.
    write_json(marker, record)
    try:
        subprocess.run(["git", "-C", str(repo), "diff", "--check"], check=True)
        for number, command in enumerate(stages[stage], 1):
            logfile = evidence / f"{stage}-{number}-{time.time_ns()}.log"
            print(f"Running {command}; log: {logfile}", flush=True)
            command_record = {"argv": command, "exit_code": None, "log": logfile.name}
            record["commands"].append(command_record)
            write_json(marker, record)
            with logfile.open("wb") as stream:
                result = subprocess.run(command, cwd=repo, stdout=stream, stderr=subprocess.STDOUT,
                                        timeout=60 if command[-1] == "--version" else None)
            command_record["exit_code"] = result.returncode
            write_json(marker, record)
            require(result.returncode == 0, f"Command failed with exit {result.returncode}. Read {logfile}")
        require(fingerprint(repo) == source_hash, "Source changed during validation; rerun this stage.")
        record["status"] = "passed"
    except BaseException as error:
        record["status"] = "failed"
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        record["finished_unix"] = time.time()
        write_json(marker, record)
    print(f"PASS: {stage} for source {source_hash}")


def apply_candidate(repo, evidence, candidate):
    require(not git(repo, "status", "--porcelain"), "Candidate application requires a clean checkout.")
    require_pass(evidence, "baseline", fingerprint(repo))
    require(not (repo / TEST).exists(), "Regression file already exists; refusing to overwrite.")
    patch = BUNDLE / "patches" / f"{candidate}.patch"
    subprocess.run(["git", "-C", str(repo), "apply", "--check", str(patch)], check=True)
    subprocess.run(["git", "-C", str(repo), "apply", str(patch)], check=True)
    shutil.copyfile(BUNDLE / "templates" / f"{candidate}-regression.lean", repo / TEST)
    write_json(BUNDLE / "selection.json", {"candidate": candidate, "base": BASE,
                                          "initial_source_sha256": fingerprint(repo)})
    print(f"Applied {candidate} locally. Run the focused stage next.")


def export_evidence(repo, evidence):
    patch = git(repo, "diff", "--binary", "HEAD", "--")
    new_paths = git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    require(all(not p or os.fsdecode(p) == TEST for p in new_paths),
            "Unexpected untracked files: review them before exporting evidence.")
    if os.fsencode(TEST) in new_paths:
        result = subprocess.run(["git", "diff", "--no-index", "--binary", "--", "/dev/null", TEST],
                                cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        require(result.returncode == 1, "Could not export the new regression file.")
        patch += result.stdout
    (evidence / "candidate.patch").write_bytes(patch)
    (evidence / "git-status.txt").write_bytes(git(repo, "status", "--short"))
    current = fingerprint(repo)
    gate_status = {}
    for stage in ("focused", "downstream", "full"):
        try:
            require_pass(evidence, stage, current)
            gate_status[stage] = "passed-for-current-source"
        except RuntimeError:
            gate_status[stage] = "pending-failed-or-stale"
    adv_paths = sorted(
        str(path.relative_to(evidence))
        for path in evidence.iterdir()
        if path.is_file() and (
            path.name.startswith(("advsuite_", "adv_", "adversarial", "spotcheck", "benchmark-diagnosis"))
            or path.name in ("advsuite_matrix.json", "adversarial-SUMMARY.md", "CLASSIFICATION.json")
        )
    )
    discrimination = {
        "status": "completed-artifacts-present" if adv_paths else "missing",
        "evidence_paths": adv_paths,
        "note": "Finite original-vs-preferred probes; not a universal reducer theorem.",
    }
    write_json(evidence / "SUMMARY.json", {
        "base": BASE, "toolchain": TOOLCHAIN, "source_sha256": current, "gates": gate_status,
        "patch_sha256": hashlib.sha256(patch).hexdigest(),
        "files": {p: hashlib.sha256((repo / p).read_bytes()).hexdigest()
                  for p in (BASIC, TEST, INTEGRATED) if (repo / p).exists()},
        "scope": "Local command evidence including adversarial discrimination artifacts when present.",
        "discrimination": discrimination,
        "candidate": json.loads((BUNDLE / "selection.json").read_text()).get("candidate")
            if (BUNDLE / "selection.json").exists() else None,
    })
    archive = BUNDLE / "validation-evidence.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(evidence.iterdir()):
            if path.is_file():
                bundle.write(path, "evidence/" + path.name)
        if (BUNDLE / "selection.json").exists():
            bundle.write(BUNDLE / "selection.json", "selection.json")
    print(f"Evidence exported: {archive}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    setup_parser = sub.add_parser("setup")
    setup_parser.add_argument("destination")
    setup_parser.add_argument("--source", default=REMOTE,
                              help="Read-only clone URL or local mirror; exact baseline is still enforced.")
    run_parser = sub.add_parser("run")
    run_parser.add_argument("stage", choices=["baseline", "focused", "downstream", "full"])
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("candidate", choices=["preferred", "fallback"])
    sub.add_parser("export")
    args = parser.parse_args()
    if args.action == "setup":
        setup(args.destination, args.source)
        return
    repo = BUNDLE.parent
    require(BUNDLE.name == ".handoff", "Run the copy installed inside your setup checkout.")
    check_repo(repo)
    evidence = BUNDLE / "evidence"
    evidence.mkdir(exist_ok=True)
    if args.action == "run":
        run_stage(repo, evidence, args.stage)
    elif args.action == "apply":
        apply_candidate(repo, evidence, args.candidate)
    else:
        export_evidence(repo, evidence)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
