# Source review notes (preferred production patch)

Evidence-host materials for Mateo. This is **not** a community mathlib4 pull
request and does not submit upstream.

Independent review of `fraware/mathlib4` commit
`bba88b87bbda4b7bf35cf52d54d5bb5919707a37` accepted the validation package.
Preferred reducer kept; fallback not used. Lean / full campaign not re-run for
this note.

## Pin and identity

| Field | Value |
| --- | --- |
| Community mathlib4 base | `08c3fc3f372a6d35d18190fb26b7be083378dc38` |
| Toolchain | `leanprover/lean4:v4.35.0-rc3` (Lake/Lean observed `4.35.0-rc3`, commit `470d5ce1400764999581fd26d5d72b00d990b0f4`) |
| Validation identity | `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57` |
| Frozen `production.patch` sha256 | `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026` |
| Audited ZIP sha256 | `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c` (240829 bytes; sidecar match) |

Apply `production.patch` from the ZIP (`evidence/production.patch`) onto the
pinned base. Do not apply `candidate.patch`. Do not cherry-pick commits from
`research/composable-arrows-reduce-map-evidence` as the production fix.

## Six paths and frozen hashes

Reconstruct exactly on the pin:

| path | sha256 |
| --- | --- |
| `Mathlib/CategoryTheory/ComposableArrows/Basic.lean` | `28b135aa722aa1e27899e94b191ac23c2e00802f61859ba1d392f64404797251` |
| `Mathlib/Algebra/Homology/ExactSequence.lean` | `3ee751c85a4a6ea926cb0e40f2c4f5ba1d178b575495804ab25782e32b1be6c5` |
| `Mathlib/Algebra/Homology/HomologySequence.lean` | `43f6fd6f84fb1d61467addbad7dfc8f873534deb618901b61543dc722bb68e04` |
| `Mathlib/Algebra/Homology/HomotopyCategory/ShortExact.lean` | `3dff79b51cb39c2f548b7035b4d2bc17fdff61d323f3506613d1cad99834d17e` |
| `MathlibTest/ComposableArrowsReduceMap.lean` | `3a3f1966332c9a2f2c7b5c378f074701646a0c480342f6a50c75fc77c23b4ecb` |
| `MathlibTest/ComposableArrowsIntegratedProbe.lean` | `b7e4de02fd8e1a433fecbe94d4840dc50a0af614898edd99da002fa42a60101e` |

## Reducer invariants (preferred)

- `Precomp.reduceMap` stays constructor-head `whnfHeadPred`.
- No numeral reconstruction / inequality-proof synthesis (fallback unused).
- 13 integrated examples and 15 direct regressions preserved.
- No `sorry` / `admit` / new axioms / kernel bypass / new linter suppressions
  in the six files.

## Validation summary (honest scope)

Independent review treated these as verified (not re-proved here):

- Six files reconstruct on the pin; identity `13281f16…07a57`; toolchain/build
  config match the pin.
- Four gates exit 0 (environment / focused / downstream / full).
- MathlibTest 419/419; Benchmark 55s under `LEAN_NUM_THREADS=2` /
  `LAKE_NUM_THREADS=2`; lint passed.
- ZIP matches sidecar; 41 `MEMBER_HASHES.txt` members OK; credential-pattern
  scan clean on the **new** package.
- **Execution scope:** cached library artifacts; **fresh MathlibTest rebuild**;
  ~22 min full stage. Not a cold library compile. Library oleans were copied
  from a same-pin tree; `lake exe cache get` then library builds were cache
  hits; MathlibTest artifacts were quarantined immediately before
  `lake --iofail test`.
- Evidence-host branch CI does not validate the production patch.
- Finite tests do not prove universal reducer correctness.

## Remaining owner actions

1. **Credential (older archive):** new-package redaction does not close earlier
   exposure. Automated follow-up cannot revoke the token. Mateo must rotate or
   revoke it. Remote cleanup needs separate approval. Secret not restated.
2. **Community Mathlib publication** still needs Mateo's explicit approval.
   This evidence-host branch / `fraware/mathlib4` PR #3 is not that submission.
3. **Source review** of the six frozen files / `production.patch` before any
   community PR.

## Recommendation

Submit the **preferred six-file source** (`production.patch` on
`08c3fc3f372a6d35d18190fb26b7be083378dc38`), not the evidence-host branch
history. Keep the ZIP frozen at `ce377c08…`.
