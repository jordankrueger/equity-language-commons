#!/usr/bin/env python3
"""
scaffold-term.py — Phase 2.6 tooling.

Generates a near-complete term .md from the coverage matrix. For each source
that mentions the term:
  - Reads the source file, extracts ~8 lines of context around the hit
  - Classifies the recommendation enum from context patterns
  - Looks up org/year/source_url/local_archive from the matching source page
  - Emits a guidance[] entry with confidence: PARTIAL

The output is meant to be reviewed by a human/LLM: tighten the auto-extracted
quotes against the PDF, fix any mis-classified recommendations, then write
the synthesis paragraph + audience_notes + related_terms (the genuinely-
judgment parts).

Target: 8–12 min/term of post-scaffold work, vs ~30–40 min raw.

Usage:
  ./scripts/scaffold-term.py tribe
  ./scripts/scaffold-term.py illegal-immigrant --force

Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from lib import (
    PROJECT_ROOT,
    build_pdf_to_md_index,
    normalize_term,
    parse_frontmatter_scalars,
    strip_yaml_string,
    yaml_escape,
)

MATRIX_CSV = PROJECT_ROOT / "notes" / "term-coverage-matrix.csv"
SOURCES_DIR = PROJECT_ROOT / "site" / "src" / "content" / "sources"
TERMS_DIR = PROJECT_ROOT / "site" / "src" / "content" / "terms"

# Context window read around each hit line, before truncation.
CONTEXT_LINES = 10
# Quote truncation budget — anything longer should be hand-tightened.
MAX_QUOTE_CHARS = 400

# Markdown / pandoc artifacts that appear in our web-scraped sources but
# should never appear in a published quote. Stripped before truncation so
# we don't waste budget on noise.
_QUOTE_NOISE = [
    re.compile(r":::+\s*[a-zA-Z_-]*\s*"),                   # pandoc fenced divs
    re.compile(r"\{[#.][^}]*\}"),                           # pandoc spans/IDs {#anchor} {.class}
    re.compile(r"\\\s*\("),                                  # stray "\(" from escaped parens
    re.compile(r"ūū\s*"),                                    # encoding glitches from PDF bullets
    re.compile(r"[•◆●]\s*"),                                # bullet characters
    re.compile(r"\\\\"),                                    # double backslashes from CSV escaping
    re.compile(r"\\(?=[^\"])"),                             # lone backslashes not preceding a quote
]


def _clean_quote_artifacts(s: str) -> str:
    for pat in _QUOTE_NOISE:
        s = pat.sub(" ", s)
    return _MULTISPACE.sub(" ", s).strip()

# ---------- recommendation classifier ----------

# Patterns evaluated in order; first match wins.
REC_PATTERNS = [
    ("avoid",
     re.compile(r"\b(avoid|do not use|don'?t use|never use|outdated|offensive|"
                r"slur|harmful|deprecated|inaccurate|inappropriate|"
                r"problematic)\b", re.I)),
    ("non-preferred",
     re.compile(r"\b(non-preferred|not preferred|less preferred|secondary "
                r"choice|fallback)\b", re.I)),
    ("reclaimed-in-community",
     re.compile(r"\b(reclaim(?:ed|ing)?|in-?group only|community-internal|"
                r"used by community)\b", re.I)),
    ("contested",
     re.compile(r"\b(contested|disputed|debate|controversial|controversy|"
                r"no consensus|divided)\b", re.I)),
    ("evolving",
     re.compile(r"\b(evolving|shifting|changing|emerging|in flux)\b", re.I)),
    ("use-with-care",
     re.compile(r"\b(with care|cautiously|in (?:some|certain) contexts|"
                r"depending on context|consider whether|use sparingly|"
                r"qualifier|caveat)\b", re.I)),
    ("use",
     re.compile(r"\b(preferred|acceptable|is the standard|appropriate term|"
                r"recommended)\b", re.I)),
]
DEFAULT_REC = "use-with-care"

_MULTISPACE = re.compile(r'\s+')


def slugify(term: str) -> str:
    return re.sub(r"\s+", "-", normalize_term(term))


def display_form(term_normalized: str) -> str:
    """Best-effort Title Case for the `term:` frontmatter field — LLM will
    fix acronyms (BIPOC, POC) and special casing."""
    return " ".join(w.capitalize() for w in term_normalized.split())


# ---------- source-page metadata ----------

@dataclass
class SourcePage:
    page_slug: str
    org: str
    org_slug: str
    year: int
    source_url: str | None
    local_archive: str | None
    archive_md_path: Path | None      # the .md file the matrix scanned


def load_source_pages() -> dict[str, SourcePage]:
    """Returns: matrix_source_slug → SourcePage.
    Builds the .md ↔ source-page mapping by reading the extract-pdfs.sh header
    of each generated markdown."""
    pdf_to_md = build_pdf_to_md_index()
    pages: dict[str, SourcePage] = {}
    for f in sorted(SOURCES_DIR.glob("*.md")):
        fm = parse_frontmatter_scalars(f.read_text(encoding="utf-8"))
        archive = strip_yaml_string(fm.get("local_archive", ""))
        if not archive:
            continue
        arch_path = Path(archive)
        # Resolve to the .md the matrix scanned.
        if arch_path.suffix.lower() == ".md":
            md_path = PROJECT_ROOT / arch_path
        elif arch_path.suffix.lower() == ".pdf":
            md_path = pdf_to_md.get(arch_path.name)
        else:
            md_path = None
        if not md_path or not md_path.exists():
            continue
        matrix_slug = md_path.stem
        year_raw = strip_yaml_string(fm.get("year", "0"))
        page = SourcePage(
            page_slug=f.stem,
            org=strip_yaml_string(fm.get("org", "")),
            org_slug=strip_yaml_string(fm.get("org_slug", "")),
            year=int(year_raw) if year_raw.isdigit() else 0,
            source_url=strip_yaml_string(fm.get("source_url", "")) or None,
            local_archive=archive,
            archive_md_path=md_path,
        )
        pages[matrix_slug] = page
    return pages


# ---------- matrix loading ----------

def load_matrix_for(term_norm: str) -> list[dict]:
    rows = []
    with MATRIX_CSV.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if r["term_normalized"] == term_norm:
                rows.append(r)
    return rows


# ---------- excerpt extraction ----------

@dataclass
class Excerpt:
    source: SourcePage
    line: int
    quote: str
    quote_loc: str
    recommendation: str
    extraction_method: str
    notes: list[str] = field(default_factory=list)


def extract_excerpt(source: SourcePage, matrix_row: dict) -> Excerpt | None:
    md_path = source.archive_md_path
    if not md_path or not md_path.exists():
        return None
    lines = md_path.read_text(encoding="utf-8").splitlines()
    hit_line = int(matrix_row["line"])
    # Read CONTEXT_LINES centered roughly on the hit, biased forward (most
    # "use X not Y" guidance unfolds after the term mention).
    start = max(0, hit_line - 1 - CONTEXT_LINES // 3)
    end = min(len(lines), hit_line + (CONTEXT_LINES * 2) // 3)
    window = lines[start:end]

    # Drop blank lines + collapse whitespace.
    cleaned = [ln.strip() for ln in window if ln.strip()]
    quote = _MULTISPACE.sub(" ", " ".join(cleaned)).strip()
    quote = _clean_quote_artifacts(quote)

    # Truncate at a word boundary near MAX_QUOTE_CHARS.
    if len(quote) > MAX_QUOTE_CHARS:
        cut = quote[:MAX_QUOTE_CHARS].rsplit(" ", 1)[0]
        quote = cut + "…"

    # Classify on a slightly wider window (5 lines around the hit) for
    # context phrases that often appear before/after the term.
    cl_start = max(0, hit_line - 1 - 5)
    cl_end = min(len(lines), hit_line + 5)
    classify_window = " ".join(lines[cl_start:cl_end])
    rec = DEFAULT_REC
    for label, pat in REC_PATTERNS:
        if pat.search(classify_window):
            rec = label
            break

    notes = []
    if matrix_row["has_avoid_marker"] == "yes" and rec not in ("avoid", "non-preferred"):
        notes.append(f"matrix flagged avoid-marker but classifier picked {rec!r} — review")
    if matrix_row["extraction_method"] == "keyword" and rec == DEFAULT_REC:
        notes.append("keyword-scan hit + no recommendation marker — may not be a real entry")

    return Excerpt(
        source=source,
        line=hit_line,
        quote=quote,
        quote_loc=f"Line {hit_line}",
        recommendation=rec,
        extraction_method=matrix_row["extraction_method"],
        notes=notes,
    )


# ---------- YAML emitter ----------

def render_guidance_entries(excerpts: list[Excerpt]) -> str:
    out = []
    for ex in excerpts:
        out.append(f"  - org: {yaml_escape(ex.source.org)}")
        out.append(f'    org_slug: "{ex.source.org_slug}"')
        out.append(f"    year: {ex.source.year}")
        out.append("    entry_updated: null")
        if ex.source.source_url:
            out.append(f"    source_url: {yaml_escape(ex.source.source_url)}")
        else:
            out.append("    source_url: null")
        if ex.source.local_archive:
            out.append(f"    local_archive: {yaml_escape(ex.source.local_archive)}")
        else:
            out.append("    local_archive: null")
        out.append(f'    recommendation: "{ex.recommendation}"')
        out.append("    derived_from: []")
        out.append(f"    quote: {yaml_escape(ex.quote)}")
        out.append(f"    quote_loc: {yaml_escape(ex.quote_loc)}")
        out.append('    paraphrase: ""  # TODO: 1-3 sentence paraphrase capturing the source\'s position')
        out.append('    confidence: "PARTIAL"  # TODO: bump to VERIFIED after PDF check')
    return "\n".join(out)


def build_term_file(slug: str, display: str, excerpts: list[Excerpt], today: str,
                    extraction_notes: list[str]) -> str:
    notes_block = ""
    if extraction_notes:
        notes_block = (
            "<!-- scaffolder notes (delete after review):\n"
            + "".join(f"  · {n}\n" for n in extraction_notes)
            + "-->\n"
        )

    return f"""---
term: {yaml_escape(display)}
slug: "{slug}"
aliases: []
related_terms: []  # TODO: cross-link to related entries (alternative-form / gendered-form / overlapping-but-distinct / subset-identity / umbrella-for)
categories: []     # TODO: e.g., "race-ethnicity", "indigenous-tribal-sovereignty"
tags: []           # TODO: e.g., "self-id-required", "capitalization-rule", "evolving-usage"
guidance:
{render_guidance_entries(excerpts)}
context_data: []
external_references: []
methodological_context: []
audience_notes: []  # TODO: 1-2 audience-specific notes (journalist vs activist vs internal-comms framing)
last_reviewed: {today}
created: {today}
contributors:
  - "jordan"
stub: true  # TODO: remove once synthesis + audience_notes are written
---
{notes_block}
## Synthesis

<!-- TODO: 2-3 paragraphs distilling the cross-source picture. Where do
sources agree? Where do they diverge? What's the chronology of the term's
treatment? Lead with the consensus where one exists, then map the dissent. -->

## Audience notes

<!-- TODO: 1-2 audience-specific cautions. E.g., journalist-vs-activist
framing, geographic variations, generational shifts in usage. -->
"""


# ---------- main ----------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("slug", help="Term slug or display form (e.g., 'tribe', 'illegal-immigrant')")
    parser.add_argument("--force", action="store_true", help="overwrite existing term file")
    args = parser.parse_args()

    term_norm = normalize_term(args.slug)
    slug = slugify(args.slug)
    display = display_form(term_norm)

    out_path = TERMS_DIR / f"{slug}.md"
    if out_path.exists() and not args.force:
        print(f"⚠ {out_path.relative_to(PROJECT_ROOT)} exists. Use --force to overwrite.",
              file=sys.stderr)
        return 1

    matrix_rows = load_matrix_for(term_norm)
    if not matrix_rows:
        print(f"no matrix hits for term {term_norm!r}", file=sys.stderr)
        return 1

    print(f"term: {term_norm!r} → {slug}.md  ({len(matrix_rows)} matrix hits)", file=sys.stderr)

    pages = load_source_pages()
    excerpts: list[Excerpt] = []
    skipped: list[tuple[str, str]] = []
    extraction_notes: list[str] = []

    for row in matrix_rows:
        src_slug = row["source_slug"]
        page = pages.get(src_slug)
        if not page:
            skipped.append((src_slug, "no matching source page — create site/src/content/sources/<slug>.md to enable"))
            continue
        ex = extract_excerpt(page, row)
        if not ex:
            skipped.append((src_slug, "extraction failed (file missing or unreadable)"))
            continue
        excerpts.append(ex)
        print(f"  ok    {src_slug:50s} L{row['line']:>5s}  rec={ex.recommendation:25s} method={ex.extraction_method}",
              file=sys.stderr)
        for note in ex.notes:
            extraction_notes.append(f"{src_slug}: {note}")
            print(f"        · {note}", file=sys.stderr)

    for src_slug, reason in skipped:
        extraction_notes.append(f"{src_slug}: {reason}")
        print(f"  skip  {src_slug:50s} {reason}", file=sys.stderr)

    if not excerpts:
        print("\nno usable excerpts — aborting", file=sys.stderr)
        return 1

    excerpts.sort(key=lambda e: e.source.year)

    today = date.today().isoformat()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        build_term_file(slug, display, excerpts, today, extraction_notes),
        encoding="utf-8",
    )

    print(f"\nwrote {out_path.relative_to(PROJECT_ROOT)} with {len(excerpts)} guidance entries",
          file=sys.stderr)
    if skipped:
        print(f"({len(skipped)} sources skipped — see notes block in the file)", file=sys.stderr)
    print("\nnext: review scaffold → tighten quotes against PDFs → fix mis-classified "
          "recommendations → write synthesis + audience_notes → remove stub: true",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
