# Content verification system — spec for sign-off

**Status:** SHIPPED 2026-06-04 — all three layers built and run. Layer 1: scripts/verify-content.py (433 checks green; overrides in notes/verification/layer1-verified-overrides.yml). Layer 2: scripts/verify-synthesis-codex.py (91 pages, 3,921 claims; 114 precision fixes applied; reports in notes/verification/). Remaining: Jordan's keep/cite/cut triage of the EXTERNAL summary; optional re-audit of 'excerpt insufficient' claims with bigger bundles.
**Goal:** Every published page is machine-verified: no hallucinated claims, every
quote traceable to its archived source, every link pointing at the right place.

## Why two layers

Most verification is mechanical (does this quote exist in that file? does this
URL resolve?) and shouldn't burn LLM time. The judgment work — "is this synthesis
claim actually supported by the quoted sources?" — needs a model, and it should
be a *different* model from the one that wrote the content, so it doesn't share
the author's blind spots. Claude wrote these pages; Codex audits them.

## Layer 0 — lint gate (SHIPPED 2026-06-04)

`scripts/lint-content.py`, wired into `deploy.sh`. Blocks deploys on authoring
artifacts: `[[wiki-brackets]]`, scaffolder-notes blocks, TODO markers on
non-stub pages, stub-flag/synthesis conflicts, broken internal links. Warns
(pre-launch) on dangling related_terms, >50-word quotes, vestigial categories.
Run `--strict` at launch to promote warnings to failures.

Current standing findings to work off before launch:
- ~60 W2 quotes over the 50-word fair-use margin (worst: 153 words, hispanic/DSG;
  144 + 135 on bipoc). These predate the cleanup-pass rule. Need trimming.
- ~30 W1 dangling related_terms slugs (planned-stub convention — fine pre-launch).
- W3 vestigial `categories` mismatches (field is unrendered; tidy-up only).

## Layer 1 — deterministic verifier (`scripts/verify-content.py`)

Pure-Python, no LLM, no network except URL checks. Run on demand and before
launch; not in every deploy (URL checks are slow and flaky-network-sensitive).

Per guidance entry on every term page:

1. **Quote-in-archive check.** Normalize (curly→straight quotes, collapse
   whitespace, strip markdown emphasis), split the quote on `…`/`...` into
   segments, and require every segment to appear as a substring of the
   normalized `local_archive` file. PDFs use their extracted `.md` sibling;
   if missing, extract on the fly with pdftotext to a temp file (never
   `--force` over committed OCR).
2. **Confidence-label audit.** `VERIFIED-ARCHIVED` + failed quote check =
   FAIL (the label is a lie). `PARTIAL` + passed check = upgrade suggestion.
   `VERIFIED` (web, unarchived) entries get listed for Layer 2 spot-checking.
3. **URL liveness.** HEAD→GET fallback on every `source_url` (same chain
   `enrich-source-pages.py` uses). Dead URL on a `live` source page = FAIL.
4. **Cross-reference integrity.** org_slug must match an existing source page;
   year must match that source page's year (or a version_history entry).

Output: `notes/verification/layer1-report.md` + JSONL with one record per
entry: `{file, org_slug, check, verdict, detail}`.

## Layer 2 — Codex semantic audit (`scripts/verify-synthesis-codex.sh`)

**Auth: ChatGPT OAuth subscription, NOT the OpenAI API.** The Codex CLI is
already authed via `codex login` (credentials in `~/.codex/`, ChatGPT Plus
account). Non-interactive runs use the same session:

```bash
codex exec --sandbox read-only --cd "$REPO_ROOT" "$PROMPT"
```

No `OPENAI_API_KEY` is set in the environment for these runs — if the key were
present, Codex could silently bill the API instead. The wrapper script will
`unset OPENAI_API_KEY` defensively and verify `codex login status` reports the
ChatGPT account before starting.

**Per term page, the harness:**
1. Assembles a context bundle: the term page markdown + the relevant excerpt
   (±40 lines around each quote's location) from each cited archive file.
   Excerpts, not whole guides — keeps each run small and focused.
2. Runs `codex exec` with a fixed audit prompt (below).
3. Parses the JSON verdict; appends to `notes/verification/layer2-verdicts.jsonl`.
4. Batches: ~10 pages per run-session, resumable via a done-list file, so a
   Plus usage cap mid-batch loses nothing.

**Audit prompt (fixed, versioned in the script):**

> /goal Audit one published reference page against its source excerpts and
> return a single JSON object listing every unsupported claim; stop when the
> JSON is emitted.
>
> You are auditing a reference page for hallucinations. You are given the page
> (frontmatter + prose) and excerpts from the primary sources it cites. For
> EVERY factual claim in the synthesis, audience notes, and paraphrases:
> classify as SUPPORTED (follows from the quoted/excerpted material),
> EXTERNAL (a real-world claim not derivable from the sources — e.g. dates,
> coinages, legal facts the author added), or CONTRADICTED (conflicts with
> the source material). For paraphrases, also flag any that misstate the
> source's position. Return JSON:
> `{"page": "<slug>", "claims": [{"text": "...", "verdict": "SUPPORTED|EXTERNAL|CONTRADICTED", "evidence": "..."}]}`
> Do not rewrite the page. Do not treat the page's own assertions as evidence.

**Disposition of verdicts (Jordan reviews the rolled-up report):**
- CONTRADICTED → fix immediately; these are the actual hallucination risk.
- EXTERNAL → triage list. Each gets one of: (a) verify against a live source
  and add a `context_data` citation, (b) keep as editorial knowledge (e.g.,
  "AP dropped illegal immigrant in 2013" — widely known, low risk), or
  (c) cut. Known EXTERNAL claims going in: Census-2010 "Negro" label,
  Carmichael/Hamilton 1967 coinage, UNCF example, Rosa's Law 2010.
- SUPPORTED → done; page gets `verified: 2026-06-XX` noted in the report.

## Cost & cadence

- Layer 1: free, minutes. Re-run after every batch.
- Layer 2: ~94 pages on the Plus subscription. Batched 10 at a time;
  if Plus limits bite, the done-list makes it resumable across days.
- New-batch workflow going forward: lint (automatic) → Layer 1 (same session)
  → Layer 2 only for the new pages (done-list diff).

## Open questions for Jordan

1. Layer 2 model: default Codex model, or pin (e.g. `-m gpt-5.5-codex`)?
   Default is fine unless audits look shallow.
2. Should EXTERNAL claims that survive triage get an inline citation
   convention on the page (footnote-style), or stay uncited as editorial
   voice? Affects ~a dozen pages.
3. The ~60 over-length quotes: trim as part of this verification pass
   (Layer 1 will already be touching every entry), or as a separate
   fair-use pass?
