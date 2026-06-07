# Tier 2 humanizer brief (2026-06-07)

Shared instructions for the launch-gate prose pass. Every editing agent follows this exactly.

## Goal

Remove AI-writing tells from ELC's editorial prose so the site reads like it was written by one careful human editor. This is a tell-removal pass, not a personality injection: ELC is reference prose. No invented anecdotes, no first person, no rhetorical questions, no jokes.

## What you may edit (per file type)

**Term pages (`site/src/content/terms/*.md`):**
- Frontmatter `audience_notes[].note` strings ONLY
- Body `## Synthesis` and `## Audience notes` sections

**Chapter pages (`site/src/content/chapters/*.md`):**
- Frontmatter `lede` and `cross_cutting_principles[].body` / `[].title`
- Markdown body after the closing `---`

**Source pages (`site/src/content/sources/*.md`):**
- Markdown body only (About / Access / Version history prose)

**Site pages (`site/src/pages/*.astro`):**
- Visible prose inside the HTML/JSX only. Never touch imports, frontmatter script, props, class names, or component structure.

## What you must NEVER touch

1. `quote:`, `quote_loc:`, `paraphrase:` fields — verification-bound, checked verbatim against archives. Any change breaks Layer 1/2.
2. Any other frontmatter field: slugs, orgs, years, URLs, recommendations, confidence, tags, related_terms, term_slugs, dates, contributors.
3. **Anything inside double quotation marks in prose.** Quoted fragments ("a system of power that structures opportunity") are verbatim source text — including their internal em dashes and `…` ellipses. Rewrite around them, never inside them.
4. Factual content: every claim, attribution, org name, year, page number, and distinction must survive the rewrite intact. If unsure whether something is load-bearing, keep it.

## Patterns to fix (in priority order for this corpus)

1. **Synonym cycling on attribution verbs.** "X frames… Y anchors… Z grounds… W locates… V ties…" — the corpus cycles elegant verbs to avoid repeating "says/defines/recommends." Plain repetition is fine. "Sierra Club says" twice beats one "anchors" + one "locates."
2. **Copula avoidance.** "serves as," "stands as," "functions as," "represents" → "is." "features/boasts" → "has."
3. **Trailing "-ing" analysis clauses.** "…, reflecting the broader shift," "…, underscoring the distinction" → cut or make a plain sentence.
4. **Evaluative padding.** "the cleanest shorthand," "most compactly," "notably," "crucially," "importantly" — cut unless the evaluation IS the point and is attributable.
5. **Rule-of-three lists** assembled for rhythm rather than content. Keep threes only when there really are three things.
6. **Em-dash overuse.** Reduce density; prefer commas, periods, or parentheses. Don't eliminate entirely (occasional em dash is normal); never touch em dashes inside quoted fragments.
7. **Significance inflation.** "a pivotal shift," "marks a turning point," "the evolving landscape" → state the fact and date.
8. **AI vocabulary:** additionally, crucially, delve, foster, highlight (verb), interplay, intricate, key (adj.), landscape (abstract), pivotal, showcase, tapestry, testament, underscore, vibrant, nuanced.
9. **Uniform sentence rhythm.** If every sentence in a paragraph is 20–28 words with the same shape, vary it. Short sentences are allowed.
10. **Negative parallelisms.** "It's not just X; it's Y" → say Y.
11. **Generic wrap-up sentences** that restate the paragraph. Cut them.

## Style anchors (keep these)

- Plain declarative reference prose. Wikipedia-adjacent register but with a clear editorial line where the corpus supports one.
- The no-blame rule: never frame an older guide as outdated/behind. Chronology-neutral framing ("pre-dates," "earlier than") stays exactly as is — do not "fix" it into judgment.
- Sentence-case headings (already the convention).
- Straight quotes in YAML; escaped `\"` inside double-quoted YAML strings; notes stay on one line.

## Process per file

1. Read the whole file.
2. Edit the allowed prose surfaces.
3. Re-read your edited prose top to bottom and ask: "What still reads as AI-generated?" Fix what you find. (First passes reliably miss synonym cycling and evaluative padding — check those twice.)
4. Confirm you touched no quote/paraphrase/frontmatter-data field.

## Report format (final message)

- Files edited, one line each: slug — number of meaningful changes — anything deliberately left alone and why.
- Any file where you found nothing to fix: say so.
- Any place you were tempted to edit a forbidden field: flag it.
