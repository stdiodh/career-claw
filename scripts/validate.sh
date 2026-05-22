#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> Checking Python syntax"
python3 -m py_compile scripts/send-discord.py

echo "==> Creating sample Markdown report"
python3 scripts/make-sample-report.py

echo "==> Checking required files"
required_files=(
  "reports/sample-daily-news.md"
  ".github/codex/prompts/daily-news.md"
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
if [ -n "${DISCORD_WEBHOOK_URL:-}" ]; then
  echo "DISCORD_WEBHOOK_URL is set."
  echo "Automatic Discord sending is intentionally skipped."
  echo "Run this command explicitly to test delivery:"
  echo "python3 scripts/send-discord.py reports/sample-daily-news.md"
else
  echo "DISCORD_WEBHOOK_URL is not set. Skipping Discord delivery guidance."
  echo "To test delivery later, set DISCORD_WEBHOOK_URL and run:"
  echo "python3 scripts/send-discord.py reports/sample-daily-news.md"
fi

echo "==> Validation complete"
