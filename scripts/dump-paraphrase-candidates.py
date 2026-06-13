#!/usr/bin/env python3
"""Dump echo-candidate paraphrases (overlap >= 0.45) grouped by term file, with
full quote + full paraphrase text, for the de-duplication rewrite pass.

Read-only. Emits JSON to stdout: {filename: [ {org, overlap, para_words,
quote, paraphrase}, ... ]}.
"""
import re
import glob
import json
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "site" / "src" / "content"
THRESHOLD = 0.45

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
    out = {}
    for f in sorted(glob.glob(str(CONTENT / "terms" / "*.md"))):
        last_q, last_org = None, "?"
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
                last_org = unquote(m.group(1)); continue
            m = QUOTE_RE.match(line)
            if m:
                last_q = unquote(m.group(1)); continue
            m = PARA_RE.match(line)
            if m:
                para = unquote(m.group(1))
                if last_q:
                    qt = set(content_tokens(last_q))
                    pt = content_tokens(para)
                    pset = set(pt)
                    overlap = len(qt & pset) / len(pset) if pset else 0.0
                    if overlap >= THRESHOLD:
                        out.setdefault(Path(f).name, []).append({
                            "org": last_org, "overlap": round(overlap, 2),
                            "para_words": len(pt),
                            "quote": last_q, "paraphrase": para,
                        })
                last_q = None
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
