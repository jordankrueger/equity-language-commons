# Equity Language Commons — site

Astro static site for the Equity Language Commons. Renders the cross-referenced omnibus from markdown content collections defined under `src/content/`.

Project root (instructions, schema, source guides, research notes) is one level up at `../`.

## Local development

```bash
npm install
npm run dev
```

Visit http://localhost:4321/

## Build

```bash
npm run build
```

Static output lands in `dist/`. Deploy target is Cloudflare Pages.

## Content collections

- `src/content/terms/` — one markdown file per term, frontmatter matches schema v0.3 in `../notes/schema.md`
- `src/content/sources/` — one file per source organization (newest edition canonical)
- `src/content/chapters/` — one file per chapter (category browse page)
