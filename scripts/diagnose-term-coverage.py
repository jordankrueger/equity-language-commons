#!/usr/bin/env python3
"""Diagnose why terms did or did not clear the W6 coverage bar.

This intentionally mirrors the coverage chain instead of rebuilding it from
scratch:
  1. normalize/query `notes/term-coverage-matrix.csv`
  2. apply `scripts/build-glossary-index.py` row filters
  3. compare the recomputed source count to `glossary-index.json`
  4. apply the W6 disposition rules from `scripts/lint-content.py`

Stdlib only. Run from the repository root:

    ./scripts/diagnose-term-coverage.py poor "asylum seeker" activist
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
MATRIX_CSV = ROOT / "notes" / "term-coverage-matrix.csv"
GLOSSARY_JSON = ROOT / "site" / "src" / "data" / "glossary-index.json"
TERMS_DIR = ROOT / "site" / "src" / "content" / "terms"
COVERAGE_DECISIONS = ROOT / "notes" / "coverage-decisions.yml"
BUILD_MATRIX = ROOT / "scripts" / "build-coverage-matrix.py"
BUILD_INDEX = ROOT / "scripts" / "build-glossary-index.py"

EXCERPT_TRACE_CHARS = 80


def _load_script(path: Path, module_name: str) -> Any | None:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        return None
    return module


_matrix_mod = _load_script(BUILD_MATRIX, "coverage_matrix_pipeline")
_index_mod = _load_script(BUILD_INDEX, "glossary_index_pipeline")


# Fallbacks are conservative copies of the pipeline helpers, used only if the
# path import above fails because the source scripts use hyphenated filenames.
if _matrix_mod is not None and hasattr(_matrix_mod, "normalize_term"):
    normalize_term = _matrix_mod.normalize_term
    KEYWORD_SCAN_BLOCKLIST = set(getattr(_matrix_mod, "KEYWORD_SCAN_BLOCKLIST", set()))
    NORMALIZE_SOURCE = "imported from scripts/build-coverage-matrix.py"
else:
    NORMALIZE_SOURCE = "fallback copy in diagnose-term-coverage.py"
    KEYWORD_SCAN_BLOCKLIST = {
        "american", "family", "out", "two", "central", "chief", "special",
        "older", "partner", "senior", "people", "covering", "acting",
        "treatment", "ethnic", "nation", "race", "male", "sex", "asia",
        "blind",
    }
    _LEADING_ARTICLES = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)
    _SURROUNDING_QUOTES = re.compile(r'^["“”\'‘’\\]+|["“”\'‘’\\]+$')
    _MULTISPACE = re.compile(r"\s+")
    _NON_WORD_TRAIL = re.compile(r"[\s,;:.!?]+$")

    def normalize_term(raw: str) -> str:
        t = raw.strip()
        t = _SURROUNDING_QUOTES.sub("", t)
        t = t.lower()
        t = t.replace("-", " ")
        t = _LEADING_ARTICLES.sub("", t)
        t = _NON_WORD_TRAIL.sub("", t)
        t = _MULTISPACE.sub(" ", t)
        return t.strip()


if _index_mod is not None:
    clean_excerpt = _index_mod._clean_excerpt
    is_index_only_excerpt = _index_mod._is_index_only_excerpt
    looks_definitional = _index_mod._looks_definitional
    is_low_content_excerpt = _index_mod._is_low_content_excerpt
    build_org_lookup = _index_mod._build_org_lookup
    resolve_source = _index_mod._resolve_source
    load_overrides = _index_mod._load_overrides
    SHORT_TERM_THRESHOLD = _index_mod.SHORT_TERM_THRESHOLD
    TRUNCATED_PHRASE_ENDINGS = _index_mod.TRUNCATED_PHRASE_ENDINGS
    FILTER_SOURCE = "imported from scripts/build-glossary-index.py"
else:
    FILTER_SOURCE = "fallback copy in diagnose-term-coverage.py"
    SHORT_TERM_THRESHOLD = 3
    TRUNCATED_PHRASE_ENDINGS = frozenset(
        {
            "of", "and", "the", "to", "or", "for", "in", "with", "on",
            "at", "by", "as", "from", "into", "onto", "via", "but",
            "an", "a",
        }
    )

    def clean_excerpt(text: str) -> str:
        cleaned = text or ""
        cleaned = re.sub(r"^[\s>]*(\|\s*)+", "", cleaned)
        cleaned = re.sub(r"\s+\|\s+", " ", cleaned)
        for _ in range(5):
            before = cleaned
            cleaned = re.sub(r"\{[^{}]*\}", "", cleaned)
            cleaned = re.sub(r"\[([^\[\]]+?)\]\(\s*[^)]+?\s*\)", r"\1", cleaned)
            cleaned = re.sub(r"\[([^\[\]]+?)\]", r"\1", cleaned)
            if cleaned == before:
                break
        cleaned = re.sub(r"^[\s>]*#{1,6}\s*", "", cleaned)
        cleaned = re.sub(r"^[\s]*[-*+]\s+", "", cleaned)
        cleaned = re.sub(r"\*\*([^*]+?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\1", cleaned)
        cleaned = re.sub(r"\.[a-zA-Z][a-zA-Z0-9_\-]*", "", cleaned)
        cleaned = re.sub(r"\.(\s*\.){2,}", "", cleaned)
        cleaned = re.sub(r"\.{3,}", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return re.sub(r"\s+\.\s*$", "", cleaned).strip()

    def is_index_only_excerpt(raw: str) -> bool:
        return bool(re.match(r"^[-*+\s]*\[[^\[\]]+\]\(\s*[^)]+\s*\)\s*\{[^{}]+\}\s*$", raw.strip()))

    def looks_definitional(cleaned: str, term: str) -> bool:
        return any(_definitional_criteria(cleaned, term).values())

    def is_low_content_excerpt(cleaned: str) -> bool:
        if len(cleaned) < 30:
            return True
        return bool(re.match(r"^[A-Za-z][\w/\-\s]{0,60}[:.]?$", cleaned))

    def build_org_lookup() -> tuple[dict[str, dict[str, str]], list[tuple[str, dict[str, str]]]]:
        return {}, []

    def resolve_source(matrix_slug: str, exact: dict[str, dict[str, str]], prefix: list[tuple[str, dict[str, str]]]) -> dict[str, str]:
        return {"page_slug": matrix_slug, "org": matrix_slug}

    def load_overrides() -> dict[str, dict[str, str]]:
        return {}


@dataclass
class TraceRow:
    row: dict[str, str]
    fate: str
    cleaned: str
    criteria: dict[str, bool]
    resolved_slug: str
    resolved_org: str


def slugify(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def truncate(value: str, limit: int = EXCERPT_TRACE_CHARS) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def load_matrix_rows() -> list[dict[str, str]]:
    with MATRIX_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_glossary_index() -> dict[str, Any]:
    with GLOSSARY_JSON.open(encoding="utf-8") as f:
        return json.load(f)


def parse_aliases() -> tuple[set[str], dict[str, str], dict[str, str]]:
    pages: set[str] = set()
    aliases: dict[str, str] = {}
    display: dict[str, str] = {}
    alias_block_re = re.compile(r"^aliases:\n((?:[ \t]+-[ \t]+.*\n)+)", re.M)
    for path in sorted(TERMS_DIR.glob("*.md")):
        slug = path.stem
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        display[slug] = fm.get("term", slug.replace("-", " ").title())
        is_stub = str(fm.get("stub", "")).strip().lower().startswith("true")
        if not is_stub:
            pages.add(slug)
            aliases.setdefault(slug, slug)
            m = alias_block_re.search(text)
            if m:
                for alias in re.findall(r"-\s+(.*)", m.group(1)):
                    alias_slug = slugify(alias.strip().strip("\"'"))
                    if alias_slug and alias_slug not in pages:
                        aliases.setdefault(alias_slug, slug)
    return pages, aliases, display


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def load_coverage_decisions() -> set[str]:
    decided: set[str] = set()
    if not COVERAGE_DECISIONS.exists():
        return decided
    for line in COVERAGE_DECISIONS.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^-\s+term:\s+"(.*)"', line.strip())
        if m:
            decided.add(slugify(m.group(1)))
    return decided


def _definitional_criteria(cleaned: str, term: str) -> dict[str, bool]:
    if not cleaned or not term:
        return {
            "starts-with-term": False,
            "term-followed-by-definition-punctuation": False,
            "prescription-word-before-term": False,
        }
    cleaned_lower = cleaned.lower()
    term_re = re.escape(term.lower())
    prescription_words = r"(?:avoid|use|prefer|instead of|say|never use|do not use|don't use)"
    return {
        "starts-with-term": bool(re.match(rf"^{term_re}s?\b", cleaned_lower)),
        "term-followed-by-definition-punctuation": bool(
            re.search(rf"\b{term_re}s?\s*[:—–-]\s", cleaned_lower)
        ),
        "prescription-word-before-term": bool(
            re.search(rf"\b{prescription_words}\b[^.]{{0,40}}\b{term_re}", cleaned_lower)
        ),
    }


def trace_rows(rows: list[dict[str, str]], term: str) -> list[TraceRow]:
    exact_lookup, prefix_lookup = build_org_lookup()
    traced: list[TraceRow] = []
    for row in rows:
        raw_excerpt = row.get("excerpt") or ""
        cleaned = clean_excerpt(raw_excerpt)
        criteria = _definitional_criteria(cleaned, term)
        source_slug = (row.get("source_slug") or "").strip()
        meta = resolve_source(source_slug, exact_lookup, prefix_lookup)
        if is_index_only_excerpt(raw_excerpt):
            fate = "DROPPED-navigation"
        elif row.get("extraction_method") == "keyword" and not looks_definitional(cleaned, term):
            fate = "DROPPED-not-definitional"
        else:
            fate = "KEPT"
        traced.append(
            TraceRow(
                row=row,
                fate=fate,
                cleaned=cleaned,
                criteria=criteria,
                resolved_slug=meta.get("page_slug", source_slug),
                resolved_org=meta.get("org", source_slug),
            )
        )
    return traced


def survives_final_term_prune(term: str, count: int, overrides: dict[str, dict[str, str]]) -> tuple[bool, str]:
    slug_dashed = term.replace(" ", "-")
    if term in overrides or slug_dashed in overrides:
        return True, "override term survives final pruning"
    if not term.startswith("#") and len(term) < SHORT_TERM_THRESHOLD:
        return False, f"short term below initial threshold ({SHORT_TERM_THRESHOLD})"
    if len(term) <= 2 and count < 3:
        return False, "final short-term prune: <=2 chars need >=3 sources"
    if 3 <= len(term) <= 4 and count < 2:
        return False, "final short-term prune: 3-4 chars need >=2 sources"
    if count == 0:
        return False, "zero surviving sources"
    words = term.split()
    if len(words) >= 2 and words[-1].lower() in TRUNCATED_PHRASE_ENDINGS:
        return False, "truncated phrase ending prune"
    return True, "passes final term-level pruning"


def variants_for(term: str) -> list[str]:
    raw = term.strip()
    variants = {raw, raw.replace("-", " "), raw.replace(" ", "-")}
    normalized = normalize_term(raw)
    variants.add(normalized)
    variants.add(normalized.replace(" ", "-"))
    words = normalized.split()
    if words:
        last = words[-1]
        if last.endswith("ies") and len(last) > 3:
            variants.add(" ".join(words[:-1] + [last[:-3] + "y"]))
        elif last.endswith("s") and not last.endswith("ss") and len(last) > 3:
            variants.add(" ".join(words[:-1] + [last[:-1]]))
        else:
            variants.add(" ".join(words[:-1] + [last + "s"]))
    return sorted(v for v in variants if v)


def render_blocklist(term: str) -> str:
    components = term.split()
    hits = []
    if term in KEYWORD_SCAN_BLOCKLIST:
        hits.append(f"`{term}`")
    hits.extend(f"`{part}`" for part in components if part in KEYWORD_SCAN_BLOCKLIST)
    if not hits:
        return "No keyword-scan blocklist hits for the normalized term or its components."
    return "Yes: " + ", ".join(dict.fromkeys(hits)) + ". Glossary hits can still count; keyword scanning skips these terms."


def render_trace_table(traced: list[TraceRow]) -> list[str]:
    if not traced:
        return ["No raw matrix rows for this normalized term."]
    lines = [
        "| Fate | Source | Method | Line | Definitional criteria | Excerpt |",
        "|---|---|---:|---:|---|---|",
    ]
    for item in traced:
        row = item.row
        criteria = ", ".join(
            f"{name}={'yes' if passed else 'no'}"
            for name, passed in item.criteria.items()
        )
        if row.get("extraction_method") != "keyword":
            criteria = "n/a for glossary row; " + criteria
        excerpt = truncate(row.get("excerpt") or "").replace("|", "\\|")
        source = f"{row.get('source_slug')} -> {item.resolved_slug}"
        lines.append(
            f"| {item.fate} | `{source}` | {row.get('extraction_method')} | "
            f"{row.get('line')} | {criteria} | {excerpt} |"
        )
    return lines


def render_near_variants(term: str, all_rows: list[dict[str, str]]) -> list[str]:
    lines = ["**Near-Form Variants**"]
    lines.append("")
    lines.append("- Checked forms: " + ", ".join(f"`{v}`" for v in variants_for(term)))
    candidates = [
        row for row in all_rows
        if row.get("term_normalized") != term
        and row.get("extraction_method") == "glossary"
        and (term in (row.get("term_normalized") or "") or (row.get("term_normalized") or "") in term)
    ]
    if not candidates:
        lines.append("- No different matrix term with glossary-method substring overlap.")
        return lines
    lines.extend([
        "- Different matrix terms with glossary-method substring overlap:",
        "",
        "| Matrix term | Source | Line | Excerpt |",
        "|---|---|---:|---|",
    ])
    for row in candidates[:25]:
        lines.append(
            f"| `{row.get('term_normalized')}` | `{row.get('source_slug')}` | "
            f"{row.get('line')} | {truncate(row.get('excerpt') or '').replace('|', '\\|')} |"
        )
    if len(candidates) > 25:
        lines.append(f"| ... | ... | ... | {len(candidates) - 25} additional candidate rows omitted |")
    return lines


def render_term(
    requested: str,
    all_rows: list[dict[str, str]],
    glossary: dict[str, Any],
    pages: set[str],
    aliases: dict[str, str],
    page_display: dict[str, str],
    decisions: set[str],
    overrides: dict[str, dict[str, str]],
) -> list[str]:
    term = normalize_term(requested)
    rows = [row for row in all_rows if row.get("term_normalized") == term]
    traced = trace_rows(rows, term)
    kept = [item for item in traced if item.fate == "KEPT"]
    surviving_source_slugs = []
    surviving_orgs = []
    for item in kept:
        if item.resolved_slug not in surviving_source_slugs:
            surviving_source_slugs.append(item.resolved_slug)
            surviving_orgs.append(item.resolved_org)
    recomputed_count = len(surviving_source_slugs)
    entry = glossary.get("entries", {}).get(term)
    json_count = entry.get("source_count") if entry else None
    json_sources = [src.get("source_slug") for src in entry.get("sources", [])] if entry else []
    survives, prune_reason = survives_final_term_prune(term, recomputed_count, overrides)
    tslug = slugify(term)

    disposition = ""
    if entry and entry.get("commons_slug"):
        disposition = f"alias/full glossary entry resolves to page `{entry.get('commons_slug')}`"
    elif tslug in pages:
        disposition = "page exists"
    elif tslug in aliases and aliases[tslug] != tslug:
        target = aliases[tslug]
        disposition = f"alias of page `{target}` ({page_display.get(target, target)})"
    elif tslug in decisions:
        disposition = "coverage decision recorded"
    elif json_count is not None and json_count < 3:
        disposition = "under bar (count < 3)"
    elif json_count is None and recomputed_count < 3:
        disposition = "under bar after filters/final pruning (count < 3 or absent from JSON)"
    elif recomputed_count >= 3:
        disposition = "SHOULD HAVE WARNED"
    else:
        disposition = "under bar"

    lines = [f"## {requested} -> `{term}`", ""]
    lines.append(f"**Blocklist Check:** {render_blocklist(term)}")
    lines.append("")
    lines.append("**Raw Matrix Rows and Filter Trace**")
    lines.append("")
    lines.extend(render_trace_table(traced))
    lines.append("")
    lines.append("**Effective Source Count**")
    lines.append("")
    lines.append(f"- Recomputed surviving source orgs: {recomputed_count}")
    if surviving_source_slugs:
        lines.append(
            "- Surviving sources: "
            + ", ".join(f"`{slug}` ({org})" for slug, org in zip(surviving_source_slugs, surviving_orgs))
        )
    else:
        lines.append("- Surviving sources: none")
    lines.append(f"- Final term-level prune: {prune_reason}")
    if json_count is None:
        lines.append("- glossary-index.json source_count: absent")
    else:
        lines.append(f"- glossary-index.json source_count: {json_count}; sources: {', '.join(f'`{s}`' for s in json_sources) or 'none'}")
    if json_count != recomputed_count:
        detail = "expected when final term-level pruning removes the entry" if not survives and json_count is None else "investigate"
        lines.append(f"- Cross-check: MISMATCH ({detail})")
    else:
        lines.append("- Cross-check: matches")
    lines.append("")
    lines.append(f"**W6 Disposition:** {disposition}")
    if json_count in (1, 2) or (json_count is None and recomputed_count in (1, 2)):
        count = json_count if json_count is not None else recomputed_count
        names = json_sources if json_sources else surviving_source_slugs
        lines.append("")
        lines.append(
            f"**Near-Miss Summary:** {count} strong source"
            f"{'' if count == 1 else 's'}: {', '.join(f'`{s}`' for s in names)} — "
            f"needs {3 - count} more."
        )
    lines.append("")
    lines.extend(render_near_variants(term, all_rows))
    lines.append("")
    return lines


def render_report(terms: list[str]) -> str:
    all_rows = load_matrix_rows()
    glossary = load_glossary_index()
    pages, aliases, page_display = parse_aliases()
    decisions = load_coverage_decisions()
    overrides = load_overrides()
    lines = [
        "# Term Coverage Diagnosis",
        "",
        "Generated by `scripts/diagnose-term-coverage.py`.",
        "",
        "Notes:",
        f"- Term normalization: {NORMALIZE_SOURCE}.",
        f"- Row filters/source resolution: {FILTER_SOURCE}.",
        "- The trace applies the row filters requested in the task and also reports the index builder's final term-level pruning for cross-checks.",
        "- `DROPPED-navigation` means a pure glossary-index link row; `DROPPED-not-definitional` means a keyword hit without the structural definition/prescription signals used by `_looks_definitional()`.",
        "",
    ]
    for term in terms:
        lines.extend(
            render_term(
                term,
                all_rows,
                glossary,
                pages,
                aliases,
                page_display,
                decisions,
                overrides,
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose W6 source coverage for one or more terms."
    )
    parser.add_argument("terms", nargs="+", help="Term(s) to diagnose.")
    parser.add_argument("--report", help="Optional markdown report path.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = render_report(args.terms)
    print(report, end="")
    if args.report:
        path = Path(args.report)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
