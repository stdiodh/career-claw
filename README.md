# Career Feed

Career Feed는 현재 GitHub 상태를 확인해 실제 첫 기여로 이어질 가능성이 높은 Spring 생태계 오픈소스 이슈를 추천하는 개인용 도구입니다.

LLM, 데이터베이스, 웹 서버를 사용하지 않습니다. 공개 GitHub REST API를 읽기만 하며 외부 저장소에 comment, assign, label, branch, fork, PR을 만들지 않습니다.

## 현재 범위

매 실행마다 Tier A 저장소를 다음 순서로 확인합니다.

1. `spring-projects/spring-security`
2. `spring-projects/spring-restdocs`
3. `spring-projects/spring-boot`

검색 결과 중 최대 5개를 issue detail, comments, timeline으로 다시 검증하고 최대 3개를 추천합니다.

- Best actionable candidate
- Safe docs/test candidate
- Learning candidate

추천할 후보가 없어도 정상입니다. API 응답이나 검증 증거가 불완전하면 전체 추천을 fail closed합니다.

## 빠른 시작

Python 3만 필요합니다. 별도 패키지 설치나 GitHub token은 필요하지 않습니다.

```bash
./career-feed
```

결과는 터미널에 출력되고, Git에서 무시되는 `reports/oss-candidates.json`과 `reports/oss-candidates.md`에도 기록됩니다.

저장소 전체 검증은 다음 명령으로 실행합니다.

```bash
./career-feed check
```

## 추천 과정

### Discover

저장소별 실제 label을 기여 신호의 의미에 맞게 config에서 관리합니다.

- `first-timers-only`, `ideal-for-contribution`
- documentation, test, sample
- small bug or regression

정확한 label 이름은 저장소마다 다르지만 점수는 동일한 의미 범주로 계산합니다.

### Filter

검색 단계에서 다음 후보를 제외합니다.

- closed 또는 locked issue
- assignee가 있는 issue
- exclusion label이 있는 issue
- 최근 180일 안에 갱신되지 않은 issue
- 허용한 저장소와 URL이 일치하지 않는 결과

### Validate

최대 5개 후보에 대해 현재 상태를 다시 확인합니다.

- open 상태와 assignee
- 연결된 PR
- 외부 기여자의 작업 선점 댓글
- 최근 maintainer 활동
- 범위, 완료 조건과 재현 근거
- 공식 CONTRIBUTING 문서와 Gradle 검증 명령

comments 또는 timeline이 한 페이지를 넘거나 API 응답이 불완전하면 추천을 노출하지 않습니다.

### Score

후보는 100점 기준으로 평가합니다.

| Category | Score |
| --- | ---: |
| Skill Fit | 30 |
| Contribution Signal | 20 |
| Scope Clarity | 15 |
| Validation | 15 |
| Maintainer Activity | 10 |
| Learning Value | 10 |

75점 이상이더라도 연결 PR, 작업 선점, 설계 미결정이나 불완전 증거가 있으면 추천하지 않습니다. 점수 계산 결과는 JSON의 `score_breakdown`에 남습니다.

### Decide

추천 결과에는 다음 정보가 포함됩니다.

- repository와 issue URL
- 현재 상태와 마지막 수정 시각
- 기여 유형, 난이도와 점수
- 추천 이유와 예상 범위
- 검증 명령, 위험과 첫 행동
- 중요한 제외 후보와 제외 이유

첫 행동은 CONTRIBUTING 확인, 기준선 테스트, 재현까지입니다. Maintainer 댓글이나 코드 변경은 사용자가 현재 상태를 다시 확인한 뒤 직접 결정합니다.

## 결정론적 fixture 실행

네트워크 없이 수집 계약을 재현할 수 있습니다. 생성물은 임시 경로에 두어 `reports/`에 테스트 파일을 남기지 않습니다.

```bash
temporary="$(mktemp -d)"
python3 scripts/collect_oss_candidates.py \
  --fixture tests/fixtures/oss-api-responses.json \
  --json-output "${temporary}/oss-candidates.json" \
  --markdown-output "${temporary}/oss-candidates.md"
```

종료 코드는 다음 의미입니다.

- `0`: 완전한 수집
- `1`: config, fixture 또는 로컬 실행 오류
- `2`: GitHub 수집 증거가 불완전해 추천 차단

## GitHub Actions

`OSS Recommendations` workflow는 수동 실행만 지원합니다. 읽기 전용 권한으로 JSON과 Markdown을 생성해 실행 요약과 14일 artifact로 보존합니다.

예약 실행, Discord 전송과 품질 ledger는 현재 범위에 없습니다. 추천 품질을 실제로 검토한 뒤 각각 별도 PR로 추가합니다.

## 계약 파일

- [추천 기준](./OSS_RECOMMENDATION_GUIDE.md)
- [저장소·점수 config](./configs/oss-repositories.json)
- [검증 계획](./VALIDATION_PLAN.md)
- [보안 정책](./SECURITY.md)

config는 검토일부터 최대 한 분기만 유효합니다. `valid_until`이 지나면 오래된 label과 기여 정책으로 추천하지 않도록 실행을 거부합니다.

## 후속 확장 순서

현재 범위가 안정된 뒤 기능을 한 PR씩 추가합니다.

1. Tier A에 후보가 없을 때만 Tier B 조회
2. 예약 artifact 생성
3. opt-in Discord 전송
4. 추천에서 PR merge까지의 품질 ledger
5. 주간 기여 회고
