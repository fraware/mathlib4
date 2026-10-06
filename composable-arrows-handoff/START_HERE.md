# ComposableArrows handoff — start here

This directory packages the **historical** local validation campaign on fork pin
`a3cfff85f9dfe0b1c6b6e92899febc338687fcc3` (Lean `v4.35.0-rc3`). Preferred-source
hashes and gate results for that campaign are recorded in `FINAL_REPORT.md` and
`validation-evidence.zip`.

## Upstream-candidate validation (complete)

A separate, completed validation of the preferred six-file production source on
community mathlib4 base `08c3fc3f372a6d35d18190fb26b7be083378dc38` lives at
repository root in `upstream-candidate-evidence/`:

| Item | Value |
| --- | --- |
| Validation identity | `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57` |
| `production.patch` sha256 | `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026` |
| ZIP | `upstream-validation-evidence.zip` |
| ZIP sha256 | `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c` (240829 bytes) |
| Gates | environment / focused / downstream / full — all passed |
| MathlibTest | 419/419; Benchmark 55s (cached library artifacts; fresh MathlibTest rebuild) |

Preferred frozen file hashes (both campaigns):

| path | sha256 |
| --- | --- |
| `Mathlib/CategoryTheory/ComposableArrows/Basic.lean` | `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251` |
| `MathlibTest/ComposableArrowsReduceMap.lean` | `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb` |
| `MathlibTest/ComposableArrowsIntegratedProbe.lean` | `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e` |

Do not treat this research branch / PR as the production upstream fix; it is an
evidence host. Historical `a3cfff85…` artifacts and the upstream-candidate package
remain separate.

## Historical campaign quick start (a3cfff85 pin)

Install Git, Python 3.9 or newer, a local IDE, and Lean's standard elan/Lake
toolchain manager. Use Linux, macOS, or a Linux environment under Windows/WSL.
In WSL, keep the checkout in the Linux filesystem.
Official Lean setup: https://lean-lang.org/install/

From this directory:

```bash
python3 workflow.py setup ../mathlib4-handoff
```

The command clones `https://github.com/fraware/mathlib4.git`, checks out exact
commit `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`, installs this handoff locally,
and adds local push-blocking safeguards. Existing destination directories are
rejected without modification.

Open the `mathlib4-handoff` folder in the IDE. Paste `.handoff/HANDOFF_PROMPT.md`
into a local agent for review. Prefer local work; do not select a remote workflow
that publishes branches or PRs automatically unless Mateo explicitly authorizes it.

## Historical runner commands

From the repository root of a setup checkout:

```bash
python3 .handoff/workflow.py run baseline
python3 .handoff/workflow.py apply preferred
python3 .handoff/workflow.py run focused
python3 .handoff/workflow.py run downstream
python3 .handoff/workflow.py run full
python3 .handoff/workflow.py export
```

Pinned toolchain: `leanprover/lean4:v4.35.0-rc3`. Use the version in
`lean-toolchain`; do not upgrade it to resolve an error. Never fabricate passing
status files.

## Return package (historical)

For the a3cfff85 campaign, send:

- `.handoff/validation-evidence.zip` (also mirrored here)
- A short report: selected candidate, errors/repairs, gate status, baseline
  discrimination findings

Export distinguishes passes from pending, failed, or stale stages. It does not
label the work ready for upstream submission.

## Repository boundary

No pushes to Mathlib, CSLib, or their forks without Mateo's explicit approval.
Setup may install a failing `pre-push` hook and an invalid push URL for `origin`
as accidental-push safeguards—not an access-control guarantee.

## Existing manual clones

```bash
python3 workflow.py setup ../mathlib4-handoff --source /absolute/path/to/mirror
```

The package does not install or alter global IDE, Git, or toolchain settings.
