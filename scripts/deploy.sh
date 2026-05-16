#!/usr/bin/env bash
# Build + deploy ELC to Cloudflare Pages.
# Used until GitHub auto-deploy is wired via the CF dashboard.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/site"

npm run build

CLOUDFLARE_API_TOKEN="${PERSONAL_CLOUDFLARE_API_TOKEN:?PERSONAL_CLOUDFLARE_API_TOKEN not set}" \
  wrangler pages deploy dist \
    --project-name=equity-language-commons \
    --branch=main \
    --commit-dirty=true
