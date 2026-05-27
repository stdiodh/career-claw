#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> Checking Python syntax"
python3 -m py_compile \
  scripts/build-ai-input.py \
  scripts/collect-feeds.py \
  scripts/collect-kr-feeds.py \
  scripts/make-sample-report.py \
  scripts/render-brief.py \
  scripts/render-overview.py \
  scripts/send-category-briefs.py \
  scripts/send-discord.py \
  scripts/validate-kr-premium-brief.py

echo "==> Checking cost guards"
if grep -q "openai/codex-action" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must not use Codex Action." >&2
  exit 1
fi

if grep -q "OPENAI_API_KEY" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must not require OPENAI_API_KEY." >&2
  exit 1
fi

if grep -q "schedule:" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must stay manual and must not define schedule." >&2
  exit 1
fi

if grep -q -- "--search" .github/workflows/daily-feed.yml; then
  echo "Cost guard failed: daily-feed.yml must not use live web search." >&2
  exit 1
fi

if grep -q "schedule:" .github/workflows/kr-premium-brief.yml; then
  echo "Cost guard failed: legacy kr-premium-brief.yml must stay manual." >&2
  exit 1
fi

if grep -q "schedule:" .github/workflows/daily-news.yml; then
  echo "Cost guard failed: daily-news.yml must stay manual and must not define schedule." >&2
  exit 1
fi

if ! grep -q 'cron: "10 0 \* \* 1-5"' .github/workflows/kr-tech-daily.yml; then
  echo "Cost guard failed: kr-tech-daily.yml must define the weekday 09:10 KST schedule." >&2
  exit 1
fi

if ! grep -q 'cron: "30 0 \* \* 1"' .github/workflows/kr-backend-career-weekly.yml; then
  echo "Cost guard failed: kr-backend-career-weekly.yml must define the Monday 09:30 KST schedule." >&2
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

if grep -q "reports/briefs/kr-tech-daily.md" .github/workflows/kr-tech-daily.yml \
  && grep -q "output-file: reports/briefs/kr-tech-daily.md" .github/workflows/kr-tech-daily.yml; then
  echo "Cost guard failed: Codex output-file must not overwrite kr-tech-daily.md." >&2
  exit 1
fi

if grep -q "reports/briefs/kr-backend-career-weekly.md" .github/workflows/kr-backend-career-weekly.yml \
  && grep -q "output-file: reports/briefs/kr-backend-career-weekly.md" .github/workflows/kr-backend-career-weekly.yml; then
  echo "Cost guard failed: Codex output-file must not overwrite kr-backend-career-weekly.md." >&2
  exit 1
fi

if ! grep -q "DISCORD_WEBHOOK_KR_TECH_DAILY" .github/workflows/kr-tech-daily.yml; then
  echo "Cost guard failed: kr-tech-daily.yml must use DISCORD_WEBHOOK_KR_TECH_DAILY." >&2
  exit 1
fi

if ! grep -q "DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY" .github/workflows/kr-backend-career-weekly.yml; then
  echo "Cost guard failed: kr-backend-career-weekly.yml must use DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY." >&2
  exit 1
fi

if grep -q "DISCORD_WEBHOOK_KR_PREMIUM_BRIEF" .github/workflows/kr-tech-daily.yml; then
  echo "Cost guard failed: kr-tech-daily.yml must not use the legacy KR premium webhook." >&2
  exit 1
fi

if grep -q "DISCORD_WEBHOOK_KR_PREMIUM_BRIEF" .github/workflows/kr-backend-career-weekly.yml; then
  echo "Cost guard failed: kr-backend-career-weekly.yml must not use the legacy KR premium webhook." >&2
  exit 1
fi

for workflow in .github/workflows/*.yml; do
  if grep -q "schedule:" "${workflow}" \
    && grep -q "DISCORD_WEBHOOK_KR_PREMIUM_BRIEF" "${workflow}"; then
    echo "Cost guard failed: scheduled workflow must not use the legacy KR premium webhook: ${workflow}" >&2
    exit 1
  fi
done

echo "==> Checking shell and workflow syntax"
bash -n scripts/validate.sh
if command -v ruby >/dev/null 2>&1; then
  ruby -e 'require "yaml"; ARGV.each { |path| YAML.load_file(path) }' .github/workflows/*.yml
else
  echo "Warning: ruby not found; skipping workflow YAML parse check." >&2
fi

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
    if path.name == "kr-premium-daily.md":
        continue
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

echo "==> Checking manual free category send dry-run"
python3 scripts/send-category-briefs.py --category daily-overview --include-disabled --dry-run
python3 scripts/send-category-briefs.py --category ai-news --include-disabled --dry-run
python3 scripts/send-category-briefs.py --category backend-news --include-disabled --dry-run
python3 scripts/send-category-briefs.py --category security-alerts --include-disabled --dry-run

echo "==> Checking Discord payload embed suppression"
python3 - <<'PY'
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("send_discord", Path("scripts/send-discord.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
payload = json.loads(module.build_payload("https://example.com").decode("utf-8"))
if payload.get("flags") != 4:
    raise SystemExit("Discord payload must set SUPPRESS_EMBEDS flag.")
PY

echo "==> Checking KR premium brief validation fixtures"
python3 scripts/validate-kr-premium-brief.py tests/fixtures/kr-premium-brief-valid.md
if python3 scripts/validate-kr-premium-brief.py tests/fixtures/kr-premium-brief-invalid-generic.md; then
  echo "KR premium validation fixture should have failed." >&2
  exit 1
fi

echo "==> Checking KR Premium v2 validation samples"
python3 - <<'PY'
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

daily_valid = """# Career Feed - Korea Tech Daily
기준시각: 2026-05-27 09:10 KST

한 줄 요약:
- 오늘은 국내 AI API와 Spring 운영 사례를 먼저 확인합니다.

## 1. 한국 AI 테크

### 1-1. 네이버클라우드 AI API 업데이트
- 무슨 일: 국내 AI API 활용 후보가 확인됐습니다.
- 왜 나에게 중요한가: 백엔드 포트폴리오에서 AI API 연동 주제를 고를 때 참고할 수 있습니다.
- 백엔드 관점: 인증, 요청 제한, 장애 대응 설계를 함께 확인해야 합니다.
- 내 액션: API 문서에서 Spring Boot 연동 가능성을 정리합니다.
- 출처/시각: Naver Cloud / 2026-05-27 09:00 KST
- 링크: [원문 보기](https://www.ncloud.com/product/aiService)

## 2. 백엔드/개발자 기술

### 2-1. 카카오 기술 블로그 백엔드 사례
- 무슨 일: 국내 대규모 서비스 운영 사례를 확인할 수 있습니다.
- 왜 나에게 중요한가: 장애 대응과 API 설계 면접 소재로 활용할 수 있습니다.
- Kotlin/Spring Boot 관련성: Spring 기반 API 서버 설계와 비교해 정리하기 좋습니다.
- 내 액션: 아키텍처 선택 이유를 포트폴리오 메모로 남깁니다.
- 출처/시각: Kakao Tech / 2026-05-27 09:00 KST
- 링크: [원문 보기](https://tech.kakao.com/)

## 오픈소스 기여 후보
- 오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다.

## 오늘 할 일
- AI API 인증 방식을 정리합니다.
- Spring 운영 사례 키워드를 기록합니다.
"""

weekly_valid = """# Career Feed - Backend Career Weekly
기준시각: 2026-05-27 09:30 KST

이번 주 요약:
- 이번 주는 백엔드 인턴과 경진대회 지원 가능성을 먼저 확인합니다.

## 이번 주 추천 TOP 5

### 1. 백엔드 채용연계형 인턴
- 유형: 인턴
- 대상 적합성: 학생/신입 지원 가능성이 있어 확인 가치가 있습니다.
- 백엔드 적합성: 서버 API 개발 경험과 직접 관련됩니다.
- Kotlin/Spring Boot 관련성: Java/Spring Boot 경험을 요구합니다.
- 마감: 2026-06-30
- 왜 나에게 맞는가: 신입 백엔드 포트폴리오와 연결하기 좋습니다.
- 내 액션: 지원 자격과 과제 여부를 확인합니다.
- 출처: Wanted
- 링크: [원문 보기](https://www.wanted.co.kr/)

## 마감 임박
- 이번 주 마감 임박 항목 없음

## 포트폴리오 관점 추천
- 데이콘 경진대회: API 서버와 모델 결과 저장 구조를 포트폴리오로 남기기 좋습니다. [원문 보기](https://dacon.io/competitions)

## 제외한 후보
- 시니어 백엔드 채용: 경력 5년 이상만 가능해 제외
"""

weekly_invalid = """# Career Feed - Backend Career Weekly
기준시각: 2026-05-27 09:30 KST

이번 주 요약:
- 마감 지난 항목을 추천하는 잘못된 예시입니다.

## 이번 주 추천 TOP 5

### 1. 오래된 백엔드 공고
- 유형: 신입
- 대상 적합성: 학생 지원 가능
- 백엔드 적합성: 서버 개발
- Kotlin/Spring Boot 관련성: Spring Boot
- 마감: 마감 지남
- 왜 나에게 맞는가: 확인용
- 내 액션: 확인
- 출처: Wanted
- 링크: [원문 보기](https://www.wanted.co.kr/)

## 마감 임박
- [원문 보기](https://dacon.io/competitions)

## 포트폴리오 관점 추천
- 없음
"""

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    daily = root / "daily.md"
    weekly = root / "weekly.md"
    invalid = root / "invalid.md"
    daily.write_text(daily_valid, encoding="utf-8")
    weekly.write_text(weekly_valid, encoding="utf-8")
    invalid.write_text(weekly_invalid, encoding="utf-8")

    run(["python3", "scripts/validate-kr-premium-brief.py", str(daily), "--type", "daily-tech"], check=True)
    run(["python3", "scripts/validate-kr-premium-brief.py", str(weekly), "--type", "weekly-career"], check=True)
    failed = run(["python3", "scripts/validate-kr-premium-brief.py", str(invalid), "--type", "weekly-career"]).returncode
    if failed == 0:
        raise SystemExit("Weekly career invalid sample should have failed.")
PY

echo "==> Checking required files"
required_files=(
  "reports/sample-daily-news.md"
  "configs/channels.json"
  "configs/audience-profile.json"
  "configs/kr-sources.json"
  "configs/sources.json"
  "docs/channels.md"
  "docs/cost-policy.md"
  "refs/categories/ai-news.md"
  "refs/categories/backend-news.md"
  "refs/categories/security-alerts.md"
  "scripts/collect-feeds.py"
  "scripts/collect-kr-feeds.py"
  "scripts/render-brief.py"
  "scripts/render-overview.py"
  "scripts/send-category-briefs.py"
  "scripts/build-ai-input.py"
  "scripts/validate-kr-premium-brief.py"
  "tests/fixtures/kr-premium-brief-valid.md"
  "tests/fixtures/kr-premium-brief-invalid-generic.md"
  ".github/codex/prompts/compact-brief.md"
  ".github/codex/prompts/daily-news.md"
  ".github/codex/prompts/kr-tech-daily-brief.md"
  ".github/codex/prompts/kr-backend-career-weekly.md"
  ".github/codex/prompts/kr-premium-brief.md"
  ".github/workflows/daily-feed.yml"
  ".github/workflows/ai-brief-manual.yml"
  ".github/workflows/daily-news.yml"
  ".github/workflows/kr-tech-daily.yml"
  ".github/workflows/kr-backend-career-weekly.yml"
  ".github/workflows/kr-premium-brief.yml"
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
