#!/usr/bin/env python3
"""Content lint for the Equity Language Commons site.

Catches authoring artifacts and broken internal references before they ship.
Run from the repo root. Wired into deploy.sh — a FAIL blocks the deploy.

Checks (FAIL — exit 1):
  F1  [[wiki-bracket]] syntax anywhere in content (renders literally; never valid)
  F2  scaffolder-notes HTML comment blocks left in published pages
  F3  TODO markers in pages that are not stubs
  F4  `stub: true` on a page whose Synthesis section has real prose
  F6  internal markdown links (/terms/..., /chapters/..., /sources/...) that
      don't resolve to a content file

Checks (WARN — exit 0 unless --strict):
  W1  related_terms slug that is neither a page, a page alias, nor a
      glossary term (the page component falls back to a glossary link,
      so page/alias/glossary targets all resolve; only true orphans warn)
  W2  quote longer than 50 words (fair-use margin)
  W3  `categories` value that doesn't match a chapter slug (field is
      currently unrendered/vestigial, but keep it consistent)
  W6  coverage completeness: a glossary term with >=3 sources must have a
      page, resolve to a page via alias, or carry a documented decision in
      notes/coverage-decisions.yml (fold/drop with reason). This is the
      "sense of completeness" gate: every term that clears the bar is
      either treated or deliberately not.

Schema-level validation (required guidance keys, recommendation/confidence
enums) is intentionally NOT duplicated here — Astro's zod schema in
site/src/content.config.ts enforces it on every build.

Usage:
  ./scripts/lint-content.py            # warnings allowed
  ./scripts/lint-content.py --strict   # warnings are failures (launch mode)
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(ROOT, "site/src/content/terms")
CHAPTERS = os.path.join(ROOT, "site/src/content/chapters")
SOURCES = os.path.join(ROOT, "site/src/content/sources")
GLOSSARY_INDEX = os.path.join(ROOT, "site/src/data/glossary-index.json")
COVERAGE_DECISIONS = os.path.join(ROOT, "notes/coverage-decisions.yml")


def _slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

strict = "--strict" in sys.argv
fails, warns = [], []


def slugs_in(directory):
    return {os.path.basename(f)[:-3] for f in glob.glob(f"{directory}/*.md")}


term_slugs = slugs_in(TERMS)
chapter_slugs = slugs_in(CHAPTERS)
source_slugs = slugs_in(SOURCES)

# alias slugs across all term pages (for W1 + W6 resolution)
alias_slugs = set()
for _p in glob.glob(f"{TERMS}/*.md"):
    _txt = open(_p).read()
    _m = re.search(r"^aliases:\n((?:[ \t]+-[ \t]+.*\n)+)", _txt, re.M)
    if _m:
        for _a in re.findall(r"-\s+(.*)", _m.group(1)):
            alias_slugs.add(_slugify(_a.strip().strip("\"'")))
    # inline form: aliases: ["a", "b"]
    _mi = re.search(r"^aliases:[ \t]*\[(.*)\]", _txt, re.M)
    if _mi:
        for _a in _mi.group(1).split(","):
            _a = _a.strip().strip("\"'")
            if _a:
                alias_slugs.add(_slugify(_a))

# glossary term slugs (for W1 fallback resolution)
glossary_slugs = set()
if os.path.exists(GLOSSARY_INDEX):
    with open(GLOSSARY_INDEX) as _f:
        _gidx = json.load(_f)
    glossary_slugs = {_slugify(t) for t in _gidx.get("entries", {})}
else:
    _gidx = None
all_content = (
    glob.glob(f"{TERMS}/*.md")
    + glob.glob(f"{CHAPTERS}/*.md")
    + glob.glob(f"{SOURCES}/*.md")
)


def rel(path):
    return os.path.relpath(path, ROOT)


for path in sorted(all_content):
    text = open(path).read()
    name = rel(path)
    is_term = "/terms/" in path

    # F1 — wiki brackets
    for n, line in enumerate(text.splitlines(), 1):
        if "[[" in line:
            fails.append(f"F1 {name}:{n} wiki-bracket syntax: {line.strip()[:80]}")

    # F2 — scaffolder notes
    if "scaffolder notes" in text:
        fails.append(f"F2 {name} contains a scaffolder-notes block")

    # split frontmatter / body
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        fails.append(f"F7 {name} has no parseable frontmatter")
        continue
    fm, body = m.groups()
    is_stub = bool(re.search(r"^stub:\s*true", fm, re.M))

    # F3 — TODO markers outside stubs
    if not is_stub and "TODO" in text:
        for n, line in enumerate(text.splitlines(), 1):
            if "TODO" in line:
                fails.append(f"F3 {name}:{n} TODO marker: {line.strip()[:80]}")

    # F4 — stub flag with real synthesis prose
    if is_stub:
        syn = re.search(r"## Synthesis\n(.*?)(\n## |\Z)", body, re.S)
        if syn and re.sub(r"<!--.*?-->", "", syn.group(1), flags=re.S).strip():
            fails.append(f"F4 {name} marked stub: true but Synthesis has prose")

    # F6 — internal links must resolve
    for target in re.findall(r"\]\(/(terms|chapters|sources)/([a-z0-9-]+)/?\)", text):
        kind, slug = target
        pool = {"terms": term_slugs, "chapters": chapter_slugs,
                "sources": source_slugs}[kind]
        if slug not in pool:
            fails.append(f"F6 {name} links to missing /{kind}/{slug}/")

    if not is_term:
        continue

    # W3 — categories should match chapter slugs (vestigial field, keep tidy)
    cat_block = re.search(r"^categories:\n((?:  - \"[^\"]+\"\n)+)", fm, re.M)
    if cat_block:
        for cat in re.findall(r'  - "([^"]+)"', cat_block.group(1)):
            if cat not in chapter_slugs:
                warns.append(f"W3 {name} category \"{cat}\" is not a chapter slug")

    # W2 — quote length (fair-use margin)
    for entry in re.split(r"\n  - org:", "\n" + fm)[1:]:
        entry = "org:" + entry
        head = entry.splitlines()[0].strip()
        quote = re.search(r'quote:\s*"(.+?)"\n', entry, re.S)
        if quote and len(quote.group(1).split()) > 50:
            warns.append(f"W2 {name} quote >50 words "
                         f"({len(quote.group(1).split())}): {head[:40]}")

    # W1 — related_terms that resolve nowhere (page, alias, or glossary)
    for slug in re.findall(r'^  - slug: "([a-z0-9-]+)"', fm, re.M):
        if (slug not in term_slugs and slug not in alias_slugs
                and slug not in glossary_slugs):
            warns.append(f"W1 {name} related_terms → \"{slug}\" resolves to "
                         "no page, alias, or glossary entry")

# W6 — coverage completeness: every >=3-source glossary term is either a
# page, an alias of a page, or carries a documented decision.
if _gidx is not None:
    decided = set()
    if os.path.exists(COVERAGE_DECISIONS):
        for line in open(COVERAGE_DECISIONS):
            dm = re.match(r'^- term: "(.*)"', line.strip())
            if dm:
                decided.add(_slugify(dm.group(1)))
    for tkey, entry in _gidx.get("entries", {}).items():
        if entry.get("source_count", 0) < 3:
            continue
        if entry.get("commons_slug"):
            continue
        tslug = _slugify(tkey)
        if tslug in term_slugs or tslug in alias_slugs or tslug in decided:
            continue
        warns.append(f"W6 coverage: \"{tkey}\" has {entry['source_count']} "
                     "sources but no page, alias, or coverage decision")

for w in warns:
    print(f"WARN  {w}")
for f in fails:
    print(f"FAIL  {f}")

n_files = len(all_content)
print(f"\nlint-content: {n_files} files checked — "
      f"{len(fails)} failure(s), {len(warns)} warning(s)"
      + (" [--strict]" if strict else ""))

sys.exit(1 if fails or (strict and warns) else 0)
