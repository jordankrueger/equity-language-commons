# Term Entry Schema — v0.3 (locked 2026-04-24)

**Changelog from v0.2** — driven by populating `unhoused-homeless` (term #2) and `indigenous` (term #3):
- Added top-level `external_references[]` for sources that name the term but only point at other guides' rulings (validated on TJA → Homelessness Beat Reporters Collective in term #2; NLGJA, TJA → IJA reporting guides in term #3)
- Added top-level `methodological_context[]` for sources that supply a framework relevant to the term without defining the term themselves (NCDJ / APA / Radical Copyeditor in term #2; Younging's *Elements of Indigenous Style* / UN Cobo report in term #3)
- Added per-guidance optional `derived_from: [org_slug]` for citation-chain clarity when one source's entry is materially built on another (e.g., DSG's Indigenous entry derived from NAJA; NGC's whole style derived from Younging 2018)
- Extended `related_terms.relation` enum with `geographic-variant` (First Nations ↔ Native American ↔ Aboriginal — same political function, different national context) and `gendered-or-dated-form` (a catch-all for older but still-current-in-some-contexts variants like "Indian")
- Extended `confidence` enum with `SUMMARY-ONLY` for archives that are faithful WebFetch summaries rather than verbatim captures (e.g., APA archived markdown)

**Changelog from v0.1 → v0.2** — driven by populating `latinx` as term #1:
- Added `related_terms` (distinct terms in the same family) to complement `aliases` (spelling/casing variants of the same term)
- Added `non-preferred` to the `recommendation` enum
- Added `VERIFIED-ARCHIVED` to the `confidence` enum
- Added `entry_updated` per-guidance (for web-native guides that version entries independently of the guide's overall year)
- Allowed `guidance[]` to have multiple entries from the same org for the same term (different quote locations within the same guide)
- Promoted `audience_notes` from optional-proposal to standard field
- Added top-level `context_data` (optional) for empirical data (e.g., Pew adoption rates) that guides cite

## File location

One file per term at `site/src/content/terms/<slug>.md`. Slug is lowercase, hyphen-separated, ASCII.

Cluster rule: each **distinct term** gets its own file. Spelling/casing variants of the same term are aliases inside a single file; semantically distinct terms (e.g., Hispanic vs. Latino — different meanings) are separate files with `related_terms` cross-references.

## YAML frontmatter

```yaml
---
# identity
term: "Latinx"
slug: "latinx"
aliases:                          # spelling/casing variants that should resolve to this entry
  - "LatinX"
  - "latinx"
related_terms:                    # distinct but related terms with their own entries
  - slug: "latine"
    relation: "alternative-form"  # gender-inclusive alternative, Spanish-pronounceable
  - slug: "latino"
    relation: "gendered-form"
  - slug: "hispanic"
    relation: "overlapping-but-distinct"  # different definitional basis
  - slug: "chicanx"
    relation: "subset-identity"

# classification
categories:
  - "race-ethnicity"
  - "language-and-identity"
tags:
  - "contested-term"
  - "evolving-usage"
  - "self-id-required"
  - "gender-inclusive"

# per-source guidance — the spine of the entry
# multiple entries from the same org allowed (e.g., a guide may have a default-statement quote
# AND a term-specific quote that both need capturing)
guidance:
  - org: "Sierra Club"
    org_slug: "sierra-club"
    year: 2021                     # guide's overall publication year
    entry_updated: null            # date this specific term entry was last updated (null if unknown/not a web-native guide)
    source_url: "https://..."
    local_archive: "source-guides/..."
    recommendation: "use-with-care"
    derived_from: []               # optional; list org_slugs of sources this entry is materially built on
    quote: "..."
    quote_loc: "p. 13"
    paraphrase: "..."
    confidence: "VERIFIED"

# context data — external empirical data the guides cite
# not a source quote; captured separately so synthesis can reference it
context_data:
  - label: "Pew Research (Dec 2019)"
    claim: "Only 3% of U.S. Hispanic/Latino adults use 'Latinx' to describe themselves; 23% have heard of the term."
    url: "https://..."
    relevance: "Frequently cited by style guides as grounds for 'use-with-care' framing."

# external references — sources that name the term only by pointing at another guide,
# without issuing their own term-level ruling
external_references:
  - org: "Trans Journalists Association"
    org_slug: "tja"
    year: 2026
    source_url: "https://..."
    local_archive: "source-guides/..."
    references: "Homelessness Reporting Guide — Homelessness Beat Reporters Collective"
    references_url: "https://..."
    note: "TJA lists this guide under its external-references section; does not issue its own ruling."

# methodological context — sources that supply a framework relevant to the term
# but don't define the term themselves. Cite in synthesis; surface in the term page as context.
methodological_context:
  - org: "Gregory Younging / Brush Education"
    org_slug: "elements-of-indigenous-style"
    year: 2018
    source_url: "https://..."
    local_archive: null   # paid book; cited, not hosted
    framework: "Indigenous style as distinct editorial system"
    note: "Foundational book-length treatment. NGC's 2021 guide is structurally built on this source."

# audience-specific guidance
audience_notes:
  - audience: "Spanish-speaking / bilingual"
    note: "'Latine' often preferred — pronounceable in Spanish, works grammatically."
  - audience: "Geographic — Eastern US / Caribbean / South American"
    note: "'Hispanic' more common in self-identification."
  - audience: "Geographic — Western US / Mexican-American"
    note: "'Latino' / 'Chicano' more common."
  - audience: "Generational"
    note: "Younger cohorts more likely to use Latinx/Latine; older cohorts Latino/Hispanic."

# meta
last_reviewed: 2026-04-24
created: 2026-04-24
contributors:
  - "Jordan Krueger"
---
```

## Body (markdown)

```markdown
## Synthesis

Jordan's cross-reference note — 1–4 paragraphs. Where guides agree, where they
diverge, what's evolving, how to decide contextually.

## Cross-references

Prose links to `related_terms` entries with brief framing of why they matter.

## History note *(optional)*
```

## Field notes

### `recommendation` enum — v0.2 values

| Value | Meaning |
|---|---|
| `use` | Source recommends as a preferred term. |
| `non-preferred` | Source accepts but recommends a different form as the default. *(new in v0.2)* |
| `avoid` | Source says don't use. |
| `use-with-care` | OK with caveats / in certain contexts. |
| `contested` | Source explicitly notes community is split. |
| `evolving` | Source flags that guidance is likely to change. |
| `reclaimed-in-community` | Slur or charged term OK from in-group, not from outside. |

### `confidence` enum — v0.3 values

| Value | Meaning |
|---|---|
| `VERIFIED` | Quote pulled from actual source PDF/page, exact wording confirmed, canonical URL publicly fetchable. |
| `VERIFIED-ARCHIVED` | Quote confirmed from archived copy; canonical URL now paywalled/offline. *(new in v0.2)* |
| `SUMMARY-ONLY` | Archive is a faithful WebFetch summary, not verbatim capture. `quote` null; `paraphrase` only. Use when source is public but live fetch blocked (e.g., anti-bot). Different from `PARTIAL` in that the archive's summary IS trustworthy — just not a quote-able verbatim capture. *(new in v0.3)* |
| `PARTIAL` | Source found but exact wording differs. `quote` null, `paraphrase` only. |
| `UNVERIFIED` | Claim from training data / secondary reference. Should not ship publicly. |

### `related_terms.relation` — v0.3 values

| Value | Meaning |
|---|---|
| `alternative-form` | Functionally substitutable but distinct term (Latinx ↔ Latine). |
| `gendered-form` | Same term with gendered suffix (Latinx ↔ Latino ↔ Latina). |
| `gendered-or-dated-form` | Older or era-specific form retained in legal/historical contexts or by self-ID (Indigenous ↔ Indian). *(new in v0.3)* |
| `geographic-variant` | Same political/identity function, different national context (Native American [US] ↔ First Nations [CA] ↔ Aboriginal [AU]). *(new in v0.3)* |
| `overlapping-but-distinct` | Different definitional basis, partial overlap (Latinx ↔ Hispanic; Indigenous ↔ Tribal). |
| `subset-identity` | More specific identity within the broader term (Latinx ⊃ Chicanx; Indigenous ⊃ Alaska Native). |
| `umbrella-for` | More general identity that subsumes this one (BIPOC ⊃ Latinx). |

### Fair-use guardrail

Each `quote` is capped at 50 words. Longer fair-use permissions require explicit per-source permission (Phase 5 outreach work).

### Multi-part guidance from one source

When a guide gives compound guidance (a default + a caveat, or a general principle + a term-specific ruling), add **multiple entries in `guidance[]` with the same `org`**, each with its own `quote` and `quote_loc`. Don't try to cram both quotes into one entry.

### What we're still NOT locking

- Whether `categories` and `tags` become controlled vocabularies or stay free-form (decide after 10 terms)
- Whether `relation` enum is exhaustive (add values as new relationships appear)
- Whether `context_data` should be its own content type (cited from many terms) rather than embedded per-term

---

## v0.3 lock — decisions and deferrals (2026-04-24)

Locked after three structurally-different test terms — `latinx` (race/ethnicity, moderate cluster), `unhoused-homeless` (class/housing, sparse corpus, time-capsule shape), `indigenous` (sovereignty framing, pan-national cluster, layered postures).

### Accepted into v0.3

| Addition | Validated on | Rationale |
|---|---|---|
| `external_references[]` top-level | Terms #2, #3 | Sources that point at other guides rather than issuing their own ruling (TJA → Homelessness Beat Reporters Collective, TJA/NLGJA → IJA). Don't want these living as ersatz guidance entries. |
| `methodological_context[]` top-level | Terms #2, #3 | Sources that articulate a framework without defining the term (NCDJ/APA/Radical Copyeditor on person-first; Younging + UN Cobo for Indigenous). Keep guidance[] clean. |
| `derived_from: [org_slug]` per guidance | Term #3 | When one source's entry is materially built on another (DSG Indigenous ← NAJA; NGC style ← Younging). Makes citation chains legible. |
| `geographic-variant` in `related_terms.relation` enum | Term #3 | Native American / First Nations / Aboriginal — same function, different national context. No existing value captured this. |
| `gendered-or-dated-form` in `related_terms.relation` enum | Term #3 | For terms like "Indian" that are older but still live in self-ID, legal, or historical contexts. |
| `SUMMARY-ONLY` in `confidence` enum | Term #3 | APA archived markdown is a WebFetch summary (anti-bot blocked curl), not verbatim capture. Trustworthy as paraphrase, not as a quote. Different from `PARTIAL`. |

### Deferred (not v0.3)

| Candidate | Why deferred |
|---|---|
| Chapter-content type (for Tribal Sovereignty, cross-cutting principles) | Not a term-schema issue — it's a chapter-schema issue. Design the chapter schema separately when starting the site scaffolding (Phase 2). |
| `avoided_terms[]` per guidance entry (structured avoided-terms list) | Currently handled in prose. Consider when starting site design if the term-page UI needs a dedicated "terms to avoid" sidebar. Not yet a design need. |
| Controlled vocabularies for `categories` and `tags` | Still free-form. Decide after ~10 terms exist (current count: 3). Emergent taxonomy will be more honest than top-down. |
| `context_data` as its own content type (cited across multiple terms) | Single-use in Latinx so far. Revisit if the same data point gets cited from ≥3 terms. |

### Implication for already-written test terms

- **`latinx.md`** — no schema changes needed. v0.2 → v0.3 is purely additive for this term. Leave as-is.
- **`unhoused-homeless.md`** — already prototypes `external_references[]` + `methodological_context[]`. Now formalized. Leave as-is.
- **`indigenous.md`** — uses all v0.3 additions (`external_references[]`, `methodological_context[]`, `derived_from`, `geographic-variant`, `gendered-or-dated-form`, `SUMMARY-ONLY`). Treat as the canonical v0.3 reference implementation.
