#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> Checking Python syntax"
python3 -m py_compile \
  scripts/check-workflow-schedules.py \
  scripts/collect-kr-feeds.py \
  scripts/render-weekly-career-site-radar.py \
  scripts/select-ps-problem.py \
  scripts/send-discord.py \
  scripts/update-ps-progress.py \
  scripts/validate-career-feed-brief.py

echo "==> Checking current workflows"
test -f .github/workflows/kr-tech-daily.yml
test -f .github/workflows/kr-tech-news-daily.yml
test -f .github/workflows/kr-backend-career-weekly.yml
test -f .github/workflows/mark-ps-solved.yml

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
grep -q 'cron: "5 8 \* \* 1-5"' .github/workflows/kr-tech-daily.yml
grep -q 'cron: "25 9 \* \* 1-5"' .github/workflows/kr-tech-daily.yml
grep -q 'timezone: "Asia/Seoul"' .github/workflows/kr-tech-daily.yml
grep -q 'workflow_dispatch:' .github/workflows/kr-tech-daily.yml
grep -q 'dry_run:' .github/workflows/kr-tech-daily.yml
grep -q 'force_send:' .github/workflows/kr-tech-daily.yml
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
grep -q 'actions/cache/restore@v4' .github/workflows/kr-tech-daily.yml
grep -q 'actions/cache/save@v4' .github/workflows/kr-tech-daily.yml
grep -q 'group: career-feed-backend-daily-${{ github.ref }}' .github/workflows/kr-tech-daily.yml
grep -q 'Wait until 09:00 KST before Discord send' .github/workflows/kr-tech-daily.yml
grep -q "if: github.event_name == 'schedule' && steps.delivery.outputs.should_send == 'true'" .github/workflows/kr-tech-daily.yml
grep -q 'target_epoch="$(TZ=Asia/Seoul date -d "${today_kst} 09:00:00" +%s)"' .github/workflows/kr-tech-daily.yml
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
grep -q 'git push' .github/workflows/kr-tech-daily.yml
grep -q 'commit-ps-progress' .github/workflows/kr-tech-daily.yml
grep -q 'ps_progress_commit_attempted' .github/workflows/kr-tech-daily.yml
grep -q 'ps_progress_commit_success' .github/workflows/kr-tech-daily.yml
if grep -q 'DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY\|kr-dev-ai-news.json\|kr-ai-tech-news.json' .github/workflows/kr-tech-daily.yml; then
  echo "Backend Daily workflow must not use the news webhook or news candidate files." >&2
  exit 1
fi

grep -q 'uses: actions/checkout@v5' .github/workflows/kr-tech-news-daily.yml
grep -q 'uses: actions/setup-python@v6' .github/workflows/kr-tech-news-daily.yml
grep -q 'uses: actions/upload-artifact@v6' .github/workflows/kr-tech-news-daily.yml
grep -q 'cron: "15 8 \* \* 1-5"' .github/workflows/kr-tech-news-daily.yml
grep -q 'cron: "30 9 \* \* 1-5"' .github/workflows/kr-tech-news-daily.yml
grep -q 'timezone: "Asia/Seoul"' .github/workflows/kr-tech-news-daily.yml
grep -q 'workflow_dispatch:' .github/workflows/kr-tech-news-daily.yml
grep -q 'dry_run:' .github/workflows/kr-tech-news-daily.yml
grep -q 'force_send:' .github/workflows/kr-tech-news-daily.yml
grep -q 'contents: read' .github/workflows/kr-tech-news-daily.yml
if grep -q 'contents: write' .github/workflows/kr-tech-news-daily.yml; then
  echo "News Daily workflow must not request contents: write." >&2
  exit 1
fi
grep -q 'actions: read' .github/workflows/kr-tech-news-daily.yml
grep -q 'timeout-minutes: 75' .github/workflows/kr-tech-news-daily.yml
grep -q 'DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY' .github/workflows/kr-tech-news-daily.yml
grep -q 'collect-kr-feeds.py --mode daily-news' .github/workflows/kr-tech-news-daily.yml
grep -q -- '--type daily-news' .github/workflows/kr-tech-news-daily.yml
grep -q 'career-feed-news-sent-' .github/workflows/kr-tech-news-daily.yml
grep -q 'actions/cache/restore@v4' .github/workflows/kr-tech-news-daily.yml
grep -q 'actions/cache/save@v4' .github/workflows/kr-tech-news-daily.yml
grep -q 'group: career-feed-news-daily-${{ github.ref }}' .github/workflows/kr-tech-news-daily.yml
grep -q 'Wait until 09:05 KST before Discord send' .github/workflows/kr-tech-news-daily.yml
grep -q "if: github.event_name == 'schedule' && steps.delivery.outputs.should_send == 'true'" .github/workflows/kr-tech-news-daily.yml
grep -q 'target_epoch="$(TZ=Asia/Seoul date -d "${today_kst} 09:05:00" +%s)"' .github/workflows/kr-tech-news-daily.yml
grep -q 'news-daily-run-summary.json' .github/workflows/kr-tech-news-daily.yml
grep -q 'DISCORD_WEBHOOK_CAREER_FEED_OPS' .github/workflows/kr-tech-news-daily.yml
grep -q 'if: always()' .github/workflows/kr-tech-news-daily.yml
grep -q 'reports/ops/\*.json' .github/workflows/kr-tech-news-daily.yml
grep -q 'reports/ops/\*.md' .github/workflows/kr-tech-news-daily.yml
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
grep -q 'workflow_dispatch:' .github/workflows/kr-backend-career-weekly.yml
grep -q 'send_to_discord:' .github/workflows/kr-backend-career-weekly.yml
grep -q 'render-weekly-career-site-radar.py' .github/workflows/kr-backend-career-weekly.yml
if grep -q 'schedule:' .github/workflows/kr-backend-career-weekly.yml; then
  echo "kr-backend-career-weekly.yml must not define a schedule." >&2
  exit 1
fi
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
grep -q '오늘의 CS Core & 백엔드 용어' .github/codex/prompts/kr-tech-daily-brief.md
if ! grep -Eq '3(~|-)5개' .github/codex/prompts/kr-tech-news-daily.md; then
  echo "News Daily prompt must include the 3~5개 output rule." >&2
  exit 1
fi

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
  "configs/audience-profile.json"
  "configs/kr-sources.json"
  "configs/backend-practical-knowledge-curriculum.json"
  "configs/backend-core-cs-curriculum.json"
  "configs/backend-terms-glossary.json"
  "configs/company-career-watchlist.json"
  "configs/weekly-career-site-radar.json"
  "configs/oss-repositories.json"
  "configs/programmers-ps-curriculum.json"
  "data/ps-progress.json"
  ".github/codex/prompts/kr-tech-news-daily.md"
  ".github/workflows/kr-tech-news-daily.yml"
  "scripts/check-workflow-schedules.py"
  "scripts/collect-kr-feeds.py"
  "scripts/render-weekly-career-site-radar.py"
  "scripts/select-ps-problem.py"
  "scripts/send-discord.py"
  "scripts/update-ps-progress.py"
  "scripts/validate-career-feed-brief.py"
  "tests/fixtures/kr-tech-daily-valid.md"
  "tests/fixtures/kr-tech-news-daily-valid.md"
  "tests/fixtures/kr-tech-news-daily-valid-sparse.md"
  "tests/fixtures/kr-tech-news-daily-valid-empty.md"
  "tests/fixtures/kr-tech-news-daily-invalid-duplicate-url.md"
  "tests/fixtures/kr-tech-news-daily-invalid-investment.md"
  "tests/fixtures/kr-backend-career-weekly-valid.md"
  "tests/test_oss_reliability_gate.py"
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

if validator.blocked_learning_domain(d2_url) != "":
    raise SystemExit("d2.naver.com must not be blocked for practical knowledge references")
if not validator.is_allowed_url_prefix(d2_url, validator.PRACTICAL_ALLOWED_URL_PREFIXES):
    raise SystemExit("d2.naver.com must be allowed for practical knowledge references")
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
python3 - <<'PY'
import json
from pathlib import Path

required = {
    "spring-projects/spring-boot",
    "spring-projects/spring-framework",
    "spring-projects/spring-security",
    "spring-projects/spring-data-jpa",
    "spring-projects/spring-ai",
    "spring-projects/spring-grpc",
    "spring-projects/spring-modulith",
    "micrometer-metrics/micrometer",
    "open-telemetry/opentelemetry-java-instrumentation",
    "Kotlin/kotlinx.coroutines",
    "Kotlin/kotlinx.serialization",
    "JetBrains/Exposed",
}
config = json.loads(Path("configs/oss-repositories.json").read_text(encoding="utf-8"))
repositories = set(config.get("repositories", []))
trusted = config.get("trusted_maintainers", {})
if not isinstance(trusted, dict):
    raise SystemExit("configs/oss-repositories.json trusted_maintainers must be an object")

missing_repositories = sorted(required - repositories)
missing_trusted = sorted(required - set(trusted.keys()))
if missing_repositories:
    raise SystemExit("oss-repositories.json is missing required repositories: " + ", ".join(missing_repositories))
if missing_trusted:
    raise SystemExit("oss-repositories.json trusted_maintainers is missing repository key(s): " + ", ".join(missing_trusted))

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
    Path("reports/candidates/cs-core-daily-topic.json"),
    Path("reports/candidates/backend-term-daily.json"),
]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("candidate_count") != 1 or not isinstance(payload.get("today"), dict):
        raise SystemExit(f"{path} must contain candidate_count=1 and a today object")

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
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
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
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-sparse.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-empty.md --type daily-news
if python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-duplicate-url.md --type daily-news; then
  echo "Expected duplicate URL fixture to fail" >&2
  exit 1
fi
if python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-invalid-investment.md --type daily-news; then
  echo "Expected investment fixture to fail" >&2
  exit 1
fi
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
python3 tests/test_oss_reliability_gate.py
python3 tests/test_weekly_career_collector.py

echo "==> Checking PS progress status"
python3 scripts/update-ps-progress.py --status >/dev/null

echo "==> Checking removed references"
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
  "오늘 ""할 일"
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
