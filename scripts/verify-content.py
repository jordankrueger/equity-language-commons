#!/usr/bin/env python3
"""Layer 1 deterministic verifier — see docs/superpowers/plans/2026-06-04-content-verification.md.

Per guidance entry on every term page:
  V1  quote-in-archive: every ellipsis-segment of the quote must appear in the
      normalized text of the entry's local archive
  V2  confidence audit: VERIFIED-ARCHIVED + failed V1 = FAIL (label is a lie);
      PARTIAL + passed V1 = upgrade suggestion
  V3  url liveness: HEAD→GET fallback on source_url (skip with --no-net)
  V4  cross-reference: org_slug must match a source page; year must match the
      source page year or a version_history year

Outputs:
  notes/verification/layer1-report.md      (human summary)
  notes/verification/layer1-results.jsonl  (one record per entry per check)

Usage: ./scripts/verify-content.py [--no-net] [--only slug1,slug2]
"""

import glob
import json
import os
import re
import sys
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(ROOT, "site/src/content/terms")
SOURCES = os.path.join(ROOT, "site/src/content/sources")
OUTDIR = os.path.join(ROOT, "notes/verification")

NO_NET = "--no-net" in sys.argv
ONLY = None
if "--only" in sys.argv:
    ONLY = set(sys.argv[sys.argv.index("--only") + 1].split(","))

QUOTE_TRANS = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
    "‐": "-", "‑": "-",
})


def normalize(s):
    s = unicodedata.normalize("NFKC", s).translate(QUOTE_TRANS)
    # accent-fold: PDF extractions often lose diacritics (Diné → Dine)
    s = "".join(c for c in unicodedata.normalize("NFKD", s)
                if not unicodedata.combining(c))
    # pandoc-scrape noise (NLGJA, DSG, TJA web archives): span attributes
    # `]{style="..."}`, heading attrs `{#id ...}`, escaped punctuation `\.`
    s = re.sub(r"\]\{[^}]*\}", " ", s)
    s = re.sub(r"\{[^}]*\}", " ", s)
    s = re.sub(r"\\([.\"'()\[\]-])", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # md links → text
    s = re.sub(r"[*_`#>|\[\]]", " ", s)      # markdown noise
    s = re.sub(r"[^a-z0-9' \"().,;:?!/-]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


# ---------- archive resolution ----------

ALL_ARCHIVE_MD = glob.glob(f"{ROOT}/source-guides/*.md") + glob.glob(
    f"{ROOT}/source-guides/discovered/*.md")
ALL_ARCHIVE_MD = [p for p in ALL_ARCHIVE_MD if not p.endswith("MANIFEST.md")]
_norm_cache = {}


def words_only(s):
    """Punctuation-blind form: bullets-vs-commas and colon-vs-period
    differences disappear; word order and word identity must still match."""
    return " ".join(re.sub(r"[^a-z0-9' ]", " ", s).split())


def archive_text(path):
    if path not in _norm_cache:
        n = normalize(open(path, errors="replace").read())
        _norm_cache[path] = (n, words_only(n))
    return _norm_cache[path]


# The six originally-archived PDFs have slug-named extractions that aren't
# derivable from the original filename — explicit map (stable set).
ROOT_PDF_MAP = {
    "CaseyStyleManualComplete.pdf": "casey-editorial-guide-2013-04.md",
    "Equity Language Guide Sierra Club 2021.pdf":
        "sierra-club-equity-language-guide-2021.md",
    "Native-Governance-Center-Style-Guide-published-2021-02.pdf":
        "native-governance-center-style-guide-2021-02.md",
    "SEIU Stylebook Jan 2020.pdf": "seiu-stylebook-2020-01.md",
    "7.27.20 YlI Styleguide 2020.pdf": "yli-styleguide-2020.md",
    "Stand_IdentityLong_June2019.pdf": "stand-earth-identity-2019-06.md",
}


def resolve_archive(local_archive, org_slug):
    """Map a local_archive value to the extracted-markdown file to search."""
    if not local_archive:
        return None
    mapped = ROOT_PDF_MAP.get(os.path.basename(local_archive))
    if mapped:
        return os.path.join(ROOT, "source-guides", mapped)
    p = os.path.join(ROOT, local_archive)
    if p.endswith(".md") and os.path.exists(p):
        return p
    # sibling .md with the same basename
    sib = re.sub(r"\.pdf$", ".md", p, flags=re.I)
    if os.path.exists(sib):
        return sib
    # slug-named extraction anywhere under source-guides
    cands = [m for m in ALL_ARCHIVE_MD
             if os.path.basename(m).startswith(org_slug)]
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        for c in cands:
            if any(y in os.path.basename(c)
                   for y in re.findall(r"(?:19|20)\d{2}", local_archive)):
                return c
        return cands[0]
    # last resort: token overlap between the archive filename and the
    # extraction filenames (handles renamed originals like
    # "CaseyStyleManualComplete.pdf" → casey-editorial-guide-2013-04.md)
    want = os.path.basename(local_archive).lower()
    best, best_n = None, 0
    for m in ALL_ARCHIVE_MD:
        # count extraction-filename tokens appearing inside the original
        # filename (handles camel-mashed originals like
        # "CaseyStyleManualComplete.pdf" → casey-editorial-guide-2013-04.md)
        n = sum(1 for t in re.findall(r"[a-z]{4,}",
                                      os.path.basename(m).lower())
                if t in want)
        if n > best_n:
            best, best_n = m, n
    return best if best_n >= 1 else None


# ---------- human-verified overrides ----------
# notes/verification/layer1-verified-overrides.yml lists (page, org_slug)
# pairs whose quotes were hand-verified against the source PDF/scrape even
# though the extraction .md cannot exact-match them. Edit a page quote →
# remove its row so it re-verifies.
OVERRIDES = set()
_ov = os.path.join(OUTDIR, "layer1-verified-overrides.yml")
if os.path.exists(_ov):
    _txt = open(_ov).read()
    OVERRIDES = set(zip(re.findall(r'page: "([^"]+)"', _txt),
                        re.findall(r'org_slug: "([^"]+)"', _txt)))


# ---------- source-page index ----------

source_pages = {}
for f in glob.glob(f"{SOURCES}/*.md"):
    s = open(f).read()
    slug = re.search(r'^org_slug: "([^"]+)"', s, re.M)
    year = re.search(r"^year: (\d+)", s, re.M)
    vyears = re.findall(r"^  - year: (\d+)", s, re.M)
    if slug:
        gated = bool(re.search(r'live_status: "(login-gated|paywalled)"', s))
        source_pages.setdefault(slug.group(1), []).append({
            "file": os.path.basename(f),
            "gated": gated,
            "years": {int(year.group(1))} | {int(v) for v in vyears}
            if year else set(),
        })


# ---------- url check ----------

def url_alive(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={
                "User-Agent": "Mozilla/5.0 (ELC verify-content)"})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status < 400:
                    return True, r.status
        except urllib.error.HTTPError as e:
            if method == "GET":
                return False, e.code
        except Exception as e:
            if method == "GET":
                return False, str(e)[:60]
    return False, "unreachable"


# ---------- main loop ----------

os.makedirs(OUTDIR, exist_ok=True)
results = []
checked_urls = {}

term_files = sorted(glob.glob(f"{TERMS}/*.md"))
for path in term_files:
    slug = os.path.basename(path)[:-3]
    if ONLY and slug not in ONLY:
        continue
    text = open(path).read()
    fm = text.split("\n---\n")[0]

    for raw in re.split(r"\n  - org: ", "\n" + fm)[1:]:
        entry = 'org: ' + raw
        get = lambda k, e=entry: (re.search(
            rf'^\s*{k}: (?:"((?:[^"\\]|\\.)*)"|(null|\d+))', e, re.M | re.S))

        def val(k):
            m = re.search(rf'^\s*{k}:\s*(.*)$', entry, re.M)
            if not m:
                return None
            v = m.group(1).strip()
            if v == "null" or v == "":
                return None
            return v.strip('"')

        # quote may span lines and contain escaped quotes
        qm = re.search(r'quote:\s*"((?:[^"\\]|\\.)*)"', entry, re.S)
        quote = qm.group(1).replace('\\"', '"') if qm else None
        org_slug = val("org_slug")
        year = val("year")
        conf = val("confidence")
        url = val("source_url")
        local_archive = val("local_archive")
        rec = {"page": slug, "org_slug": org_slug, "year": year}

        # V1 quote-in-archive
        if quote:
            arch = resolve_archive(local_archive, org_slug or "")
            if not arch:
                results.append({**rec, "check": "V1", "verdict": "NO-ARCHIVE",
                                "detail": local_archive})
            else:
                hay, hay_w = archive_text(arch)
                # PDF extractions sometimes drop hyphens at line breaks
                # ("French-Canadian" → "FrenchCanadian"): fall back to a
                # hyphen-blind comparison before calling a segment missing.
                hay_nh = hay.replace("-", "")
                hay_wnh = hay_w.replace(" ", "")
                # quote-mark boundaries are presentation, not content —
                # strip them from segment edges before comparing
                segs = [s.strip().strip('"“”‘’\'')
                        for s in re.split(r"…|\.\.\.", quote)
                        if len(s.split()) >= 3]
                missing, truncated, loose, gapped = [], [], [], []
                for s in segs:
                    ns = normalize(s)
                    if ns in hay or ns.replace("-", "") in hay_nh:
                        continue
                    # clean truncation: the segment matches except its final
                    # punctuation closed a sentence the source continues
                    # (period-for-ellipsis). Cosmetic — fix is adding "…".
                    stem = ns.rstrip(".?!\"' ")
                    if stem and (stem in hay
                                 or stem.replace("-", "") in hay_nh):
                        truncated.append(s)
                        continue
                    # punctuation-blind: same words in the same order
                    # (list flattening, comma/bullet differences)
                    ws = words_only(ns)
                    if ws and (ws in hay_w
                               or ws.replace(" ", "") in hay_wnh
                               or ws.rstrip(".?!\"' ") in hay_w):
                        loose.append(s)
                        continue
                    # shingle test: PDF extractions interleave page
                    # headers/footers mid-sentence. If >=80% of the segment's
                    # 6-word windows appear verbatim, the quote is real and
                    # the gap is extraction noise — not changed wording.
                    w = ws.split()
                    if len(w) >= 6:
                        shingles = [" ".join(w[i:i + 6])
                                    for i in range(len(w) - 5)]
                        hit = sum(1 for sh in shingles if sh in hay_w)
                        if hit / len(shingles) >= 0.8:
                            gapped.append(s)
                            continue
                    missing.append(s)
                if (missing or truncated) and (slug, org_slug) in OVERRIDES:
                    results.append({**rec, "check": "V1",
                                    "verdict": "HUMAN-VERIFIED",
                                    "detail": os.path.basename(arch)})
                elif missing:
                    results.append({**rec, "check": "V1", "verdict": "MISS",
                                    "detail": f"{os.path.basename(arch)} :: "
                                    + " // ".join(m[:70] for m in missing)})
                elif truncated:
                    results.append({**rec, "check": "V1",
                                    "verdict": "TRUNCATED",
                                    "detail": f"{os.path.basename(arch)} :: "
                                    + " // ".join(t[-60:] for t in truncated)})
                elif loose:
                    results.append({**rec, "check": "V1", "verdict": "LOOSE",
                                    "detail": f"{os.path.basename(arch)} :: "
                                    + " // ".join(t[:60] for t in loose)})
                elif gapped:
                    results.append({**rec, "check": "V1", "verdict": "GAPPED",
                                    "detail": f"{os.path.basename(arch)} :: "
                                    + " // ".join(t[:60] for t in gapped)})
                else:
                    results.append({**rec, "check": "V1", "verdict": "OK",
                                    "detail": os.path.basename(arch)})

            # V2 confidence audit
            v1 = results[-1]["verdict"]
            if conf == "VERIFIED-ARCHIVED" and v1 == "MISS":
                results.append({**rec, "check": "V2", "verdict": "FAIL",
                                "detail": "labeled VERIFIED-ARCHIVED but quote "
                                          "not found in archive"})
            elif conf == "PARTIAL" and v1 == "OK":
                results.append({**rec, "check": "V2", "verdict": "UPGRADE",
                                "detail": "PARTIAL but quote verifies — bump "
                                          "to VERIFIED-ARCHIVED"})

        # V3 url liveness
        if url and not NO_NET:
            if url not in checked_urls:
                checked_urls[url] = url_alive(url)
            ok, code = checked_urls[url]
            # 401/403 on a login-gated/paywalled source is expected
            if not ok and str(code) in ("401", "403") and any(
                    p.get("gated") for p in source_pages.get(org_slug, [])):
                ok = True
                code = f"{code} (gated — expected)"
            results.append({**rec, "check": "V3",
                            "verdict": "OK" if ok else "DEAD",
                            "detail": f"{code} {url}"})

        # V4 cross-reference
        if org_slug:
            sp = source_pages.get(org_slug)
            if not sp:
                results.append({**rec, "check": "V4", "verdict": "FAIL",
                                "detail": "org_slug has no source page"})
            elif year and all(int(year) not in p["years"] for p in sp):
                results.append({**rec, "check": "V4", "verdict": "YEAR-MISMATCH",
                                "detail": f"entry year {year} not on source "
                                          f"page(s) {[p['file'] for p in sp]}"})

with open(f"{OUTDIR}/layer1-results.jsonl", "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")

# ---------- report ----------

def count(check, verdict):
    return sum(1 for r in results if r["check"] == check
               and r["verdict"] == verdict)


bad = [r for r in results if r["verdict"] in
       ("MISS", "FAIL", "DEAD", "NO-ARCHIVE", "YEAR-MISMATCH", "TRUNCATED")]
upgrades = [r for r in results if r["verdict"] == "UPGRADE"]

with open(f"{OUTDIR}/layer1-report.md", "w") as f:
    f.write("# Layer 1 verification report\n\n")
    f.write(f"- V1 quote-in-archive: {count('V1','OK')} OK, "
            f"{count('V1','MISS')} MISS, {count('V1','TRUNCATED')} truncated, "
            f"{count('V1','LOOSE')} loose-match, "
            f"{count('V1','GAPPED')} gapped(extraction noise), "
            f"{count('V1','HUMAN-VERIFIED')} human-verified, "
            f"{count('V1','NO-ARCHIVE')} no-archive\n")
    f.write(f"- V2 confidence: {count('V2','FAIL')} FAIL, "
            f"{len(upgrades)} upgrade suggestions\n")
    f.write(f"- V3 urls: {count('V3','OK')} OK, {count('V3','DEAD')} dead\n")
    f.write(f"- V4 cross-ref: {count('V4','FAIL')} FAIL, "
            f"{count('V4','YEAR-MISMATCH')} year mismatches\n\n")
    if bad:
        f.write("## Findings\n\n")
        for r in bad:
            f.write(f"- **{r['check']} {r['verdict']}** `{r['page']}` "
                    f"({r['org_slug']}): {r['detail']}\n")
    if upgrades:
        f.write("\n## Upgrade suggestions (PARTIAL → VERIFIED-ARCHIVED)\n\n")
        for r in upgrades:
            f.write(f"- `{r['page']}` ({r['org_slug']})\n")

print(f"verify-content: {len(results)} checks, {len(bad)} findings, "
      f"{len(upgrades)} upgrades → notes/verification/layer1-report.md")
sys.exit(0)
