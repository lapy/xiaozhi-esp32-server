#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required for this audit." >&2
  exit 1
fi

CONTENT_IGNORE=(
  "!**/.git/**"
  "!**/node_modules/**"
  "!**/.venv*/**"
  "!**/dist/**"
  "!**/target/**"
  "!**/build/**"
  "!**/*.png"
  "!**/*.jpg"
  "!**/*.jpeg"
  "!**/*.gif"
  "!**/*.webp"
  "!**/*.bin"
  "!**/*.onnx"
  "!**/*.so"
  "!**/*.ttf"
  "!**/*.woff"
  "!**/*.woff2"
  "!**/*.mp3"
  "!**/*.wav"
  "!**/*.opus"
  "!**/*.pdf"
)

MAIN_IGNORE=(
  "${CONTENT_IGNORE[@]}"
  "!main/manager-api/src/main/resources/db/changelog/**"
  "!main/manager-web/public/generator/assets/**"
)

CONTENT_PATTERN='[\p{Han}]|zh-CN|zh-TW'
PATH_IGNORE=(
  "./.git"
  "./node_modules"
  "./main/manager-web/node_modules"
  "./main/manager-web/dist"
  "./main/manager-api/target"
)

section() {
  printf '\n== %s ==\n' "$1"
}

run_rg() {
  local pattern="$1"
  shift
  rg -n "$pattern" . "${@/#/-g }"
}

show_limited_matches() {
  local title="$1"
  local pattern="$2"
  shift 2
  local matches
  matches="$(rg -n "$pattern" "$@" || true)"
  if [[ -z "$matches" ]]; then
    echo "No matches."
    return 1
  fi

  local count
  count="$(printf '%s\n' "$matches" | wc -l | tr -d ' ')"
  echo "$count match(es). Showing up to 40:"
  printf '%s\n' "$matches" | sed -n '1,40p' | cut -c1-240
  if [[ "$count" -gt 40 ]]; then
    echo "... truncated ..."
  fi
  return 0
}

section "Live Source And Docs Audit"
if run_rg "$CONTENT_PATTERN" "${MAIN_IGNORE[@]}"; then
  echo
  echo "Live source/doc audit: FAIL"
  live_status=1
else
  echo "Live source/doc audit: PASS"
  live_status=0
fi

section "Historical Changelog Exceptions"
if show_limited_matches \
  "Historical changelog exceptions" \
  "$CONTENT_PATTERN" \
  main/manager-api/src/main/resources/db/changelog; then
  echo
  echo "Historical changelog exceptions detected above."
else
  echo "No historical changelog hits."
fi

section "Generated Bundle Exceptions"
if show_limited_matches \
  "Generated bundle exceptions" \
  "$CONTENT_PATTERN" \
  main/manager-web/public/generator/assets \
  main/manager-web/public/generator/index.html \
  -g '!**/*.png' -g '!**/*.jpg' -g '!**/*.jpeg'; then
  echo
  echo "Generated bundle exceptions detected above."
else
  echo "No generated bundle hits."
fi

section "Path Audit"
path_output="$(
  find . \
    $(printf " -path '%s' -prune -o" "${PATH_IGNORE[@]}") \
    -type f -print | rg '[\p{Han}]' || true
)"
if [[ -n "$path_output" ]]; then
  printf '%s\n' "$path_output"
  echo
  echo "Path audit: FAIL"
  path_status=1
else
  echo "Path audit: PASS"
  path_status=0
fi

section "Summary"
if [[ "$live_status" -eq 0 && "$path_status" -eq 0 ]]; then
  echo "Westernization baseline is clean outside intentional exceptions."
  echo "Intentional exceptions:"
  echo "- append-only Liquibase history under main/manager-api/src/main/resources/db/changelog"
  echo "- generated generator bundle under main/manager-web/public/generator/assets"
  exit 0
fi

echo "Westernization baseline still has non-exempt findings."
exit 1
