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
OVERRIDES_YML = ROOT / "notes" / "curated-glossary-overrides.yml"

# Precedence for picking a curated term's canonical source among its
# structured-glossary ("glossary" extraction_method) sources. Most
# comprehensive aggregator first, then domain-specific guides. Matched
# against the resolved source page-slug with startswith(), so the short
# form here matches both "hrc" and "hrc-glossary-2023-05".
CANONICAL_PRECEDENCE = [
    "diversity-style-guide",
    "ncdj",
    "hrc",
    "nlgja",
    "tja",
    "radical-copyeditor",
]

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
            "live_status": fm.get("live_status", "live"),
            "local_archive": fm.get("local_archive", ""),
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


def _build_commons_lookup() -> tuple[dict[str, str], dict[str, str]]:
    """Map term-slug → commons-page-slug, split by publication state.

    Returns:
        (published, stub_display)
        - published: slug → slug for term pages with `stub` falsy. These
          are the `full`-tier pages that get a /terms/<slug>/ link.
        - stub_display: slug → display-term for `stub:true` pages. These
          are NOT full pages (they fall to `verified-hold` via the
          overrides file); the display name is kept so the glossary can
          render it nicely.
    """
    published: dict[str, str] = {}
    stub_display: dict[str, str] = {}
    alias_lists: dict[str, list[str]] = {}
    alias_block_re = re.compile(r"^aliases:\n((?:[ \t]+-[ \t]+.*\n)+)", re.M)
    for path in sorted(TERMS_DIR.glob("*.md")):
        slug = path.stem
        fm = _parse_frontmatter(path)
        # The stub line often carries an inline comment
        # ("stub: true  # TODO ..."), so match on the leading token.
        is_stub = str(fm.get("stub", "")).strip().lower().startswith("true")
        if is_stub:
            stub_display[slug] = fm.get("term", slug.replace("-", " ").title())
        else:
            published[slug] = slug
            text = path.read_text(encoding="utf-8")
            found: list[str] = []
            m = alias_block_re.search(text)
            if m:
                found += [
                    a.strip().strip("\"'")
                    for a in re.findall(r"-\s+(.*)", m.group(1))
                ]
            # inline form: aliases: ["a", "b"]
            mi = re.search(r"^aliases:[ \t]*\[(.*)\]", text, re.M)
            if mi:
                found += [
                    a.strip().strip("\"'")
                    for a in mi.group(1).split(",")
                    if a.strip().strip("\"'")
                ]
            if found:
                alias_lists[slug] = found
    # Alias resolution: a glossary term matching a published page's alias
    # links to that page (e.g. "daca" → /terms/dreamer/, "autistic" →
    # /terms/autism/). Page slugs win over aliases; first alias wins ties.
    for slug, aliases in alias_lists.items():
        for alias in aliases:
            alias_slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", alias.lower())).strip("-")
            if alias_slug and alias_slug not in published:
                published[alias_slug] = slug
    return published, stub_display


def _load_overrides() -> dict[str, dict[str, str]]:
    """Parse notes/curated-glossary-overrides.yml with a minimal block
    parser (no PyYAML). Expects flat structure: a top-level term key
    (no indent, trailing colon) followed by indented `key: "value"`
    scalar fields. Returns term → {canonical_source_slug, excerpt, note}.
    """
    overrides: dict[str, dict[str, str]] = {}
    if not OVERRIDES_YML.exists():
        return overrides
    current: Optional[str] = None
    for raw_line in OVERRIDES_YML.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line[0].isspace():
            # Top-level term key: "jew:"
            key = raw_line.split(":", 1)[0].strip()
            if key:
                current = key.lower()
                overrides[current] = {}
            continue
        if current is None or ":" not in raw_line:
            continue
        field, _, value = raw_line.strip().partition(":")
        value = value.strip()
        # Strip a single matching pair of surrounding quotes, then
        # unescape the \" sequences the YAML used inside them.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        value = value.replace('\\"', '"')
        overrides[current][field.strip()] = value
    return overrides


def _resolve_canonical(
    source_slug: str,
    exact: dict[str, dict[str, str]],
    prefix: list[tuple[str, dict[str, str]]],
) -> tuple[Optional[dict], bool]:
    """Resolve a canonical source slug (from an override or a curated
    pick) to a renderable canonical_source object + a resolved flag.

    Returns (canonical_source | None, resolved). `resolved` is False when
    the slug matches no real source page — the caller treats that as an
    unresolved-override error (no broken /sources/ link emitted).
    """
    resolved = source_slug in exact or any(
        source_slug == org_slug or source_slug.startswith(org_slug + "-")
        for org_slug, _ in prefix
    )
    if not resolved:
        return None, False
    meta = _resolve_source(source_slug, exact, prefix)
    page_slug = meta.get("page_slug", source_slug)
    canonical = {
        "source_slug": page_slug,
        "page_slug": page_slug,
        "org": meta.get("org", source_slug),
        "year": meta.get("year", ""),
        "source_page_url": f"/sources/{page_slug}/",
        "live_status": meta.get("live_status", "live"),
        "local_archive": meta.get("local_archive", ""),
    }
    return canonical, True


def _pick_curated_canonical(
    sources: list[dict],
    exact: dict[str, dict[str, str]],
    prefix: list[tuple[str, dict[str, str]]],
) -> tuple[Optional[dict], str]:
    """Among a term's structured-glossary sources, pick the canonical one
    by CANONICAL_PRECEDENCE. Returns (canonical_source | None, excerpt).
    None when the term has no `glossary`-method source.
    """
    glossary_sources = [
        s for s in sources if s.get("extraction_method") == "glossary"
    ]
    if not glossary_sources:
        return None, ""

    def rank(src: dict) -> int:
        page_slug = src.get("source_slug", "")
        for i, pref in enumerate(CANONICAL_PRECEDENCE):
            if page_slug == pref or page_slug.startswith(pref):
                return i
        return len(CANONICAL_PRECEDENCE)

    glossary_sources.sort(key=rank)
    chosen = glossary_sources[0]
    canonical, _ = _resolve_canonical(chosen.get("source_slug", ""), exact, prefix)
    return canonical, chosen.get("excerpt", "")


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


def _looks_definitional(cleaned: str, term: str) -> bool:
    """For keyword-scan hits, decide whether the excerpt shows the
    source defining or prescribing usage on the term — vs the term
    appearing incidentally inside a discussion of something else.

    Three structural signals count as real entries:
    1. Excerpt opens with the term (cleanup already stripped bullets,
       headings, and Pandoc/Wix emphasis spans, so a real entry's
       first word will be the term itself).
    2. Term is followed by a colon, em-dash, or en-dash anywhere in
       the excerpt (`activist:`, `ableism —`). This is the most
       universal definition pattern across style guides.
    3. Term is preceded by `avoid`, `use`, `prefer`, `instead of`,
       or `say` (with or without quote marks). This is the standard
       style-guide prescription pattern.

    Without any of these, a keyword-scan hit is treated as incidental
    and dropped.
    """
    if not cleaned or not term:
        return False
    cleaned_lower = cleaned.lower()
    term_lower = term.lower()
    # Build a regex-safe term pattern allowing optional trailing `s`
    # (so the scan catches both "activist" and "activists").
    term_re = re.escape(term_lower)

    # 1. Term at start of excerpt.
    if re.match(rf"^{term_re}s?\b", cleaned_lower):
        return True
    # 2. Term followed by definition punctuation.
    if re.search(rf"\b{term_re}s?\s*[:—–-]\s", cleaned_lower):
        return True
    # 3. Prescription pattern: avoid/use/prefer/instead of/say + term.
    prescription_words = r"(?:avoid|use|prefer|instead of|say|never use|do not use|don't use)"
    if re.search(rf"\b{prescription_words}\b[^.]{{0,40}}\b{term_re}", cleaned_lower):
        return True
    return False


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


def _apply_offline_policy(
    entry: dict,
    term: str,
    canonical: dict,
    tier: str,
    offline: list[tuple[str, str, str]],
) -> None:
    """Apply the canonical source's live_status policy, mutating entry.

    - live → expose the canonical pointer.
    - offline/login-gated WITH a local archive → expose pointer + archived flag.
    - offline WITHOUT a local archive → the failure mode:
        curated → demote to `listed` (lose pointer, excerpt, provenance);
        verified-hold → keep excerpt + note, drop the pointer only.
      Either way, record the term in the offline report.
    """
    live_status = canonical.get("live_status", "live")
    has_archive = bool(canonical.get("local_archive"))
    # Strip the internal-only local_archive key before exposing.
    public = {k: v for k, v in canonical.items() if k != "local_archive"}

    if live_status == "offline" and not has_archive:
        offline.append((tier, term, canonical.get("page_slug", "")))
        if tier == "curated":
            entry["tier"] = "listed"
            entry["provenance"] = None
            entry["excerpt"] = None
            entry["canonical_source"] = None
        else:  # verified-hold keeps its human-checked excerpt + note
            entry["canonical_source"] = None
        return

    entry["canonical_source"] = public
    if live_status in ("offline", "login-gated") and has_archive:
        entry["canonical_archived"] = True


def _assign_tier(
    entry: dict,
    term: str,
    overrides: dict[str, dict[str, str]],
    exact: dict[str, dict[str, str]],
    prefix: list[tuple[str, dict[str, str]]],
    unresolved: list[tuple[str, str]],
    offline: list[tuple[str, str, str]],
) -> None:
    """Resolve an entry's tier and canonical source in place.

    Precedence: full (published page) → verified-hold (override) →
    curated (has a structured-glossary source) → listed (default).
    """
    if entry["commons_slug"]:
        entry["tier"] = "full"
        return

    slug_dashed = term.replace(" ", "-")
    override = overrides.get(term) or overrides.get(slug_dashed)
    if override:
        entry["tier"] = "verified-hold"
        entry["provenance"] = "verified"
        entry["excerpt"] = override.get("excerpt") or None
        entry["note"] = override.get("note") or None
        canonical, resolved = _resolve_canonical(
            override.get("canonical_source_slug", ""), exact, prefix
        )
        if not resolved:
            unresolved.append((term, override.get("canonical_source_slug", "")))
            entry["canonical_source"] = None
        else:
            _apply_offline_policy(entry, term, canonical, "verified-hold", offline)
        return

    canonical, excerpt = _pick_curated_canonical(entry["sources"], exact, prefix)
    if canonical is not None:
        entry["tier"] = "curated"
        entry["provenance"] = "machine-extracted"
        entry["excerpt"] = excerpt or None
        _apply_offline_policy(entry, term, canonical, "curated", offline)
    # else: tier stays "listed" (set in the entry default)


def build_index() -> dict:
    if not MATRIX_CSV.exists():
        raise SystemExit(
            f"matrix CSV not found at {MATRIX_CSV} — run build-coverage-matrix.py first"
        )

    exact_lookup, prefix_lookup = _build_org_lookup()
    commons_lookup, stub_display = _build_commons_lookup()
    overrides = _load_overrides()
    # Build-time reports (printed to stderr, non-fatal).
    unresolved_overrides: list[tuple[str, str]] = []
    offline_reports: list[tuple[str, str, str]] = []

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
            extraction_method = (row.get("extraction_method") or "").strip()
            # For keyword-scan hits (narrative sources without a
            # structured glossary extractor), require structural
            # evidence that the source actually defines or prescribes
            # usage on this term — otherwise the hit is an incidental
            # mention inside a discussion of something else.
            if extraction_method == "keyword" and not _looks_definitional(cleaned, term):
                continue
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
                    "tier": "listed",            # full | verified-hold | curated | listed
                    "provenance": None,          # verified | machine-extracted | None
                    "canonical_source": None,
                    "canonical_archived": False,
                    "excerpt": None,             # canonical teaser (curated/verified-hold)
                    "note": None,
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
        slug_dashed = term.replace(" ", "-")
        # Hand-curated override terms always survive the noise filters —
        # the override supplies the canonical excerpt even when matrix
        # coverage is thin or the term is short (e.g. "jew").
        is_override = term in overrides or slug_dashed in overrides
        if not is_override:
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
        # Resolve commons-page link (published, non-stub pages only).
        if slug_dashed in commons_lookup:
            entry["commons_slug"] = commons_lookup[slug_dashed]
        # Display: published page name → stub page name → derived form.
        if slug_dashed in stub_display:
            entry["display"] = stub_display[slug_dashed]
        else:
            entry["display"] = _display_form(term, entry["commons_slug"])
        # Tier + canonical-source resolution.
        _assign_tier(
            entry, term, overrides, exact_lookup, prefix_lookup,
            unresolved_overrides, offline_reports,
        )
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
    for commons_slug, target_slug in commons_lookup.items():
        # Alias keys (commons_slug != target) only resolve existing matrix
        # entries — they don't get synthesized glossary rows of their own.
        if commons_slug != target_slug:
            continue
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
            "tier": "full",
            "provenance": None,
            "canonical_source": None,
            "canonical_archived": False,
            "excerpt": None,
            "note": None,
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

    by_tier: dict[str, int] = {}
    for e in entries.values():
        by_tier[e["tier"]] = by_tier.get(e["tier"], 0) + 1

    stats = {
        "total_terms": len(entries),
        "commons_terms": by_tier.get("full", 0),
        "verified_hold_terms": by_tier.get("verified-hold", 0),
        "curated_terms": by_tier.get("curated", 0),
        "listed_terms": by_tier.get("listed", 0),
        "long_tail_terms": sum(1 for e in entries.values() if not e["commons_slug"]),
        "by_coverage": {str(k): v for k, v in sorted(coverage_histogram.items())},
    }

    # Build-time reports (non-fatal — visible in deploy logs).
    if unresolved_overrides:
        print("UNRESOLVED OVERRIDE SOURCES:", file=sys.stderr)
        for term, slug in sorted(unresolved_overrides):
            print(f"  {term} -> {slug}", file=sys.stderr)
    if offline_reports:
        print(
            "UNAVAILABLE CANONICAL SOURCES (offline, no archive):",
            file=sys.stderr,
        )
        for tier, term, slug in sorted(offline_reports):
            print(f"  [{tier}] {term} -> {slug}", file=sys.stderr)

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
        f"  total: {stats['total_terms']} | full: {stats['commons_terms']} | "
        f"verified-hold: {stats['verified_hold_terms']} | "
        f"curated: {stats['curated_terms']} | listed: {stats['listed_terms']}"
    )
    print(f"  coverage histogram: {stats['by_coverage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
