# OSS 후보 저장소 정책

Daily Backend Brief의 OSS 후보는 `configs/oss-repositories.json`에 등록된 Java/Kotlin 백엔드 framework 저장소만 대상으로 합니다. 목표는 고정 issue 번호를 추천하는 것이 아니라, 매 실행마다 현재 GitHub issue 상태를 확인해 안전한 첫 기여 후보 1개 또는 OSS 기여 준비 루틴을 제공하는 것입니다.

GitHub issue에는 댓글, assign, label 변경 같은 mutation을 하지 않습니다. 이 프로젝트는 issue 추천과 로컬 progress 기록만 수행합니다.

## 저장소 우선순위

Daily 후보는 아래 순서로 Spring 생태계를 먼저 보고, 이후 JVM/Kotlin framework와 테스트 도구로 확장합니다.

1. `spring-projects/spring-security` - priority A, initial fit 90
2. `spring-projects/spring-restdocs` - priority A, initial fit 84
3. `spring-projects/spring-boot` - priority A, initial fit 82
4. `gradle/gradle` - priority B, initial fit 78
5. `ktorio/ktor-documentation` - priority B, initial fit 76
6. `quarkusio/quarkus` - priority B, initial fit 74
7. `testcontainers/testcontainers-java` - priority B, initial fit 72
8. `micronaut-projects/micronaut-core` - priority B, initial fit 70
9. `spring-projects/spring-framework` - priority C, initial fit 66

`ktorio/ktor`와 `Kotlin/kotlinx.coroutines`는 low-frequency weekly observation 대상으로만 둡니다. Daily 후보에서 primary 9개 저장소를 밀어내지 않습니다.

## 저장소 Profile 필드

- `repository`: GitHub `owner/name` 형식입니다.
- `display_name`: 브리핑에 사람이 읽기 좋게 표시할 저장소명입니다.
- `priority`: `A`, `B`, `C` 중 하나입니다.
- `initial_fit_score`: 저장소 자체가 주니어 백엔드 첫 기여에 맞는 정도입니다.
- `ecosystem_tags`: Spring, JVM, Kotlin, security, testing 같은 생태계 분류입니다.
- `preferred_contribution_types`: `docs`, `test`, `sample`, `bug-repro`, `javadoc`, `kdoc`, `error-message` 중 추천할 수 있는 기여 유형입니다.
- `beginner_labels`: 해당 저장소에서 beginner-friendly 근거로 볼 수 있는 label입니다.
- `positive_title_keywords`: 제목/본문에 있으면 가점이 되는 키워드입니다.
- `avoid_labels`: 있으면 추천하지 않는 label입니다.
- `avoid_title_keywords`: 제목에 있으면 추천하지 않는 키워드입니다.
- `contribution_guide`: 기여 전 확인할 가이드입니다.
- `search_urls`: 다음 탐색에 사용할 GitHub 검색식입니다.
- `local_check_hints`: 첫 30분 로컬 확인에 쓸 명령이나 확인 경로입니다.
- `docs_or_test_hints`: 문서 또는 테스트 위치를 좁히는 힌트입니다.
- `junior_notes`: 왜 주니어 백엔드 개발자에게 적합하거나 조심해야 하는지 적습니다.

## 100점 Scoring 모델

후보 score는 100점 만점입니다.

- `technical_fit`: 30점
- `external_contribution_signal`: 20점
- `scope_clarity`: 15점
- `validation_feasibility`: 15점
- `maintainer_signal`: 10점
- `portfolio_value`: 10점

해석 기준은 다음과 같습니다.

- 85점 이상: 오늘의 최우선 후보
- 75-84점: top 3 후보 가능
- 65-74점: 보류 또는 주간 후보
- 64점 이하: Daily 추천 제외

후보 JSON에는 `score`, `score_breakdown`, `repository_initial_fit_score`, `repository_priority`, `repository_ecosystem_tags`, `repository_local_check_hints`, `repository_docs_or_test_hints`, `repository_junior_notes`, `junior_fit_evidence`를 남겨 Markdown 생성과 validator가 근거를 확인할 수 있게 합니다.

## Safe Candidate Gate

`safe_to_recommend=true`가 되려면 모든 조건을 만족해야 합니다.

- issue가 open 상태입니다.
- issue가 configured repository에 속합니다.
- assignee가 없습니다.
- linked PR 또는 linked branch가 없습니다.
- linked work 확인이 완료되었습니다. GitHub GraphQL 확인이 실패하거나 불완전하면 추천하지 않습니다.
- 댓글이나 본문에 "I'll work on this", "I'm working on this", "can I take this", "I'd like to work on this"처럼 작업 의사를 밝힌 흔적이 없습니다.
- issue 작성자가 maintainer/member/collaborator이거나, 저장소 profile의 beginner-friendly label이 있습니다.
- contribution type이 저장소별 `preferred_contribution_types`에 포함됩니다.
- 저장소별 `avoid_labels`와 `avoid_title_keywords`에 걸리지 않습니다.
- score가 65점 이상입니다.

## Positive Signal

다음 label과 키워드는 가점 신호로 봅니다.

- `good first issue`
- `help wanted`
- `ideal-for-contribution`
- `first-timers-only`
- `documentation`
- `docs`
- `testing`
- `javadoc`
- `kdoc`
- `sample`
- `example`
- `bug`
- `reproducible`
- `comprehensibility`

추천 유형은 문서, 예제, 테스트, 재현 sample, Javadoc/KDoc, 오류 메시지, 작고 범위가 명확한 bug fix입니다.

## Exclusion Signal

다음 label, 제목, 본문 신호가 있으면 추천하지 않습니다.

- `team-only`
- `blocked`
- `on-hold`
- `pending-design-work`
- `needs-design`
- `needs-decision`
- `internal-feedback`
- `breaking-change`
- `major`
- `epic`
- `security vulnerability`
- `CVE`
- `release blocker`
- broad design proposal, RFC, major API change

보안 취약점, 릴리스 차단, breaking change, 내부 구현, 대규모 설계 논의는 학습 가치가 있어도 Daily 첫 기여 후보로 추천하지 않습니다.

## Fallback 동작

안전한 후보가 없으면 특정 issue URL을 만들거나 추정하지 않습니다. Daily Brief는 `오늘의 OSS 기여 준비 루틴`을 출력합니다.

준비 루틴은 다음과 같은 30분 행동 중 하나여야 합니다.

- Spring Security `CONTRIBUTING.adoc`와 docs 빌드 절차 확인
- Spring REST Docs 문서 빌드와 sample snippet 위치 확인
- Spring Boot docs/test 위치 확인
- Gradle Kotlin DSL docs issue 검색식 저장
- Testcontainers Java Spring Boot example 문서 확인

준비 루틴에도 `저장소`, `30분 액션`, `확인할 문서`, `다음에 issue를 찾을 때 쓸 GitHub 검색식`, `기여 전 매너`를 포함합니다. GitHub issue URL은 포함하지 않습니다.

## 첫 달 운영 전략

- Week 1: Spring Security, Spring REST Docs, Spring Boot issue와 기여 가이드만 관찰합니다.
- Week 2: 문서 issue 1개를 분석하고, 필요하면 "작은 docs/test/example 범위로 확인해도 되는지" 조심스럽게 댓글 초안을 준비합니다.
- Week 3: 작은 docs PR 또는 reproducer/sample PR을 목표로 합니다.
- Week 4: Gradle, Ktor Documentation, Quarkus까지 관찰 범위를 넓힙니다.

## 유지보수 기준

- 저장소 추가보다 기존 저장소 profile의 label, 검색식, 힌트를 먼저 보강합니다.
- Secret, token, Webhook URL, 실제 credential 값은 config에 넣지 않습니다.
- OpenJDK/JBS는 참고 모델로만 사용하고 직접 수집하지 않습니다.
- `reports/` 산출물은 기본적으로 커밋하지 않습니다.
