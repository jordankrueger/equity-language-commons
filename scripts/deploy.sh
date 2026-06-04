#!/usr/bin/env bash
# Build + deploy ELC to Cloudflare Pages.
# Used until GitHub auto-deploy is wired via the CF dashboard.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Content lint — blocks the deploy on authoring artifacts / broken links.
"$PROJECT_ROOT/scripts/lint-content.py"

# Refresh derived data first — order matters: matrix → glossary → sqlite.
"$PROJECT_ROOT/scripts/build-coverage-matrix.py" >/dev/null
"$PROJECT_ROOT/scripts/build-glossary-index.py"
"$PROJECT_ROOT/scripts/build-sqlite-index.py"

cd "$PROJECT_ROOT/site"

npm run build

CLOUDFLARE_API_TOKEN="${PERSONAL_CLOUDFLARE_API_TOKEN:?PERSONAL_CLOUDFLARE_API_TOKEN not set}" \
  wrangler pages deploy dist \
    --project-name=equity-language-commons \
    --branch=main \
    --commit-dirty=true
