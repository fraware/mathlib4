# fix(CategoryTheory): support Fin.reduceFinMk in ComposableArrows

Restore compatibility with `Fin.reduceFinMk` by adding a definitional reducer for `ComposableArrows.Precomp.map`. The reducer checks whether both actual index expressions expose `Fin.mk`, then reduces the original application. This respects custom numeral instances and preserves the supplied standard-order witness, category instance, and universe arguments, including in contexts with a locally shadowing `LE` instance.

Supply explicit inverse-law fields for `isoMk₃` and `isoMk₄` through the corresponding `isoMkSucc` constructions. Remove the file-wide and downstream `Fin.reduceFinMk` exclusions addressed by this change.

Regression coverage includes all defining map branches, wrapped numerals, custom numeral instances, a shadowing order instance, arbitrary inequality witnesses, symbolic successor indices, and opaque indices. Direct reducer checks inspect the returned expression, its type, and definitional equality with both the input and expected result. Integrated examples exercise simplification and downstream constructions.

Validation on base `321b3b85cb86b65144d78546020d53650b0d9071` with Lean `v4.35.0-rc4` passed environment (`lake --version`, `lake env lean --version`, `lake exe cache get`), focused builds of `Mathlib.CategoryTheory.ComposableArrows.Basic` and both regression modules, downstream builds of the eight homology / composable-arrows / Mayer–Vietoris targets, full library targets (`Mathlib`, `Archive`, `Counterexamples`, `Wanted`) with library caches retained, a fresh rebuild of all 422 MathlibTest source modules after quarantining prior test artifacts, and `lake lint`. Source/configuration identity remained `ef3dc5d381ca1010898c59454f38b4a9aeac22e3eddd0f529a1587d07d3e5d51` throughout. Resource limits were `LEAN_NUM_THREADS=2` and `LAKE_NUM_THREADS=2`.

Fixes #27382.
