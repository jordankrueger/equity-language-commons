#!/usr/bin/env python3
"""
fetch-source-about-material.py — Phase 2.6 #3 research staging.

Gathers background material for source-page About sections without modifying
the live content pages. For each source page, reads frontmatter from
site/src/content/sources/, then stages raw research material in
research/source-about-material/<org_slug>.md:
  - Known facts from source-page frontmatter + MANIFEST
  - Wikipedia REST summary, when a mapped page exists
  - Org homepage raw text excerpt, machine-stripped from HTML
  - Manual-research checklist

Default scope is source pages with `stub: true`. Use `--all` to include filled
pages. Use `--no-net` to emit packets from local facts only.

Usage:
  ./scripts/fetch-source-about-material.py              # fetch + write packets
  ./scripts/fetch-source-about-material.py --check-only # list planned set
  ./scripts/fetch-source-about-material.py --all        # include non-stubs
  ./scripts/fetch-source-about-material.py --no-net     # no external fetches

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "site" / "src" / "content" / "sources"
MANIFEST = PROJECT_ROOT / "source-guides" / "MANIFEST.md"
OUT_DIR = PROJECT_ROOT / "research" / "source-about-material"
INDEX_PATH = OUT_DIR / "INDEX.md"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) equity-language-commons/0.1 (+fetch-source-about-material.py)"
)
HTTP_TIMEOUT = 10  # seconds
WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
EXCERPT_CHARS = 1500

# Copied from scaffold-source-pages.py so homepage fallbacks stay consistent.
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

# Best-effort org_slug -> Wikipedia page title map. Missing or 404 pages are
# expected for niche projects; packets record those as UNVERIFIED.
ORG_WIKIPEDIA = {
    "aecf": "Annie_E._Casey_Foundation",
    "apa": "American_Psychological_Association",
    "color-of-change": "Color_of_Change",
    "define-american": "Define_American",
    "diversity-style-guide": "Diversity_Style_Guide",
    "elements-of-indigenous-style": "Gregory_Younging",
    "gcjt": "Dart_Center_for_Journalism_and_Trauma",
    "hrc": "Human_Rights_Campaign",
    "idp": "Immigrant_Defense_Project",
    "interact": "InterACT",
    "nabj": "National_Association_of_Black_Journalists",
    "naja": "Indigenous_Journalists_Association",
    "ncdj": "National_Center_on_Disability_and_Journalism",
    "ngc": "Native_Governance_Center",
    "nlgja": "NLGJA:_The_Association_of_LGBTQ_Journalists",
    "racial-equity-tools": "Racial_Equity_Tools",
    "seiu": "Service_Employees_International_Union",
    "sierra-club": "Sierra_Club",
    "sumofus": "SumOfUs",
    "tja": "Trans_Journalists_Association",
    "un-cobo-1972": "José_R._Martínez_Cobo",
}

FRONTMATTER_KEY = re.compile(r"^([a-zA-Z_]+):(?:\s+(.*))?$")


@dataclass
class SourcePage:
    page_slug: str
    path: Path
    org: str
    org_slug: str
    source_url: str
    work_title: str
    year: str
    host_posture: str
    stub: bool
    local_archive: str
    manifest_scope: str


@dataclass
class ManifestEntry:
    filename: str
    org: str
    title: str
    year: int
    scope: str
    host_posture: str


@dataclass
class WikiResult:
    status: str
    title: str
    url: str
    confidence: str
    text: str


@dataclass
class HomepageResult:
    status: str
    url: str
    confidence: str
    text: str


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        elif tag.lower() in {"p", "div", "section", "article", "header", "footer", "br", "li", "h1", "h2", "h3"}:
            self._chunks.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        elif tag.lower() in {"p", "div", "section", "article", "header", "footer", "li", "h1", "h2", "h3"}:
            self._chunks.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._chunks.append(data)

    def text(self) -> str:
        return normalize_ws(" ".join(self._chunks))


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def strip_yaml_string(s: str | None) -> str:
    if s is None:
        return ""
    s = s.strip()
    if s in ("", "null"):
        return ""
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def parse_frontmatter_scalars(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line.startswith((" ", "\t")):
            continue
        m = FRONTMATTER_KEY.match(line)
        if m and m.group(2) is not None:
            out[m.group(1)] = m.group(2).strip()
    return out


def strip_backticks(s: str) -> str:
    s = s.strip()
    if s.startswith("`") and s.endswith("`"):
        return s[1:-1]
    return s


def extract_year(s: str) -> int:
    m = re.search(r"\b(19|20)\d{2}\b", s)
    return int(m.group(0)) if m else 0


def classify_host(host_text: str) -> str:
    h = host_text.strip().lower()
    if h.startswith("archive"):
        return "host-publicly"
    if h.startswith("reference"):
        return "link-out-only"
    return "private-mirror-link-out"


def parse_manifest() -> dict[str, ManifestEntry]:
    text = MANIFEST.read_text(encoding="utf-8")
    entries: dict[str, ManifestEntry] = {}
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
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
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cells) < 6:
            continue
        fname = strip_backticks(cells[0])
        if not fname:
            continue
        entries[fname] = ManifestEntry(
            filename=fname,
            org=cells[1].strip(),
            title=cells[2].strip(),
            year=extract_year(cells[3]),
            scope=cells[4].strip(),
            host_posture=classify_host(cells[5]),
        )
    return entries


def manifest_scope_for(fm: dict[str, str], manifest: dict[str, ManifestEntry]) -> str:
    local_archive = strip_yaml_string(fm.get("local_archive"))
    if local_archive:
        archive_name = Path(local_archive).name
        if archive_name in manifest:
            return manifest[archive_name].scope
    work_title = strip_yaml_string(fm.get("work_title")).lower()
    org = strip_yaml_string(fm.get("org")).lower()
    for entry in manifest.values():
        if entry.org.lower() == org and (
            entry.title.lower() in work_title or work_title in entry.title.lower()
        ):
            return entry.scope
    return "unknown"


def load_source_pages(include_all: bool) -> list[SourcePage]:
    manifest = parse_manifest()
    pages: list[SourcePage] = []
    for path in sorted(SOURCES_DIR.glob("*.md")):
        fm = parse_frontmatter_scalars(path.read_text(encoding="utf-8"))
        stub = strip_yaml_string(fm.get("stub")).lower() == "true"
        if not include_all and not stub:
            continue
        org = strip_yaml_string(fm.get("org"))
        org_slug = strip_yaml_string(fm.get("org_slug")) or path.stem
        pages.append(
            SourcePage(
                page_slug=path.stem,
                path=path,
                org=org,
                org_slug=org_slug,
                source_url=strip_yaml_string(fm.get("source_url")),
                work_title=strip_yaml_string(fm.get("work_title")),
                year=strip_yaml_string(fm.get("year")),
                host_posture=strip_yaml_string(fm.get("host_posture")),
                stub=stub,
                local_archive=strip_yaml_string(fm.get("local_archive")),
                manifest_scope=manifest_scope_for(fm, manifest),
            )
        )
    return pages


def group_by_org_slug(pages: list[SourcePage]) -> dict[str, list[SourcePage]]:
    grouped: dict[str, list[SourcePage]] = {}
    for page in pages:
        grouped.setdefault(page.org_slug, []).append(page)
    return grouped


def fetch_url(url: str, *, headers: dict[str, str] | None = None) -> tuple[int, str, str, str]:
    """HEAD -> ranged GET -> GET. Returns (status_code, final_url, text, note)."""
    attempts = [
        ("HEAD", {}, "HEAD"),
        ("GET", {"Range": "bytes=0-50000"}, "GET-range"),
        ("GET", {}, "GET"),
    ]
    for method, extra_headers, label in attempts:
        merged = {"User-Agent": USER_AGENT, **(headers or {}), **extra_headers}
        req = urllib.request.Request(url, method=method, headers=merged)
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                code = resp.getcode()
                if method == "HEAD":
                    if 200 <= code < 400:
                        continue
                    return code, resp.geturl(), "", f"{label} {code}"
                raw = resp.read()
                charset = resp.headers.get_content_charset() or "utf-8"
                text = raw.decode(charset, errors="replace")
                return code, resp.geturl(), text, f"{label} {code}"
        except urllib.error.HTTPError as e:
            if e.code in (405, 501) and method != "GET":
                continue
            if method == "HEAD":
                continue
            return e.code, url, "", f"{label} {e.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return 0, url, "", f"{type(e).__name__}: {e}"
    return 0, url, "", "all methods exhausted"


def fetch_get(url: str, *, headers: dict[str, str] | None = None) -> tuple[int, str, str, str]:
    merged = {"User-Agent": USER_AGENT, **(headers or {})}
    req = urllib.request.Request(url, method="GET", headers=merged)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.getcode(), resp.geturl(), raw.decode(charset, errors="replace"), f"GET {resp.getcode()}"
    except urllib.error.HTTPError as e:
        return e.code, url, "", f"GET {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, url, "", f"{type(e).__name__}: {e}"


def fetch_wikipedia(org_slug: str) -> WikiResult:
    title = ORG_WIKIPEDIA.get(org_slug, "")
    if not title:
        return WikiResult(
            status="no-title",
            title="",
            url="none",
            confidence="UNVERIFIED",
            text=f"No Wikipedia title mapped for {org_slug}.",
        )
    api_url = WIKI_API.format(urllib.parse.quote(title, safe=""))
    code, final_url, text, note = fetch_get(api_url, headers={"Accept": "application/json"})
    if code == 404:
        return WikiResult(
            status="no-page",
            title=title,
            url=f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title, safe=':_')}",
            confidence="UNVERIFIED",
            text=f"No Wikipedia entry found for {title}. ({note})",
        )
    if not (200 <= code < 300) or not text:
        return WikiResult(
            status="failed",
            title=title,
            url=final_url or api_url,
            confidence="UNVERIFIED",
            text=f"Wikipedia summary fetch failed for {title}. ({note})",
        )
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return WikiResult(
            status="failed",
            title=title,
            url=final_url or api_url,
            confidence="UNVERIFIED",
            text=f"Wikipedia summary JSON parse failed for {title}: {e}",
        )
    extract = normalize_ws(str(data.get("extract") or ""))
    page_url = (
        data.get("content_urls", {})
        .get("desktop", {})
        .get("page")
        or f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title, safe=':_')}"
    )
    if not extract:
        return WikiResult(
            status="no-extract",
            title=title,
            url=page_url,
            confidence="UNVERIFIED",
            text=f"Wikipedia entry found for {title}, but no extract was returned.",
        )
    return WikiResult(
        status="yes",
        title=title,
        url=page_url,
        confidence="VERIFIED",
        text=extract,
    )


def homepage_seed(pages: list[SourcePage]) -> str:
    for page in pages:
        if page.source_url:
            parsed = urllib.parse.urlparse(page.source_url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}/"
    return KNOWN_URLS.get(pages[0].org_slug, "")


def fetch_homepage(pages: list[SourcePage]) -> HomepageResult:
    url = homepage_seed(pages)
    if not url:
        return HomepageResult(
            status="skipped",
            url="none",
            confidence="UNVERIFIED",
            text="No source_url domain or KNOWN_URLS fallback available.",
        )
    code, final_url, html, note = fetch_url(url)
    if not (200 <= code < 300) or not html:
        return HomepageResult(
            status="failed",
            url=final_url or url,
            confidence="UNVERIFIED",
            text=f"Homepage fetch failed. ({note})",
        )
    parser = TextExtractor()
    parser.feed(html)
    extracted = parser.text()
    if not extracted:
        return HomepageResult(
            status="failed",
            url=final_url or url,
            confidence="UNVERIFIED",
            text="Homepage fetched, but no readable text was extracted.",
        )
    return HomepageResult(
        status="yes",
        url=final_url or url,
        confidence="PARTIAL",
        text=extracted[:EXCERPT_CHARS].rstrip(),
    )


def no_net_wiki(org_slug: str) -> WikiResult:
    title = ORG_WIKIPEDIA.get(org_slug, "")
    if title:
        text = f"Network disabled; Wikipedia title mapped but not fetched: {title}."
    else:
        text = f"Network disabled; no Wikipedia title mapped for {org_slug}."
    return WikiResult(
        status="skipped",
        title=title,
        url="not fetched (--no-net)",
        confidence="UNVERIFIED",
        text=text,
    )


def no_net_homepage(pages: list[SourcePage]) -> HomepageResult:
    url = homepage_seed(pages)
    if url:
        text = f"Network disabled; homepage seed not fetched: {url}."
    else:
        text = "Network disabled; no source_url domain or KNOWN_URLS fallback available."
    return HomepageResult(
        status="skipped",
        url=url or "none",
        confidence="UNVERIFIED",
        text=text,
    )


def markdown_escape(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n").strip()


def render_packet(pages: list[SourcePage], wiki: WikiResult, homepage: HomepageResult, today: str) -> str:
    first = pages[0]
    facts = []
    for page in pages:
        facts.append(
            "\n".join(
                [
                    f"- Source page: `site/src/content/sources/{page.page_slug}.md`",
                    f"  - Work: {page.work_title or 'unknown'} ({page.year or 'unknown year'})",
                    f"  - Host posture: {page.host_posture or 'unknown'}",
                    f"  - Original URL: {page.source_url or 'none on file'}",
                    f"  - Local archive: {page.local_archive or 'none on file'}",
                    f"  - Scope (MANIFEST): {page.manifest_scope}",
                ]
            )
        )
    facts_block = "\n".join(facts)
    wiki_text = markdown_escape(wiki.text)
    homepage_text = markdown_escape(homepage.text)
    return f"""# About material — {first.org} ({first.org_slug})

> STAGING FILE — raw research material for writing the source page About section.
> Not published. Claude writes the final About prose from this; a human approves
> before `stub: true` is removed from the matching source page.

Generated: {today}

## Known facts (from MANIFEST + frontmatter)
{facts_block}

## Wikipedia summary
- Source: {wiki.url}  ·  Accessed: {today}  ·  Confidence: {wiki.confidence}

{wiki_text}

## Org homepage (raw extract)
- Source: {homepage.url}  ·  Accessed: {today}  ·  Confidence: {homepage.confidence}

{homepage_text}

## Still needs manual research
- [ ] Founding year / mission (if not above)
- [ ] Why this guide exists / its scope and intended audience
- [ ] Access/host-posture rationale specific to this org
- [ ] Confirm copyright holder + any reuse license
"""


def wiki_yes_no(status: str) -> str:
    return "yes" if status == "yes" else "no"


def homepage_yes_no(status: str) -> str:
    if status == "yes":
        return "yes"
    if status == "failed":
        return "failed"
    return "no"


def write_index(rows: list[tuple[str, list[SourcePage], WikiResult, HomepageResult]], today: str) -> None:
    lines = [
        "# Source About Material Index",
        "",
        f"Generated: {today}",
        "",
        "| org_slug | source pages | wiki | homepage | packet |",
        "|----------|--------------|------|----------|--------|",
    ]
    for org_slug, pages, wiki, homepage in rows:
        page_names = ", ".join(page.page_slug for page in pages)
        lines.append(
            f"| `{org_slug}` | {page_names} | {wiki_yes_no(wiki.status)} | "
            f"{homepage_yes_no(homepage.status)} | `{org_slug}.md` |"
        )
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_check_only(pages: list[SourcePage]) -> None:
    print(f"planned source pages: {len(pages)}")
    grouped = group_by_org_slug(pages)
    print(f"planned packets: {len(grouped)}")
    for page in pages:
        print(f"- {page.page_slug}  org_slug={page.org_slug}  org={page.org}")
    duplicate_groups = {k: v for k, v in grouped.items() if len(v) > 1}
    if duplicate_groups:
        print("\nduplicate org_slug groups will be combined into one packet each:")
        for org_slug, group in duplicate_groups.items():
            print(f"- {org_slug}: {', '.join(page.page_slug for page in group)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check-only", action="store_true", help="list planned set without fetching or writing")
    parser.add_argument("--all", action="store_true", help="include non-stub source pages")
    parser.add_argument("--no-net", action="store_true", help="skip external fetches and write local-facts-only packets")
    args = parser.parse_args()

    pages = load_source_pages(include_all=args.all)
    if not pages:
        print("no matching source pages found", file=sys.stderr)
        return 1
    if args.check_only:
        print_check_only(pages)
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    rows: list[tuple[str, list[SourcePage], WikiResult, HomepageResult]] = []
    grouped = group_by_org_slug(pages)
    for org_slug, group in sorted(grouped.items()):
        if args.no_net:
            wiki = no_net_wiki(org_slug)
            homepage = no_net_homepage(group)
        else:
            wiki = fetch_wikipedia(org_slug)
            homepage = fetch_homepage(group)
        packet = render_packet(group, wiki, homepage, today)
        out_path = OUT_DIR / f"{org_slug}.md"
        out_path.write_text(packet, encoding="utf-8")
        rows.append((org_slug, group, wiki, homepage))
        print(
            f"wrote {out_path.relative_to(PROJECT_ROOT)} "
            f"(wiki={wiki_yes_no(wiki.status)}, homepage={homepage_yes_no(homepage.status)})",
            file=sys.stderr,
        )

    write_index(rows, today)
    print(f"\nwrote {len(rows)} packets + {INDEX_PATH.relative_to(PROJECT_ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
