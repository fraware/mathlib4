# rc4 validation evidence — hosting note

Frozen validation evidence archive for the Lean `v4.35.0-rc4` campaign. ZIP bytes are intentional and must not be rebuilt.

## Download

- Archive: [`mathlib-rc4-validation-evidence-20261006T200656Z.zip`](./mathlib-rc4-validation-evidence-20261006T200656Z.zip)
- sha256: `c51d0dc66b96f5de6154f5ae52702bcb2f5eb9f3a7a8b4249873f5cfe63634bf` (ZIP bytes frozen; do not rebuild)
- Sidecar: [`mathlib-rc4-validation-evidence-20261006T200656Z.zip.sha256`](./mathlib-rc4-validation-evidence-20261006T200656Z.zip.sha256)
- Member hashes (audited, inside ZIP / copy): [`MEMBER_HASHES.txt`](./MEMBER_HASHES.txt) — contains a stale self-hash; left unchanged
- Member hashes (**corrected sidecar**): [`MEMBER_HASHES.corrected.txt`](./MEMBER_HASHES.corrected.txt) — every archive member with correct hashes; does not list itself. See [`MEMBER_HASHES.NOTE.md`](./MEMBER_HASHES.NOTE.md).
- Outside-ZIP doc note: branch `READINESS.md` corrects the host-failure wording (elan-managed success; earlier failure unexplained). The ZIP’s internal `READINESS.md` remains audited/unchanged.

Raw URL (evidence branch tip after this commit lands):

`https://github.com/fraware/mathlib4/raw/research/composable-arrows-reduce-map-evidence/rc4-validation-evidence/mathlib-rc4-validation-evidence-20261006T200656Z.zip`

Browse directory:

`https://github.com/fraware/mathlib4/tree/research/composable-arrows-reduce-map-evidence/rc4-validation-evidence`

## Linked source identity (rc4 tip)

| Field | Value |
| --- | --- |
| Branch | `research/composable-arrows-reduce-map-rc4-source` |
| Tip | `87c02f58ddee83b0a10946c762c6ba6f6eda7738` |
| Parent / review base | `321b3b85cb86b65144d78546020d53650b0d9071` |
| Contents | Exactly six Lean files (no evidence archives) |
| Validation identity | `ef3dc5d381ca1010898c59454f38b4a9aeac22e3eddd0f529a1587d07d3e5d51` |
| Toolchain | `leanprover/lean4:v4.35.0-rc4` |
| Patch sha256 | `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026` |

Compare: https://github.com/fraware/mathlib4/compare/321b3b85cb86b65144d78546020d53650b0d9071...87c02f58ddee83b0a10946c762c6ba6f6eda7738

## Historical rc3 pin (unchanged)

- Source tip `47e94148ec270467ea9cbccf5c56d1d9a6478a75` on `research/composable-arrows-reduce-map-source` remains the rc3 campaign pin.
- Audited rc3 validation ZIP under `upstream-candidate-evidence/` is unchanged.
- Preferred reducer unchanged across both campaigns; six Lean file bytes match the accepted patch.

## Gates (this package)

- environment / focused / downstream / full: passed
- MathlibTest: 422/422 after quarantining prior test artifacts
- Resource limits: `LEAN_NUM_THREADS=2`, `LAKE_NUM_THREADS=2`
- See `READINESS.md`, `SOURCE_VERIFICATION.json`, and the JSON summaries under `engineer-evidence/`

## Scope

This evidence-host path and any fraware draft PR that links here are for **fraware review only**. Community / upstream mathlib4 submission still requires Mateo’s explicit later approval. No community remote write is authorized by this note.

## Release asset (same ZIP bytes)

- Tag: `rc4-validation-evidence-ef3dc5d3`
- https://github.com/fraware/mathlib4/releases/tag/rc4-validation-evidence-ef3dc5d3
- Asset: https://github.com/fraware/mathlib4/releases/download/rc4-validation-evidence-ef3dc5d3/mathlib-rc4-validation-evidence-20261006T200656Z.zip
