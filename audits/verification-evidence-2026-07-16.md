# Career Feed 구현 검증 증거

기준 시각: 2026-07-16 KST/UTC
대상 profile: `jvm-spring-2026q3-v1`

## Phase 0 — 기준 고정

- Temurin `21.0.11+10-LTS`, Spring Boot `4.1.0`, Kotlin `2.4.10`, Gradle `9.5.0`, PostgreSQL `17.10`을 `configs/verification-profile.json`에 고정했다.
- Gradle distribution SHA-256과 Wrapper JAR SHA-256이 profile과 실제 파일에 일치했다.
- Maven Central에서 다시 받은 Boot Gradle plugin, Boot BOM, Kotlin Gradle plugin의 SHA-256이 profile의 retrieval lock과 각각 일치했다.
- `postgres:17.10-bookworm` pull 결과 OCI index digest가 profile의 `sha256:4f736ae292687621d4dbe0d499ffd024a36bd2ee7d8ca6f2ccd4c800f047b394`와 일치했다.
- 최근 60일의 신입·인턴·3년 이하 공고를 15개 회사에서 1개씩 수집했다. 2026-07-16 재검사에서 15개 URL이 모두 HTTP 200이었다.
- 표본 자동 검사에서 15개, 회사 중복 0, 업종 비율 최대 AI 4/15, keyword frequency 재계산 일치를 확인했다. 경력 범위는 허용된 8개 코드만 받고 자유 문자열, 미래 audit, 만료 audit는 fail closed한다.
- Spring Framework, Spring Security, Spring Data JPA, Flyway, Hibernate ORM, Jackson Kotlin의 실제 해석 버전을 `lab/gradle.lockfile`과 profile에서 교차 검사한다.

## Phase 1 — 커리큘럼과 lab

- 핵심 lesson: 16개
- `JVM_CORE`: 15개(93.75%)
- 최소 competency gap: 0개
- lab content revision: `sha256:46d3ef065c7060604c5159f87fb178924dcde889a84ce47903100be6e399d999`
- stable assertion ID: 26개, lab source에서 각각 정확히 1회 정의

실행 결과:

| 검증 | 환경 | 결과 |
|---|---|---|
| `./lab/gradlew -p lab test --rerun-tasks --no-daemon` | macOS arm64, local JDK 21.0.6 | 25/25 통과 |
| `clean test --no-build-cache` | Docker linux/amd64, Temurin 21.0.11+10 | 25/25 통과 |
| `./lab/gradlew -p lab postgresTest --rerun-tasks --no-daemon` | Docker, pinned PostgreSQL OCI digest | 1/1 통과 |
| `python3 scripts/verify_curriculum.py` | canonical config/profile/taxonomy/manifest | 16/16 VERIFIED |
| source/revision URL GET | 공식 근거의 고유 URL 36개 | 36/36 HTTP 200 |

추가 실패 재현과 수정:

- 같은 Idempotency-Key 동시 요청에서 주문 두 개가 생기는 race를 먼저 재현했다. DB lock bucket과 `PESSIMISTIC_WRITE` 적용 뒤 주문 1개, stock 변경 1회로 고정했다.
- JPA lazy traversal의 4 queries를 재현하고 join fetch가 1 query로 줄이는 것을 assertion했다.
- 실제 HTTP Basic filter chain에서 익명·오류 credential은 401, 실행 시 생성한 credential은 201임을 확인했다. credential은 저장하지 않았다.
- lab source 한 줄을 바꾼 복사본에서 manifest가 `STALE`로 판정돼 Daily 생성이 차단되는 mutation test를 통과했다.
- 미래 job audit, source review, manifest 날짜와 senior 경력 범위 코드를 넣은 mutation에서 모두 Daily 생성이 차단됐다.
- dependency profile을 실제 lock과 다른 버전으로 바꾼 mutation에서 검증이 차단됐다.
- `SPRING_PROFILES_ACTIVE`와 `LAB_EXTERNAL_*` 형태의 system-environment property source가 typed config에 bind되고 blank Secret은 context 시작 시 실패하는 것을 확인했다.
- HTTP 응답 request ID가 MDC `request_id`와 구조화 `method/path/status` 로그에 함께 남고 health와 outcome metric이 조회되는 것을 확인했다.
- PostgreSQL test는 인덱스 전·후에 각각 3회 warm-up한 뒤 두 `EXPLAIN (ANALYZE, BUFFERS)` plan을 기록한다. timing/buffer 수치는 관찰만 하고 target index 사용만 hard assertion한다.
- 실제 import가 없는 test starter와 Kotlin test/launcher 직접 선언 5개를 제거하고 lockfile을 198줄에서 190줄로 줄인 뒤 기본 25개와 PostgreSQL 1개를 재검증했다.

최종 반복 검증:

- 최종 스냅샷에서 `RUN_POSTGRES_TESTS=1 ./scripts/validate.sh`를 2회 연속 실행했다.
- 매 실행마다 Python 129개, curriculum 16/16, deterministic Daily/fixture 생성, Kotlin/Spring 25개, PostgreSQL 1개, workflow 개수와 diff 검사가 모두 통과했다.
- `.git`, build/cache, reports, `.codex`를 제외해 만든 독립 snapshot을 새 Git index에 올려 whitespace를 검사하고 별도 빈 `GRADLE_USER_HOME`에서 Gradle 9.5.0을 다시 받아 동일한 전체 검증을 한 번 더 통과했다. 이는 clean source snapshot 자동 재현 증거이며 사람 attestation을 대신하지 않는다.
- 별도 linux/amd64 Temurin 21.0.11+10 컨테이너의 `clean test --no-build-cache`와 pinned actionlint OCI digest도 통과했다.
- 같은 입력을 두 번 생성한 SHA-256은 Daily `eff3c5a7c7cfb53457f932289e2ebaff7c34edb8f4c145ea51fa30ac99684767`, OSS JSON `7ce7327062df3fc883182eb3d6616f3f57a58b4ffaaa27774c884adca3f19c12`, OSS Markdown `243c44ef05f2bb3b20fe88e49405a68c3e2ac3442aeb8a24c77b89f45c4c0b0a`로 각각 일치했다.

## Phase 2·3 — OSS fixture와 live shadow

- OSS collector contract/fixture test: 42개 통과
- tracked delivery gate test: 21개 통과
- Shadow evidence recorder test: 21개 통과
- fixture end-to-end: 정확히 19/19 GET 요청, 성공 empty 경로 10/19 요청, deterministic JSON/Markdown, body/comment 전문 비저장
- write method, comment, assign, label, branch, fork, PR 생성 경로 없음
- schema 2 allowlist는 5개 저장소의 archived/fork/issues 상태, 최근 기본 브랜치 활동, 최근 외부 사람 병합 PR, 공식 build/test 근거와 분기 만료일을 구조화해 검증한다. 이 감사는 자동 감사이며 사람 attestation으로 표시하지 않는다.
- Spring Security는 최근 90일 병합 PR 132건이 모두 Dependabot이고 외부 사람 병합 PR은 0건이라 활성 수집 대상에서 제거했다.
- maintainer association만 있고 actor가 없던 comment와 singular `assignee`/plural `assignees`가 모순된 detail이 과거 `READY_TO_ASK`가 되는 두 fail-open을 재현한 뒤 모두 제외되는 regression test를 추가했다.

활성 allowlist admission snapshot:

| 저장소 | default branch commit | 외부 사람 merged PR | 판정 |
|---|---|---|---|
| Spring Boot | `046d4c64` · 2026-07-15 | `#50892` · CONTRIBUTOR · 2026-07-15 | 유지 |
| Spring Framework | `99b991b6` · 2026-07-13 | `#36967` · CONTRIBUTOR · 2026-07-12 | 유지 |
| detekt | `bc1e091e` · 2026-07-16 | `#9492` · CONTRIBUTOR · 2026-07-12 | 유지 |
| Micrometer | `442eccb1` · 2026-07-15 | `#7509` · CONTRIBUTOR · 2026-07-03 | 유지 |
| Testcontainers Java | `deb78e1e` · 2026-06-22 | `#11845` · CONTRIBUTOR · 2026-06-22 | 유지 |

각 SHA/PR의 전체 URL, archived/fork/issues 상태, build instructions와 proprietary 환경 불필요 attestation은 `configs/oss-repositories.json`에 보존하며 2026-10-14 뒤에는 collector가 시작되지 않는다.

Unauthenticated accelerated live smoke:

| UTC generated_at | 요청 | core 잔여 | search 잔여 | 상세 후보 | READY_TO_ASK | 결과 |
|---|---:|---:|---:|---:|---:|---|
| 03:33:51 | 19 | 45 | 6 | 3 | 0 | complete; Spring Framework label drift와 Testcontainers pagination을 repository fail-closed |
| 03:35:55 | 20 | 30 | 5 | 3 | 0 | complete; drift 수정 후 Testcontainers만 fail-closed |
| 03:37:41 | 20 | 15 | 5 | 3 | 0 | complete |
| 03:39:19 | 20 | 0 | 5 | 3 | 0 | complete |
| 05:46:20 | 21 | 30 | 4 | 3 | 0 | complete; 6개 label contract 모두 확인, warning/repository failure 0 |
| 06:33:39 | 21 | 45 | 4 | 3 | 0 | complete; 폐기된 6-repository 계약의 hardened validator 통과 |
| 07:10:12 | 19 | 17 | 5 | 3 | 0 | complete; 최종 5-repository/schema 2 계약, 19/19 HTTP 200, warning/repository failure 0 |

03:33~06:33 실행은 폐기된 6-repository/21-request 계약의 역사적 smoke다. 현재 계약의 상세 후보는 Micrometer `#6502`, `#6079`, `#5063`이었다. 앞의 두 후보는 연결 PR·선점 댓글·180일 초과 maintainer activity로 `EXCLUDED`, 마지막 후보는 외부 댓글과 module mapping 미확정으로 `MANUAL_REVIEW`였다. READY를 억지로 보충하지 않은 것이 기대 동작이다.

07:10:12 UTC live JSON은 schema 3 recorder의 hardened artifact validator와 deterministic Markdown 재렌더링을 통과했다. HTTP 응답은 19/19 모두 200이었고 JSON SHA-256은 `78dd52552d487a7f2502bd7c242f61a8b34e6e46beefa8922ba614933f7ae98f`, Markdown SHA-256은 `1834e9aeaaf69e8372a7824d9a3538ba0ec76547ea8f9079f18966894e02edf3`였다. 이 실행은 로컬 smoke이므로 tracked gate에는 기록하지 않았다.

core quota가 0인 상태에서 추가 실행한 결과:

- exit code: `2`
- request: 6/21 (폐기된 6-repository 계약)
- `complete=false`, `delivery_allowed=false`, READY 0
- JSON/Markdown artifact 생성
- 당시 6개 repository labels 요청의 HTTP 403과 missing search header 기록
- Discord 전송 조건 불충족

원격 legacy 실행 관찰(현행 OSS 계약의 증거에서 제외):

- 약 07:28 UTC에 기존 `Backend Daily Brief` [run `29480009001`](https://github.com/stdiodh/career-feed/actions/runs/29480009001)이 `main@1e0700c`에서 실행돼 Discord 전송에 성공하고 progress bot commit [`fc30f51a`](https://github.com/stdiodh/career-feed/commit/fc30f51a)를 만들었다.
- 이 legacy 실행은 Spring Security를 후보로 추천했지만, 현행 5-repository/19-request collector, schema 3 recorder/gate 또는 `OSS Weekly`을 실행하지 않았다. 따라서 새 OSS 로직이나 Shadow 승격의 증거로 계산하지 않는다.

## Phase 4 — artifact-only 운영 결정

- `OSS Weekly`은 월요일 00:37 UTC에 read-only artifact와 GitHub Actions provenance metadata를 생성한다.
- `OSS_DELIVERY_ENABLED=true`만으로는 OSS Discord step이 실행되지 않는다. tracked gate의 `APPROVED`가 동시에 필요하다.
- schema 3 gate는 canonical schedule/main/GitHub-hosted provenance, run/attempt 순서, contract fingerprint, metadata/artifact hash, attestation/review/approval 시간 순서를 검증한다.
- 성공적으로 업로드되고 운영자가 기록한 실패와 재실행도 ledger에 남지만 첫 attempt 성공만 주차로 계산한다. 미래·역순 시각, 기록된 run의 누락 attempt, incomplete/non-zero, HTTP 403·429, warning/repository failure, source artifact에 없던 후보는 승인 증거가 될 수 없다. metadata 생성 전 runner 실패와 아직 기록하지 않은 마지막 rerun은 GitHub run history를 사람이 대조해야 한다.
- collector exit가 0이 아니어도 metadata와 존재하는 artifact를 먼저 업로드하고 job을 실패시킨다. artifact 이름은 run/attempt별로 고유하며 retention은 90일이다.
- rollback은 repository variable `OSS_DELIVERY_ENABLED`를 제거하는 한 단계다.
- 수집기는 인증 헤더를 만들지 않는다. `GITHUB_TOKEN`, PAT, GitHub App private key/installation token은 입력으로 받지 않는다.
- 네 workflow의 reusable action은 full commit SHA로 고정했고 pinned `actionlint` OCI digest와 workflow 계약 테스트를 통과했다.

## 의도적으로 남겨 둔 승격 gate

같은 날의 live smoke는 API와 fail-closed 구현 검증이다. 달력이 다른 연속 4주와 서로 다른 live 후보 10개 검토를 대체하지 않는다. tracked gate는 Shadow contract `sha256:c9404a544582fdcd3489b5924e956b08de8abef2f368ee6c5591952c8137edc2`의 schema 3, 0주/0개 `LOCKED`다. 이 증거를 기록한 약 07:28 UTC의 legacy bot commit 뒤 원격 `main`은 `fc30f51a`, `oss-weekly.yml` API는 404였고 기존 5개 workflow만 활성 상태였다. 당시 현행 OSS 변경은 아직 commit/push되지 않아 GitHub-hosted runner artifact 실행 증거가 없었다. 병합 뒤에도 연속 4주·10개 리뷰를 충족할 때까지 OSS Discord 자동 전송은 잠금 상태다.
