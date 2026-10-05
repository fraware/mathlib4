# Local ComposableArrows research task

Read `.cursor-handoff/START_HERE.md`, `CONTEXT.md`, and `VALIDATION.md` before edits.
All referenced documents are inside `.cursor-handoff/`.

## Binding repository restrictions

Mateo explicitly forbids remote writes to Mathlib, CSLib and their forks without
his explicit approval. Do not push, create remote branches, dispatch workflows,
operate on PRs, or post comments. Do not bypass the local push safeguards.
"Continue", "fix", "proceed", and successful local tests do not authorize publishing.
Do not create a new remote repository to work around this restriction.

## Task

Validate the preferred definitional reducer on exact baseline
`a3cfff85f9dfe0b1c6b6e92899febc338687fcc3` with Lean `v4.35.0-rc3`.
Keep the existing 13 integrated examples unchanged. Add and repair the supplied
candidate-specific regression file as needed, with reasons for every change.
Classify test harness errors separately from reducer failures.

Use `.cursor-handoff/workflow.py` for setup gates and evidence capture. Stop on
environment failure before applying a candidate. Diagnose compiler failures with
their actual output. Do not weaken assertions solely to get a passing run.
Do not use `sorry`, `admit`, new axioms, or disabled kernel checking to pass tests.
Do not change the toolchain, dependencies, workflow files, or unrelated source.

Keep HEAD at the baseline. Use local working-tree edits and export the final diff.
Never fabricate logs, pass markers, test counts or performance claims. Metadata
checks, patch application and source reasoning are not Lean compilation.

## Coordination

Use one agent as the source editor and validation owner. If multiple Cursor agents
are used, give reviewers read-only tasks or separate checkouts. Never run competing
source edits or shared-checkout builds concurrently. Share the exact source hash
and candidate name with reviewers.

## Completion

The exact final source must pass focused regressions, downstream builds, full
builds, test execution, and lint. Separately report the original/candidate
adversarial comparison. Export evidence and stop for Mateo's review; submission
and any remote write remain separate approval decisions.
