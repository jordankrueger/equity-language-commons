#!/usr/bin/env python3
"""Fail when generated glossary rows regress into duplicate or misplaced entries."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site/src/data/glossary-index.json"
data = json.loads(path.read_text())
rows = data["rows"]
by_letter = data["by_letter"]
aliases = data["aliases_by_commons_slug"]

listed = [key for keys in by_letter.values() for key in keys]
assert len(listed) == len(set(listed)) == len(rows), "rows must appear exactly once"
assert data["stats"]["visible_rows"] == len(rows), "visible row count is stale"
assert data["stats"]["visible_canonical_rows"] == sum(row["tier"] in {"verified-hold", "curated"} for row in rows.values())
assert data["stats"]["visible_listed_rows"] == sum(row["tier"] == "listed" for row in rows.values())

for letter, keys in by_letter.items():
    for key in keys:
        display = rows[key]["display"]
        expected = display[0].lower() if display and display[0].isalpha() else "#"
        assert letter == expected, f"{display!r} is under {letter.upper()}, expected {expected.upper()}"

assert [rows[key]["display"] for key in by_letter["c"]].count("Crazy") == 1
assert [rows[key]["display"] for key in by_letter["l"]].count("Little Person") == 1
for slug, items in aliases.items():
    terms = [item["term"] for item in items]
    assert len(terms) == len(set(terms)), f"duplicate aliases for {slug}"
    assert slug not in terms, f"self-alias for {slug}"

org_slugs = set()
for source in (ROOT / "site/src/content/sources").glob("*.md"):
    match = re.search(r"^org_slug:\s*[\"']?([^\s\"']+)", source.read_text(), re.M)
    if match:
        org_slugs.add(match.group(1))
for entry in data["entries"].values():
    for source in entry["sources"]:
        assert source["source_slug"] in org_slugs, f"bad source route: {source['source_slug']}"
    canonical = entry.get("canonical_source")
    if canonical:
        assert canonical["source_page_url"] == f"/sources/{canonical['source_slug']}/", "bad canonical route"

print(f"Glossary index OK: {len(rows)} unique rows")
