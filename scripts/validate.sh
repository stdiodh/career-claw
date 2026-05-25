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
  scripts/render-overview.py \
  scripts/send-category-briefs.py \
  scripts/send-discord.py

echo "==> Checking cost guards"
if grep -q "openai/codex-action" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must not use Codex Action." >&2
  exit 1
fi

if grep -q "OPENAI_API_KEY" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must not require OPENAI_API_KEY." >&2
  exit 1
fi

if grep -q -- "--search" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must not use live web search." >&2
  exit 1
fi

if grep -q "schedule:" .github/workflows/daily-news.yml; then
  echo "Cost guard failed: daily-news.yml must stay manual and must not define schedule." >&2
  exit 1
fi

if grep -q -- "--search" .github/workflows/ai-brief-manual.yml; then
  echo "Cost guard failed: AI_LIGHT_MODE must not use live web search." >&2
  exit 1
fi

for workflow in .github/workflows/*.yml; do
  if grep -q "schedule:" "${workflow}" && grep -q -- "--search" "${workflow}"; then
    echo "Cost guard failed: scheduled workflow must not use Codex live web search: ${workflow}" >&2
    exit 1
  fi
done

echo "==> Creating sample Markdown report"
python3 scripts/make-sample-report.py

echo "==> Rendering free category briefs"
python3 scripts/render-brief.py

echo "==> Rendering daily overview"
python3 scripts/render-overview.py

echo "==> Checking brief length and empty-candidate rendering"
python3 - <<'PY'
import json
import tempfile
from pathlib import Path
from subprocess import run

for path in Path("reports/briefs").glob("*.md"):
    limit = 1000 if path.name == "daily-overview.md" else 1200
    size = len(path.read_text(encoding="utf-8"))
    if size > limit:
        raise SystemExit(f"Brief is too long: {path} ({size} chars > {limit})")

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    candidate = root / "empty.json"
    brief = root / "empty.md"
    channels = root / "channels.json"
    candidate.write_text(
        json.dumps({"category": "empty-test", "generated_at": "", "items": []}),
        encoding="utf-8",
    )
    channels.write_text(
        json.dumps(
            {
                "channels": [
                    {
                        "id": "empty-test",
                        "name": "Empty Test",
                        "enabled": True,
                        "candidate_file": str(candidate),
                        "brief_file": str(brief),
                        "webhook_env": "DISCORD_WEBHOOK_EMPTY_TEST",
                        "send_offset_minutes": 0,
                        "max_items": 3,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    run(["python3", "scripts/render-brief.py", "--channels", str(channels)], check=True)
    content = brief.read_text(encoding="utf-8")
    if "오늘 확인된 주요 항목이 없습니다." not in content:
        raise SystemExit("Empty candidate brief did not include the required empty message.")
    if "오늘은 확인할 원본 링크가 없습니다." not in content:
        raise SystemExit("Empty candidate brief did not include the required original-link placeholder.")
PY

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
  "scripts/render-overview.py"
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
