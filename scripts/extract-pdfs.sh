#!/usr/bin/env bash
# extract-pdfs.sh — convert PDFs in source-guides/ to grep-able markdown siblings.
#
# Walks source-guides/ and source-guides/discovered/, runs pdftotext on each PDF
# that lacks a sibling .md, and writes <slug>.md next to the PDF.
#
# Phase 2.5a tooling. See ROADMAP.md "Phase 2.5" for context.
#
# Usage:
#   ./scripts/extract-pdfs.sh           # convert missing siblings (text-only)
#   ./scripts/extract-pdfs.sh --force   # re-extract even if sibling exists
#   ./scripts/extract-pdfs.sh --dry-run # show what would be done
#   ./scripts/extract-pdfs.sh --layout  # preserve column layout (default: reading order)
#   ./scripts/extract-pdfs.sh --ocr     # OCR image-only PDFs (auto-detected by low text density)
#
# Requires: pdftotext (poppler). `brew install poppler` if missing.
# Optional (for --ocr): pdftoppm (poppler, already there) + tesseract.
#   `brew install tesseract` if missing.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${PROJECT_ROOT}/source-guides"

FORCE=0
DRY_RUN=0
LAYOUT_FLAG=""
OCR=0

for arg in "$@"; do
  case "$arg" in
    --force)    FORCE=1 ;;
    --dry-run)  DRY_RUN=1 ;;
    --layout)   LAYOUT_FLAG="-layout" ;;
    --ocr)      OCR=1 ;;
    -h|--help)  sed -n '2,20p' "$0"; exit 0 ;;
    *)          echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

command -v pdftotext >/dev/null || {
  echo "pdftotext not found. Install with: brew install poppler" >&2
  exit 1
}

if [[ $OCR -eq 1 ]]; then
  command -v pdftoppm >/dev/null || { echo "pdftoppm missing (brew install poppler)" >&2; exit 1; }
  command -v tesseract >/dev/null || { echo "tesseract missing (brew install tesseract)" >&2; exit 1; }
fi

# OCR an image-only PDF: rasterize each page with pdftoppm @ 300dpi,
# OCR each page image with tesseract, concatenate.
# Writes UTF-8 text to stdout. Returns non-zero on any failure.
ocr_pdf() {
  local pdf="$1"
  local workdir
  workdir="$(mktemp -d -t extract-ocr.XXXXXX)"
  pdftoppm -r 300 -png "$pdf" "${workdir}/page" 2>/dev/null || { rm -rf "$workdir"; return 1; }
  local img
  for img in "${workdir}"/page-*.png; do
    [[ -f "$img" ]] || continue
    tesseract "$img" - -l eng 2>/dev/null
    printf "\n"
  done
  rm -rf "$workdir"
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

  local pages
  pages="$(pdfinfo "$pdf" 2>/dev/null | awk -F: '/^Pages/ {gsub(/ /,"",$2); print $2}')"

  # Density check: if text per page is suspiciously low, the PDF is probably
  # image-only. With --ocr set, transparently fall back to tesseract.
  local tool_used="pdftotext"
  local raw_chars
  raw_chars="$(wc -c < "$tmp" | tr -d ' ')"
  if [[ -n "${pages:-}" && "$pages" -gt 0 ]]; then
    local raw_density=$(( raw_chars / pages ))
    if (( raw_density < 200 )) && [[ $OCR -eq 1 ]]; then
      printf "  ocr    %s (low density: %d bytes/page — running tesseract…)\n" "$base" "$raw_density"
      if ocr_pdf "$pdf" > "$tmp" 2>/dev/null && [[ -s "$tmp" ]]; then
        tool_used="tesseract (OCR)"
      else
        printf "  FAIL   %s (tesseract OCR error)\n" "$base" >&2
        rm -f "$tmp"
        ((failed++)) || true
        return 0
      fi
    fi
  fi

  {
    printf -- "<!--\n"
    printf "extracted_from: %s\n" "$base"
    printf "tool: %s%s\n" "$tool_used" "${LAYOUT_FLAG:+ (layout-preserving)}"
    printf "extracted_on: %s\n" "$(date -u +%Y-%m-%d)"
    printf "note: machine-extracted text; verify against the source PDF before quoting.\n"
    printf -- "-->\n\n"
    cat "$tmp"
  } > "$out"
  rm -f "$tmp"

  local chars density
  chars="$(wc -c < "$out" | tr -d ' ')"
  printf "  ok     %s → %s (%s pages, %s bytes, %s)" "$base" "${slug}.md" "${pages:-?}" "$chars" "$tool_used"
  if [[ -n "${pages:-}" && "$pages" -gt 0 ]]; then
    density=$(( chars / pages ))
    if (( density < 200 )); then
      if [[ $OCR -eq 0 ]]; then
        printf "  ⚠ low text density — image-only PDF, rerun with --ocr"
      else
        printf "  ⚠ low text density even after OCR — manual transcription may be needed"
      fi
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
