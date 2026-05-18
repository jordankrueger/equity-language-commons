#!/usr/bin/env python3
"""Build a SQLite index of the commons content for future API / faceted-query use.

Markdown files in `site/src/content/{terms,sources,chapters}` remain
source of truth. This script reads them at build time and emits a
SQLite database to:

    site/public/data/elc-index.sqlite

That path makes the file part of the static deployment, so anyone can
fetch it from the live site:

    https://equitylanguagecommons.org/data/elc-index.sqlite

Schema (kept minimal — extend in place as needs surface):

    terms(slug PRIMARY KEY, term, last_reviewed, stub)
    sources(slug PRIMARY KEY, org, org_slug, work_title, year,
            source_url, host_posture, live_status, last_checked, format,
            length_pages, stub)
    guidance(id PRIMARY KEY, term_slug, org_slug, year, recommendation,
             quote, quote_loc, paraphrase, confidence)
    chapters(slug PRIMARY KEY, title, "order")
    term_chapters(term_slug, chapter_slug)
    term_categories(term_slug, category)
    term_tags(term_slug, tag)

Idempotent — rebuilds from scratch on every run.

Currently uses a basic line-by-line parser to avoid a PyYAML
dependency. That parser handles scalar fields and the `guidance:` /
`related_terms:` lists used in the term schema. If the term schema
grows new nested structures, extend the parser here.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TERMS_DIR = ROOT / "site" / "src" / "content" / "terms"
SOURCES_DIR = ROOT / "site" / "src" / "content" / "sources"
CHAPTERS_DIR = ROOT / "site" / "src" / "content" / "chapters"
OUT_PATH = ROOT / "site" / "public" / "data" / "elc-index.sqlite"


def _extract_frontmatter(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in ("null", "~", ""):
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def _parse_term_frontmatter(block: str) -> dict[str, Any]:
    """Parse the term YAML frontmatter into a dict.

    Hand-rolled to keep this script stdlib-only. Handles scalar fields
    and the two list-of-records used in the term schema (guidance,
    related_terms). Other nested structures are ignored (audience_notes,
    context_data, etc. — fine for the SQLite index's current scope).
    """
    result: dict[str, Any] = {}
    lines = block.splitlines()
    i = 0
    current_list_key: str | None = None
    current_record: dict[str, Any] | None = None
    current_records: list[dict[str, Any]] = []

    def flush_list() -> None:
        nonlocal current_list_key, current_record, current_records
        if current_list_key is not None:
            if current_record is not None:
                current_records.append(current_record)
            result[current_list_key] = current_records
        current_list_key = None
        current_record = None
        current_records = []

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        i += 1
        if not line.strip():
            continue
        # Detect top-level scalar/list assignment.
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2)
            flush_list()
            if value == "" or value == "|":
                # List or block scalar — peek next lines.
                # Look ahead to decide list vs nested.
                if i < len(lines) and lines[i].lstrip().startswith("- "):
                    current_list_key = key
                    current_records = []
                    current_record = None
                    continue
                # Otherwise treat as null for our purposes.
                result[key] = None
            else:
                # If value is "[]" or similar inline list, ignore (not needed).
                if value.startswith("[") and value.endswith("]"):
                    inner = value[1:-1].strip()
                    if not inner:
                        result[key] = []
                    else:
                        # Comma-split inline list of scalars (aliases, categories, tags).
                        items = []
                        for piece in inner.split(","):
                            scalar = _parse_scalar(piece.strip())
                            if scalar:
                                items.append(scalar)
                        result[key] = items
                else:
                    result[key] = _parse_scalar(value)
            continue
        # List item: '  - key: value' or continuation.
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("- "):
            if current_list_key is None:
                # Stray list item — likely a top-level inline list. Skip.
                continue
            if current_record is not None:
                current_records.append(current_record)
            current_record = {}
            after = stripped[2:].strip()
            if ":" in after:
                k, _, v = after.partition(":")
                current_record[k.strip()] = _parse_scalar(v.strip())
            continue
        if current_record is not None and ":" in stripped:
            k, _, v = stripped.partition(":")
            current_record[k.strip()] = _parse_scalar(v.strip())
    flush_list()
    return result


def init_schema(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS terms;
        DROP TABLE IF EXISTS sources;
        DROP TABLE IF EXISTS guidance;
        DROP TABLE IF EXISTS chapters;
        DROP TABLE IF EXISTS term_chapters;
        DROP TABLE IF EXISTS term_categories;
        DROP TABLE IF EXISTS term_tags;

        CREATE TABLE terms (
            slug TEXT PRIMARY KEY,
            term TEXT NOT NULL,
            last_reviewed TEXT,
            stub INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE sources (
            slug TEXT PRIMARY KEY,
            org TEXT NOT NULL,
            org_slug TEXT,
            work_title TEXT,
            year INTEGER,
            source_url TEXT,
            host_posture TEXT,
            live_status TEXT,
            last_checked TEXT,
            format TEXT,
            length_pages INTEGER,
            stub INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE guidance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_slug TEXT NOT NULL,
            org_slug TEXT,
            year INTEGER,
            recommendation TEXT,
            quote TEXT,
            quote_loc TEXT,
            paraphrase TEXT,
            confidence TEXT,
            FOREIGN KEY (term_slug) REFERENCES terms(slug)
        );

        CREATE TABLE chapters (
            slug TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            "order" INTEGER
        );

        CREATE TABLE term_chapters (
            term_slug TEXT NOT NULL,
            chapter_slug TEXT NOT NULL,
            PRIMARY KEY (term_slug, chapter_slug)
        );

        CREATE TABLE term_categories (
            term_slug TEXT NOT NULL,
            category TEXT NOT NULL,
            PRIMARY KEY (term_slug, category)
        );

        CREATE TABLE term_tags (
            term_slug TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (term_slug, tag)
        );

        CREATE INDEX idx_guidance_term ON guidance(term_slug);
        CREATE INDEX idx_guidance_org ON guidance(org_slug);
        CREATE INDEX idx_guidance_recommendation ON guidance(recommendation);
        CREATE INDEX idx_guidance_year ON guidance(year);
        CREATE INDEX idx_term_chapters ON term_chapters(chapter_slug);
        CREATE INDEX idx_term_categories ON term_categories(category);
        """
    )
    con.commit()


def ingest_sources(con: sqlite3.Connection) -> int:
    count = 0
    cur = con.cursor()
    for path in sorted(SOURCES_DIR.glob("*.md")):
        block = _extract_frontmatter(path)
        if not block:
            continue
        fm = _parse_term_frontmatter(block)
        cur.execute(
            """
            INSERT OR REPLACE INTO sources
              (slug, org, org_slug, work_title, year, source_url,
               host_posture, live_status, last_checked, format,
               length_pages, stub)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                path.stem,
                fm.get("org") or path.stem,
                fm.get("org_slug"),
                fm.get("work_title"),
                fm.get("year") if isinstance(fm.get("year"), int) else None,
                fm.get("source_url"),
                fm.get("host_posture"),
                fm.get("live_status"),
                fm.get("last_checked"),
                fm.get("format"),
                fm.get("length_pages")
                if isinstance(fm.get("length_pages"), int)
                else None,
                1 if fm.get("stub") else 0,
            ),
        )
        count += 1
    con.commit()
    return count


def ingest_chapters(con: sqlite3.Connection) -> tuple[int, int]:
    chapter_count = 0
    mapping_count = 0
    cur = con.cursor()
    for path in sorted(CHAPTERS_DIR.glob("*.md")):
        block = _extract_frontmatter(path)
        if not block:
            continue
        fm = _parse_term_frontmatter(block)
        slug = fm.get("slug") or path.stem
        cur.execute(
            """INSERT OR REPLACE INTO chapters (slug, title, "order") VALUES (?, ?, ?)""",
            (
                slug,
                fm.get("title") or slug.title(),
                fm.get("order") if isinstance(fm.get("order"), int) else None,
            ),
        )
        chapter_count += 1
        # term_slugs is an inline list, but the parser doesn't capture
        # that yet — re-extract from the raw block.
        for term_slug in _extract_string_list(block, "term_slugs"):
            cur.execute(
                "INSERT OR IGNORE INTO term_chapters (term_slug, chapter_slug) VALUES (?, ?)",
                (term_slug, slug),
            )
            mapping_count += 1
    con.commit()
    return chapter_count, mapping_count


def _extract_string_list(block: str, key: str) -> list[str]:
    """Pull a top-level YAML list-of-scalars out of the frontmatter block.

    Handles both inline (`key: [a, b]`) and block (`key:\n  - a\n  - b`)
    forms. Returns an empty list if the key isn't present.
    """
    inline = re.search(rf"^{re.escape(key)}:\s*\[(.*?)\]\s*$", block, re.MULTILINE)
    if inline:
        items = []
        for piece in inline.group(1).split(","):
            scalar = piece.strip().strip('"').strip("'")
            if scalar:
                items.append(scalar)
        return items
    m = re.search(rf"^{re.escape(key)}:\s*\n((?:\s+-\s+.*\n?)+)", block, re.MULTILINE)
    if not m:
        return []
    items = []
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("- "):
            scalar = s[2:].strip().strip('"').strip("'")
            if scalar:
                items.append(scalar)
    return items


def ingest_terms(con: sqlite3.Connection) -> tuple[int, int, int, int, int]:
    term_count = 0
    guidance_count = 0
    chapter_mappings = 0
    category_mappings = 0
    tag_mappings = 0
    cur = con.cursor()
    for path in sorted(TERMS_DIR.glob("*.md")):
        block = _extract_frontmatter(path)
        if not block:
            continue
        fm = _parse_term_frontmatter(block)
        slug = fm.get("slug") or path.stem
        cur.execute(
            "INSERT OR REPLACE INTO terms (slug, term, last_reviewed, stub) VALUES (?, ?, ?, ?)",
            (
                slug,
                fm.get("term") or slug.replace("-", " ").title(),
                fm.get("last_reviewed"),
                1 if fm.get("stub") else 0,
            ),
        )
        term_count += 1

        for entry in fm.get("guidance") or []:
            year = entry.get("year") if isinstance(entry.get("year"), int) else None
            cur.execute(
                """
                INSERT INTO guidance
                  (term_slug, org_slug, year, recommendation, quote,
                   quote_loc, paraphrase, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slug,
                    entry.get("org_slug"),
                    year,
                    entry.get("recommendation"),
                    entry.get("quote"),
                    entry.get("quote_loc"),
                    entry.get("paraphrase"),
                    entry.get("confidence"),
                ),
            )
            guidance_count += 1

        # Categories, tags — inline string-list fields.
        for category in _extract_string_list(block, "categories"):
            cur.execute(
                "INSERT OR IGNORE INTO term_categories (term_slug, category) VALUES (?, ?)",
                (slug, category),
            )
            category_mappings += 1
            # Categories often match chapter slugs — wire the mapping too.
            cur.execute(
                "SELECT 1 FROM chapters WHERE slug = ?", (category,)
            )
            if cur.fetchone():
                cur.execute(
                    "INSERT OR IGNORE INTO term_chapters (term_slug, chapter_slug) VALUES (?, ?)",
                    (slug, category),
                )
                chapter_mappings += 1
        for tag in _extract_string_list(block, "tags"):
            cur.execute(
                "INSERT OR IGNORE INTO term_tags (term_slug, tag) VALUES (?, ?)",
                (slug, tag),
            )
            tag_mappings += 1
    con.commit()
    return term_count, guidance_count, chapter_mappings, category_mappings, tag_mappings


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OUT_PATH.exists():
        OUT_PATH.unlink()
    con = sqlite3.connect(OUT_PATH)
    try:
        init_schema(con)
        source_count = ingest_sources(con)
        chapter_count, _ = ingest_chapters(con)
        (
            term_count,
            guidance_count,
            chapter_mappings,
            category_mappings,
            tag_mappings,
        ) = ingest_terms(con)
    finally:
        con.close()

    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    print(
        f"  terms: {term_count} | guidance entries: {guidance_count} | "
        f"sources: {source_count} | chapters: {chapter_count}"
    )
    print(
        f"  term→chapter mappings: {chapter_mappings} | "
        f"categories: {category_mappings} | tags: {tag_mappings}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
