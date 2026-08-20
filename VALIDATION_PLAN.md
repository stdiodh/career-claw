# Validation Plan

## Goal

현재 GitHub 상태가 불완전하거나 후보가 이미 선점된 경우 추천하지 않고, 완전한 증거가 있을 때만 최대 3개 후보를 결정론적으로 출력한다.

## Static Checks

- `career-feed` Bash 문법
- Python syntax
- config와 fixture JSON 문법
- 활성 workflow 두 개와 read-only 권한
- pinned GitHub Actions
- 제거한 Daily, lab, Discord와 GitHub 쓰기 경로 부재
- whitespace 오류 부재

## Config Contract

- schema version 4
- Tier A 저장소 세 개와 탐색 순서
- 분기 안에 끝나는 검토 유효기간
- shortlist 5개, recommendation 3개, API 21회 상한
- 100점 점수 합계
- HTTPS CONTRIBUTING URL
- shell metacharacter가 없는 Gradle 검증 명령

## Fixture Contract

`tests/fixtures/oss-api-responses.json`은 다음 경로를 재현한다.

- repository 활성 상태
- 저장소별 검색 결과
- issue detail, comments와 timeline
- 추천 가능한 문서·테스트 후보
- 작업 선점 댓글
- 설계 미결정 후보
- rate-limit header

fixture 검증은 결과가 실행마다 같고 다음 상한을 지키는지 확인한다.

```text
shortlist <= 5
recommendations <= 3
requests <= 21
0 <= score <= 100
```

## Hard Gates

테스트는 다음 상태가 점수와 관계없이 제외되거나 전체 추천을 차단하는지 확인한다.

- closed, locked 또는 assigned issue
- 허용하지 않은 repository 또는 issue URL
- exclusion label
- 연결 PR
- 작업 선점 댓글
- 오래되거나 확인할 수 없는 maintainer 활동
- 미결정 설계
- 불완전 API payload
- comments 또는 timeline pagination
- request 또는 rate-limit 오류

## Commands

전체 검증:

```bash
./scripts/validate.sh
```

공개 API read-only smoke test:

```bash
temporary="$(mktemp -d)"
python3 scripts/collect_oss_candidates.py \
  --live-dry-run \
  --json-output "${temporary}/oss-candidates.json" \
  --markdown-output "${temporary}/oss-candidates.md"
```

live 결과에 후보가 없는 것은 실패가 아니다. HTTP, pagination 또는 계약 검증 오류로 `complete=false`인 결과는 실패다.
