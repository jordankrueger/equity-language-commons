#!/usr/bin/env python3
"""Build the bounded ELC proofing packet.

The 766-page print export has no finish line. This builds the opposite: a
finite, countable set of pages that actually carry risk, each annotated with
*why* it's in the packet, with a checkbox per page and a running counter.

Groups:
  A  Slur & quote-only pages     - reproduce a slur verbatim on a public page
  B  Faith cluster               - newest content, thinnest sourcing
  C  Chapter intros              - Jordan's voice, frames everything below it
  D  Politically contested       - what a bad-faith critic reaches for first
  E  Site-level pages            - highest reputational weight per word
  F  Random sample               - deterministic quality spot-check

Only prose Jordan is responsible for is shown: chapter ledes, cross-cutting
principle bodies, and the markdown body (Synthesis / Audience notes). Verbatim
`quote:` fields are Layer 1 material and are NOT part of the proofing surface.
Paraphrases are shown collapsed, since the de-dup pass rewrote many of them.

Output (gitignored): print-export/proofing-packet.html
Rebuild after content changes. Checkbox/note state lives in the reader's
localStorage and survives a rebuild (keyed by page id, not by position).

Usage:  python3 scripts/build-proofing-packet.py
"""

import html
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "site" / "src" / "content"
PAGES = ROOT / "site" / "src" / "pages"
OUT = ROOT / "print-export" / "proofing-packet.html"

SAMPLE_SEED = 20260722
SAMPLE_SIZE = 10

# --------------------------------------------------------------------------
# packet definition
# --------------------------------------------------------------------------

GROUPS = [
    {
        "id": "A",
        "title": "Slur & quote-only pages",
        "why": "These reproduce a slur verbatim on a public page. Highest risk per word "
               "in the whole project. Read for framing and for anything that could read "
               "as gratuitous rather than necessary.",
        "kind": "term",
        "slugs": [
            "retarded", "tranny", "negro", "colored", "cripple", "lame", "crazy",
            "insane", "ghetto", "hermaphrodite", "transvestite", "sexual-preference",
            "schizophrenic", "illegal-alien",
        ],
    },
    {
        "id": "B",
        "title": "Faith cluster",
        "why": "Newest content with the thinnest source coverage, and the cluster most "
               "likely to generate an angry email. Read for claims that outrun the sources.",
        "kind": "term",
        "slugs": [
            "jew", "islam", "muslim", "antisemitism", "islamophobia",
            "nation-of-islam", "interfaith",
        ],
    },
    {
        "id": "C",
        "title": "Chapter intros",
        "why": "Your voice, not the corpus. Each one frames every term page beneath it, "
               "so an error here propagates. Also the most likely place for stale status "
               "claims about what's covered.",
        "kind": "chapter",
        "slugs": None,  # all of them
    },
    {
        "id": "D",
        "title": "Politically contested",
        "why": "The pages a bad-faith critic reaches for first. Read for anything that "
               "could be quoted out of context against you.",
        "kind": "term",
        "slugs": ["bipoc", "latinx", "white", "reverse-racism", "grooming", "urban"],
    },
    {
        "id": "E",
        "title": "Site-level pages",
        "why": "Highest reputational weight per word on the site. Methodology especially "
               "— it's where a serious critic goes before reading a single term page.",
        "kind": "astro",
        "slugs": ["index", "about", "methodology"],
    },
    {
        "id": "F",
        "title": "Random sample",
        "why": "Deterministic draw from the remaining term pages. This is a quality "
               "spot-check, not a risk check — you're sampling to find out whether the "
               "un-read majority is in good shape.",
        "kind": "term",
        "slugs": "SAMPLE",
    },
]


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return "", text
    return m.group(1), m.group(2)


def scalar(fm, key):
    """Pull a top-level quoted-or-bare scalar out of frontmatter."""
    m = re.search(rf'^{key}:\s*"(.*?)"\s*$', fm, re.M | re.S)
    if m:
        return m.group(1)
    m = re.search(rf"^{key}:\s*(.+?)\s*$", fm, re.M)
    return m.group(1).strip('"') if m else ""


def principles(fm):
    """Extract cross_cutting_principles title/body pairs."""
    block = re.search(r"^cross_cutting_principles:\n(.*?)(?=^\w|\Z)", fm, re.M | re.S)
    if not block:
        return []
    out = []
    for item in re.split(r"^  - ", block.group(1), flags=re.M)[1:]:
        t = re.search(r'title:\s*"(.*?)"\s*$', item, re.M | re.S)
        b = re.search(r'body:\s*"(.*?)"\s*$', item, re.M | re.S)
        if t and b:
            out.append((unescape_yaml(t.group(1)), unescape_yaml(b.group(1))))
    return out


def paraphrases(fm):
    """Extract (org, paraphrase) pairs in document order."""
    out = []
    org = None
    for line in fm.splitlines():
        m = re.match(r'\s*- org:\s*"(.*?)"\s*$', line)
        if m:
            org = unescape_yaml(m.group(1))
            continue
        m = re.match(r'\s*paraphrase:\s*"(.*)"\s*$', line)
        if m and org:
            out.append((org, unescape_yaml(m.group(1))))
    return out


def unescape_yaml(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def astro_prose(path):
    """Pull human prose out of an .astro page: headings and paragraph text."""
    text = path.read_text(encoding="utf-8")
    # drop the frontmatter script block and any <style>/<script>
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"<(style|script)\b.*?</\1>", "", text, flags=re.S)
    chunks = []
    for m in re.finditer(r"<(h1|h2|h3|p|li)\b[^>]*>(.*?)</\1>", text, re.S):
        tag, inner = m.group(1), m.group(2)
        inner = re.sub(r"\{[^{}]*\}", "", inner)          # drop JSX expressions
        inner = re.sub(r"<[^>]+>", "", inner)             # drop nested markup
        inner = html.unescape(inner)
        inner = re.sub(r"\s+", " ", inner).strip()
        if len(inner) < 3:
            continue
        chunks.append((tag, inner))
    return chunks


# --------------------------------------------------------------------------
# minimal markdown -> html
# --------------------------------------------------------------------------

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def md(text):
    out, buf, in_list = [], [], False

    def flush_p():
        if buf:
            out.append("<p>" + inline(" ".join(buf)) + "</p>")
            buf.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_p()
            close_list()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_p()
            close_list()
            lvl = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush_p()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + inline(re.sub(r"^[-*]\s+", "", stripped)) + "</li>")
            continue
        close_list()
        buf.append(stripped)

    flush_p()
    close_list()
    return "\n".join(out)


# --------------------------------------------------------------------------
# entry assembly
# --------------------------------------------------------------------------

def build_term(slug):
    path = CONTENT / "terms" / f"{slug}.md"
    if not path.exists():
        return None
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    return {
        "id": f"term:{slug}",
        "label": scalar(fm, "term") or slug,
        "sub": f"/terms/{slug}/",
        "words": len(body.split()),
        "html": md(body),
        "paraphrases": paraphrases(fm),
    }


def build_chapter(slug):
    path = CONTENT / "chapters" / f"{slug}.md"
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    lede = scalar(fm, "lede")
    parts = []
    if lede:
        parts.append('<h2>Lede</h2>' + f"<p>{inline(lede)}</p>")
    princ = principles(fm)
    if princ:
        parts.append("<h2>Cross-cutting principles</h2>")
        for t, b in princ:
            parts.append(f"<h3>{inline(t)}</h3><p>{inline(b)}</p>")
    parts.append(md(body))
    return {
        "id": f"chapter:{slug}",
        "label": scalar(fm, "title") or slug,
        "sub": f"/chapters/{slug}/",
        "words": len(lede.split()) + sum(len(b.split()) for _, b in princ) + len(body.split()),
        "html": "\n".join(parts),
        "paraphrases": [],
    }


def build_astro(name):
    path = PAGES / f"{name}.astro"
    chunks = astro_prose(path)
    parts = []
    for tag, txt in chunks:
        if tag in ("h1", "h2", "h3"):
            parts.append(f"<h{'2' if tag == 'h1' else '3'}>{inline(txt)}</h{'2' if tag == 'h1' else '3'}>")
        elif tag == "li":
            parts.append(f"<ul><li>{inline(txt)}</li></ul>")
        else:
            parts.append(f"<p>{inline(txt)}</p>")
    label = {"index": "Homepage", "about": "About", "methodology": "Methodology"}.get(name, name)
    return {
        "id": f"page:{name}",
        "label": label,
        "sub": f"/{'' if name == 'index' else name + '/'}",
        "words": sum(len(t.split()) for _, t in chunks),
        "html": "\n".join(parts),
        "paraphrases": [],
        "note": "Extracted prose only — verify against the live page for anything layout-dependent.",
    }


def resolve_sample(used):
    all_terms = sorted(p.stem for p in (CONTENT / "terms").glob("*.md"))
    pool = [t for t in all_terms if t not in used]
    return random.Random(SAMPLE_SEED).sample(pool, min(SAMPLE_SIZE, len(pool)))


# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------

CSS = """
:root{--bg:#fbfaf8;--fg:#1c1a17;--mut:#6b645c;--line:#e2ddd5;--card:#fff;
--acc:#7a4f2b;--done:#3f7a52;--flag:#a8402c;--flagbg:#fdf3f1}
@media(prefers-color-scheme:dark){:root{--bg:#161513;--fg:#eceae6;--mut:#9b948a;
--line:#302d29;--card:#1e1c1a;--acc:#c99a6a;--done:#6fae83;--flag:#e08a76;--flagbg:#2a1e1b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.62 Charter,Georgia,"Iowan Old Style",serif;-webkit-text-size-adjust:100%}
header{position:sticky;top:0;z-index:10;background:var(--bg);
border-bottom:1px solid var(--line);padding:14px 24px}
.hrow{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;
max-width:1080px;margin:0 auto}
h1{font-size:19px;margin:0;letter-spacing:-.01em}
.count{font:600 15px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--acc)}
.bar{height:4px;background:var(--line);border-radius:2px;overflow:hidden;
max-width:1080px;margin:10px auto 0}
.bar>div{height:100%;width:0;background:var(--done);transition:width .3s}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
.chip{font:500 12px/1 system-ui,sans-serif;padding:6px 10px;border-radius:20px;
border:1px solid var(--line);background:var(--card);color:var(--mut);cursor:pointer}
.chip[aria-pressed=true]{background:var(--acc);color:#fff;border-color:var(--acc)}
main{max-width:1080px;margin:0 auto;padding:0 24px 120px}
.intro{margin:28px 0 40px;padding:18px 20px;border-left:3px solid var(--acc);
background:var(--card);border-radius:0 6px 6px 0}
.intro p{margin:0 0 10px}.intro p:last-child{margin:0}
.grp{margin:48px 0 0}
.grp>h2{font-size:14px;letter-spacing:.09em;text-transform:uppercase;
color:var(--acc);margin:0 0 6px;font-family:system-ui,sans-serif}
.grp>.why{color:var(--mut);font-size:14.5px;margin:0 0 22px;max-width:66ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;
margin:0 0 18px;overflow:hidden}
.card.done{opacity:.55}
.card.flagged{border-color:var(--flag);box-shadow:inset 3px 0 0 var(--flag)}
.top{display:flex;align-items:center;gap:12px;padding:13px 18px;cursor:pointer;
user-select:none}
.top:hover{background:rgba(122,79,43,.04)}
.cb{width:19px;height:19px;flex:none;accent-color:var(--done);cursor:pointer}
.nm{font-weight:600;font-size:17px}
.meta{color:var(--mut);font:400 12.5px/1 ui-monospace,Menlo,monospace;margin-left:auto;
display:flex;gap:12px;align-items:center}
.flagbtn{font:500 11px/1 system-ui,sans-serif;padding:5px 9px;border-radius:4px;
border:1px solid var(--line);background:transparent;color:var(--mut);cursor:pointer}
.flagbtn[aria-pressed=true]{background:var(--flagbg);color:var(--flag);border-color:var(--flag)}
.body{display:none;padding:4px 18px 18px;border-top:1px solid var(--line)}
.card.open .body{display:block}
.body h2{font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);
font-family:system-ui,sans-serif;margin:24px 0 8px}
.body h3{font-size:16.5px;margin:20px 0 6px}
.body p,.body li{max-width:70ch}
.body a{color:var(--acc)}
details{margin:20px 0 0;font-size:14.5px}
summary{cursor:pointer;color:var(--mut);font-family:system-ui,sans-serif;font-size:13px}
details p{color:var(--mut);font-size:14px}
textarea{width:100%;margin-top:18px;padding:10px 12px;border:1px solid var(--line);
border-radius:6px;background:var(--bg);color:var(--fg);font:15px/1.5 inherit;
resize:vertical;min-height:62px}
textarea::placeholder{color:var(--mut)}
footer{position:fixed;bottom:0;left:0;right:0;background:var(--card);
border-top:1px solid var(--line);padding:11px 24px;display:flex;gap:12px;
align-items:center;justify-content:center}
button.act{font:500 13px/1 system-ui,sans-serif;padding:9px 15px;border-radius:6px;
border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
button.act:hover{border-color:var(--acc)}
.hide{display:none!important}
"""

JS = """
const KEY='elc-proofing-v1';
const state=JSON.parse(localStorage.getItem(KEY)||'{}');
const save=()=>localStorage.setItem(KEY,JSON.stringify(state));
const cards=[...document.querySelectorAll('.card')];

function get(id){return state[id]||(state[id]={done:false,flag:false,note:''})}

function paint(){
  let done=0;
  cards.forEach(c=>{
    const s=get(c.dataset.id);
    c.classList.toggle('done',s.done);
    c.classList.toggle('flagged',s.flag);
    c.querySelector('.cb').checked=s.done;
    c.querySelector('.flagbtn').setAttribute('aria-pressed',s.flag);
    if(s.done)done++;
  });
  document.getElementById('count').textContent=done+' of '+cards.length+' done';
  document.getElementById('fill').style.width=(done/cards.length*100)+'%';
}

cards.forEach(c=>{
  const s=get(c.dataset.id);
  const ta=c.querySelector('textarea');
  ta.value=s.note;
  ta.addEventListener('input',()=>{get(c.dataset.id).note=ta.value;save()});
  c.querySelector('.cb').addEventListener('click',e=>{
    e.stopPropagation();
    const st=get(c.dataset.id);st.done=e.target.checked;save();paint();
  });
  c.querySelector('.flagbtn').addEventListener('click',e=>{
    e.stopPropagation();
    const st=get(c.dataset.id);st.flag=!st.flag;save();paint();
  });
  c.querySelector('.top').addEventListener('click',e=>{
    if(e.target.closest('.cb,.flagbtn'))return;
    c.classList.toggle('open');
  });
});

document.querySelectorAll('.chip').forEach(ch=>{
  ch.addEventListener('click',()=>{
    const on=ch.getAttribute('aria-pressed')==='true';
    document.querySelectorAll('.chip').forEach(o=>o.setAttribute('aria-pressed','false'));
    ch.setAttribute('aria-pressed',String(!on));
    const f=on?null:ch.dataset.filter;
    cards.forEach(c=>{
      let show=true;
      if(f==='todo')show=!get(c.dataset.id).done;
      else if(f==='flag')show=get(c.dataset.id).flag;
      c.classList.toggle('hide',!show);
    });
    document.querySelectorAll('.grp').forEach(g=>{
      g.classList.toggle('hide',![...g.querySelectorAll('.card')].some(c=>!c.classList.contains('hide')));
    });
  });
});

document.getElementById('expand').addEventListener('click',()=>{
  const anyClosed=cards.some(c=>!c.classList.contains('open'));
  cards.forEach(c=>c.classList.toggle('open',anyClosed));
});

document.getElementById('export').addEventListener('click',()=>{
  let out='# ELC proofing findings\\n\\n';
  let n=0;
  cards.forEach(c=>{
    const s=get(c.dataset.id);
    if(!s.flag && !s.note.trim())return;
    n++;
    out+='## '+c.dataset.label+'  ('+c.dataset.sub+')\\n';
    if(s.flag)out+='- FLAGGED\\n';
    if(s.note.trim())out+=s.note.trim()+'\\n';
    out+='\\n';
  });
  if(!n)out+='_Nothing flagged and no notes yet._\\n';
  const b=new Blob([out],{type:'text/markdown'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b);a.download='elc-proofing-findings.md';a.click();
});

document.getElementById('reset').addEventListener('click',()=>{
  if(!confirm('Clear all checkboxes, flags and notes?'))return;
  localStorage.removeItem(KEY);location.reload();
});

paint();
"""


def render(groups_out, total):
    parts = []
    parts.append("<!doctype html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("<title>ELC proofing packet</title>")
    parts.append(f"<style>{CSS}</style>")
    parts.append("</head><body>")

    parts.append('<header><div class="hrow">')
    parts.append("<h1>Equity Language Commons — proofing packet</h1>")
    parts.append('<span class="count" id="count">0 of 0 done</span>')
    parts.append('<div class="chips">')
    parts.append('<button class="chip" data-filter="todo" aria-pressed="false">Unread only</button>')
    parts.append('<button class="chip" data-filter="flag" aria-pressed="false">Flagged only</button>')
    parts.append("</div></div>")
    parts.append('<div class="bar"><div id="fill"></div></div></header>')

    parts.append("<main>")
    parts.append('<div class="intro">')
    parts.append(
        f"<p><strong>{total} pages.</strong> Not 766. This is the bounded Tier 1 read from "
        "<code>notes/launch-confidence-analysis.md</code> — the pages that carry real "
        "risk, plus a sample to check the rest.</p>"
    )
    parts.append(
        "<p>Only prose you're responsible for is shown: ledes, cross-cutting principles, "
        "synthesis, audience notes. Verbatim source quotes are Layer 1 material and are "
        "already machine-verified — they're deliberately not here.</p>"
    )
    parts.append(
        "<p>Click a page to open it. Check it when read. Hit <em>Flag</em> or type a note "
        "for anything to fix, then <em>Export findings</em> at the bottom for a markdown "
        "punch list. Progress is saved in this browser and survives a rebuild.</p>"
    )
    parts.append("</div>")

    for g in groups_out:
        parts.append('<section class="grp">')
        parts.append(f'<h2>{g["id"]} · {html.escape(g["title"])} ({len(g["entries"])})</h2>')
        parts.append(f'<p class="why">{g["why"]}</p>')
        for e in g["entries"]:
            parts.append(
                f'<article class="card" data-id="{html.escape(e["id"])}" '
                f'data-label="{html.escape(e["label"])}" data-sub="{html.escape(e["sub"])}">'
            )
            parts.append('<div class="top">')
            parts.append('<input class="cb" type="checkbox">')
            parts.append(f'<span class="nm">{html.escape(e["label"])}</span>')
            parts.append('<span class="meta">')
            parts.append(f'<span>{html.escape(e["sub"])}</span>')
            parts.append(f'<span>{e["words"]}w</span>')
            parts.append('<button class="flagbtn" aria-pressed="false">Flag</button>')
            parts.append("</span></div>")
            parts.append('<div class="body">')
            if e.get("note"):
                parts.append(f'<p class="why"><em>{html.escape(e["note"])}</em></p>')
            parts.append(e["html"])
            if e["paraphrases"]:
                parts.append(
                    f"<details><summary>Paraphrases ({len(e['paraphrases'])}) — "
                    "rewritten in the de-dup pass, published prose</summary>"
                )
                for org, p in e["paraphrases"]:
                    parts.append(f"<p><strong>{html.escape(org)}.</strong> {inline(p)}</p>")
                parts.append("</details>")
            parts.append(
                '<textarea placeholder="Notes on this page — anything to fix, '
                'reword, or double-check…"></textarea>'
            )
            parts.append("</div></article>")
        parts.append("</section>")
    parts.append("</main>")

    parts.append("<footer>")
    parts.append('<button class="act" id="expand">Expand / collapse all</button>')
    parts.append('<button class="act" id="export">Export findings</button>')
    parts.append('<button class="act" id="reset">Reset progress</button>')
    parts.append("</footer>")
    parts.append(f"<script>{JS}</script>")
    parts.append("</body></html>")
    return "\n".join(parts)


def main():
    groups_out = []
    used = set()
    missing = []

    # first pass so the sample never re-draws a page already in the packet
    for g in GROUPS:
        if g["kind"] == "term" and isinstance(g["slugs"], list):
            used.update(g["slugs"])

    total = 0
    for g in GROUPS:
        entries = []
        if g["kind"] == "term":
            slugs = resolve_sample(used) if g["slugs"] == "SAMPLE" else g["slugs"]
            for s in slugs:
                e = build_term(s)
                if e is None:
                    missing.append(f"terms/{s}.md")
                    continue
                entries.append(e)
        elif g["kind"] == "chapter":
            for p in sorted((CONTENT / "chapters").glob("*.md")):
                entries.append(build_chapter(p.stem))
        elif g["kind"] == "astro":
            for n in g["slugs"]:
                if not (PAGES / f"{n}.astro").exists():
                    missing.append(f"pages/{n}.astro")
                    continue
                entries.append(build_astro(n))
        total += len(entries)
        groups_out.append({**g, "entries": entries})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(groups_out, total), encoding="utf-8")

    for g in groups_out:
        words = sum(e["words"] for e in g["entries"])
        print(f"  {g['id']}  {len(g['entries']):>2} pages  {words:>6,} words  {g['title']}")
    print(f"\n{total} pages, {sum(e['words'] for g in groups_out for e in g['entries']):,} words")
    print(f"-> {OUT.relative_to(ROOT)}")
    if missing:
        print("\nMISSING (check the packet definition):", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
