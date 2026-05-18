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


def _build_org_lookup() -> dict[str, dict[str, str]]:
    """Map source_slug → {org, year, source_url}."""
    lookup: dict[str, dict[str, str]] = {}
    for path in sorted(SOURCES_DIR.glob("*.md")):
        fm = _parse_frontmatter(path)
        slug = path.stem
        # Many source pages use a per-edition slug; the matrix uses the
        # same slug, so we key on filename stem directly. Fall back to
        # the frontmatter org_slug when the filename has been renamed.
        org = fm.get("org", slug.replace("-", " ").title())
        year = fm.get("year", "")
        url = fm.get("source_url", "")
        if url == "null":
            url = ""
        lookup[slug] = {"org": org, "year": year, "source_url": url}
        # Also register the org_slug from frontmatter in case some matrix
        # rows use the short slug.
        org_slug_fm = fm.get("org_slug")
        if org_slug_fm and org_slug_fm not in lookup:
            lookup[org_slug_fm] = lookup[slug]
    return lookup


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

    org_lookup = _build_org_lookup()
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
            excerpt = _truncate(row.get("excerpt") or "")
            org_meta = org_lookup.get(source_slug, {})
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
                    "source_slug": source_slug,
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
        # Heuristic: a single-character term should always be dropped.
        # An ultra-short term (≤2 chars) is only kept when it has ≥3
        # sources — those are real glossary entries (e.g., 'b.c' for
        # 'before Christ'/'before common era').
        if len(term) <= 2 and entry["source_count"] < 3:
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
