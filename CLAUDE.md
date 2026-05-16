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

Phases 0 and 1 **complete** (2026-04-24). Schema v0.3 locked after three
structurally-different test terms (Latinx, unhoused/homeless, Indigenous).
Phase 2 next: Astro site scaffold + four queued source acquisitions
(Homelessness Beat Reporters guide; Radical Copyeditor's 30-phrases essay;
full APA Inclusive Language Guide; NAJA Tribal Nations Media Guide).
See `ROADMAP.md` for phased plan.

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

- `source-guides/` — archived guides Jordan dropped in (6 originals)
- `source-guides/discovered/` — guides pulled during research phase (27 files)
- `source-guides/MANIFEST.md` — file catalog with host posture per guide
- `research/research-notes.md` — full research audit trail (follow `.claude/rules/client-research.md` — VERIFIED sources)
- `notes/` — taxonomy drafts, schema, test terms, working notes
- `site/` — Astro project (scaffolded; Phase 2 in progress)
- `scripts/` — utility scripts (deploy.sh, etc.)
- `ROADMAP.md` — phased plan

## Deploy

- **Production URL (preview-tier, not announced):** https://equity-language-commons.pages.dev/
- **Deploy command:** `./scripts/deploy.sh` — runs `npm run build` in `site/` and pushes `dist/` to CF Pages via Wrangler using `PERSONAL_CLOUDFLARE_API_TOKEN`.
- **GitHub repo:** https://github.com/jordankrueger/equity-language-commons (private)
- **Wrangler CF Pages project:** `equity-language-commons` on Jordan's personal CF account, currently direct-upload.
- **TODO (Jordan, one-time):** wire GitHub auto-deploy via the CF dashboard so pushes to `main` deploy automatically. Path: CF Dashboard → Workers & Pages → equity-language-commons → Settings → Build & deployments → Connect to Git. Until that's done, run `./scripts/deploy.sh` after each meaningful change.
- **Custom domain (equitylanguagecommons.org) is NOT pointed at the project yet.** DNS flip = public launch per ROADMAP Phase 4.

## Locked decisions (2026-04-23)

- **Shape:** Option C — cross-referenced omnibus with sourced excerpts
- **Name:** Equity Language Commons (domain: equitylanguagecommons.org; repo: equity-language-commons)
- **Branding:** side-hustle only, not CH
- **Stack:** Astro + Pagefind + Cloudflare Pages + R2 (for orphan PDFs)
- **GitHub account:** `jordankrueger/`
- **Host posture (per source):** see MANIFEST.md — Link / Archive / Reference tiers

## Still open

- Domain name
- Whether to accept user submissions at v1 or v2
- Relationship with Conscious Style Guide + Diversity Style Guide (sibling or competitor framing)
- Downloadable "everything" PDF — later decision

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
