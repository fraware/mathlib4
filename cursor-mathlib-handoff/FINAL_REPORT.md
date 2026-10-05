# ComposableArrows handoff — FINAL REPORT

Generated from live verification on the WSL preferred checkout. Claims below are
tied to files under `.cursor-handoff/evidence/`. Nothing here authorizes remote writes.

## Selection
- Candidate: preferred
- Base HEAD: `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`
- Toolchain: `leanprover/lean4:v4.35.0-rc3`
- Final source fingerprint: `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`
- Fallback used: no
- `sorry` / `admit` / new axioms in Basic + ReduceMap + IntegratedProbe: none found
- Linter disables (`set_option linter.*`) in those files: none found
- Integrated probe byte-identical to HEAD: yes (`b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e`)
- Preferred expectation shape in ReduceMap: 15 `example`s; 11 visit + 1 decline
  check tactics and 3 `rfl` baselines (not fallback counts)

## File hashes
| path | sha256 |
| --- | --- |
| `Mathlib/CategoryTheory/ComposableArrows/Basic.lean` | `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251` |
| `MathlibTest/ComposableArrowsReduceMap.lean` | `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb` |
| `MathlibTest/ComposableArrowsIntegratedProbe.lean` | `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e` |

## Gate statuses (fingerprint `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`)
| stage | status | fingerprint match | command exits |
| --- | --- | --- | --- |
| baseline | passed (pre-candidate clean tree) | n/a (clean-tree fp `5511d3b051368432a2922bb1292994db0c5d8b181417fd0fec22d9c4344c94ba`) | [0, 0, 0, 0] |
| focused | passed | True | [0, 0] |
| downstream | passed | True | [0] |
| full | passed | True | [0, 0, 0, 0] |

### Full command detail (current official marker)
| step | exit | log | log_size |
| --- | --- | --- | --- |
| `lake exe mk_all --check` | 0 | `full-1-1791105555568304863.log` | 153 |
| `lake build Mathlib Archive Counterexamples Wanted` | 0 | `full-2-1791105560534445262.log` | 42 |
| `lake --iofail test` | 0 | `full-3-1791105572341543794.log` | 140 |
| `lake lint -- --trace` | 0 | `full-4-1791105591250400144.log` | 2668 |

### Official full-3 test log (non-empty)
Log `full-3-1791105572341543794.log` (140 bytes), exit 0:

```
✔ [9402/9403] Built MathlibTest.ComposableArrowsReduceMap (9.1s)
✔ [9403/9403] Built MathlibTest.ComposableArrowsIntegratedProbe (9.8s)
```

How this log was obtained: deleted lake artifacts for
`MathlibTest.ComposableArrowsReduceMap` and `MathlibTest.ComposableArrowsIntegratedProbe`,
then ran `python3 .cursor-handoff/workflow.py run full`. Other MathlibTest targets were
already up-to-date (cache hits, not rebuilt). `ClickSuggestions.Benchmark.olean` was
left intact because a prior broad rebuild failed that wall-clock guard
(`full-3-1791084123470358418.log`).

### Supplemental (labeled supplemental; not a substitute marker)
- `lake --iofail test` after the same candidate artifact clean:
  `supplemental-iofail-mathlibtest-1791105436788757300.log` size=295 exit=0
  fingerprint=cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0
- Earlier candidate-only rebuild:
  `supplemental-iofail-candidate-1791088555137648473.log` (266 bytes, EXIT:0)

## What was false or incomplete before
1. Official full-gate test log `full-3-1791085799857013292.log` was **0 bytes**.
   Exit 0 was real; rebuild evidence for the candidate was not in that official log.
2. Prior ZIP `66484dfc1f5f3c8d571b243c9817602a3296dda531994a4466fbfa47848ffd03` matched its bytes (verified) but packaged that empty full-3.
3. Export `SUMMARY.json` scope text still said baseline discrimination needed a
   separate report even though adversarial artifacts were already present.
4. Preferred adversarial success logs are only `EXIT:0` (lean silent on success).
   Not fabricated, but weak as transcripts; original-failure logs hold the errors.

## What was fixed (evidence paths)
1. Forced non-cached candidate rebuild through official full gate:
   - `full-rerun-clean-note-*.json`, `full-rerun-wrapper.log`
   - new `full.json` with non-empty `full-3-1791105572341543794.log`
2. Supplemental non-empty `lake --iofail test`: `supplemental-iofail-mathlibtest-1791105436788757300.log`
3. Live adversarial spot-check after full rerun (fingerprint unchanged): `spotcheck-adv-1791107561069787219.json`
   preferred custom_ofnat_first / wrong_sem exit 0; original both exit 1.
4. FINAL_REPORT rewritten to verified facts only.

## Adversarial matrix (`~/mathlib4-cursor-adv`)
Source matrix: `advsuite_matrix.json` (timestamp 2026-10-03T22:40:00.969906+00:00).
Live confirmation: `spotcheck-adv-1791107561069787219.json`.

| probe | original exit | preferred exit |
| --- | --- | --- |
| standard_visit | 0 | 0 |
| custom_ofnat_first | 1 | 0 |
| custom_ofnat_first_wrong_sem | 1 | 0 |
| custom_ofnat_second | 1 | 0 |
| custom_ofnat_second_wrong_sem | 1 | 0 |
| equivalent_ofnat | 0 | 0 |
| shadow_le | 1 | 0 |
| opaque_decline | 0 | 0 |
| successor_constructors | 1 | 0 |

## Push safeguards
- failing `pre-push` via `core.hooksPath` mateo-local-hooks
- `remote.origin.pushurl=disabled://mateo-approval-required`
- No remote mutations performed.

## Residual risks / what was NOT proven
- Official full-3 proves rebuild of the **two candidate MathlibTest modules** under
  `lake --iofail test` exit 0. It does **not** prove a cold rebuild of all MathlibTest
  modules in that run.
- Prior broader MathlibTest rebuild failed on `MathlibTest.ClickSuggestions.Benchmark`
  (`full-3-1791084123470358418.log`). Full-suite cold test under this host is not proven.
- Finite adversarial probes only; not a universal claim about all `Precomp.map` inputs.
- Local gates/export do not authorize upstream submission.
- WSL ~7.4Gi RAM remains an environment risk for aggressive MathlibTest parallelism.

## Export hashes (verified from ZIP bytes)
- WSL ZIP: `/home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip`
- Windows ZIP: `C:/Users/mateo/mathlib4-1/cursor-mathlib-handoff/cursor-validation-evidence.zip`
- ZIP sha256: `4a10c162ddba394a4ad9c2e647f6cf74b8243221ee930c0be2a7feba05e1caef`
- ZIP bytes: 135050
- Supersedes older ZIP `66484dfc1f5f3c8d571b243c9817602a3296dda531994a4466fbfa47848ffd03` (that archive matched its own hash but contained
  empty official full-3 log `full-3-1791085799857013292.log`).

## Artifacts
- Evidence: `/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/`
- WSL ZIP: `/home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip`
- Windows mirror: `C:/Users/mateo/mathlib4-1/cursor-mathlib-handoff/cursor-validation-evidence.zip`
