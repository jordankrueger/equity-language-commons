# Task: structured-glossary extractors for the newly ingested sources

## Goal
Add structured-glossary extractors to `scripts/build-coverage-matrix.py` for the new glossary-shaped sources so their headwords enter the candidate term universe, then rebuild the matrix + glossary index and capture the new W6 lint output. Stopping condition: `notes/term-coverage-matrix.csv` contains `glossary`-method rows for `religion-stylebook-2026-06` and `movement-strategy-center-glossary-2024`, the glossary index rebuilds cleanly, and `notes/source-discovery-2026-06-w6-report-v2.md` contains the fresh strict-lint W6 output plus your run notes.

## Background
Read `scripts/build-coverage-matrix.py` first — the extractor pattern is established: a small `extract_<org>()` per source using `_emit_glossary_hits()`, registered in the `EXTRACTORS` dict keyed by source slug. The 6 existing extractors are the model. `split_term_aliases()` already handles comma/“or”-separated headwords. Diagnostic tool available for spot checks: `./scripts/diagnose-term-coverage.py <term>`.

## Extractors to add

1. **`religion-stylebook-2026-06`** (`source-guides/discovered/religion-stylebook-2026-06.md`): entries are `## headword` lines (e.g. `## anti-Semitism`, `## apocalypse, apocalyptic`, `## brit milah or bris`). Real entries start around line 21 — inspect the top of the file and exclude any document-metadata `##` headings (title, section heads) by name or position, the way `_RADICALCOPYEDITOR_META` does. Use a lookahead of a few lines so AVOID_PAT/CAP_PAT see the definition body. Expect ~185 entries.

2. **`movement-strategy-center-glossary-2024`** (`source-guides/discovered/movement-strategy-center-glossary-2024.md`): entries are `#### Headword` lines, sometimes bold-wrapped (`#### **Afro-Latinx**`). One regex should handle both; strip the `**`. Exclude non-entry `####` headings if any exist. Expect ~106 entries.

3. **`18doors-interfaith-glossary-2023`** and **`picum-words-matter-2017-03`**: inspect both files. Add an extractor ONLY if there is a reliable structural headword pattern (18Doors looks like DO/DON'T narrative guidance, not a headword glossary — if so, leave it keyword-scan and say why in the report). Do not force a fuzzy extractor; a wrong universe entry is worse than a missing one.

## After the extractors work

Run, in order, and capture stderr/stdout summaries in the report:
1. `./scripts/build-coverage-matrix.py`
2. `./scripts/build-glossary-index.py`
3. `./scripts/lint-content.py --strict` — expect NEW W6 warnings (that is the point); a nonzero exit from lint due to W6 warnings is success, not failure. Any FAIL line is a real problem — report it and stop.

Write `notes/source-discovery-2026-06-w6-report-v2.md` containing:
- which extractors were added, entry counts per source, which were skipped and why
- the full new W6 warning list
- a diff summary vs the 17 terms in `notes/source-discovery-2026-06-w6-report.md` (newly-qualified terms, by chapter area where obvious)
- spot-check output of `./scripts/diagnose-term-coverage.py "asylum seeker" migrant poor activist equality tolerance` after the rebuild

## Constraints
- Files you may modify: `scripts/build-coverage-matrix.py` (additive — new extractor functions + EXTRACTORS entries only; do not change existing extractors, filters, or the keyword scan), plus the regenerated artifacts those scripts own (`notes/term-coverage-matrix.csv`, `notes/term-coverage-matrix.md`, `site/src/data/glossary-index.json`).
- New files only otherwise (the v2 report).
- Do NOT edit any content files (terms/sources/chapters), lint-content.py, build-glossary-index.py, or coverage-decisions.yml.
- NO git commands of any kind. No npm, no build, no deploy.
- Python 3, stdlib only, match existing style.
- If a file's format is ambiguous, be conservative and document the ambiguity in the report rather than guessing silently.
