# Post-publication addendum (outside the audited ZIP)

This file is **not** a member of `upstream-validation-evidence.zip`. It exists so
the audited archive stays byte-identical (outer sha256
`ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c`; sidecar
match; 41 hashed members per `MEMBER_HASHES.txt`). Rebuilding the ZIP would
change that hash and is not done.

The repository copy of `FINAL_REPORT.md` now includes the same addendum text.
The copy inside the ZIP does not. That difference is intentional.

Independent review of commit `bba88b87bbda4b7bf35cf52d54d5bb5919707a37`
accepted the validation package. Preferred reducer retained; `production.patch`
frozen at sha256
`20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026`.

## "No remote writes" meant the validation phase

Wording in the packaged report described isolated validation: checkout of
community mathlib4 `08c3fc3f372a6d35d18190fb26b7be083378dc38`, disabled push
URL / local pre-push hook, no community Mathlib or CSLib writes.

After validation, evidence was published to the **evidence-host** repository
`fraware/mathlib4` (`bba88b87bbda4b7bf35cf52d54d5bb5919707a37`, draft PR #3).
That later publish is not a community mathlib4 submission. Evidence-host branch
CI does not validate the production patch.

## Credential exposed in an older archive

New-package scan: clean (known URL-password and GitHub token shapes).

New-package redaction does **not** close exposure from an older archive.
Expiry or revocation remains an **owner** responsibility. Follow-up work cannot
revoke the credential. Mateo (credential owner) must rotate or revoke the leaked
token. Any remote cleanup is a separately approved action. The secret is not
repeated here.

## Source review

See `SOURCE_REVIEW.md` in this directory. Submit preferred six-file source
against community mathlib4; do not cherry-pick evidence-host commits as the
production fix.
