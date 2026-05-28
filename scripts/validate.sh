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

daily_valid = """# Career Feed - Backend Daily
기준시각: 2026-05-27 09:10 KST

오늘의 방향:
- Spring 설정 흐름을 익히고 해시 문제를 이어서 풉니다.

## 1. 오늘의 Spring Boot/JVM 학습

### 주제: Spring Boot AutoConfiguration 흐름 읽기
- 핵심 개념: starter가 어떤 조건에서 bean을 등록하는지 확인합니다.
- 30분 실습: 작은 설정 클래스를 만들고 조건부 bean 등록을 테스트합니다.
- 검색 키워드: Spring Boot AutoConfiguration condition test
- 확장해서 볼 것: 테스트 slice와 설정 분리 방식
- 참고 링크: [원문 보기](https://www.ncloud.com/product/aiService)

## 2. 이번 주 PS 성장 루틴
- 이번 주 주제: 해시
- 이번 주 목표: Key-value 기반 조회와 빈도 처리를 익힙니다.
- 현재 진행: 1/5
- 오늘 문제: 전화번호 목록
- 플랫폼: Programmers
- 난이도: Level 2
- 먼저 생각할 것: 정렬 후 인접한 번호의 접두어 관계를 확인합니다.
- 오늘 목표: 정답 코드보다 조건을 먼저 말로 정리합니다.
- 막히면 검색: 프로그래머스 전화번호 목록 Kotlin startsWith
- 링크: [문제 보기](https://school.programmers.co.kr/learn/courses/30/lessons/42577)

## 3. 오픈소스 기여 후보

- 오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다.

## 4. 한국 개발/AI 뉴스

### 뉴스: 국내 개발자 플랫폼 업데이트
- 제목: 카카오 기술 블로그 백엔드 사례
- 핵심: 국내 대규모 서비스 운영 사례를 확인할 수 있습니다.
- 공부로 연결할 점: API 장애 대응 기록을 학습 메모로 연결합니다.
- 검색 키워드: Spring Boot API resilience
- 링크: [원문 보기](https://tech.kakao.com/)

## 오늘 할 일
1. AutoConfiguration 조건을 한 가지 테스트합니다.
2. Programmers 해시 문제를 30분 안에 시도합니다.
3. 풀었다면 Mark PS Solved workflow로 기록한다.
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
