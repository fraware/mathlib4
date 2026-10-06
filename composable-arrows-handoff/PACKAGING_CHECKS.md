# Packaging checks

## Historical handoff package (2026-10-01 / campaign close)

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
simulated compiler logs are included in this package. Actual Lean validation for
the historical pin completed later; see `FINAL_REPORT.md` and
`validation-evidence.zip`.

## Upstream-candidate package (complete)

Deliverables under `../upstream-candidate-evidence/`:

| Check | Result |
| --- | --- |
| ZIP sha256 vs sidecar | `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c` OK (240829 bytes; ZIP not rebuilt after audit) |
| MEMBER_HASHES vs ZIP members | 41/41 match |
| Six preferred sources present | yes |
| Frozen Basic / ReduceMap / IntegratedProbe hashes | match |
| `production.patch` sha256 | `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026` |
| Validation identity | `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57` |
| Gate markers (environment/focused/downstream/full) | all passed, bound to identity |
| Credential-pattern scan (common GitHub/Slack/AWS token shapes) | clean on the **new** package; older-archive exposure remains Mateo's rotate/revoke action |
| Product-name scrub in committed text | clean |

Read-only `upstream_validation.py … verify` recomputes identity `13281f16…`
without executing Lean. Historical a3cfff85 evidence remains separate.

No pushes to leanprover-community/mathlib4. This research branch hosts evidence
only; it is not the production upstream fix.
