═══════════════════════ PASTE TO CODEX ═══════════════════════

/goal Wire client-side search into the Equity Language Commons Astro site using the
astro-pagefind integration. Done = `npm run build` (run from the `site/` dir) succeeds
and produces a `dist/pagefind/` directory, a new `/search/` page renders a working search
box, a "Search" link appears in the header nav, and running `npm run preview` then querying
a known term (e.g. "latino", "ableism", "tribe") returns results that link to the correct
term pages. Stop when that's verified and committed. Do NOT deploy.

Repo: ~/ClaudeCode/side-hustle/equity-language-commons (private, solo — commit straight to `main`).
First read the full plan: docs/superpowers/plans/2026-05-29-pagefind-search.md — it has the
verified file structure and exact wiring. Follow it. All app files live under `site/`.

TASKS (one slice):
1. cd site && npm install -D astro-pagefind
2. astro.config.mjs — add `import pagefind from "astro-pagefind"` and `integrations: [pagefind()]`.
   Change NOTHING else in that file (keep site, trailingSlash, build.format: "directory",
   and the vite.server.allowedHosts block exactly as-is).
3. src/layouts/BaseLayout.astro — add an optional prop `pagefind?: boolean` and render the
   index marker conditionally on <main>:
     <main class={mainClass} data-pagefind-body={pagefind ? true : undefined}>
   (Astro omits an attribute set to undefined and renders the bare attribute for true.)
4. Pass `pagefind` on the <BaseLayout> opening tag in EXACTLY these four content pages:
     src/pages/terms/[slug].astro      (~line 24)
     src/pages/chapters/[slug].astro   (~line 37)
     src/pages/sources/[slug].astro    (~line 61, multiline tag)
     src/pages/glossary/index.astro    (~line 40, multiline tag)
   Do NOT add it to index, about, contribute, chapters/index, sources/index, or /search.
5. Add `data-pagefind-ignore` to the <header class="site-header"> element in
   src/components/SiteHeader.astro and to the root element of src/components/SiteFooter.astro.
6. Create src/pages/search.astro — a normal page using BaseLayout (title "Search", do NOT pass
   pagefind), an <h1>Search</h1> + one short intro line, and the Search component:
     import Search from "astro-pagefind/components/Search.astro";
   Verify the component's real prop names against the installed package's README/types before
   using them — if they differ from the plan's snippet, follow the installed version. Style it
   minimally so it fits the site (reuse global classes where natural).
7. src/components/SiteHeader.astro — add to the NAV array:
     { href: "/search/", label: "Search", match: /^\/search/ }
8. Verify: `npm run build` succeeds AND `dist/pagefind/` exists. Then `npm run preview`, open
   /search/, query a known term, confirm results link to the right pages.
9. Commit. Suggested split: commit A = tasks 1–5; commit B = tasks 6–8.

OPTIONAL (only if quick + clean, else skip and say so): on terms/[slug].astro add
data-pagefind-filter="chapter:<category>" so the UI can offer a chapter filter.

HARD RULES:
- Edit ONLY files under site/. Do NOT touch scripts/, ROADMAP.md, CLAUDE.md, any
  src/content/** .md files, or anything outside site/.
- Do NOT run ./scripts/deploy.sh, wrangler, or any deploy/publish command. Build + preview only.
- Only dependency change allowed: `npm install -D astro-pagefind` inside site/. No other
  packages, no global/system installs. No --no-verify.
- If astro-pagefind is incompatible with Astro 5 / build.format "directory", or the Search
  component's props differ, or the build fails in a non-trivial way — STOP and report. Do NOT
  silently fall back to raw pagefind, change the config format, or paper over a failure.
- Read-only commands (ls, cat, git status/log/diff, npm run build/preview) are fine without asking.
- If any deviation from the plan isn't trivial, stop and report instead of improvising.

REPORT BACK: git log --oneline of new commits + git diff --stat; confirm dist/pagefind/ exists;
which query you tested and that results were correct; whether you did or skipped the optional
chapter filter; any deviations or surprises.

═══════════════════════════ END ═══════════════════════════
