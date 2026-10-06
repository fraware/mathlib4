Evidence-host package for preferred ComposableArrows `Precomp.reduceMap` validation. This PR is not the production upstream fix.

## rc4 campaign (complete)

- Base: `321b3b85cb86b65144d78546020d53650b0d9071` + `production.patch`
- Toolchain: `leanprover/lean4:v4.35.0-rc4`
- Validation identity: `ef3dc5d381ca1010898c59454f38b4a9aeac22e3eddd0f529a1587d07d3e5d51`
- Package: `rc4-validation-evidence/` (`mathlib-rc4-validation-evidence-20261006T200656Z.zip` sha256 `c51d0dc66b96f5de6154f5ae52702bcb2f5eb9f3a7a8b4249873f5cfe63634bf`)
- Gates: environment / focused / downstream / full all passed
- MathlibTest: 422/422 after quarantine rebuild under `LEAN_NUM_THREADS=2` / `LAKE_NUM_THREADS=2`
- Preferred reducer: unchanged
- Source tip: `87c02f58ddee83b0a10946c762c6ba6f6eda7738` on `research/composable-arrows-reduce-map-rc4-source` (parent `321b3b85…`)
- Download: https://github.com/fraware/mathlib4/raw/research/composable-arrows-reduce-map-evidence/rc4-validation-evidence/mathlib-rc4-validation-evidence-20261006T200656Z.zip
- Directory: https://github.com/fraware/mathlib4/tree/research/composable-arrows-reduce-map-evidence/rc4-validation-evidence
- Release: https://github.com/fraware/mathlib4/releases/tag/rc4-validation-evidence-ef3dc5d3
- See `rc4-validation-evidence/READINESS.md` and `rc4-validation-evidence/HOSTING.md`

## Upstream candidate / rc3 (complete; unchanged)

- Base: `08c3fc3f372a6d35d18190fb26b7be083378dc38` + `production.patch`
- Toolchain: `leanprover/lean4:v4.35.0-rc3`
- Validation identity: `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`
- Package: `upstream-candidate-evidence/` (`upstream-validation-evidence.zip` sha256 `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c`)
- Gates: environment / focused / downstream / full all passed
- MathlibTest: 419/419 after quarantine rebuild; Benchmark ~55s under `LEAN_NUM_THREADS=2` / `LAKE_NUM_THREADS=2`
- Historical source tip `47e94148ec270467ea9cbccf5c56d1d9a6478a75` preserved on `research/composable-arrows-reduce-map-source`
- See `upstream-candidate-evidence/FINAL_REPORT.md`

## Historical pin (separate)

- `composable-arrows-handoff/` remains the earlier `a3cfff85…` campaign evidence.
- Prefer kit recovered/sanitized archives for provenance review of that campaign.

## Limits

- Finite tests do not prove universal reducer correctness.
- Does not authorize community Mathlib submission by itself.

## Housekeeping

- rc4 ZIP is frozen at sha256 `c51d0dc66b96f5de6154f5ae52702bcb2f5eb9f3a7a8b4249873f5cfe63634bf` (not rebuilt).
- Audited rc3 ZIP remains `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c` (not rebuilt).
- Documentation sidecars (ZIP bytes unchanged): `MEMBER_HASHES.corrected.txt` + `MEMBER_HASHES.NOTE.md` beside the ZIP and on release `rc4-validation-evidence-ef3dc5d3`. The ZIP-internal `MEMBER_HASHES.txt` still has a stale self-hash and is left audited.
- Branch `READINESS.md` (outside ZIP) records elan-managed success; the earlier host failure remains unexplained. ZIP-internal `READINESS.md` left audited/unchanged.
- "No remote writes" in packaged validation reports referred to the isolated validation phase (no community Mathlib/CSLib writes). Evidence is published to this evidence-host repository only. Evidence-host CI does not validate the production patch.
- Independent review accepted the rc3 validation package. Source-review notes: `upstream-candidate-evidence/SOURCE_REVIEW.md`.
- Submit preferred six-file `production.patch` (sha256 `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026`), not this evidence-host branch.
