#!/usr/bin/env bash
# Set a GitHub PR body from a file with zero product branding injection.
# Prefer this (or the set-pr-body.yml Actions workflow) over ManagePullRequest.
set -euo pipefail

usage() {
  echo "Usage: $0 <pr-number> <body-file> [--repo owner/name]" >&2
  exit 2
}

PR_NUMBER="${1:-}"
BODY_FILE="${2:-}"
REPO="${GITHUB_REPOSITORY:-fraware/mathlib4}"

shift 2 || usage
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="${2:?}"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      ;;
  esac
done

[[ -n "$PR_NUMBER" && -f "$BODY_FILE" ]] || usage

# Fail closed if the source body already contains product branding.
if ! scripts/check-product-branding.sh --file "$BODY_FILE"; then
  echo "Refusing to publish: body file fails product-branding check." >&2
  exit 1
fi

# Cloud-agent gh tokens often lack pull-requests:write. Prefer Actions workflow
# when this returns 403.
if ! jq -n --rawfile body "$BODY_FILE" '{body:$body}' \
  | gh api -X PATCH "repos/${REPO}/pulls/${PR_NUMBER}" --input - >/tmp/set-pr-body.out.json; then
  echo "Direct API PATCH failed (often 403 for integration tokens)." >&2
  echo "Dispatch the brand-free Actions path instead:" >&2
  echo "  gh workflow run set-pr-body.yml -f pr_number=${PR_NUMBER} -f body_path=${BODY_FILE}" >&2
  exit 1
fi

echo "Updated PR #${PR_NUMBER} on ${REPO}."
gh api "repos/${REPO}/pulls/${PR_NUMBER}" --jq .body \
  | scripts/check-product-branding.sh --stdin \
  || {
    echo "WARNING: live PR body failed branding check after update." >&2
    exit 1
  }
