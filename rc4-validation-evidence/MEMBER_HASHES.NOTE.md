# MEMBER_HASHES correction note

The audited evidence ZIP (`mathlib-rc4-validation-evidence-20261006T200656Z.zip`, sha256 `c51d0dc66b96f5de6154f5ae52702bcb2f5eb9f3a7a8b4249873f5cfe63634bf`) is unchanged.

Its internal `MEMBER_HASHES.txt` remains as audited. That file incorrectly lists a **stale self-hash** for `MEMBER_HASHES.txt` (`d0ad1c5f…`) instead of the hash of its own bytes (`257ebe2d…`). All other member hashes in that file match the archive contents.

Use the sidecar `MEMBER_HASHES.corrected.txt` (next to this note and the ZIP) for member verification:

- Lists every archive member under `mathlib-rc4-validation-prep/` with the correct content sha256.
- Includes the ZIP’s internal `MEMBER_HASHES.txt` under its **actual** content hash `257ebe2d988a065ce55c077b07938a4698ea21691a6e5bf4dc66d5b94466c819`.
- Does **not** list itself (`MEMBER_HASHES.corrected.txt`).

Do not rebuild or repack the ZIP to “fix” the internal manifest.
