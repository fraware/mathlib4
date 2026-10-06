#!/usr/bin/env bash
# Fail if text contains product-branding patterns.
# Intentionally does NOT match Lean "recursor" / "AuxRecursor".
set -euo pipefail

DOMAIN='cursor.com'
MARKER='CURSOR_AGENT'
EMAIL='cursoragent@cursor.com'
OPEN_IN='Open in Cursor'
MADE_WITH_A='Made with Cursor'
MADE_WITH_B='Made-with: Cursor'
# Product composer as a whole word (capital C); not "compose" / "composed".
COMPOSER_RE='\bComposer\b'
BRANCH_RE='cursor/cloud-agent'

mode='paths'
target=''

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      mode='file'
      target="${2:?}"
      shift 2
      ;;
    --stdin)
      mode='stdin'
      shift
      ;;
    --paths)
      mode='paths'
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--paths|--file PATH|--stdin]"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

scan_text() {
  local label="$1"
  local text="$2"
  local hits=0
  local pat
  for pat in \
    "$DOMAIN" \
    "$MARKER" \
    "$EMAIL" \
    "$OPEN_IN" \
    "$MADE_WITH_A" \
    "$MADE_WITH_B" \
    "$BRANCH_RE"
  do
    if grep -Fqi -- "$pat" <<<"$text"; then
      echo "HIT [$label]: fixed-string /$pat/" >&2
      hits=1
    fi
  done
  if grep -Eq -- "$COMPOSER_RE" <<<"$text"; then
    echo "HIT [$label]: /$COMPOSER_RE/" >&2
    hits=1
  fi
  return "$hits"
}

scan_stream() {
  local label="$1"
  local text
  text="$(cat)"
  if scan_text "$label" "$text"; then
    return 0
  fi
  return 1
}

# Return 0 = clean, 1 = dirty (matches set -e callers via explicit checks)
failed=0

case "$mode" in
  stdin)
    if ! scan_stream 'stdin'; then
      failed=1
    fi
    ;;
  file)
    if ! scan_stream "$target" <"$target"; then
      failed=1
    fi
    ;;
  paths)
    # Evidence-host / agent-facing paths only (avoid scanning all of Mathlib).
    mapfile -t files < <(
      git ls-files \
        'AGENTS.md' \
        '.cursor/**' \
        'scripts/set-pr-body.sh' \
        'scripts/check-product-branding.sh' \
        '.github/workflows/product-branding-guard.yml' \
        '.github/workflows/set-pr-body.yml' \
        'composable-arrows-handoff/**' \
        'upstream-candidate-evidence/**' \
        'source-submission-prep/**' \
        'rc4-validation-evidence/**' \
        2>/dev/null || true
    )
    # Guardrail / policy docs name banned strings on purpose; exclude them.
    exclude_re='^\.cursor/rules/|^AGENTS\.md$|^composable-arrows-handoff/AGENTS\.md$|^composable-arrows-handoff/BRANDING_HANDOFF\.md$|^scripts/check-product-branding\.sh$|^\.github/workflows/product-branding-guard\.yml$|^\.github/workflows/set-pr-body\.yml$|^scripts/set-pr-body\.sh$'
    for f in "${files[@]}"; do
      [[ -f "$f" ]] || continue
      if [[ "$f" =~ $exclude_re ]]; then
        continue
      fi
      # Skip binaries / zips
      if file -b --mime-encoding "$f" 2>/dev/null | grep -qi 'binary'; then
        continue
      fi
      case "$f" in
        *.zip|*.olean|*.png|*.jpg|*.jpeg|*.gif|*.webp|*.pdf)
          continue
          ;;
      esac
      if ! scan_stream "$f" <"$f"; then
        failed=1
      fi
    done
    ;;
esac

if [[ "$failed" -ne 0 ]]; then
  echo "product-branding check FAILED" >&2
  exit 1
fi
echo "product-branding check OK"
exit 0
