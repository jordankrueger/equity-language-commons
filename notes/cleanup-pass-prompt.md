# Cleanup-pass prompt (subagent reference)

This document is the standing instruction set for the cleanup pass that
runs after each `scripts/scaffold-term.py` batch. It's referenced from
the main agent's dispatch prompt:

> Read `notes/cleanup-pass-prompt.md` and follow its instructions exactly.
> Apply to these term files: `…`.

Keep this file up to date as new editorial rules emerge. Every rule in
here has a specific incident behind it — don't relax them without
checking the incident first.

---

## What the cleanup pass does

The scaffolder (`scripts/scaffold-term.py`) generates a near-complete
term file from the coverage matrix. The cleanup pass converts that
scaffold into a publishable `guidance:` block.

**Your job, per term file:**

1. Verify each guidance entry against its `local_archive` source. If
   the quoted text isn't in the source, fix the quote. If the source
   doesn't have a real entry on this term (the hit was an incidental
   keyword match), remove the entry.
2. Tighten quotes to ≤50 words (fair-use safety margin). Pick the
   most term-relevant passage; trim ellipses cleanly.
3. Fix mis-classified `recommendation` values. See the SEIU inversion
   rule below — this is the most common error pattern.
4. Write a 1-3 sentence `paraphrase` for each entry that contextualizes
   the source's position without editorializing about the author.
5. Set `confidence: "VERIFIED-ARCHIVED"` when the quote is confirmed
   against a local archived file. Use `"VERIFIED"` for web-extracted
   sources we haven't archived. Use `"PARTIAL"` if the wording is
   approximate.
6. Populate top-level fields: `aliases`, `categories`, `tags`, and
   especially `related_terms` (see the related-terms rule below).
7. Set `last_reviewed: <today>` and `contributors: ["jordan"]`.

**What you do NOT do:**

- Do NOT write the `## Synthesis` section. Leave the placeholder
  comment in place.
- Do NOT write the `audience_notes` block. Leave the placeholder.
- Do NOT remove `stub: true`. Jordan removes that when he reviews
  and approves the synthesis.
- Do NOT modify any file outside the term files listed in your
  dispatch prompt.

---

## Editorial voice rules

These are project-level rules; they apply to every term file in the
commons.

**No blame-leaning language about source-guide authors.** Every
style-guide author was doing the best they could with what was
available at the time. Use neutral chronological framing:
"pre-dates X," "earlier than," "written before Y settled into
practice." Never use:

- "outdated"
- "hasn't aged well"
- "behind"
- "missing the mark"
- Anything else that reads as a judgment of the author or org.

Editorial synthesis about positions, trends, and chronology is
welcome. Editorial judgment of individual authors is not.

**Self-identification is primary** across every term. When a
source's rule touches on personal identification, the rule defers
to how the subject identifies. Reflect this in paraphrases.

---

## Fair use and quotation rules

- **Every direct quote ≤50 words.** This is a safety margin, not the
  actual fair-use ceiling — but staying inside it keeps the commons
  defensible without per-source negotiation.
- **Every quote cites:** `org`, `org_slug`, `year`, `source_url` (or
  null with explanation), `local_archive`, `quote_loc` (a real
  page/section name, not just a line number), and `confidence`.
- **`quote_loc` must be specific.** "Glossary entry" is fine.
  "p. 14, Race and Ethnicity → Preferred Terms for Racial Identity"
  is better. "Line 154" alone is not enough.

---

## Source removal rule

The matrix's keyword-scan extraction sometimes picks up incidental
mentions where a term appears mid-sentence in a discussion of
something else. These are not real sources for the term.

**Remove a guidance entry when:**

- The term only appears inside a list of unrelated entries (e.g.,
  Color of Change mentioning "Native American Journalists' Association"
  in a sources-consulted list is NOT a Color of Change entry on
  "Native American" the term).
- The term appears as part of a longer compound that's actually about
  something else (e.g., "abortion" in "abortion and sterilization,
  economic deprivation" is in a discussion of forced sterilization,
  not a definition of abortion).
- The matrix hit is a Pandoc-style glossary-index link with no
  definition content (e.g., DSG's `- [TERM](url){.glossaryLink}`
  pattern — these are navigation entries, not real definitions).

**Quality over quantity.** A term page with 4 strong sources is
better than 9 noisy ones. The launch threshold is ≥3 strong sources
per commons-style entry; below that, the term belongs in the Glossary
Index long tail, not as a full commons page.

---

## Common error patterns (read these every time)

### 1. SEIU "Correct: X / Don't use: Y" inversion

SEIU's stylebook uses an alphabetical-by-the-avoided-form pattern. The
entry looks like:

> Oriental [Do not use.] Correct: Asian

This appears on the page for **Asian** (or **Asian American**), and
the recommendation is `use` — SEIU is prescribing Asian as the
correct form. The `Do not use` applies to **Oriental**, not Asian.

**Check this every time SEIU's quote contains "[Do not use.] Correct:".**
The recommendation should be `use`, not `avoid`. The avoid lives on a
separate term page for the rejected form.

Same pattern shows up in other style guides with paired prescribe/reject
entries. Verify which side of the pair the current term is on before
setting `recommendation`.

### 2. `related_terms` relation classification

The `RELATION` enum has eight values:

- `alternative-form` — same identity, different spelling/capitalization
- `gendered-form` — explicit gender variant (Latino/Latina)
- `gendered-or-dated-form` — gendered form that's also dated
- `geographic-variant` — same identity, different region
  (Native American / American Indian / First Nations)
- `overlapping-but-distinct` — two terms that can refer to the same
  person but mean somewhat different things (Black ↔ African American;
  gay ↔ queer)
- `subset-identity` — a narrower identity within a broader one
- `umbrella-for` — a broader term that includes the current one
- `related-concept` — catch-all for non-identity-overlap connections
  (prejudices, co-occurring concepts, legal/geographic adjacencies)

**Use `overlapping-but-distinct` only when both terms can describe the
same person.** Don't use it for:

- **Prejudices vs. identities** — homophobia ↔ gay is `related-concept`,
  not overlapping (homophobia is not an identity that overlaps with gay).
- **Grammatical concepts vs. identities** — pronouns ↔ transgender is
  `related-concept` (pronouns is a grammatical concept, not an identity).
- **Legal/geographic entities vs. identities** — reservation ↔ tribe is
  `related-concept` (reservation is a land base, tribe is a political
  entity; they're not overlapping identities).
- **Different axes** — gay ↔ transgender is usually best dropped
  entirely (sexual orientation vs. gender identity). The chapter page
  already lists both. Cross-linking them on the term pages can
  reinforce the very confusion the chapter intro is trying to prevent.

**When in doubt, prefer dropping the cross-link.** The chapter page's
`term_slugs` already groups all chapter terms; redundant cross-links
between every chapter term on every term page is noise, not signal.

### 3. Quote attribution direction

When a source says "X is the preferred term; avoid Y," the current
term page's `recommendation` should reflect the source's position on
the CURRENT term — not on the paired term.

- Page is for "Asian American"; quote says "use Asian" → `use`
- Page is for "Oriental"; same quote → `avoid` (on a different page)

Always check which term the page is about and which term in the
source's quote the recommendation applies to.

---

## Output expectations

After processing a batch of term files, report:

- Per term: number of guidance entries kept vs. scaffolded;
  recommendation distribution; any sources removed and why.
- Any term where you couldn't find ≥3 strong entries (those need
  flagging — Jordan may want to drop them from this batch or look for
  more sources).
- Any quote that didn't verify against the local archive (those need
  manual review).
- Build status from `cd site && npm run build`.

---

## Workflow

1. Read each term file in the batch.
2. For each guidance entry, open the `local_archive` source and find
   the actual term entry.
3. Apply the rules above. Verify each quote, fix recommendations,
   write paraphrases.
4. Audit `related_terms` using the rules in #2 above. Drop weak
   cross-links; reclassify mis-typed ones.
5. Populate top-level fields.
6. Run `cd site && npm run build` to verify schema.
7. Report.

---

## When to update this document

Any time a new error pattern appears in a published term file, add the
pattern + how to detect it to the "Common error patterns" section.
The goal is that every error caught in review becomes a rule the
next subagent batch follows.

Last updated: 2026-05-18 — added §SEIU inversion rule (asian-american
fix) and §related_terms classification rule (LGBTQ+ + reservation fix).
