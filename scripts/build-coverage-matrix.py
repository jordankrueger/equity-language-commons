#!/usr/bin/env python3
"""
build-coverage-matrix.py — Phase 2.5b tooling.

Walks every source markdown under source-guides/ + source-guides/discovered/,
extracts term entries from sources with clean glossary structure, then keyword-
scans the narrative sources against that term universe. Produces:

  notes/term-coverage-matrix.csv  — one row per (term, source) pair
  notes/term-coverage-matrix.md   — ranking by cross-source coverage, with
                                    indexed terms (site/src/content/terms/) marked

Use the .md ranking to pick the next Phase 3 batch: filter out indexed terms,
take the top N by coverage. See ROADMAP.md "Phase 2.5b" for context.

Stdlib only — no pip installs needed.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from lib import PROJECT_ROOT, SOURCE_ROOTS, normalize_term

# ---------- paths ----------

INDEXED_TERMS_DIR = PROJECT_ROOT / "site" / "src" / "content" / "terms"
NOTES_DIR = PROJECT_ROOT / "notes"
CSV_OUT = NOTES_DIR / "term-coverage-matrix.csv"
MD_OUT = NOTES_DIR / "term-coverage-matrix.md"

# ---------- excluded sources ----------

# Out-of-scope brand-identity guides + non-glossary AAJA/GLAAD landing-page
# scrapes that contributed nothing in the structure survey. The script will
# still skip these gracefully if they're in the corpus, just won't waste cycles
# pretending to scan them.
NON_TERM_SOURCES = {
    "yli-styleguide-2020",                  # brand identity, out-of-scope per MANIFEST
    "stand-earth-identity-2019-06",         # brand voice, out-of-scope per MANIFEST
    "aaja-style-guide-2024-08",             # press-release archive, not the actual style guide
    "glaad-media-reference-2022-11",        # blog landing page, not the actual reference guide
    "conscious-style-guide-index-2026-04",  # meta-index of other guides, not a glossary
    "color-of-change-narrative-index-2024", # site index, not a glossary
    "radicalcopyeditor-index-2026-04",      # blog index, not a glossary
}

# ---------- term normalization ----------

_MULTISPACE = re.compile(r'\s+')

# Bare-article fragments that an alias-splitter on commas can produce — e.g.
# DSG’s inverted glossary form "Great Migration, the" splits to ["Great
# Migration", "the"], and the "the" is junk. Same for "X, a" / "X, an".
_ARTICLE_FRAGMENTS = {"the", "a", "an"}

# Stopwords + grammatical scaffolding that should never appear as a term, no
# matter what extractor picked them up. Single-word and very short.
_UNIVERSE_STOPWORDS = {
    "the", "a", "an", "or", "and", "but", "to", "of", "in", "on", "at", "by",
    "for", "with", "as", "is", "are", "was", "were", "be", "been", "being",
    "it", "its", "this", "that", "these", "those", "if", "when", "where",
    "how", "why", "no", "not", "do", "does", "did", "done", "from", "into",
    "over", "than", "then",
}

# Common-English single-word terms that are LEGITIMATELY in some glossaries
# (e.g., DSG has entries for "family", "out", "American") but whose keyword
# scan in narrative sources produces almost entirely false positives — every
# guide mentions "family" because every guide is about people. Glossary hits
# from structured extractors are still recorded; keyword scan is skipped.
KEYWORD_SCAN_BLOCKLIST = {
    "american", "family", "out", "two", "central", "chief", "special",
    "older", "partner", "senior", "people", "covering", "acting", "treatment",
    "ethnic",  # too easily matched as part of "ethnicity" / "ethnically"
    "nation",  # matches "nationally", "international", etc.
    "race",    # matches "race-baiting", "horse race", etc.
    "male",    # matches "female", "Smalltalk", etc.
    "sex",     # matches "Sussex", "sextant", "essex" etc.
    "asia",    # matches "Asian-American" already covered by "asian"
    "blind",   # often used metaphorically (color-blind, blind spot) not as a term
}


def split_term_aliases(raw: str) -> list[str]:
    """A heading like "trans male, trans female" or "groomer, grooming" lists
    related terms in one entry. Split on commas / slashes / parenthetical
    qualifiers and treat each as its own term, normalized. Drops fragments
    that are bare articles (DSG inverted form: "Great Migration, the")."""
    raw = re.sub(r"\([^)]*\)", "", raw)  # drop "(n.)", "(adj.)" etc.
    parts = re.split(r"[,/]| or ", raw)
    out = []
    for p in parts:
        n = normalize_term(p)
        if not n or n in _ARTICLE_FRAGMENTS:
            continue
        out.append(n)
    return out


# ---------- glossary extractors ----------

@dataclass
class TermHit:
    term: str               # normalized
    source_slug: str
    line: int
    excerpt: str            # first ~120 chars of the surrounding line
    extraction: str         # 'glossary' or 'keyword'
    has_avoid_marker: bool
    has_capitalization_rule: bool


AVOID_PAT = re.compile(
    r"\b(avoid|do not use|don'?t use|never use|outdated|offensive|slur|"
    r"non-preferred|deprecated|harmful)\b",
    re.IGNORECASE,
)
CAP_PAT = re.compile(
    r"\b(capitali[sz]e|lower\s?case|upper\s?case|capital [A-Z]|cap [A-Z])\b",
    re.IGNORECASE,
)


def _short(line: str, limit: int = 120) -> str:
    return _MULTISPACE.sub(" ", line.strip())[:limit]


def extract_tja(slug: str, text: str) -> list[TermHit]:
    """### [term](#anchor){.header-anchor} {#anchor updated="DATE" ...}"""
    pat = re.compile(r"^###\s+\[([^\]]+)\]\(#[^)]+\)\{\.header-anchor\}")
    return _emit_glossary_hits(slug, text, pat, lookahead=4)


def extract_dsg(slug: str, text: str) -> list[TermHit]:
    """- ["term"](URL){.glossaryLink .cmtt_Category}"""
    pat = re.compile(r"^- \[\\?\"?([^\"\\\]]+?)\"?\\?\]\([^)]+\)\{\.glossaryLink")
    return _emit_glossary_hits(slug, text, pat, lookahead=0)


def extract_ncdj(slug: str, text: str) -> list[TermHit]:
    """### [term]{.highlight-gold}"""
    pat = re.compile(r"^###\s+\[([^\]]+)\]\{\.highlight-gold\}")
    return _emit_glossary_hits(slug, text, pat, lookahead=10)


def extract_hrc(slug: str, text: str) -> list[TermHit]:
    """**term \\|** definition  (pipe-separated definition list)"""
    pat = re.compile(r"^\*\*([^*]+?)\s*\\\|\*\*\s+(.+)$")
    return _emit_glossary_hits(slug, text, pat, lookahead=0, definition_in_match=True)


def extract_nlgja(slug: str, text: str) -> list[TermHit]:
    """**Term\\**  (bold with trailing backslash before newline)"""
    pat = re.compile(r"^\*\*([^*]+?)\\\*\*\s*$")
    return _emit_glossary_hits(slug, text, pat, lookahead=3)


# Radical Copyeditor's guide uses `**Term:** definition` for actual entries,
# but the same pattern matches file metadata (`**Source:**`, `**Author:**`,
# `**Published:**`, `**Archived:**`) and section meta (`**How to use this
# guide:**`). Drop these by name.
_RADICALCOPYEDITOR_META = {
    "source", "author", "published", "archived",
    "how to use this guide", "how not to use this guide",
}


def extract_radicalcopyeditor_trans(slug: str, text: str) -> list[TermHit]:
    """**Term:** definition"""
    pat = re.compile(r"^\*\*([^:*]{2,80}?):\*\*\s+(.+)$")
    hits = _emit_glossary_hits(slug, text, pat, lookahead=0, definition_in_match=True)
    return [h for h in hits if h.term not in _RADICALCOPYEDITOR_META]


def _emit_glossary_hits(
    slug: str,
    text: str,
    pattern: re.Pattern,
    lookahead: int,
    definition_in_match: bool = False,
) -> list[TermHit]:
    """Common emit loop for structured-glossary extractors. lookahead controls
    how many subsequent lines to scan for avoid/capitalization markers."""
    hits: list[TermHit] = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = pattern.match(line)
        if not m:
            continue
        raw_term = m.group(1)
        if definition_in_match and m.lastindex and m.lastindex >= 2:
            context = line
        else:
            window_end = min(len(lines), i + 1 + lookahead)
            context = " ".join(lines[i:window_end])
        for alias in split_term_aliases(raw_term):
            if not _is_plausible_term(alias):
                continue
            hits.append(TermHit(
                term=alias,
                source_slug=slug,
                line=i + 1,
                excerpt=_short(line),
                extraction="glossary",
                has_avoid_marker=bool(AVOID_PAT.search(context)),
                has_capitalization_rule=bool(CAP_PAT.search(context)),
            ))
    return hits


def _is_plausible_term(t: str) -> bool:
    """Drop obvious junk: too short, all numbers, anchor names, stopwords."""
    if len(t) < 2:
        return False
    if len(t) > 80:
        return False
    if not re.search(r"[a-z]", t):
        return False
    if t.startswith(("section-", "subsection-", "appendix-")):
        return False
    if t in _UNIVERSE_STOPWORDS:
        return False
    return True


EXTRACTORS: dict[str, Callable[[str, str], list[TermHit]]] = {
    "tja-stylebook-2026-01": extract_tja,
    "diversity-style-guide-2023-11": extract_dsg,
    "ncdj-disability-style-guide-2021": extract_ncdj,
    "hrc-glossary-2023-05": extract_hrc,
    "nlgja-stylebook-lgbtq-2025-06": extract_nlgja,
    "radicalcopyeditor-trans-style-guide-2017": extract_radicalcopyeditor_trans,
}


# ---------- keyword scan (narrative sources) ----------

def keyword_scan(slug: str, text: str, term_universe: Iterable[str]) -> list[TermHit]:
    """For each term in the universe, find its first occurrence in this source.
    Skips KEYWORD_SCAN_BLOCKLIST (common single-word terms that produce mostly
    noise in narrative scans — glossary hits still count).
    Hyphens in terms also match the spaced form: 'african-american' matches
    'African American'. Word-boundary matching to avoid 'urban'→'suburban'."""
    # Strip the extracted-text header (lines 1–6 of every PDF-extracted .md)
    # so the scan doesn't hit "source" / "extracted" in our own footers.
    body_offset = 0
    if text.startswith("<!--"):
        end = text.find("-->")
        if end > 0:
            body_offset = text.count("\n", 0, end + 3)
            text = text[end + 3:]
    lines = text.splitlines()
    hits: list[TermHit] = []
    text_lower = text.lower()
    for term in term_universe:
        if term in KEYWORD_SCAN_BLOCKLIST:
            continue
        # Build a search variant set so hyphen/space forms collide.
        variants = {term}
        if " " in term:
            variants.add(term.replace(" ", "-"))
        if "-" in term:
            variants.add(term.replace("-", " "))
        any_pat_parts = []
        for v in variants:
            if " " in v or "-" in v:
                any_pat_parts.append(r"\b" + re.escape(v) + r"\b")
            else:
                any_pat_parts.append(r"\b" + re.escape(v) + r"s?\b")
        needle = re.compile("|".join(any_pat_parts), re.IGNORECASE)
        if not needle.search(text_lower):
            continue
        for i, line in enumerate(lines):
            if needle.search(line):
                window = " ".join(lines[i:min(len(lines), i + 3)])
                hits.append(TermHit(
                    term=term,
                    source_slug=slug,
                    line=i + 1 + body_offset,
                    excerpt=_short(line),
                    extraction="keyword",
                    has_avoid_marker=bool(AVOID_PAT.search(window)),
                    has_capitalization_rule=bool(CAP_PAT.search(window)),
                ))
                break
    return hits


# ---------- corpus walk ----------

def list_source_files() -> list[Path]:
    files: list[Path] = []
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for f in sorted(root.glob("*.md")):
            if f.name == "MANIFEST.md":
                continue
            slug = f.stem
            if slug in NON_TERM_SOURCES:
                continue
            files.append(f)
    return files


def list_indexed_terms() -> set[str]:
    """Indexed-term filenames are slug-form (african-american.md); the universe
    uses normalized form (african american). Normalize on the way in."""
    if not INDEXED_TERMS_DIR.exists():
        return set()
    return {normalize_term(p.stem) for p in INDEXED_TERMS_DIR.glob("*.md")}


# ---------- main ----------

def main() -> int:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    sources = list_source_files()
    indexed = list_indexed_terms()
    print(f"scanning {len(sources)} sources; {len(indexed)} terms already indexed", file=sys.stderr)

    all_hits: list[TermHit] = []
    glossary_terms: set[str] = set()
    per_source_counts: dict[str, int] = {}

    # Pass 1: structured extractors → seed the term universe
    for path in sources:
        slug = path.stem
        if slug not in EXTRACTORS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = EXTRACTORS[slug](slug, text)
        # Dedupe within a source (one row per term).
        seen = set()
        deduped = []
        for h in hits:
            if h.term in seen:
                continue
            seen.add(h.term)
            deduped.append(h)
            glossary_terms.add(h.term)
        all_hits.extend(deduped)
        per_source_counts[slug] = len(deduped)
        print(f"  glossary  {slug}: {len(deduped)} terms", file=sys.stderr)

    # Indexed terms are part of the universe too (so we see which narrative
    # sources mention already-indexed terms even if no glossary defines them).
    term_universe = sorted(glossary_terms | indexed)
    print(f"\nterm universe: {len(term_universe)} unique terms\n", file=sys.stderr)

    # Pass 2: keyword scan over non-glossary sources
    for path in sources:
        slug = path.stem
        if slug in EXTRACTORS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = keyword_scan(slug, text, term_universe)
        all_hits.extend(hits)
        per_source_counts[slug] = len(hits)
        print(f"  keyword   {slug}: {len(hits)} term hits", file=sys.stderr)

    # ---------- write CSV ----------
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "term_normalized", "source_slug", "line", "excerpt",
            "extraction_method", "has_avoid_marker", "has_capitalization_rule",
        ])
        for h in sorted(all_hits, key=lambda x: (x.term, x.source_slug)):
            w.writerow([
                h.term, h.source_slug, h.line, h.excerpt,
                h.extraction,
                "yes" if h.has_avoid_marker else "no",
                "yes" if h.has_capitalization_rule else "no",
            ])

    # ---------- write ranking MD ----------
    coverage: dict[str, set[str]] = defaultdict(set)
    for h in all_hits:
        coverage[h.term].add(h.source_slug)

    ranked = sorted(coverage.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    with MD_OUT.open("w", encoding="utf-8") as fh:
        fh.write("# Term Coverage Matrix\n\n")
        fh.write(
            "Generated by `scripts/build-coverage-matrix.py`. One row per term, "
            "showing how many sources cover it. Use this to pick the next Phase 3 "
            "batch — filter out indexed terms (marked ✅) and take the top N by "
            "coverage. Full per-source detail in `term-coverage-matrix.csv`.\n\n"
            "**Compound-slug caveat:** Indexed term files like "
            "`unhoused-homeless.md` represent comparison pages covering two "
            "related terms; the matrix can't match those compound slugs as a "
            "single phrase. Check `unhoused` and `homeless` separately in the "
            "full ranking below.\n\n"
        )
        fh.write(f"- Sources scanned: **{len(sources)}**\n")
        fh.write(f"- Unique terms found: **{len(coverage)}**\n")
        fh.write(f"- Terms already indexed: **{sum(1 for t in coverage if t in indexed)}** / {len(indexed)}\n\n")

        fh.write("## Top 50 candidates (excluding indexed)\n\n")
        fh.write("| Coverage | Term | Sources |\n|---|---|---|\n")
        shown = 0
        for term, sources_set in ranked:
            if term in indexed:
                continue
            if shown >= 50:
                break
            fh.write(f"| {len(sources_set)} | `{term}` | {', '.join(sorted(sources_set))} |\n")
            shown += 1

        fh.write("\n## Indexed terms — current source coverage\n\n")
        fh.write("| Coverage | Term | Sources |\n|---|---|---|\n")
        for term in sorted(indexed):
            sources_set = coverage.get(term, set())
            mark = "✅" if sources_set else "⚠ no hits"
            fh.write(f"| {len(sources_set)} {mark} | `{term}` | {', '.join(sorted(sources_set)) or '—'} |\n")

        fh.write("\n## Full ranking\n\n")
        fh.write("| Coverage | Term | Indexed? | Sources |\n|---|---|---|---|\n")
        for term, sources_set in ranked:
            mark = "✅" if term in indexed else ""
            fh.write(f"| {len(sources_set)} | `{term}` | {mark} | {', '.join(sorted(sources_set))} |\n")

    print(f"\nwrote {CSV_OUT.relative_to(PROJECT_ROOT)} ({len(all_hits)} rows)", file=sys.stderr)
    print(f"wrote {MD_OUT.relative_to(PROJECT_ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
