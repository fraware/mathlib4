# ComposableArrows: Fin.reduceFinMk-compatible Precomp.reduceMap

> **fraware review hosting only.** This draft PR presents the frozen six-file source tip for auditor/reviewer download of the submission text ZIP. It is **not** a community/upstream mathlib4 submission. Upstream submission still requires Mateo’s explicit later approval.

## Submission text ZIP (auditor download)

Frozen archive (do not rebuild):

| Item | Value |
| --- | --- |
| File | `source-submission-prep.zip` |
| sha256 | `f100cfeb6ba8f63d6513e7ecbe8120af3b79c46327a3aa81766b184f9d710289` |
| Contents | `FINAL_SOURCE.diff`, `PR_DRAFT.md`, `REVIEW_NOTES.md` |

**Download (evidence branch):**

- https://github.com/fraware/mathlib4/raw/research/composable-arrows-reduce-map-evidence/source-submission-prep/source-submission-prep.zip
- Directory: https://github.com/fraware/mathlib4/tree/research/composable-arrows-reduce-map-evidence/source-submission-prep
- Hosting note: https://github.com/fraware/mathlib4/blob/research/composable-arrows-reduce-map-evidence/source-submission-prep/HOSTING.md

GitHub Release asset (same ZIP bytes):

- https://github.com/fraware/mathlib4/releases/tag/source-submission-prep-47e94148
- https://github.com/fraware/mathlib4/releases/download/source-submission-prep-47e94148/source-submission-prep.zip

## Real base pin

GitHub may show `master` (or another branch) as the PR base UI field. The **real review base** for this one-commit, six-file patch is:

`08c3fc3f372a6d35d18190fb26b7be083378dc38`

Compare: https://github.com/fraware/mathlib4/compare/08c3fc3f372a6d35d18190fb26b7be083378dc38...47e94148ec270467ea9cbccf5c56d1d9a6478a75

Source tip (frozen; do not amend/rebase): `47e94148ec270467ea9cbccf5c56d1d9a6478a75` on `research/composable-arrows-reduce-map-source`.

## Summary

This PR restores compatibility between `Fin.reduceFinMk` and `ComposableArrows.Precomp.map` reduction (leanprover-community/mathlib4#27382). It removes the file-wide `Fin.reduceFinMk` disable and the scattered `[-Fin.reduceFinMk]` workarounds, and adds a preferred `dsimproc` that definitionally reduces `Precomp.map` applications when both indices expose `Fin.mk` constructors.

## Design

`Precomp.reduceMap`:

- Gates on both indices exposing `Fin.mk` (via constructor-head `whnfHeadPred`).
- Then reduces the **original** `Precomp.map` application with the same transparency, so the supplied inequality proof, category instance, and universes are preserved.
- Does **not** reconstruct numerals or synthesize fresh inequality proofs (no `getFinValue?` / `toExpr` / `mkDecideProof` path).

Actual numeral semantics are preserved: custom `OfNat` / `LE` instances continue to mean what the terms definitionally mean, rather than being replaced by standard decimal reconstructions.

## Additional source

- Explicit `hom_inv_id` / `inv_hom_id` fields on `isoMk₃` and `isoMk₄`, delegated to the corresponding `isoMkSucc` constructions (inverse laws).
- Downstream homology call sites drop `[-Fin.reduceFinMk]` once the reducer is in place.
- Direct regressions: `MathlibTest/ComposableArrowsReduceMap.lean` (15 examples: 11 visit, 1 decline, 3 `rfl` baselines).
- Integrated probe: `MathlibTest/ComposableArrowsIntegratedProbe.lean` (13 examples, unchanged intent).

## Pin / identity

| Field | Value |
| --- | --- |
| Base | `08c3fc3f372a6d35d18190fb26b7be083378dc38` |
| Patch sha256 | `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026` |
| Validation identity (six files + build config) | `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57` |
| Toolchain | `leanprover/lean4:v4.35.0-rc3` |

Frozen path hashes:

- `Mathlib/CategoryTheory/ComposableArrows/Basic.lean` — `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251`
- `MathlibTest/ComposableArrowsReduceMap.lean` — `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb`
- `MathlibTest/ComposableArrowsIntegratedProbe.lean` — `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e`
- plus the three homology files recorded in `upstream-source.json`

## Validation results

On the pinned upstream candidate (fresh MathlibTest rebuild with cached library dependencies; not a cold library compile):

- Gates: environment / focused / downstream / full — exit 0.
- MathlibTest: 419/419 after artifact quarantine before `lake --iofail test`.
- Benchmark recorded under `LEAN_NUM_THREADS=2` / `LAKE_NUM_THREADS=2`.
- Lint passed for Mathlib.
- Finite probes are not a universal theorem about the reducer.

Evidence for that campaign was later published on the separate evidence-host branch / fraware PR #3. The audited validation evidence ZIP remains unchanged and still applies:

- sha256: `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c`

## Credential note (owner action pending)

New-package credential-pattern scan was clean. Redaction of the new package does **not** close earlier exposure in older archives. Expiry/revocation remains **owner action pending**: Mateo must rotate or revoke the leaked token. Remote cleanup requires separate approval. The secret is not restated here.

## Scope clarification

- Validation-phase “no remote writes” referred to the isolated gate campaign only (no community mathlib4 / CSLib writes during gates).
- Evidence-host publication to fraware (PR #3) is separate from this six-file source tip.
- This draft is **fraware review only**. Community mathlib4 submission is **not** authorized yet and needs Mateo’s explicit later approval.

## Checklist

- [x] Preferred reducer unchanged (no fallback numeral-reconstruction design).
- [x] Six Lean files only; no evidence archives or handoff scripts on the source tip.
- [x] No `sorry` / `admit` / new axioms / kernel bypass / new linter suppressions in these files.
- [x] Submission text ZIP hosted on the evidence branch for auditor download.
- [ ] Ready for community mathlib4 submission only after Mateo’s explicit approval.
