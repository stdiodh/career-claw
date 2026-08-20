# OSS Contribution Recommendation Guide

Java/Kotlin Backend 경험으로 실제 첫 PR까지 끝낼 가능성이 높은 Spring 생태계 issue를 고르는 기준이다.

특정 issue를 고정하지 않는다. 실행할 때마다 현재 GitHub 상태를 확인한다.

## Contribution Profile

다음 경험과 연결되는 기여를 우선한다.

- Kotlin과 Spring Boot
- 인증·인가, OAuth2, JWT와 OIDC
- API와 error contract
- logging, observability와 operations
- 단위·통합·회귀 테스트
- reference documentation과 tutorial

첫 기여 유형은 다음 순서를 기본값으로 사용한다.

1. Documentation
2. Example 또는 Sample
3. Test 또는 Reproduction
4. Javadoc 또는 KDoc
5. Small Bug Fix

Public API 변경, breaking change, 대규모 refactoring, architecture 변경, pending design과 공개 security vulnerability 작업은 추천하지 않는다.

## Repository Pool

현재 구현은 Tier A만 매 실행 확인한다.

1. `spring-projects/spring-security`
2. `spring-projects/spring-restdocs`
3. `spring-projects/spring-boot`

Tier A에서 추천 품질을 확인한 뒤 Tier B와 Tier C를 별도 PR로 확장한다. Tier는 프로젝트 중요도가 아니라 현재 기여 접근 순서를 의미한다.

## Candidate Signals

저장소마다 label 문자열이 다르므로 config가 다음 의미를 실제 label에 매핑한다.

긍정 신호:

- first contribution 또는 ideal for contribution
- help wanted
- documentation, example 또는 sample
- test, reproduction 또는 regression
- small bug

경고 또는 제외 신호:

- team only
- blocked 또는 on hold
- pending design 또는 needs decision
- breaking change 또는 epic
- security vulnerability

## Candidate Validation

제목과 label만 보고 추천하지 않는다. 상세 후보마다 다음을 확인한다.

- issue가 open인가?
- assignee가 없는가?
- 다른 기여자가 작업 의사를 밝히지 않았는가?
- 연결되거나 중복된 PR이 없는가?
- 최근 maintainer 활동이 있는가?
- 한 가지 목적으로 범위를 제한할 수 있는가?
- CONTRIBUTING과 로컬 검증 명령이 있는가?

comments 또는 timeline이 한 페이지를 넘으면 보이지 않은 선점이나 연결 PR이 있을 수 있으므로 전체 추천을 차단한다.

## Scoring

| Category | Score | Question |
| --- | ---: | --- |
| Skill Fit | 30 | 현재 Backend 경험과 직접 연결되는가? |
| Contribution Signal | 20 | 외부 기여를 원하는 신호가 있는가? |
| Scope Clarity | 15 | 작은 PR로 범위를 제한할 수 있는가? |
| Validation | 15 | 변경 결과를 직접 검증할 수 있는가? |
| Maintainer Activity | 10 | 최근 triage와 review가 있는가? |
| Learning Value | 10 | 첫 기여와 기술 학습 가치가 있는가? |

점수 해석:

```text
85-100  Analyze today
75-84   Strong candidate
65-74   Keep for later
0-64    Skip today
```

75점 이상이어도 hard gate가 있으면 추천하지 않는다. 점수는 현재 상태 검증을 대체하지 않는다.

## Daily Workflow

```text
Discover
→ Filter
→ Validate
→ Score
→ Decide
```

- 검색 후보를 저장소별로 정렬한다.
- 저장소 편향을 줄이기 위해 Tier A를 순환한다.
- 최대 5개만 상세 검증한다.
- 최대 3개만 추천한다.
- 실제 행동할 후보는 첫 번째 추천 하나로 제한한다.

## Daily Output

추천 결과는 다음 구조를 사용한다.

```text
Summary
Recommendation 1..3
Excluded
Today
Limitations
```

각 추천에는 repository, issue URL, 현재 상태, 점수, 마지막 수정 시각, 추천 이유, 범위, 검증 방법, 위험과 첫 행동을 포함한다.

## First Action

좋은 issue를 찾았다고 바로 수정하거나 댓글을 남기지 않는다.

```text
Read
→ Reproduce
→ Locate
→ Plan
→ Communicate
→ Change
→ Verify
```

도구가 수행하는 범위는 현재 상태 확인과 첫 행동 제안까지다. 외부 comment, assign, branch, fork와 PR 생성은 자동화하지 않는다.

## Before Opening an External PR

- issue와 연결 PR 상태를 다시 확인한다.
- 한 가지 목적만 변경한다.
- 관련 없는 refactoring과 formatting을 포함하지 않는다.
- 문제를 변경 전에 재현한다.
- 실제로 실행한 검증만 PR에 작성한다.
- 대상 저장소의 CONTRIBUTING과 PR convention을 우선한다.

좋은 첫 기여는 큰 기능이 아니라 문제를 정확히 이해하고 작은 변경으로 해결한 검증 가능한 PR이다.
