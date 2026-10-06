# Source review — preferred six-file production patch

**Verdict: preserve validated source.** No concrete defect found; preferred reducer left unchanged.

## Local source branch

| Field | Value |
| --- | --- |
| Repo path | `/home/ubuntu/mathlib-source-review` |
| Branch | `research/composable-arrows-reduce-map-source` |
| Parent (community base) | `08c3fc3f372a6d35d18190fb26b7be083378dc38` |
| Commit | `47e94148ec270467ea9cbccf5c56d1d9a6478a75` |
| Contents | Exactly the six Lean files from `production.patch` |
| Push protection | `remote.origin.pushurl=disabled://mateo-approval-required`; `core.hooksPath=/home/ubuntu/mateo-local-hooks` (pre-push exits 1); same pushurl on optional `fraware` remote |
| Publication | **Local-only** (not pushed to fraware; PR #3 untouched) |

## Identity checks

- Patch sha256: `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026`
- Six-file + build-config validation identity: `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`
- Frozen hashes match `upstream-source.json` (Basic `28b135aa…`, ReduceMap `3a3f1966…`, IntegratedProbe `b7e4de02…`, plus three homology files)

## Checklist findings

### Reducer

- Constructor-head `whnfHeadPred` gates on both indices exposing `Fin.mk`.
- Reduction applies to the **original** `Precomp.map` application (preserves proof/`Category`/universes).
- No `getFinValue?` / `toExpr` / `mkDecideProof` pattern on this path.
- Custom numeral / order adversarial cases exercise actual semantics rather than reconstructed decimals.

### Fin.reduceFinMk compatibility + inverse laws

- Removes file-wide `attribute [-simp] Fin.reduceFinMk` and per-site `[-Fin.reduceFinMk]`.
- Adds `hom_inv_id` / `inv_hom_id` on `isoMk₃` / `isoMk₄` via `isoMkSucc`.

### Regressions

- Integrated probe: 13 examples unchanged in content/intent.
- Direct ReduceMap: 15 examples = 11 visit + 1 decline + 3 `rfl` baselines.

### Hygiene

- No `sorry` / `admit` / axioms / kernel bypass in the six files.
- No new linter suppressions beyond base (test file avoids unused/unreachable tactics by closing with `rfl` after Meta checks).
- Mathlib style at a glance: doc comment on `dsimproc`, standard namespace/open, homology call-site cleanup matches surrounding proofs.

### Design changes

None proposed. Auditor found no preferred-design failure warranting the fallback.

## Credential status

**Owner action pending.** New-package scan clean; older-archive exposure unresolved by redaction. This prep cannot revoke the token. Mateo must rotate/revoke; remote cleanup needs separate approval. Secret not restated.

## “No remote writes” clarification

Validation-phase scope only (no community mathlib4/CSLib writes during gates). Evidence later published to fraware evidence-host `bba88b87…` / PR #3. Audited ZIP `ce377c08…` left frozen. This source branch was kept local to avoid conflating with the evidence-host PR.
