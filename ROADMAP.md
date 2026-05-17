# Equity Language Commons — Roadmap

**Status as of 2026-05-17 (afternoon):** Phases 0, 1, and most of Phase 2 complete. Phase 2.5a (`scripts/extract-pdfs.sh`) shipped — all 17 PDFs in `source-guides/` now have grep-able markdown siblings, including OCR for NAJA. Phase 2.5b (`scripts/build-coverage-matrix.py`) shipped — 26 sources scanned, 1,273 unique terms across the universe, 2,672-row CSV at `notes/term-coverage-matrix.csv`, ranked MD at `notes/term-coverage-matrix.md`. Top non-indexed candidates by cross-source coverage: `asian` (15), `community` (15), `diversity` (13), `families` (13), `discrimination` (12), `illegal` (12), `immigrant` (12), `victim` (12), `transgender` (10), `tribe` (8).

**Status as of 2026-05-16:** Phases 0, 1, and most of Phase 2 complete. GitHub remote live at `jordankrueger/equity-language-commons` (private). CF Pages preview build live at `https://equity-language-commons.pages.dev/` (Wrangler direct-upload via `./scripts/deploy.sh`; one-time GitHub auto-deploy wire-up still pending Jordan's CF dashboard click). Phase 3 underway — **Race & Ethnicity chapter at 16 indexed terms** (up from 1) covering the highest cross-source-coverage R&E vocabulary in the in-scope corpus. R&E chapter intro rewritten with 6 cross-cutting principles drawn from the actual term patterns. Build clean, 44 static pages.

**Status as of 2026-05-14:** Phases 0 and 1 complete. Phase 2 is well underway — Astro site scaffolded under `site/`, content collections defined for terms / sources / chapters with Zod schemas mirroring schema v0.3, 3 test terms migrated into the collection, 16 source entries (1 fleshed out, 15 stubs), 5 chapter entries (1 fleshed out, 4 stubs), all 8 page templates built, build clean, dev server verified. Domain `equitylanguagecommons.org` secured. Project renamed from "Progressive Language Commons" to "Equity Language Commons" today.

## Direction (locked 2026-04-23)

- **Shape:** Option C — cross-referenced omnibus with sourced excerpts. Per term, show every org's rule side-by-side (short fair-use quote + paraphrase + year + source link + synthesis note where needed).
- **Name:** Equity Language Commons. (Renamed 2026-05-14 from working title "Progressive Language Commons.") Domain `equitylanguagecommons.org` secured. GitHub repo: `equity-language-commons`.
- **Branding:** Side-hustle only. Not CampaignHelp-branded. Gift-to-the-community posture.
- **License (cross-reference layer):** CC-BY 4.0 — the commons's original curation is attributable and reusable.
- **License (source guides):** tiered per host posture below.
- **Tech stack:** Astro → Cloudflare Pages. Pagefind client-side search. R2 for mirrored PDFs. GitHub repo under `jordankrueger/` account.

## Editorial voice (locked 2026-04-24)

- **No blame-leaning language about source-guide authors or orgs.** Everyone was doing their best with what they had at the time. Describe what each guide does, name dates and context, and let chronology speak for itself. "Pre-dates X," "earlier than," "written before Y settled into practice" — not "outdated," "behind," "hasn't aged well."
- Editorial synthesis is welcome — positions, trends, practical guidance, audience-aware advice. Editorial judgment of individual authors is not.

## Display direction (locked 2026-04-24)

Two reading modes need to coexist:
1. **Chapters** — readers can browse a whole category top-to-bottom like a reference book (e.g., "Race & Ethnicity")
2. **Term index + search** — readers can jump to a specific term via A–Z index or full-text search

Primary design constraint: **attribution clarity.** Every term page must make three things immediately visible:
- **Who** said what (org names, prominent, linkable)
- **When** they said it (publication year + entry-updated date where distinct)
- **Where each source landed** (visible recommendation badge: use / use-with-care / non-preferred / avoid / contested / evolving / reclaimed-in-community)

## Routing (locked 2026-04-24)

| URL | Purpose |
|---|---|
| `/` | Homepage |
| `/chapters/<category-slug>/` | Chapter browse (e.g., `/chapters/race-ethnicity/`) |
| `/terms/` | A–Z term index |
| `/terms/<term-slug>/` | Individual term page (e.g., `/terms/latinx/`) |
| `/sources/` | All-sources index |
| `/sources/<org-slug>/` | Source landing page — **one per org, newest edition canonical** |
| `/about/` | About the commons |

When an org publishes a new edition, it becomes the current canonical version on its source page; the prior edition moves to a "Version history" section on the same page. Older editions aren't cited as standalone sources in term entries — term entries record the edition via `year` + `entry_updated` fields.

## Host posture per source (locked 2026-04-24)

Every source gets one of three postures, chosen per `source-guides/MANIFEST.md`:

| Posture | When used | Examples |
|---|---|---|
| **Host publicly** | Orphaned / defunct works with no active rights-holder | SumOfUs 2016 |
| **Private mirror + link-out** | Active orgs with no reuse grant, but static guide | Sierra Club 2021, NGC 2021, Casey 2013, SEIU 2020 |
| **Link-out only (no mirror)** | Living documents, peer aggregators — a snapshot would misrepresent | TJA, Diversity Style Guide, Racial Equity Tools |

Private preservation copies are kept regardless of public posture, so that cited quotes remain verifiable even when the original source goes offline.

## License findings (2026-04-24)

Checked 4 active-org guides. **None carry explicit reuse permission.** All display only "© [org]" footers. No Creative Commons marks, no "may be reproduced" language.

- Sierra Club Equity Language Guide (2021) — no license; **canonical URL returns 404**; archived PDF may be the only accessible copy
- Native Governance Center Style Guide (2021) — no license; freely downloadable from nativegov.org
- TJA Stylebook (2026) — no license; living web document, entries versioned individually
- Diversity Style Guide (2023) — no license; living web document + peer aggregator

The "never host an active org's PDF publicly without explicit permission" guardrail is correct for all four.

## Inspiration / spiritual predecessor

**"A Progressive's Style Guide"** — Hanna Thomas (SumOfUs) + Anna Hirsch (ActivistEditor), 2016.
- PDF local: `source-guides/discovered/sumofus-progressive-styleguide-2016.pdf`
- SumOfUs merged into Ekō in 2022; guide is effectively orphaned.
- Jordan will reach out to Hanna Thomas before launch — courtesy notice, spiritual-successor framing.
- Do not reuse the "A Progressive's Style Guide" name.

## Phases

### ✅ Phase 0 — Research & discovery (complete)

- 6 guides in the archive inventoried + scope-filtered (4 in-scope, 2 out)
- Update check on 4 in-scope archived orgs — 3 are effectively dark (Sierra Club 404; Casey + SEIU pulled from public)
- 12 new guides discovered from candidate orgs (Tier 1 + Tier 2)
- Listserv mining via notmuch on Kingston SSD — 15+ style-guide threads in RadComms + GameChanger Salon — found SumOfUs predecessor and 9 additional guide candidates
- 33 total files archived in `source-guides/` + `source-guides/discovered/`
- Full research trail in `research/research-notes.md`

### ✅ Phase 1 — Schema design + 3 test terms (complete 2026-04-24)

**Approach change from the original plan:** Top-down taxonomy design is deferred. Taxonomy emerges bottom-up from populated term entries. Categories are free-form strings in frontmatter; formal taxonomy gets drafted after ~10 real terms exist and the natural shape is visible.

- [x] Draft YAML frontmatter schema (`notes/schema.md`; v0.1 → v0.2 → v0.3)
- [x] Pick 3 test terms: `Latinx`, `unhoused/homeless`, `Indigenous`
- [x] **Populate test term #1 — Latinx** (8 source citations, Latinx/Latine/Latino/Hispanic cross-linked)
  - Schema v0.2 fixes: `non-preferred` recommendation, `VERIFIED-ARCHIVED` confidence, multiple guidance entries per org allowed, `related_terms` separate from `aliases`, `entry_updated` per-guidance, top-level `context_data` for cited empirical data, `audience_notes` promoted to standard field.
- [x] **Populate test term #2 — `unhoused/homeless`** (2 direct-guidance sources: SumOfUs 2016 + DSG 2023; 1 external-ref: TJA; 3 methodological-context: NCDJ, APA, Radical Copyeditor). Time-capsule shape: 2016→2023 migration in approved construction (identity-first → person-first) and vocabulary ("unhoused" entering). Prototyped `external_references[]` + `methodological_context[]` inline.
- [x] **Populate test term #3 — `Indigenous`** (11 direct-guidance sources; pan-national cluster; three distinct postures — Indigenous as umbrella, as US-editorial default, as sovereignty-first framing). Schema stressed further: `derived_from` per guidance, `geographic-variant` + `gendered-or-dated-form` relations, `SUMMARY-ONLY` confidence.
- [x] **Schema v0.3 locked** (2026-04-24): added `external_references[]`, `methodological_context[]`, per-guidance `derived_from`, two new `relation` values, one new `confidence` value. Deferred: chapter-content type, `avoided_terms[]`, controlled category/tag vocabularies, context_data as shared type. See `notes/schema.md` v0.3 lock section.

Artifacts from Phase 1:
- `notes/schema.md` (v0.3 locked)
- `notes/test-terms/latinx.md`, `notes/test-terms/latinx-extraction.md`
- `notes/test-terms/unhoused-homeless.md`, `notes/test-terms/unhoused-homeless-extraction.md`
- `notes/test-terms/indigenous.md`, `notes/test-terms/indigenous-extraction.md`
- `notes/taxonomy-comparison.md`

Housekeeping surfaced during Phase 1:
- **NAJA file naming mismatch:** `source-guides/discovered/naja-indigenous-terminology-2023-06.pdf` has PDF metadata creation date 2017-04-08. Actual poster is 2017. Update MANIFEST.md dating (and consider renaming file to `naja-indigenous-terminology-2017.pdf`).
- **Phase 2 acquisitions queued:** Homelessness Beat Reporters Collective reporting guide; Radical Copyeditor's "Thirty Everyday Phrases that Perpetuate the Oppression of Indigenous Peoples" (2020-10); full APA Inclusive Language Guide (archive currently a WebFetch summary); NAJA Tribal Nations Media Guide 2020. Queue in `research/research-notes.md`.

### 🔄 Phase 2 — Design previews + site scaffold (in progress)

**Design previews built early to pressure-test the schema + routing against real display.** Standalone HTML, single-file, inline CSS, no build step — quick-iterate format.

Done:
- [x] `preview/latinx.html` — term page with all display elements (At-a-glance table, synthesis, source cards sorted chronologically, context data, audience notes, history, related terms)
- [x] `preview/sierra-club.html` — source landing page (access posture panel, publication details, version history scaffold, terms citing this source)
- [x] `preview/index.html` — A–Z term index
- [x] `preview/race-ethnicity.html` — chapter browse page
- [x] Visual language locked: cream ground, Charter serif headings, system sans body, terracotta accent, color-coded recommendation badges, mobile-responsive
- [x] **Scaffold Astro project under `site/`** (Astro 5 + TypeScript strict)
- [x] **Content collections for `terms`, `sources`, `chapters`** (Zod schemas in `site/src/content.config.ts`, mirror `notes/schema.md` v0.3)
- [x] **Migrate 3 test terms into `site/src/content/terms/`** (via `git mv` from `notes/test-terms/`)
- [x] **16 source entries created** — Sierra Club fleshed out; 15 stubs auto-generated from term frontmatter so URLs/years/archive paths are pre-populated
- [x] **5 chapter entries created** — Race & Ethnicity fleshed out; 4 stubs for categories referenced by test terms
- [x] **Port preview HTML/CSS into Astro layouts + components** — `BaseLayout`, `SiteHeader`, `SiteFooter`, `Breadcrumb`, `RecBadge`, `GuidanceCard`; global stylesheet extracted from previews
- [x] **All 8 page templates built** — `/`, `/about/`, `/terms/`, `/terms/[slug]/`, `/sources/`, `/sources/[slug]/`, `/chapters/`, `/chapters/[slug]/`
- [x] **Source page auto-builds a reverse "Terms citing this source" index** — adding a new term that cites Sierra Club shows up on the Sierra Club page automatically; no manual cross-linking
- [x] **Build verified clean** — 29 static pages, no schema errors, dev server runs at `http://jordans-mac-mini:4321/`
- [x] **Git initialized** with two commits: baseline + scaffold

Remaining:
- [ ] Verify Sierra Club guide page count / section count against actual PDF (placeholder values currently)
- [ ] Acquire 4 queued source guides (Homelessness Beat Reporters, Radical Copyeditor 30-phrases, full APA Inclusive Language Guide, NAJA Tribal Nations Media Guide 2020)
- [x] Set up remote GitHub repo at `jordankrueger/equity-language-commons` (private to start) — done 2026-05-16
- [ ] Wire Pagefind client-side search
- [x] Deploy to Cloudflare Pages on the `pages.dev` URL (not yet pointed at custom domain) — done 2026-05-16 via Wrangler direct upload (`./scripts/deploy.sh`); GitHub auto-deploy via CF dashboard pending Jordan
- [ ] Fill out the 15 source stubs over time as more terms get added (8 new sources cited in R&E batches need verification of stub auto-generation)

### Phase 2.5 — Tooling to reduce LLM tax before Phase 3 scales (added 2026-05-16)

The 2026-05-16 R&E batch session surfaced where LLM time is being spent vs. where it's actually adding value. Three pieces of tooling, built once, would make every subsequent Phase 3 batch 2–3x more efficient. Build before the next term batch.

#### ✅ 2.5a — PDF→markdown extractor for archived source guides (shipped 2026-05-17)

**Problem:** The 6 archived PDFs in `source-guides/*.pdf` (Sierra Club, NGC, AECF, SEIU, yli, Stand.earth) are read page-by-page during term research, burning significant context per term. The 27 already-converted markdown files in `source-guides/discovered/` are grep-able instantly.

**Built:** `scripts/extract-pdfs.sh` — runs `pdftotext` (poppler) over every PDF in `source-guides/` and `source-guides/discovered/`, writes a sibling `.md` with a slug matching the org_slug-YYYY-MM convention. Flags: `--dry-run`, `--force`, `--layout`. Hardcoded slug overrides for the 6 archived PDFs (whose original filenames don't slugify cleanly). Emits a `⚠ low text density` warning when output density is < 200 bytes/page (image-only PDF that needs OCR).

**Outcome:** 17 PDFs converted (6 archived + 11 from discovered/). Total grep-able corpus: 27 pre-existing `.md` + 17 new = 44 source markdowns. Per-term PDF-reading context tax should drop to ~0 for 16 of 17.

**Known gap:** `naja-indigenous-terminology-2023-06.pdf` extracted to only 201 bytes (2 pages) — it's an image-only PDF. NAJA is a primary source for the Indigenous & Tribal Sovereignty chapter (next chapter up). Needs OCR (`tesseract` or `ocrmypdf`) before the Indigenous chapter starts, or manual transcription. Also: NGC PDF has smart-quote rendering glitches (`"` → `<...=`) — text is still grep-able but quotes need PDF verification before publication.

**Rule:** Re-run when a new PDF is dropped in. Output is gitignored-eligible (machine-extractable) but currently committed for grep-ability across worktrees.

#### ✅ 2.5b — Term coverage matrix (shipped 2026-05-17)

**Problem:** Survey step at the start of every Phase 3 batch — "which terms are well-covered across sources?" — was being done by ad-hoc `grep` each time. The same per-term rediscovery, repeated forever.

**Built:** `scripts/build-coverage-matrix.py` — two-pass extractor.
- **Pass 1 — structured glossary extractors** for the 6 sources with clean term-entry markup: TJA, DSG, NCDJ, HRC, NLGJA, Radical Copyeditor (trans guide). Together these yield ~1,490 candidate terms.
- **Pass 2 — keyword scan** over the 20 narrative/non-glossary sources (Sierra Club, NGC, Casey, SEIU, SumOfUs, NABJ, NAJA, Color of Change, etc.), looking for occurrences of any glossary term in the universe.
- **Filters:** universe stopwords dropped (`the`, `a`, `or`, ...); inverted-glossary fragments dropped (DSG's "Great Migration, the" no longer leaks "the"); Radical Copyeditor metadata keys (`source`, `author`, `published`) blocklisted; common single-word noise (`american`, `family`, `mass`, `red`, ...) blocklisted from keyword scan only — glossary entries for those terms still count.
- **Normalization:** hyphens collapse to spaces, so the indexed slug `african-american` matches DSG's `african american` and the narrative `African American` in Sierra Club.

**Outputs:**
- `notes/term-coverage-matrix.csv` — one row per (term × source) hit, ~2,670 rows. Columns: `term_normalized`, `source_slug`, `line`, `excerpt`, `extraction_method` (glossary/keyword), `has_avoid_marker`, `has_capitalization_rule`.
- `notes/term-coverage-matrix.md` — ranking. Top 50 candidates excluding indexed terms; indexed terms with current coverage; full ranking. Use the top-50 section to pick the next Phase 3 batch.

**Findings worth flagging:**
- `chicanx` — 0 hits across all 26 sources. Indexed Chicanx page is the thinnest-sourced in the R&E chapter.
- `unhoused-homeless` — 0 hits because the indexed slug is a comparison compound, not a single phrase. Caveat noted in the MD output.
- Top non-indexed candidates by coverage: `asian` (15), `community` (15), `diversity` (13), `discrimination` (12), `illegal` (12), `immigrant` (12), `victim` (12), `transgender` (10), `tribe` (8). The Indigenous chapter's natural starting terms (`tribe`, `indigenous`, `native american`, `tribal`) all show up well-covered.

**Rule:** Re-run after each Phase 3 batch (new terms indexed → fresh "what's left" ranking) and after new sources are dropped into `source-guides/`.

#### 2.5c — Source page enrichment (one-time research session)

**Problem:** 15 of 16 source pages are stubs auto-generated from term frontmatter. Each needs: publication year, page/section count, license findings, host posture rationale, access posture panel content, version history (if any), live status check. None of this needs LLM cross-corpus synthesis; it's per-source metadata research.

**Build:** A focused 60–90 minute session per source (not LLM-driven), OR a script (`scripts/enrich-source-pages.py`) that reads PDF metadata + filename + MANIFEST.md to pre-populate the metadata fields, leaving only the qualitative parts for human input. Most leveraged if combined with the live-status check via a simple HEAD request to each `source_url`.

**Rule:** Run after every Phase 3 batch to update any newly-cited source stubs. Trigger: build report showing N terms cite source X but source X is still `stub: true`.

**Time saved:** Eliminates the "LLM writing source page from scratch" pattern, which is wrong-tool work. Cost: maybe 2 hours for the enricher script + 60–90 min per source for the qualitative pieces (15–20 hours total across all current source stubs, but spread across batches).

#### 2.5d — Recommended order

1. **First**: 2.5a (PDF extractor) — fastest, unblocks 2.5b
2. **Second**: 2.5b (coverage matrix) — highest leverage on remaining Phase 3 work
3. **Third**: 2.5c (source page enricher) — can be in-progress in parallel with Phase 3 batches; not blocking

After 2.5a + 2.5b land, **Phase 3 term batches should drop from ~3 hours / 5 terms to ~60–90 min / 5 terms**, with the LLM time concentrated on synthesis, paraphrase, and audience notes — the work that actually requires cross-corpus judgment.

### Phase 3 — Bulk term indexing (iterative, one category at a time)

Chunk by the taxonomy that emerges from the first ~10 terms. Aim ~20–40 terms per category. Each category is a focused session.

Likely categories (subject to what emerges):
- [~] Race & Ethnicity — **16 terms indexed as of 2026-05-16** (african-american, asian-american, bipoc, black, brown, caucasian, chicanx, hispanic, latine, latino, latinx, minority, multiracial, people-of-color, urban, white). Chapter intro rewritten with 6 cross-cutting principles. Need ~8–15 more terms to round out the chapter for launch: probably mestizo, afro-latino, mena, native-hawaiian, biracial-as-its-own-page (currently aliased), south-asian, mixed-race subset entries, model-minority, anti-Black, racism vs. prejudice, white supremacy, white nationalism, white privilege, microaggression, gentrification, racial-coding entries like "thug" and "articulate".
- [ ] Indigenous & Tribal Sovereignty
- [ ] Gender & Sexuality (with trans subcategory)
- [ ] Disability
- [ ] Age
- [ ] Class & Wealth
- [ ] Labor & Workers
- [ ] Housing — 1 term (unhoused-homeless); needs ~15 more
- [ ] Immigration & Refugees
- [ ] Incarceration & Policing
- [ ] Sexual & Domestic Violence
- [ ] Health
- [ ] Food (sovereignty, deserts, labor intersection)
- [ ] Environment / Climate
- [ ] Religion & Culture
- [ ] Reproductive Rights

### Phase 4 — Quiet build → public launch

**No "soft launch." No private reviewer round.** Build until the site is launch-ready, then flip it public in one motion. Friends-and-family preview rounds make launches feel like failure-by-default — the work is either published or it isn't.

Launch readiness criteria:
- [x] Domain secured — `equitylanguagecommons.org` (2026-05-14)
- [ ] ~50 terms published across 3–4 chapters, enough breadth that the cross-reference value is immediately visible to a first-time reader
- [ ] All 16+ source pages filled out (not stubs); access-posture panels accurate
- [ ] At least 2 chapters with real cross-cutting-principle intros and term lists
- [ ] Final legal pass: per-source attribution, CC-BY notice on curation layer, fair-use posture clear on every quoted passage
- [ ] Pagefind search wired and indexing the live content
- [ ] Deployed to Cloudflare Pages on `equitylanguagecommons.org` — DNS flip is the launch
- [ ] Homepage doesn't read like a stub — about page, contributing posture, and source list are all complete

During build, deploy to the `equity-language-commons.pages.dev` URL but don't publicize it. That URL is for build-validation, not feedback collection.

### Phase 5 — Post-launch outreach + community

Outreach happens **after** the public site is live, not before. Source orgs and peers see the actual finished work, not a preview link with notes attached.

- [ ] Email Hanna Thomas (SumOfUs) — courtesy + spiritual-successor framing, point to the live site
- [ ] Email active source orgs whose guides are cross-referenced — Sierra Club, GLAAD, TJA, APA, NCDJ, NGC, NABJ, NAJA, AAJA, IDP, Dart Center, Race Forward, interACT, Define American, Color of Change, HRC, Radical Copyeditor, Words about War Matter. Frame as notification + acknowledgment of their work, not permission-seeking.
- [ ] Email Conscious Style Guide + Diversity Style Guide maintainers as professional courtesy (peer projects, not competitors)
- [ ] Public announcement in RadComms + GameChanger Salon listservs
- [ ] LinkedIn post from Jordan's personal account (not CampaignHelp)
- [ ] Decide on contribution workflow — opens to community submissions once enough breadth exists to be a recognizable peer project

### Phase 6 — Maintenance rhythm

Ongoing, not a phase in the usual sense.

- Quarterly: re-check for new editions of source guides (TJA updates per-entry; several update annually)
- As found: add new source orgs + new terms
- Accept PR contributions from the community once a contribution workflow exists
- Log `last_reviewed` per term

## Open questions / parked decisions

- **Domain name** — ~~pick before Phase 5 outreach~~ resolved 2026-05-14: `equitylanguagecommons.org`
- **User submissions at v1 or v2** — Google Form → GitHub issue workflow is the lightest-weight option for non-technical contributors
- **Downloadable "everything" PDF** — useful offline but more copyright-sensitive; later decision
- **Relationship with Conscious Style Guide / Diversity Style Guide** — sibling resources; decide outreach framing (complementary, not competitive)
- **Controlled vs. free-form taxonomy** — let it stay free-form until ~10 terms exist and the natural shape is visible
- **Whether `related_terms.relation` enum is exhaustive** — add values as new relationship types appear
- **Whether `context_data` becomes its own content type** (cited from many terms) instead of embedded per-term — decide after 2–3 more terms are populated

## Guardrails

- Never host an active org's PDF publicly without explicit permission
- Every direct quote under 50 words (fair-use safety margin) unless permissioned
- Every quote cites: org, year, source URL or canonical reference
- `research/research-notes.md` is the audit trail — every claim must be traceable
- Do not reach out to source orgs or Hanna Thomas until **Phase 4 is complete and the public site is live** — outreach is post-launch, not pre-launch (see Phase 5)
