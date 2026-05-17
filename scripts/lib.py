#!/usr/bin/env python3
"""
lib.py — shared helpers for ELC pipeline scripts.

Stdlib only. Imported by build-coverage-matrix.py, scaffold-term.py,
scaffold-source-pages.py, and enrich-source-pages.py.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOTS = [PROJECT_ROOT / "source-guides", PROJECT_ROOT / "source-guides" / "discovered"]

# ---------- YAML helpers ----------

def yaml_escape(s: str) -> str:
    """Conservative: always double-quote, escape backslashes and double quotes."""
    if s == "":
        return '""'
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def strip_yaml_string(s: str) -> str:
    s = s.strip()
    if s in ("null", ""):
        return ""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


# ---------- frontmatter ----------

def parse_frontmatter_scalars(text: str) -> dict[str, str]:
    """Parse top-level scalar keys from YAML frontmatter. Returns {} if no frontmatter."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line.startswith((" ", "\t")):
            continue
        m = re.match(r"^([a-zA-Z_]+):(?:\s+(.*))?$", line)
        if m and m.group(2) is not None:
            out[m.group(1)] = m.group(2).strip()
    return out


# ---------- source-guide index ----------

def build_pdf_to_md_index() -> dict[str, Path]:
    """For every extracted .md sibling in source-guides/, parse the header
    comment to find which PDF it came from. Returns: pdf_basename → md path."""
    idx: dict[str, Path] = {}
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for md in root.glob("*.md"):
            if md.name == "MANIFEST.md":
                continue
            head = md.read_text(encoding="utf-8", errors="replace")[:400]
            m = re.search(r"^extracted_from:\s+(.+)$", head, re.MULTILINE)
            if m:
                idx[m.group(1).strip()] = md
    return idx


# ---------- term normalization ----------

_LEADING_ARTICLES = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)
_SURROUNDING_QUOTES = re.compile(r'''^[""''\"\\']+|[""''\"\\']+$''')
_MULTISPACE = re.compile(r"\s+")
_NON_WORD_TRAIL = re.compile(r"[\s,;:.!?]+$")


def normalize_term(raw: str) -> str:
    """Lowercase, strip quotes/articles/punctuation, collapse whitespace.
    Hyphens collapse to spaces so 'african-american' and 'african american'
    are the same term in the universe."""
    t = raw.strip()
    t = _SURROUNDING_QUOTES.sub("", t)
    t = t.lower()
    t = t.replace("-", " ")
    t = _LEADING_ARTICLES.sub("", t)
    t = _NON_WORD_TRAIL.sub("", t)
    t = _MULTISPACE.sub(" ", t)
    return t.strip()
