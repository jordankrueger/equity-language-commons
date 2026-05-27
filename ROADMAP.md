# Equity Language Commons — Roadmap

**Status as of 2026-05-18 (end-of-session 2):** Phases 0–2.7 all complete. Phase 3 in progress across **3 active chapters** — Race & Ethnicity (18 terms), Indigenous & Tribal Sovereignty (5 terms), Sexuality & Gender Identity (10 terms). **33 indexed terms total.** Build clean, 73 static pages.

**Today's shipped work (session 2):**
- LGBTQ+ chapter rounded out from 5 → 10 terms: bisexual, lesbian, cisgender, intersex, sexual-orientation added with cleanup-pass-verified guidance + written synthesis + audience notes. Two SEIU/TJA inversions caught and corrected.
- Phase 2.7 tooling all landed: Glossary Index page + scaffolder (`scripts/build-glossary-index.py`), SQLite build-time index (`scripts/build-sqlite-index.py`), Contribute page (`/contribute/`). Glossary Index merged with A-Z browse (one page, filter chips) per Jordan's Option 1 call.
- Repo scaffolding for community contributions: LICENSE (3-layer CC-BY/MIT/fair-use), README, CONTRIBUTING, CODE_OF_CONDUCT (Contributor Covenant 2.1), 4 issue templates, Discussions enabled. Repo remains private until launch per Jordan's call.
- `notes/cleanup-pass-prompt.md` written as the standing subagent instruction set for cleanup passes after `scaffold-term.py` batches. Captures editorial voice, fair-use rules, source removal rules, and three common error patterns (SEIU "Correct: X / Not: Y" inversion, related_terms classification, quote attribution direction).
- Sources page UX fix: `private-mirror-link-out` posture now renders as two discrete chips ("Private mirror" / "Links out") instead of run-on phrase.
- Legacy `## Cross-references` prose block stripped from 18 R&E term files — was duplicating the auto-generated "Related terms" section. Substantive operational detail (Aboriginal/Australia, Alaska Native subsets, Inuit/Eskimo, Two-Spirit) folded into indigenous.md synthesis before stripping.
- `related-concept` added to RELATION enum (catch-all for non-identity-overlap connections; prejudices, concepts, legal/geographic adjacencies). Five term files reclassified.
- Editorial fix: asian-american SEIU recommendation flipped `avoid` → `use` (SEIU inversion pattern).

**Open notes for pick-up next session** (in priority order):

1. **Sierra Club URL refresh.** `source-url` on sierra-club.md returns 404. Affects ~30 term-page citations. Search for current canonical URL.
2. **Next chapter: Disability & Mental Health** (strongest unstarted; NCDJ dedicated source). Or **Immigration & Citizenship** (next-strongest, politically high-impact, Define American dedicated source).
3. **Round out LGBTQ+** with nonbinary, deadnaming, outing if reaching for completeness (not strictly needed for launch).
4. **Manual items Jordan owes** (tracked in Drift): Cloudflare Email Routing setup, GitHub Discussion categories, GitHub auto-deploy in CF dashboard.

**Earlier session status block (2026-05-18, session 1):** Phases 0–2.6 complete. Phase 3 underway across **3 chapters** — Race & Ethnicity (16 terms), Indigenous & Tribal Sovereignty (5 terms), Sexuality & Gender Identity (5 terms). Indigenous chapter intro shipped (6 cross-cutting principles + chronology). Sexuality & Gender Identity chapter intro shipped (7 cross-cutting principles + chronology). 28 indexed terms total.

**Launch scope expanded 2026-05-18.** Original "~50 terms / 3-4 chapters" target was a minimum-viable-launch threshold. After looking at actual matrix data — 268 terms have ≥3 sources, ~180 have ≥4 — Jordan locked the full-launch threshold at **≥3 sources, ~250 commons-style term pages across 8-10 chapters, plus a Glossary Index for the ~1,000-term long tail.** No soft launch — full public launch when ready, per `feedback_no_soft_launches`. Phase 4 criteria revised accordingly.

**Stale URLs fixed 2026-05-18** via pipeline re-run: NAJA → `indigenousjournalists.org/ap-style-insert/` (post-IJA rebrand), NABJ → `nabj.org/page/styleguide`, Define American → `defineamerican.com/resources-for-journalists/`. `KNOWN_URLS` map in `scaffold-source-pages.py` updated. Sierra Club URL now returns 404 — flagged for pick-up.

**Phase 2.7 added 2026-05-18** — three new tooling pieces to support the expanded scope: Glossary Index scaffolder + page, SQLite build-time index, and Contribute page. All shipped end-of-day. See §Phase 2.7.

**Status as of 2026-05-17 (end-of-session):** Phases 0, 1, 2, 2.5, and 2.6 all complete. The full programmatic pipeline ships:

| Stage | Script | Purpose |
|---|---|---|
| 1 | `scripts/extract-pdfs.sh` | PDF → grep-able markdown sibling (with `--ocr` fallback for image-only PDFs) |
| 2 | `scripts/build-coverage-matrix.py` | Walk corpus, output term universe + ranked candidate list |
| 3 | `scripts/scaffold-source-pages.py` | Create source pages for any matrix source missing one (reads MANIFEST.md) |
| 4 | `scripts/enrich-source-pages.py` | Fill mechanical metadata on all source pages (pdfinfo + HEAD checks) |
| 5 | `scripts/scaffold-term.py <slug>` | Pre-populate a term .md from the matrix — ready for LLM refinement |
| 6 | `scripts/deploy.sh` | Build + Wrangler upload to CF Pages |

Corpus state: 27 source pages (15 fleshed-out + 12 new stubs), 26 of 33 sources scanned by matrix (7 excluded as non-glossary/out-of-scope), 1,273 unique terms in universe, build clean at **56 pages**.

**Phase 3 is unblocked.** Workflow: pick term from `notes/term-coverage-matrix.md` top-50 → `./scripts/scaffold-term.py <slug>` → review + tighten quotes + write synthesis + audience_notes → remove `stub: true` → commit. Target: 8–12 min/term.

Known stragglers carried into Phase 3:
- NAJA `source_url` (`naja.com`) is dead — needs update to `indigenousjournalists.org`
- `KNOWN_URLS` in `scaffold-source-pages.py` had stale NABJ + Define American URLs (returned 404 on live-check)
- Recommendation classifier doesn't catch semantic negation (e.g., SumOfUs's "a person is never illegal" classifies as `use-with-care` not `avoid` — easy LLM-time fix during scaffold review)
- Source-page About sections (all 27) still need to be written for Phase 4 launch — Phase 2.6 #3 (About generator) is the deferred "do this before launch" item

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
- [x] Set up remote GitHub repo at `jordankrueger/equity-language-commons` (private to start) — done 2026-05-16
- [x] Deploy to Cloudflare Pages on the `pages.dev` URL — done 2026-05-16 via Wrangler direct upload (`./scripts/deploy.sh`); GitHub auto-deploy via CF dashboard pending Jordan
- [x] Source-page mechanical metadata filled out — done 2026-05-17 via `enrich-source-pages.py` (length_pages, format, live_status, dates)
- [ ] **Wire Pagefind client-side search** — needed for Phase 4 launch
- [ ] **Write About sections for all 27 source pages** — Phase 4 launch gate. Either manually as part of Phase 3 batches, or build Phase 2.6 #3 (source-page About generator) to batch-process.
- [ ] Verify Sierra Club guide page count / section count against actual PDF (placeholder values currently — note: enrich script pulled `length_pages: 40` from pdfinfo)
- [ ] Acquire 4 queued source guides (Homelessness Beat Reporters, Radical Copyeditor 30-phrases, full APA Inclusive Language Guide, NAJA Tribal Nations Media Guide 2020) — if/when discovered
- [ ] Update NAJA `source_url` from `naja.com` to `indigenousjournalists.org` (rebrand happened 2023, old domain dead)
- [ ] Confirm canonical URLs in `scaffold-source-pages.py` `KNOWN_URLS` map — NABJ + Define American returned 404 on live-check

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

#### ✅ 2.5c — Source page enrichment (shipped 2026-05-17)

**Problem:** 15 of 16 source pages were stubs auto-generated from term frontmatter. Each needs mechanical metadata (year, page count, format, live status, dates) and qualitative content (About section, Access-posture rationale, version history, license findings). Doing this by hand or LLM was wrong-tool work.

**Built:** `scripts/enrich-source-pages.py` — walks every `site/src/content/sources/*.md`, parses its frontmatter line-by-line (no YAML library — stdlib only), and:
- For PDF `local_archive` → runs `pdfinfo`, fills `length_pages`, `format: "PDF"`. PDF Author/Creator metadata is reported as a note (often "Adobe InDesign CC 2017" — not actually the copyright holder) but never auto-applied.
- For markdown `local_archive` → distinguishes our own PDF-extracted markdown (has `extracted_from:` header → set format to PDF, pull pages from sibling PDF) from web-scraped markdown (no header → set format to `"markdown"` or `"web"`).
- For `source_url` → HEAD with fallback chain (HEAD → ranged GET → plain GET, so anti-bot 405/501 still gets a real answer). Status mapping: 401/403 → `login-gated`, 404/410 → `404`, other 4xx → `live` with "manual check recommended" note, 5xx/connection error → `offline`. Won't demote a human-set value without `--force`.
- Seeds `added` and `last_checked` to today if missing.
- Preserves body, comments, and untouched frontmatter fields.

Flags: `--check-only`, `--force`, `--no-net`.

**Outcome:** 48 field updates across 16 pages on first run. Astro build clean (44 pages). Findings: NAJA `source_url` (`naja.com`) returns connection-refused — NAJA rebranded to Indigenous Journalists Association in 2023 and the old domain went dead. URL needs update before NAJA goes live as a primary Indigenous-chapter source.

**Rule:** Re-run after each Phase 3 batch (to refresh `last_checked` on newly-cited stubs) and after editing any source page's `source_url` or `local_archive`.

#### 2.5d — Recommended order

1. **First**: 2.5a (PDF extractor) — fastest, unblocks 2.5b
2. **Second**: 2.5b (coverage matrix) — highest leverage on remaining Phase 3 work
3. **Third**: 2.5c (source page enricher) — can be in-progress in parallel with Phase 3 batches; not blocking

After 2.5a + 2.5b land, **Phase 3 term batches should drop from ~3 hours / 5 terms to ~60–90 min / 5 terms**, with the LLM time concentrated on synthesis, paraphrase, and audience notes — the work that actually requires cross-corpus judgment.

### Phase 2.6 — Programmatic-first term production (locked 2026-05-17)

**Locked direction:** Push as much of the per-term work as possible into
scripts, so Phase 3 batches become "review and tighten" rather than
"research and write from scratch." Each script reduces the per-term LLM-
time floor; the goal is ≤10 min/term of human/LLM judgment instead of the
~30-40 min/term Phase 3 batches were running at without tooling.

Built in priority order; reassess after each script lands before
committing to the next.

#### ✅ 1. Term scaffolder (shipped 2026-05-17)

`scripts/scaffold-term.py <slug>` — given a term, walks
`notes/term-coverage-matrix.csv`, looks up each hit source's metadata via
the source-page archive index (PDF→md mapping built from
`extracted_from:` headers), reads the source markdown for context around
the hit line, classifies the recommendation enum from context patterns,
strips known markdown noise (pandoc fenced divs, span IDs, bullet
glyphs), and emits a near-complete `site/src/content/terms/<slug>.md`.

Validation on `tribe` (8 source hits): 8/8 recommendations correctly
classified (APA/DSG → avoid; SumOfUs/NAJA/GCJT → use;
NGC/Sierra Club/RET → use-with-care). DSG quote came out as the
clean canonical "Avoid. Eurocentric term for ethnic conflict among
people of color" — ready to cite without editing.

Per-term LLM work after scaffold: tighten quotes against PDFs, fix any
mis-classified recommendations, write synthesis paragraph + audience
notes, cross-link related terms. Target: 8-12 min/term.

#### ✅ 1b. Source-page scaffolder (shipped 2026-05-17)

`scripts/scaffold-source-pages.py` — walks the matrix CSV for source
slugs not represented in `site/src/content/sources/`, parses
`source-guides/MANIFEST.md` tables to look up org/title/year/host
posture for each orphan, and writes a stub source page with proper
frontmatter + boilerplate About/Access body. Then `enrich-source-
pages.py` fills `length_pages` / `format` / `live_status` mechanically.

First-run outcome: 12 stub pages created (HRC, Color of Change × 3,
Define American, IDP × 2, Comm-Unity, InterACT, NABJ, WordsAboutWar
× 2, WFP USA). Site grew from 44 → 56 built pages, schema clean.

**Validation by re-scaffolding `illegal immigrant`:** went from 3/7
to 7/7 source coverage. DSG quote came out canonical-ready ("Avoid.
Alternative terms are undocumented worker or undocumented
immigrant... criminalizes the person rather than the actual act").
Define American + IDP × 2 + Color of Change all contributed real
"avoid the term" framing.

**Idempotent + future-proof:** if a new PDF gets dropped into
`source-guides/` and the pipeline re-runs (extract → matrix →
scaffold-source-pages → enrich → scaffold-term), the new source
flows through automatically.

**Known limit:** a few hardcoded canonical URLs in
`scaffold-source-pages.py`'s `KNOWN_URLS` map may be stale (NABJ
and Define American returned 404 on first live-check). Update the
map and re-run when canonical URLs are confirmed.

#### 2. Expanded glossary extractors (build only if scaffolder leaves obvious gaps)

NABJ (2,150 lines), SumOfUs (3,539 lines), and the 3 Color of Change PDFs
(1,180-2,605 lines each) are currently keyword-scanned only. If the
scaffolder's quote-extraction on these sources is weak — pulling random
line context instead of real term entries — add per-source structured
extractors. Each adds 100-300 terms to the universe and gives the
scaffolder better-bounded excerpts for those sources.

Decision point: review scaffold output for `tribe` after the scaffolder
ships. If the SumOfUs/NABJ excerpts look like garbage, build the
extractors. If they look fine, skip and move on.

#### 3. Source-page About generator (smaller win, defer)

For each stub source page, fetch the org's About page or Wikipedia entry
and generate a 2-3 paragraph About summary. Compresses source-page
write-up from ~30 min to ~5 min of LLM tightening. Worth doing in
batch before Phase 4 (launch gate requires non-stub source pages).

#### 4. GLAAD reference fetcher (defer to Gender & Sexuality chapter)

Fetch the ~6 GLAAD `/reference/X` URLs (transgender, bisexual, intersex,
nonbinary, etc.) into `source-guides/discovered/`. ~30 min programmatic.
Only matters for the Gender & Sexuality chapter — defer until that
chapter is next up.

### Phase 2.7 — Full-launch scope tooling (✅ complete 2026-05-18)

Three new pieces of tooling needed to support the expanded launch scope (≥3 sources, ~250 commons + Glossary Index for the long tail, 8-10 chapters). All three shipped end-of-day 2026-05-18.

#### ✅ 1. Glossary Index page + scaffolder (shipped 2026-05-18)

**Problem:** The matrix has 1,273 unique candidate terms. 268 will become commons pages (≥3 sources). The remaining ~1,000 single- and dual-source terms are real reference material from real source guides — readers looking up "ABCD" or "Two Spirit" or specific phrases shouldn't hit nothing. But they aren't commons material; there's no cross-reference work to do on a 1-source term.

**Solution:** A single Glossary Index page (or 26 per-letter pages at scale) listing every term found in any source guide. Each entry shows: term name + source-count indicator + one-line excerpt from the strongest source + link. The link target depends on coverage:
- ≥3 sources → full commons page (cross-source synthesis)
- 1-2 sources → source page(s) with the brief excerpt as the bridge

**Build approach:**
- `scripts/build-glossary-index.py` — walks `notes/term-coverage-matrix.csv` + Astro content collections, emits structured glossary-index entries (markdown or JSON for content collection)
- Astro page at `/glossary/` (or `/index/`) renders A-Z with filterable display
- Idempotent — re-run after each term batch to refresh

**Rule:** Re-run after each Phase 3 batch (refreshes the long tail with the new indexed-term links) and after new sources are dropped in.

**Outcome:** `scripts/build-glossary-index.py` ships, emitting `site/src/data/glossary-index.json`. Glossary page at `/glossary/` renders A-Z with filter chips ("Commons entries" / "All" / "Long tail only"), default-selected to Commons entries. Three cleanup passes during the session tightened the noise filter: definitional pattern detection for keyword-scan hits, Pandoc fence stripping, slug resolution (matrix long-form vs short-form). Final count: 939 entries (down from 1,271 noisy initial). A-Z browse merged into Glossary per Jordan's Option 1 call; `/terms` → `/glossary` redirect via Cloudflare Pages `_redirects`.

#### ✅ 2. SQLite build-time index (shipped 2026-05-18)

**Problem:** As the commons grows past 250 entries, faceted-query patterns (filter by recommendation × year × source × chapter) will be useful for future API layers, third-party tools, or community-built explorers. Markdown remains source of truth; SQLite is derived.

**Solution:** `scripts/build-sqlite-index.py` — reads term + source data at build time, emits `dist/elc-index.sqlite` (also written to `site/public/` so it's served from CF Pages).

Schema:
- `terms(slug, term, last_reviewed, stub)`
- `sources(org_slug, org, year, source_url, host_posture, live_status, last_checked)`
- `guidance(term_slug, org_slug, recommendation, year, quote_loc)`
- `chapters(slug, title, order)`
- `term_chapters(term_slug, chapter_slug)`

**Use cases (none required for launch):**
- Future API endpoints for third-party tools
- Community-built faceted browsers
- Bulk export for academic/research use

**Rule:** Build at deploy time, ship in `dist/` alongside the static HTML.

**Outcome:** `scripts/build-sqlite-index.py` ships (stdlib-only Python YAML parser, no PyYAML dependency). Emits `site/public/data/elc-index.sqlite`. Schema includes terms, sources, guidance, chapters, mappings tables with appropriate indexes. Build pipeline regenerates on every deploy.

#### ✅ 3. Contribute page + GitHub onboarding section (shipped 2026-05-18)

**Problem:** Phase 5 outreach plans community contributions, but no `/contribute` page exists. The launch site needs a clear "how to participate" surface that respects both technical and non-technical readers.

**Solution:** New page at `/contribute/`. Three contribution paths plus a non-technical onboarding section:

1. **Suggest a term, source, or correction** — GitHub Issues (templated)
2. **Discuss interpretation, framing, or methodology** — GitHub Discussions (Q&A + Ideas categories)
3. **Submit a direct change** — Pull Requests (for git-fluent contributors)
4. **Email Jordan** — fallback for everyone

The non-technical onboarding section walks readers through creating a free GitHub account, finding the project, and opening an issue. Links to an authoritative external "GitHub for beginners" guide rather than reinventing the wheel.

**Prerequisite:** Repo must be public before launch. Currently private. Phase 4 launch criterion: flip repo to public alongside DNS flip.

**GitHub configuration changes needed:**
- ✅ Enable Discussions in repo settings (done 2026-05-18)
- ⏸ Create Discussion categories: Ideas, Q&A, Show-and-Tell, Announcements (Jordan manual; tracked in Drift)
- ✅ Create issue templates: "Suggest a new term," "Suggest a new source," "Report an error," "General feedback" (done 2026-05-18)
- ✅ Add CODE_OF_CONDUCT.md and CONTRIBUTING.md to the repo root (done 2026-05-18)
- ⏸ Flip repo to public (Phase 4 launch criterion)

**Outcome:** `/contribute/` page live with four paths (Issues, Discussions, PRs, email). Non-technical onboarding section walks through creating a GitHub account, finding the project, opening an issue. Links to GitHub's official Hello World, About Issues, and Discussions Quickstart guides. Issue templates live as YAML forms in `.github/ISSUE_TEMPLATE/`. Three-layer license added at repo root (CC-BY 4.0 for cross-reference layer, MIT for code, fair-use attribution for source publisher quotes).

### Phase 3 — Bulk term indexing (iterative, one category at a time)

**Now scaffolder-driven.** With Phase 2.5 + 2.6 complete, each Phase 3 batch is:

1. Open `notes/term-coverage-matrix.md` → "Top 50 candidates" section
2. Pick 5 terms (filter by chapter focus, e.g., Indigenous-related terms for the next chapter)
3. For each: `./scripts/scaffold-term.py <slug>` (~30 sec total)
4. Review each scaffolded file — read the `<!-- scaffolder notes -->` block, tighten quotes against PDFs, fix any mis-classified recommendations, write synthesis paragraph + audience_notes, cross-link related_terms, fill categories + tags, remove `stub: true`
5. `cd site && npm run build` to verify schema
6. `./scripts/build-coverage-matrix.py` to regenerate the ranking (so the new terms are excluded from the next batch)
7. Commit batch

Target per term: 8–12 min of LLM/human judgment work.

Chunk by the taxonomy that emerges from the first ~10 terms. Aim ~20–40 terms per category. Each category is a focused session.

Likely categories (subject to what emerges):
- [~] **Race & Ethnicity** — **18 terms indexed** (african-american, asian-american, bipoc, black, brown, caucasian, chicanx, hispanic, indigenous, latine, latino, latinx, minority, multiracial, people-of-color, unhoused-homeless, urban, white). Chapter intro with 6 cross-cutting principles. Need ~8–15 more terms to round out for launch: mestizo, afro-latino, mena, native-hawaiian, south-asian, mixed-race, model-minority, anti-Black, white supremacy, white nationalism, white privilege, microaggression, gentrification, "thug", "articulate".
- [~] **Indigenous & Tribal Sovereignty** — **5 terms indexed** (native-american, american-indian, first-nations, reservation, tribe). Chapter intro with 6 cross-cutting principles. Matrix-strong candidates next: tribal (separate from tribe), two-spirit, sovereignty, treaty, indigenous (currently dual-categorized into R&E + this chapter).
- [~] **Sexuality & Gender Identity** — **10 terms indexed** (transgender, gay, queer, pronouns, homophobia, bisexual, lesbian, cisgender, intersex, sexual-orientation). Chapter intro with 7 cross-cutting principles. Matrix-strong candidates next: nonbinary, deadnaming, outing, transition, gender-identity, sexual-minority, pansexual, biphobia, transphobia.
- [~] **Disability & Mental Health** — **5 terms indexed** (disability, ableism, accessible, mental-health, survivor). Chapter intro with 6 cross-cutting principles. NCDJ dedicated source. Matrix-strong candidates next: injury (8), victim (12, pairs with survivor), addiction, recovery, neurodiversity. Note: `accessible` thinnest (3-4 srcs); APA was SUMMARY-ONLY, upgraded to VERIFIED-ARCHIVED 2026-05-26.
- [~] **Immigration & Citizenship** — **5 terms indexed** (immigrant, refugees, undocumented-immigrant, illegal-immigrant, alien). Chapter intro with 6 cross-cutting principles. Define American + Immigrant Defense Project dedicated sources. Matrix-strong candidates next: noncitizen (3), asylum-seeker (TJA-dedicated), migrant, anchor-baby, naturalized. DACA/Dreamer high-impact but thin — may need a discovered source.
- [ ] Age
- [ ] Class & Economic Status
- [ ] Labor & Workers
- [ ] Housing — 1 term (unhoused-homeless); needs ~15 more
- [ ] Incarceration & Policing
- [ ] Sexual & Domestic Violence
- [ ] Health
- [ ] Food (sovereignty, deserts, labor intersection)
- [ ] Environment / Climate
- [ ] Religion & Culture
- [ ] Reproductive Rights

### Phase 4 — Quiet build → public launch

**No "soft launch." No private reviewer round.** Build until the site is launch-ready, then flip it public in one motion. Friends-and-family preview rounds make launches feel like failure-by-default — the work is either published or it isn't.

**Launch scope (revised 2026-05-18):**
- **~250 commons-style term pages** covering every term with ≥3 source citations across the in-scope corpus. After light noise filtering, expect 230-250 substantive commons entries.
- **8-10 chapters**, each with lede + cross-cutting principles + chronology + term list (matching the R&E and Indigenous patterns).
- **Glossary Index** — alphabetical page covering all ~1,300 candidate terms, with links to commons pages (≥3 sources) or source pages (1-2 sources). The "everything else" surface.

Launch readiness criteria:
- [x] Domain secured — `equitylanguagecommons.org` (2026-05-14)
- [ ] ~250 commons term pages published across 8-10 chapters
- [ ] All chapters with lede + cross-cutting principles + chronology + term list
- [ ] Glossary Index page populated and linked from primary nav
- [ ] All source pages filled out (not stubs); access-posture panels accurate; About sections written
- [ ] Final legal pass: per-source attribution, CC-BY notice on curation layer, fair-use posture clear on every quoted passage
- [ ] Pagefind search wired and indexing the live content
- [ ] SQLite index built and shipped in `dist/` for future API / faceted-query consumers
- [ ] **Contribute page live** — three contribution paths (Issues, Discussions, PRs) plus GitHub-for-beginners onboarding section, plus email fallback
- [ ] **Repo flipped to public** before DNS flip — Discussions enabled, issue templates configured, CONTRIBUTING.md + CODE_OF_CONDUCT.md in repo root
- [ ] Deployed to Cloudflare Pages on `equitylanguagecommons.org` — DNS flip is the launch
- [ ] Homepage doesn't read like a stub — about page, contributing posture, and source list are all complete

During build, deploy to the `equity-language-commons.pages.dev` URL but don't publicize it. That URL is for build-validation, not feedback collection.

**Chapter targets** (rough — exact counts refine as Phase 3 progresses):
- Race & Ethnicity — ~25 terms
- Indigenous Identity & Sovereignty — ~10 terms
- Sexuality & Gender Identity — ~25 terms
- Disability & Accessibility — ~25 terms
- Immigration — ~20 terms
- Class & Economic Status — ~15 terms
- Trauma, Violence & Survivors — ~15 terms
- Religion — ~15 terms
- War & Conflict — ~10 terms
- Housing, Age, Body & Appearance — smaller chapters, ~15 combined

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

- **User submissions at v1 or v2** — Google Form → GitHub issue is the lightest-weight workflow; decide before Phase 4 launch
- **Downloadable "everything" PDF** — useful offline but more copyright-sensitive than per-term pages; later decision
- **Relationship with Conscious Style Guide / Diversity Style Guide** — sibling resources; decide outreach framing (complementary, not competitive) — defer to Phase 5 outreach
- **Controlled vs. free-form taxonomy** — currently free-form (`categories: []` strings). Now that R&E has 16 indexed terms, may be time to lock the chapter taxonomy. Indigenous chapter's first batch will pressure-test whether the current categories cover that domain or need additions.
- **Whether `related_terms.relation` enum is exhaustive** — add values as new relationship types appear
- **Whether `context_data` becomes its own content type** (cited from many terms) instead of embedded per-term — decide after 2–3 more terms are populated
- **Whether to build Phase 2.6 #3 (source-page About generator) before Phase 4** — would batch-process all 27 About sections instead of writing each by hand. Decide once 3–5 terms are finalized through the new scaffolder flow and we see how often the source pages need touching.
- **Stub-flag handling in build** — `tribe.md` and `transgender.md` were deleted as test scaffolds. Real Phase 3 batches will produce term files with `stub: true` until finalized. Decide whether matrix should count stubs as indexed (currently does) and whether `/terms/index` should hide stubs (currently shows everything).

## Guardrails

- Never host an active org's PDF publicly without explicit permission
- Every direct quote under 50 words (fair-use safety margin) unless permissioned
- Every quote cites: org, year, source URL or canonical reference
- `research/research-notes.md` is the audit trail — every claim must be traceable
- Do not reach out to source orgs or Hanna Thomas until **Phase 4 is complete and the public site is live** — outreach is post-launch, not pre-launch (see Phase 5)
