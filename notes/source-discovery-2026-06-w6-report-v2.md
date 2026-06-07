# 2026-06-07 source-discovery context - W6 strict lint findings v2

## Extractor changes

Added structured-glossary extractors in `scripts/build-coverage-matrix.py`:

- `religion-stylebook-2026-06`: `## headword` entries, with a 4-line lookahead for prescription/capitalization markers. Metadata/section names are filtered conservatively even though the real section headings in this file are `#` headings. Rebuilt count: 183 glossary terms after per-source dedupe.
- `movement-strategy-center-glossary-2024`: `#### Headword` entries, including bold-wrapped and markdown-linked headwords. The extractor stops before the post-glossary "Terms to Avoid" category tables. Rebuilt count: 108 glossary terms after per-source dedupe.

Skipped structured extractors:

- `18doors-interfaith-glossary-2023`: left as keyword scan. The file is a discussion guide with `####` section prompts (`What do we mean by "Interfaith"?`, `Why don't we say "Non-Jew"?`, `Dos and Don'ts`, policy/self-identification notes), not a reliable headword glossary.
- `picum-words-matter-2017-03`: left as keyword scan. The machine-extracted PDF text interleaves country names, institution headings, translations, and layout fragments; there is no reliable structural headword pattern without fuzzy parsing.

## Run notes

`./scripts/build-coverage-matrix.py`

```text
scanning 34 sources; 117 terms already indexed
  glossary  diversity-style-guide-2023-11: 936 terms
  glossary  hrc-glossary-2023-05: 21 terms
  glossary  movement-strategy-center-glossary-2024: 108 terms
  glossary  ncdj-disability-style-guide-2021: 202 terms
  glossary  nlgja-stylebook-lgbtq-2025-06: 133 terms
  glossary  radicalcopyeditor-trans-style-guide-2017: 26 terms
  glossary  religion-stylebook-2026-06: 183 terms
  glossary  tja-stylebook-2026-01: 169 terms

term universe: 1467 unique terms

wrote notes/term-coverage-matrix.csv (3714 rows)
wrote notes/term-coverage-matrix.md
```

CSV verification with Python's `csv` module:

```text
religion-stylebook-2026-06 183
movement-strategy-center-glossary-2024 108
```

`./scripts/build-glossary-index.py`

```text
wrote site/src/data/glossary-index.json
  total: 1196 | full: 166 | verified-hold: 3 | curated: 970 | listed: 57
  coverage histogram: {'1': 816, '2': 258, '3': 75, '4': 34, '5': 8, '6': 3, '8': 2}
```

`./scripts/lint-content.py --strict`

Strict lint exited nonzero because of W6 warnings only. No `FAIL` lines were present.

```text
WARN  W6 coverage: "accountability" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "black lives matter" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "cultural appropriation" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "culture" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "decolonization" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "differently abled" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "economy" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "equity" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "gender" has 8 sources but no page, alias, or coverage decision
WARN  W6 coverage: "gender identity disorder" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "hermaphrodite" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "implicit bias" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "interfaith" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "nation of islam" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "oppression" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "poverty" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "prejudice" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "privilege" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "racism" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "reverse racism" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "rosh hashanah" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "sex" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "sex change" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "social justice" has 4 sources but no page, alias, or coverage decision
WARN  W6 coverage: "tranny" has 3 sources but no page, alias, or coverage decision
WARN  W6 coverage: "violence" has 5 sources but no page, alias, or coverage decision
WARN  W6 coverage: "white supremacy" has 3 sources but no page, alias, or coverage decision

lint-content: 169 files checked - 0 failure(s), 27 warning(s) [--strict]
```

## Diff vs previous 17-term report

Newly qualified W6 terms:

- Race/social-justice/glossary-core: `accountability`, `black lives matter` already present previously, `cultural appropriation`, `culture`, `decolonization`, `equity`, `implicit bias` already present previously, `oppression`, `prejudice`, `privilege`, `racism`, `reverse racism` already present previously, `social justice`, `violence`, `white supremacy`.
- Economic/class language: `economy`, `poverty`.
- Gender/sex/LGBTQIA+ language: `gender`, `sex`; prior warnings retained for `gender identity disorder`, `hermaphrodite`, `sex change`, `tranny`.
- Religion/interfaith: `nation of islam`, `rosh hashanah`; prior warning retained for `interfaith`.
- Disability: `differently abled` retained from the prior report.

Set comparison:

- New in v2: `accountability`, `cultural appropriation`, `culture`, `decolonization`, `economy`, `equity`, `gender`, `nation of islam`, `oppression`, `poverty`, `prejudice`, `privilege`, `racism`, `rosh hashanah`, `sex`, `social justice`, `violence`, `white supremacy`.
- Still warning from the prior report: `black lives matter`, `differently abled`, `gender identity disorder`, `hermaphrodite`, `implicit bias`, `interfaith`, `reverse racism`, `sex change`, `tranny`.
- No longer in the W6 strict-lint output: `abnormal`, `bathroom bill`, `bigender`, `cripple`, `functional needs`, `limited vision`, `sexual preference`, `trans woman`.

## Spot-check diagnostics

Command:

```text
./scripts/diagnose-term-coverage.py "asylum seeker" migrant poor activist equality tolerance
```

Output summary:

```text
asylum seeker -> asylum seeker
- No raw matrix rows.
- Effective source count: 0.
- W6 disposition: under bar after filters/final pruning.
- Near-form glossary overlap: reporting on asylum seekers (tja-stylebook-2026-01).

migrant -> migrant
- No raw matrix rows.
- Effective source count: 0.
- W6 disposition: under bar after filters/final pruning.
- Near-form glossary overlaps: illegal immigrant, immigrant, undocumented immigrant (diversity-style-guide-2023-11).

poor -> poor
- No raw matrix rows.
- Effective source count: 0.
- Final term-level prune: final short-term prune: 3-4 chars need >=2 sources.
- W6 disposition: under bar after filters/final pruning.

activist -> activist
- Raw matrix rows include 1 kept row and multiple dropped keyword/navigation rows.
- Kept source: color-of-change-black-survivors-styleguide-2022.
- Effective source count: 1.
- glossary-index.json source_count: 1.
- W6 disposition: under bar (count < 3).
- Near-form glossary overlaps: trans activists, trans rights activists (tja-stylebook-2026-01).

equality -> equality
- Raw matrix rows include kept rows from dcfpi-inclusive-language-2017-12 and movement-strategy-center-glossary-2024.
- Multiple keyword hits were dropped as not definitional; the Diversity Style Guide glossary row was dropped as navigation.
- Effective source count: 2.
- glossary-index.json source_count: 2.
- W6 disposition: under bar (count < 3).

tolerance -> tolerance
- Raw matrix rows include kept rows from diversity-style-guide-2023-11 and sierra-club-equity-language-guide-2021.
- Multiple keyword hits were dropped as not definitional.
- Effective source count: 2.
- glossary-index.json source_count: 2.
- W6 disposition: under bar (count < 3).
```
