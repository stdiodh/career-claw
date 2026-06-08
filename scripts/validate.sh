#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

expect_fail() {
  if "$@"; then
    echo "Expected command to fail: $*" >&2
    exit 1
  fi
}

echo "==> Checking Python syntax"
python3 -m py_compile \
  scripts/build-daily-news-shortlist.py \
  scripts/check-doc-format.py \
  scripts/check-workflow-schedules.py \
  scripts/collect-kr-feeds.py \
  scripts/evaluate-news-daily-quality.py \
  scripts/estimate-prompt-budget.py \
  scripts/render-weekly-career-site-radar.py \
  scripts/select-ps-problem.py \
  scripts/send-discord.py \
  scripts/should-run-now.py \
  scripts/update-oss-progress.py \
  scripts/update-ps-progress.py \
  scripts/validate-career-feed-brief.py \
  scripts/write-news-daily-run-summary.py

echo "==> Checking current workflows"
test -f .github/workflows/kr-tech-daily.yml
test -f .github/workflows/kr-tech-news-daily.yml
test -f .github/workflows/kr-backend-career-weekly.yml
test -f .github/workflows/mark-ps-solved.yml

echo "==> Checking document formatting"
python3 scripts/check-doc-format.py

removed_workflows=(
  ".github/workflows/ai-brief-""manual.yml"
  ".github/workflows/daily-""feed.yml"
  ".github/workflows/daily-""news.yml"
  ".github/workflows/kr-""pre""mium-brief.yml"
)

for file in "${removed_workflows[@]}"; do
  test ! -f "${file}"
done

workflow_count="$(find .github/workflows -maxdepth 1 -type f | wc -l | tr -d ' ')"
if [ "${workflow_count}" != "4" ]; then
  echo "Expected exactly 4 workflow files, found ${workflow_count}." >&2
  exit 1
fi

echo "==> Checking workflow versions and schedules"
grep -q 'uses: actions/checkout@v5' .github/workflows/kr-tech-daily.yml
grep -q 'uses: actions/setup-python@v6' .github/workflows/kr-tech-daily.yml
grep -q 'uses: actions/upload-artifact@v6' .github/workflows/kr-tech-daily.yml
grep -q 'cron: "5,35 \* \* \* \*"' .github/workflows/kr-tech-daily.yml
if grep -q 'timezone: "Asia/Seoul"' .github/workflows/kr-tech-daily.yml; then
  echo "Backend Daily workflow should use runtime timezone variables, not schedule timezone." >&2
  exit 1
fi
grep -q 'workflow_dispatch:' .github/workflows/kr-tech-daily.yml
grep -q 'dry_run:' .github/workflows/kr-tech-daily.yml
grep -q 'force_send:' .github/workflows/kr-tech-daily.yml
grep -q 'Check runtime schedule' .github/workflows/kr-tech-daily.yml
grep -q 'should-run-now.py --workflow backend_daily' .github/workflows/kr-tech-daily.yml
grep -q 'CAREER_FEED_TIMEZONE' .github/workflows/kr-tech-daily.yml
grep -q 'CAREER_FEED_BACKEND_DAILY_TIME' .github/workflows/kr-tech-daily.yml
grep -q 'CAREER_FEED_OSS_RECENT_DAYS' .github/workflows/kr-tech-daily.yml
grep -q 'CAREER_FEED_DISCORD_DELIVERY_ENABLED' .github/workflows/kr-tech-daily.yml
grep -q 'discord_delivery_disabled' .github/workflows/kr-tech-daily.yml
grep -q 'contents: write' .github/workflows/kr-tech-daily.yml
grep -q 'actions: read' .github/workflows/kr-tech-daily.yml
grep -q 'persist-credentials: true' .github/workflows/kr-tech-daily.yml
grep -q 'timeout-minutes: 75' .github/workflows/kr-tech-daily.yml
grep -q 'DISCORD_WEBHOOK_KR_TECH_DAILY' .github/workflows/kr-tech-daily.yml
grep -q 'collect-kr-feeds.py --mode daily-backend' .github/workflows/kr-tech-daily.yml
if grep -q 'collect-kr-feeds.py --mode daily-tech' .github/workflows/kr-tech-daily.yml; then
  echo "Backend Daily workflow must not use --mode daily-tech." >&2
  exit 1
fi
grep -q -- '--type daily-tech' .github/workflows/kr-tech-daily.yml
grep -q 'career-feed-backend-sent-' .github/workflows/kr-tech-daily.yml
grep -q 'actions/cache/restore@v5' .github/workflows/kr-tech-daily.yml
grep -q 'actions/cache/save@v5' .github/workflows/kr-tech-daily.yml
grep -q 'group: career-feed-backend-daily-${{ github.ref }}' .github/workflows/kr-tech-daily.yml
grep -q 'Wait until configured Backend Daily send time' .github/workflows/kr-tech-daily.yml
grep -q "if: github.event_name == 'schedule' && steps.delivery.outputs.should_send == 'true'" .github/workflows/kr-tech-daily.yml
grep -q 'target_epoch="$(TZ="${RUNTIME_TIMEZONE}" date -d "${RUNTIME_LOCAL_DATE} ${TARGET_TIME}:00" +%s)"' .github/workflows/kr-tech-daily.yml
grep -q 'sent_at_local=' .github/workflows/kr-tech-daily.yml
grep -q 'backend-daily-run-summary.json' .github/workflows/kr-tech-daily.yml
grep -q 'reports/candidates/cs-core-daily-topic.json' .github/workflows/kr-tech-daily.yml
grep -q 'reports/candidates/backend-term-daily.json' .github/workflows/kr-tech-daily.yml
grep -q 'DISCORD_WEBHOOK_CAREER_FEED_OPS' .github/workflows/kr-tech-daily.yml
grep -q 'if: always()' .github/workflows/kr-tech-daily.yml
grep -q 'reports/ops/\*.json' .github/workflows/kr-tech-daily.yml
grep -q 'reports/ops/\*.md' .github/workflows/kr-tech-daily.yml
grep -q 'retention-days: 14' .github/workflows/kr-tech-daily.yml
grep -q 'Commit Programmers assignment progress' .github/workflows/kr-tech-daily.yml
grep -q 'data/ps-progress.json' .github/workflows/kr-tech-daily.yml
grep -q 'data/spring-jvm-blog-topic-progress.json' .github/workflows/kr-tech-daily.yml
grep -q 'git push' .github/workflows/kr-tech-daily.yml
grep -q 'commit-ps-progress' .github/workflows/kr-tech-daily.yml
grep -q 'ps_progress_commit_attempted' .github/workflows/kr-tech-daily.yml
grep -q 'ps_progress_commit_success' .github/workflows/kr-tech-daily.yml
grep -q 'oss_safe_candidate_count' .github/workflows/kr-tech-daily.yml
grep -q 'oss_filtered_out_count' .github/workflows/kr-tech-daily.yml
grep -q 'oss_source_errors_count' .github/workflows/kr-tech-daily.yml
grep -q 'selected_oss_issue_url' .github/workflows/kr-tech-daily.yml
grep -q 'OSS 후보 상태' .github/workflows/kr-tech-daily.yml
grep -q 'CAREER_FEED_OSS_RECENT_DAYS: ${{ vars.CAREER_FEED_OSS_RECENT_DAYS }}' .github/workflows/kr-tech-daily.yml
grep -q 'backend-daily-validation-report.md' .github/workflows/kr-tech-daily.yml
grep -q 'cat "${validation_report}" >> "${GITHUB_STEP_SUMMARY}"' .github/workflows/kr-tech-daily.yml
grep -q 'validator error: ${validation_error}' .github/workflows/kr-tech-daily.yml
if grep -q 'DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY\|kr-dev-ai-news.json\|kr-ai-tech-news.json' .github/workflows/kr-tech-daily.yml; then
  echo "Backend Daily workflow must not use the news webhook or news candidate files." >&2
  exit 1
fi

grep -q 'uses: actions/checkout@v5' .github/workflows/kr-tech-news-daily.yml
grep -q 'uses: actions/setup-python@v6' .github/workflows/kr-tech-news-daily.yml
grep -q 'uses: actions/upload-artifact@v6' .github/workflows/kr-tech-news-daily.yml
grep -q 'cron: "5,35 \* \* \* \*"' .github/workflows/kr-tech-news-daily.yml
if grep -q 'timezone: "Asia/Seoul"' .github/workflows/kr-tech-news-daily.yml; then
  echo "News Daily workflow should use runtime timezone variables, not schedule timezone." >&2
  exit 1
fi
grep -q 'workflow_dispatch:' .github/workflows/kr-tech-news-daily.yml
grep -q 'dry_run:' .github/workflows/kr-tech-news-daily.yml
grep -q 'force_send:' .github/workflows/kr-tech-news-daily.yml
grep -q 'Check runtime schedule' .github/workflows/kr-tech-news-daily.yml
grep -q 'should-run-now.py --workflow news_daily' .github/workflows/kr-tech-news-daily.yml
grep -q 'CAREER_FEED_TIMEZONE' .github/workflows/kr-tech-news-daily.yml
grep -q 'CAREER_FEED_NEWS_DAILY_TIME' .github/workflows/kr-tech-news-daily.yml
grep -q 'CAREER_FEED_OSS_RECENT_DAYS' .github/workflows/kr-tech-news-daily.yml
grep -q 'CAREER_FEED_DISCORD_DELIVERY_ENABLED' .github/workflows/kr-tech-news-daily.yml
grep -q 'discord_delivery_disabled' .github/workflows/kr-tech-news-daily.yml
grep -q 'contents: read' .github/workflows/kr-tech-news-daily.yml
if grep -q 'contents: write' .github/workflows/kr-tech-news-daily.yml; then
  echo "News Daily workflow must not request contents: write." >&2
  exit 1
fi
grep -q 'actions: read' .github/workflows/kr-tech-news-daily.yml
grep -q 'timeout-minutes: 75' .github/workflows/kr-tech-news-daily.yml
grep -q 'DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY' .github/workflows/kr-tech-news-daily.yml
grep -q 'collect-kr-feeds.py --mode daily-news' .github/workflows/kr-tech-news-daily.yml
grep -q 'build-daily-news-shortlist.py' .github/workflows/kr-tech-news-daily.yml
grep -q 'estimate-prompt-budget.py' .github/workflows/kr-tech-news-daily.yml
grep -q 'evaluate-news-daily-quality.py' .github/workflows/kr-tech-news-daily.yml
grep -q 'kr-tech-news-shortlist.json' .github/workflows/kr-tech-news-daily.yml
grep -q 'news-daily-token-budget.json' scripts/write-news-daily-run-summary.py
grep -q 'news-daily-quality-report.json' scripts/write-news-daily-run-summary.py
grep -q -- '--type daily-news' .github/workflows/kr-tech-news-daily.yml
grep -q 'career-feed-news-sent-' .github/workflows/kr-tech-news-daily.yml
grep -q 'actions/cache/restore@v5' .github/workflows/kr-tech-news-daily.yml
grep -q 'actions/cache/save@v5' .github/workflows/kr-tech-news-daily.yml
if grep -Eq 'actions/cache(/[^@[:space:]]*)?@v4' .github/workflows/*.yml; then
  echo "GitHub Actions cache v4 usage must not remain." >&2
  exit 1
fi
grep -q 'group: career-feed-news-daily-${{ github.ref }}' .github/workflows/kr-tech-news-daily.yml
grep -q 'Wait until configured News Daily send time' .github/workflows/kr-tech-news-daily.yml
grep -q "if: github.event_name == 'schedule' && steps.delivery.outputs.should_send == 'true'" .github/workflows/kr-tech-news-daily.yml
grep -q 'target_epoch="$(TZ="${RUNTIME_TIMEZONE}" date -d "${RUNTIME_LOCAL_DATE} ${TARGET_TIME}:00" +%s)"' .github/workflows/kr-tech-news-daily.yml
grep -q 'sent_at_local=' .github/workflows/kr-tech-news-daily.yml
grep -q 'news-daily-run-summary.json' .github/workflows/kr-tech-news-daily.yml
grep -q 'news-daily-validation-report.md' .github/workflows/kr-tech-news-daily.yml
grep -q 'cat "${validation_report}" >> "${GITHUB_STEP_SUMMARY}"' .github/workflows/kr-tech-news-daily.yml
grep -q 'validator error: ${validation_error}' .github/workflows/kr-tech-news-daily.yml
grep -q 'DISCORD_WEBHOOK_CAREER_FEED_OPS' .github/workflows/kr-tech-news-daily.yml
grep -q 'if: always()' .github/workflows/kr-tech-news-daily.yml
grep -q 'reports/ops/\*.json' .github/workflows/kr-tech-news-daily.yml
grep -q 'reports/ops/\*.md' .github/workflows/kr-tech-news-daily.yml
grep -q 'raw_candidate_count_total' scripts/write-news-daily-run-summary.py
grep -q 'write-news-daily-run-summary.py' .github/workflows/kr-tech-news-daily.yml
grep -q 'tech_selected_count' scripts/write-news-daily-run-summary.py
grep -q 'investment_selected_count' scripts/write-news-daily-run-summary.py
grep -q 'bridge_present' scripts/write-news-daily-run-summary.py
grep -q 'growth_score' scripts/write-news-daily-run-summary.py
grep -q 'growth_action_present' scripts/write-news-daily-run-summary.py
grep -q 'quality_score' scripts/write-news-daily-run-summary.py
grep -q 'quality_recommendation' scripts/write-news-daily-run-summary.py
grep -q 'target_ratio_met' scripts/write-news-daily-run-summary.py
grep -q 'growth_action_quality' scripts/write-news-daily-run-summary.py
grep -q 'investment_advice_risk' scripts/write-news-daily-run-summary.py
grep -q 'price_move_only_risk' scripts/write-news-daily-run-summary.py
grep -q 'estimated_prompt_tokens_rough' scripts/write-news-daily-run-summary.py
grep -q 'retention-days: 14' .github/workflows/kr-tech-news-daily.yml
if grep -q 'DISCORD_WEBHOOK_KR_TECH_DAILY' .github/workflows/kr-tech-news-daily.yml; then
  echo "News Daily workflow must not use the Backend Daily webhook." >&2
  exit 1
fi
if grep -q 'data/ps-progress.json\|Commit Programmers assignment progress\|git push' .github/workflows/kr-tech-news-daily.yml; then
  echo "News Daily workflow must not commit PS progress." >&2
  exit 1
fi

grep -q 'uses: actions/checkout@v5' .github/workflows/kr-backend-career-weekly.yml
grep -q 'uses: actions/setup-python@v6' .github/workflows/kr-backend-career-weekly.yml
grep -q 'uses: actions/upload-artifact@v6' .github/workflows/kr-backend-career-weekly.yml
grep -q 'contents: read' .github/workflows/kr-backend-career-weekly.yml
grep -q 'cron: "5,35 \* \* \* \*"' .github/workflows/kr-backend-career-weekly.yml
grep -q 'workflow_dispatch:' .github/workflows/kr-backend-career-weekly.yml
grep -q 'send_to_discord:' .github/workflows/kr-backend-career-weekly.yml
grep -q 'Check runtime schedule' .github/workflows/kr-backend-career-weekly.yml
grep -q 'should-run-now.py --workflow career_weekly' .github/workflows/kr-backend-career-weekly.yml
grep -q 'CAREER_FEED_CAREER_WEEKLY_DAY' .github/workflows/kr-backend-career-weekly.yml
grep -q 'CAREER_FEED_CAREER_WEEKLY_TIME' .github/workflows/kr-backend-career-weekly.yml
grep -q 'CAREER_FEED_DISCORD_DELIVERY_ENABLED' .github/workflows/kr-backend-career-weekly.yml
grep -q 'manual_delivery_disabled' .github/workflows/kr-backend-career-weekly.yml
grep -q 'discord_delivery_disabled' .github/workflows/kr-backend-career-weekly.yml
grep -q 'render-weekly-career-site-radar.py' .github/workflows/kr-backend-career-weekly.yml
if grep -q 'openai/codex-action\|OPENAI_API_KEY\|NAVER_CLIENT_ID\|NAVER_CLIENT_SECRET\|git commit' .github/workflows/kr-backend-career-weekly.yml; then
  echo "Weekly site radar workflow must not use OpenAI, Naver, or cache commits." >&2
  exit 1
fi

grep -q 'uses: actions/checkout@v5' .github/workflows/mark-ps-solved.yml
grep -q 'uses: actions/setup-python@v6' .github/workflows/mark-ps-solved.yml
if grep -q 'schedule:' .github/workflows/mark-ps-solved.yml; then
  echo "mark-ps-solved.yml must not define a schedule." >&2
  exit 1
fi

echo "==> Checking current prompts"
test -f .github/codex/prompts/kr-tech-daily-brief.md
test -f .github/codex/prompts/kr-tech-news-daily.md
test ! -f .github/codex/prompts/kr-backend-career-weekly.md

removed_prompts=(
  ".github/codex/prompts/compact-""brief.md"
  ".github/codex/prompts/daily-""news.md"
  ".github/codex/prompts/kr-""pre""mium-brief.md"
)

for file in "${removed_prompts[@]}"; do
  test ! -f "${file}"
done

prompt_count="$(find .github/codex/prompts -maxdepth 1 -type f | wc -l | tr -d ' ')"
if [ "${prompt_count}" != "2" ]; then
  echo "Expected exactly 2 prompt files, found ${prompt_count}." >&2
  exit 1
fi

if grep -Eq 'reports/candidates/kr-dev-ai-news.json|reports/candidates/kr-ai-tech-news.json|## [0-9]+\. 한국 최신 개발/AI 뉴스|한국 최신 개발/AI 뉴스 섹션' .github/codex/prompts/kr-tech-daily-brief.md; then
  echo "Backend Daily prompt must not include news candidate inputs or a news output section." >&2
  exit 1
fi
grep -q 'reports/candidates/cs-core-daily-topic.json' .github/codex/prompts/kr-tech-daily-brief.md
grep -q 'reports/candidates/backend-term-daily.json' .github/codex/prompts/kr-tech-daily-brief.md
grep -q '오늘의 백엔드 실무 충전' .github/codex/prompts/kr-tech-daily-brief.md
grep -q 'CS Core 연결' .github/codex/prompts/kr-tech-daily-brief.md
grep -q '오늘의 백엔드 용어' .github/codex/prompts/kr-tech-daily-brief.md
grep -q '기술 블로그 제목 후보' .github/codex/prompts/kr-tech-daily-brief.md
grep -q 'PAAR 글 목차' .github/codex/prompts/kr-tech-daily-brief.md
grep -q '고정 커리큘럼' .github/codex/prompts/kr-tech-daily-brief.md
if ! grep -Eq '3(~|-)5개' .github/codex/prompts/kr-tech-news-daily.md; then
  echo "News Daily prompt must include the 3~5개 output rule." >&2
  exit 1
fi
grep -q 'reports/candidates/kr-tech-news-shortlist.json' .github/codex/prompts/kr-tech-news-daily.md
grep -q 'Tech & Investment Daily' .github/codex/prompts/kr-tech-news-daily.md
grep -q '주식/투자 이야기' .github/codex/prompts/kr-tech-news-daily.md

echo "==> Checking workflow schedules"
python3 scripts/check-workflow-schedules.py

echo "==> Checking removed scripts"
removed_scripts=(
  "scripts/build-ai-input.py"
  "scripts/collect-""feeds.py"
  "scripts/make-sample-""report.py"
  "scripts/render-""brief.py"
  "scripts/render-""overview.py"
  "scripts/send-category-""briefs.py"
  "scripts/validate-kr-""pre""mium-brief.py"
)

for file in "${removed_scripts[@]}"; do
  test ! -f "${file}"
done

echo "==> Checking required files"
required_files=(
  "CHANGELOG.md"
  "CONTRIBUTING.md"
  "SECURITY.md"
  "SUPPORT.md"
  "configs/audience-profile.json"
  "configs/kr-sources.json"
  "configs/backend-practical-knowledge-curriculum.json"
  "configs/backend-core-cs-curriculum.json"
  "configs/backend-terms-glossary.json"
  "configs/company-career-watchlist.json"
  "configs/weekly-career-site-radar.json"
  "configs/oss-repositories.json"
  "configs/programmers-ps-curriculum.json"
  "data/oss-progress.json"
  "data/ps-progress.json"
  "data/spring-jvm-blog-topic-progress.json"
  "docs/archive/README.md"
  "docs/archive/legacy-inventory.md"
  "docs/README.md"
  "docs/operations/backend-growth-curriculum.md"
  "docs/project/contributor-tasks.md"
  "docs/operations/daily-growth-ops.md"
  "docs/policies/daily-spring-jvm-blog-topic-policy.md"
  "docs/getting-started/fork-setup.md"
  "docs/policies/oss-candidate-policy.md"
  "docs/project/release-checklist.md"
  "docs/release-notes/v0.1.0.md"
  "docs/project/roadmap.md"
  "docs/getting-started/runtime-configuration.md"
  "docs/getting-started/sample-output.md"
  ".github/pull_request_template.md"
  ".github/ISSUE_TEMPLATE/bug-report.yml"
  ".github/ISSUE_TEMPLATE/docs-improvement.yml"
  ".github/ISSUE_TEMPLATE/feature-request.yml"
  ".github/codex/prompts/kr-tech-news-daily.md"
  ".github/workflows/kr-tech-news-daily.yml"
  "scripts/build-daily-news-shortlist.py"
  "scripts/check-workflow-schedules.py"
  "scripts/collect-kr-feeds.py"
  "scripts/evaluate-news-daily-quality.py"
  "scripts/estimate-prompt-budget.py"
  "scripts/render-weekly-career-site-radar.py"
  "scripts/select-ps-problem.py"
  "scripts/send-discord.py"
  "scripts/should-run-now.py"
  "scripts/update-oss-progress.py"
  "scripts/update-ps-progress.py"
  "scripts/validate-career-feed-brief.py"
  "scripts/write-news-daily-run-summary.py"
  "tests/fixtures/kr-tech-daily-valid.md"
  "tests/fixtures/kr-tech-daily-invalid-blog-title-count.md"
  "tests/fixtures/kr-tech-daily-invalid-paar-action-missing.md"
  "tests/fixtures/kr-tech-daily-invalid-fixed-plan.md"
  "tests/fixtures/kr-tech-daily-invalid-oversized-title.md"
  "tests/fixtures/kr-tech-daily-invalid-reference-domain.md"
  "tests/fixtures/kr-tech-daily-invalid-extension-field.md"
  "tests/fixtures/kr-tech-news-daily-valid.md"
  "tests/fixtures/kr-tech-news-daily-valid-sparse.md"
  "tests/fixtures/kr-tech-news-daily-valid-empty.md"
  "tests/fixtures/kr-tech-news-daily-valid-tech-investment.md"
  "tests/fixtures/kr-tech-news-daily-valid-quality-score-4.md"
  "tests/fixtures/kr-tech-news-daily-valid-tech-only.md"
  "tests/fixtures/kr-tech-news-daily-valid-checklist-action.md"
  "tests/fixtures/kr-tech-news-daily-invalid-duplicate-url.md"
  "tests/fixtures/kr-tech-news-daily-invalid-investment-advice.md"
  "tests/fixtures/kr-tech-news-daily-invalid-related-stock.md"
  "tests/fixtures/kr-tech-news-daily-invalid-investment-missing-risk.md"
  "tests/fixtures/kr-tech-news-daily-invalid-price-only.md"
  "tests/fixtures/kr-tech-news-daily-invalid-investment-missing-indicator.md"
  "tests/fixtures/kr-tech-news-daily-invalid-growth-vague-action.md"
  "tests/fixtures/kr-tech-news-daily-invalid-too-many-investment.md"
  "tests/fixtures/kr-tech-news-daily-invalid-growth-missing.md"
  "tests/fixtures/kr-backend-career-weekly-valid.md"
  "tests/fixtures/oss-recency-candidates.json"
  "tests/fixtures/candidates-empty/kr-oss-contribution-opportunities.json"
  "tests/test_daily_oss_contract.py"
  "tests/test_oss_reliability_gate.py"
  "tests/test_should_run_now.py"
)

for file in "${required_files[@]}"; do
  test -f "${file}"
done

echo "==> Checking daily source split"
python3 - <<'PY'
import json
from pathlib import Path

sources = json.loads(Path("configs/kr-sources.json").read_text(encoding="utf-8"))
categories = {
    category.get("id"): category
    for category in sources.get("categories", [])
    if isinstance(category, dict)
}
spring = categories.get("spring-jvm-study-topics")
if not spring:
    raise SystemExit("spring-jvm-study-topics category is required")
if spring.get("output_file") != "reports/candidates/spring-study-topic.json":
    raise SystemExit("spring-jvm-study-topics must write spring-study-topic.json")
if spring.get("naver_queries") != []:
    raise SystemExit("spring-jvm-study-topics must not use Naver queries")
if not spring.get("rss_sources") or not spring.get("reference_pages"):
    raise SystemExit("spring-jvm-study-topics needs official RSS/reference sources")

practical = json.loads(Path("configs/backend-practical-knowledge-curriculum.json").read_text(encoding="utf-8"))
required = {
    "track",
    "situation",
    "failure_mode",
    "practice_steps",
    "official_refs",
}
missing = []
for lesson in practical.get("lessons", []):
    absent = [
        field
        for field in required
        if not lesson.get(field)
    ]
    if absent:
        missing.append(f"{lesson.get('id', 'unknown')}:{','.join(absent)}")
if missing:
    raise SystemExit("backend practical curriculum misses required growth fields: " + "; ".join(missing[:5]))

broad_titles = {
    "처리량과 응답 시간",
    "서버 성능 개선 기초",
    "REST API란",
    "WebSocket 개념",
    "성능 최적화",
    "자료구조와 알고리즘",
}
matches = [
    f"{lesson.get('id', 'unknown')}:{lesson.get('title', '')}"
    for lesson in practical.get("lessons", [])
    if lesson.get("title") in broad_titles
]
if matches:
    raise SystemExit("backend practical curriculum still has broad title(s): " + "; ".join(matches))

cs_curriculum = json.loads(Path("configs/backend-core-cs-curriculum.json").read_text(encoding="utf-8"))
required_tracks = {
    "computer-architecture",
    "operating-system",
    "network",
    "database",
    "jvm-runtime",
}
required_topic_fields = {
    "id",
    "track",
    "title",
    "why_backend",
    "key_concept",
    "practice_steps",
    "done_criteria",
    "interview_question",
    "refs",
}
topics = cs_curriculum.get("topics", [])
if not isinstance(topics, list) or not topics:
    raise SystemExit("backend core CS curriculum must contain topics")
tracks = {
    topic.get("track")
    for topic in topics
    if isinstance(topic, dict)
}
missing_tracks = sorted(required_tracks - tracks)
if missing_tracks:
    raise SystemExit("backend core CS curriculum misses tracks: " + ", ".join(missing_tracks))
topic_missing = []
for topic in topics:
    if not isinstance(topic, dict):
        topic_missing.append("non-object")
        continue
    absent = [
        field
        for field in required_topic_fields
        if not topic.get(field)
    ]
    if absent:
        topic_missing.append(f"{topic.get('id', 'unknown')}:{','.join(absent)}")
if topic_missing:
    raise SystemExit("backend core CS curriculum misses required fields: " + "; ".join(topic_missing[:5]))

terms_glossary = json.loads(Path("configs/backend-terms-glossary.json").read_text(encoding="utf-8"))
required_term_fields = {
    "id",
    "term",
    "one_line_definition",
    "backend_context",
    "common_misunderstanding",
    "spring_or_api_connection",
    "check_question",
    "refs",
}
terms = terms_glossary.get("terms", [])
if not isinstance(terms, list) or len(terms) < 30:
    raise SystemExit("backend terms glossary must contain at least 30 terms")
term_missing = []
for term in terms:
    if not isinstance(term, dict):
        term_missing.append("non-object")
        continue
    absent = [
        field
        for field in required_term_fields
        if not term.get(field)
    ]
    if absent:
        term_missing.append(f"{term.get('id', 'unknown')}:{','.join(absent)}")
if term_missing:
    raise SystemExit("backend terms glossary misses required fields: " + "; ".join(term_missing[:5]))

print("daily source split smoke check passed")
PY

echo "==> Checking daily learning reference policy"
python3 - <<'PY'
import importlib.util
import sys
from pathlib import Path

module_path = Path("scripts/validate-career-feed-brief.py")
spec = importlib.util.spec_from_file_location("validate_career_feed_brief", module_path)
if spec is None or spec.loader is None:
    raise SystemExit("Could not load validate-career-feed-brief.py")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)

d2_url = "https://d2.naver.com/helloworld/123"
news_url = "https://news.naver.com/article/123"
search_url = "https://search.naver.com/search.naver?query=spring"
blog_url = "https://blog.naver.com/example/123"
media_url = "https://www.etnews.com/20260529000123"
aws_docs_url = "https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_Java.html"
aws_marketing_url = "https://aws.amazon.com/architecture/"
kotlin_docs_url = "https://kotlinlang.org/docs/null-safety.html"

if validator.blocked_learning_domain(d2_url) != "":
    raise SystemExit("d2.naver.com must not be blocked for practical knowledge references")
if not validator.is_allowed_url_prefix(d2_url, validator.PRACTICAL_ALLOWED_URL_PREFIXES):
    raise SystemExit("d2.naver.com must be allowed for practical knowledge references")
if not validator.is_allowed_url_prefix(aws_docs_url, validator.SPRING_OFFICIAL_ALLOWED_URL_PREFIXES):
    raise SystemExit("docs.aws.amazon.com must be allowed for Spring/JVM learning references")
if validator.is_allowed_url_prefix(aws_marketing_url, validator.SPRING_ALLOWED_URL_PREFIXES):
    raise SystemExit("aws.amazon.com must not be broadly allowed for Spring/JVM learning references")
if not validator.is_allowed_url_prefix(kotlin_docs_url, validator.SPRING_OFFICIAL_ALLOWED_URL_PREFIXES):
    raise SystemExit("Kotlin official docs must be allowed for Spring/JVM learning references")
if not validator.blocked_learning_domain(news_url):
    raise SystemExit("news.naver.com must be blocked for learning references")
if not validator.blocked_learning_domain(search_url):
    raise SystemExit("search.naver.com must be blocked for learning references")
if not validator.blocked_learning_domain(blog_url):
    raise SystemExit("blog.naver.com must be blocked for learning references")
if not validator.blocked_learning_domain(media_url):
    raise SystemExit("domestic media domains must be blocked for learning references")

print("daily learning reference policy smoke check passed")
PY

echo "==> Checking OSS repository config"
grep -q 'def is_recent_issue' scripts/collect-kr-feeds.py
grep -q 'created_at_older_than_recent_window' scripts/collect-kr-feeds.py
grep -q 'stale_issue_filtered_count' scripts/collect-kr-feeds.py
grep -q 'safe_oss_candidates' scripts/collect-kr-feeds.py
grep -q 'def extract_github_issue_urls' scripts/validate-career-feed-brief.py
grep -q 'OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES' scripts/validate-career-feed-brief.py
grep -q 'OSS_FALLBACK_CONTAINS_ISSUE_URL' scripts/validate-career-feed-brief.py
grep -q 'created_within_recent_window' scripts/validate-career-feed-brief.py
grep -q 'CAREER_FEED_OSS_RECENT_DAYS' docs/policies/oss-candidate-policy.md
grep -q 'created_at' docs/policies/oss-candidate-policy.md
grep -q 'Fork Setup Guide' docs/getting-started/fork-setup.md
grep -q 'CAREER_FEED_DISCORD_DELIVERY_ENABLED=false' docs/getting-started/fork-setup.md
grep -q 'OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES' docs/getting-started/fork-setup.md
grep -q 'docs/getting-started/fork-setup.md' README.md
python3 - <<'PY'
import json
from pathlib import Path

required = {
    "spring-projects/spring-security",
    "spring-projects/spring-restdocs",
    "spring-projects/spring-boot",
    "gradle/gradle",
    "ktorio/ktor-documentation",
    "quarkusio/quarkus",
    "testcontainers/testcontainers-java",
    "micronaut-projects/micronaut-core",
    "spring-projects/spring-framework",
}
observation = {
    "ktorio/ktor",
    "Kotlin/kotlinx.coroutines",
}
config = json.loads(Path("configs/oss-repositories.json").read_text(encoding="utf-8"))
repositories = set(config.get("repositories", []))
weekly_observation_repositories = set(config.get("weekly_observation_repositories", []))
trusted = config.get("trusted_maintainers", {})
profiles = config.get("repository_profiles", [])
if not isinstance(trusted, dict):
    raise SystemExit("configs/oss-repositories.json trusted_maintainers must be an object")
if not isinstance(profiles, list):
    raise SystemExit("configs/oss-repositories.json repository_profiles must be a list")

missing_repositories = sorted(required - repositories)
missing_observation = sorted(observation - weekly_observation_repositories)
missing_trusted = sorted((required | observation) - set(trusted.keys()))
if missing_repositories:
    raise SystemExit("oss-repositories.json is missing required repositories: " + ", ".join(missing_repositories))
if missing_observation:
    raise SystemExit("oss-repositories.json is missing observation repositories: " + ", ".join(missing_observation))
if missing_trusted:
    raise SystemExit("oss-repositories.json trusted_maintainers is missing repository key(s): " + ", ".join(missing_trusted))

profiles_by_repo = {
    str(profile.get("repository", "")).strip(): profile
    for profile in profiles
    if isinstance(profile, dict)
}
missing_profiles = sorted(repositories - set(profiles_by_repo.keys()))
if missing_profiles:
    raise SystemExit("oss-repositories.json repository_profiles is missing repository key(s): " + ", ".join(missing_profiles))

required_profile_fields = [
    "display_name",
    "priority",
    "initial_fit_score",
    "ecosystem_tags",
    "beginner_labels",
    "positive_title_keywords",
    "avoid_labels",
    "avoid_title_keywords",
    "preferred_contribution_types",
    "contribution_guide",
    "search_urls",
    "search_queries",
    "local_check_hints",
    "docs_or_test_hints",
    "junior_notes",
]
allowed_types = {"docs", "test", "sample", "bug-repro", "javadoc", "kdoc", "error-message"}
for repository, profile in profiles_by_repo.items():
    missing_fields = [field for field in required_profile_fields if not profile.get(field)]
    if missing_fields:
        raise SystemExit(f"repository profile misses field(s): {repository} {missing_fields}")
    if profile.get("priority") not in {"A", "B", "C"}:
        raise SystemExit(f"repository profile has invalid priority: {repository}")
    for list_field in (
        "ecosystem_tags",
        "beginner_labels",
        "positive_title_keywords",
        "avoid_labels",
        "avoid_title_keywords",
        "preferred_contribution_types",
        "search_urls",
        "search_queries",
        "local_check_hints",
        "docs_or_test_hints",
    ):
        if not isinstance(profile.get(list_field), list) or not profile.get(list_field):
            raise SystemExit(f"repository profile field must be a non-empty list: {repository} {list_field}")
    if not isinstance(profile.get("initial_fit_score"), int) or not 0 <= profile["initial_fit_score"] <= 100:
        raise SystemExit(f"repository profile has invalid initial_fit_score: {repository}")
    preferred = set(profile.get("preferred_contribution_types", []))
    if not preferred <= allowed_types:
        raise SystemExit(f"repository profile has unsupported contribution type: {repository}")
    for query in profile.get("search_queries", []):
        if not isinstance(query, dict) or not str(query.get("name", "")).strip() or not str(query.get("query", "")).strip():
            raise SystemExit(f"repository profile has invalid search query: {repository}")
        if "repo:" in str(query.get("query", "")):
            raise SystemExit(f"repository profile search query must not hardcode repo scope: {repository}")

print("OSS repository config smoke check passed")
PY

echo "==> Checking workflow YAML parse"
if command -v ruby >/dev/null 2>&1; then
  ruby -e 'require "yaml"; ARGV.each { |path| YAML.load_file(path); puts "ok: #{path}" }' .github/workflows/*.yml
else
  echo "Warning: ruby not found; skipping workflow YAML parse check." >&2
fi

echo "==> Checking Discord sender safety"
python3 - <<'PY'
import importlib.util
import sys
from pathlib import Path

module_path = Path("scripts/send-discord.py")
spec = importlib.util.spec_from_file_location("send_discord", module_path)
if spec is None or spec.loader is None:
    raise SystemExit("Could not load send-discord.py")
sender = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sender
spec.loader.exec_module(sender)

long_markdown = "# Career Feed Test\n\n" + "\n\n".join(
    f"## Section {index}\n" + ("긴 본문 " * 90)
    for index in range(1, 30)
)
chunks = sender.split_markdown_for_discord(long_markdown)
if not chunks:
    raise SystemExit("Long Markdown split produced no chunks")
if any(len(chunk) > 2000 for chunk in chunks):
    raise SystemExit("Discord chunk exceeds 2000 characters")
try:
    sender.split_markdown_for_discord(" \n\t")
except RuntimeError:
    pass
else:
    raise SystemExit("Empty Markdown must fail")

print("Discord sender split smoke check passed")
PY

if rg -n --glob '!scripts/validate.sh' 'echo .*DISCORD_WEBHOOK_URL|print\(.*webhook_url|webhook_url.*print|DISCORD_WEBHOOK_URL.*echo' scripts .github; then
  echo "Webhook URL may be printed by scripts or workflows." >&2
  exit 1
fi

if rg -n 'https://discord(?:app)?\.com/api/webhooks/[0-9]+' .github scripts configs docs README.md .env.example tests AGENTS.md; then
  echo "Hardcoded Discord webhook URL found." >&2
  exit 1
fi

echo "==> Checking collector dry-runs"
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
python3 - <<'PY'
import json
from pathlib import Path

required_daily_backend_candidates = [
    Path("reports/candidates/spring-study-topic.json"),
    Path("reports/candidates/ps-weekly-routine.json"),
    Path("reports/candidates/kr-oss-contribution-opportunities.json"),
    Path("reports/candidates/backend-practical-knowledge.json"),
    Path("reports/candidates/cs-core-daily-topic.json"),
    Path("reports/candidates/backend-term-daily.json"),
]
missing = [
    str(path)
    for path in required_daily_backend_candidates
    if not path.exists()
]
if missing:
    raise SystemExit("daily-backend dry-run did not create candidate file(s): " + ", ".join(missing))

for path in [
    Path("reports/candidates/spring-study-topic.json"),
    Path("reports/candidates/cs-core-daily-topic.json"),
    Path("reports/candidates/backend-term-daily.json"),
]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("candidate_count") != 1 or not isinstance(payload.get("today"), dict):
        raise SystemExit(f"{path} must contain candidate_count=1 and a today object")

spring_payload = json.loads(Path("reports/candidates/spring-study-topic.json").read_text(encoding="utf-8"))
spring_today = spring_payload.get("today", {})
if not isinstance(spring_today, dict):
    raise SystemExit("spring-study-topic.json must include a today object")
required_spring_fields = {
    "track",
    "level",
    "one_line_question",
    "problem_situation",
    "official_doc_keywords",
    "learning_steps_30m",
    "practice_steps_30m",
    "blog_title_candidates",
    "paar_outline",
    "done_criteria",
    "next_topic",
}
missing_spring_fields = sorted(
    field for field in required_spring_fields if not spring_today.get(field)
)
if missing_spring_fields:
    raise SystemExit(
        "spring-study-topic.json today misses required field(s): "
        + ", ".join(missing_spring_fields)
    )
if len(spring_today.get("learning_steps_30m", [])) < 2:
    raise SystemExit("spring-study-topic.json must include at least 2 learning steps")
if len(spring_today.get("practice_steps_30m", [])) < 2:
    raise SystemExit("spring-study-topic.json must include at least 2 practice steps")
if len(spring_today.get("blog_title_candidates", [])) != 3:
    raise SystemExit("spring-study-topic.json must include exactly 3 blog title candidates")
outline = spring_today.get("paar_outline", {})
if not isinstance(outline, dict) or not {"problem", "analyze", "action", "result"} <= set(outline):
    raise SystemExit("spring-study-topic.json PAAR outline is incomplete")
spring_diagnostics = spring_payload.get("diagnostics", {})
if not isinstance(spring_diagnostics, dict):
    raise SystemExit("spring-study-topic.json must include diagnostics")
if "fallback_used" not in spring_diagnostics or "fallback_reasons" not in spring_diagnostics:
    raise SystemExit("spring-study-topic.json diagnostics must include fallback state")

oss_payload = json.loads(Path("reports/candidates/kr-oss-contribution-opportunities.json").read_text(encoding="utf-8"))
if oss_payload.get("verification_policy", "").find("safe_to_recommend=true") == -1:
    raise SystemExit("OSS candidate payload must document the safe_to_recommend gate")
diagnostics = oss_payload.get("diagnostics", {})
if not isinstance(diagnostics, dict):
    raise SystemExit("OSS candidate payload must include diagnostics")
if diagnostics.get("linked_work_verification") != "graphql_required":
    raise SystemExit("OSS diagnostics must require GraphQL linked work verification")
for item in oss_payload.get("items", []):
    if not isinstance(item, dict) or item.get("safe_to_recommend") is not True:
        raise SystemExit("OSS payload items must all have safe_to_recommend=true")

print("daily-backend CS/term candidate smoke check passed")
PY

echo "==> Checking Backend Daily run summary smoke"
EVENT_NAME=workflow_dispatch \
EVENT_SCHEDULE= \
DRY_RUN=true \
FORCE_SEND=false \
DELIVERY_LOCK_KEY=career-feed-backend-sent-test \
DELIVERY_LOCK_HIT=false \
SHOULD_GENERATE=true \
SHOULD_SEND=false \
SKIP_REASON=dry_run \
DISCORD_SEND_OUTCOME=skipped \
PS_PROGRESS_COMMIT_OUTCOME=skipped \
PS_PROGRESS_CHANGED=false \
python3 - <<'PY'
import json
import os
from pathlib import Path

workflow = Path(".github/workflows/kr-tech-daily.yml").read_text(encoding="utf-8").splitlines()
step_start = next(
    index
    for index, line in enumerate(workflow)
    if line.strip() == "- name: Write Backend Daily run summary"
)
heredoc_start = next(
    index
    for index in range(step_start, len(workflow))
    if "python3 - <<'PY'" in workflow[index]
)
heredoc_end = next(
    index
    for index in range(heredoc_start + 1, len(workflow))
    if workflow[index].strip() == "PY"
)
code_lines = []
for line in workflow[heredoc_start + 1 : heredoc_end]:
    code_lines.append(line[10:] if line.startswith("          ") else line)
exec(compile("\n".join(code_lines), "kr-tech-daily-run-summary", "exec"), {})

summary = json.loads(Path("reports/ops/backend-daily-run-summary.json").read_text(encoding="utf-8"))
required_fields = [
    "oss_safe_candidate_count",
    "oss_candidate_count",
    "oss_filtered_out_count",
    "oss_fallback_reason",
    "oss_source_errors_count",
    "selected_oss_repository",
    "selected_oss_issue_url",
    "selected_oss_difficulty_band",
]
missing = [field for field in required_fields if field not in summary]
if missing:
    raise SystemExit("Backend Daily run summary misses OSS field(s): " + ", ".join(missing))
summary_md = Path("reports/ops/backend-daily-run-summary.md").read_text(encoding="utf-8")
for text in ("OSS 후보 상태", "선택 후보", "linked work check degraded"):
    if text not in summary_md:
        raise SystemExit(f"Backend Daily run summary markdown misses: {text}")
print("Backend Daily run summary smoke check passed")
PY

python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/build-daily-news-shortlist.py
python3 scripts/estimate-prompt-budget.py --kst-now "2026-05-29 09:05:00 KST"
python3 - <<'PY'
import json
from pathlib import Path

shortlist = json.loads(Path("reports/candidates/kr-tech-news-shortlist.json").read_text(encoding="utf-8"))
budget = json.loads(Path("reports/ops/news-daily-token-budget.json").read_text(encoding="utf-8"))
for field in [
    "schema_version",
    "raw_candidate_count_total",
    "shortlist_count",
    "tech_shortlist_count",
    "investment_shortlist_count",
    "tracks",
    "items",
]:
    if field not in shortlist:
        raise SystemExit(f"shortlist payload misses field: {field}")
if shortlist["schema_version"] != 2:
    raise SystemExit("shortlist schema_version must be 2")
for track in ["tech", "investment"]:
    if track not in shortlist["tracks"] or "items" not in shortlist["tracks"][track]:
        raise SystemExit(f"shortlist payload misses track items: {track}")
for field in [
    "raw_candidate_count_total",
    "shortlist_count",
    "tech_shortlist_count",
    "investment_shortlist_count",
    "estimated_prompt_chars",
    "estimated_prompt_tokens_rough",
    "estimated_output_tokens_budget_rough",
    "target_total_items",
    "target_tech_items",
    "target_investment_items",
    "max_flat_shortlist_items",
    "token_budget_status",
]:
    if field not in budget:
        raise SystemExit(f"token budget payload misses field: {field}")
if budget["estimated_prompt_tokens_rough"] < 1:
    raise SystemExit("rough token estimate must be positive")
print("news daily shortlist and token budget smoke check passed")
PY
python3 - <<'PY'
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

module_path = Path("scripts/build-daily-news-shortlist.py")
spec = importlib.util.spec_from_file_location("build_daily_news_shortlist", module_path)
if spec is None or spec.loader is None:
    raise SystemExit("Could not load build-daily-news-shortlist.py")
shortlist_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = shortlist_module
spec.loader.exec_module(shortlist_module)

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    input_path = tmp / "candidates.json"
    profile_path = tmp / "audience-profile.json"
    input_path.write_text(
        json.dumps(
            {
                "candidate_count": 2,
                "items": [
                    {
                        "title": "AI API rate limit update",
                        "url": "https://tech.example.com/api-rate-limit",
                        "summary": "Developer API timeout and retry policy changed.",
                        "query": "국내 AI API 개발자",
                        "developer_relevance": "high",
                        "score": 80,
                    },
                    {
                        "title": "Cloud CAPEX and GPU server demand",
                        "url": "https://finance.example.com/cloud-capex",
                        "summary": "Cloud CAPEX, GPU server demand, and enterprise AI revenue are connected.",
                        "query": "클라우드 CAPEX AI 인프라",
                        "developer_relevance": "medium",
                        "score": 70,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    profile_path.write_text(
        json.dumps({"preferences": {"content_tracks": {"enabled": True}}}),
        encoding="utf-8",
    )
    payload = shortlist_module.build_shortlist([input_path], profile_path, 12, 8, 4)

if payload["tech_shortlist_count"] != 1:
    raise SystemExit("shortlist smoke must classify one tech item")
if payload["investment_shortlist_count"] != 1:
    raise SystemExit("shortlist smoke must classify one investment item")
investment_item = payload["tracks"]["investment"]["items"][0]
for field in ["investment_relevance", "technology_link", "risk_flags"]:
    if field not in investment_item:
        raise SystemExit(f"investment shortlist item misses field: {field}")
print("news daily track split smoke check passed")
PY
cp tests/fixtures/kr-tech-news-daily-valid-tech-investment.md reports/briefs/kr-tech-news-daily.md
python3 scripts/evaluate-news-daily-quality.py \
  --report tests/fixtures/kr-tech-news-daily-valid-tech-investment.md \
  --shortlist reports/candidates/kr-tech-news-shortlist.json \
  --token-budget reports/ops/news-daily-token-budget.json
python3 - <<'PY'
import json
from pathlib import Path

quality = json.loads(Path("reports/ops/news-daily-quality-report.json").read_text(encoding="utf-8"))
required_fields = [
    "quality_score",
    "tech_item_count",
    "investment_item_count",
    "total_item_count",
    "target_ratio_met",
    "bridge_present",
    "growth_score",
    "growth_action_present",
    "growth_action_quality",
    "investment_advice_risk",
    "price_move_only_risk",
    "token_efficiency",
    "warnings",
    "recommendation",
]
missing = [field for field in required_fields if field not in quality]
if missing:
    raise SystemExit("News Daily quality report misses field(s): " + ", ".join(missing))
if quality["quality_score"] < 3:
    raise SystemExit("News Daily quality report score must be at least 3 for valid fixture")
if quality["recommendation"] not in {"accept", "review"}:
    raise SystemExit("News Daily quality report must not tune a valid fixture")
print("News Daily quality report smoke check passed")
PY
EVENT_NAME=workflow_dispatch \
EVENT_SCHEDULE= \
DRY_RUN=true \
FORCE_SEND=false \
DELIVERY_LOCK_KEY=career-feed-news-sent-test \
DELIVERY_LOCK_HIT=false \
SHOULD_GENERATE=true \
SHOULD_SEND=false \
SKIP_REASON=dry_run \
DISCORD_SEND_OUTCOME=skipped \
python3 scripts/write-news-daily-run-summary.py
python3 - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("reports/ops/news-daily-run-summary.json").read_text(encoding="utf-8"))
required_fields = [
    "raw_candidate_count_total",
    "shortlist_count",
    "tech_shortlist_count",
    "investment_shortlist_count",
    "selected_news_count",
    "tech_selected_count",
    "investment_selected_count",
    "bridge_present",
    "growth_score",
    "growth_action_present",
    "quality_score",
    "quality_recommendation",
    "target_ratio_met",
    "growth_action_quality",
    "investment_advice_risk",
    "price_move_only_risk",
    "estimated_prompt_chars",
    "estimated_prompt_tokens_rough",
    "estimated_output_tokens_budget_rough",
]
missing = [field for field in required_fields if field not in summary]
if missing:
    raise SystemExit("News Daily run summary misses field(s): " + ", ".join(missing))
if summary["tech_selected_count"] != 2:
    raise SystemExit("News Daily run summary must count two tech items")
if summary["investment_selected_count"] != 1:
    raise SystemExit("News Daily run summary must count one investment item")
if summary["bridge_present"] is not True:
    raise SystemExit("News Daily run summary must detect bridge section")
if summary["growth_score"] != 5 or summary["growth_action_present"] is not True:
    raise SystemExit("News Daily run summary must detect growth score and action")
print("News Daily run summary smoke check passed")
PY
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/render-weekly-career-site-radar.py
python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career
python3 - <<'PY'
import json
from pathlib import Path

required = {"official-careers", "job-intern-platforms", "activities-competitions"}
path = Path("reports/candidates/weekly-career-site-radar.json")
data = json.loads(path.read_text(encoding="utf-8"))

sections = data.get("sections", [])
if not isinstance(sections, list):
    raise SystemExit("weekly career site radar sections must be a list")
section_ids = {
    str(section.get("id", ""))
    for section in sections
    if isinstance(section, dict)
}
if section_ids != required:
    missing = sorted(required - section_ids)
    extra = sorted(section_ids - required)
    raise SystemExit(f"site radar section id mismatch: missing={missing} extra={extra}")

minimums = {
    "official-careers": 7,
    "job-intern-platforms": 6,
    "activities-competitions": 5,
}
for section in sections:
    sites = section.get("sites", []) if isinstance(section, dict) else []
    section_id = str(section.get("id", "")) if isinstance(section, dict) else ""
    if not isinstance(sites, list) or len(sites) < minimums[section_id]:
        raise SystemExit(f"site radar section has too few sites: {section}")

compat = json.loads(Path("reports/candidates/kr-backend-career-events.json").read_text(encoding="utf-8"))
if compat.get("items") != [] or compat.get("diagnostics", {}).get("status") != "disabled":
    raise SystemExit("weekly career compat candidate payload must be disabled")

print("weekly career site radar smoke check passed")
PY

echo "==> Checking fixtures"
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-invalid-blog-title-count.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-invalid-paar-action-missing.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-invalid-fixed-plan.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-invalid-oversized-title.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-invalid-reference-domain.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-invalid-extension-field.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-sparse.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-empty.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-tech-investment.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-quality-score-4.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-tech-only.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-checklist-action.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-duplicate-url.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-investment-advice.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-related-stock.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-investment-missing-risk.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-price-only.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-investment-missing-indicator.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-growth-vague-action.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-too-many-investment.md --type daily-news
expect_fail python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-growth-missing.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
python3 tests/test_daily_oss_contract.py
python3 tests/test_oss_reliability_gate.py
python3 tests/test_should_run_now.py
python3 tests/test_weekly_career_collector.py

echo "==> Checking PS progress status"
python3 scripts/update-ps-progress.py --status >/dev/null
python3 scripts/update-oss-progress.py --status >/dev/null

echo "==> Checking removed references"
blocked_terms=(
  "FREE_""MODE"
  "AI_LIGHT_""MODE"
  "AI_SEARCH_""MODE"
  "KR_""PRE""MIUM_""MODE"
  "kr-""pre""mium"
  "KR ""Pre""mium"
  "Daily Korea ""Pre""mium"
  "daily-""feed"
  "ai-brief-""manual"
  "compact-""brief"
  "kr-""pre""mium-brief"
  "collect-""feeds"
  "render-""overview"
  "render-""brief"
  "send-category-""briefs"
  "make-sample-""report"
  "validate-kr-""pre""mium-brief"
  "DISCORD_WEBHOOK_KR_""PRE""MIUM_""BRIEF"
  "DISCORD_WEBHOOK_DAILY_""OVERVIEW"
  "DISCORD_WEBHOOK_AI_""NEWS"
  "DISCORD_WEBHOOK_BACKEND_""NEWS"
  "DISCORD_WEBHOOK_SECURITY_""ALERTS"
  "DISCORD_WEBHOOK_BACKEND_""TECH"
  "DISCORD_WEBHOOK_JOB_""FEED"
  "무료 ""RSS"
  "수동 ""백업"
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
  echo "Removed route references remain. Clean them up before finishing." >&2
  exit 1
fi

echo "==> Checking removed output fields"
removed_output_terms=(
  "Mark PS Solved ""workflow"
  "대상 ""적합성"
  "백엔드 ""적합성"
  "Kotlin/Spring Boot ""관련성"
  "왜 나에게 ""맞는가"
  "제외한 ""후보"
)

removed_output_pattern=""
for term in "${removed_output_terms[@]}"; do
  if [ -z "${removed_output_pattern}" ]; then
    removed_output_pattern="${term}"
  else
    removed_output_pattern="${removed_output_pattern}|${term}"
  fi
done

if rg -n "${removed_output_pattern}" .github scripts tests README.md docs .env.example; then
  echo "Removed output fields remain. Clean them up before finishing." >&2
  exit 1
fi

echo "==> Checking diff whitespace"
git diff --check

echo "==> Validation complete"
