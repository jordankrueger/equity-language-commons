# Launch audit: 2026-09-04

## Passed

- Strict content lint: 191 files, 0 failures, 0 warnings.
- Production build: 193 static pages; Pagefind indexed all 193.
- Internal links and anchors: 0 failures across the built site.
- Glossary: 1,154 unique visible rows; Crazy appears once under C; Little Person appears once under L; duplicate and wrong-letter mutations fail the permanent check.
- Source links: generated links resolve to organization routes, including canonical-source links.
- Dependencies: Astro 7.3.1 and astro-pagefind 2.0.1; `npm audit` reports 0 vulnerabilities.
- Public copy: the homepage status section is removed; no public planned/stub labels remain; Jordan Krueger appears only in the footer.
- Assets: no production image exceeds 500 KB. The large built files are the glossary HTML and downloadable SQLite index.
- Search metadata: canonical URL, description, Open Graph basics, favicon, and sitemap are present.
- Security headers: MIME sniffing protection, strict referrer policy, frame denial, and restrictive camera/microphone/geolocation permissions are configured in `_headers`.
- Search indexing is enabled, and `robots.txt` points crawlers to the sitemap.
- External citation verification: 1,154 checks completed. The 72 dead-link findings belong to Sierra Club (71 citations sharing one URL) and the UN Martínez Cobo source (1); their source statuses and check dates now reflect that result.

## Launch state

- The custom domain is attached and the proxied apex CNAME points to the Pages project.
- HTTPS, security headers, search, glossary, sources, sitemap, robots, and a representative term page were verified on the apex domain.
- Cloudflare Email Routing MX and SPF records were preserved.
- The repository remains private because its Git history contains copyrighted preservation copies that the website does not publish.
- Keep the canonical custom-domain URL so the Pages preview does not become the preferred search result.

## Cloudflare

- The existing project remains a direct-upload Cloudflare Pages project on the personal account, deployed by the repository workflow or `scripts/deploy.sh`.
- The deployment artifact now includes the security headers, favicon, robots policy, and sitemap.
- Cloudflare domain verification is active. Certificate validation may continue to show pending briefly in the Pages API even though HTTPS is already serving successfully.
