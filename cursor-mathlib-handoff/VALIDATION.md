# Validation protocol

## Gate order

The runner enforces exact HEAD and toolchain, a clean baseline before candidate
application, and current-source focused/downstream passes before full validation.
It writes command exit codes and source fingerprints. It never changes candidate
source during a run. An edited source invalidates earlier stage evidence.

Baseline: Lake/Lean version reporting, dependency cache, Basic and existing
integrated-probe build. Candidate application is blocked until this stage passes.

Focused: Basic, new direct regression tests, unchanged integrated probe.

Downstream: ExactSequence, HomologySequence, HomotopyCategory.ShortExact,
ComposableArrows.Four, ExactSequenceFour, Abelian.DiagramLemmas.Four, and both
Sites.SheafCohomology.MayerVietoris and Topology.Sheaves.MayerVietoris.

Full: `lake exe mk_all --check`; `lake build Mathlib Archive Counterexamples Wanted`;
`lake --iofail test`; `lake lint -- --trace`.

## Proposed regression expectations

Each supplied suite has 15 examples. Three are independent rfl baselines, and 12
directly inspect the reducer before the example's proof completes.

| Input | Preferred | Fallback |
| --- | --- | --- |
| Standard numerals, four map branches, diagonal, wrapped numeral | visit | visit |
| Explicit symbolic successor constructors | visit | decline |
| Opaque symbolic Fin variables | decline | decline |
| Nonstandard first numeral | visit using actual meaning | decline |
| Nonstandard second numeral | visit using actual meaning | decline |
| Shadowing LE instance | visit using stored proof | visit using stored proof |
| Alternative numeral instance with equal value | visit | visit |

Preferred totals: 11 visit assertions, one decline assertion, three baselines.
Fallback totals: eight visit assertions, four decline assertions, three baselines.
Counts describe proposed source cases, not executed results.

On visit, the helper checks reduction of the Precomp.map head, inferred-type
equality, result/input definitional equality, and result/expected definitional
equality. These are metaprogram checks; they are not a universal theorem about
all possible reducer inputs. The final Lean proofs still undergo ordinary kernel
checking. Independent rfl baselines distinguish invalid example statements from
reducer-specific behavior.

## Error handling

Separate environment/dependency failures, test-harness API errors, mistaken test
expectations, reducer elaboration failures, semantic failures and downstream
regressions. Never weaken an assertion just to make the run pass. Record the
diagnostic and source justification for each edit. Keep the original integrated
probe unchanged. Do not repair unrelated baseline files to hide failures.

## Baseline discrimination

Use a separate fresh setup checkout at the same SHA. Preserve the preferred
checkout and logs. Once the test harness compiles, create small local probes
containing that helper plus one adversarial section at a time. The plain rfl
baseline must compile separately; then run the direct reducer check with the
original implementation. Keep the compiler diagnostics and source of each probe.

Custom-numeral cases should distinguish wrong semantics, not merely a difference
in willingness to reduce. Shadowing-order failures should identify the unwanted
instance/proof synthesis. Any unexpectedly passing original case needs review of
the elaborated instance and whether the reducer was actually called.

For these additional probes, manually log `lake env lean path/to/probe.lean` and
its exit code. Store the source and logs under `.cursor-handoff/evidence/` so the
export includes them. Do not make an expected baseline failure look like a passed
candidate stage, and do not repurpose the automated stage markers.

## Fallback decision

First minimize and explain the preferred-design failure. If fallback is justified,
create a new setup checkout, run baseline, and use `apply fallback`. Never stack
both patches or reuse preferred-stage markers. Each candidate has its own test
expectations, checkout, hashes and logs.

## Final report

State the candidate, base, final source fingerprint, observed adversarial baseline
failures, all gate results and limitations. Include test-harness repairs and the
reason for any expectation changes. Report build jobs as build jobs, not tests.
Passing finite tests does not prove universal correctness of the metaprogram.
Passing local gates does not authorize publication or imply upstream acceptance.
