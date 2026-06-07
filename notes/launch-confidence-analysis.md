# Launch-confidence analysis — 2026-06-07

Jordan's question: *how do I launch confident this won't embarrass me — especially
in any way that makes it seem like I let AI do everything and didn't check my work?*

**Core answer: don't obscure how the site was built — make "I checked my work"
actually true, visible, and structurally provable.** A disclosed pipeline with
receipts can't be exposed; an obscured one can. For this audience (progressive
comms professionals), disclosed rigor is a differentiator; discovered concealment
is the embarrassment.

## Threat model — where embarrassment could come from

1. **Wrong quote / misattribution found by a source org or reader.** Worst case;
   currently the strongest area. Layer 1 verbatim verification (1,154 checks),
   Layer 2 cross-model semantic audit (~4,900 claims), adversarial verify in the
   writing pipeline. Residuals (documented, not hidden): NAJA quotes ride on OCR;
   a few PARTIAL-confidence entries; 325 Layer 2 "excerpt-insufficient" flags
   skipped under the 2026-06-05 group rule.
2. **AI-sounding prose.** The real exposure as of 2026-06-07. Syntheses and
   audience notes were agent-written across several sessions; no humanizer pass
   has ever run on site content. AI voice alone triggers the "he let AI do
   everything" read even when every fact is right.
3. **Slur/reclamation pages.** (~15 pages: tranny, retarded, negro, cripple,
   hermaphrodite, two-spirit, …) Read most critically by the communities
   concerned; a tone miss here costs the most. Disproportionate human attention
   required.
4. **The "Jordan's synthesis" framing.** The cross-reference layer is presented
   as Jordan's editorial work (CC-BY, his name). If he hasn't read a synthesis
   he's asked about, that IS the embarrassment scenario. Fix = bounded reading,
   not rewriting.
5. **Source orgs surprised by being mirrored.** Conservative fair-use posture is
   documented, but no live contact path yet. A visible corrections path is the
   cheapest credibility signal that exists.

## The launch gate (agreed 2026-06-07, execution order 4 → 3 → 2 → 1)

### Tier 4 — legal/fair-use pass (Claude) — FIRST — ✅ DONE 2026-06-07 (commit b3c56c7)
- [x] Build per-source quote audit: total quotes, total words quoted, longest
      quote, per-org aggregate across all term pages; flag any org where the
      aggregate looks heavy relative to the source's length
- [x] Confirm every source page's host posture matches actual behavior
      (no public hosting of active orgs' content)
- [x] Produce `notes/fair-use-audit.md` for the launch file
      → Outcome: NGC trimmed 41.8%→14.7% of guide quoted, HRC 21.6%→12.9%,
        Sierra 19.2% accepted w/ four-factor rationale; gcjt fabricated-name
        residue fixed in 18 term pages + 4 chapters; Layer 1 stayed green.

### Tier 3 — transparency (Claude builds, Jordan approves) — SECOND — ✅ DONE 2026-06-07 (commit 8ab0f15)
- [x] Methodology/colophon page: how the corpus was assembled; that AI tooling
      did extraction and drafting; that every quote is machine-verified verbatim
      against archived sources; the layered audit; the human editorial review
      protocol; how to report an error
- [x] Per-page "report an error" affordance (footer link is enough at launch)
- [x] Surface per-quote confidence (VERIFIED-ARCHIVED etc.) in the term-page UI
      as a reader-facing trust signal — moved from Tier 2, it's transparency
      → /methodology/ live; footer carries "How this site is built & verified"
        + "Report an error" (mailto hello@); confidence badges already rendered
        in GuidanceCard, no change needed.

### Tier 2 — prose (Claude does, Jordan skims diffs) — THIRD — ✅ DONE 2026-06-07 (commit b294646)
- [x] Humanizer pass over every synthesis, audience note, chapter intro, and
      source About — multiple passes per page (first pass misses synonym
      cycling and evaluative padding)
- [x] Voice-alignment check so 139 pages read like one author
      → Two waves (15 + 6 agents) over 160 files: all 139 term pages, 11
        chapters, 41 sources, 5 site pages. Shared brief at
        notes/tier2-humanizer-brief.md. Bonus catches: 2 "For Jordan's-voice"
        drafting leaks in published prose (brown, urban), a stray tool-call
        artifact (differently-abled), wrong principle count (R&E chapter).
        Lint strict 0/0, Layer 1 quote checks 0 findings. Deployed + verified.

### Tier 1 — Jordan's eyes (after 4/3/2 are done)
- [ ] Read 100% of slur/reclamation pages (~15)
- [ ] Read all 9 chapter intros
- [ ] Read the jew / islam / nation-of-islam cluster
- [ ] Random-sample audit: ~15 randomly drawn term pages, read cold.
      0 substantive errors → defensible "I reviewed this"; ≥1 → widen sample
- [x] Reading vehicle: full-content export in a printable format (single
      PDF/book) — built by Claude after Tiers 4/3/2 land
      → DONE (commit 46d7f5b): scripts/build-print-export.py; current export
        print-export/elc-print-2026-06-07.pdf (766pp) + .html, reading order
        about → methodology → chapters w/ terms → sources. Rebuild after any
        content change.
- [ ] Optional: one trusted outside human sensitivity-reads the Disability +
      slur pages

### Jordan's pre-existing manual items, now launch-blocking
- [ ] Cloudflare Email Routing for hello@equitylanguagecommons.org (corrections path)
- [ ] GitHub Discussion categories (corrections path)
- [ ] CF auto-deploy from GitHub (operational hygiene, not credibility)

## Sequencing rationale

Tier 4 first because it can change content (a heavy-quoted org might need
trims, which the humanizer pass should see in final form). Tier 3 second
because the methodology page's claims must describe the finished process.
Tier 2 third so humanized prose is the version Jordan reads. Tier 1 last,
against a print export, so his review is of the launch candidate — not a
moving target.
