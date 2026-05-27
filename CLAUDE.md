# Equity Language Commons — Project Instructions

## What this is

Cross-referenced omnibus of progressive equity/inclusive language guidance.
Per term, shows every source org's rule side-by-side (fair-use quote +
paraphrase + year + source link + Jordan's synthesis). Reference for
progressive communicators, campaigners, and allied nonprofits.

**Name:** Equity Language Commons (ELC). Renamed from working title
"Progressive Language Commons" on 2026-05-14 once the focus on equity
language specifically (not all progressive language) settled. Still
distinct from "A Progressive's Style Guide" — that's SumOfUs/Hanna
Thomas's 2016 title; outreach planned.

**Realm:** Side hustle. Not CampaignHelp-branded. Gift-to-the-community
posture. Precedent: `side-hustle/progressives-for-ai/`.

**License:** CC-BY 4.0 for Jordan's cross-reference layer. Source guides
handled in tiers — see `ROADMAP.md` and `source-guides/MANIFEST.md`.

## Phase

Phases 0, 1, 2, 2.5, 2.6, and 2.7 **complete** (2026-05-18). Schema v0.3
locked. Astro site live at the preview URL. Full programmatic pipeline
shipped — extract → matrix → source-page scaffold → enrich → term scaffold,
plus glossary index + SQLite build-time index + Contribute page.

**Phase 3 (bulk term indexing) is underway** across **6 chapters**:
- **Race & Ethnicity** — 18 indexed terms, chapter intro shipped with 6 cross-cutting principles
- **Indigenous & Tribal Sovereignty** — 5 indexed terms (native-american, american-indian, first-nations, reservation, tribe), chapter intro with 6 cross-cutting principles
- **Sexuality & Gender Identity** — 10 indexed terms (transgender, gay, queer, pronouns, homophobia, bisexual, lesbian, cisgender, intersex, sexual-orientation), chapter intro with 7 cross-cutting principles
- **Disability & Mental Health** — 14 indexed terms (disability, ableism, accessible, mental-health, survivor, victim, handicapped, mental-illness, addiction, deaf, + rejected labels addict, crazy, insane, retarded), chapter intro with 6 cross-cutting principles; anchored by NCDJ's Disability Language Style Guide. Added 2026-05-26, rounded out 2026-05-27, rejected-labels batch added 2026-05-27. Note: `accessible` + `addiction` are the thinnest pages (3-4 sources each); `victim` is intentionally split-recommendation (avoid in illness/disability framing, contested in violence/trauma framing); `deaf` is the chapter's first specific-condition identity-first page (capital-D Deaf). The 4 rejected labels are all unanimous `avoid` (addict covers junkie; crazy covers loony/psycho/nuts/deranged; insane carries a legal-term carve-out; retarded is the slur, cites Rosa's Law).
- **Immigration & Citizenship** — 6 indexed terms (immigrant, refugees, undocumented-immigrant, illegal-immigrant, illegal-alien, alien), chapter intro with 6 cross-cutting principles; anchored by Define American + Immigrant Defense Project (2020 + 2021 Comm/Unity). Added 2026-05-27. Splits cleanly prescribe (undocumented = unanimous `use`) vs. reject (illegal-immigrant `avoid` ×7, illegal-alien `avoid` ×4, alien `avoid` ×6). One PARTIAL: Color of Change on illegal-immigrant (OCR collapsed the use/avoid table columns).
- **Class & Economic Status** — 3 indexed terms (classism, ghetto, disadvantaged), chapter intro with 5 cross-cutting principles; anchored by APA's Socioeconomic Status section + Sierra Club's Classism and Wealth section. Added 2026-05-27. `classism` is the structural concept (`use`, parallel to ableism); `ghetto` is unanimous `avoid` and also covers its companion "inner city" (folded in as an alias — see note below); `disadvantaged` is the deficit/charity-descriptor cluster page (covers underprivileged, at-risk, the poor, the needy — `avoid` ×3 + APA `use-with-care`). Corpus is genuinely thin on class — few guides have dedicated "poverty"/"poor" headwords, so the chapter clusters around these structural/euphemistic terms.

**56 indexed terms total.** Build clean, 98 static pages.

**Launch scope expanded 2026-05-18.** Original "~50 terms / 3-4 chapters" target was a minimum-viable-launch threshold. After looking at actual matrix data (268 terms have ≥3 sources), Jordan locked the full-launch threshold at **≥3 sources, ~250 commons-style term pages across 8-10 chapters, plus a Glossary Index for the ~1,000-term long tail.** No soft launch — full public launch when ready, per `feedback_no_soft_launches`.

**Standing reference — `notes/cleanup-pass-prompt.md`** captures the subagent cleanup-pass workflow + every editorial rule + error pattern caught during Phase 3. Read it before dispatching a cleanup subagent. Update when new error patterns appear.

## Pick-up notes for next ELC session

**Done 2026-05-27 (latest) — rejected-labels batch + Class & Economic Status chapter started:** Two batches in one session. (1) **Disability rejected labels 10 → 14:** added `addict`, `crazy`, `insane`, `retarded` — all unanimous `avoid`. addict is the noun/label (distinct from the existing `addiction` condition page; covers "junkie"); crazy groups loony/mad/psycho/nuts/deranged; insane carries the legal/criminal-defense carve-out; retarded is the slur (cites Rosa's Law 2010). Cleanup subagent removed 2 incidental hits (Color of Change from crazy, Define American from insane), fixed many scaffolder `use-with-care`→`avoid` mis-tags and 4 wrong DSG quotes. (2) **Class & Economic Status chapter launched (order 6) with 3 terms:** `classism` (structural concept, `use` — APA/SumOfUs/Sierra/RET), `ghetto` (avoid ×6, race/class-coded place term), `disadvantaged` (deficit/charity descriptors — Sierra's do-not-use list + APA's "the poor"→low-income table + CoC charity-framing + SumOfUs). **`inner-city` attempted and folded into `ghetto`** — only 2 distinct orgs (DSG ×2 + NABJ), below the ≥3-org bar, and the sources literally pair "ghetto, inner city"; added as a ghetto alias, and `urban` already aliases it from the race-code angle. **`the poor` NOT shipped as a standalone** — only 2 strong orgs (APA + Sierra); folded into the `disadvantaged` cluster page per Sierra's own grouping. Class corpus is genuinely thin (no dedicated "poverty"/"poor" headwords in the guides). Cleared Astro cache, clean-rebuilt (98 pages, zero warnings), deployed, verified all 7 new pages + both chapters live. Matrix regenerated.

**Done 2026-05-27:** Immigration & Citizenship chapter shipped (6 terms, Define American + IDP-anchored) and deployed to preview. Batch 1: immigrant, refugees, undocumented-immigrant, illegal-immigrant, alien. Round-out: illegal-alien (4 srcs, unanimous avoid). Note: bare `undocumented` is not a matrix term — the matrix-strong form is `undocumented immigrant` (slug `undocumented-immigrant`). Cleanup subagent removed 9 incidental hits from `immigrant` (kept 4 of 13) and 4 from `refugees` (kept 4 of 8); fixed Sierra Club inversion on undocumented (avoid→use) and 5 use-with-care→avoid mis-tags on illegal-immigrant. **`noncitizen` attempted and dropped** — only DSG is a real entry (IDP + comm-unity "hits" were both the same incidental BAJI statistic); below the ≥3 threshold, so it stays in the Glossary Index long tail. Its guidance (USCIS 2021 shift) is already captured in the `alien` + `undocumented-immigrant` syntheses. Removed redundant "Illegal alien" alias from the `alien` page. DSG generic-URL scaffolder default verified NOT widespread (only `indigenous.md`, where it's correct). Matrix regenerated.

**Also done 2026-05-27 — Disability & Mental Health rounded out 5 → 10 terms:** added victim, handicapped, mental-illness, addiction, deaf. `victim` is the nuanced one — kept 6 of 13 (pruned 7 incidental hits), added the NCDJ anchor entry by hand, and it carries a SPLIT recommendation by context (avoid for "victim of [a condition]" in illness/disability framing; contested/use-with-care for the victim-vs-survivor debate in violence/trauma coverage). `handicapped` unanimous avoid (6). `deaf` all use/use-with-care — the "avoid" scaffold hits were compounds/metaphors ("the deaf," "fell on deaf ears"), correctly not allowed to flip the page; central teaching is capital-D Deaf vs lowercase-d. `addiction` at the ≥3 floor (3 srcs — the rejected noun "addict" carries the rest and wants its own page). `mental-illness` kept distinct from `mental-health`. Two new sources joined this chapter: SEIU (2020) + WFP USA (2022).

**⚠️ Astro content-layer cache gotcha (new, 2026-05-27):** when the cleanup subagent runs `npm run build` and THEN the main agent edits the same term files, the next build throws `[glob-loader] Duplicate id "<slug>" found … Later items overwrite earlier` warnings for every edited file. It's a stale cache, not a real duplicate — "later overwrites earlier" means the current file content wins, so output is correct. To clear it before the final deploy: `rm -rf site/.astro site/node_modules/.astro && npm run build` (rebuilds warning-free). Verified the live pages render current content either way.

**Done 2026-05-26:** Sierra Club URL fixed — old `sierraclub.org/equity-language-guide` is dead (404); the live 2021 PDF (30pp, verified correct edition vs. the 2018 one) is at the `sce-authors/u12332` files path. Updated the source page + all 25 term pages citing it; logged the 2018 predecessor in version_history; corrected length_pages 40→30. Disability & Mental Health chapter shipped (5 terms, NCDJ-anchored) and deployed to preview.

In priority order:

1. **Immigration & Citizenship is largely tapped for the current corpus** (6 terms). What's left needs care, not just another scaffold batch:
   - **DACA / Dreamer cluster** — `daca` (3) + `dream act` (3) have coverage, but it's borderline scope (policy vs. equity language — the in-scope angle is the people-terms "Dreamer" / "DACA recipient", not explaining the program) AND the Define American extraction is column-scrambled (definitions mismatched to headers around L405–455). Build as ONE consolidated "Dreamer / DACA recipient" page with careful PDF verification; expect some PARTIAL.
   - **Below the ≥3 bar → Glossary Index long tail, not full pages:** `anchor baby` (2), `asylum seeker` (1, TJA-only), `undocumented worker` (2). `migrant` is not a standalone matrix term (appears only inside other entries / on avoid lists).
   - **To go deeper needs a new discovered source** — a migration/asylum-dedicated guide (e.g., a UNHCR/refugee-press or Define American companion) would unlock asylum-seeker, migrant, anchor-baby as full pages.
   - **Carryover:** Color of Change illegal-immigrant entry is PARTIAL (verify the use/avoid table against the PDF to bump to VERIFIED-ARCHIVED).

2. **Disability & Mental Health is at 14 terms** (rejected-labels batch done 2026-05-27). Further candidates if going for completeness: more specific-condition identities (`autism`/`autistic` 6, `blind` 2, `wheelchair` 5, `intellectual disability`), `lame`/`invalid`/`cripple` (more rejected labels — note `cripple` 3 has a documented reclamation angle, "crip", so it's `use-with-care`/`reclaimed-in-community`, not a clean avoid), plus `injury` (9, the "suffers/sustained" framing), `recovery`, `neurodiversity` (4), `suicide` (5, NCDJ has strong reporting guidance). `accessible` + `addiction` remain the thinnest pages (3-4 srcs).

2b. **Class & Economic Status is at 3 terms (just started).** Round-out candidates, but the corpus is thin: `welfare queen/king` (Sierra do-not-use list + others), `blue-collar`/`white-collar` (APA avoid table — "outdated", → skilled tradesworker / salaried professional), `class privilege` (APA has a definition), `socioeconomic status`/`SES` (APA), `culture of poverty` (SumOfUs avoid). Most are 1-2 orgs — likely a single "welfare queen / welfare" page + folding the rest into existing syntheses rather than many thin pages. Labor & Workers and Housing are adjacent unstarted chapters (`homeless`/`unhoused` already live in Housing via `unhoused-homeless`).

3. **Round out LGBTQ+ further.** `nonbinary` (4 srcs), `deadnaming` (likely 2-3), `outing` (2), `transition` (5), `sexual minority`, `pansexual`. Not strictly needed for launch — chapter at 10 is already strong — but nonbinary, deadnaming, and outing are the most-conspicuous gaps.

4. **Round out Indigenous chapter further.** Matrix-strong candidates not yet indexed: `tribal` (separate from `tribe`), `two-spirit`, `sovereignty`, `treaty`.

5. **Manual setup items Jordan owes (tracked in Drift):** Cloudflare Email Routing for hello@equitylanguagecommons.org; GitHub Discussion categories; GitHub auto-deploy in CF dashboard. None block Phase 3 term work.

6. **At launch (Phase 4):** flip repo to public, DNS flip equitylanguagecommons.org, verify all source pages have About sections written, run final legal pass.

## Scope (locked 2026-04-23)

**Equity language only** — cross-org guidance on *what to call people, how
to frame issues*. Not brand identity (logos/fonts) or general editorial
(grammar/AP style) unless it intersects with equity language.

**In-scope from the archive:**
- Sierra Club Equity Language Guide (2021) — core
- Native Governance Center Style Guide (Feb 2021) — core
- Annie E. Casey Foundation Editorial Guide (Apr 2013) — partial (race/ethnicity sections only)
- SEIU Stylebook (Jan 2020) — partial (labor/workers terminology, identity standards only)

**Out of scope from the archive:**
- yli 2020 Style Guide — brand identity only
- Stand.earth Identity, Voice & Vision (June 2019) — brand voice / messaging

## Goals

1. **Process** in-scope guides — extract guidance into a consistent
   structure (topic → term → recommendation → rationale → source org).
2. **Discover updates** — check whether each source org has issued a newer
   version since Jordan's archived copy.
3. **Discover new guides** — find equity language guides from other
   progressive orgs that aren't in the archive yet.
4. **Eventually** — assemble an omnibus site (searchable, attributed,
   linkable by term).

## Folder structure

- `source-guides/` — 6 originally-archived PDFs + their extracted `.md` siblings
- `source-guides/discovered/` — guides pulled during research phase (PDFs + scraped/extracted markdown)
- `source-guides/MANIFEST.md` — canonical catalog: file, org, title, year, scope, host posture per guide. **Update first when adding a new source** — `scaffold-source-pages.py` reads this to derive metadata.
- `research/research-notes.md` — full research audit trail (follow `.claude/rules/client-research.md` — VERIFIED sources)
- `notes/` — schema, test terms, working notes, **coverage matrix outputs** (`term-coverage-matrix.csv` + `.md`)
- `site/` — Astro project. Content collections in `site/src/content/` for `terms/`, `sources/`, `chapters/`
- `scripts/` — full pipeline (extract-pdfs.sh, build-coverage-matrix.py, scaffold-source-pages.py, enrich-source-pages.py, scaffold-term.py, deploy.sh)
- `ROADMAP.md` — phased plan
- `preview/` — early HTML/CSS design previews (pre-Astro)

## Deploy

- **Production URL (preview-tier, not announced):** https://equity-language-commons.pages.dev/
- **Deploy command:** `./scripts/deploy.sh` — runs `npm run build` in `site/` and pushes `dist/` to CF Pages via Wrangler using `PERSONAL_CLOUDFLARE_API_TOKEN`.
- **GitHub repo:** https://github.com/jordankrueger/equity-language-commons (private)
- **Wrangler CF Pages project:** `equity-language-commons` on Jordan's personal CF account, currently direct-upload.
- **TODO (Jordan, one-time):** wire GitHub auto-deploy via the CF dashboard so pushes to `main` deploy automatically. Path: CF Dashboard → Workers & Pages → equity-language-commons → Settings → Build & deployments → Connect to Git. Until that's done, run `./scripts/deploy.sh` after each meaningful change.
- **Custom domain (equitylanguagecommons.org) is NOT pointed at the project yet.** DNS flip = public launch per ROADMAP Phase 4.

## Tooling — Phase 2.5

Phase 3 term-indexing was LLM-heavy in places where it shouldn't be. Three scripts to remove that tax (see ROADMAP Phase 2.5 for detail):

1. **✅ `scripts/extract-pdfs.sh`** (shipped 2026-05-17) — `pdftotext` over every PDF in `source-guides/` + `source-guides/discovered/`, writes sibling `.md` with slug matching the org_slug-YYYY-MM convention. 17 PDFs converted. Flags: `--dry-run`, `--force`, `--layout`, `--ocr`. Warns when output density < 200 bytes/page (image-only PDF).
   - **⚠️ Never run `extract-pdfs.sh --force` globally.** It re-extracts *every* PDF, and for the image-only NAJA PDF it re-runs plain `pdftotext` (no OCR) and **clobbers the committed tesseract OCR** down to ~7 lines (incident 2026-05-26, caught + reverted). When adding one new source, extract only that file or pass `--ocr`; never `--force` the whole tree.
   - **Known gap:** NAJA Indigenous Terminology Guide (`naja-indigenous-terminology-2023-06.pdf`) is image-only — plain pdftotext yields 201 bytes; the committed `.md` is the tesseract OCR done 2026-05-17 (118 lines). NGC PDF has smart-quote rendering issues; text grep-able but quotes need PDF verification before publication.

2. **✅ `scripts/build-coverage-matrix.py`** (shipped 2026-05-17) — two-pass extractor: structured glossary extractors for TJA / DSG / NCDJ / HRC / NLGJA / Radical Copyeditor build the candidate term universe (~1,490 terms), then keyword scan over the 20 narrative sources (Sierra Club, NGC, Casey, SEIU, SumOfUs, NABJ, NAJA, Color of Change, etc.) records first-hit-per-source. Outputs `notes/term-coverage-matrix.csv` (~2,670 rows) and ranked `notes/term-coverage-matrix.md`. **Use the top-50-candidates section of the MD to pick the next batch.**
   - **Filters baked in:** stopwords + inverted-glossary fragments dropped from the universe; common single-word noise (`family`, `american`, `mass`, ...) blocklisted from keyword scan but kept if they have a real glossary entry; hyphens collapse to spaces in the universe and search.
   - **Known limit:** compound indexed slugs like `unhoused-homeless` show coverage 0 because they're comparison pages, not single phrases. Check the component terms (`unhoused`, `homeless`) separately.
   - **Re-run trigger:** after each Phase 3 batch (refreshes "what's left to do") and after dropping new sources into `source-guides/`.

3. **✅ `scripts/enrich-source-pages.py`** (shipped 2026-05-17) — walks every source page in `site/src/content/sources/`, fills `length_pages` from `pdfinfo`, sets `format` based on archive type (PDF vs PDF-extracted markdown vs web-scraped markdown), checks `source_url` via HEAD→GET fallback chain, updates `last_checked`/`added` to today. Frontmatter parsed line-by-line so bodies and untouched fields are preserved exactly. Flags: `--check-only`, `--force`, `--no-net`. Won't demote a human-set live_status without `--force`.
   - **Known finding:** NAJA's `source_url` (`naja.com`) is dead — NAJA rebranded to Indigenous Journalists Association in 2023. Needs URL update before NAJA can go live as a primary Indigenous-chapter source.
   - **Re-run trigger:** after each Phase 3 batch (refreshes `last_checked` on newly-cited stubs) and after any source page URL/archive edits.

**Phase 2.5 fully shipped.** With 2.5a + 2.5b + 2.5c in place, term batches should drop from ~3 hrs / 5 terms to ~60–90 min / 5 terms — LLM time concentrated on synthesis and audience notes. Indigenous & Tribal Sovereignty is the natural next chapter; matrix shows `tribe`, `native american`, `tribal` all well-covered.

## Tooling — Phase 2.6 (programmatic-first term production)

The Phase 3 floor — even with the matrix — is still ~30-40 min/term of LLM grinding through sources. Phase 2.6 pushes that floor toward 8-12 min/term by scaffolding the term file mechanically. See ROADMAP.md Phase 2.6 for the locked plan.

Build order: scaffolder first → evaluate → only then build more extractors / generators. Don't re-litigate.

### ✅ `scripts/scaffold-term.py <slug>` (shipped 2026-05-17)

Generates a near-complete `site/src/content/terms/<slug>.md` from the coverage matrix. For each source that mentions the term: reads ±10 lines of context, classifies recommendation (avoid / use / use-with-care / etc.) from context patterns, looks up org/year/url from the matching source page, strips markdown noise from the quote, emits a `guidance[]` entry with `confidence: PARTIAL`. Per-term LLM work after scaffold: tighten quotes, fix mis-classifications, write synthesis + audience_notes.

**Standard Phase 3 batch flow:**
1. Look at top of `notes/term-coverage-matrix.md` "Top 50 candidates" — pick 5 terms
2. `./scripts/scaffold-term.py <slug>` for each (~30 sec total)
3. For each scaffolded file: review notes block, verify quotes against source PDFs, fix any wrong recommendations, write synthesis + audience_notes, cross-link related_terms, remove `stub: true`
4. `cd site && npm run build` to verify schema
5. Commit batch, regenerate `notes/term-coverage-matrix.md` (rerun `build-coverage-matrix.py`) so subsequent batches see updated indexed-terms set

### ✅ `scripts/scaffold-source-pages.py` (shipped 2026-05-17)

Walks the coverage matrix for source slugs not represented in `site/src/content/sources/`, parses `source-guides/MANIFEST.md` to look up org/title/year/host posture, writes stub source pages. Run before `enrich-source-pages.py` to bring new sources fully online. Idempotent — only creates missing pages, never touches existing. Stays clean for future source additions.

**Standard pipeline when adding new source guides:**
1. Drop new PDF/markdown into `source-guides/` or `source-guides/discovered/`
2. Add an entry row to `source-guides/MANIFEST.md` (file, org, title, year, scope, host)
3. `./scripts/extract-pdfs.sh` (if PDF)
4. `./scripts/build-coverage-matrix.py` (rebuilds matrix with new source)
5. `./scripts/scaffold-source-pages.py` (creates stub source pages for any orphans)
6. `./scripts/enrich-source-pages.py` (fills mechanical fields on new stubs)

## Locked decisions (2026-04-23)

- **Shape:** Option C — cross-referenced omnibus with sourced excerpts
- **Name:** Equity Language Commons (domain: equitylanguagecommons.org; repo: equity-language-commons)
- **Branding:** side-hustle only, not CH
- **Stack:** Astro + Pagefind + Cloudflare Pages + R2 (for orphan PDFs)
- **GitHub account:** `jordankrueger/`
- **Host posture (per source):** see MANIFEST.md — Link / Archive / Reference tiers

## Still open

- Whether to accept user submissions at v1 or v2 (lightweight: Google Form → GitHub issue)
- Relationship with Conscious Style Guide + Diversity Style Guide (sibling or competitor framing — defer to Phase 5 outreach)
- Downloadable "everything" PDF — later decision (more copyright-sensitive than the per-term pages)
- Whether to build Phase 2.6 #3 (source-page About generator) before Phase 4, or write Abouts manually as part of Phase 3 batches

## Guardrails

- Never host an active org's PDF publicly without explicit permission
- Every direct quote under 50 words (fair-use margin) unless permissioned
- Every quote cites org, year, and canonical source URL
- `research-notes.md` is the audit trail — every claim must be traceable
- Don't reach out to source orgs or Hanna Thomas until Phase 1 schema work is done and we have something concrete to show

## Editorial voice

**No blame-leaning language.** Every style-guide author was doing the best they could with what was available at the time. Describe what each guide does, name dates and context, and let chronology speak for itself. Never frame an older guide's treatment as "outdated," "hasn't aged well," "behind," or any phrasing that reads as judgment of the author. Neutral chronological framing only: "pre-dates X," "earlier than," "written before Y settled into practice."

Editorial synthesis is welcome — positions, trends, practical guidance. Editorial judgment of individual authors is not.

## Display direction (locked 2026-04-24)

Two reading modes need to coexist:
1. **Chapters** — readers can browse a whole category (e.g., "Race & Ethnicity") top-to-bottom like a reference book.
2. **Term index + search** — readers can jump to a specific term directly (search bar; A–Z index page).

Every term page's display should make three things immediately visible:
- **Who** said what (org names)
- **When** they said it (publication year + entry update date if distinct)
- **Where each source landed** (use / avoid / use-with-care / non-preferred / etc. as a visible badge, not buried in prose)

Attribution clarity is the primary design constraint — a reader should never have to hunt for which org a given quote comes from or when that position was set.

### Chapter page components (always present)

- **Sticky sidebar TOC** on every chapter page, regardless of chapter length. Short chapters get a short TOC; the component is always there. Consistency > code-branching.
- **"Cross-cutting principles" intro block** at the top of every chapter, before individual term entries. Captures the 2–4 principles that thread through every term in the chapter, so readers have orientation before scrolling.
- **Chapter lede paragraph** before anything else — a single orienting sentence or two that says what this chapter covers and what the cross-chapter relationships are (e.g., "Indigenous & Tribal Sovereignty is a separate chapter because…").

### Source page components (always present)

- **Access-posture panel** immediately below the title, communicating hosting posture (public mirror / private mirror + link-out / link-out only) + the original source's status (live, offline, login-gated).
- **Publication details** as a key/value grid (work, year, format, length, copyright, original URL, commons access, added).
- **Version history** section — scaffolded even when only one version exists.
- **Terms citing this source** — every commons term that draws on this source, with position badges.

### Placeholder content during build-out

Terms, chapters, and sources that don't yet have content are OK to show during development as visually-dimmed "planned" stubs. This signals scope and invites contributors. Pre-launch (Phase 4), we'll decide whether to hide stubs or keep the "roadmap-visible" posture — not a constraint during Phase 1–3.
