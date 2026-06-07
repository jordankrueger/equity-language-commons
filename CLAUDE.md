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

**Phase 3 (bulk term indexing) is underway** across **9 chapters**:
- **Race & Ethnicity** — 29 indexed terms (added 2026-06-05: colored, diversity, ethnicity, intersectionality). Chapter lede + cross-cutting principles updated to cover structural vocabulary alongside identity labels. Note: `arab` went here, not Faith — Sierra separates Muslim (religion) from Arab (ethnicity).
- **Indigenous & Tribal Sovereignty** — 8 indexed terms (added 2026-06-04: indian, indian-country, two-spirit), chapter intro with 6 cross-cutting principles. Note: two-spirit's 3rd source is NLGJA's dedicated two-spirit entry, which the matrix scan missed; two-spirit is dual-category (also LGBTQ+). `tribal`/`sovereignty`/`treaty` are NOT standalone matrix terms in the current corpus (only compounds) — the earlier pick-up note claiming they were matrix-strong was stale.
- **Sexuality & Gender Identity** — 28 indexed terms (added 2026-06-05: agender, ally, biological-sex, deadname, female-to-male, gender-affirming-care, gender-nonconforming, grooming, transvestite), chapter intro with 7 cross-cutting principles
- **Disability & Mental Health** — 27 indexed terms (added 2026-06-05: alcoholic, lame, little-person, psychiatric-hospital, schizophrenic, special-needs, suicide, wheelchair), chapter intro with 6 cross-cutting principles; anchored by NCDJ's Disability Language Style Guide. Note: `accessible` + `addiction` are the thinnest pages (3-4 sources each); `victim` is intentionally split-recommendation (avoid in illness/disability framing, contested in violence/trauma framing); `deaf` is the chapter's first specific-condition identity-first page (capital-D Deaf). The 4 rejected labels are all unanimous `avoid`.
- **Immigration & Citizenship** — 7 indexed terms (added 2026-06-04: dreamer — the consolidated Dreamer / DACA Recipient page; slug `dreamer`, aliases cover DACA/DREAM Act), chapter intro with 6 cross-cutting principles; anchored by Define American + Immigrant Defense Project. One PARTIAL: Color of Change on illegal-immigrant (OCR collapsed the use/avoid table columns).
- **Class & Economic Status** — 4 indexed terms (classism, ghetto, disadvantaged, working-class), chapter intro with 5 cross-cutting principles. Corpus is genuinely thin on class — few guides have dedicated "poverty"/"poor" headwords.
- **Age & Generations** — 3 indexed terms (ageism, elderly, aging), order 7. Added 2026-06-03.
- **Criminal Justice & Incarceration** — 4 indexed terms (convict, felon, inmate, offender), order 8. Added 2026-06-03.
- **Faith & Religious Identity** — 3 indexed terms (antisemitism, islamophobia, muslim), order 9. Added 2026-06-03.

**115 indexed terms total** (2026-06-05 coverage-completeness arc: +21). 2 intentional `verified-hold` stubs: `jew.md`, `islam.md` — real content, below the ≥3-source bar; need a Jewish-press or interfaith style guide as 3rd source to graduate to full pages.

**COMPLETENESS IS NOW A LINT PROPERTY (2026-06-05).** Lint W6: every glossary term with ≥3 sources must have a page, resolve to a page via alias, or carry a documented decision in `notes/coverage-decisions.yml` (fold/drop + reason). `lint-content.py --strict` is fully green — "do any long-tail terms NEED stronger treatment?" is now a build-time answer. When new sources are added, re-run the matrix + glossary index and W6 surfaces any new ≥3 terms automatically.

**Done 2026-06-05 (third arc) — coverage completeness: 21 new pages + display fixes:**
- **Workflow-produced** (26 units through triage → write → adversarial-verify pipeline; 68 agents): D&MH +8 (alcoholic, lame, little-person [absorbs dwarf/midget], psychiatric-hospital, schizophrenic, special-needs, suicide, wheelchair [absorbs confined-to-a-wheelchair]); S&GI +9 (agender, ally, biological-sex, deadname, female-to-male [absorbs male-to-female], gender-affirming-care, gender-nonconforming, grooming, transvestite); R&E +4 (colored, diversity, ethnicity, intersectionality). 5 documented drops in `notes/coverage-decisions.yml` (america, american-sign-language, families, mexican, parent — all sub-3-strong after incidental pruning).
- **Adversarial verify stage caught real errors:** a fabricated NLGJA "988" claim on suicide, non-verbatim APA table reconstructions, a wrong DSG quote_loc (schizo/schizoid vs schizophrenia entry), a schema violation. Workflow gotcha: agents skipped `npm build` (parallel cache trap), so the audience_notes string-vs-object schema error surfaced only at the final build — 19 pages converted mechanically. **Check audience_notes object form in future agent-written pages.**
- **Display/structural fixes:** glossary index now resolves page ALIASES → 35 more glossary rows link to pages (daca→dreamer etc.); `related_terms` falls back page → alias → glossary anchor (never a dead link; glossary rows have anchor ids); APA two-column-table quote convention is "TERM TO AVOID … SUGGESTED ALTERNATIVE … cell … cell" (verbatim all-caps headers, ellipsis-joined — bracketed editorial labels fail Layer 1); 2 SumOfUs column-scramble override rows added (hand-verified vs `pdftotext -layout`).
- Final state: lint --strict 0/0, Layer 1 961 checks 0 findings, 166 pages, deployed + live-verified. Commit 975a249.
- **Merge gotcha:** main repo's working tree accumulates generated-artifact drift (`site/src/data/glossary-index.json`, `site/public/data/elc-index.sqlite`) from deploy builds — `git checkout --` them before ff-merging a worktree branch.

**Movement & Advocacy chapter deferred** — `ally` (the one ≥3 term) now lives on the LGBTQ+ chapter where its corpus anchors are (HRC/NLGJA/DSG). `tolerance`/`activist`/`advocate`/`equality` are sub-threshold. Needs a movement/organizing-focused source guide to unlock.

**NEW FEATURE (2026-06-03) — Glossary Index canonical-source tiering:**
- Spec: `docs/superpowers/specs/2026-06-03-glossary-canonical-source-tiering-design.md`
- Four tiers in `site/src/data/glossary-index.json`: `full` (≥3 sources, has page) / `verified-hold` (hand-verified 1-2, from `notes/curated-glossary-overrides.yml`) / `curated` (≥1 real glossary-headword source, auto-promoted — 821 terms) / `listed` (incidental only)
- `curated` + `verified-hold` entries link to an INTERNAL `/sources/<slug>/` canonical page — link-rot is handled once via each source page's `live_status` + local archive. Offline-no-archive demotes `curated`→`listed`, keeps `verified-hold` excerpt, emits build-time stderr report.
- Key files: `scripts/build-glossary-index.py` (tiering logic), `notes/curated-glossary-overrides.yml` (seeded with jew/islam/tolerance), `site/src/pages/glossary/index.astro` (tier display/badges/canonical links)
- **Parser gotcha:** `stub: true  # TODO...` inline comment makes a `== "true"` check fail — the string becomes `"true  # TODO..."`. Fixed with `.startswith("true")`. Affects any frontmatter field with an inline comment.

**Launch scope expanded 2026-05-18.** Original "~50 terms / 3-4 chapters" target was a minimum-viable-launch threshold. After looking at actual matrix data (268 terms have ≥3 sources), Jordan locked the full-launch threshold at **≥3 sources, ~250 commons-style term pages across 8-10 chapters, plus a Glossary Index for the ~1,000-term long tail.** No soft launch — full public launch when ready, per `feedback_no_soft_launches`.

**Standing reference — `notes/cleanup-pass-prompt.md`** captures the subagent cleanup-pass workflow + every editorial rule + error pattern caught during Phase 3. Read it before dispatching a cleanup subagent. Update when new error patterns appear.

## Pick-up notes for next ELC session

**NEXT SESSION PLAN (updated 2026-06-06, after source-discovery research):**
1. **Source discovery DONE (2026-06-06).** Research run + audited (`research/source-discovery-2026-06/research-notes.md`). Jordan locked **8 new corpus sources + 2 reference-tier** (UNHCR, IOM): DCFPI (Class anchor), PICUM + HRW (Migration), Opportunity Agenda + Movement Strategy Center (Movement anchor), Religion Stylebook RNA + 18Doors + CAIR (Faith — Religion Stylebook graduates `jew`/`islam`). Skipped: ADL, AJC, ISPU, Momentum, COF, Blanchet, MIRA, Race Forward, Urban Institute; APA SES page = deepen existing APA citations instead. Posture rule established: legal-definitional sources (UNHCR/IOM) go reference-tier, never guidance tables — corpus sources must be equity guides or identity-journalism guides.
2. **Codex ingestion slices DONE (2026-06-06).** Then 2026-06-07: Codex built `scripts/diagnose-term-coverage.py` (W6 counting-chain tracer) + structured-glossary extractors for Religion Stylebook (183 headwords) and MSC (108) — 18Doors/PICUM stay keyword-scan (no reliable headword structure). Matrix/index rebuilt; W6 now 27 terms. **Gotcha:** giving a source a structured extractor removes its keyword-scan hits — 8 of the original 17 W6 terms dropped to 2 sources (their 3rd was an MSC/RS in-body mention). Reports: `notes/source-discovery-2026-06-w6-report-v2.md`, diagnosis in `notes/term-coverage-diagnosis-2026-06.md` (asylum-seeker/migrant/poor have NO headword anywhere; activist/equality/tolerance at 1–2 — Movement still needs another source).
2a. **W6 TRIAGE DONE (2026-06-07, Jordan-approved) — `notes/w6-triage-2026-06-07.md`:** 15 pages to write (incl. `racism` as cluster anchor w/ `prejudice` alias, one gender-vs-sex anchor page w/ `sex` alias, nation-of-islam, interfaith, equity, poverty), 9 coverage-decision drops (violence carries a future Conflict & War chapter seed note), 3 hand-rescue candidates from the dropped 8 (trans-woman, cripple, sexual-preference).
2b. **BRANCH FINISHED + MERGED + DEPLOYED (2026-06-07).** Everything below done: extractions verified (8/8 by parallel agents), 10 source pages written w/ equity-focus posture framing, jew/islam graduated, W6 triage executed (22 pages via 50-agent workflow w/ adversarial verify; 25 Layer-2 precision fixes), 11 coverage decisions + aliases, chapter registration. Merged b1a830d, deployed, live-verified. **State: 139 indexed terms, 198 pages, lint strict 0/0, Layer 1+2 green.** Notable fixes: MSC avoid-tables now extracted (phantom category-header hits removed — gender/poverty counts were inflated); inline `aliases: [..]` now parsed by lint + index builder (43 pages' aliases had never resolved). Original next-task list (for reference): equity-focus framing on the 10 new source pages (progressive equity guide vs identity-journalism guide vs legal-definitional reference — Jordan request 2026-06-06); verify slice A/B extractions; polish source-page About/Access prose; graduate jew/islam (Religion Stylebook = 3rd source; remove from curated-glossary-overrides.yml); execute the triage (15 pages + 2 aliases + 9 decisions + rescue checks); re-run matrix + lint to strict-green; Layer 1/2 verification; merge → main → deploy.
3. **DECISION FOR JORDAN before launch prep:** launch at 115 machine-verified pages vs. grow further with the discovered sources. The verification system changes the calculus — per-page quality is provable and completeness-vs-corpus is machine-checked. Launch prep (repo public, DNS flip, legal pass) waits on this call.

**Done 2026-06-05 (later) — Layer 2 external-claims dispositions executed; verification arc CLOSED:**
- **Dispositions:** ~620 of 664 flags closed as keep under 3 group rules (excerpt-insufficient = bundle artifact; site-structural/chronology framing; hedged sociolinguistic generalizations). Doc: `notes/verification/layer2-external-dispositions.md` (EXECUTED). Re-audit of the 325 excerpt-insufficient flags skipped pre-launch per approved rule.
- **~25 distinct hard facts verified against primary sources** (3 parallel research agents; audit trail in `notes/verification/external-facts-research.md` with URLs + excerpts + VERIFIED/PARTIAL/UNVERIFIED flags).
- **NEW citation mechanism — reference-tier source pages** (`host_posture: link-out-only`, no archive): `sources/ap-stylebook.md`, `sources/pew-research-center.md`, `sources/us-census-bureau.md`. They absorb ~40 citation flags; synthesis prose links internally (`/sources/ap-stylebook/` etc.); statutes/events link inline to primary URLs (congress.gov, law.cornell.edu, census.gov…). 16 term pages carry internal citation links.
- **Research-discovered corrections (beyond the 10 planned exceptions):** caucasian federal-label claim was FALSE (OMB uses "White"; fixed in 3 places); illegal-alien's "1994 UNITY" chronology UNVERIFIED in our voice (the 1994 UNITY resolution on record is about mascots — claim survives only inside the DSG paraphrase, attributed); USCIS 2021 "noncitizen" shift was reversed in 2025 (pages now frame it as a documented turn, not current practice); DACA count refreshed 580k→~538k (KFF, late 2024); two-spirit "coined at"→"adopted at" Winnipeg 1990; HR 4238 scoped to its two 1970s statutes (it did NOT rewrite federal Indian law); AP singular-they "2019 expansion" dropped (only 2017 is documented).
- Lint 0 failures, Layer 1 802 checks 0 findings, 145 pages built, deployed + live-verified. Commits b46b4c7 + 34858e7 on main.

**Done 2026-06-05 — all 81 over-length quotes trimmed to fair-use ≤50 words (W2 lint clean):**
- 67 mechanical (51–80w) via 3 parallel subagents + 14 big ones (81–153w, the definitional heavyweights: bipoc, hispanic, latino, black, white) Jordan-reviewed. All trims are **pure-deletion contiguous spans** of the previously verified quote, span-checked programmatically against git HEAD — paraphrases carry the dropped material (5 extended). Working pattern: the quote-worthy part is the org's *rule or argument in its own voice*; definitions, stats, and worked examples paraphrase fine.
- **Override-row bookkeeping:** 18 touched rows removed from `layer1-verified-overrides.yml`; 16 re-added dated 2026-06-05 with a substring-of-verified-chain rationale (trimmed spans are substrings of 2026-06-04 hand-verified text, so faithfulness is preserved by construction; extraction .mds still can't exact-match them). 3 TRUNCATED verdicts fixed with the trailing-"…" convention instead.
- **Gotcha:** override rows are per (page, org_slug) and cover ALL of that org's entries on the page — removing one exposes untrimmed sibling quotes to re-verification too.
- Layer 1 green (802 checks, 0 findings), lint 0 W2, 142 pages built, deployed + spot-checked live. Commits b9bc6d9 + e1dbccc on main.

**Done 2026-06-04 (later) — full content-verification system shipped + run:**
- **Layer 0** `scripts/lint-content.py` gates every deploy (brackets/TODOs/scaffold notes/broken links). Fixed 19 [[wiki-bracket]] artifacts + 58 leftover TODO comments.
- **Layer 1** `scripts/verify-content.py`: every guidance quote checked against its archive (exact/truncated/loose/gapped tiers + accent-folding + pandoc-noise stripping), confidence-label audit, URL liveness (gated-source tolerant), org/year cross-refs. 433 checks GREEN. 103 extraction-artifact quotes hand-verified vs PDFs live in `notes/verification/layer1-verified-overrides.yml` — **remove a row if its quote is edited**. Quote-triage found zero fabrications; 8 fixes (ellipses, NAJA years).
- **Layer 2** `scripts/verify-synthesis-codex.py`: Codex (ChatGPT OAuth, `codex exec` via stdin, OPENAI_API_KEY stripped) audited 3,921 claims on 91 pages. 125 CONTRADICTED hand-triaged → **114 REAL paraphrase/synthesis precision fixes** (over-claimed consensus, misattributed definitions), 8 dismissed, 3 stale. Zero fabricated quotes / wrong recommendations. Reports + dispositions in `notes/verification/`.
- **Open for Jordan:** keep/cite/cut triage of ~336 genuine EXTERNAL added-facts (`notes/verification/layer2-external-summary.md`, grouped); 325 more flags are "excerpt insufficient" (bundle-size limitation — optional re-audit with bigger bundles).
- **Gotchas captured:** codex hangs = hidden Gatekeeper dialog (Screen Share to dismiss); codex exec input cap ~1MB (use stdin + char-capped bundles); `codex exec -` reads prompt from stdin.

**Done 2026-06-04 — 13-term mega-batch across 5 chapters (94 terms total):**
- Top-coverage sweep: `asian` (5 kept of 16 scaffolded — heavy incidental pruning; SEIU Oriental→Asian inversion handled), `negro` (unanimous avoid, proper-name/historical carve-out), `institutional-racism` (unanimous use; Carmichael/Hamilton coinage in synthesis), `people-with-disabilities` (SEIU inversion fixed avoid→use; person-first vs identity-first debate is the page's spine), `homosexual` (avoid ×4 + DSG medical-context carve-out)
- LGBTQ+ round-out: `transgendered` (unanimous avoid ×6, 2016→2026 register shift documented), `transition` (3 kept of 6 — SumOfUs/SEIU/Sierra were wrong-sense hits: labor/energy transition; NLGJA relevance test), `genderqueer` (exactly 3 strong; not-a-synonym-for-trans rule), `gender-binary` (4 concept-term entries)
- Indigenous round-out: `indian` (bare-Indian page, distinct from american-indian; DSG India-disambiguation + self-id rules + Canadian First Nation replacement), `indian-country` (Title 18 legal term; NAJA OCR verified against PDF), `two-spirit` (rescued from 2-source flag by adding NLGJA's dedicated entry by hand — matrix scan had missed it; capitalization divergence NLGJA-lowercase vs TJA/RET-capitalized documented)
- Immigration: consolidated `dreamer` page (Dreamer / DACA Recipient; 5 entries, 4 orgs). Define American column-scramble resolved by reading PDF p.9 with -layout — definitions verified verbatim. Key teaching: DACA recipients (580k) are a subset of Dreamers (2M+); DREAM Act = legislation (never passed), DACA = executive program (2012). Raw daca/dream-act scaffolds deleted in favor of the one page.
- Fixed 2 invalid category values the scaffolder emitted: `lgbtq-identity` → `sexuality-and-gender-identity`, `disability` → `disability-and-mental-health` (two-spirit, people-with-disabilities)
- Chapter intros updated (race, LGBTQ+, indigenous, immigration); matrix regenerated (94/96 indexed)
- Clean build 142 pages, 0 warnings; deployed; all 13 pages + /search HTTP-200 verified; content spot-checked
- Worktree merged to main (ff), pushed to GitHub, worktree+branch removed

**Done 2026-06-03 — 3 new chapters + round-outs + glossary canonical-source tiering:**
- Age & Generations (3 terms), Criminal Justice & Incarceration (4 terms), Faith & Religious Identity (3 terms) — all deployed + HTTP 200 verified
- Round-outs: Race & Ethnicity +6 (slavery, systemic-racism, discrimination, stereotypes, colonialism, arab), LGBTQ+ +4 (nonbinary, asexual, transsexual, gender-identity), Disability +4 (autism, disabled, depression, injury). Term count 57 → 81.
- Glossary tiering feature shipped (spec + implementation + deployment). 821 curated entries auto-promoted. `jew`/`islam`/`tolerance` seeded in `notes/curated-glossary-overrides.yml` as `verified-hold`.
- Movement & Advocacy chapter deferred — only `ally` at ≥3 sources. Needs a movement/organizing-focused source guide.
- **Parser gotcha fixed:** `stub: true  # TODO...` inline comment breaks `== "true"` check; use `.startswith("true")` everywhere in frontmatter parsers.
- Git hygiene: `site/node_modules` symlink accidentally tracked by `git add -A`; removed from index, added to `.gitignore`. 15 commits merged to origin/main; worktree removed.

**Done 2026-05-30 — all 26 stub source pages written + deployed (Phase 4 launch item closed):**
- **Every source page now has real About + Access prose.** Wrote all 26 from the `research/source-about-material/` packets, the archived guides themselves, and live web verification. Added `copyright_holder` + a conservative fair-use `license` to each; removed `stub: true` from all 26. Clean build (100 pages, 0 warnings; Pagefind now indexes 96 fragments). Deployed + verified live. The ROADMAP Phase 4 item "verify all source pages have About sections written" is **done** — only `apa` and `sierra-club` were written before; the rest are new.
- **Data errors found and fixed while writing:**
  - `gcjt`: org name was "Global Consortium for Journalism & Trauma" → corrected to **"Global Center for Journalism & Trauma"**, and work_title "Gender-Capable Journalism Toolkit" (a fabrication) → **"GCJT Style Guide for Trauma-Informed Journalism"** — both confirmed against the archived document's own masthead/title.
  - `wordsaboutwar` (both full + short): `source_url` `wordsaboutwarmatter.org` was dead → corrected to **`wordsaboutwar.org`** (verified live; David Vine / multi-institutional); `live_status` offline → live.
  - `naja`: year `2017` → **`2023`** (matches the archived June-2023 edition + MANIFEST).
- **Two data discrepancies left as inline notes (your call, not blockers):**
  - `comm-unity-style-guide-2021`: frontmatter says "Comm/Unity Style Guide R4 (2021)" but the archived PDF title page reads "Third Edition • March 2022." NOT changed (the slug `comm-unity-style-guide-2021` is referenced by term-page citations; a year/slug change needs your call).
  - `un-cobo-1972`: year 1972 = study's commissioning; the definition-bearing final report is 1981–1984. Kept 1972 (matches slug); clarified in prose.
- **⚠️ Architecture finding (your decision):** source routes in `site/src/pages/sources/[slug].astro` are keyed by `org_slug`, so the **28 source files collapse to 24 routes** — Color of Change (3 works), IDP (2), and Words about War (2) each render as ONE per-org page. I rewrote those 7 files to be **org-level** (describe the org, list all its cited works) so whichever file Astro renders is correct. Limitation: a single per-org page can't show per-work access postures (e.g. IDP's 2020 first edition is an orphaned 404 while the Comm/Unity edition is live) — both are described in prose but only one frontmatter posture badge shows. If you want a distinct page per work, that's a route change (give each file a unique slug instead of `org_slug`).
- **Next step:** Phase 4 launch remainder — flip repo to public, DNS flip equitylanguagecommons.org, final legal pass; plus the manual setup items below (CF Email Routing, GitHub Discussion categories, CF auto-deploy). Term-rounding-out chapters (LGBTQ+, Indigenous, Disability) remain optional pre-launch.

**Done 2026-05-29 — Pagefind search shipped (Phase 4 launch-gate) + source About fetcher planned:**
- **Pagefind search live.** `astro-pagefind` integration added to `site/astro.config.mjs`; `/search` page added to nav (`site/src/pages/search.astro`); `data-pagefind-body` conditionally scoped via `pagefind?: boolean` prop in `BaseLayout.astro` — only the 4 content page types (terms, chapters, sources, glossary) are indexed; SiteHeader/SiteFooter carry `data-pagefind-ignore`. Build indexes 90 fragments (57 terms + 24 sources + 8 chapters + 1 glossary). Deployed and verified live at https://equity-language-commons.pages.dev/search/.
- **Source About fetcher (next Codex task):** plan at `docs/superpowers/plans/2026-05-29-source-about-fetcher.md`; paste-to-Codex prompt at `docs/superpowers/plans/2026-05-29-source-about-fetcher.codex-prompt.md` (untracked scratch). Script gathers Wikipedia REST + org homepage text for each stub source page into `research/source-about-material/<slug>.md` with VERIFIED/PARTIAL/UNVERIFIED flags. Run Codex on it next session, then Claude writes the About prose from vetted material.
- ~~**Next step:** run the source-about fetcher Codex prompt → review output → write About prose for the 26 stub source pages.~~ **Done 2026-05-30 — see top block.**

**Done 2026-05-27 (latest) — rejected-labels batch + Class & Economic Status chapter started:** Two batches in one session. (1) **Disability rejected labels 10 → 14:** added `addict`, `crazy`, `insane`, `retarded` — all unanimous `avoid`. addict is the noun/label (distinct from the existing `addiction` condition page; covers "junkie"); crazy groups loony/mad/psycho/nuts/deranged; insane carries the legal/criminal-defense carve-out; retarded is the slur (cites Rosa's Law 2010). Cleanup subagent removed 2 incidental hits (Color of Change from crazy, Define American from insane), fixed many scaffolder `use-with-care`→`avoid` mis-tags and 4 wrong DSG quotes. (2) **Class & Economic Status chapter launched (order 6) with 3 terms:** `classism` (structural concept, `use` — APA/SumOfUs/Sierra/RET), `ghetto` (avoid ×6, race/class-coded place term), `disadvantaged` (deficit/charity descriptors — Sierra's do-not-use list + APA's "the poor"→low-income table + CoC charity-framing + SumOfUs). **`inner-city` attempted and folded into `ghetto`** — only 2 distinct orgs (DSG ×2 + NABJ), below the ≥3-org bar, and the sources literally pair "ghetto, inner city"; added as a ghetto alias, and `urban` already aliases it from the race-code angle. **`the poor` NOT shipped as a standalone** — only 2 strong orgs (APA + Sierra); folded into the `disadvantaged` cluster page per Sierra's own grouping. Class corpus is genuinely thin (no dedicated "poverty"/"poor" headwords in the guides). Cleared Astro cache, clean-rebuilt (98 pages, zero warnings), deployed, verified all 7 new pages + both chapters live. Matrix regenerated. **Then rounded out Class 3 → 4:** added `working-class` (`contested` — Color of Change "coded-white, excludes Black families" ↔ APA "claimed pride identity"; 2 strong-but-opposed orgs carry the contested page). **`hardworking` attempted and dropped** — only 2 strong orgs (Sierra coded-stereotype + Define American "good immigrant" myth) once CoC's "hardworking taxpayers" was removed as incidental welfare-queen rhetoric; its Sierra angle already lives on the `urban` page, so nothing lost. Final state: 99 pages, 57 terms, 6 chapters.

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

2b. **Class & Economic Status is at 4 terms (started + rounded out 2026-05-27).** Added `working-class` (`contested`). The round-out confirmed the corpus is genuinely thin on class — a full sweep of candidates left almost nothing else at ≥3 strong orgs. **Attempted and dropped/folded:** `hardworking` (only 2 strong orgs — Sierra "coded stereotype" + Define American "good immigrant" myth; CoC's "hardworking taxpayers" was incidental to the welfare-queen myth — and the Sierra angle is already captured on the `urban` page, the Define American angle is immigration-side); `welfare`/`welfare queen` (only CoC + Sierra one-liner real — the rest incidental); `deserving/undeserving` (1 real); `income/wealth inequality` (2 — Sierra + SumOfUs "use precisely", thin); `class privilege` (APA + RET-incidental); `blue/white-collar` (APA + SEIU = 2); `culture of poverty` (SumOfUs only); `gentrification`/`underclass` (1 each). To go deeper on class needs a new discovered source (a poverty/economic-justice-dedicated guide). Labor & Workers and Housing are adjacent unstarted chapters (`homeless`/`unhoused` already live in Housing via `unhoused-homeless`).

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
