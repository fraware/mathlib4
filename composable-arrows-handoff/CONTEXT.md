# Technical context and evidence boundary

## Identity

- Repository: https://github.com/fraware/mathlib4
- Research / evidence branch: `research/composable-arrows-reduce-map-evidence`
- Historical campaign baseline: `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`
- Upstream-candidate base (community mathlib4): `08c3fc3f372a6d35d18190fb26b7be083378dc38`
- Parent recorded in the earlier audit: `380f2aafb622cb2c1c93dac545b6389083c68c51`
- Toolchain (both campaigns): `leanprover/lean4:v4.35.0-rc3`
- Upstream issue: https://github.com/leanprover-community/mathlib4/issues/27382

Branch names and upstream status might move; workflows use full commits.
No rebase or upstream status check is needed to inspect packaged evidence.

## Original change

The baseline removes the disabling of `Fin.reduceFinMk`, adds a map dsimproc for
`Precomp.map`, supplies inverse-law fields for `isoMk₃` and `isoMk₄`, and adjusts
related homology simplification. The original diff comprised five files:

1. `Mathlib/CategoryTheory/ComposableArrows/Basic.lean`
2. `Mathlib/Algebra/Homology/ExactSequence.lean`
3. `Mathlib/Algebra/Homology/HomologySequence.lean`
4. `Mathlib/Algebra/Homology/HomotopyCategory/ShortExact.lean`
5. `MathlibTest/ComposableArrowsIntegratedProbe.lean`

The integrated file contains 13 examples. Historical fork run 36672667647 was
previously inspected and reported successful for that exact baseline, including
full builds, the integrated probe, tests and lint. Raw historical logs are not
included in this package. That result does not alone validate the preferred
reducer redesign.

## Defect hypothesis and proposed repair

Lean's `getFinValue?` interprets numeral syntax using standard Fin semantics while
discarding the actual OfNat instance. `toExpr` reconstructs a standard numeral.
An alternative instance can give the input numeral a different value. The original
reducer also synthesizes a fresh LE relation, decidability instance and proof,
despite already having the original inequality witness.

These are source-supported reasons to harden the reducer. Do not describe them as
a Lean kernel soundness hole.

Preferred patch: use implicit-transparency definitional reduction to expose Fin
constructors, then reduce the original Precomp.map application. No index, universe,
category instance, or proof is reconstructed. Its constructor check does NOT
exclude every symbolic value; explicit successor constructors can reduce.

Fallback patch: retain numeral canonicalization but demand definitional equality
for both indices at fresh metavariable depth and preserve all original arguments
and the original proof. Fresh depth prevents caller-metavariable assignment; it
is not a claim that every part of the metaprogramming state is rolled back.

## Current status

**Historical campaign (a3cfff85…):** preferred candidate fully gated (focused /
downstream / full passed) on fingerprint
`cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`. Evidence:
`validation-evidence.zip` and `FINAL_REPORT.md` in this directory.

**Upstream-candidate campaign (08c3fc3f…):** preferred six-file production source
validated with identity
`13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`. All four
stages (environment / focused / downstream / full) passed. MathlibTest 419/419;
Benchmark 55s (cached library artifacts; fresh MathlibTest rebuild). Deliverables:
`../upstream-candidate-evidence/` (`upstream-validation-evidence.zip` sha256
`ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c`).

Preferred design and frozen hashes are unchanged across both campaigns. This
branch hosts evidence only; it is not the production upstream PR.

## Primary source references

- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/Meta/WHNF.lean
- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/Meta/LitValues.lean
- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/ToExpr.lean
- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/Meta/Tactic/Simp/Types.lean
