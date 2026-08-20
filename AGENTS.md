# AGENTS.md

이 문서는 Codex가 Career Feed 저장소에서 작업할 때 따를 규칙을 정의한다.

## 제품 범위

- Career Feed는 개인용 Spring 생태계 OSS 기여 추천 도구다.
- Tier A는 Spring Security, Spring REST Docs, Spring Boot 순서로 확인한다.
- 검색 결과 중 최대 5개를 상세 검증하고 최대 3개만 추천한다.
- 후보는 기술 적합도, 외부 기여 신호, 범위, 검증, maintainer 활동과 학습 가치로 100점 평가한다.
- 추천보다 현재 open 상태, assignee, 연결 PR, 작업 선점과 검증 가능성 확인을 우선한다.
- 공개 GitHub REST API를 인증 없이 GET으로만 사용한다.
- 외부 저장소의 comment, assign, label, branch, fork, PR 생성은 금지한다.
- LLM/API 생성, 데이터베이스, 웹 UI, 자동 코드 변경은 범위 밖이다.

## 변경 원칙

- 요청한 문제를 해결하는 최소 변경만 한다.
- 한 번만 쓰는 로직을 추상화하지 않는다.
- 저장소별 label 문자열보다 label이 나타내는 의미를 점수화한다.
- hard gate를 점수로 상쇄하지 않는다.
- API, comments 또는 timeline 검증이 불완전하면 전체 추천을 fail closed한다.
- issue body와 댓글 전문을 artifact에 저장하지 않는다.
- Secret, token과 credential을 코드, 문서, config, fixture에 넣지 않는다.
- `reports/` 생성물과 사용자의 미추적 파일을 commit하지 않는다.
- 새 외부 의존성은 Python 표준 라이브러리로 해결할 수 없을 때만 추가한다.
- 코드 주석은 영어, 사용자 브리핑과 README는 한국어를 기본으로 한다.

## 활성 경로

- `career-feed`
- `configs/oss-repositories.json`
- `scripts/collect_oss_candidates.py`
- `scripts/validate.sh`
- `tests/fixtures/oss-api-responses.json`
- `tests/test_collect_oss_candidates.py`
- `.github/workflows/oss-weekly.yml`
- `.github/workflows/pr-checks.yml`

## 검증

- 기본 검증 명령은 `./scripts/validate.sh`다.
- 수집기 변경 시 관련 `unittest`와 결정론적 fixture를 추가하거나 수정한다.
- config 변경 시 JSON 문법, Tier 순서, label 의미, 점수 합계, HTTPS URL, 안전한 검증 명령과 만료일을 확인한다.
- 생성 경로는 임시 파일로 검증하며 `reports/`에 테스트 산출물을 남기지 않는다.
- live dry-run은 외부 상태를 수정하지 않아야 하며 후보가 없는 결과도 정상으로 처리한다.
- 추천 수는 최대 3개, 상세 검증 수는 최대 5개, API 요청은 최대 21회인지 확인한다.
