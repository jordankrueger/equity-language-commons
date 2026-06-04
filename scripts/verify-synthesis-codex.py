#!/usr/bin/env python3
"""Layer 2 semantic audit — Codex (ChatGPT OAuth) checks every term page's
synthesis/paraphrase claims against the archived source material.
See docs/superpowers/plans/2026-06-04-content-verification.md.

BILLING GUARD: runs `codex exec` with OPENAI_API_KEY removed from the
environment so the CLI can only use the ChatGPT-subscription OAuth session
in ~/.codex/auth.json. Aborts if that file is missing.

Per page: assemble the page + ±40-line excerpts around each cited quote in
its archive, ask Codex to classify every factual claim as
SUPPORTED / EXTERNAL / CONTRADICTED, append the JSON verdict to
notes/verification/layer2-verdicts.jsonl, and record the page in
notes/verification/layer2-done.txt (resumable across runs / usage caps).

Usage:
  ./scripts/verify-synthesis-codex.py                 # next 10 undone pages
  ./scripts/verify-synthesis-codex.py --limit 3       # smaller batch
  ./scripts/verify-synthesis-codex.py --pages negro,dreamer   # specific pages
  ./scripts/verify-synthesis-codex.py --report        # roll up verdicts only
"""

import glob
import json
import os
import re
import subprocess
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(ROOT, "site/src/content/terms")
OUTDIR = os.path.join(ROOT, "notes/verification")
DONE = os.path.join(OUTDIR, "layer2-done.txt")
VERDICTS = os.path.join(OUTDIR, "layer2-verdicts.jsonl")

LIMIT = 10
PAGES = None
if "--limit" in sys.argv:
    LIMIT = int(sys.argv[sys.argv.index("--limit") + 1])
if "--pages" in sys.argv:
    PAGES = sys.argv[sys.argv.index("--pages") + 1].split(",")

QUOTE_TRANS = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
})

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
ALL_ARCHIVE_MD = [p for p in
                  glob.glob(f"{ROOT}/source-guides/*.md")
                  + glob.glob(f"{ROOT}/source-guides/discovered/*.md")
                  if not p.endswith("MANIFEST.md")]


def norm(s):
    s = unicodedata.normalize("NFKC", s).translate(QUOTE_TRANS).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]", " ", s)).strip()


def resolve_archive(local_archive, org_slug):
    if not local_archive:
        return None
    mapped = ROOT_PDF_MAP.get(os.path.basename(local_archive))
    if mapped:
        return os.path.join(ROOT, "source-guides", mapped)
    p = os.path.join(ROOT, local_archive)
    if p.endswith(".md") and os.path.exists(p):
        return p
    sib = re.sub(r"\.pdf$", ".md", p, flags=re.I)
    if os.path.exists(sib):
        return sib
    cands = [m for m in ALL_ARCHIVE_MD
             if os.path.basename(m).startswith(org_slug)]
    return cands[0] if cands else None


def excerpt_for(quote, arch_path, context=120):
    """Whole archive when it's small enough (claims often draw on parts of
    the source far from the quoted entry); otherwise ±context raw lines
    around the first place the quote's opening words appear."""
    lines = open(arch_path, errors="replace").read().splitlines()
    if len(lines) <= 2500:
        return "\n".join(lines)
    probe = " ".join(norm(quote).split()[:6])
    if probe:
        for i in range(len(lines)):
            window = norm(" ".join(lines[i:i + 4]))
            if probe in window:
                lo, hi = max(0, i - context), min(len(lines), i + context)
                return "\n".join(lines[lo:hi])
    return "\n".join(lines[:2 * context])


def bundle_for(path):
    text = open(path).read()
    fm = text.split("\n---\n")[0]
    parts = [f"=== PAGE UNDER AUDIT ===\n{text}\n"]
    seen = set()
    for raw in re.split(r"\n  - org: ", "\n" + fm)[1:]:
        entry = "org: " + raw
        qm = re.search(r'quote:\s*"((?:[^"\\]|\\.)*)"', entry, re.S)
        am = re.search(r'^\s*local_archive:\s*"([^"]+)"', entry, re.M)
        om = re.search(r'^\s*org_slug:\s*"([^"]+)"', entry, re.M)
        if not (qm and am):
            continue
        arch = resolve_archive(am.group(1), om.group(1) if om else "")
        if not arch:
            continue
        quote = qm.group(1).replace('\\"', '"')
        key = arch
        if key in seen:
            continue
        seen.add(key)
        parts.append(f"=== SOURCE EXCERPT: {os.path.basename(arch)} "
                     f"(org: {om.group(1) if om else '?'}) ===\n"
                     f"{excerpt_for(quote, arch)}\n")
    return "\n".join(parts)


PROMPT_TEMPLATE = """/goal Audit one published reference page against its source excerpts and return a single JSON object listing EVERY audited factual claim with its verdict (including SUPPORTED ones); stop when the JSON is emitted.

You are auditing a reference page for hallucinations. Below you are given the page (frontmatter + prose) and excerpts from the primary sources it cites. Audit ONLY factual claims — statements about the world or about what a source says: dates, statistics, coinages, legal facts, chronology, and characterizations of a cited source's position. Do NOT audit the page's own editorial advice, recommendations, or writing guidance ("writers should...", "use X when...", practical tips) — that is the author's voice, not a factual claim. For every factual claim in the Synthesis section, Audience notes section, and each guidance entry's paraphrase field, classify it as:
- SUPPORTED: follows from the quoted/excerpted source material
- EXTERNAL: a real-world claim not derivable from the provided sources (dates, coinages, legal facts, statistics the author added)
- CONTRADICTED: conflicts with the provided source material

For paraphrases, additionally flag any that misstate the cited source's position (treat that as CONTRADICTED with the evidence).

Calibration: reserve EXTERNAL for CONCRETE checkable facts the sources do not contain — named entities, dates, numbers, statistics, events, legal/institutional facts, coinages, attributions. Interpretive syntheses, characterizations, and judgments about the corpus ("the sources agree...", "the arc is well documented", "this reads as...") are the author's analysis: classify them SUPPORTED when consistent with the sources, CONTRADICTED only when the sources actually conflict with them. Do not flag a claim merely because the sources don't state it in those words.

Rules: do not rewrite the page; do not treat the page's own assertions as evidence; when an excerpt is too noisy to judge, use verdict EXTERNAL with evidence "source excerpt insufficient". Output ONLY one JSON object, no markdown fences, shaped:
{{"page": "{slug}", "claims": [{{"text": "<claim, abbreviated ok>", "section": "synthesis|audience_notes|paraphrase:<org_slug>", "verdict": "SUPPORTED|EXTERNAL|CONTRADICTED", "evidence": "<one line>"}}]}}

{bundle}"""


def run_codex(prompt):
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    r = subprocess.run(
        ["codex", "exec", "--sandbox", "read-only", "--cd", ROOT, prompt],
        capture_output=True, text=True, timeout=600, env=env)
    out = r.stdout
    # last JSON object in the output (codex prints session noise first)
    m = re.findall(r'\{"page".*\}', out, re.S)
    if not m:
        raise RuntimeError(f"no JSON in codex output (rc={r.returncode}): "
                           f"{out[-400:]}{r.stderr[-200:]}")
    return json.loads(m[-1])


def report():
    if not os.path.exists(VERDICTS):
        print("no verdicts yet")
        return
    rows = [json.loads(l) for l in open(VERDICTS)]
    flat = [(r["page"], c) for r in rows for c in r.get("claims", [])]
    bad = [(p, c) for p, c in flat if c["verdict"] == "CONTRADICTED"]
    ext = [(p, c) for p, c in flat if c["verdict"] == "EXTERNAL"]
    with open(f"{OUTDIR}/layer2-report.md", "w") as f:
        f.write("# Layer 2 (Codex) audit report\n\n")
        f.write(f"- pages audited: {len(rows)}\n"
                f"- claims: {len(flat)} — "
                f"{len(flat) - len(bad) - len(ext)} supported, "
                f"{len(ext)} external, {len(bad)} CONTRADICTED\n\n")
        if bad:
            f.write("## CONTRADICTED — fix these\n\n")
            for p, c in bad:
                f.write(f"- `{p}` [{c.get('section','?')}] {c['text']}\n"
                        f"  - {c.get('evidence','')}\n")
        if ext:
            f.write("\n## EXTERNAL — triage (verify+cite / keep / cut)\n\n")
            for p, c in ext:
                f.write(f"- `{p}` [{c.get('section','?')}] {c['text']}\n")
    print(f"layer2-report.md: {len(rows)} pages, {len(bad)} contradicted, "
          f"{len(ext)} external")


if "--report" in sys.argv:
    report()
    sys.exit(0)

# ---- preflight: subscription auth only ----
if not os.path.exists(os.path.expanduser("~/.codex/auth.json")):
    sys.exit("ABORT: ~/.codex/auth.json missing — run `codex login` "
             "(ChatGPT account), never set OPENAI_API_KEY for this script.")

os.makedirs(OUTDIR, exist_ok=True)
done = set()
if os.path.exists(DONE):
    done = set(open(DONE).read().split())

targets = PAGES or [os.path.basename(p)[:-3]
                    for p in sorted(glob.glob(f"{TERMS}/*.md"))]
targets = [t for t in targets if t not in done][:LIMIT]
if not targets:
    print("nothing to do (all pages in layer2-done.txt)")
    sys.exit(0)

for slug in targets:
    path = f"{TERMS}/{slug}.md"
    if not os.path.exists(path):
        print(f"skip {slug}: no such page")
        continue
    print(f"auditing {slug} ...", flush=True)
    try:
        verdict = run_codex(PROMPT_TEMPLATE.format(
            slug=slug, bundle=bundle_for(path)))
    except Exception as e:
        print(f"  ERROR {slug}: {e}")
        continue
    with open(VERDICTS, "a") as f:
        f.write(json.dumps(verdict) + "\n")
    with open(DONE, "a") as f:
        f.write(slug + "\n")
    n = len(verdict.get("claims", []))
    flags = sum(1 for c in verdict.get("claims", [])
                if c["verdict"] != "SUPPORTED")
    print(f"  {n} claims, {flags} flagged")

report()
