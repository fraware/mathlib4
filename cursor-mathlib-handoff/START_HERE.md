# Start the ComposableArrows experiment in Cursor

This package creates a local checkout of an existing GitHub repository. No new
branch or file has been published. The preferred and fallback Lean candidates
and their test harnesses remain UNCOMPILED.

## Quick start

Install Git, Python 3.9 or newer, Cursor, and Lean's standard elan/Lake toolchain
manager on your development machine. Use Linux, macOS, or a Linux environment
under Windows/WSL for the commands below. In WSL, keep the checkout in the Linux
filesystem. Official Lean setup instructions: https://lean-lang.org/install/

Extract this ZIP and open a terminal in `cursor-mathlib-handoff`. Run:

```bash
python3 workflow.py setup ../mathlib4-cursor
```

The command clones `https://github.com/fraware/mathlib4.git`, checks out exact
commit `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`, installs this handoff locally,
and adds local push-blocking safeguards. Existing destination directories are
rejected without modification. A failed clone is left for inspection; use a new
destination for a retry.

Open **the `mathlib4-cursor` folder** in Cursor. Paste the contents of
`.cursor-handoff/CURSOR_PROMPT.md` into a local Cursor agent. Do not select a
remote/background workflow that publishes branches or PRs automatically.

## Commands the agent will execute

From the repository root:

```bash
python3 .cursor-handoff/workflow.py run baseline
python3 .cursor-handoff/workflow.py apply preferred
python3 .cursor-handoff/workflow.py run focused
python3 .cursor-handoff/workflow.py run downstream
python3 .cursor-handoff/workflow.py run full
python3 .cursor-handoff/workflow.py export
```

Run one command at a time and inspect its result. Baseline validation downloads
the dependency cache. The pinned toolchain is `leanprover/lean4:v4.35.0-rc3`.
Use the version in `lean-toolchain`; do not upgrade it to resolve an error.
Toolchain/cache downloads need network access and several gigabytes of free disk.
Full builds have substantial resource demands; elapsed time depends on hardware
and cache availability. The runner supplies no invented time estimate.

The setup leaves HEAD detached intentionally. Keep that HEAD fixed while
iterating; local working-tree edits are sufficient. The runner rejects a changed
HEAD. Full gate completion is recorded against a fingerprint of the working tree.
Any subsequent source edit makes earlier gate results stale.

Logs are written incrementally under `.cursor-handoff/evidence/`. Long-running
commands print a log path; inspect that file from a second terminal as needed.
If a command fails or the environment blocks execution, preserve the log, diagnose
the failure, and rerun the relevant stage. Never fabricate passing status files.

## Return to Mateo

Run `export` even for incomplete work. Send:

- `.cursor-handoff/cursor-validation-evidence.zip`
- A short report stating the selected candidate, observed errors and repairs,
  current gate status, and the baseline-discrimination findings.

The export includes the full candidate patch, the new regression file as a patch,
command logs, exact exit codes, and source hashes. Its summary distinguishes
current passes from pending, failed or stale stages. It does not label the work
ready for upstream submission.

## Repository boundary

No pushes to Mathlib, CSLib, or their forks. No remote branch creation, workflow
dispatch, PR operations, comments, or other repository mutations without Mateo's
explicit approval. Local checkout, cache downloads, edits and builds are allowed.

Setup installs a failing `pre-push` hook and an invalid push URL for `origin`.
These are accidental-push safeguards, not an access-control guarantee. Do not
disable them, use `--no-verify`, push to explicit URLs, or write through APIs.
Read operations remain available. Handoff files and AGENTS.md are locally ignored
so they stay out of the mathematical patch.

## Existing manual clones

Prefer the setup command for a reproducible fresh checkout. If you already cloned
the project, keep that checkout untouched and run setup with a new destination.
An existing local mirror is supported without changing the pinned commit:

```bash
python3 workflow.py setup ../mathlib4-cursor --source /absolute/path/to/mirror
```

The package does not install or alter your global editor, Git or toolchain settings.
