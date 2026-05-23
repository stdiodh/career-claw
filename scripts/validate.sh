#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> Checking Python syntax"
python3 -m py_compile \
  scripts/build-ai-input.py \
  scripts/collect-feeds.py \
  scripts/make-sample-report.py \
  scripts/render-brief.py \
  scripts/send-category-briefs.py \
  scripts/send-discord.py

echo "==> Creating sample Markdown report"
python3 scripts/make-sample-report.py

echo "==> Rendering free category briefs"
python3 scripts/render-brief.py

echo "==> Checking category send dry-run"
python3 scripts/send-category-briefs.py --dry-run

echo "==> Checking required files"
required_files=(
  "reports/sample-daily-news.md"
  "configs/channels.json"
  "configs/sources.json"
  "docs/channels.md"
  "docs/cost-policy.md"
  "refs/categories/ai-news.md"
  "refs/categories/backend-news.md"
  "refs/categories/security-alerts.md"
  "scripts/collect-feeds.py"
  "scripts/render-brief.py"
  "scripts/send-category-briefs.py"
  "scripts/build-ai-input.py"
  ".github/codex/prompts/compact-brief.md"
  ".github/codex/prompts/daily-news.md"
  ".github/workflows/daily-feed.yml"
  ".github/workflows/ai-brief-manual.yml"
  ".github/workflows/daily-news.yml"
)

for file in "${required_files[@]}"; do
  if [ ! -f "${file}" ]; then
    echo "Missing required file: ${file}" >&2
    exit 1
  fi
  echo "Found: ${file}"
done

echo "==> Discord send test"
echo "Automatic Discord sending is intentionally skipped."
echo "To test category delivery, set the DISCORD_WEBHOOK_* variables and run:"
echo "python3 scripts/send-category-briefs.py"
echo "To test legacy single-file delivery, set DISCORD_WEBHOOK_URL and run:"
echo "python3 scripts/send-discord.py reports/sample-daily-news.md"

echo "==> Validation complete"
