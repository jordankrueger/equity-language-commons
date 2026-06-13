#!/usr/bin/env python3
"""Scout pass: rank guidance paraphrases by how much they echo their quote.

For each guidance entry (term pages), pairs the `quote:` with the `paraphrase:`
that follows it and scores lexical overlap. High overlap + short paraphrase =
likely "echo" (the paraphrase just restates the quote the reader already saw).
This is a heuristic ranking to surface the worst offenders for editorial review,
NOT a verdict — borderline cases still need a human/LLM read.

Deterministic, read-only. No writes.
"""
import re
import glob
from pathlib import Path
from collections import Counter

CONTENT = Path(__file__).resolve().parent.parent / "site" / "src" / "content"

STOP = set("""a an the and or but of to in on at for with as by from into that this
these those is are was were be been being it its his her their our your my we you they
them he she who whom which what when where why how not no nor so than then there here
do does did has have had will would can could should may might must about over under
between within without across per each any all some more most such only also both either
neither one two non vs use uses using used avoid avoids prefer preferred term terms word
words people person language guide guides org note notes entry says say said""".split())

QUOTE_RE = re.compile(r'^\s*quote:\s*(.*)$')
PARA_RE = re.compile(r'^\s*paraphrase:\s*(.*)$')
ORG_RE = re.compile(r'^\s*org_slug:\s*(.*)$')


def unquote(v: str) -> str:
    v = v.strip()
    if v in ("null", "~", ""):
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return v.replace('\\"', '"')


def content_tokens(text: str):
    toks = re.findall(r"[a-z][a-z'-]+", text.lower())
    return [t for t in toks if t not in STOP and len(t) > 2]


def main():
    pairs = []
    for f in sorted(glob.glob(str(CONTENT / "terms" / "*.md"))):
        last_q = None
        last_org = "?"
        # only scan frontmatter (between first two --- lines)
        lines = Path(f).read_text(encoding="utf-8").splitlines()
        fm_end = None
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    fm_end = i
                    break
        for line in lines[1:fm_end]:
            m = ORG_RE.match(line)
            if m:
                last_org = unquote(m.group(1))
                continue
            m = QUOTE_RE.match(line)
            if m:
                last_q = unquote(m.group(1))
                continue
            m = PARA_RE.match(line)
            if m:
                para = unquote(m.group(1))
                if last_q is not None:
                    qt = set(content_tokens(last_q))
                    pt = content_tokens(para)
                    pset = set(pt)
                    overlap = len(qt & pset) / len(pset) if pset else 0.0
                    pairs.append({
                        "file": Path(f).name, "org": last_org,
                        "overlap": overlap, "para_words": len(pt),
                        "q_empty": not qt, "para": para,
                    })
                last_q = None
    scored = [p for p in pairs if not p["q_empty"]]
    echoes = [p for p in scored if p["overlap"] >= 0.6]
    high = [p for p in scored if 0.45 <= p["overlap"] < 0.6]

    print(f"Total guidance entries:            {len(pairs)}")
    print(f"  with a real quote to compare:    {len(scored)}")
    print(f"  quote: null (no echo possible):  {len(pairs) - len(scored)}")
    print(f"\nLIKELY ECHO   (overlap >= 0.60):  {len(echoes)}")
    print(f"BORDERLINE    (0.45-0.60):        {len(high)}")
    print(f"ADDS VALUE    (< 0.45):           {len(scored) - len(echoes) - len(high)}")

    echoes.sort(key=lambda p: (-p["overlap"], p["para_words"]))
    print("\n--- Top 20 worst echoes (high overlap, paraphrase ~= quote) ---")
    for p in echoes[:20]:
        print(f"  {p['overlap']:.2f}  {p['para_words']:>3}w  {p['file'][:-3]:<22} [{p['org']}]")
        print(f"        “{p['para'][:120]}”")


if __name__ == "__main__":
    main()
