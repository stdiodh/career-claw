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
if [ "${workflow_count}" != "3" ]; then
  echo "Expected exactly 3 workflow files, found ${workflow_count}." >&2
  exit 1
fi

echo "==> Checking workflow versions and schedules"
grep -q 'uses: actions/checkout@v5' .github/workflows/kr-tech-daily.yml
grep -q 'uses: actions/setup-python@v6' .github/workflows/kr-tech-daily.yml
grep -q 'uses: actions/upload-artifact@v6' .github/workflows/kr-tech-daily.yml
grep -q 'cron: "47 8 \* \* 1-5"' .github/workflows/kr-tech-daily.yml
grep -q 'timezone: "Asia/Seoul"' .github/workflows/kr-tech-daily.yml

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
if [ "${prompt_count}" != "1" ]; then
  echo "Expected exactly 1 prompt file, found ${prompt_count}." >&2
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
	  "configs/company-career-watchlist.json"
	  "configs/weekly-career-site-radar.json"
	  "configs/oss-repositories.json"
	  "configs/programmers-ps-curriculum.json"
	  "data/ps-progress.json"
  "scripts/check-workflow-schedules.py"
  "scripts/collect-kr-feeds.py"
  "scripts/render-weekly-career-site-radar.py"
  "scripts/select-ps-problem.py"
  "scripts/send-discord.py"
  "scripts/update-ps-progress.py"
  "scripts/validate-career-feed-brief.py"
  "tests/fixtures/kr-tech-daily-valid.md"
  "tests/fixtures/kr-backend-career-weekly-valid.md"
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

echo "==> Checking collector dry-runs"
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
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
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
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
  "daily-""news"
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
