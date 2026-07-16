# Career Feed 소스·OSS 검증 계획

상태: 로컬 구현·자동 검증 완료 · 사람 attestation/OSS runner/4주 shadow 대기
기준일: 2026-07-16
대상: 주니어~초급 실무 Kotlin/Java/Spring 백엔드 개발자

## 결론

기존 12개 설명·의사코드 중심 과제는 기본 순환에서 제거하고, 실제 Kotlin/Java/Spring lab test와 연결된 핵심 16개로 교체했다.

- Temurin 21.0.11+10, Spring Boot 4.1.0, Kotlin 2.4.10, Gradle 9.5.0, PostgreSQL 17.10을 하나의 profile로 고정했다.
- 핵심 16개 중 `JVM_CORE`는 15개(93.75%)다.
- 기본 lab test 25개와 pinned PostgreSQL test 1개가 통과했다.
- config, source claim과 immutable revision, 채용시장 audit, taxonomy, profile, lab content hash, test ID를 contract hash로 묶고 일치하는 `VERIFIED` 과제만 Daily에 노출한다.
- OSS 경로는 read-only collector와 artifact-only weekly workflow까지 구현했으며 Discord 승격은 달력 기준 Shadow gate로 잠갔다.

따라서 다음 두 검증을 분리한다.

1. 학습 과제 검증: 이 과제가 취업·실무 준비에 필요한지, 공식 소스와 실행 증거가 있는지 검증한다.
2. OSS 후보 검증: 현재 열려 있고, 선점되지 않았으며, Kotlin/Java/Spring과 관련된 최신 기여 후보인지 매 실행마다 검증한다.

이 문서는 검증 계약과 구현 후 판정의 단일 기준이다. 사용·운영 절차는 [README](./README.md), 상세 실행 결과는 [검증 증거](./audits/verification-evidence-2026-07-16.md)에서만 관리한다. 제품 문서는 한국어 단일 원본을 사용하고 코드 식별자·명령·공식 명칭만 영어로 유지하며, 삭제한 `docs/en/`·`docs/kr/` 복제 트리를 되살리지 않는다.

> 구현과 배포는 분리해 판정한다. 이 revision에는 5개 OSS 저장소·주간 최대 19회 조회·`LOCKED` gate와 네 workflow가 구현돼 있다. 기본 브랜치 병합 전 원격 상태는 위 검증 증거 문서에 역사 기록으로 고정하고, 병합 뒤에는 GitHub-hosted runner 결과를 별도 운영 증거로 추가한다.

## 1. 공통 원칙

### 1.1 `필수`의 정의

다음 중 하나를 만족해야 핵심 과제로 인정한다.

- 최근 목표 채용공고 표본에서 반복해서 요구된다.
- 다른 백엔드 역량의 선행 조건이다.
- 장애, 데이터 정합성, 보안 사고를 막기 위해 생략할 수 없다.

유명하거나 어려운 주제라는 이유만으로 핵심 과제에 넣지 않는다.

### 1.2 `최신 OSS 후보`의 정의

raw `updated_at`으로 정렬하지 않는다. 댓글이나 봇 동작만으로 오래된 이슈가 최신처럼 보일 수 있기 때문이다.

`최신 순`은 hard gate를 통과한 후보의 `created_at DESC`, `repository/number` 순으로 정의한다. 검색 결과의 preselect와 최종 출력에 같은 기준을 사용해야 API 요청 상한 안에서 정렬 정확성을 검증할 수 있다.

`last_maintainer_activity_at`은 정렬 기준이 아니라 freshness gate다. 다음 중 가장 최근 시각으로 계산한다.

- actor type이 bot이 아니고 author association이 `OWNER`, `MEMBER`, `COLLABORATOR`인 issue 생성 시각
- actor type이 bot이 아니고 `OWNER`, `MEMBER`, `COLLABORATOR`가 작성한 댓글
- bot이 아닌 사용자가 수행한 라벨, milestone, assignment timeline event

일반 사용자의 댓글로만 바뀐 `updated_at`은 최신성 근거로 인정하지 않는다.

### 1.3 비용 원칙

- LLM 모델 토큰과 유료 API 비용: 0
- GitHub API 요청: 주간 실행 최대 19회
- 전체 issue body와 댓글 전문 저장 금지
- 주간 실행 1회
- 후보 출력 최대 3개
- 후보가 없으면 정상적인 empty 결과로 처리

## 2. 학습 소스 검증

### 2.1 목표 버전 고정

과제 개편 전에 서로 호환되는 버전 묶음을 하나의 immutable verification profile로 고정한다.

- JDK distribution, 정확한 build 식별자, 배포 파일 checksum
- Spring Boot 정확한 patch 버전
- Spring Boot와 호환되는 Kotlin Gradle plugin 정확한 버전
- Gradle Wrapper 정확한 버전과 distribution checksum
- PostgreSQL image tag와 image digest
- 검증 profile ID와 생성일

기준일 현재 공식 문서는 [Spring Boot 4.1.0](https://docs.spring.io/spring-boot/system-requirements.html)과 [Kotlin 2.4.10](https://kotlinlang.org/docs/faq.html)을 안내한다. 최신 버전과 채용 시장에서 가장 많이 쓰는 버전은 같지 않을 수 있으므로, 단순히 최신 버전을 자동 선택하지 않는다.

profile은 `./gradlew test`와 PostgreSQL integration smoke test가 깨끗한 환경에서 통과해야 승인한다. 각각의 stable 버전을 독립적으로 조합하지 않는다.

각 과제에는 최소한 다음 메타데이터가 필요하다.

- 목표 JDK, Kotlin, Spring Boot 범위
- 과제가 검증하는 한 문장의 주장
- 그 주장을 직접 설명하는 공식 문서 절 또는 anchor
- 공식 문서의 release tag 또는 source commit permalink
- 마지막 의미 검토일
- 실행 명령과 객관적 완료 증거

### 2.2 필요성 근거 수집

분기마다 최근 60일 이내의 한국 신입 또는 경력 3년 이하 백엔드 채용공고 15개를 수동 표본으로 확인한다.

- 가능하면 회사의 직접 채용 페이지를 우선한다.
- 최소 5개 회사에서 수집하고 한 회사는 최대 2개까지만 포함한다.
- 한 업종이 전체 표본의 40%를 넘지 않게 한다.
- 같은 회사, 직무명, 요구사항 조합은 하나로 중복 제거한다.
- 공고 전문은 저장하지 않고 URL, 확인일, 경력 범위, 요구 기술 키워드만 기록한다.
- 15개 중 4개 이상에서 반복되면 시장 수요 근거로 인정한다.
- 빈도가 낮아도 보안·정합성·장애 대응의 선행 조건이면 별도 근거를 적고 유지할 수 있다.
- 각 공고는 허용된 신입·인턴·3년 이하 경력 범위 코드와 `INTERNSHIP_ENTRY_OR_MAX_3Y`를 사람이 확인했다는 구조화된 attestation을 남긴다. 자유 문자열 경력 범위는 허용하지 않는다.
- audit는 확인일로부터 최대 한 분기만 유효하며 `valid_until`이 지나면 Daily 생성을 fail closed한다.

키워드는 별도 taxonomy의 canonical ID와 alias로 집계한다. 예를 들어 `Spring`/`Spring Boot`, `JPA`/`Hibernate`, `테스트`/`JUnit`의 포함 관계를 표본 수집 전에 고정하고 중간에 바꾸지 않는다. 조건에 맞는 공고가 15개 미만이면 `INSUFFICIENT_SAMPLE`로 기록하고 4/15 판정을 수행하지 않으며, 기간이나 경력 범위를 자동으로 넓히지 않는다.

### 2.3 과제 평가표

각 항목을 0~2점으로 평가한다.

| 항목 | 0점 | 1점 | 2점 |
|---|---|---|---|
| 필요성 | 근거 없음 | 간접 근거 | 채용 반복 요구 또는 필수 선행 역량 |
| 소스 적합성 | 링크만 존재 | 관련 내용 일부 | 정확한 공식 절이 핵심 주장을 직접 뒷받침 |
| 스택 관련성 | JVM 사용 없음 | 개념만 연결 | Kotlin/Java/Spring 코드로 직접 실행 |
| 실패 재현 | 설명만 존재 | 예상 결과 존재 | 실패를 실제 테스트·명령으로 재현 |
| 실행 증거 | 주관적 완료 | 일부 결과 | 코드·테스트·SQL·로그 중 재현 가능한 증거 |

합격 조건은 8/10 이상이며 `소스 적합성=2`, `실패 재현=2`, `실행 증거=2`를 모두 만족해야 한다.

- `JVM_CORE` 과제는 `스택 관련성=2`가 필수다.
- `PLATFORM_CORE` 과제는 셸이나 SQL이 중심일 수 있지만 고정된 JVM 실습 앱을 대상으로 실행하고 `스택 관련성`이 1점 이상이어야 한다.
- 전체 핵심 과제 중 `JVM_CORE` 비율은 70% 이상이어야 한다.

### 2.4 기존 12개 정량화 전 1차 판정

| 과제 ID | 1차 판정 | 검증 시 필요한 변경 |
|---|---|---|
| `server-check-process` | 조건부 유지 | Python 서버 대신 JVM 프로세스로 바꾸고 `lsof`/`ss`와 thread dump를 직접 설명하는 공식 소스로 교체한다. |
| `perf-test-metrics` | 전면 보완 | 고정 배열 계산을 Spring endpoint와 Micrometer/JUnit 검증으로 바꾼다. |
| `api-post-idempotency-payment-duplicate` | 조건부 유지 | RFC 9110만으로 Idempotency-Key 저장 계약을 주장하지 않고, 실제 UNIQUE 제약과 동시 요청을 검증한다. |
| `db-index-design-for-read-traffic` | 유지 | 예상 plan이 아니라 PostgreSQL의 `EXPLAIN (ANALYZE, BUFFERS)` 전후를 남긴다. |
| `db-failure-transaction-considerations` | 조건부 유지 | Spring local transaction 문서만으로 외부 API 원자성을 주장하지 않고, 실패 상태 invariant와 재처리를 검증한다. |
| `external-integration-timeout` | 조건부 전면 보완 | 일반 REST Clients 문서 대신 실제 client 설정 소스를 연결하고 검증할 timeout 한 종류로 주장을 좁힌다. |
| `external-integration-retry` | 조건부 전면 보완 | 일반 REST Clients 문서 대신 retry 근거를 연결하고 attempt, backoff, deadline의 정답을 고정한다. |
| `async-transactional-outbox` | 선택 트랙 이동 | 실제 durable outbox 없이 `@TransactionalEventListener`만으로 설명하지 않는다. |
| `concurrency-db` | 유지 | 실제 동시 요청에서 성공 1건, 실패 1건, 최종 재고 0을 검증한다. |
| `security-authentication-authorization` | 조건부 유지 | 현재 lesson의 claim은 resource 소유권 authorization으로 좁히고 BOLA를 검증한다. authentication과 credential 처리는 별도 competency로 둔다. |
| `security-hmac-verification` | 선택 트랙 이동 | 유지한다면 Python이 아닌 Java JCA `Mac`과 replay 방지 테스트로 바꾼다. |
| `server-disk-capacity` | 운영 선택 트랙 이동 | Spring/JPA/테스트 핵심 과제 뒤에 배치한다. |

이 표는 개편 전 설명형 과제를 정성적으로 분류한 역사 기록이며 0~2점 정량 합격 판정으로 사용하지 않는다. 구현에서는 기존 12개를 기본 순환에서 모두 제거하고, 유지 가치가 있던 역량을 실행 가능한 핵심 16개에 다시 배치했다. outbox, HMAC, disk는 현재 제품 범위에서 삭제했으며 검증되지 않은 선택 트랙으로 노출하지 않는다.

### 2.5 과제 계약과 coverage matrix

과제의 설명만으로 합격을 판정하지 않는다. 구현 전에 각 lesson을 다음 필드와 연결한 `curriculum matrix`를 만든다.

- `lesson_id`
- `tier` (`core` 또는 `optional`)
- `core_type` (`JVM_CORE` 또는 `PLATFORM_CORE`)
- `coverage_areas`
- 원자적인 `competency_ids`
- `source_claims`와 immutable source revision
- `lab_repo`, `lab_revision`, `fixture_path`
- `verify_command`, `test_ids`, `expected_assertions`
- `verified_at`, verification profile ID

별도 competency registry가 각 `competency_id`를 하나의 coverage area에 연결한다. 한 과제에 여러 competency가 있으면 각각 별도 test ID가 있어야 한다. 일부 assertion만 통과한 과제로 영역 전체를 완료 처리하지 않는다.

최소 coverage 영역은 Java language, JVM runtime, Kotlin/JVM interop, Spring Web, Spring configuration, testing, JPA, SQL, transaction, authentication, authorization, security, observability, operations다. 각 영역은 최소 하나의 통과한 test ID와 연결돼야 한다.

현재 과제는 Phase 1에서 다음 acceptance contract를 먼저 확정한다.

- `perf-test-metrics`: latency fixture는 20개의 성공 요청, 실패 2건은 error count 전용으로 정의한다. 전체 처리량 2.2 req/s, 성공 처리량 2.0 req/s, 오류율 9.09%를 각각 이름 붙여 검증한다. fixed duration은 `Timer`에 직접 기록해 결정론적으로 검증하고, 실제 endpoint test는 count와 outcome tag만 assertion하며 wall-clock percentile을 exact 비교하지 않는다.
- `db-index-design-for-read-traffic`: PostgreSQL 정확한 버전, seed, row 수, 값 분포, query, warm-up 횟수, `ANALYZE` 실행을 고정한다. pinned 환경에서 target index가 plan에 나타나는지는 검증하되, timing과 raw buffer 감소는 관찰값으로만 기록하고 hard assertion으로 사용하지 않는다.
- `db-failure-transaction-considerations`: 결제 승인 후 DB 실패 시 허용 상태를 하나로 고정하고, 승인 유실 없이 idempotent reconciliation 후 최종 상태가 한 번만 완료되는 invariant를 검증한다.
- `external-integration-timeout`: 30분 핵심 과제는 underlying HTTP client를 고정한 response/read timeout 하나로 좁힌다. connect와 전체 deadline은 별도 과제로 검증하지 않는 한 이 lesson의 완료 주장에 포함하지 않는다.
- `external-integration-retry`: timeout 500ms, 최대 3회 시도, 100ms와 200ms backoff라면 계산상 budget은 1800ms다. fake sleeper 또는 virtual clock으로 시도 수와 요청된 sleep을 검증하고, 실제 wall clock을 1800ms exact assertion으로 사용하지 않는다. 사용되지 않는 400ms backoff를 완료 근거에 넣지 않는다.
- `concurrency-db`: barrier 또는 latch로 두 transaction의 동시 시작을 보장하고 성공 1건, 실패 1건, 최종 stock 0을 검증한다.
- `security-authentication-authorization`: 사용자 A가 자신의 resource에 성공하고 B의 resource에는 일관된 403 또는 404 정책으로 실패하는 BOLA assertion을 포함한다.

### 2.6 현재 빠진 핵심 과제

다음 영역을 검증하기 전에는 커리큘럼을 `완료`로 보지 않는다. 각 항목이 반드시 별도 lesson일 필요는 없지만, coverage matrix에서는 독립된 competency와 test ID로 검증한다.

1. Spring MVC DTO validation, `ProblemDetail`, `@ControllerAdvice`
2. 순수 unit, MVC slice, 실제 DB integration test의 차이
3. JPA persistence context, lazy loading, N+1, pagination, projection
4. Flyway 또는 Liquibase 기반 schema migration
5. Kotlin nullability, Spring proxy, `kotlin-spring`, Jackson Kotlin 경계
6. `@ConfigurationProperties`, profile, 환경변수, Secret 검증
7. health, 구조화 로그, request ID, HTTP metric을 연결한 장애 추적
8. Java language와 JVM runtime을 실제 Java 코드, thread, memory/GC 증거로 검증하는 과제
9. Spring Security authentication 성공·실패와 credential 처리 경계를 검증하는 과제

핵심 과제는 최대 16개로 제한한다. 새 항목을 계속 추가하지 않고, 낮은 우선순위 항목을 선택 트랙으로 이동한다.

### 2.7 실행 가능한 실습 저장소

제품 범위 승인 뒤 이 저장소의 `lab/`에 고정된 최소 Spring Boot 실습 모듈을 추가했다.

- Career Feed는 과제 순서와 완료 상태만 관리한다.
- 실습 저장소는 Kotlin/Java 코드, Gradle, PostgreSQL, 테스트를 관리한다.
- 모든 핵심 과제는 깨끗한 checkout에서 정확한 명령 하나로 재현돼야 한다.
- 각 lesson은 lab의 tracked input 전체로 계산한 immutable SHA-256 content revision과 fixture 경로를 참조한다.
- lab content revision이 바뀌면 모든 연결 test를 다시 실행하고 검증 manifest를 갱신한다.

아직 commit하지 않은 working tree에서도 검증을 강제할 수 있도록 commit SHA 대신 결정론적 lab content hash를 사용한다. `AGENTS.md`는 구현 전에 `lab/`와 read-only OSS 경로를 포함하도록 변경했다.

lesson config, source revisions와 검토일, verification profile, 채용시장 audit, taxonomy, Gradle dependency lock을 포함한 lab content hash, fixture path, verify command, test IDs, expected assertions를 canonical JSON으로 묶어 `contract_hash`를 계산한다.

Career Feed에는 전체 로그 대신 lesson ID, contract hash, lab content hash, profile ID, assertion별 pass/fail, 확인일을 담은 tracked verification manifest를 둔다. manifest의 contract hash가 현재 계약과 일치할 때만 `VERIFIED`다. 입력이 하나라도 바뀌면 `STALE`, 검증 이력이 없으면 `UNVERIFIED`다.

검증 enforcement가 활성화된 뒤에는 `STALE`과 `UNVERIFIED` lesson을 Daily Feed 기본 순환에서 제외한다. 원본 CI 로그는 선택적 보조 자료이며, 나중에 artifact가 만료돼도 감사할 수 있도록 assertion 결과 자체를 manifest에 남긴다.

### 2.8 학습 소스 합격 기준

- 핵심 과제의 공식 source claim 일치율 100%
- 핵심 과제의 `JVM_CORE` 비율 70% 이상
- 각 핵심 과제의 실패 재현과 완료 증거 확인 100%
- competency registry에 정의된 모든 최소 coverage area의 공백 0개
- 링크 HTTP 200 확인은 통과 조건이 아니라 보조 검사로만 사용
- 사람이 깨끗한 환경에서 각 과제를 최소 한 번 재현

## 3. Kotlin/Java/Spring OSS 후보 검증

### 3.1 저장소 allowlist

활성 후보는 최대 5개만 사용한다.

| 구분 | 저장소 |
|---|---|
| Spring 핵심 | `spring-projects/spring-boot` |
| Spring 핵심 | `spring-projects/spring-framework` |
| Kotlin 입문 후보 | `detekt/detekt` |
| Spring 관측성 | `micrometer-metrics/micrometer` |
| Java 통합 테스트 | `testcontainers/testcontainers-java` |

다음 저장소는 확장 후보로만 둔다.

- `spring-projects/spring-data-commons`
- `spring-projects/spring-data-jpa`
- `junit-team/junit-framework`
- `Kotlin/kotlinx.coroutines`

다음 저장소는 GitHub issue 자동 수집 대상에서 제외한다.

- `JetBrains/kotlin`: GitHub Issues가 활성화된 공식 issue tracker가 아니다.
- `ktorio/ktor`: 공식 CONTRIBUTING이 기여 후보를 YouTrack에서 찾도록 안내한다.
- `Kotlin/kotlinx.serialization`, `gradle/gradle`: 자동 추천에 사용할 명시적 contributor inclusion label이 확인되지 않았다.

`Kotlin/kotlinx.coroutines`는 기여 가이드가 있지만 첫 기여 난도와 빌드 비용이 높으므로 확장 단계에서만 검토한다.

allowlist 등록 조건은 다음과 같다.

- archived 또는 fork가 아니고 Issues가 활성화돼 있다.
- 공식 `CONTRIBUTING`과 로컬 build/test 방법이 있다.
- 최근 90일 안에 기본 브랜치 활동이 있다.
- 최근 90일 안에 외부 기여자의 PR이 실제 merge된 기록이 있다.
- proprietary 환경 없이 후보 모듈의 테스트를 로컬에서 실행할 수 있다.
- Kotlin/Java/Spring 백엔드 역량과 연결되는 기여 유형이 있다.

allowlist는 분기마다 다시 검토한다. 저장소가 유명하다는 이유만으로 조건을 면제하지 않는다.

2026-07-16 자동 감사에서 `spring-projects/spring-security`의 최근 90일 병합 PR 132건은 모두 Dependabot이었다. 외부 사람 기여자의 병합 근거가 0건이므로 OSS 수집 allowlist에서 제외했다. Spring Security 학습·인증/인가 lab은 이 결정과 무관하게 유지한다. 활성 5개는 `configs/oss-repositories.json` schema 2에 repository 상태, 기본 브랜치 활동 시각, 외부 사람 병합 PR, 공식 build/test 근거와 `valid_until=2026-10-14`를 기록하며, 만료·미래·내부 기여·archived/fork/proprietary 환경 증거는 collector 시작 전에 fail closed한다. 현재 감사는 GitHub REST와 공식 문서를 사용한 자동 감사이며 사람 attestation으로 표시하지 않는다.

### 3.2 후보 1차 검색

저장소별로 raw `updated_at`이 최근 180일인 후보를 `sort=created&order=desc`로 최대 10개 조회한다. server-side 정렬을 먼저 적용해야 잘린 결과 안에서도 최신 후보를 보장할 수 있다. `updated_at` 조건은 검색 범위를 줄이기 위한 prefilter일 뿐, 최종 최신성 판정에는 사용하지 않는다.

기본 조건:

- open issue
- assignee 없음
- 연결된 closing PR 없음
- locked 상태가 아님
- 저장소별 공식 contributor inclusion label
- archived repository 제외

GitHub는 `is:issue`, `is:open`, `no:assignee`, `-linked:pr`, label, created/updated 검색을 공식 지원한다. 저장소마다 라벨 이름이 다르므로 라벨 목록은 allowlist config에서 명시한다.

초기 저장소별 inclusion label은 다음처럼 고정한다.

| 저장소 | inclusion label |
|---|---|
| Spring Framework | `status: ideal-for-contribution` |
| Spring Boot | `status: ideal-for-contribution`, `status: first-timers-only` |
| detekt | `good first issue` |
| Micrometer | `help wanted` |
| Testcontainers Java | `good first issue` |

각 repository config에는 labels API로 확인한 `include_labels`, 정확한 `exclude_labels`, `module_label_to_build_command`, `contributing_url`, `checked_at`을 저장한다. `blocked 성격`처럼 자연어 또는 부분 문자열로 라벨을 추측하지 않는다. 예를 들어 Spring의 `status: blocked`, `status: waiting-for-feedback`, Testcontainers의 `resolution/waiting-for-info`, Micrometer의 `waiting for team`은 서로 다른 정확한 값으로 관리한다.

주간 실행마다 저장소별 labels API를 `per_page=100`으로 한 번 호출한다. config의 label이 사라지거나 이름이 바뀌면 해당 저장소 전체를 fail closed하고 allowlist 재검토 대상으로 돌린다. `Link: rel="next"`가 있어도 필요한 configured label이 첫 페이지에서 모두 확인되면 계약은 완전하다. 하나라도 첫 페이지에 없고 다음 page가 있으면 추가 요청 없이 `labels_pagination_incomplete`로 해당 저장소를 fail closed한다. 이 5회 호출은 주간 요청 상한에 포함한다.

상세 조회에서 유지보수자 활동이 90일 이내면 `FRESH`, 91~180일이면 `WARM`으로 분류하며 둘 다 후보가 될 수 있다. 180일을 넘으면 제외한다. 상세 검증한 최신 3개가 모두 탈락하면 범위를 자동으로 넓히지 않고 `최신 검색 후보 3개 중 READY_TO_ASK 없음`을 정상 결과로 낸다. 이는 전체 open issue에 안전한 후보가 없다는 뜻이 아니다.

현재 5개 계약의 2026-07-16 07:02 UTC 공식 API probe에서는 Testcontainers Java 1건, Micrometer 6건만 1차 조건을 만족했고 Spring Framework, Spring Boot, detekt는 0건이었다. 이는 특정 언어나 저장소의 후보를 억지로 채우면 안 된다는 기준 사례로만 사용하며, 숫자 자체는 매 실행마다 다시 계산한다.

### 3.3 후보 상세 검증

각 저장소에서 server-side 생성일 정렬로 받은 결과를 합치고 중복 제거한 뒤 `created_at DESC`, `repository/number`로 preselect한 최대 3개에 대해서만 issue detail, comments, timeline을 다시 조회한다. 상세 조회는 freshness와 선점 상태를 검증하며 정렬 기준을 바꾸지 않는다. API 상한 때문에 4번째 이후 후보를 backfill하지 않는 제한을 결과에 명시한다.

다음 중 하나라도 해당하면 제외한다.

- 이미 closed 됐거나 pull request 객체다.
- assignee가 있거나 작업 선점 댓글이 확인된다.
- 연결된 PR 또는 cross-reference PR이 있다.
- repository config의 exact `exclude_labels` 중 하나가 있다.
- bot 이벤트를 제외한 유지보수자 활동이 180일을 넘었다.

LLM 없이 body의 재현성, 설계 규모, 관련성을 추측하지 않는다. 자동 `READY_TO_ASK`는 exact label, assignee, linked work, freshness, repo/module mapping처럼 구조화된 필드만으로 결정한다.

- issue가 config의 module label과 매칭되면 해당 module의 고정 build/test 명령을 출력한다.
- module label이 없거나 config에 명령이 없으면 `MANUAL_REVIEW`로 둔다.
- body를 읽어 범위와 난도를 판정하는 작업은 Shadow run의 사람 검토에만 사용한다.

자동 검증이 작업 선점 여부를 확정하지 못해도 `MANUAL_REVIEW`로 둔다. Spring과 JUnit을 포함한 여러 프로젝트는 댓글로 기여 의사를 밝히고 maintainer 배정을 기다리도록 안내하므로, 브리핑에는 항상 이슈에서 착수 의사를 확인한 뒤 시작하라는 문구를 포함한다.

### 3.4 판정과 정렬

임의의 100점 점수는 사용하지 않는다.

- `READY_TO_ASK`: 모든 hard gate를 통과해 기여 의사를 문의할 수 있음
- `MANUAL_REVIEW`: 관련성은 있으나 선점·범위 확인이 불완전
- `EXCLUDED`: hard gate 실패와 정확한 사유 기록

Discord나 Markdown에는 `READY_TO_ASK`만 최대 3개 출력한다. preselect와 최종 정렬 모두 `created_at DESC`, `repository/number` 순이다. `last_maintainer_activity_at`은 FRESH/WARM 판정에만 사용한다.

각 항목에는 다음만 표시한다.

- repository와 issue 번호
- title과 URL
- 생성일, 마지막 수정일, 최종 확인일
- contribution label과 예상 유형(code/test/docs/sample)
- Kotlin/Java/Spring 관련 이유 한 줄
- 첫 30분에 확인할 build/test 명령

### 3.5 API와 인증

GitHub Actions의 기본 `GITHUB_TOKEN`은 workflow가 있는 저장소 범위로 제한되므로 외부 저장소 조회에 사용할 수 있다고 가정하지 않는다.

1. GitHub-hosted runner에서 공개 REST API를 인증 없이 19회 이하로 호출하는 spike를 수행한다.
2. core와 search bucket의 rate-limit header를 각각 기록하고 오류가 나면 후보를 보내지 않는다.
3. Shadow run 4회 모두 403/429 없이 끝나고 각 bucket의 reset 시각이 다음 예약 실행보다 앞서야 unauthenticated 운영을 승인한다.
4. 조건을 한 번이라도 만족하지 못하면 해당 실행은 fail closed하고 artifact-only 상태를 유지한다.
5. 현재 저장소에 한정된 `GITHUB_TOKEN` 또는 GitHub App installation token을 여러 외부 조직 조회의 fallback으로 사용하지 않는다. installation token은 App이 설치되고 접근을 부여받은 저장소로 범위가 제한되기 때문이다.
6. 개인 PAT와 기타 장기 credential은 제품 범위에 넣지 않는다. 인증 없는 운영이 runner에서 안정적이지 않으면 후보 전송을 활성화하지 않는다.

주간 실행은 labels contract 5회, 검색 5회, 최종 후보 3개의 detail/comments/timeline 9회를 합쳐 최대 19회다. Search는 별도 rate-limit bucket을 사용하므로 5회를 넘기지 않는다. 상세 조회가 최종 live validation이며 별도의 재조회는 하지 않는다.

comments와 timeline은 `per_page=100`으로 한 번만 요청한다. 응답에 다음 page가 있으면 일부 상태를 놓칠 수 있으므로 해당 후보를 `MANUAL_REVIEW`로 두고 추가 요청하지 않는다. 마지막 상세 응답이 성공한 시각을 `checked_at`으로 기록하고 즉시 렌더링한다.

### 3.6 테스트 계획

fixture 단위 테스트:

- 유지보수자 활동이 정확히 90일 전이면 `FRESH`, 91일 전이면 `WARM`
- 유지보수자 활동이 정확히 180일 전이면 `WARM`, 181일 전이면 제외
- 외부 댓글로 raw `updated_at`만 최근이 된 issue 제외
- bot의 label/milestone event는 유지보수자 활동에서 제외
- 입력 순서와 무관하게 생성일, repository/number 순으로 정렬
- closed, PR, assigned, linked PR, cross-reference PR 제외
- 선점 댓글과 위험 라벨 제외
- 중복 issue 제거
- allowlist 밖 URL과 repository 제외
- API 일부 실패 시 결과를 incomplete로 표시하고 Discord 전송 차단
- 실행당 19회 API 요청 상한 초과 시 실패

live contract 검증:

- detail/comments/timeline 상세 조회 자체를 최종 상태 검증으로 사용
- comments 또는 timeline에 다음 page가 있으면 `MANUAL_REVIEW`
- labels 응답에 다음 page가 있고 configured label이 첫 페이지에서 확인되지 않으면 해당 저장소 fail closed
- 마지막 상세 응답의 `checked_at`부터 출력까지 15분 이내
- 실제 GitHub 화면과 open, assignee, linked work 상태를 수동 비교
- 검색 결과가 비어 있어도 정상 종료

### 3.7 Shadow run과 출시 조건

처음 최소 4주 동안 Discord에 보내지 않고 artifact만 만든다.

- 주 1회, 최소 4회 실행
- 서로 다른 live 후보 최소 10개를 사람이 검토할 때까지 Shadow 기간 연장
- freshness 분류와 생성일 정렬 정확도 100%
- closed, assigned, linked, 선점된 후보 오추천 0건
- Kotlin/Java/Spring 관련성과 범위 명확성 80% 이상
- API 오류가 발생한 실행의 Discord 전송 0건

각 예약 실행은 JSON/Markdown과 별도로 workflow metadata를 생성한다. metadata에는 canonical repository/workflow/ref, `schedule` event, GitHub run ID와 attempt, head/workflow SHA, GitHub-hosted Linux runner, 실제 collector exit, Discord 전송 횟수, 두 출력의 SHA-256, 현재 Shadow contract hash가 들어간다. metadata builder는 기본 로컬 환경을 거부하고 recorder는 다운로드한 파일의 hash와 exact artifact schema를 다시 계산한다. sidecar 자체는 암호학적 증명이 아니므로 운영자는 기록 전에 GitHub의 immutable run 화면과 artifact를 다시 대조한다.

tracked gate schema 3은 다음 규칙으로 증거를 보존한다.

- attempt 1의 성공한 예약 실행만 주차로 계산한다.
- GitHub에서 성공적으로 artifact가 생성·업로드된 attempt 2 이상과 non-zero 실행은 운영자가 모두 기록하되 주차로 계산하지 않는다.
- 한 GitHub run의 attempt가 중간에 빠지거나 시간 순서가 역전되면 gate 전체를 거부한다.
- `run_at <= workflow_recorded_at <= attested_at <= review <= approval` 순서를 강제한다.
- warning, repository failure, HTTP 403/429, Discord 전송, 정렬·freshness 오판이 하나라도 있으면 해당 주를 제외한다.
- 관련 workflow/config/collector/recorder/gate 코드의 fingerprint가 바뀌면 기존 gate는 stale이 되어 새 Shadow 기간이 필요하다.
- Actions artifact는 run/attempt별 고유 이름과 retention 90일을 사용한다. `reports/` 본문은 git에 넣지 않고 gate에는 hash, READY candidate key, warning과 fail-closed 사유만 남긴다.
- recorder는 기록된 attempt의 중간 누락은 거부하지만 아직 기록하지 않은 마지막 재실행이나 metadata 생성 전 runner 실패를 GitHub API 없이 발견할 수 없다. 운영자는 `gh run view`의 전체 attempt/conclusion과 ledger를 대조한다.

사용자가 전체 phase 구현을 승인했으므로 별도 `OSS Weekly` workflow는 artifact-only로 먼저 추가했다. `OSS_DELIVERY_ENABLED`가 없으면 전송 step 자체가 실행되지 않는다. 달력 기준 Shadow 조건을 합격한 뒤에만 이 variable을 `true`로 바꾼다. Backend Daily에는 합치지 않으며, 두 번 연속 위험 후보가 나오면 variable을 제거해 즉시 artifact-only로 되돌린다.

같은 날의 반복 live probe는 API 계약과 rate-limit 동작을 검증하는 accelerated smoke일 뿐, 4주 관찰을 대체하지 않는다. 따라서 artifact 생성은 실제 사용 가능하지만 OSS Discord 자동 전송은 의도적으로 잠긴 상태가 정상이다.

## 4. 구현 단계

### Phase 0 — 기준 고정 (`AUTOMATED COMPLETE · HUMAN SCOPE ATTESTATION PENDING`)

- 호환성 smoke test를 통과한 immutable verification profile 결정
- in-repo `lab/`와 lesson별 pinned content hash 규칙 결정
- 최근 채용공고 15개 표본 작성
- `주간 read-only OSS 후보 수집`을 제품 범위에 넣을지 명시적으로 승인

완료 증거: `jvm-spring-2026q3-v1`, 최근 공고 15개/15개 회사 표본, 고정 taxonomy, `AGENTS.md` 범위 변경이 모두 반영됐다.

### Phase 1 — 현재 커리큘럼 감사 (`LOCAL VERIFIED · HUMAN CLEAN-CHECKOUT ATTESTATION PENDING`)

- 기존 12개를 정성적으로 삭제·교체 판정하고, 대체 핵심 16개만 평가표로 실제 채점
- source claim과 정확한 공식 문서 절 기록
- 선택 트랙 이동과 핵심 누락 항목 확정
- 실습 저장소에서 실패 재현과 완료 명령 검증

로컬 증거: 핵심 16개가 모두 9/10 이상이고 필수 항목은 전부 2점이다. 26개 stable `LAB-*` assertion, exact JDK x86_64 container, PostgreSQL digest test가 통과했다. profile/env-var binding과 blank Secret 시작 실패, request ID가 포함된 구조화 로그, 고정 3회 warm-up과 인덱스 전후 `EXPLAIN (ANALYZE, BUFFERS)`도 실제 테스트에 포함한다. build/cache를 제거한 독립 source snapshot과 빈 Gradle home에서도 전체 검증을 재현했지만, 사람이 commit된 clean checkout에서 전 과제를 재현했다는 attestation은 아직 없다.

### Phase 2 — OSS 수집기 prototype (`LOCAL COMPLETE · RUNNER SPIKE PENDING`)

- `AGENTS.md` 범위 변경이 이미 승인·반영됐는지 확인
- allowlist config
- 표준 라이브러리 기반 read-only REST collector
- fixture와 단위 테스트
- JSON과 Markdown artifact
- GitHub-hosted runner 인증·rate-limit spike

로컬 완료 증거: fixture 최대 경로 19/19 요청, empty 검색 10/19 요청, OSS 단위/계약 테스트, actor/assignee 불일치·archived·만료 allowlist fail-closed, unauthenticated live dry-run을 통과했다. 공유 IP quota가 0인 최초 probe도 exit 2와 전송 차단으로 끝났으며 reset 뒤 probe들은 정상 완료했다.

남은 완료 증거: 기본 브랜치에 병합된 revision으로 GitHub-hosted runner의 첫 artifact-only 실행을 수행하고 core/search bucket을 기록해야 한다. 로컬 공유 IP 실행은 runner spike를 대체하지 않는다.

### Phase 3 — Shadow run (`IMPLEMENTED · DEPLOYMENT/4-WEEK RUN PENDING`)

- 최소 4주, 주 1회 artifact-only 실행
- 서로 다른 live 후보 최소 10개 수동 검토까지 필요하면 기간 연장
- false positive와 제외 사유 기록

구현 완료 조건: 반복 live smoke, empty 결과, quota 오류, provenance metadata, strict artifact 검증, 실패/rerun ledger, artifact 생성과 전송 차단을 검증하고 주간 schedule을 artifact-only로 시작한다.

Discord 승격 조건: 달력이 다른 주간 실행 4회와 서로 다른 live 후보 10개 검토를 모두 충족한다. 현재 후보 부족 또는 시간 경과 전에는 `OSS_DELIVERY_ENABLED`를 설정하지 않는다.

승격은 운영자 약속만으로 처리하지 않는다. schema 3 gate에는 GitHub Actions provenance, metadata/artifact/Markdown hash, 실제 exit와 rate-limit, warning/repository failure, 정렬·freshness attestation, READY candidate key와 수동 리뷰를 기록한다. 미래·역순 시각, 누락 attempt, incomplete/non-zero, HTTP 403·429, source artifact에 없는 후보는 승인 증거가 될 수 없다. workflow는 이 결과, canonical repository/main, collector 성공과 `OSS_DELIVERY_ENABLED=true`를 모두 요구한다.

운영 순서는 다음과 같다.

1. `gh run view RUN_ID --repo stdiodh/career-feed`로 schedule/ref/SHA/attempt/conclusion을 확인한다.
2. `oss-weekly-RUN_ID-ATTEMPT` artifact를 내려받는다.
3. 실제 GitHub issue 화면과 정렬·freshness를 비교한다.
4. `record-run`으로 metadata와 실제 남은 JSON/Markdown, 두 attestation을 기록한다. exit 2는 두 artifact가 필수이고 exit 1은 metadata-only 또는 부분 출력도 nonqualifying evidence로 보존한다.
5. READY 후보마다 `record-review`로 관련성, 범위, false positive와 근거를 기록한다.
6. `check_oss_delivery_gate.py` 결과와 gate diff를 확인하고 gate JSON만 commit한다.
7. 조건을 채운 뒤 `approve`하고, 승인 commit이 원격 `main`에서 검증된 후에만 variable을 활성화한다.

### Phase 4 — 운영 결정 (`LOCAL COMPLETE · REMOTE RUN PENDING`)

- 사용자의 전체 phase 승인에 따라 주간 workflow 추가
- Discord 전송 전 마지막 live validation 수행

구현 완료 증거: sparse/empty는 정상 성공, API/rate-limit 오류는 fail closed, tracked gate는 현재 `LOCKED`, `OSS_DELIVERY_ENABLED` 제거가 추가 rollback이며 Discord는 Shadow gate 전까지 실행되지 않는다. 실제 GitHub Actions run은 병합된 revision에서 확인한다.

## 5. 최종 성공 기준

artifact-only 제품 구현은 다음 질문에 모두 `예`라고 답할 때 완료된다. OSS Discord 승격은 3.7의 시간 조건을 별도로 만족해야 한다.

- 이 과제가 왜 Kotlin/Java/Spring 백엔드 준비에 필요한지 근거가 있는가?
- 공식 소스의 정확한 절이 과제의 핵심 주장을 직접 설명하는가?
- 실제 JVM 코드와 테스트로 실패 전후를 재현했는가?
- OSS issue에 최근 180일 안의 유지보수자 활동이 있는가?
- 후보가 생성일 기준 최신 순으로 정렬됐는가?
- 현재 open이고 assignee와 연결 PR이 없는가?
- 실제로 외부 기여를 받는 활성 저장소인가?
- 불확실하거나 API가 실패했을 때 추천하지 않는가?
- LLM 모델 토큰 없이 주 1회, 19회 이하 GitHub API 요청으로 동작하는가?

## 6. 공식 근거

- [GitHub issue와 PR 검색 문법](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests)
- [GitHub issue timeline event](https://docs.github.com/en/rest/using-the-rest-api/issue-event-types)
- [GitHub issue labels REST API](https://docs.github.com/en/rest/issues/labels)
- [GitHub issue와 PR 연결](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
- [GitHub의 good first issue 안내](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/encouraging-helpful-contributions-to-your-project-with-labels)
- [GitHub의 첫 오픈소스 기여 안내](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-open-source)
- [GitHub REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [GitHub REST API best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
- [GitHub Actions `GITHUB_TOKEN` 범위](https://docs.github.com/en/actions/concepts/security/github_token)
- [GitHub Actions context와 run provenance](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
- [GitHub Actions 기본 run/runner 환경변수](https://docs.github.com/en/actions/reference/workflows-and-actions/variables)
- [Spring Framework contributing](https://github.com/spring-projects/spring-framework/blob/main/CONTRIBUTING.md)
- [Spring Boot contributing](https://github.com/spring-projects/spring-boot/blob/main/CONTRIBUTING.adoc)
- [Spring Security contributing — 다음 분기 OSS allowlist 재검토용](https://github.com/spring-projects/spring-security/blob/main/CONTRIBUTING.adoc)
- [Ktor contributing과 YouTrack 안내](https://github.com/ktorio/ktor/blob/main/CONTRIBUTING.md)
- [detekt contributing](https://github.com/detekt/detekt/blob/main/.github/CONTRIBUTING.md)
- [Micrometer contributing](https://github.com/micrometer-metrics/micrometer/blob/main/CONTRIBUTING.md)
- [Testcontainers contributing](https://java.testcontainers.org/contributing/)
- [Spring Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html)
- [Spring Boot Kotlin support](https://docs.spring.io/spring-boot/reference/features/kotlin.html)
- [Spring Boot testing](https://docs.spring.io/spring-boot/reference/testing/spring-applications.html)
- [Spring Data JPA reference](https://docs.spring.io/spring-data/jpa/reference/jpa.html)
- [Kotlin release information](https://kotlinlang.org/docs/releases.html)
