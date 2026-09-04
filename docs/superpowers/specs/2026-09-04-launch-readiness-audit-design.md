# Equity Language Commons launch-readiness audit

## Verdict

Fix the visible launch problems at their source, not in generated output. The glossary will publish one row per commons page and retain aliases as secondary searchable text. The Sources page will translate its two technical status systems into one reader-facing availability label. The homepage will lose its internal build-status section and personal-name references outside the footer. A launch audit will then check the built site, repository, dependencies, public headers, Cloudflare Pages configuration, accessibility, performance, metadata, links, indexing, and production behavior. The custom-domain DNS flip remains out of scope.

## Scope and success criteria

The work is complete when:

1. No commons term appears more than once as a primary glossary row.
2. Every glossary row is filed under the first character of its displayed primary term.
3. Aliases remain visible and searchable without becoming duplicate rows.
4. Every source remains listed, but each has one of three clear availability labels: Available online, Archived copy available, or Access restricted.
5. The Sources page explains those labels in plain language.
6. The homepage has no Status section and refers to “Synthesis paragraphs,” not “Jordan Krueger’s synthesis.”
7. Jordan Krueger’s name appears in rendered site output only in the footer. This includes contributor metadata and prose labels.
8. Launch checks either pass or produce a short, evidence-backed list of remaining decisions. Safe configuration fixes are included; the custom-domain DNS flip is not.

## Design

### 1. Glossary generation

Reuse: `scripts/build-glossary-index.py`, term frontmatter aliases, `site/src/data/glossary-index.json`, and the current glossary filters.

Add: a canonical-row model in the generated data. Published term pages contribute one primary row keyed by their own slug and displayed with their `term` value. Their aliases attach to that row as a de-duplicated list. Matrix-only terms that do not resolve to a published page continue as independent long-tail rows.

The letter bucket is computed from the primary display value, never the matrix term or alias. The generator will reject duplicate primary rows, duplicate visible primary labels, and rows whose display value does not match their bucket. The glossary template will render aliases beneath the primary label in subdued text that remains part of the indexed page content.

This removes the current failure mode: alias keys such as `deranged`, `psycho`, and `loony` all inherit the display “Crazy,” creating duplicate “Crazy” rows under several letters. The same error creates multiple “Little Person” rows.

### 2. Source availability

Reuse: the existing `host_posture`, `live_status`, and `local_archive` fields. These remain intact because source detail pages and archival policy use them.

Add: one display-only availability mapper on the Sources index:

- Available online: the original source is live and does not require access.
- Archived copy available: the original is offline or returns 404, and the commons has an allowed archive path.
- Access restricted: the original is login-gated or paywalled.

If an offline source has no usable archive, the label becomes “Original unavailable.” This is an error state the audit should surface, not hide. A compact explanation above the list will say that unavailable sources remain listed because they are cited in commons entries and preserve the record of what was reviewed.

The current posture chips (“Private mirror,” “Links out,” “Hosts publicly”) will be removed from the index. Those details remain on each source’s page where they are relevant.

### 3. Homepage and personal-name cleanup

Reuse: the existing homepage structure and footer attribution.

Remove: the complete homepage Status section and its internal phase/stub language.

Change: “Jordan Krueger’s synthesis paragraphs” to “Synthesis paragraphs.” Remove Jordan’s name from other rendered prose and contributor arrays. Keep the copyright attribution in `SiteFooter.astro`. The repository may retain Jordan’s name in non-rendered documentation, authorship history, and Git metadata.

### 4. Launch audit

Reuse: project lint, quote verification, Astro build, Pagefind build, Cloudflare Pages deployment metadata, existing source archives, and the project’s current direct-upload deploy path.

Check and fix, where safe:

- Content correctness: glossary invariants, duplicate routes, stale public copy, broken internal links, dead public links, missing pages, and quote integrity.
- Build and code: strict content lint, production build, generated-data reproducibility, unused code, large assets, accidental source maps, and repository cleanliness.
- Discoverability: unique titles and descriptions, canonical URL behavior, Open Graph basics, sitemap, robots.txt, favicon, and search indexing.
- Accessibility: headings, landmark structure, keyboard use, focus visibility, color contrast, accessible names, and reduced-motion behavior where relevant.
- Performance: HTML/CSS/JS payloads, largest assets, cache headers, compression, render-blocking resources, and representative Lighthouse results.
- Security: HTTPS behavior, response headers, content security policy feasibility, clickjacking protection, referrer policy, MIME sniffing protection, permissions policy, exposed files, dependency audit, and absence of secrets.
- Cloudflare: correct Personal account and Pages project, production branch, deployment status, custom domains, redirects, headers, caching, bot/robots posture, and TLS settings. No DNS record changes and no custom-domain activation.
- Operations: rollback path, deploy reproducibility, error-report contact path, and clean working tree.

Findings fall into three groups: fixed now, launch blocker requiring Jordan’s decision, or post-launch improvement. Only evidence-backed findings are reported.

## Files expected to change

- `scripts/build-glossary-index.py`
- `site/src/pages/glossary/index.astro`
- `site/src/pages/sources/index.astro`
- `site/src/pages/index.astro`
- `site/src/content/terms/*.md` only where rendered contributor/name data must be removed
- The smallest existing test or lint file capable of enforcing glossary invariants; add one small test only if no suitable check exists
- Configuration files only when the audit finds a verified launch problem

Generated glossary and SQLite outputs may change during verification. They will be committed only if the repository already treats them as source-controlled release inputs.

## Verification

1. Run a focused glossary regression check covering duplicate primary rows, alias de-duplication, and letter placement.
2. Rebuild the matrix, glossary index, and SQLite index using the normal order.
3. Run strict content lint and quote verification without changing verified quotations.
4. Run the production Astro/Pagefind build.
5. Inspect representative rendered pages: glossary C and L sections, Sources, homepage, and a term with former contributor metadata.
6. Run the launch checks against local output and the deployed Pages URL.
7. Review the complete diff before commit, push, and deploy only after Jordan authorizes those steps.

## Decisions

- Keep all cited sources on the Sources page.
- Show one reader-facing availability label rather than the two internal status systems.
- Remove the homepage Status section.
- Show one canonical glossary row and place aliases beneath it.
- Remove Jordan’s name from rendered content except the footer.
- Audit and safely fix Cloudflare settings, but do not flip custom-domain DNS.

## Open questions

None. If the audit uncovers a destructive, billing-related, or public-launch action, stop and ask before taking it. The recommended default is to leave it unchanged and report it as a launch decision.
