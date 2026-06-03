# Glossary Index — canonical-source tiering for sub-threshold terms

**Date:** 2026-06-03
**Status:** Design approved (Jordan), pending ChatGPT spec review
**Project:** Equity Language Commons (`side-hustle/equity-language-commons/`)

## Problem

The commons publishes a full cross-reference page only for terms with **≥3 strong sources**. Terms below that bar (e.g. `jew`, `islam`, `tolerance`, `advocate`) are not invisible — the Glossary Index already lists all ~1,273 corpus terms A–Z with their source orgs, years, URLs, and auto-extracted excerpts. But that long-tail listing treats a term with a real, clean dictionary definition in one authoritative guide the same as a term that only appears as an incidental keyword mid-sentence.

We want a curated middle layer: any term that has at least one **real glossary headword** in a source should get an index entry that (a) shows a clean excerpt and (b) points the reader to a **canonical source** to consult — with a graceful policy for when that source goes offline.

## Goals

1. Promote sub-threshold terms that have ≥1 genuine glossary-headword source into a **curated** index tier, pointing to a canonical source.
2. Give the handful of hand-verified holds (`jew`, `islam`, `tolerance`) a **verified** tier with a clean, human-checked excerpt.
3. Route every canonical-source link through our **internal source page** (`/sources/<slug>/`), so link-rot is handled in one place via the source page's existing `live_status` + local archive.
4. Fix an existing bug: `stub:true` term pages currently leak into the glossary as if they were full published pages.

## Non-goals (YAGNI)

- No generated page per curated term (avoids stub proliferation / thin SEO pages).
- No per-term offline tracking — the source page owns availability state.
- No external-URL-primary links; the canonical link is always the internal source page.
- No automated re-sourcing when a source dies — we emit a build-time report and a human decides.
- No change to `build-coverage-matrix.py` — the needed signal (`extraction_method`) already exists.

## Background — what already exists

- **`notes/term-coverage-matrix.csv`** columns: `term_normalized, source_slug, line, excerpt, extraction_method, has_avoid_marker, has_capitalization_rule`. **`extraction_method` is already `glossary` (real structured headword) or `keyword` (incidental scan).** This is the signal that distinguishes a real definition from noise. Structured-glossary extractors run over: Diversity Style Guide, NCDJ, HRC, NLGJA, TJA, Radical Copyeditor. Everything else is keyword-scanned.
- **`scripts/build-glossary-index.py`** reads the matrix CSV + the term collection + the source collection and emits `site/src/data/glossary-index.json` (`stats`, `by_letter`, `entries`). Relevant internals:
  - `_build_commons_lookup()` — maps every `terms/*.md` stem → itself. **Does not currently check `stub`, so stub pages count as commons pages.**
  - `_build_source_lookup()` / `_resolve_source()` — read each `sources/*.md` frontmatter into `{org, year, source_url, page_slug}` and resolve a matrix `source_slug` to it (exact filename match, else longest `org_slug` prefix match, else synthetic).
  - `_looks_definitional(cleaned, term)` — an existing heuristic for excerpt quality; reused where helpful.
- **`sources/*.md`** frontmatter already carries: `org`, `org_slug`, `year`, `source_url`, `format`, `local_archive`, `live_status` (`live` / `offline` / `login-gated`).
- **`scripts/enrich-source-pages.py`** maintains `live_status` via HEAD→GET checks (`--check-only` for a non-mutating sweep). Runs in the standard deploy pipeline.

## Design

### The four tiers

Every entry in `glossary-index.json` gains a `tier` field, resolved in this precedence order:

1. **`full`** — a published commons page exists (`terms/<slug>.md` with `stub` falsy). Existing behavior; `commons_slug` set.
2. **`verified-hold`** — the term appears in the new overrides file (1–2 hand-verified sources). Uses the override's human-checked excerpt; `provenance: "verified"`. Stub term pages (`jew`, `islam`) resolve here, not to `full`.
3. **`curated`** — not `full`/`verified-hold`, but the term has **≥1 matrix row with `extraction_method == "glossary"`**. Auto-promoted. Excerpt taken from the highest-precedence glossary row; `provenance: "machine-extracted"`.
4. **`listed`** — only `keyword` rows. Plain long-tail line. Existing behavior.

### Canonical source resolution (`curated` + `verified-hold`)

Each `curated`/`verified-hold` entry carries:

```json
"canonical_source": {
  "source_slug": "diversity-style-guide-2023-11",
  "page_slug": "diversity-style-guide",
  "org": "Diversity Style Guide",
  "year": "2023",
  "source_page_url": "/sources/diversity-style-guide/",
  "live_status": "live"
}
```

- **`verified-hold`**: `canonical_source_slug` comes from the overrides file (explicit human choice).
- **`curated`**: among the term's `glossary`-method rows, pick the canonical source by a fixed precedence list:
  `["diversity-style-guide", "ncdj", "hrc", "nlgja", "tja", "radical-copyeditor"]`
  (most comprehensive aggregator first, then domain-specific). Resolve via the existing `_resolve_source()` to get `page_slug`, `org`, `year`; then read `live_status` + `local_archive` from that source's frontmatter.
- `source_page_url` is always `/sources/<page_slug>/` — never the raw external URL.

### Overrides file (new)

`notes/curated-glossary-overrides.yml` — hand-maintained, parsed without PyYAML (reuse the line-by-line scalar approach already in the script, or a minimal block parser). Format:

```yaml
# Sub-threshold terms we have hand-verified and chosen to elevate.
# Each points to a canonical internal source page.
jew:
  canonical_source_slug: "diversity-style-guide-2023-11"
  excerpt: "Use Jew for both men and women. Never use Jew as a verb or adjective; the forms are demeaning."
  note: "2 verified sources (DSG, SumOfUs); below the 3-source bar. Needs a Jewish-press/interfaith guide to graduate to a full page."
islam:
  canonical_source_slug: "diversity-style-guide-2023-11"
  excerpt: "..."
  note: "..."
tolerance:
  canonical_source_slug: "sierra-club"
  excerpt: "Avoid the frame of \"tolerance\" of differences."
  note: "Sierra-only real entry; valuable but single-source."
```

The override `excerpt` is authoritative for the entry; `canonical_source_slug` resolves through the same source-lookup as curated terms.

**Malformed override guard:** if an override's `canonical_source_slug` does not resolve to a real source page (typo, renamed source), the builder MUST NOT emit a broken `/sources/.../` link. Instead it: (a) keeps the entry as `verified-hold` with its excerpt/note but `canonical_source: null`, and (b) adds the term to the stderr report as `UNRESOLVED OVERRIDE SOURCE: <term> -> <bad_slug>`. This makes overrides typos loud at build time rather than silently broken in the page.

### Offline / link-rot policy

The builder reads `live_status` (and presence of `local_archive`) for each canonical source and sets entry state:

- **`live`** → normal render: "Canonical source: {org} ({year}) →" linking to the source page.
- **`offline` or `login-gated` WITH `local_archive`** → entry adds `canonical_archived: true`; render shows an "archived copy available" hint. The source page itself surfaces the local archive. No build failure.
- **`offline` WITHOUT `local_archive`** → the genuine failure mode. Behavior differs by tier, because a `curated` excerpt is machine-extracted (low standalone value) while a `verified-hold` excerpt is human-checked (worth keeping):
  - **`curated`** → **downgraded to `listed`** (loses its canonical pointer entirely until re-sourced).
  - **`verified-hold`** → **retains its verified excerpt + note** (the human content stays surfaced) but `canonical_source` is set to `null` and `canonical_archived` is irrelevant; the reader sees the verified text without a live pointer.
  - In both cases the term is added to a build-time **report** printed to stderr: `UNAVAILABLE CANONICAL SOURCES (<tier>): <term> -> <source_slug>`. Non-fatal (exit 0), but visible in deploy logs.

This means availability is tracked exactly once (on the source page, by `enrich-source-pages.py`); the glossary inherits it.

### JSON schema additions (per entry)

```json
{
  "term": "jew",
  "display": "Jew",
  "tier": "verified-hold",            // NEW: full | verified-hold | curated | listed
  "provenance": "verified",            // NEW: verified | machine-extracted | null (full/listed)
  "source_count": 2,
  "commons_slug": null,
  "canonical_source": { ... } | null,  // NEW (curated/verified-hold only)
  "canonical_archived": false,         // NEW
  "note": "..." | null,                // NEW (overrides only)
  "sources": [ ... ]                   // unchanged
}
```

`stats` gains: `verified_hold_terms`, `curated_terms` counts (and `long_tail_terms` becomes `listed`-only).

### Display (`site/src/pages/glossary/index.astro`)

Per entry, by tier:
- `full` — unchanged (bold, links to `/terms/<slug>/`).
- `verified-hold` — show display term + verified excerpt + "Canonical source: {org} ({year}) →" (→ `/sources/<page_slug>/`) + a small **"verified"** marker + optional `note`. If `canonical_archived`, append an "archived copy" hint.
- `curated` — same layout, excerpt from matrix, **"from source glossary"** (machine-extracted) marker.
- `listed` — unchanged (plain, sources listed inline).

Stats line near the top gains the curated/verified counts. Tier markers are small text badges, not heavy UI. No new pages, no routing changes.

## Components / units of work

1. **`notes/curated-glossary-overrides.yml`** *(new data file)* — seed with `jew`, `islam`, `tolerance`. Pull the verified excerpts from the existing `jew.md` / `islam.md` guidance blocks.
2. **`scripts/build-glossary-index.py`** *(edit — the one substantive change)*:
   - `_build_commons_lookup()` reads `stub`; stub-true terms are excluded from `full` and recorded as stub for verified-hold resolution.
   - New `_load_overrides()`.
   - New canonical-source precedence resolution + `live_status`/`local_archive` read (extend `_resolve_source` meta or add a helper).
   - Tier assignment + the 4 new entry fields.
   - Offline downgrade + stderr report.
   - Extend `stats`.
3. **`site/src/pages/glossary/index.astro`** *(edit)* — render tiers/markers/canonical link/archived hint; update the TS type for the new fields; update stats line + subtitle copy.
4. **`build-coverage-matrix.py`** — no change.

## Testing / verification

- **Builder unit checks** (script is stdlib-only; add a `--self-check` or a small pytest-free assert block, or verify by inspection of output JSON):
  - A known glossary-headword sub-threshold term (e.g. pick one with exactly one `glossary` row) → `tier: curated`, `canonical_source.source_page_url` set, `provenance: machine-extracted`.
  - `jew` / `islam` → `tier: verified-hold`, override excerpt present, `provenance: verified`, NOT `full`.
  - A keyword-only term → `tier: listed`, no `canonical_source`.
  - A real ≥3 page (e.g. `ageism`) → `tier: full`.
- **Offline simulation:** temporarily flip one canonical source's `live_status` to `offline` and remove/rename its `local_archive` in a scratch copy → entry downgrades to `listed` and the term appears in the stderr report. (Do this read-only / revert; do not commit the flip.)
- **Build:** `cd site && npm run build` clean; `/glossary/` renders curated + verified entries with working `/sources/...` links; Pagefind still indexes.
- **Live:** deploy to the CF Pages preview; spot-check `/glossary/` shows the new tiers and the canonical links resolve to live source pages.

## Rollout

1. Implement units 1–3 in the worktree.
2. Run `scripts/build-glossary-index.py`; inspect `glossary-index.json` against the tier checks above.
3. `npm run build`; visual check `/glossary/`.
4. Deploy to preview; verify live.
5. Commit; merge to `main`. (Pre-launch preview — no announce.)

## Open questions / risks

- **Excerpt quality for `curated` (machine-extracted)** entries depends on the structured extractor's cleanliness; the "from source glossary" marker is the honesty mechanism. Acceptable because these are pointers-to-canonical, not authoritative cross-references.
- **Precedence list** is a fixed heuristic; if a term's only `glossary` source isn't in the list, fall back to the first `glossary` row by source order and still link its source page.
- **`jew`/`islam` are currently `stub:true` term pages.** Decision implied by this design: they become `verified-hold` glossary entries; keep the `.md` files (so the verified guidance + eventual synthesis survive) but the stub-aware builder stops rendering them as full pages. They graduate back to `full` automatically once a 3rd source lands and `stub` is removed.
