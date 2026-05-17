#!/usr/bin/env python3
"""
enrich-source-pages.py — Phase 2.5c tooling.

Pre-populates the mechanical metadata fields on every source page in
site/src/content/sources/, so the qualitative work (About section, Access-
posture rationale, version history, license findings) is the only thing that
needs human/LLM input.

For each source page:
  - If local_archive points to a PDF → run pdfinfo, fill length_pages, format
  - If source_url is set → HEAD request, set live_status + last_checked
  - Initialise `added` to today if missing

Frontmatter is updated in place line-by-line so existing values, comments,
field ordering, and multi-line structures (version_history) are preserved.
Skipped fields are never touched.

Usage:
  ./scripts/enrich-source-pages.py              # update only missing/stale fields
  ./scripts/enrich-source-pages.py --check-only # report what would change, no writes
  ./scripts/enrich-source-pages.py --force      # overwrite even if already set
  ./scripts/enrich-source-pages.py --no-net     # skip HEAD requests (PDF metadata only)

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = PROJECT_ROOT / "site" / "src" / "content" / "sources"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) equity-language-commons/0.1 (+enrich-source-pages.py)"
)
HTTP_TIMEOUT = 10  # seconds

# HTTP status → live_status enum value (matches site/src/content.config.ts LIVE_STATUS)
# Anything not in this map gets `_classify_other(code)` applied: 2xx/3xx → live,
# 4xx (other than the mapped auth/missing codes) → live with a warning, 5xx → offline.
STATUS_MAP = {
    401: "login-gated",
    403: "login-gated",
    404: "404",
    410: "404",
}


def _classify_status(code: int) -> tuple[str, str]:
    """(live_status enum, optional note)."""
    if code in STATUS_MAP:
        return STATUS_MAP[code], ""
    if 200 <= code < 400:
        return "live", ""
    if 400 <= code < 500:
        # Server responded — page exists, request was rejected (anti-bot, method,
        # rate limit). Treat as live but flag for manual verification.
        return "live", f"server returned {code} — manual check recommended"
    return "offline", f"server returned {code}"


@dataclass
class PageChange:
    path: Path
    slug: str
    updates: dict[str, str]            # key → new value (rendered for YAML)
    notes: list[str]                   # diagnostic notes for the run summary


# ---------- frontmatter parsing/writing ----------

FRONTMATTER_KEY = re.compile(r"^([a-zA-Z_]+):(?:\s+(.*))?$")


def split_frontmatter(text: str) -> tuple[list[str], str] | None:
    """Returns (frontmatter_lines, body) or None if no frontmatter found.
    Frontmatter lines exclude the surrounding `---` delimiters."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fm_text = text[4:end]
    body = text[end + 5:]
    return fm_text.splitlines(), body


def frontmatter_values(lines: list[str]) -> dict[str, str | None]:
    """Read top-level keys (column-0, no indent) and their values. Multi-line
    structures (lists/maps) collapse to a sentinel '<complex>' marker —
    we won't touch those."""
    values: dict[str, str | None] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or line.startswith(" ") or line.startswith("\t"):
            i += 1
            continue
        m = FRONTMATTER_KEY.match(line)
        if not m:
            i += 1
            continue
        key, raw_val = m.group(1), m.group(2)
        # Is the value continued on indented following lines (list/map)?
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        if (raw_val is None or raw_val == "") and next_line.startswith((" ", "\t")):
            values[key] = "<complex>"
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or lines[i] == ""):
                i += 1
            continue
        values[key] = raw_val
        i += 1
    return values


def apply_updates(lines: list[str], updates: dict[str, str]) -> list[str]:
    """Update existing top-level keys in place; append missing keys at the end."""
    out: list[str] = []
    seen: set[str] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = FRONTMATTER_KEY.match(line)
        if m and not line.startswith((" ", "\t")):
            key = m.group(1)
            if key in updates:
                out.append(f"{key}: {updates[key]}")
                seen.add(key)
                # Skip any indented continuation lines (for list/map values
                # we never rewrite, but FRONTMATTER_KEY only matches scalars,
                # so this branch only fires when we're replacing a scalar
                # with a scalar — no continuation to skip).
                i += 1
                continue
        out.append(line)
        i += 1
    for key, val in updates.items():
        if key not in seen:
            out.append(f"{key}: {val}")
    return out


def write_page(path: Path, fm_lines: list[str], body: str) -> None:
    text = "---\n" + "\n".join(fm_lines) + "\n---\n" + body
    path.write_text(text, encoding="utf-8")


# ---------- PDF metadata ----------

def pdfinfo(path: Path) -> dict[str, str]:
    """Return parsed pdfinfo key/value pairs, or {} on failure."""
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            capture_output=True, text=True, timeout=15, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}
    info = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            info[k.strip()] = v.strip()
    return info


# ---------- HTTP HEAD check ----------

def head_live_status(url: str) -> tuple[str, str]:
    """Return (live_status_enum, note). Tries HEAD, then ranged GET (for
    servers that 405 on HEAD), then bare GET (for servers that block ranged
    requests too — they're still alive, we just need a different verb)."""
    for method, headers, label in [
        ("HEAD", {}, "HEAD"),
        ("GET",  {"Range": "bytes=0-0"}, "GET-range"),
        ("GET",  {}, "GET"),
    ]:
        merged_headers = {"User-Agent": USER_AGENT, **headers}
        req = urllib.request.Request(url, method=method, headers=merged_headers)
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                code = resp.getcode()
                status, note = _classify_status(code)
                return status, f"{label} {code}" + (f" ({note})" if note else "")
        except urllib.error.HTTPError as e:
            # 405/501 means the verb isn't supported — fall through and try the
            # next method. Anything else is the final answer.
            if e.code in (405, 501) and label != "GET":
                continue
            status, note = _classify_status(e.code)
            return status, f"{label} {e.code}" + (f" ({note})" if note else "")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return "offline", f"{type(e).__name__}: {e}"
    return "offline", "all methods exhausted"


# ---------- per-page enricher ----------

def enrich(path: Path, force: bool, no_net: bool) -> PageChange:
    slug = path.stem
    text = path.read_text(encoding="utf-8")
    parsed = split_frontmatter(text)
    change = PageChange(path=path, slug=slug, updates={}, notes=[])

    if parsed is None:
        change.notes.append("no frontmatter — skipped")
        return change

    fm_lines, body = parsed
    values = frontmatter_values(fm_lines)

    today = date.today().isoformat()

    # PDF metadata (if local_archive points to a PDF that exists)
    archive_raw = (values.get("local_archive") or "").strip().strip('"')
    if archive_raw and archive_raw.lower() != "null":
        archive_path = (PROJECT_ROOT / archive_raw).resolve()
        if archive_path.exists() and archive_path.suffix.lower() == ".pdf":
            info = pdfinfo(archive_path)
            if info:
                pages = info.get("Pages")
                if pages and pages.isdigit():
                    if force or values.get("length_pages") in (None, "null", ""):
                        change.updates["length_pages"] = pages
                if force or values.get("format") in (None, "null", ""):
                    change.updates["format"] = '"PDF"'
                copyright_meta = info.get("Author") or info.get("Creator")
                if copyright_meta and (force or values.get("copyright_holder") in (None, "null", "")):
                    change.notes.append(f"PDF metadata Author/Creator: {copyright_meta!r} (not auto-applied — needs human review)")
            else:
                change.notes.append(f"pdfinfo failed on {archive_path.name}")
        elif archive_path.exists() and archive_path.suffix.lower() == ".md":
            # Distinguish web-scraped markdown from authored markdown by checking
            # for the extract-pdfs.sh header. Anything machine-extracted is the
            # text layer of a PDF or web scrape — set format accordingly.
            if force or values.get("format") in (None, "null", ""):
                first_lines = archive_path.read_text(encoding="utf-8", errors="replace")[:400]
                if "extracted_from:" in first_lines:
                    # Extracted from a PDF in source-guides/ — set format to PDF and
                    # try to pull pages from the sibling PDF if it exists.
                    pdf_sib = archive_path.with_suffix(".pdf")
                    if pdf_sib.exists():
                        info = pdfinfo(pdf_sib)
                        if info.get("Pages", "").isdigit():
                            change.updates["length_pages"] = info["Pages"]
                            change.updates["format"] = '"PDF"'
                    else:
                        # Came from a web-scraped guide — markdown is the source format.
                        change.updates["format"] = '"web"'
                else:
                    change.updates["format"] = '"markdown"'

    # Live-status check
    url_raw = (values.get("source_url") or "").strip().strip('"')
    if not no_net and url_raw and url_raw.lower() != "null":
        status, note = head_live_status(url_raw)
        change.notes.append(f"live_status: {status} ({note})")
        if force or values.get("live_status") in (None, "null", ""):
            change.updates["live_status"] = f'"{status}"'
        elif values.get("live_status") != f'"{status}"':
            existing = values.get("live_status")
            if existing != f'"{status}"':
                # Only auto-update if we're more certain than the existing value
                # — e.g., promote 'live' → '404' or 'login-gated', but don't
                # demote a human-set '404' back to 'live' without --force.
                if existing in ('"live"', None) and status != "live":
                    change.updates["live_status"] = f'"{status}"'
                else:
                    change.notes.append(
                        f"live_status mismatch (file: {existing}, head: {status}) — leaving as-is, use --force to overwrite"
                    )
        change.updates["last_checked"] = today

    # Seed `added` if missing
    if values.get("added") in (None, "null", "") and "added" not in change.updates:
        change.updates["added"] = today

    if change.updates:
        new_fm = apply_updates(fm_lines, change.updates)
        if not args.check_only:
            write_page(path, new_fm, body)

    return change


# ---------- CLI ----------

def main() -> int:
    pages = sorted(SOURCES_DIR.glob("*.md"))
    if not pages:
        print(f"no source pages found at {SOURCES_DIR}", file=sys.stderr)
        return 1

    print(f"enriching {len(pages)} source pages "
          f"(check_only={args.check_only}, force={args.force}, no_net={args.no_net})",
          file=sys.stderr)

    total_updates = 0
    for path in pages:
        change = enrich(path, force=args.force, no_net=args.no_net)
        total_updates += len(change.updates)
        marker = "    " if not change.updates else " →  "
        bits = [f"{k}={v}" for k, v in change.updates.items()] or ["(no changes)"]
        print(f"{marker}{change.slug:32s} {', '.join(bits)}", file=sys.stderr)
        for note in change.notes:
            print(f"          · {note}", file=sys.stderr)

    print(f"\n{total_updates} field updates across {len(pages)} pages "
          f"({'DRY RUN — no writes' if args.check_only else 'written'})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--check-only", action="store_true", help="report changes without writing")
    p.add_argument("--force", action="store_true", help="overwrite existing values")
    p.add_argument("--no-net", action="store_true", help="skip HEAD requests")
    args = p.parse_args()
    sys.exit(main())
