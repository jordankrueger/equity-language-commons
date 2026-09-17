#!/usr/bin/env python3
"""
scaffold-source-pages.py — Phase 2.6 #1b tooling.

Walks the coverage matrix for source slugs that don't yet have a corresponding
page in site/src/content/sources/, looks up each one's metadata in
source-guides/MANIFEST.md, and writes a stub source page with proper
frontmatter + boilerplate About/Access body.

The stub is immediately usable: scaffold-term.py will pick up the new pages
and stop skipping their guidance entries. After running this, run
enrich-source-pages.py to fill mechanical fields (length_pages, live_status,
last_checked).

Idempotent — only creates pages that don't exist; existing pages untouched.

Usage:
  ./scripts/scaffold-source-pages.py              # create missing stubs
  ./scripts/scaffold-source-pages.py --check-only # report what would be created

Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from lib import (
    PROJECT_ROOT,
    SOURCE_ROOTS,
    build_pdf_to_md_index,
    parse_frontmatter_scalars,
    strip_yaml_string,
    yaml_escape,
)

MATRIX_CSV = PROJECT_ROOT / "notes" / "term-coverage-matrix.csv"
SOURCES_DIR = PROJECT_ROOT / "site" / "src" / "content" / "sources"
MANIFEST = PROJECT_ROOT / "source-guides" / "MANIFEST.md"

# Org → short slug. The schema's `org_slug` field is what term-pages cite, and
# the project convention is abbreviations for well-known orgs (NAJA not Native
# American Journalists Association, NGC not Native Governance Center).
ORG_SLUG_OVERRIDES = {
    "Annie E. Casey Foundation": "aecf",
    "Native Governance Center": "ngc",
    "NAJA": "naja",
    "NAJA / Indigenous Journalists Association": "naja",
    "Native American Journalists Association": "naja",
    "Trans Journalists Association": "tja",
    "National Center on Disability and Journalism": "ncdj",
    "NLGJA": "nlgja",
    "NLGJA: The Association of LGBTQ+ Journalists": "nlgja",
    "Human Rights Campaign": "hrc",
    "American Psychological Association": "apa",
    "Diversity Style Guide": "diversity-style-guide",
    "SF State / Diversity Style Guide": "diversity-style-guide",
    "NABJ": "nabj",
    "AAJA": "aaja",
    "GLAAD": "glaad",
    "Color of Change": "color-of-change",
    "Immigrant Defense Project": "idp",
    "Define American": "define-american",
    "interACT Advocates for Intersex Youth": "interact",
    "interACT": "interact",
    "Global Consortium for Journalism & Trauma (fmr. Dart Center)": "gcjt",
    "Global Consortium for Journalism & Trauma": "gcjt",
    "WFP USA": "wfpusa",
    "David Vine / American University": "wordsaboutwar",
    "Alex Kapitan / Radical Copyeditor": "radical-copyeditor",
    "Sierra Club": "sierra-club",
    "SumOfUs (defunct; merged into Ekō 2022)": "sumofus",
    "SumOfUs": "sumofus",
    "Racial Equity Tools": "racial-equity-tools",
    "SEIU": "seiu",
    "Stand.earth": "stand-earth",
    "Youth Leadership Institute": "yli",
    "Conscious Style Guide": "conscious-style-guide",
}

# Optional canonical URLs for orgs whose URLs aren't easy to derive from the
# org name alone. Leaving an entry out is fine — script falls back to null.
KNOWN_URLS = {
    "hrc": "https://www.hrc.org/resources/glossary-of-terms",
    "nabj": "https://www.nabj.org/page/styleguide",
    "color-of-change": "https://colorofchange.org/resources/",
    "define-american": "https://defineamerican.com/resources-for-journalists/",
    "idp": "https://www.immigrantdefenseproject.org/",
    "interact": "https://interactadvocates.org/",
    "wordsaboutwar": "https://wordsaboutwarmatter.org/",
    "wfpusa": "https://www.wfpusa.org/",
    "naja": "https://indigenousjournalists.org/ap-style-insert/",
}


@dataclass
class ManifestEntry:
    filename: str           # e.g. "hrc-glossary-2023-05.md" — as written in MANIFEST
    org: str
    title: str
    year: int
    host_posture: str       # mapped enum value
    scope: str              # In / Partial / Out — informational only


# ---------- MANIFEST parsing ----------

def _strip_backticks(s: str) -> str:
    s = s.strip()
    if s.startswith("`") and s.endswith("`"):
        return s[1:-1]
    return s


def _extract_year(s: str) -> int:
    """'Jul 2020', '2017 (last revision Feb 2025)', 'Jan 2024' → first 4-digit year."""
    m = re.search(r"\b(19|20)\d{2}\b", s)
    return int(m.group(0)) if m else 0


def _classify_host(host_text: str) -> str:
    """MANIFEST 'Host' column (free text) → host_posture enum value.
    Legend (from MANIFEST):
      Link — active org, link out only. Don't republish.
      Archive — orphan work or permission granted. OK to host locally.
      Reference — book or paid work. Cite only, never host.
    Project rule: even 'Link' guides get a private preservation copy
    for citation verification, so 'Link' → 'private-mirror-link-out'."""
    h = host_text.strip().lower()
    if h.startswith("archive"):
        return "host-publicly"
    if h.startswith("reference"):
        return "link-out-only"
    # Default: any "Link..." or anything else → private mirror + link-out,
    # which is the safest enum value the schema accepts for active orgs.
    return "private-mirror-link-out"


def parse_manifest() -> dict[str, ManifestEntry]:
    """Returns: filename (with extension) → ManifestEntry. Filename is the
    key because that's what's quoted in the MANIFEST tables — caller can
    derive matrix slugs by stripping the extension and applying the
    extract-pdfs.sh slug rules."""
    text = MANIFEST.read_text(encoding="utf-8")
    entries: dict[str, ManifestEntry] = {}
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        # Section transitions reset table state.
        if stripped.startswith("##"):
            in_table = False
            continue
        if stripped.startswith("| File |"):
            in_table = True
            continue
        if stripped.startswith("|------"):
            continue
        if not in_table or not stripped.startswith("|"):
            continue
        # Data row. Split on |, drop leading/trailing empties from outer pipes.
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 6:
            continue
        fname = _strip_backticks(cells[0])
        if not fname:
            continue
        entries[fname] = ManifestEntry(
            filename=fname,
            org=cells[1].strip(),
            title=cells[2].strip(),
            year=_extract_year(cells[3]),
            scope=cells[4].strip(),
            host_posture=_classify_host(cells[5]),
        )
    return entries


# ---------- existing-pages enumeration ----------

def represented_matrix_slugs(pdf_to_md: dict[str, Path]) -> set[str]:
    """Returns the set of matrix-source slugs already covered by an existing
    source page (i.e., whose local_archive resolves to a .md file we'd find
    in the matrix)."""
    covered: set[str] = set()
    for f in SOURCES_DIR.glob("*.md"):
        fm = parse_frontmatter_scalars(f.read_text(encoding="utf-8"))
        archive = strip_yaml_string(fm.get("local_archive", ""))
        if not archive:
            continue
        arch_path = Path(archive)
        if arch_path.suffix.lower() == ".md":
            md = PROJECT_ROOT / arch_path
        elif arch_path.suffix.lower() == ".pdf":
            md = pdf_to_md.get(arch_path.name)
        else:
            md = None
        if md and md.exists():
            covered.add(md.stem)
    return covered


def all_matrix_source_slugs() -> set[str]:
    slugs: set[str] = set()
    with MATRIX_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            slugs.add(row["source_slug"])
    return slugs


# ---------- orphan resolution ----------

def matrix_slug_to_manifest_filename(matrix_slug: str, md_to_pdf: dict[str, str]) -> str | None:
    """Matrix slug is the .md stem of the source-guides file. MANIFEST keys
    are filenames with extension — but the .md and .pdf in source-guides/
    can have *different* base names because extract-pdfs.sh slugifies
    archived PDFs. So we resolve by walking the source-guides tree."""
    target_md_name = matrix_slug + ".md"
    if target_md_name in md_to_pdf:
        return md_to_pdf[target_md_name]  # MANIFEST key is the original PDF name
    # Discovered-folder .md files are listed in MANIFEST under their own .md name.
    return target_md_name


def derive_org_slug(org: str, fallback_from_filename: str) -> str:
    if org in ORG_SLUG_OVERRIDES:
        return ORG_SLUG_OVERRIDES[org]
    # Fallback: snake-case the first word of the filename.
    return re.split(r"[-_]", fallback_from_filename)[0].lower()


def derive_local_archive_path(matrix_slug: str, manifest_filename: str) -> str:
    """Returns the path relative to project root that the source page should
    cite as local_archive. Prefer the original (often PDF) when the MANIFEST
    references a PDF, else the .md sibling itself."""
    for root in SOURCE_ROOTS:
        candidate = root / manifest_filename
        if candidate.exists():
            return str(candidate.relative_to(PROJECT_ROOT))
    # Fall back to the .md file directly.
    for root in SOURCE_ROOTS:
        candidate = root / (matrix_slug + ".md")
        if candidate.exists():
            return str(candidate.relative_to(PROJECT_ROOT))
    return ""


# ---------- source-page rendering ----------

def build_stub(*, page_slug: str, org: str, org_slug: str, work_title: str,
               year: int, source_url: str | None, local_archive: str,
               host_posture: str, today: str) -> str:
    url_line = (
        f"source_url: {yaml_escape(source_url)}" if source_url else "source_url: null"
    )
    return f"""---
org: {yaml_escape(org)}
org_slug: {yaml_escape(org_slug)}
work_title: {yaml_escape(work_title)}
year: {year}
{url_line}
local_archive: {yaml_escape(local_archive)}
host_posture: "{host_posture}"
live_status: "live"
added: {today}
last_checked: {today}
stub: true
---

## About

*Source stub — about section pending.* This page exists so term entries that cite {org} can link to a source page. Full publication details, host-posture rationale, version history, and license findings will be filled in as Phase 2 progresses.

## Access

Posture: **{host_posture}** (provisional). Live status when last checked: **live** (provisional — run `enrich-source-pages.py` to confirm).
"""


# ---------- main ----------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check-only", action="store_true",
                        help="report what would be created without writing")
    args = parser.parse_args()

    # Build the pdf→md index once; reused by represented_matrix_slugs and
    # matrix_slug_to_manifest_filename to avoid repeated glob walks.
    pdf_to_md = build_pdf_to_md_index()
    md_to_pdf = {md.name: pdf_name for pdf_name, md in pdf_to_md.items()}

    manifest = parse_manifest()
    represented = represented_matrix_slugs(pdf_to_md)
    all_matrix = all_matrix_source_slugs()
    orphans = sorted(all_matrix - represented)

    print(f"matrix sources: {len(all_matrix)}", file=sys.stderr)
    print(f"already represented: {len(represented)}", file=sys.stderr)
    print(f"orphans to scaffold: {len(orphans)}", file=sys.stderr)
    print(f"manifest entries loaded: {len(manifest)}", file=sys.stderr)
    print(file=sys.stderr)

    today = date.today().isoformat()
    created = 0
    skipped = 0
    not_in_manifest: list[str] = []

    for matrix_slug in orphans:
        manifest_fname = matrix_slug_to_manifest_filename(matrix_slug, md_to_pdf)
        entry = manifest.get(manifest_fname) if manifest_fname else None
        if not entry:
            not_in_manifest.append(matrix_slug)
            print(f"  ⚠ no MANIFEST entry for {matrix_slug} (key tried: {manifest_fname!r}) — skipping",
                  file=sys.stderr)
            skipped += 1
            continue

        org_slug = derive_org_slug(entry.org, matrix_slug)
        local_archive = derive_local_archive_path(matrix_slug, manifest_fname)
        source_url = KNOWN_URLS.get(org_slug)
        page_slug = matrix_slug   # full unambiguous slug

        out_path = SOURCES_DIR / f"{page_slug}.md"
        if out_path.exists():
            print(f"  -  {page_slug} already exists, skipping", file=sys.stderr)
            skipped += 1
            continue

        body = build_stub(
            page_slug=page_slug,
            org=entry.org,
            org_slug=org_slug,
            work_title=entry.title,
            year=entry.year,
            source_url=source_url,
            local_archive=local_archive,
            host_posture=entry.host_posture,
            today=today,
        )

        if not args.check_only:
            out_path.write_text(body, encoding="utf-8")
        print(f"  +  {page_slug:50s}  org={org_slug:20s}  posture={entry.host_posture}",
              file=sys.stderr)
        created += 1

    print(file=sys.stderr)
    if args.check_only:
        print(f"DRY RUN — would create {created} stub source pages", file=sys.stderr)
    else:
        print(f"created {created} stub source pages, skipped {skipped}", file=sys.stderr)
        if created > 0:
            print(f"\nnext: ./scripts/enrich-source-pages.py  # fill length_pages + live_status",
                  file=sys.stderr)
    if not_in_manifest:
        print(f"\n⚠ {len(not_in_manifest)} matrix sources have no MANIFEST entry — "
              f"add them to source-guides/MANIFEST.md or update the script's "
              f"matrix_slug_to_manifest_filename() lookup:", file=sys.stderr)
        for s in not_in_manifest:
            print(f"    {s}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
