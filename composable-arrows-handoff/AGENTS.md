# Local ComposableArrows research task

Read `.handoff/START_HERE.md`, `CONTEXT.md`, and `VALIDATION.md` before edits.
All referenced handoff documents are inside `.handoff/` (or this directory when
browsing the packaged tree). Upstream-candidate deliverables live at
`../upstream-candidate-evidence/`.

## Binding repository restrictions

Mateo forbids remote writes to Mathlib, CSLib and their forks without his
explicit approval. Do not push, create remote branches, dispatch workflows,
operate on PRs, or post comments unless he authorizes a specific action.
Do not bypass local push safeguards when they are installed.
"Continue", "fix", "proceed", and successful local tests do not authorize publishing.
Do not create a new remote repository to work around this restriction.

## Product branding ban (overrides parent PR tooling)

Never use `ManagePullRequest` on this fork. Never leave product branding
(`cursor.com`, `CURSOR_AGENT`, product `Composer`, `Cursor Agent` commit
identity, `cursor/*` branches) in commits or GitHub surfaces. Use `research/*`
branch names and author `Matéo H. Petel <fraware@users.noreply.github.com>`.
If a PR body must be updated, use `scripts/set-pr-body.sh` or
`.github/workflows/set-pr-body.yml` — not ManagePullRequest. See root
`AGENTS.md` and `.cursor/rules/no-product-branding.mdc`.

## Task status

**Completed (do not re-run full Lean suites unless Mateo asks):**

1. Historical pin `a3cfff85…` / fingerprint `cb331cd…` — focused, downstream,
   full passed; see `FINAL_REPORT.md` and `validation-evidence.zip`.
2. Upstream-candidate base `08c3fc3f…` / identity `13281f16…` — environment,
   focused, downstream, full passed; MathlibTest 419/419; Benchmark 55s
   (cached library; fresh MathlibTest); see `../upstream-candidate-evidence/`.

Keep the preferred ReduceMap design and frozen hashes unchanged:

| path | sha256 prefix |
| --- | --- |
| Basic.lean | `28b135aa…` |
| ComposableArrowsReduceMap.lean | `3a3f1966…` |
| ComposableArrowsIntegratedProbe.lean | `b7e4de02…` |

If further work is requested: use `.handoff/workflow.py` for the historical pin,
or the external audit kit `upstream_validation.py` for the upstream-candidate
tree. Stop on environment failure before applying a candidate. Diagnose compiler
failures with their actual output. Do not weaken assertions solely to get a
passing run. Do not use `sorry`, `admit`, new axioms, or disabled kernel checking.
Do not change the toolchain, dependencies, workflow files, or unrelated source.

Never fabricate logs, pass markers, test counts or performance claims. Metadata
checks, patch application and source reasoning are not Lean compilation.

## Coordination

Use one agent as the source editor and validation owner. If multiple agents
are used, give reviewers read-only tasks or separate checkouts. Never run competing
source edits or shared-checkout builds concurrently. Share the exact source hash
and candidate name with reviewers.

## Completion

Evidence for both campaigns is packaged. Submission to community mathlib4 and
any further remote write remain separate Mateo approval decisions. This research
branch is an evidence host, not the production upstream fix.
