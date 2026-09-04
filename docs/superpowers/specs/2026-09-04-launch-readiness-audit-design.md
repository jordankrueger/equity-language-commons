# Equity Language Commons launch-readiness audit

## Verdict

Fix the visible launch problems at their source, not in generated output. The glossary will publish one row per commons page and retain aliases as secondary searchable text. The Sources page will translate its two technical status systems into one reader-facing availability label. The homepage will lose its internal build-status section and personal-name references outside the footer. A launch audit will then check the built site, repository, dependencies, public headers, Cloudflare Pages configuration, accessibility, performance, metadata, links, indexing, and production behavior. The custom-domain DNS flip remains out of scope.

## Scope and success criteria

The work is complete when:

1. No commons term appears more than once as a primary glossary row.
2. Every glossary row is filed under the first character of its displayed primary term.
3. Aliases remain visible and searchable without becoming duplicate rows, and retain their own source counts and source pointers.
4. Every cited work remains listed once beneath one organization row, with an accurate reader-facing availability label.
5. The Sources page explains those labels in plain language.
6. The homepage has no Status section and refers to “Synthesis paragraphs,” not “Jordan Krueger’s synthesis.” No rendered page uses internal labels such as stub, planned, draft, or build phase.
7. Jordan Krueger’s name appears in rendered site output only in the footer. This includes contributor metadata and prose labels.
8. Launch checks either pass or produce a short, evidence-backed list of remaining decisions. Safe configuration fixes are included; the custom-domain DNS flip is not.

## Design

### 1. Glossary generation

Reuse: `scripts/build-glossary-index.py`, term frontmatter aliases, `site/src/data/glossary-index.json`, and the current glossary filters.

Add: a canonical-row model in the generated data. Published term pages contribute one primary row keyed by their own slug and displayed with their `term` value. Their aliases attach to that row as de-duplicated objects retaining the alias term, display form, source count, and source pointers. Matrix-only terms that do not resolve to a published page continue as independent long-tail rows.

The letter bucket is computed from the primary display value, never the matrix term or alias. Alphabetic terms must match their A–Z bucket; nonalphabetic terms go in `#`. The generator will exit non-zero on duplicate primary slugs, duplicate visible primary labels, or wrong bucket placement so CI/deploy cannot publish bad output. If two legitimately distinct pages ever share a display label, that is an editorial collision to resolve explicitly rather than silently dropping a row. The glossary template will render aliases beneath the primary label in subdued text that remains part of the indexed page content.

Visible counts will distinguish primary rows from aliases. `stats.total_terms`, coverage data used by W6, and diagnostic inputs retain every matrix term; glossary filter counts describe visible primary rows. The page introduction will say that every corpus term appears either as a primary entry or as an alias beneath one. Alias source details remain expandable beneath the canonical row rather than being discarded or merged into the canonical term's own source count.

This removes the current failure mode: alias keys such as `deranged`, `psycho`, and `loony` all inherit the display “Crazy,” creating duplicate “Crazy” rows under several letters. The same error creates multiple “Little Person” rows.

### 2. Source availability

Reuse: the existing `host_posture`, `live_status`, and `local_archive` fields. These remain intact because source detail pages and archival policy use them.

Add: organization grouping by `org_slug`, with every work listed once beneath its organization. This removes the current duplicate organization rows and gives each work its own availability label. Add a display-only availability mapper derived from `host_posture`, `live_status`, and archive presence together:

- Available online: the original source is live and does not require access.
- Public archive available: the original is offline and the commons is permitted to host its archived copy.
- Reviewed from a reference copy: the original is offline and the commons holds a private verification copy that readers cannot download.
- Access restricted: the original is login-gated or paywalled.
- Original unavailable: the original is offline and no archive is held.

“Public archive available” is emitted only for `host-publicly`; private mirrors never imply reader access. “Original unavailable” is an error state the audit should surface, not hide. A compact explanation above the list will say that unavailable sources remain listed because they are cited in commons entries and preserve the record of what was reviewed.

The current posture chips (“Private mirror,” “Links out,” “Hosts publicly”) will be removed from the index. Those details remain on each source’s page where they are relevant.

### 3. Homepage and personal-name cleanup

Reuse: the existing homepage structure and footer attribution.

Remove: the complete homepage Status section and its internal phase/stub language. Retire the same public build-state vocabulary elsewhere: hide stub sources and chapters from public indexes and navigation, remove planned counts/chips from chapter pages, and remove Phase 3 placeholder copy from source pages. The internal roadmap and frontmatter flags remain available to maintainers.

Change: “Jordan Krueger’s synthesis paragraphs” to “Synthesis paragraphs.” Remove Jordan’s name from other rendered prose and contributor arrays. Rewrite the About-page license sentence as “The original cross-reference layer … is licensed under CC BY 4.0,” with the footer copyright identifying the rights holder. Keep the copyright attribution in `SiteFooter.astro`. The repository may retain Jordan’s name in non-rendered documentation, authorship history, and Git metadata.

### 4. Launch audit

Reuse: project lint, quote verification, Astro build, Pagefind build, Cloudflare Pages deployment metadata, existing source archives, and the project’s current direct-upload deploy path.

Check and fix, where safe:

- Content correctness: glossary invariants, duplicate routes, stale public copy, broken internal links, dead public links, missing pages, and quote integrity.
- Build and code: strict content lint, production build, generated-data reproducibility, unused code, large assets, accidental source maps, and repository cleanliness.
- Discoverability: unique titles and descriptions, canonical URL behavior, Open Graph basics, sitemap, robots.txt, favicon, and search indexing. The unannounced `pages.dev` preview should use `noindex` until the custom domain launches, preventing competing preview URLs from entering search results; the launch procedure must reverse that directive with the DNS/domain activation.
- Accessibility: headings, landmark structure, keyboard use, focus visibility, color contrast, accessible names, and reduced-motion behavior where relevant.
- Performance: HTML/CSS/JS payloads, largest assets, cache headers, compression, render-blocking resources, and representative Lighthouse results.
- Security: HTTPS behavior, response headers, clickjacking protection, referrer policy, MIME sniffing protection, permissions policy, exposed files, dependency audit, and absence of secrets. Content Security Policy is report-only in this pass unless the inline glossary script is moved to a CSP-compatible asset and its interactive behavior is tested; a blocking policy must not be guessed from 200 responses.
- Cloudflare Pages: correct Personal account and Direct Upload project, latest production deployment, custom-domain attachment state, redirects, `_headers`, and caching/compression behavior. Zone-level DNS, TLS, and bot settings are report-only until the custom domain is attached. No DNS record changes and no custom-domain activation.
- Operations: rollback path, deploy reproducibility, error-report contact path, and clean working tree.

Must-pass before launch: no duplicate or misplaced glossary rows; no duplicate source work rows; no public internal-status labels; clean lint/verification/build; working navigation and filters; no broken internal links; no exposed secrets; HTTPS; safe baseline security headers; valid robots/sitemap state; and a verified production deployment. Report-only unless a concrete defect is proven: dependency upgrades, CSP enforcement, Cloudflare zone settings before domain attachment, and performance refinements beyond the current static-site budget. Findings fall into three groups: fixed now, launch blocker requiring Jordan’s decision, or post-launch improvement.

## Files expected to change

- `scripts/build-glossary-index.py`
- `site/src/pages/glossary/index.astro`
- `site/src/pages/sources/index.astro`
- `site/src/pages/index.astro`
- `site/src/pages/chapters/index.astro`
- `site/src/pages/chapters/[slug].astro`
- `site/src/pages/sources/[slug].astro`
- `site/src/content/terms/*.md` only where rendered contributor/name data must be removed
- The smallest existing test or lint file capable of enforcing glossary invariants; add one small test only if no suitable check exists
- `site/public/_headers`, robots/sitemap configuration, or other configuration files only when the audit finds a verified launch problem

Generated glossary and SQLite outputs may change during verification. They will be committed only if the repository already treats them as source-controlled release inputs.

## Verification

1. Run a focused glossary regression check covering duplicate primary rows, preserved alias data, alias de-duplication, and letter placement including the `#` bucket. Reintroduce the current alias-to-display inheritance defect, prove the check fails, then revert the mutation and prove it passes.
2. Rebuild the matrix, glossary index, and SQLite index using the normal order.
3. Run strict content lint and quote verification without changing verified quotations.
4. Run the production Astro/Pagefind build.
5. Run browser assertions against representative rendered pages: glossary C and L sections, Sources, homepage, chapter index/detail, source detail, and a term with former contributor metadata. Assert expected row counts/text and exercise glossary filters from the keyboard.
6. Run the launch checks against local output and the deployed Pages URL.
7. Review the complete diff before commit, push, and deploy only after Jordan authorizes those steps.

## Decisions

- Keep all cited sources on the Sources page.
- Group source works under one organization and show one accurate reader-facing availability label per work rather than the two internal status systems.
- Remove the homepage Status section.
- Show one canonical glossary row and place aliases beneath it.
- Remove Jordan’s name from rendered content except the footer.
- Audit the Direct Upload Pages project and safely fix Pages-level settings, but do not flip custom-domain DNS or change zone-level launch settings.
- Keep the preview host out of search indexes until the custom domain launches; reversing `noindex` is an explicit launch step.

## Open questions

None. If the audit uncovers a destructive, billing-related, or public-launch action, stop and ask before taking it. The recommended default is to leave it unchanged and report it as a launch decision.
