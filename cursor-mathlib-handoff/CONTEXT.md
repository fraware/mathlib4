# Technical context and evidence boundary

## Identity

- Repository: https://github.com/fraware/mathlib4
- Existing branch: `fix/composable-arrows-fin-reduce`
- Fixed baseline: `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`
- Parent recorded in the earlier audit: `380f2aafb622cb2c1c93dac545b6389083c68c51`
- Toolchain: `leanprover/lean4:v4.35.0-rc3`
- Upstream issue: https://github.com/leanprover-community/mathlib4/issues/27382

Branch names and upstream status might move; the workflow uses the full commit.
No rebase or upstream status check is needed to run this experiment.

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
included in this package. That result does not validate either new candidate.

## Defect hypothesis and proposed repair

Lean's `getFinValue?` interprets numeral syntax using standard Fin semantics while
discarding the actual OfNat instance. `toExpr` reconstructs a standard numeral.
An alternative instance can give the input numeral a different value. The original
reducer also synthesizes a fresh LE relation, decidability instance and proof,
despite already having the original inequality witness.

These are source-supported reasons to harden the reducer. Runtime reproduction
of the adversarial failures is still pending here. Do not describe them as a Lean
kernel soundness hole.

Preferred patch: use implicit-transparency definitional reduction to expose Fin
constructors, then reduce the original Precomp.map application. No index, universe,
category instance, or proof is reconstructed. Its constructor check does NOT
exclude every symbolic value; explicit successor constructors can reduce.

Fallback patch: retain numeral canonicalization but demand definitional equality
for both indices at fresh metavariable depth and preserve all original arguments
and the original proof. Fresh depth prevents caller-metavariable assignment; it
is not a claim that every part of the metaprogramming state is rolled back.

## Current status

Both supplied patches and Lean test files are experimental and uncompiled.
Earlier local attempts used the official pinned Linux binary, which failed at
startup with `error: failed to locate application`; process-executable lookup was
denied. Lake version reporting succeeded, while normal Lean execution did not.
One explicit-root Lake invocation timed out. Those environment errors are not
evidence of a candidate compilation failure.

This package moves execution to Mateo's own local Cursor environment. Do not
reproduce platform restrictions or use an access-control workaround.

## Primary source references

- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/Meta/WHNF.lean
- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/Meta/LitValues.lean
- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/ToExpr.lean
- https://github.com/leanprover/lean4/blob/v4.35.0-rc3/src/Lean/Meta/Tactic/Simp/Types.lean
