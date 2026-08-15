# AGENTS.md

이 문서는 Codex가 Career Feed 저장소에서 작업할 때 따를 규칙을 정의한다.

## 제품 범위

- Career Feed는 개인용 한국어 백엔드 성장 루프다.
- Daily는 아직 풀지 않은 Programmers 문제 1개와 공식 Spring Boot 또는 Spring AI 안정 릴리스 1개만 결정론적으로 렌더링한다.
- 완료 상태는 `data/progress.json`에서만 관리한다.
- 예약 실행은 GitHub Actions, 전송은 선택적 Discord Webhook만 사용하며 기본 목표 시각은 `Asia/Seoul` 09:00이다.
- 사용자 발송 시각은 `configs/delivery-schedule.json`에서만 바꾸고 workflow 예약 블록은 동기화 스크립트로 생성한다.
- `lab/`는 Kotlin/Java/Spring 과제를 실제 코드와 테스트로 검증하는 최소 실습 모듈이다.
- 별도 OSS 경로는 allowlist의 공개 GitHub 이슈를 읽기 전용으로 조회하고 실행 가능한 후보를 최대 2개 노출하며 외부 저장소를 수정하지 않는다.
- 새소식은 allowlist에 고정된 Spring Boot·Spring AI 공식 GitHub Releases API만 허용하고 `published_at`을 발행일로 사용한다. 일반 AI 동향, 블로그·뉴스·소셜 미디어·투자 정보 수집은 범위 밖이다.
- LLM/API 생성, 다국어, 상시 실행 서버, 운영 데이터베이스, 웹 UI, 배포 인프라는 범위 밖이다.

## 변경 원칙

- 요청한 문제를 해결하는 최소 변경만 한다.
- 한 번만 쓰는 로직을 추상화하지 않는다.
- 커리큘럼 항목 ID를 변경하거나 제거할 때 진행 파일과의 호환성을 확인한다.
- Secret, 토큰, Webhook URL을 코드·문서·fixture에 하드코딩하지 않는다.
- `reports/` 생성물과 사용자의 미추적 파일을 커밋 대상으로 만들지 않는다.
- 새 외부 의존성은 표준 라이브러리로 해결할 수 없을 때만 추가한다.
- OSS 자동화는 issue 조회와 artifact/Discord 렌더링까지만 허용한다. comment, assign, label, branch, fork, PR 생성은 금지한다.
- 핵심 lesson과 lab 검증은 별도 학습 계약으로 유지하고 Daily에는 lesson을 렌더링하지 않는다.
- 코드 주석은 영어, 사용자 브리핑과 README는 한국어를 기본으로 한다.

## 활성 경로

- `scripts/generate_backend_daily.py`
- `scripts/mark_progress.py`
- `scripts/send_discord.py`
- `scripts/collect_spring_updates.py`
- `scripts/collect_oss_candidates.py`
- `scripts/record_oss_shadow.py`
- `scripts/check_oss_delivery_gate.py`
- `scripts/sync_delivery_schedule.py`
- `lab/`
- `.github/workflows/backend-daily.yml`
- `.github/workflows/mark-progress.yml`
- `.github/workflows/oss-weekly.yml`
- `.github/workflows/pr-checks.yml`

## 검증

- 기본 검증 명령은 `./scripts/validate.sh`다.
- 스크립트 변경 시 관련 `unittest`를 추가하거나 수정한다.
- config 변경 시 JSON 문법, ID 고유성, 준비 조건, 완료 증거, 필수 필드, HTTPS 참고 링크를 확인한다.
- 생성 경로는 임시 파일로 검증하며 `reports/`에 테스트 산출물을 남기지 않는다.
- `lab/` 변경 시 Gradle Wrapper 기반 테스트를 실행한다.
- Spring 새소식 경로는 공식 API allowlist, stable-only, `published_at` 기준 14일 freshness, 과거 기준일 이후 `updated_at` 변경 차단, 예약 timezone·현지 발송 시각 재현, 최대 10페이지 완전 소진 또는 fail-closed를 확인한다.
- OSS 경로는 fixture 검증, 요청 상한, fail-closed, live dry-run을 확인한다.
