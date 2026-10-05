# Packaging checks — 2026-10-01

The Python/Git handoff workflow was exercised locally against the exact repository
baseline using an existing local clone as its read-only source.

Passed checks:

- Python syntax, including Python 3.9 syntax compatibility.
- Fresh checkout at the pinned commit with clean source state.
- Existing destination refusal without overwrite.
- Candidate application refused before baseline completion.
- Installed pre-push hook returns failure; origin push URL is disabled.
- Preferred patch application and independent fallback patch applicability.
- Candidate-specific counts: 15 examples in each test template.
- Full validation refused before prerequisite stages.
- Source edits invalidate previous focused, downstream and full results.
- A failed rerun replaces the old success marker and preserves exit code 7.
- Evidence export includes the untracked regression file and recreates candidate
  files byte-for-byte when applied to the baseline.

The workflow state-machine tests used a Lake TEST DOUBLE, with 12 orchestration
cases. These tests executed zero Lean compilations. No simulated pass markers or
simulated compiler logs are included in this package or installed into the user's
checkout. Actual baseline and candidate validation must run on the user's machine.

No pushes, workflow dispatches or remote repository writes were performed.
