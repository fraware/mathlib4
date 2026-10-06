# Upstream candidate FINAL REPORT

Preferred six-file production source validated on community mathlib4
revision `08c3fc3f372a6d35d18190fb26b7be083378dc38`. No remote writes. Does not authorize upstream submission.

This package is a **fresh Lean validation** of the upstream-candidate identity
`13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`. It is not a reuse of the earlier host logs under
`/home/ubuntu/upstream-evidence` (same identity, older attempt). Historical
a3cfff85 evidence remains separate (`recovered-evidence.zip` in the audit kit;
fingerprint `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`).

## Selection
- Candidate: preferred (unchanged; no fallback)
- Upstream base: `08c3fc3f372a6d35d18190fb26b7be083378dc38`
- Toolchain pin: `leanprover/lean4:v4.35.0-rc3`
- Observed Lake: `Lake version 5.0.0-src+470d5ce (Lean version 4.35.0-rc3)`
- Observed Lean: `Lean (version 4.35.0-rc3, x86_64-unknown-linux-gnu, commit 470d5ce1400764999581fd26d5d72b00d990b0f4, Release)`
- Validation identity: `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`
- Patch: `production.patch` sha256 `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026`
- Verifier: `upstream_validation.py` applied to an isolated tree

## Isolated tree
- Checkout: `/home/ubuntu/mathlib-upstream-reviewed-fresh`
- Evidence root: `/home/ubuntu/upstream-evidence-fresh`
- Recipe: `git config remote.origin.pushurl disabled://mateo-approval-required`,
  `core.hooksPath` → `/home/ubuntu/mateo-local-hooks/pre-push`, depth-1 fetch of
  the pinned SHA, `production.patch` only (never `candidate.patch`).
- Kit extract: `/home/ubuntu/mathlib-audit-kit-20261006` (byte-identical to
  `/home/ubuntu/mathlib-audit-kit` for all hashed members; extract added only
  `__pycache__` from runner unit tests).

## Scope and reducer
Six files only. Frozen hashes:
- Basic `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251`
- ReduceMap `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb`
- IntegratedProbe `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e`
Preferred `Precomp.reduceMap` remains constructor-head `whnfHeadPred` (no numeral
reconstruction / inequality-proof synthesis). 13 integrated examples and 15
direct regressions unchanged. No sorry/admit/axioms/kernel bypass/new linter
suppressions in the six files.

## Gates (this run)
| stage | status | exits |
| --- | --- | --- |
| environment | passed | [0, 0, 0] |
| focused | passed | [0, 0] |
| downstream | passed | [0] |
| full | passed | [0, 0, 0, 0] |

All stages bound to `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`. Resource policy: `LEAN_NUM_THREADS=2`,
`LAKE_NUM_THREADS=2`.

### Full detail
- `lake --iofail test` exit 0; MathlibTest coverage expected=419 built_expected=419 missing=[]
- Benchmark line: `✔ [9349/9445] Built MathlibTest.ClickSuggestions.Benchmark (55s)`
- Full wall time ~1314s (dominated by MathlibTest rebuild + lint).
- Label: **fresh MathlibTest rebuild with cached library deps**. Library oleans
  were copied from the same-pin tree `/home/ubuntu/mathlib-upstream-reviewed`
  before gates; `lake exe cache get` then `lake build Mathlib Archive
  Counterexamples Wanted` were cache hits. MathlibTest artifacts were quarantined
  immediately before `lake --iofail test` (`files_moved` 3711 lib + 1257 ir).
  The ZIP includes `quarantine.json` plus the two candidate-module quarantine
  products only (full 378MiB MathlibTest quarantine omitted for review size).

## Failures and repairs
None on this run. Preferred source was not edited.

## Limitations
- Finite tests do not prove universal reducer correctness.
- Publication / PR / remote cleanup require Mateo's explicit approval.
- Credential-pattern scan covers known URL-password and GitHub token shapes only.
- Kit `upstream-environment-attempt.json` records a prior host without Lake; it
  does not describe this execution.

## Package contents
Sanitized gate logs and four stage markers, `production.patch`,
`upstream-source.json`, six preferred source files under `evidence/source/`.
`MEMBER_HASHES.txt` regenerated from final archive members; outer ZIP checksum
is external only.

---

## Post-publication addendum (repository copy only)

This section is **not** present in `upstream-validation-evidence.zip`. The
audited archive copy of this file (member sha256
`09e50c3b48696d4b3f6fa19095d2b6f6cd9a24a2b96ba315ed2bdc4e312fede5`) ends at
Package contents. The difference is intentional: rebuilding the ZIP would
change outer sha256 `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c`.
See also `POST_PUBLICATION_ADDENDUM.md` (outside the ZIP).

### "No remote writes" (validation phase)

The opening "No remote writes" referred to the **validation phase**: an isolated
checkout of community mathlib4 revision
`08c3fc3f372a6d35d18190fb26b7be083378dc38` with no writes to community Mathlib
or CSLib. After gates passed, evidence was published to the evidence-host
repository `fraware/mathlib4` at commit
`bba88b87bbda4b7bf35cf52d54d5bb5919707a37` (draft PR #3 on
`research/composable-arrows-reduce-map-evidence`). Evidence-host CI does not
validate the production patch. Publication of preferred source to community
mathlib4 still requires Mateo's explicit approval and is not this branch.

### Credential owner action (older archive)

The **new** package credential-pattern scan was clean. Redaction of this ZIP
does not resolve exposure in an **older** archive. Expiry or revocation of that
credential remains the credential owner's responsibility. Automated follow-up
cannot revoke it. Mateo must rotate or revoke the leaked token and treat any
remote cleanup as a separately approved action. The secret is not restated here.
