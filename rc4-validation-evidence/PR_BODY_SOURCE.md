# ComposableArrows: Fin.reduceFinMk-compatible Precomp.reduceMap (rc4)

> **fraware review hosting only.** This draft PR presents the six-file source tip rebased onto base `321b3b85…` and validated on Lean `v4.35.0-rc4`. It is **not** a community/upstream mathlib4 submission. Upstream submission still requires Mateo’s explicit later approval.

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
- Direct regressions: `MathlibTest/ComposableArrowsReduceMap.lean`
- Integrated probe: `MathlibTest/ComposableArrowsIntegratedProbe.lean`

## Pin / identity (rc4)

| Field | Value |
| --- | --- |
| Base | `321b3b85cb86b65144d78546020d53650b0d9071` |
| Source tip | `87c02f58ddee83b0a10946c762c6ba6f6eda7738` |
| Patch sha256 | `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026` |
| Validation identity (six files + build config) | `ef3dc5d381ca1010898c59454f38b4a9aeac22e3eddd0f529a1587d07d3e5d51` |
| Toolchain | `leanprover/lean4:v4.35.0-rc4` |

Frozen path hashes:

- `Mathlib/CategoryTheory/ComposableArrows/Basic.lean` — `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251`
- `MathlibTest/ComposableArrowsReduceMap.lean` — `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb`
- `MathlibTest/ComposableArrowsIntegratedProbe.lean` — `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e`
- plus the three homology files recorded in `rc4-validation-evidence/upstream-source.json`

Compare: https://github.com/fraware/mathlib4/compare/321b3b85cb86b65144d78546020d53650b0d9071...87c02f58ddee83b0a10946c762c6ba6f6eda7738

## Validation results

On the pinned rc4 candidate (fresh MathlibTest rebuild with cached library dependencies):

- Gates: environment / focused / downstream / full — exit 0.
- MathlibTest: 422/422 after artifact quarantine before `lake --iofail test`.
- Resource limits: `LEAN_NUM_THREADS=2` / `LAKE_NUM_THREADS=2`.
- Lint passed.
- Finite probes are not a universal theorem about the reducer.

Evidence package:

- Path: `rc4-validation-evidence/` on `research/composable-arrows-reduce-map-evidence`
- ZIP sha256: `c51d0dc66b96f5de6154f5ae52702bcb2f5eb9f3a7a8b4249873f5cfe63634bf` (frozen; not rebuilt)
- Corrected sidecars (outside ZIP): `MEMBER_HASHES.corrected.txt`, `MEMBER_HASHES.NOTE.md`; branch `READINESS.md` notes elan-managed success
- Download: https://github.com/fraware/mathlib4/raw/research/composable-arrows-reduce-map-evidence/rc4-validation-evidence/mathlib-rc4-validation-evidence-20261006T200656Z.zip
- Release: https://github.com/fraware/mathlib4/releases/tag/rc4-validation-evidence-ef3dc5d3

## Historical rc3 tip (unchanged)

The earlier tip `47e94148ec270467ea9cbccf5c56d1d9a6478a75` on `research/composable-arrows-reduce-map-source` (base `08c3fc3f…`, toolchain rc3) remains as-is. Six Lean file bytes match; this branch is the rc4 re-pin and re-validation.

## Scope clarification

- This draft is **fraware review only**. Community mathlib4 submission is **not** authorized yet and needs Mateo’s explicit later approval.
- Preferred reducer unchanged.

## Checklist

- [x] Preferred reducer unchanged (no fallback numeral-reconstruction design).
- [x] Six Lean files only; no evidence archives or handoff scripts on the source tip.
- [x] No `sorry` / `admit` / new axioms / kernel bypass / new linter suppressions in these files.
- [x] rc4 validation evidence hosted on the evidence branch for auditor download.
- [ ] Ready for community mathlib4 submission only after Mateo’s explicit approval.
