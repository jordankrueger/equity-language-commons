#!/usr/bin/env python3
"""Build the Glossary Index JSON consumed by /glossary/.

Reads `notes/term-coverage-matrix.csv`, the term content collection (to
detect which terms have commons pages), and the source content collection
(for org display names + URLs). Emits a single JSON file Astro reads at
build time:

    site/src/data/glossary-index.json

Structure (truncated):

    {
      "generated_at": "2026-05-18T...",
      "stats": {
        "total_terms": 1273,
        "commons_terms": 18,
        "long_tail_terms": 1255,
        "by_coverage": {"1": 717, "2": 292, ...}
      },
      "by_letter": {
        "a": ["abc", "ableism", ...],
        ...,
        "#": ["#blackoutday", ...]
      },
      "entries": {
        "abc": {
          "term": "abc",
          "display": "ABC",
          "source_count": 2,
          "commons_slug": null,
          "sources": [{"org_slug": ..., "org": ..., "year": ..., "excerpt": ...}, ...]
        },
        ...
      }
    }

Idempotent. Re-run after any term batch / matrix rebuild / source edit.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
MATRIX_CSV = ROOT / "notes" / "term-coverage-matrix.csv"
TERMS_DIR = ROOT / "site" / "src" / "content" / "terms"
SOURCES_DIR = ROOT / "site" / "src" / "content" / "sources"
OUT_PATH = ROOT / "site" / "src" / "data" / "glossary-index.json"

# Maximum excerpt length per source, in characters. The matrix already
# truncates to 150ish chars; we re-truncate at 220 for display.
EXCERPT_MAX_CHARS = 220

# Terms shorter than this get filtered out — single chars and 2-char
# acronyms tend to be noise unless they have ≥3 source coverage.
SHORT_TERM_THRESHOLD = 3

# Stop-word endings that indicate a term is a truncated multi-word
# phrase (the matrix's term-universe builder sometimes captures only
# the first few words of a longer DSG glossary entry). A term ending
# in one of these whose word count is ≥ 2 gets dropped as noise.
TRUNCATED_PHRASE_ENDINGS = frozenset(
    {
        "of", "and", "the", "to", "or", "for", "in", "with", "on",
        "at", "by", "as", "from", "into", "onto", "via", "but",
        "an", "a",
    }
)


def _parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse YAML-ish frontmatter, line by line. No PyYAML dependency."""
    result: dict[str, str] = {}
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return result
    end = text.find("\n---", 4)
    if end == -1:
        return result
    block = text[4:end]
    for line in block.splitlines():
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            result[key] = value
    return result


def _build_org_lookup() -> tuple[dict[str, dict[str, str]], list[tuple[str, dict[str, str]]]]:
    """Build two lookups mapping matrix source_slug → source-page metadata.

    Matrix source slugs use long-form filenames (e.g.
    `ncdj-disability-style-guide-2021`). Site source-page slugs sometimes
    use a shorter org-only form (`ncdj.md`) because they predate the
    expanded matrix corpus. The two need to be bridged on both org
    display name AND the `/sources/<slug>/` link target.

    Returns:
        (exact_lookup, prefix_lookup)
        - exact_lookup: matrix_slug → metadata for direct filename match
        - prefix_lookup: sorted list of (org_slug, metadata) for
          longest-prefix matching against matrix slugs
    """
    exact: dict[str, dict[str, str]] = {}
    prefix: list[tuple[str, dict[str, str]]] = []

    for path in sorted(SOURCES_DIR.glob("*.md")):
        fm = _parse_frontmatter(path)
        page_slug = path.stem
        org = fm.get("org", page_slug.replace("-", " ").title())
        year = fm.get("year", "")
        url = fm.get("source_url", "")
        if url == "null":
            url = ""
        meta = {
            "org": org,
            "year": year,
            "source_url": url,
            "page_slug": page_slug,
        }
        exact[page_slug] = meta
        org_slug_fm = fm.get("org_slug")
        if org_slug_fm:
            prefix.append((org_slug_fm, meta))

    # Sort longest-first so "racial-equity-tools" matches before "racial".
    prefix.sort(key=lambda x: -len(x[0]))
    return exact, prefix


def _resolve_source(
    matrix_slug: str,
    exact: dict[str, dict[str, str]],
    prefix: list[tuple[str, dict[str, str]]],
) -> dict[str, str]:
    """Resolve a matrix source slug to source-page metadata, falling
    back to org_slug prefix matching when no exact filename match
    exists."""
    if matrix_slug in exact:
        return exact[matrix_slug]
    for org_slug, meta in prefix:
        if matrix_slug == org_slug or matrix_slug.startswith(org_slug + "-"):
            return meta
    # No match — return a synthetic entry so the row still renders.
    return {
        "org": matrix_slug,
        "year": "",
        "source_url": "",
        "page_slug": matrix_slug,
    }


def _build_commons_lookup() -> dict[str, str]:
    """Map term-slug → commons-page-slug for terms with .md files."""
    lookup: dict[str, str] = {}
    for path in sorted(TERMS_DIR.glob("*.md")):
        slug = path.stem
        # Index by both the file stem and any aliases visible in
        # frontmatter (the basic parser only sees scalar values, so
        # alias arrays aren't read here — fine for current usage).
        lookup[slug] = slug
        # Compound-slug case: tribe.md indexed as 'tribe' should also
        # match 'tribal' searches in the long-tail. Handled via aliases
        # in the term file's display, not here.
    return lookup


def _display_form(term: str, commons_slug: Optional[str]) -> str:
    """Pick a display form for the term. Commons-indexed terms get
    capitalized display; long-tail terms get title-case for non-acronyms,
    raw for hashtags/short acronyms."""
    if term.startswith("#"):
        return term
    if commons_slug:
        # Read the actual term-display name from the file.
        path = TERMS_DIR / f"{commons_slug}.md"
        fm = _parse_frontmatter(path)
        return fm.get("term", term.title())
    # Long-tail default: title-case unless it looks like an acronym.
    if len(term) <= 4 and term.isalpha() and term == term.lower():
        # Could be an acronym (abc, abcd) or a short word (gay, the).
        # Title-case is safer.
        return term.title()
    return term.title()


def _letter_bucket(term: str) -> str:
    """Return the A-Z bucket letter, or '#' for non-alphabetic starts."""
    if not term:
        return "#"
    first = term[0].lower()
    if "a" <= first <= "z":
        return first
    return "#"


def _clean_excerpt(text: str) -> str:
    """Strip Pandoc attribute fences, markdown link syntax, Wix-rich-text
    spans, and other formatting noise that leaks out of source markdown
    extracts. Returns the human-readable text content only.

    Run iteratively because the source markdown sometimes has nested
    span/attribute syntax (DSG and RET both produce these).
    """
    if not text:
        return ""

    cleaned = text

    # Strip markdown table-row separator pipes at the start of the
    # excerpt (NABJ's PDF extraction comes through as `| | | content`).
    cleaned = re.sub(r"^[\s>]*(\|\s*)+", "", cleaned)
    # Collapse internal cell separators to a single space for
    # readability — they're meaningful only in actual table layouts.
    cleaned = re.sub(r"\s+\|\s+", " ", cleaned)

    for _ in range(5):  # iterate to handle nested attribute spans
        before = cleaned
        # Drop Pandoc-style attribute fences: {.class}, {key="value"},
        # {.foo .bar key="value"}. Non-greedy, no inner braces.
        cleaned = re.sub(r"\{[^{}]*\}", "", cleaned)
        # Collapse markdown links: [text](url) → text. Handle URL-encoded
        # leading/trailing spaces in the URL.
        cleaned = re.sub(r"\[([^\[\]]+?)\]\(\s*[^)]+?\s*\)", r"\1", cleaned)
        # Strip remaining bracket spans (Wix nested form, Pandoc inline
        # markup without explicit attributes): [text] → text. Only when
        # there are no further bracketed inner segments.
        cleaned = re.sub(r"\[([^\[\]]+?)\]", r"\1", cleaned)
        if cleaned == before:
            break

    # Strip Pandoc heading markers, list bullets, and Markdown emphasis.
    cleaned = re.sub(r"^[\s>]*#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"^[\s]*[-*+]\s+", "", cleaned)
    cleaned = re.sub(r"\*\*([^*]+?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\1", cleaned)
    # Strip stray Pandoc/HTML attribute residue (rare but possible
    # after partial brace stripping mid-attribute).
    cleaned = re.sub(r"\.[a-zA-Z][a-zA-Z0-9_\-]*", "", cleaned)
    # Collapse Sierra Club TOC dot-leaders (`ABLEISM. .........`) to
    # a single period. Three or more dots in sequence — with or without
    # spaces between them — collapse to nothing.
    cleaned = re.sub(r"\.(\s*\.){2,}", "", cleaned)
    cleaned = re.sub(r"\.{3,}", "", cleaned)
    # Collapse whitespace.
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Trim a trailing standalone period left after dot-leader strip.
    cleaned = re.sub(r"\s+\.\s*$", "", cleaned).strip()
    return cleaned


def _is_index_only_excerpt(raw: str) -> bool:
    """True if the raw matrix excerpt looks like a pure DSG-style
    alphabetical glossary index entry — a bare link with attribute
    fence and nothing else. These have no definition content and are
    pure navigation; they shouldn't appear as sources in the glossary
    index page.
    """
    if not raw:
        return False
    stripped = raw.strip()
    # Pattern: optional leading list bullet, then [TERM](url){attrs} at
    # end-of-excerpt with at most trailing whitespace.
    pattern = r"^[-*+\s]*\[[^\[\]]+\]\(\s*[^)]+\s*\)\s*\{[^{}]+\}\s*$"
    return bool(re.match(pattern, stripped))


def _is_low_content_excerpt(cleaned: str) -> bool:
    """True if the cleaned excerpt has too little real content to be
    worth displaying inline. Sources still get listed, but the excerpt
    field is blanked out so the reader isn't shown noise.

    Targets:
    - PDF-extract garbage like 'yy able-bodied' or single-token noise
    - Section-heading-only matches like '### Abnormal/abnormality' that
      cleanup leaves as just the term name
    - Anything that doesn't have at least a verb-or-modifier-worth of
      context around the term
    """
    if len(cleaned) < 30:
        return True
    # Heading-only or label-only patterns: a term name + optional colon
    # or short trailing punctuation, no actual sentence content.
    if re.match(r"^[A-Za-z][\w/\-\s]{0,60}[:.]?$", cleaned):
        return True
    return False


def _truncate(text: str, max_chars: int = EXCERPT_MAX_CHARS) -> str:
    text = text.strip().replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def build_index() -> dict:
    if not MATRIX_CSV.exists():
        raise SystemExit(
            f"matrix CSV not found at {MATRIX_CSV} — run build-coverage-matrix.py first"
        )

    exact_lookup, prefix_lookup = _build_org_lookup()
    commons_lookup = _build_commons_lookup()

    entries: dict[str, dict] = {}
    coverage_histogram: dict[int, int] = {}

    with MATRIX_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = (row.get("term_normalized") or "").strip().lower()
            if not term:
                continue
            # Light noise filter: drop ultra-short non-hashtag terms with
            # low coverage. Final filter happens after grouping.
            if not term.startswith("#") and len(term) < SHORT_TERM_THRESHOLD:
                continue
            source_slug = (row.get("source_slug") or "").strip()
            raw_excerpt = row.get("excerpt") or ""
            # Drop pure-navigation-index hits — DSG/RET glossary index
            # entries with no actual definition content. They produce
            # the "[ABC](url){.glossaryLink}" style noise.
            if _is_index_only_excerpt(raw_excerpt):
                continue
            cleaned = _clean_excerpt(raw_excerpt)
            # Blank out low-content excerpts (section headings, PDF
            # garbage like 'yy able-bodied') — the source still gets
            # listed but the inline excerpt is suppressed.
            excerpt = "" if _is_low_content_excerpt(cleaned) else _truncate(cleaned)
            org_meta = _resolve_source(source_slug, exact_lookup, prefix_lookup)
            entry = entries.setdefault(
                term,
                {
                    "term": term,
                    "display": term,  # filled after grouping
                    "source_count": 0,
                    "commons_slug": None,
                    "sources": [],
                },
            )
            entry["sources"].append(
                {
                    # Use the resolved site-source-page slug for the
                    # link target — matrix slug may be a long-form
                    # filename that doesn't match the site's URL.
                    "source_slug": org_meta.get("page_slug", source_slug),
                    "org": org_meta.get("org", source_slug),
                    "year": org_meta.get("year", ""),
                    "source_url": org_meta.get("source_url", ""),
                    "excerpt": excerpt,
                    "extraction_method": row.get("extraction_method", ""),
                }
            )

    # Post-process: source_count, dedupe sources (same source can hit
    # the same term on multiple lines), commons-slug resolution,
    # display form, letter bucket.
    by_letter: dict[str, list[str]] = {}
    for term, entry in entries.items():
        # Dedupe sources by org/source_slug — keep first (strongest)
        # excerpt and discard later hits from the same source.
        seen_slugs = set()
        deduped = []
        for src in entry["sources"]:
            slug = src["source_slug"]
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            deduped.append(src)
        entry["sources"] = deduped
        entry["source_count"] = len(deduped)
        # Ultra-short terms are noise-prone — TV networks, file
        # extensions, country codes, etc. all match 2-4 char keyword
        # scans. Require more coverage to keep them:
        #   ≤2 chars → need ≥3 sources
        #   3-4 chars → need ≥2 sources
        #   5+ chars → any count (including 1) is acceptable
        if len(term) <= 2 and entry["source_count"] < 3:
            continue
        if 3 <= len(term) <= 4 and entry["source_count"] < 2:
            continue
        # Also drop if the term has zero remaining sources (the only
        # hits were filtered as index-only).
        if entry["source_count"] == 0:
            continue
        # Drop truncated multi-word phrases — the matrix's term-universe
        # builder sometimes captures only the first few words of a
        # longer DSG glossary entry (e.g. "accents and direct quotation
        # of [dialect]" → indexed as "accents and direct quotation of").
        # Terms with multiple words ending in a stop word are dropped.
        words = term.split()
        if len(words) >= 2 and words[-1].lower() in TRUNCATED_PHRASE_ENDINGS:
            continue
        # Resolve commons-page link.
        slug_dashed = term.replace(" ", "-")
        if slug_dashed in commons_lookup:
            entry["commons_slug"] = commons_lookup[slug_dashed]
        entry["display"] = _display_form(term, entry["commons_slug"])
        bucket = _letter_bucket(term)
        by_letter.setdefault(bucket, []).append(term)
        coverage_histogram[entry["source_count"]] = (
            coverage_histogram.get(entry["source_count"], 0) + 1
        )

    # Drop terms with source_count==0 (shouldn't happen post-dedupe, but
    # belt-and-suspenders) and any term filtered out above.
    valid_terms = {t for letters in by_letter.values() for t in letters}
    entries = {t: e for t, e in entries.items() if t in valid_terms}

    # Add commons-page-only entries the matrix didn't surface (compound
    # comparison pages like `unhoused-homeless`, or terms whose matrix
    # keyword-scan hits were filtered out like `chicanx`). These need to
    # be browsable in the glossary even when the matrix doesn't list them.
    for commons_slug in commons_lookup:
        # Matrix uses spaces; normalize back the other direction.
        term = commons_slug.replace("-", " ")
        if term in entries or commons_slug in entries:
            continue
        # Read the term file's display name + guidance to synthesize a
        # minimal entry. Source-count is derived from guidance entries.
        path = TERMS_DIR / f"{commons_slug}.md"
        fm = _parse_frontmatter(path)
        display = fm.get("term", commons_slug.replace("-", " ").title())
        # Count guidance entries by parsing the file for `- org:` lines.
        # This is approximate but matches what the commons page shows.
        text = path.read_text(encoding="utf-8")
        guidance_count = len(re.findall(r"^\s*-\s+org:\s*", text, re.MULTILINE))
        entries[term] = {
            "term": term,
            "display": display,
            "source_count": guidance_count,
            "commons_slug": commons_slug,
            "sources": [],  # full source list lives on the commons page
        }
        bucket = _letter_bucket(term)
        by_letter.setdefault(bucket, []).append(term)
        coverage_histogram[guidance_count] = (
            coverage_histogram.get(guidance_count, 0) + 1
        )

    # Sort each letter bucket alphabetically.
    for letter in by_letter:
        by_letter[letter].sort()

    stats = {
        "total_terms": len(entries),
        "commons_terms": sum(1 for e in entries.values() if e["commons_slug"]),
        "long_tail_terms": sum(1 for e in entries.values() if not e["commons_slug"]),
        "by_coverage": {str(k): v for k, v in sorted(coverage_histogram.items())},
    }

    # Sort letter keys: A-Z then '#'.
    ordered_letters: dict[str, list[str]] = {}
    for letter in "abcdefghijklmnopqrstuvwxyz#":
        if letter in by_letter:
            ordered_letters[letter] = by_letter[letter]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stats": stats,
        "by_letter": ordered_letters,
        "entries": dict(sorted(entries.items())),
    }


def main() -> int:
    data = build_index()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    stats = data["stats"]
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    print(
        f"  total: {stats['total_terms']} | commons: {stats['commons_terms']} | "
        f"long-tail: {stats['long_tail_terms']}"
    )
    print(f"  coverage histogram: {stats['by_coverage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
