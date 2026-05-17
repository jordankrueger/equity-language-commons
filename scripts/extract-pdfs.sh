#!/usr/bin/env bash
# extract-pdfs.sh — convert PDFs in source-guides/ to grep-able markdown siblings.
#
# Walks source-guides/ and source-guides/discovered/, runs pdftotext on each PDF
# that lacks a sibling .md, and writes <slug>.md next to the PDF.
#
# Phase 2.5a tooling. See ROADMAP.md "Phase 2.5" for context.
#
# Usage:
#   ./scripts/extract-pdfs.sh           # convert missing siblings
#   ./scripts/extract-pdfs.sh --force   # re-extract even if sibling exists
#   ./scripts/extract-pdfs.sh --dry-run # show what would be done
#   ./scripts/extract-pdfs.sh --layout  # preserve column layout (default: reading order)
#
# Requires: pdftotext (poppler). `brew install poppler` if missing.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${PROJECT_ROOT}/source-guides"

FORCE=0
DRY_RUN=0
LAYOUT_FLAG=""

for arg in "$@"; do
  case "$arg" in
    --force)    FORCE=1 ;;
    --dry-run)  DRY_RUN=1 ;;
    --layout)   LAYOUT_FLAG="-layout" ;;
    -h|--help)  sed -n '2,17p' "$0"; exit 0 ;;
    *)          echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

command -v pdftotext >/dev/null || {
  echo "pdftotext not found. Install with: brew install poppler" >&2
  exit 1
}

# Explicit slug overrides for the 6 archived PDFs in source-guides/ root,
# so their markdown siblings match the org_slug-YYYY-MM convention used in
# source-guides/discovered/ and in term frontmatter.
slug_for() {
  local basename="$1"
  case "$basename" in
    "7.27.20 YlI Styleguide 2020.pdf")                        echo "yli-styleguide-2020" ;;
    "CaseyStyleManualComplete.pdf")                           echo "casey-editorial-guide-2013-04" ;;
    "Equity Language Guide Sierra Club 2021.pdf")             echo "sierra-club-equity-language-guide-2021" ;;
    "Native-Governance-Center-Style-Guide-published-2021-02.pdf") echo "native-governance-center-style-guide-2021-02" ;;
    "SEIU Stylebook Jan 2020.pdf")                            echo "seiu-stylebook-2020-01" ;;
    "Stand_IdentityLong_June2019.pdf")                        echo "stand-earth-identity-2019-06" ;;
    *)
      # Already slugified (most files in discovered/): strip .pdf, keep as-is.
      # Otherwise fall back to a generic slugify pass.
      local stem="${basename%.pdf}"
      if [[ "$stem" =~ ^[a-z0-9._-]+$ ]]; then
        echo "$stem"
      else
        echo "$stem" \
          | tr '[:upper:]' '[:lower:]' \
          | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g'
      fi
      ;;
  esac
}

converted=0
skipped=0
failed=0

extract_one() {
  local pdf="$1"
  local dir base slug out
  dir="$(dirname "$pdf")"
  base="$(basename "$pdf")"
  slug="$(slug_for "$base")"
  out="${dir}/${slug}.md"

  if [[ -f "$out" && $FORCE -eq 0 ]]; then
    printf "  skip   %s (sibling exists)\n" "$base"
    ((skipped++)) || true
    return 0
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    printf "  would  %s → %s\n" "$base" "${slug}.md"
    ((converted++)) || true
    return 0
  fi

  local tmp
  tmp="$(mktemp -t extract-pdf.XXXXXX)"
  if ! pdftotext -enc UTF-8 -nopgbrk $LAYOUT_FLAG "$pdf" "$tmp" 2>/dev/null; then
    printf "  FAIL   %s (pdftotext error)\n" "$base" >&2
    rm -f "$tmp"
    ((failed++)) || true
    return 0
  fi

  {
    printf -- "<!--\n"
    printf "extracted_from: %s\n" "$base"
    printf "tool: pdftotext (poppler) %s\n" "${LAYOUT_FLAG:+layout-preserving }default"
    printf "extracted_on: %s\n" "$(date -u +%Y-%m-%d)"
    printf "note: machine-extracted text; verify against the source PDF before quoting.\n"
    printf -- "-->\n\n"
    cat "$tmp"
  } > "$out"
  rm -f "$tmp"

  local pages chars density
  pages="$(pdfinfo "$pdf" 2>/dev/null | awk -F: '/^Pages/ {gsub(/ /,"",$2); print $2}')"
  chars="$(wc -c < "$out" | tr -d ' ')"
  printf "  ok     %s → %s (%s pages, %s bytes)" "$base" "${slug}.md" "${pages:-?}" "$chars"
  if [[ -n "${pages:-}" && "$pages" -gt 0 ]]; then
    density=$(( chars / pages ))
    # Header is ~250 bytes; real text usually >500 bytes/page. Below ~200 is almost
    # always an image-only PDF that needs OCR (tesseract) rather than pdftotext.
    if (( density < 200 )); then
      printf "  ⚠ low text density — likely image-only PDF, needs OCR"
    fi
  fi
  printf "\n"
  ((converted++)) || true
}

echo "scanning ${SOURCE_DIR}…"

# Walk root + discovered/ only (avoid surprises in any future subdirs).
shopt -s nullglob
for dir in "$SOURCE_DIR" "$SOURCE_DIR/discovered"; do
  [[ -d "$dir" ]] || continue
  echo
  echo "${dir#$PROJECT_ROOT/}:"
  for pdf in "$dir"/*.pdf "$dir"/*.PDF; do
    [[ -f "$pdf" ]] && extract_one "$pdf"
  done
done

echo
printf "summary: %d converted, %d skipped, %d failed\n" "$converted" "$skipped" "$failed"
[[ $failed -eq 0 ]] || exit 1
