# ComposableArrows handoff — FINAL REPORT

Generated on cloud agent host after migration from WSL. Claims are tied to
`.cursor-handoff/evidence/` on fingerprint `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`. This does **not** authorize remote writes.

## Selection
- Candidate: preferred
- Base HEAD: `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`
- Toolchain: `leanprover/lean4:v4.35.0-rc3`
- Final source fingerprint: `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`
- Fallback used: no
- `sorry` / `admit` / new axioms in Basic + ReduceMap + IntegratedProbe: none
- Linter disables in those files: none
- Integrated probe unchanged vs HEAD: yes (`b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e`)
- Preferred ReduceMap shape: 15 examples; 11 visit + 1 decline + 3 rfl baselines

## File hashes
| path | sha256 |
| --- | --- |
| `Mathlib/CategoryTheory/ComposableArrows/Basic.lean` | `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251` |
| `MathlibTest/ComposableArrowsReduceMap.lean` | `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb` |
| `MathlibTest/ComposableArrowsIntegratedProbe.lean` | `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e` |

## Gate statuses (fingerprint `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`)
| stage | status | fingerprint match | command exits |
| --- | --- | --- | --- |
| baseline | passed (pre-candidate) | clean-tree `5511d3b051368432a2922bb1292994db0c5d8b181417fd0fec22d9c4344c94ba` | [0, 0, 0, 0] |
| focused | passed | True | [0, 0] |
| downstream | passed | True | [0] |
| full | passed | True | [0, 0, 0, 0] |

### Full command detail (current official marker)
| step | exit | log | log_bytes |
| --- | --- | --- | --- |
| `lake exe mk_all --check` | 0 | `full-1-1791224101478833583.log` | 14732 |
| `lake build Mathlib Archive Counterexamples Wanted` | 0 | `full-2-1791224135954543363.log` | 30158 |
| `lake --iofail test` | 0 | `full-3-1791224613247116264.log` | 30848 |
| `lake lint -- --trace` | 0 | `full-4-1791225243707426479.log` | 7949 |

### Cold MathlibTest rebuild (this campaign)
- Quarantine: `quarantine-mathlibtest-20261005T181458-cold-rerun/` (16 MathlibTest artifacts moved; active tree had 0 MathlibTest files remaining before full). Mathlib/dependency caches retained.
- Resource policy: `LEAN_NUM_THREADS=2`, `LAKE_NUM_THREADS=2` (documented in `resource-policy-cloud.json`). **Benchmark.lean threshold not changed.**
- Official `full-3` rebuilt the MathlibTest suite non-selectively. Quote: `✔ [9308/9403] Built MathlibTest.ClickSuggestions.Benchmark (53s)`.
- Candidate modules also rebuilt in that log: `ComposableArrowsReduceMap (1.4s)`, `ComposableArrowsIntegratedProbe (2.3s)`.
- Label: **fresh MathlibTest rebuild with cached library dependencies**.

## Benchmark diagnosis
- Classification: 60-second wall-clock assertion (`guard (all < 60_000)` at Benchmark.lean:33).
- Prior WSL suite-load failures preserved under `preserved-benchmark-fail/` and noted in `preserved-cold-full-20261005/` (Oct 5 WSL fail log bytes were not transferred; assessment reported ~102s fail).
- This cloud cold full: Benchmark **passed** at 53s under reduced parallelism.
- Implication: suite-load / resource contention, **not** a preferred-reducer design failure. Fallback not used.

## Adversarial (original vs preferred)
Artifacts from prior WSL campaign packaged under `evidence/advsuite_*`, `advsuite_matrix.json`, `spotcheck-adv-*.json`.
Preferred visits custom-OfNat / wrong-sem / shadow-LE / successors where original fails; both pass standard_visit / opaque_decline / equivalent_ofnat.
Finite probes only — not a universal theorem.

## Environment migration honesty
Work continued on a Cursor cloud Linux host after the WSL checkout was unavailable. Phase A archived transferable failure evidence and explicitly recorded the missing Oct 5 WSL log path. Preferred source bytes were restored from the validated `candidate.patch` (hashes match prior fingerprint `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`).

## Push safeguards
- `core.hooksPath` mateo-local-hooks; failing pre-push
- `remote.origin.pushurl=disabled://mateo-approval-required`
- No remote mutations in this campaign

## Residual risks / NOT proven
- Passing finite Meta checks and MathlibTest does not prove universal reducer correctness.
- Export does not authorize upstream submission.
- Adversarial suite logs for preferred successes remain lean-silent `EXIT:0` transcripts from the prior campaign (not re-executed on this host in this turn).
- Warm Mathlib/Archive/Wanted caches: full-2 may include cache hits; MathlibTest portion was cold.

## Export notes
- Member-file hashes: `evidence/MEMBER_HASHES.txt` (inside ZIP).
- ZIP sha256: external sidecar only (`cursor-validation-evidence.zip.sha256`), never inside the archive.
