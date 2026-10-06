# rc4 validation status

Completed on 2026-10-06. Upstream submission remains pending Mateo’s explicit publication approval.

## Verified preparation

- Separate local detached checkout at `321b3b85cb86b65144d78546020d53650b0d9071`.
- Historical source commit `47e94148ec270467ea9cbccf5c56d1d9a6478a75` preserved (unchanged).
- Exactly the reviewed six-file patch applied; source bytes unchanged from the accepted rc3 campaign.
- Upstream rc4 toolchain, lakefile and all locked dependency revisions preserved.
- Source/configuration identity `ef3dc5d381ca1010898c59454f38b4a9aeac22e3eddd0f529a1587d07d3e5d51` stable through all stages.
- 422 MathlibTest source modules enumerated from this checkout; all rebuilt under the full stage.

## Toolchain repair

The prior host failure (`lean --version` → `failed to locate application`; `lake env lean --version` → Lake installation detection failure) came from a broken standalone Linux rc4 tree. On this host, elan installed `leanprover/lean4:v4.35.0-rc4` and both checks succeed:

- `lean --version` → `Lean (version 4.35.0-rc4, x86_64-unknown-linux-gnu, commit c29b6dda4f7c20e3eeaa717c4e565663c5cfa364, Release)`
- `lake --version` → `Lake version 5.0.0-src+c29b6dd (Lean version 4.35.0-rc4)`
- `lake env lean --version` → same Lean `4.35.0-rc4` string

## Gate results (`LEAN_NUM_THREADS=2`, `LAKE_NUM_THREADS=2`)

| Stage | Status | Notes |
| --- | --- | --- |
| verify | passed | identity `ef3dc5d381…7d3e5d51` |
| environment | passed | version checks + `lake exe cache get` |
| focused | passed | Basic + both regression modules |
| downstream | passed | eight homology / composable-arrows / Mayer–Vietoris targets |
| full | passed | `mk_all --check`; `Mathlib`/`Archive`/`Counterexamples`/`Wanted` with library caches retained; `lake --iofail test` rebuilt 422/422 expected MathlibTest modules after quarantining prior test artifacts; `lake lint` passed |

Preferred reducer unchanged. No remotes were written. Publication remains a separate approval step.

Evidence for this run lives under `engineer-evidence/` in this package (prior failed environment attempt retained under `evidence/`).
