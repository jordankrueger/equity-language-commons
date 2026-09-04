# Launch-readiness audit implementation plan

1. Fix glossary generation and add an output-level regression check. Rebuild data and prove the check catches deliberate duplicate, alias, bucket, and key-collision mutations.
2. Group source routes and index rows by organization. Add the shared availability mapper and verify every generated source link resolves.
3. Remove public build-state language and Jordan-name references outside the footer. Exclude stub chapter routes.
4. Add the missing launch basics: canonical/Open Graph metadata, preview noindex behavior, baseline headers, robots.txt, favicon, and sitemap.
5. Run the full local audit: content and quote checks, build, internal/external links, assets, accessibility, dependency audit, security headers, performance, Cloudflare Pages configuration, and repository hygiene.
6. Write evidence and remaining decisions to `notes/launch-readiness-audit-2026-09-04.md`, review the complete diff, and stop before push/deploy or DNS changes.
