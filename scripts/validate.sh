#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> Checking Python syntax"
python3 -m py_compile \
  scripts/collect-kr-feeds.py \
  scripts/select-ps-problem.py \
  scripts/update-ps-progress.py \
  scripts/send-discord.py \
  scripts/validate-career-feed-brief.py

echo "==> Checking shell and workflow syntax"
bash -n scripts/validate.sh
if command -v ruby >/dev/null 2>&1; then
  ruby -e 'require "yaml"; ARGV.each { |path| YAML.load_file(path) }' .github/workflows/*.yml
else
  echo "Warning: ruby not found; skipping workflow YAML parse check." >&2
fi

echo "==> Checking required files"
required_files=(
  ".github/workflows/kr-tech-daily.yml"
  ".github/workflows/kr-backend-career-weekly.yml"
  ".github/workflows/mark-ps-solved.yml"
  ".github/codex/prompts/kr-tech-daily-brief.md"
  ".github/codex/prompts/kr-backend-career-weekly.md"
  "configs/audience-profile.json"
  "configs/kr-sources.json"
  "configs/backend-practical-knowledge-curriculum.json"
  "configs/company-career-watchlist.json"
  "configs/oss-repositories.json"
  "configs/programmers-ps-curriculum.json"
  "data/ps-progress.json"
  "scripts/collect-kr-feeds.py"
  "scripts/select-ps-problem.py"
  "scripts/update-ps-progress.py"
  "scripts/send-discord.py"
  "scripts/validate-career-feed-brief.py"
  "tests/fixtures/kr-tech-daily-valid.md"
  "tests/fixtures/kr-backend-career-weekly-valid.md"
)

for file in "${required_files[@]}"; do
  test -f "${file}"
done

workflow_count="$(find .github/workflows -maxdepth 1 -type f | wc -l | tr -d ' ')"
prompt_count="$(find .github/codex/prompts -maxdepth 1 -type f | wc -l | tr -d ' ')"
if [ "${workflow_count}" != "3" ]; then
  echo "Expected exactly 3 workflow files, found ${workflow_count}." >&2
  exit 1
fi
if [ "${prompt_count}" != "2" ]; then
  echo "Expected exactly 2 prompt files, found ${prompt_count}." >&2
  exit 1
fi

echo "==> Checking collector dry-runs"
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run

echo "==> Checking Markdown fixtures"
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career

echo "==> Checking PS progress status"
python3 scripts/update-ps-progress.py --status >/dev/null

echo "==> Checking current route references"
if ! grep -q "DISCORD_WEBHOOK_KR_TECH_DAILY" .github/workflows/kr-tech-daily.yml; then
  echo "kr-tech-daily.yml must use DISCORD_WEBHOOK_KR_TECH_DAILY." >&2
  exit 1
fi
if ! grep -q "DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY" .github/workflows/kr-backend-career-weekly.yml; then
  echo "kr-backend-career-weekly.yml must use DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY." >&2
  exit 1
fi

blocked_terms=(
  "leg""acy"
  "Leg""acy"
  "FREE_""MODE"
  "AI_LIGHT_""MODE"
  "AI_SEARCH_""MODE"
  "KR_""PRE""MIUM_""MODE"
  "kr-""pre""mium"
  "KR ""Pre""mium"
  "Daily Korea ""Pre""mium"
  "daily-""feed"
  "daily-""news"
  "ai-brief-""manual"
  "compact-""brief"
  "validate-kr-""pre""mium-brief"
  "collect-""feeds"
  "render-""overview"
  "render-""brief"
  "send-category-""briefs"
  "make-sample-""report"
  "DISCORD_WEBHOOK_KR_""PRE""MIUM_""BRIEF"
  "DISCORD_WEBHOOK_DAILY_""OVERVIEW"
  "DISCORD_WEBHOOK_AI_""NEWS"
  "DISCORD_WEBHOOK_BACKEND_""NEWS"
  "DISCORD_WEBHOOK_SECURITY_""ALERTS"
  "DISCORD_WEBHOOK_BACKEND_""TECH"
  "DISCORD_WEBHOOK_JOB_""FEED"
  "무료 ""RSS"
  "수동 ""백업"
  "manual ""backup"
)

blocked_pattern=""
for term in "${blocked_terms[@]}"; do
  if [ -z "${blocked_pattern}" ]; then
    blocked_pattern="${term}"
  else
    blocked_pattern="${blocked_pattern}|${term}"
  fi
done

if rg -n "${blocked_pattern}" .github scripts configs docs README.md .env.example tests AGENTS.md .gitignore; then
  echo "Retired route references remain." >&2
  exit 1
fi

echo "==> Validation complete"
