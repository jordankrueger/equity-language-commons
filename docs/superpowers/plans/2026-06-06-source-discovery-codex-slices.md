# Source discovery ingestion — Codex slices

**Date:** 2026-06-06
**Decision:** 8 new corpus sources + 2 reference-tier citations, locked by Jordan after the source-discovery research session (`research/source-discovery-2026-06/research-notes.md`, audited).

**Locked source list:**

Corpus sources (guidance-table tier):
1. DCFPI — Style Guide for Inclusive Language (Dec 2017, PDF) — Class anchor
2. PICUM — Words Matter terminology leaflet (Mar 2017, PDF) — Migration
3. The Opportunity Agenda — Social Justice Phrase Guide (2015, PDF) — Movement/cross-cutting
4. CAIR — A Journalist's Guide to Reporting on Islam and Muslims (Aug 2021, PDF — verify content on download; may be image-only) — Faith
5. Religion Stylebook (RNA / Religion Newswriters Foundation, web, CC BY-NC-ND 3.0) — Faith anchor
6. Movement Strategy Center — Glossary + Terms to Avoid (2024, web) — Movement anchor
7. 18Doors — Interfaith Inclusive Language Glossary (2023, web) — Faith
8. HRW — Guidelines for Describing Migrants (2014, web) — Migration

Reference-tier (link-out-only, no archive — same pattern as `sources/ap-stylebook.md`):
9. UNHCR — 'Refugees' and 'Migrants' FAQ (2024)
10. IOM — Glossary on Migration, 3rd ed. (2019)

Explicitly skipped: ADL Antisemitism Uncovered (trope explainer, political drift), AJC Translate Hate (contested framing, defer), ISPU / Momentum / COF (practice guides, weak term-level fit), Blanchet House (too narrow), MIRA (Define American companion, defer), Race Forward Drop the I-Word (corpus overlap), Urban Institute (house style, not equity), APA SES page (APA already a corpus source — deepen existing citations during term work instead).

**Branch discipline:** all three slices work on ONE feature branch `add-discovered-sources-2026-06`. Do NOT merge to main — the final W6 lint findings are expected (they are the point), and Claude writes the term pages before merge. Slices run in order A → B → C.

---

## Slice A — acquire + extract the 4 PDF sources

═══════════════════════ PASTE TO CODEX ═══════════════════════

/goal In repo ~/ClaudeCode/side-hustle/equity-language-commons on branch `add-discovered-sources-2026-06` (create from main if absent), acquire and extract 4 new PDF source guides. STOP when ALL are true: the 4 PDFs exist in `source-guides/discovered/` named `dcfpi-inclusive-language-2017-12.pdf` (from https://www.dcfpi.org/wp-content/uploads/2017/12/Style-Guide-for-Inclusive-Language_Dec-2017.pdf), `picum-words-matter-2017-03.pdf` (from https://picum.org/wp-content/uploads/2023/08/Words_Matter_Terminology_FINAL_March2017.pdf), `opportunity-agenda-social-justice-phrase-guide-2015.pdf` (from https://opportunityagenda.org/wp-content/uploads/2023/01/Social-Justice-Phrase-Guide.pdf), `cair-journalists-guide-2021-08.pdf` (from https://www.cair.com/wp-content/uploads/2021/08/MediaGuide.pdf — if 403, retry with a browser User-Agent header); each PDF is a real PDF (`file` says PDF, `pdfinfo` returns a page count); each has a sibling `.md` extraction produced by running `./scripts/extract-pdfs.sh` scoped to ONLY that file (read the script first to find the single-file invocation — NEVER pass `--force` without a file argument, it clobbers committed OCR in other files) with density >200 bytes/page, EXCEPT any image-only PDF (likely CAIR) which instead gets `--ocr` and a >50-line extraction; spot-check strings confirm right documents (DCFPI .md contains "People facing barriers" or "Working hard to make ends meet"; PICUM .md contains "undocumented" and "irregular"; Opportunity Agenda .md contains "People with felony convictions"; CAIR .md mentions "jihad" or "Sharia"); `source-guides/MANIFEST.md` gains one row per file in the discovered-tier table matching the existing column format (File | Org | Title | Year | Scope | Host) with Scope=In and Host=Link for all 4; `git diff --stat main -- source-guides/` shows ONLY the 8 new files plus MANIFEST.md — zero modifications to any pre-existing extraction .md (this guards the known --force clobber incident); all work is committed on the branch with a descriptive message. Do not run the coverage matrix, scaffolders, or site build — that is a later slice.

═══════════════════════════════════════════════════════════════

## Slice B — scrape the 4 web sources to markdown

═══════════════════════ PASTE TO CODEX ═══════════════════════

/goal In repo ~/ClaudeCode/side-hustle/equity-language-commons on branch `add-discovered-sources-2026-06`, scrape 4 web-based source guides into verbatim markdown archives in `source-guides/discovered/` (follow the existing web-scraped pattern, e.g. `hrc-glossary-2023-05.md` — a header block noting source URL + access date + tool, then faithful content). STOP when ALL are true: `religion-stylebook-2026-06.md` contains the Religion Stylebook entries scraped from https://religionstylebook.com/ — at minimum the complete Judaism and Islam category entries (https://religionstylebook.com/entries/category/judaism and .../islam), each entry as `## <term>` + its full definition text, fetched politely (≥1s delay between requests), and contains the strings "Follower of the Jewish faith" and "reordering government and society in accordance with laws prescribed by Islam"; `movement-strategy-center-glossary-2024.md` contains the full glossary AND the Terms to Avoid section from https://movementstrategy.org/glossary/ including the strings "allocating the exact resources" and "Able-bodied"; `18doors-interfaith-glossary-2023.md` contains the glossary from https://18doors.org/glossary-of-terms/ including the entries for non-Jew, shiksa, goy, convert, and patrilineal/half-Jew (string check: "fully Jewish"); `hrw-describing-migrants-2014-06.md` contains the full statement from https://www.hrw.org/news/2014/06/24/human-rights-watch-guidelines-describing-migrants including the strings "Unauthorized migrants" and "illegal aliens"; `source-guides/MANIFEST.md` gains one row per file (format/web noted in File or Title cell as the existing web-scraped rows do; Scope=In; Host=Link for MSC/18Doors/HRW, Host=Archive for Religion Stylebook with note "CC BY-NC-ND 3.0"); `git diff --stat main -- source-guides/` shows only additions from this slice and slice A; committed on the branch. Scrape verbatim — do not summarize, paraphrase, or reformat definition text beyond markdown structure. Do not run the coverage matrix or site build.

═══════════════════════════════════════════════════════════════

## Slice C — reference-tier pages + pipeline rebuild + W6 report

═══════════════════════ PASTE TO CODEX ═══════════════════════

/goal In repo ~/ClaudeCode/side-hustle/equity-language-commons on branch `add-discovered-sources-2026-06`, bring the 8 new sources online and surface newly-qualified terms. STOP when ALL are true: two new reference-tier source pages exist — `site/src/content/sources/unhcr.md` (UNHCR, "'Refugees' and 'Migrants' — Frequently Asked Questions", 2024, source_url https://emergency.unhcr.org/sites/default/files/2024-01/2.%20Refugees%20and%20migrants%20FAQ.pdf) and `site/src/content/sources/iom-glossary.md` (IOM, "Glossary on Migration — International Migration Law No. 34", 2019, source_url https://publications.iom.int/books/international-migration-law-ndeg34-glossary-migration) — both copying the exact frontmatter shape and link-out-only posture of `site/src/content/sources/ap-stylebook.md` (host_posture "link-out-only", local_archive null, an About section explaining they are legal-definitional references not equity guides, and an Access section; keep About prose factual and minimal — Claude will polish); the pipeline has been run in this order with each script exiting 0: `./scripts/build-coverage-matrix.py`, `./scripts/scaffold-source-pages.py`, `./scripts/enrich-source-pages.py`, `python3 scripts/build-glossary-index.py` (check exact name/invocation in scripts/); scaffolded stub source pages exist for all 8 new corpus source slugs from slices A+B; `cd site && npm run build` completes with exit 0; `./scripts/lint-content.py --strict` has been run and its FULL output saved to `notes/source-discovery-2026-06-w6-report.md` with a header noting the date and branch — W6 findings (newly ≥3-source terms without pages) are EXPECTED and are the deliverable of this slice, do NOT silence them by editing coverage-decisions.yml, deleting glossary entries, or modifying the lint script, and any lint failure that is NOT a W6 finding must be fixed before stopping; `git status` is clean (everything committed on the branch, including regenerated `site/src/data/glossary-index.json` and `site/public/data/elc-index.sqlite`); the branch is NOT merged to main and nothing is deployed.

═══════════════════════════════════════════════════════════════

## After Codex (Claude's work, next session)

1. Read `notes/source-discovery-2026-06-w6-report.md` — the W6 list is the term-page work queue.
2. Verify slice A/B extractions against the live sources (Layer 1 conventions).
3. Polish the 8 scaffolded source pages (About/Access prose, real metadata) + the 2 reference-tier pages.
4. Graduate `jew`/`islam` from verified-hold (Religion Stylebook is the 3rd source) — remove from `notes/curated-glossary-overrides.yml`, write full pages.
5. Write/expand term pages per W6: expect Faith chapter growth, Movement & Advocacy chapter unlock (check `ally`, activist, advocate, tolerance, equality counts), Class additions (poor, poverty, at-risk, vulnerable, food stamps, working poor), Migration round-out (asylum-seeker, migrant possibly now ≥3).
6. Re-run matrix + lint until `--strict` green, Layer 1/2 verification on new pages, then merge branch → main → deploy.
