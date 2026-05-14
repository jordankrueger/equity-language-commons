# Equity Language Commons — Roadmap

**Status as of 2026-04-24:** Research complete, schema v0.2 drafted, first test term (`Latinx`) populated end-to-end, HTML design previews built for term + source pages.

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

### 🔄 Phase 2 — Design previews + site scaffold (partially in progress)

**Design previews built early to pressure-test the schema + routing against real display.** Standalone HTML, single-file, inline CSS, no build step — quick-iterate format.

Done:
- [x] `preview/latinx.html` — term page with all display elements (At-a-glance table, synthesis, source cards sorted chronologically, context data, audience notes, history, related terms)
- [x] `preview/sierra-club.html` — source landing page (access posture panel, publication details, version history scaffold, terms citing this source)
- [x] Visual language locked: cream ground, Charter serif headings, system sans body, terracotta accent, color-coded recommendation badges, mobile-responsive

Remaining:
- [ ] `preview/index.html` — A–Z term index
- [ ] `preview/race-ethnicity.html` — chapter browse page
- [ ] Verify Sierra Club guide page count / section count against actual PDF (placeholder values currently)
- [ ] Scaffold Astro project under `site/`
- [ ] Content collections for `terms`, `sources`, `chapters`
- [ ] Port preview HTML/CSS into Astro layouts + components
- [ ] Wire Pagefind client-side search
- [ ] Deploy preview to Cloudflare Pages (private URL)

### Phase 3 — Bulk term indexing (iterative, one category at a time)

Chunk by the taxonomy that emerges from the first ~10 terms. Aim ~20–40 terms per category. Each category is a focused session.

Likely categories (subject to what emerges):
- [ ] Race & Ethnicity
- [ ] Indigenous & Tribal Sovereignty
- [ ] Gender & Sexuality (with trans subcategory)
- [ ] Disability
- [ ] Age
- [ ] Class & Wealth
- [ ] Labor & Workers
- [ ] Housing
- [ ] Immigration & Refugees
- [ ] Incarceration & Policing
- [ ] Sexual & Domestic Violence
- [ ] Health
- [ ] Food (sovereignty, deserts, labor intersection)
- [ ] Environment / Climate
- [ ] Religion & Culture
- [ ] Reproductive Rights

### Phase 4 — Soft launch (private)

- [ ] Pick a domain (e.g., `progressivelanguagecommons.org`). Confirm availability.
- [ ] Final legal review: attribution block per source, CC-BY notice on the curation layer, clear fair-use posture
- [ ] Share preview URL with 3–5 friendly reviewers (progressive comms pros) for feedback
- [ ] Iterate on feedback

### Phase 5 — Outreach + public launch

- [ ] Email Hanna Thomas (SumOfUs) — courtesy + crediting spiritual-successor framing
- [ ] Email active orgs whose guides are cross-referenced — Sierra Club, GLAAD, TJA, APA, NCDJ, NGC, NABJ, NAJA, AAJA, IDP, Dart Center, Race Forward, interACT, Define American, Color of Change, HRC, Radical Copyeditor, Words about War Matter. Notify + ask blessing. Incorporate feedback.
- [ ] Email Conscious Style Guide + Diversity Style Guide maintainers as professional courtesy (peer projects, not competitors)
- [ ] Public announcement. RadComms + GameChanger Salon are natural venues.
- [ ] LinkedIn post from Jordan's personal account (not CampaignHelp).

### Phase 6 — Maintenance rhythm

Ongoing, not a phase in the usual sense.

- Quarterly: re-check for new editions of source guides (TJA updates per-entry; several update annually)
- As found: add new source orgs + new terms
- Accept PR contributions from the community once a contribution workflow exists
- Log `last_reviewed` per term

## Open questions / parked decisions

- **Domain name** — pick before Phase 5 outreach
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
- Do not reach out to source orgs or Hanna Thomas until Phase 1 is complete and we have something concrete (term page + source page previews) to show
