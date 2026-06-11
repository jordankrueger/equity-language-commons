#!/usr/bin/env python3
"""Build a single printable HTML (and optionally PDF) of the whole commons.

Reads the BUILT site (site/dist) so the export shows exactly what's published,
ordered for linear reading: front matter (about, methodology), then each
chapter followed by its term pages in the chapter's own term_slugs order,
then the source pages. Glossary, search, and contribute are skipped (not
useful on paper).

Usage:
  ./scripts/build-print-export.py                       # full export
  ./scripts/build-print-export.py --dist path/to/dist   # explicit dist
  ./scripts/build-print-export.py --out print-export/elc.html
  ./scripts/build-print-export.py --slugs racism,white  # subset of terms

PDF: render the output HTML with headless Chrome (see --pdf), e.g.
  --pdf print-export/elc.pdf
which shells out to Chrome with --user-data-dir=/tmp/chrome-pdf-render
(required; without it Chrome can emit a 1.2KB stub).
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PRINT_CSS = """
@page { size: letter; margin: 0.8in 0.9in; }
* { box-sizing: border-box; }
body { font-family: Charter, Georgia, serif; font-size: 11pt; line-height: 1.5;
       color: #1a1a1a; max-width: 7in; margin: 0 auto; padding: 1rem; }
h1, h2, h3, h4 { font-family: Avenir, "Helvetica Neue", sans-serif; line-height: 1.25; }
h1 { font-size: 20pt; }
h2 { font-size: 14pt; margin-top: 1.6em; }
h3 { font-size: 12pt; }
a { color: inherit; text-decoration: none; }
a[href^="http"]::after { content: ""; } /* no URL dumps in print */
blockquote { border-left: 3px solid #999; margin-left: 0; padding-left: 1em; color: #333; }
table { border-collapse: collapse; font-size: 9.5pt; }
th, td { border: 1px solid #bbb; padding: 0.25em 0.5em; text-align: left; }
.print-cover { text-align: center; padding-top: 3in; }
.print-cover h1 { font-size: 28pt; }
.print-section { page-break-before: always; }
.print-term { page-break-before: always; }
.print-toc ul { list-style: none; padding-left: 0; column-count: 2; }
.print-toc li { margin: 0.15em 0; }
.print-meta { color: #555; font-size: 9pt; }
.breadcrumb, nav, script, .site-header, .site-footer { display: none !important; }
/* keep guidance cards readable in monochrome */
[class*="badge"], [class*="rec-"] { border: 1px solid #555; padding: 0 0.35em;
  border-radius: 3px; font-family: Avenir, sans-serif; font-size: 8.5pt;
  text-transform: uppercase; letter-spacing: 0.04em; }
img { max-width: 100%; }
h2, h3 { page-break-after: avoid; }
blockquote, li { page-break-inside: avoid; }
"""


def parse_chapter_meta(content_dir: Path):
    """Order + term_slugs per chapter from content frontmatter (line-based)."""
    chapters = []
    for f in sorted((content_dir / "chapters").glob("*.md")):
        order, title, slugs, in_slugs = 999, f.stem, [], False
        for line in f.read_text().splitlines():
            if line.startswith("order:"):
                order = int(line.split(":", 1)[1].strip())
            elif line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("term_slugs:"):
                in_slugs = True
            elif in_slugs:
                m = re.match(r'\s+-\s+"?([a-z0-9-]+)"?\s*$', line)
                if m:
                    slugs.append(m.group(1))
                elif not line.startswith(" "):
                    in_slugs = False
        chapters.append({"slug": f.stem, "title": title, "order": order, "terms": slugs})
    return sorted(chapters, key=lambda c: c["order"])


def extract_main(dist: Path, rel: str):
    """Return the <main> innerHTML of a built page, or None if missing."""
    page = dist / rel / "index.html"
    if not page.exists():
        return None
    soup = BeautifulSoup(page.read_text(), "html.parser")
    main = soup.find("main")
    if main is None:
        return None
    for crumb in main.select(".breadcrumb"):
        crumb.decompose()
    return main.decode_contents()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=str(ROOT / "site" / "dist"))
    ap.add_argument("--content", default=str(ROOT / "site" / "src" / "content"))
    ap.add_argument("--out", default=str(ROOT / "print-export" / "elc-print.html"))
    ap.add_argument("--pdf", help="also render a PDF to this path via headless Chrome")
    ap.add_argument("--slugs", help="comma list: restrict term pages to these slugs")
    args = ap.parse_args()

    dist, content = Path(args.dist), Path(args.content)
    if not dist.exists():
        sys.exit(f"dist not found: {dist} — run npm run build first")

    only = set(args.slugs.split(",")) if args.slugs else None
    chapters = parse_chapter_meta(content)
    parts, toc, missing = [], [], []

    def add(rel, cls, label=None):
        html = extract_main(dist, rel)
        if html is None:
            missing.append(rel)
            return
        parts.append(f'<article class="{cls}" id="{rel.replace("/", "-")}">{html}</article>')
        if label:
            toc.append(label)

    # front matter
    add("about", "print-section", "About the commons")
    add("methodology", "print-section", "Methodology")

    # chapters + their terms
    seen = set()
    for ch in chapters:
        add(f'chapters/{ch["slug"]}', "print-section", f'Chapter: {ch["title"]}')
        for slug in ch["terms"]:
            if only and slug not in only:
                continue
            seen.add(slug)
            add(f"terms/{slug}", "print-term")

    # terms not registered to any chapter (shouldn't happen, but don't drop silently)
    all_terms = {p.name for p in (dist / "terms").iterdir() if p.is_dir()}
    orphans = sorted(all_terms - seen) if not only else []
    if orphans:
        parts.append('<article class="print-section"><h1>Terms not in any chapter</h1></article>')
        toc.append(f"Unchaptered terms ({len(orphans)})")
        for slug in orphans:
            add(f"terms/{slug}", "print-term")

    # sources
    parts.append('<article class="print-section"><h1>Sources</h1>'
                 "<p>Every source guide cited in the commons, with access posture "
                 "and the terms that draw on it.</p></article>")
    toc.append("Sources")
    src_slugs = sorted(p.name for p in (dist / "sources").iterdir() if p.is_dir())
    for slug in src_slugs:
        add(f"sources/{slug}", "print-term")

    n_terms = len(seen) + len(orphans)
    today = date.today().isoformat()
    toc_html = "".join(f"<li>{t}</li>" for t in toc)
    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Equity Language Commons — print export {today}</title>
<style>{PRINT_CSS}</style></head><body>
<div class="print-cover">
  <h1>Equity Language Commons</h1>
  <p>Full review export &middot; {today}</p>
  <p class="print-meta">{n_terms} term pages &middot; {len(chapters)} chapters &middot; {len(src_slugs)} source pages<br>
  Built from the deployed site content. Quotes verified against archived sources (Layer 1);
  synthesis claims audited against excerpts (Layer 2).</p>
</div>
<div class="print-section print-toc"><h1>Contents</h1><ul>{toc_html}</ul></div>
{"".join(parts)}
</body></html>"""

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    print(f"wrote {out} ({len(doc) // 1024} KB, {n_terms} terms, {len(src_slugs)} sources)")
    if missing:
        print(f"WARNING — {len(missing)} pages not found in dist: {', '.join(missing)}")
    if orphans:
        print(f"note: {len(orphans)} terms were in no chapter: {', '.join(orphans)}")

    if args.pdf:
        pdf = Path(args.pdf).resolve()
        pdf.parent.mkdir(parents=True, exist_ok=True)
        # check=False: Chrome can be OOM-killed (exit 137) AFTER writing a
        # complete, valid PDF on big documents — judge by the artifact, not
        # the exit code.
        result = subprocess.run([CHROME, "--headless", "--disable-gpu",
                                 "--user-data-dir=/tmp/chrome-pdf-render",
                                 "--no-pdf-header-footer",
                                 f"--print-to-pdf={pdf}", out.resolve().as_uri()],
                                check=False, capture_output=True, timeout=600)
        size = pdf.stat().st_size if pdf.exists() else 0
        if size < 100_000 or b"%%EOF" not in pdf.read_bytes()[-1024:]:
            sys.exit(f"PDF missing/truncated ({size // 1024} KB, Chrome exit "
                     f"{result.returncode}) — stub-render or failed write.")
        print(f"wrote {pdf} ({size // 1024} KB, Chrome exit {result.returncode})")


if __name__ == "__main__":
    main()
