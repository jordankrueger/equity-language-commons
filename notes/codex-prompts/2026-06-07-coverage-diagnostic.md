# Task: build scripts/diagnose-term-coverage.py

## Goal
A diagnostic script that explains, for any given term, why it did or did not reach the W6 ≥3-source coverage bar. Stopping condition: `./scripts/diagnose-term-coverage.py poor "asylum seeker" activist` runs clean and prints a per-hit trace for each term, and `notes/term-coverage-diagnosis-2026-06.md` contains the generated report for the 9 target terms listed below.

## Background — the counting chain you must replicate (read these files first)
1. `notes/term-coverage-matrix.csv` — raw hits. Columns: term_normalized, source_slug, line, excerpt, extraction_method (glossary|keyword), has_avoid_marker, has_capitalization_rule. Produced by `scripts/build-coverage-matrix.py` (which also has a keyword-scan blocklist for common words — read it).
2. `scripts/build-glossary-index.py` — consumes the matrix and applies filters before counting sources:
   - pure-navigation-index hits are dropped (DSG/RET glossary-index link noise)
   - keyword-method hits must pass `_looks_definitional()` or they are dropped as incidental
   - the surviving sources become `source_count` in `site/src/data/glossary-index.json`
   - alias resolution: a term matching a published page's alias gets a `commons_slug`
3. `scripts/lint-content.py` W6 block (~lines 162-180) — warns only when `source_count >= 3` AND no `commons_slug` AND slug not in term pages, alias slugs, or `notes/coverage-decisions.yml`.

## What the script must do
`./scripts/diagnose-term-coverage.py <term> [<term> ...] [--report <path>]`

For each term (normalize the same way the pipeline does — reuse/replicate the existing slugify/normalize helpers, do NOT invent a new normalization):

1. **Blocklist check** — is the term (or its components) on build-coverage-matrix.py's keyword-scan blocklist? Report yes/no.
2. **Raw matrix rows** — list every matrix row for the term: source_slug, extraction_method, line, excerpt (truncate excerpt to 80 chars).
3. **Filter trace** — for each row, compute its fate using the SAME logic as build-glossary-index.py (import its functions if importable; otherwise replicate exactly and say so in a comment): KEPT, DROPPED-navigation, DROPPED-not-definitional. Show which `_looks_definitional` criterion passed/failed.
4. **Effective source_count** — distinct surviving source orgs, and the value actually recorded in `site/src/data/glossary-index.json` for cross-check. Flag any mismatch between your recomputation and the JSON.
5. **W6 disposition** — page exists / alias of page (name which page) / coverage decision recorded / under bar (count < 3) / SHOULD HAVE WARNED (≥3, no page/alias/decision — would indicate a W6 bug).
6. **Near-miss summary** — if count is 1-2, name the missing-source gap explicitly (e.g. "2 strong sources: X, Y — needs 1 more").
7. Also check near-form variants: the term with hyphens↔spaces, simple plural/singular, and whether a DIFFERENT matrix term contains it as a substring with glossary-method entries (e.g. "the poor" vs "poor") — list those candidate rows so alias-absorption is visible.

`--report <path>`: write the same output as markdown.

## Run it
After the script works, run:
`./scripts/diagnose-term-coverage.py poor "at-risk" vulnerable "asylum seeker" migrant activist tolerance equality advocate --report notes/term-coverage-diagnosis-2026-06.md`

## Constraints
- Read-only with respect to all existing files: do NOT modify build-coverage-matrix.py, build-glossary-index.py, lint-content.py, the matrix CSV, the glossary JSON, or any content files. New files only: the script + the report.
- NO git commands of any kind (no add/commit/status/diff). Claude reviews and commits.
- Python 3, stdlib only, match the style of the existing scripts/ files.
- Do not run npm or any build/deploy command.
- If something in the existing logic is ambiguous, replicate it conservatively and note the ambiguity in the report header rather than guessing silently.
