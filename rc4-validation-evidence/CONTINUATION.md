# Engineer continuation — rc4 validation complete; publication gated

## Outcome

All kit validation stages passed on base `321b3b85cb86b65144d78546020d53650b0d9071` with toolchain `leanprover/lean4:v4.35.0-rc4`. Source identity remained `ef3dc5d381ca1010898c59454f38b4a9aeac22e3eddd0f529a1587d07d3e5d51`. Preferred reducer unchanged. No remotes were written.

## Toolchain note

If `lean --version` reports `failed to locate application` against a manually extracted Linux tarball, prefer elan:

```bash
export PATH="$HOME/.elan/bin:$PATH"
elan toolchain install leanprover/lean4:v4.35.0-rc4
```

Confirm from the checkout root (so `lean-toolchain` selects rc4):

```bash
lean --version
lake --version
lake env lean --version
```

## Reproduce checkout

```bash
kit_path="$(pwd)"  # this package, outside any Lean checkout
mkdir ../mathlib-rc4-checkout && cd ../mathlib-rc4-checkout
git init
git remote add origin https://github.com/leanprover-community/mathlib4.git
git config remote.origin.pushurl disabled://mateo-approval-required
git config core.autocrlf false
printf '%s\n' '#!/bin/sh' 'printf "%s\n" "STOP: explicit Mateo approval required." >&2' 'exit 1' > .git/hooks/pre-push
chmod +x .git/hooks/pre-push
git fetch --depth=1 origin 321b3b85cb86b65144d78546020d53650b0d9071
git checkout --detach FETCH_HEAD
git apply --check "$kit_path/production.patch"
git apply "$kit_path/production.patch"
```

## Re-run gates

```bash
export PATH="$HOME/.elan/bin:$PATH"
export LEAN_NUM_THREADS=2
export LAKE_NUM_THREADS=2
python3 "$kit_path/upstream_validation.py" ../mathlib-rc4-checkout "$kit_path/engineer-evidence" verify
# then environment → focused → downstream → full, stopping on nonzero exit
```

## Publication

Stop for Mateo. Do not push to leanprover-community. Do not change historical source commit `47e94148…`. If a fraware-only research branch is later approved, use brand-free commit messages and the repository’s PR-body script/Actions — not automated product PR footers.
