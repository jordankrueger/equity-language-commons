# Contributing to the Equity Language Commons

Thank you for considering a contribution. This document is for people who want to submit a change directly via a pull request. If you're looking for the friendlier "how do I suggest something" version, start at the [Contribute page on the live site](https://equitylanguagecommons.org/contribute/): it covers Issues, Discussions, and email as alternatives to PRs.

This guide covers:

1. [What the commons is, briefly](#what-the-commons-is-briefly)
2. [Before you start: open an issue or discussion first](#before-you-start)
3. [Setting up locally](#setting-up-locally)
4. [Project structure](#project-structure)
5. [Editorial voice and quoting rules](#editorial-voice-and-quoting-rules)
6. [How to add a new term](#how-to-add-a-new-term)
7. [How to add a new source guide](#how-to-add-a-new-source-guide)
8. [Running the pipeline](#running-the-pipeline)
9. [Submitting a pull request](#submitting-a-pull-request)
10. [What we can't accept](#what-we-cant-accept)

---

## What the commons is, briefly

The Equity Language Commons is a cross-referenced omnibus of progressive equity-language guidance. Each term page shows every source organization's rule side-by-side: short fair-use quote, year, page reference, recommendation badge, with a synthesis paragraph identifying cross-source patterns. The commons does not issue its own rulings; it surfaces what the source guides say.

The full project context lives in [CLAUDE.md](CLAUDE.md) and [ROADMAP.md](ROADMAP.md).

## Before you start

For anything beyond a typo fix, **open an issue or discussion first** so we can align before you invest time:

- New term suggestion → [open an issue](https://github.com/jordankrueger/equity-language-commons/issues/new/choose) using the "Suggest a new term" template
- New source guide → "Suggest a new source guide" template
- Methodology, framing, chapter organization questions → [start a Discussion](https://github.com/jordankrueger/equity-language-commons/discussions)
- Editorial voice questions → Discussion

For typo fixes, broken-link fixes, and obvious factual corrections, a direct PR is fine: no issue needed.

## Setting up locally

You'll need:

- **Node 20+** (Astro 5 requirement)
- **Python 3.11+** for the build pipeline scripts (stdlib only: no Python dependencies to install)
- **poppler** for PDF→text extraction (`brew install poppler` on macOS)
- **tesseract** for OCR on image-only PDFs (`brew install tesseract` on macOS): only needed if you're adding a scanned PDF source

Clone, install Node deps, and start the dev server:

```bash
git clone https://github.com/jordankrueger/equity-language-commons.git
cd equity-language-commons/site
npm install
npm run dev
```

The dev server runs at `http://localhost:4321/`.

To preview a production build:

```bash
npm run build
npm run preview
```

## Project structure

```
equity-language-commons/
├── site/                   # Astro project
│   └── src/
│       ├── content/
│       │   ├── terms/      # One .md per term (the commons entries)
│       │   ├── sources/    # One .md per source organization
│       │   └── chapters/   # One .md per chapter
│       ├── pages/          # Astro pages
│       ├── components/     # Astro components
│       ├── layouts/        # BaseLayout
│       └── data/           # Derived data (glossary-index.json)
├── scripts/                # Build pipeline (Python + bash, stdlib-only)
├── source-guides/          # Source PDFs + extracted markdown
│   ├── *.pdf               # Originally-archived sources
│   ├── *.md                # PDF→markdown extractions
│   ├── discovered/         # Sources discovered during research phase
│   └── MANIFEST.md         # Canonical catalog of every source
├── notes/                  # Schema docs, coverage matrix outputs
├── research/               # Research-notes audit trail
├── preview/                # Early HTML/CSS design previews (pre-Astro)
├── ROADMAP.md              # Phased plan
├── CLAUDE.md               # Project instructions
└── README.md               # You're reading the file pointed at by this
```

## Editorial voice and quoting rules

The commons enforces editorial voice rules that go beyond ordinary style. Read these before drafting any synthesis or paraphrase.

**No blame-leaning language about source-guide authors.** Every style-guide author was doing the best they could with what was available at the time. Describe what each guide does, name dates and context, and let chronology speak for itself. Use neutral chronological framing: "pre-dates X," "earlier than," "written before Y settled into practice." Never use "outdated," "hasn't aged well," "behind," or any phrasing that reads as judgment of the author. The full rule lives in [CLAUDE.md](CLAUDE.md).

**Editorial synthesis is welcome: editorial judgment of individual authors is not.** Synthesis identifies patterns, positions, and trends across the corpus. It does not characterize older guides as failures.

**Quote attribution is non-negotiable.** Every direct quote must include:

- Org name and `org_slug`
- Publication year
- `source_url` (current canonical URL: verify with a live HEAD check)
- `local_archive` path (relative to repo root)
- `quote_loc`: a real page/section name, not just a line number
- `paraphrase`: 1-3 sentence contextualization in your own words
- `confidence: "VERIFIED-ARCHIVED"` only if you confirmed the quote against the local archived file

**Fair-use limit: every direct quote must be under 50 words.** This is a safety margin, not the actual fair-use ceiling, but staying inside it keeps the commons defensible without per-source negotiation.

**Self-identification is primary** across every term in the commons. When a guide's rule or the commons's synthesis touches on personal identification, defer to how the subject identifies. Never override stated preference with a "default."

## How to add a new term

The fast path uses the existing pipeline:

```bash
# 1. Refresh the coverage matrix
./scripts/build-coverage-matrix.py

# 2. Pick a term from notes/term-coverage-matrix.md "Top 50 candidates"
#    (or pick your own: verify it has at least 3 source citations first)

# 3. Scaffold the term file from matrix data
./scripts/scaffold-term.py <slug>

# 4. Open site/src/content/terms/<slug>.md and clean up:
#    - Verify each quote against the local source archive
#    - Fix any mis-classified recommendations
#    - Tighten quotes to <50 words; pick the most term-relevant passage
#    - Write the synthesis (2-4 paragraphs, follow editorial voice rules)
#    - Write audience_notes (2-4 entries)
#    - Populate related_terms, categories, tags
#    - Remove `stub: true`

# 5. Verify the schema
cd site && npm run build && cd ..

# 6. Refresh derived data
./scripts/build-coverage-matrix.py
./scripts/build-glossary-index.py
./scripts/build-sqlite-index.py
```

Model your work on existing high-quality term pages: `site/src/content/terms/black.md` (gold standard for cross-source treatment) or any term from the Indigenous or LGBTQ+ batches (`native-american.md`, `transgender.md`, etc.).

## How to add a new source guide

```bash
# 1. Drop the PDF into source-guides/ or source-guides/discovered/
#    (use discovered/ unless it was in Jordan's original archive)

# 2. Add a row to source-guides/MANIFEST.md
#    (filename, org, title, year, scope, host_posture)

# 3. Extract PDF→markdown
./scripts/extract-pdfs.sh

# 4. Refresh matrix to include the new source's terms
./scripts/build-coverage-matrix.py

# 5. Scaffold a source page if one doesn't already exist
./scripts/scaffold-source-pages.py

# 6. Run the enricher to fill mechanical metadata (page count, format,
#    live URL status, last_checked date)
./scripts/enrich-source-pages.py

# 7. Manually write the source page's About section and Access posture
#    rationale at site/src/content/sources/<slug>.md
```

Host posture must be picked thoughtfully: see [ROADMAP.md](ROADMAP.md#host-posture-per-source-locked-2026-04-24) for the three-tier system.

## Running the pipeline

The full pipeline order, when adding both new sources and new terms:

```bash
./scripts/extract-pdfs.sh              # PDF → markdown (only when new PDFs added)
./scripts/build-coverage-matrix.py     # Refresh term coverage data
./scripts/scaffold-source-pages.py     # Create source pages for new sources
./scripts/enrich-source-pages.py       # Fill mechanical metadata
./scripts/scaffold-term.py <slug>      # Scaffold each new term
# … per-term LLM cleanup happens here …
./scripts/build-glossary-index.py      # Refresh glossary data
./scripts/build-sqlite-index.py        # Refresh SQLite index
cd site && npm run build               # Final schema check
```

The deploy script runs steps 2, 5 (glossary), 6 (sqlite), and the npm build automatically:

```bash
./scripts/deploy.sh
```

## Submitting a pull request

1. Fork the repo and create a branch with a descriptive name: `add-term-undocumented`, `fix-naja-url`, `rewrite-disability-chapter-intro`.
2. Run the build locally and make sure schema validation passes (`cd site && npm run build`).
3. Open the PR with:
   - A clear title describing the change
   - A short description of what changed and why
   - A reference to the originating issue or discussion (if one exists)
4. The PR will be reviewed by Jordan Krueger. Expect editorial feedback on synthesis paragraphs: voice and tone matter as much as factual accuracy.
5. Once approved, the PR will be squash-merged and the change will deploy automatically on the next push.

## What we can't accept

- **Full reproductions of copyrighted source guides.** Quotes must be under 50 words, with full attribution. If you've co-written or hold rights to a guide you'd like included, [open a discussion](https://github.com/jordankrueger/equity-language-commons/discussions) or email hello@equitylanguagecommons.org first.
- **Claims not traceable to source guides in the corpus.** Every synthesis statement must be attributable to a source we've archived. "Most people think X" without a source isn't usable.
- **Editorial judgment of source-guide authors.** See [editorial voice rules](#editorial-voice-and-quoting-rules) above. The commons describes; it doesn't characterize earlier guides as failures.
- **Promotional content for non-style-guide projects.** The commons is a reference, not a directory.
- **Anything that breaks the fair-use margin** (≥50-word quotes without permission, full-text mirrors without explicit grant).

If you're unsure whether something would be accepted, open a Discussion first: it's lower-friction than learning during PR review.

---

By contributing, you agree that your contributions will be licensed under the same terms as the rest of the commons (CC BY 4.0 for content, MIT for code): see [LICENSE](LICENSE).
