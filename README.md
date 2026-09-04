# Equity Language Commons

A cross-referenced omnibus of progressive equity-language guidance: every source organization's rule side-by-side, per term, with attribution.

🌐 **Live site:** [equitylanguagecommons.org](https://equitylanguagecommons.org)

📖 **Browse the commons:** [Chapters](https://equitylanguagecommons.org/chapters/) · [Glossary](https://equitylanguagecommons.org/glossary/) · [Sources](https://equitylanguagecommons.org/sources/)

🤝 **Want to contribute?** Start at the [Contribute page](https://equitylanguagecommons.org/contribute/): there are four paths in (suggest, discuss, PR, email) and a step-by-step onboarding section for people new to GitHub.

---

## What this is

Every progressive equity-language style guide says something a little different. Sierra Club has a position. NABJ has one. Native Governance Center has one. The Trans Journalists Association has one. Diversity Style Guide aggregates them. **Each one is one author's view at one moment in time.**

The commons puts them next to each other.

For every term: `Latinx`, `tribe`, `transgender`, `unhoused`, `disability`, on and on: every source organization's ruling appears together: their direct quote, their year, their page reference, and a position badge that summarizes where they landed (`use`, `use-with-care`, `avoid`, `evolving`, etc.). A short synthesis paragraph identifies the cross-source pattern: where guides agree, where they diverge, what's shifted over time.

**The commons does not issue its own rulings.** It surfaces what the source guides say so readers can see the multi-source picture and decide what fits their audience.

## What this is not

- **Not a single-author style guide.** That's a separate genre. SumOfUs's *A Progressive's Style Guide* (Hanna Thomas + Anna Hirsch, 2016) is the spiritual predecessor: a single-author synthesis. The commons preserves SumOfUs as one source among many.
- **Not exhaustive.** The commons covers progressive equity-language guides specifically. Brand identity guides, journalism style references for grammar/AP usage, and clinical/academic terminology guides are out of scope unless they intersect with equity language.
- **Not a clearinghouse.** Each source guide remains on its publisher's site (or, where the publisher has gone dark, in our private mirror). The commons cites; it does not republish.

## How it works

```
You read a source guide       The commons reads 30+ source guides
     ↓                                  ↓
You see one rule                You see every rule side-by-side
     ↓                                  ↓
You apply it                    You make a more informed choice
```

The data model centers on **terms**, **sources**, and **chapters**:

- A **term page** (e.g. `/terms/transgender/`) lists every source organization's treatment of the term, with attribution, quote, and position badge. A synthesis paragraph identifies cross-source patterns. Audience notes give per-audience operational guidance.
- A **source page** (e.g. `/sources/nlgja/`) describes one organization, lists every term in the commons that cites it, and provides access-posture information (hosted publicly, private mirror with link-out, or link-out only).
- A **chapter page** (e.g. `/chapters/sexuality-and-gender-identity/`) bundles related terms with a lede, cross-cutting principles drawn from the actual term patterns, and a chronology.

The site also ships with:

- A **Glossary Index** covering 1,154 primary entries from the source corpus, with aliases grouped under their canonical entries.
- A **SQLite build-time index** at `/data/elc-index.sqlite` for anyone who wants to run faceted queries against the commons without scraping.

## Current coverage

| Item | Status |
|---|---|
| Indexed commons terms | 139 |
| Published chapters | 9 |
| Source organizations | 37 |
| Glossary Index | 1,154 primary entries |
| SQLite index | Live |

## Stack

- **Astro 7** + TypeScript strict mode: content collections with Zod schemas, static-site generator
- **Pagefind**: client-side search at build time
- **Cloudflare Pages**: hosting, free tier
- **Cloudflare Email Routing**: `hello@equitylanguagecommons.org` forwarded to maintainer inbox
- **Python 3.11+** stdlib only: the build pipeline (PDF extraction, coverage matrix, scaffolders, enrichers, glossary index, SQLite index)
- **GitHub**: version control, Discussions, Issues, PRs

No databases, no runtime dependencies, no JavaScript framework. The whole site is static HTML + CSS with a single client-side script for search.

## Running locally

You'll need Node 20+, Python 3.11+, and poppler (for PDF extraction).

```bash
git clone https://github.com/jordankrueger/equity-language-commons.git
cd equity-language-commons/site
npm install
npm run dev   # http://localhost:4321/
```

For production preview:

```bash
npm run build
npm run preview
```

For the public build:

```bash
# Run from the repo root
./scripts/build-glossary-index.py    # Glossary data
./scripts/check-glossary-index.py    # Glossary integrity
./scripts/build-sqlite-index.py      # SQLite index
python3 scripts/lint-content.py      # Content checks
cd site && npm run build             # Production site
```

Copyrighted source PDFs and full-text extractions are kept in a private maintainer archive and are not part of the public repository. Propose new sources through an issue so a maintainer can archive and verify them.

Detailed contribution workflow in [CONTRIBUTING.md](CONTRIBUTING.md).

## Editorial principles

Three rules govern every piece of content in the commons:

1. **Self-identification is primary.** When a guide's rule or the commons's synthesis touches on identification, defer to how the subject identifies. Never override stated preference with a default.
2. **No blame-leaning language about source-guide authors.** Every style-guide author was doing the best they could with what was available at the time. Use neutral chronological framing ("pre-dates X," "earlier than"): never "outdated," "behind," "hasn't aged well."
3. **Editorial synthesis is welcome: editorial judgment of individual authors is not.** Identify patterns and trends across the corpus. Don't characterize earlier guides as failures.

Quote attribution rules:

- Every direct quote ≤50 words (fair-use safety margin)
- Every quote cites org, year, source URL, page/section, and confidence level
- Every claim in synthesis must be traceable to a source in the corpus

Full editorial voice rules in [CONTRIBUTING.md](CONTRIBUTING.md#editorial-voice-and-quoting-rules).

## License

The commons consists of three layers, each with its own license:

- **Content** (synthesis, chapter intros, schema, per-term composition): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Share, adapt, and reuse freely with attribution.
- **Code** (Astro components, build pipeline, deploy tooling): [MIT](LICENSE). Standard open-source software license.
- **Source-guide quotations**: © respective publishers. Used under fair use (each quote <50 words with full attribution). Reuse beyond fair-use citation requires permission from the original publisher.

Full text in [LICENSE](LICENSE).

## Credits and acknowledgments

The commons cites work from dozens of organizations doing the on-the-ground work of equity language. A full list, with current access status, lives at [/sources/](https://equitylanguagecommons.org/sources/). The corpus would not exist without:

- Hanna Thomas + Anna Hirsch: *A Progressive's Style Guide* (SumOfUs, 2016): the spiritual predecessor.
- Native Governance Center, NAJA / Indigenous Journalists Association, NABJ, NLGJA, Trans Journalists Association, GLAAD, HRC, interACT: primary identity-led style references.
- Sierra Club, NCDJ, APA, Race Forward, Diversity Style Guide, Racial Equity Tools, Color of Change, Define American, Immigrant Defense Project, Dart Center / GCJT, World Food Program USA, Words About War Matter: primary movement and journalism style references.
- The maintainers of the *Conscious Style Guide* and *Diversity Style Guide*: peer aggregators whose work is the prior art for this kind of cross-reference project.

Maintained by [Jordan Krueger](https://jordankrueger.com).

## Code of Conduct

This project follows the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md) with a project-specific note about terminology debates. Reports to **hello@equitylanguagecommons.org**.

---

*A side project, not a CampaignHelp deliverable. Built as a gift to the community of progressive communicators who do this work for a living.*
