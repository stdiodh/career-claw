# Career Feed

Career Feed는 Kotlin/Java/Spring 백엔드 취업 준비를 매일 실행 가능한 백엔드 실무, PS, OSS 기여 준비, 연결 CS 지식과 주간 오픈소스 후보로 묶는 개인용 성장 루프입니다. LLM을 호출하지 않으며 모델 토큰 비용은 0입니다.

## 지금 검증된 범위

- 백엔드 핵심 과제 16개: Spring MVC, 테스트 계층, JPA/N+1, PostgreSQL 인덱스, Flyway, Kotlin 경계, 설정/Secret, 관측성, Java/JVM, 인증/인가, idempotency, transaction 복구, timeout/retry, 동시성
- 고정 profile: Temurin `21.0.11+10-LTS`, Spring Boot `4.1.0`, Kotlin `2.4.10`, Gradle `9.5.0`, PostgreSQL `17.10`
- `lab/` 기본 테스트 25개와 PostgreSQL 전용 테스트 1개
- 최근 60일 한국 신입·인턴·3년 이하 공고 15개 회사 표본, 통제된 경력 범위 코드, 분기 만료일, 고정 taxonomy
- 주간 최대 19회 공개 GitHub REST 조회, 후보 최대 3개, 외부 저장소 쓰기 0회

각 과제는 config, 고정된 공식 source revision, 채용시장 audit, taxonomy, Gradle dependency lock, lab 파일, `LAB-*` test ID, 기대 assertion을 하나의 contract hash로 묶습니다. 이 hash와 [검증 manifest](./data/curriculum-verification.json)가 일치하는 `VERIFIED` 핵심 과제만 Daily의 실무와 CS 섹션에 나옵니다. OSS 준비 섹션도 유효한 allowlist 저장소만 날짜별로 순환합니다. lab·의존성·근거를 한 줄만 바꾸거나 채용 audit가 만료돼도 검증 전에는 생성이 fail closed됩니다.

## 빠른 시작

저장소 전체 검증을 실행합니다.

```bash
./scripts/validate.sh
```

오늘의 브리핑을 확인합니다.

```bash
python3 scripts/generate_backend_daily.py --stdout
```

출력은 `백엔드 실무`, `PS`, `OSS 기여 준비`, `백엔드 연결 CS 지식` 네 영역으로 구성됩니다. OSS 준비는 기여 문서와 첫 build/test 명령을 안내할 뿐 실제 이슈 착수 승인이 아닙니다.

브리핑에 표시된 명령으로 해당 Kotlin/Spring 테스트를 실행합니다. 전체 기본 lab은 다음 명령으로 확인합니다.

```bash
./lab/gradlew -p lab test --no-daemon
```

Docker가 실행 중이면 pinned PostgreSQL integration test도 실행할 수 있습니다.

```bash
./lab/gradlew -p lab postgresTest --no-daemon
```

완료한 과제와 Programmers 문제는 ID로 기록합니다.

```bash
python3 scripts/mark_progress.py backend spring-mvc-validation-problem-detail
python3 scripts/mark_progress.py ps programmers-1845
```

완료 상태는 `data/progress.json`에만 저장됩니다. 로컬 변경을 다음 예약 실행에 이어 쓰려면 이 파일을 commit해야 합니다. GitHub에서는 `Mark Progress` workflow가 파일을 직접 갱신합니다.

## 발송 시각 선택

기본 목표 시각은 매일 한국시간 오전 9시입니다. 발송 시각은 콘텐츠와 분리된 [`configs/delivery-schedule.json`](./configs/delivery-schedule.json)의 `local_time`과 `timezone`만 수정합니다. `timezone`은 `Asia/Seoul`, `America/New_York` 같은 IANA 이름을 사용합니다.

```bash
python3 scripts/sync_delivery_schedule.py
python3 scripts/sync_delivery_schedule.py --check
```

동기화하면 `Backend Daily`는 선택한 현지 시각에 매일, `OSS Weekly`은 같은 현지 시각에 월요일 실행되도록 두 workflow의 예약 블록이 함께 갱신됩니다. 브리핑 기준일과 날짜별 CS·OSS 준비 순환도 같은 timezone을 사용합니다. GitHub Actions가 [IANA timezone 예약을 직접 지원](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)하므로 UTC 변환이나 반복 폴링은 사용하지 않습니다.

아직 OSS Shadow 증거가 없는 `LOCKED` gate라면 동기화 스크립트가 변경된 Weekly workflow의 contract hash도 함께 갱신합니다. 이미 run·후보 리뷰·승인이 존재하면 증거를 조용히 지우지 않고 시간 변경을 거부하므로, 먼저 기존 증거를 보존하고 새 관찰 기간으로 전환할지 명시적으로 결정해야 합니다.

예약 시각은 목표 시각이지 도착 보장 시간이 아닙니다. GitHub 공식 문서도 [예약 실행이 부하에 따라 지연되거나 누락될 수 있음](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)을 명시합니다. 정확한 시각 SLA가 필요하면 GitHub Actions 외부 scheduler가 `workflow_dispatch`를 호출해야 합니다.

## 주간 OSS 후보

수집 대상은 Spring Boot, Spring Framework, detekt, Micrometer, Testcontainers Java의 공개 issue입니다. 각 저장소의 상태, 최근 기본 브랜치 활동, 최근 외부 사람 병합 PR, 공식 build/test 경로를 분기 단위로 config에 고정하고 만료되면 수집을 거부합니다. Spring Security는 학습 lab에는 남아 있지만 2026-07-16 기준 최근 90일 병합 PR이 Dependabot뿐이어서 OSS 후보 수집에서는 제외했습니다.

```bash
python3 scripts/collect_oss_candidates.py \
  --live-dry-run \
  --json-output /tmp/oss-candidates.json \
  --markdown-output /tmp/oss-candidates.md
```

수집기는 `archived:false`와 repository별 exact label 계약을 확인하고 `created_at DESC`로 합친 최신 3개만 detail/comments/timeline까지 다시 검증합니다. closed, singular/plural assignee 증거가 불일치하거나 assigned인 issue, 연결 PR, 선점 댓글, actor가 불완전한 maintainer activity는 fail closed합니다. module label을 build 명령에 매핑할 수 없거나 상태가 애매하면 `MANUAL_REVIEW`이므로 브리핑에 노출하지 않습니다. 안전한 후보가 없으면 정상적인 empty 결과입니다.

공개 API rate limit이 부족하면 결과를 `complete=false`로 기록하고 Discord 전송을 차단합니다. 수집기는 인증 헤더를 보내지 않으며 `GITHUB_TOKEN`, PAT, GitHub App key를 받지 않습니다. 현재 repository에 한정된 installation token은 여러 외부 조직의 저장소를 조회하는 신뢰 가능한 fallback이 아니기 때문입니다.

`OSS Weekly`은 매주 월요일 `configs/delivery-schedule.json`의 현지 시각에 artifact-only shadow를 실행하도록 구성돼 있습니다. 기본값은 `Asia/Seoul` 09:00입니다. checkout과 metadata 생성까지 도달한 실행은 고유한 run/attempt 이름으로 provenance metadata와 실제 생성된 JSON/Markdown을 90일간 보존합니다. [tracked delivery gate](./configs/oss-delivery-gate.json)는 현재 `LOCKED`입니다. 서로 다른 연속 ISO 주차 4회와 고유 후보 10개 리뷰, 정렬·freshness 100%, hard-gate false positive 0건을 기록해 gate가 `APPROVED`되고 repository variable `OSS_DELIVERY_ENABLED=true`일 때만 실제 이슈 후보를 Discord로 전송할 수 있습니다. Daily의 OSS 준비 섹션은 네트워크 조회 없이 allowlist의 기여 문서만 보여 주므로 이 gate를 우회하지 않습니다.

주차로 인정되는 것은 canonical repository의 `main`에서 GitHub-hosted Linux runner가 실행한 `schedule` 이벤트의 첫 attempt뿐입니다. 성공적으로 업로드된 실패·재실행 artifact도 운영자가 `record-run`으로 ledger에 보존하지만 승인 주차에는 넣지 않습니다. 미래 시각, 불완전 수집, non-zero exit, HTTP 403·429, warning 또는 repository fail-closed가 있는 실행도 주차로 셀 수 없습니다. 리뷰 후보는 hash로 묶인 source artifact의 `READY_TO_ASK` 목록에 실제로 있어야 하며, 변수만 먼저 켜도 전송되지 않습니다.

### Shadow 증거 누적

예약 실행 뒤 GitHub 화면 또는 `gh`로 run의 event, ref, SHA, 모든 attempt와 conclusion을 먼저 확인합니다. recorder는 중간 attempt 누락과 역순은 거부하지만 아직 ledger에 없는 마지막 재실행을 GitHub API 없이 자동 발견하지는 못하므로, run history와 대조하는 절차가 provenance sidecar의 운영 신뢰 경계입니다. 수동 `workflow_dispatch` artifact는 smoke 용도이며 gate에 기록할 수 없습니다.

```bash
gh run view RUN_ID \
  --attempt ATTEMPT \
  --repo stdiodh/career-feed \
  --json attempt,conclusion,event,headBranch,headSha,status,url,workflowName
gh run download RUN_ID \
  --repo stdiodh/career-feed \
  --name oss-weekly-RUN_ID-ATTEMPT \
  --dir /tmp/career-feed-oss-RUN_ID-ATTEMPT
```

JSON의 정렬과 각 후보의 `checked_at`/현재 GitHub 상태를 직접 대조한 뒤에만 attestation을 기록합니다.

```bash
python3 scripts/record_oss_shadow.py record-run \
  /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-run-metadata.json \
  --artifact /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-candidates.json \
  --markdown /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-candidates.md \
  --sort-accurate yes \
  --freshness-accurate yes
```

exit `2`의 incomplete 실행은 JSON/Markdown을 함께 넘기고 두 attestation을 `no`로 기록합니다. artifact 생성 전 exit `1`이면 metadata만 넘기며, JSON 또는 Markdown 한쪽만 남았다면 존재하는 파일의 flag만 추가합니다.

```bash
python3 scripts/record_oss_shadow.py record-run \
  /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-run-metadata.json \
  --sort-accurate no \
  --freshness-accurate no

python3 scripts/record_oss_shadow.py record-run \
  /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-run-metadata.json \
  --artifact /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-candidates.json \
  --markdown /tmp/career-feed-oss-RUN_ID-ATTEMPT/oss-candidates.md \
  --sort-accurate no \
  --freshness-accurate no
```

실제 `READY_TO_ASK` 후보마다 관련성, 범위, hard-gate 오추천 여부와 짧은 근거를 남깁니다. 오추천이면 `--hard-gate-false-positive yes`와 함께 recorder가 허용하는 사유를 반드시 선택합니다.

```bash
python3 scripts/record_oss_shadow.py record-review \
  'spring-projects/spring-boot#12345' \
  --source-run-id github-RUN_ID-attempt-1 \
  --reviewer backend-owner \
  --notes '재현 경로와 module test 범위를 issue에서 확인함' \
  --relevant yes \
  --scope-clear yes \
  --hard-gate-false-positive no

python3 scripts/check_oss_delivery_gate.py
```

각 주의 gate diff를 검토한 뒤 `configs/oss-delivery-gate.json`만 commit/push합니다. 다운로드한 `reports/`나 `/tmp` artifact는 commit하지 않습니다. 4주/10개 조건이 실제로 채워진 뒤에만 `approve`를 실행합니다. 관련 workflow, collector, recorder, gate checker 또는 OSS config가 바뀌면 Shadow contract hash가 달라져 기존 승인이 자동으로 무효화되므로 새 관찰 기간을 시작해야 합니다.

```bash
python3 scripts/record_oss_shadow.py approve
```

## GitHub Actions와 Discord

### 로컬 구현 기준

현재 로컬 작업 트리에는 다음 네 workflow와 5개 OSS 저장소·주간 최대 19회 조회 계약이 구현돼 있습니다. OSS gate는 `LOCKED`이므로 artifact만 생성하고 Discord로 전송하지 않습니다.

- `Backend Daily`: 기본 `Asia/Seoul` 09:00, 백엔드 실무·PS·OSS 기여 준비·연결 CS 지식 생성
- `OSS Weekly`: 기본 매주 월요일 `Asia/Seoul` 09:00, read-only 실제 후보 artifact 생성
- `Mark Progress`: 완료 ID를 `data/progress.json`에 기록
- `Pull Request Checks`: Python, contract, Gradle, PostgreSQL, 결정론적 생성 검증

repository secret은 `DISCORD_WEBHOOK_URL`을 사용합니다. 기존 저장소의 `DISCORD_WEBHOOK_KR_TECH_DAILY`는 Secret 값을 다시 등록할 때까지 migration fallback으로만 읽으며 둘 중 하나만 있으면 됩니다. 수동 실행은 기본 `dry_run=true`라 전송하지 않습니다. OSS Discord는 위 shadow gate와 `OSS_DELIVERY_ENABLED`를 추가로 통과해야 합니다.

### 원격 배포 확인

실제 원격 동작 기준은 기본 브랜치에 병합된 commit입니다. 병합 뒤 Actions 목록이 위 네 workflow만 포함하는지 확인하고, `Backend Daily`는 `dry_run=true`, `OSS Weekly`은 artifact-only로 먼저 실행합니다. 배포 전 원격 상태와 실행 시각·SHA는 [검증 증거](./audits/verification-evidence-2026-07-16.md#의도적으로-남겨-둔-승격-gate)에 역사 기록으로 남깁니다.

## 문서 기준과 검증 근거

제품 설명과 운영 안내는 이 한국어 README를 단일 기준으로 관리합니다. 영어는 코드 식별자, 명령, 외부 프로젝트·제품의 공식 명칭에만 유지하며, 삭제한 `docs/en/`·`docs/kr/` 번역 복제 트리를 다시 만들지 않습니다. 상세 합격 계약은 [검증 계획](./VALIDATION_PLAN.md), 실행 결과는 [검증 증거](./audits/verification-evidence-2026-07-16.md)에서만 관리합니다.

- 백엔드 과제: [`configs/backend-practice.json`](./configs/backend-practice.json)
- 과제/소스/lab 계약: [`configs/curriculum-matrix.json`](./configs/curriculum-matrix.json)
- 호환 버전과 checksum: [`configs/verification-profile.json`](./configs/verification-profile.json)
- 채용 표본: [`audits/job-market-2026q3.json`](./audits/job-market-2026q3.json)
- OSS allowlist: [`configs/oss-repositories.json`](./configs/oss-repositories.json)
- OSS 4주/10개 승격 gate: [`configs/oss-delivery-gate.json`](./configs/oss-delivery-gate.json)
- 사용자 발송 시각: [`configs/delivery-schedule.json`](./configs/delivery-schedule.json)
- 전체 기준과 phase 기록: [`VALIDATION_PLAN.md`](./VALIDATION_PLAN.md)

`reports/`는 생성물이라 커밋하지 않습니다. Secret, issue body, 댓글 전문도 저장하지 않습니다.

## 구조

```text
.github/workflows/          일일·주간·진행·PR 검증
audits/                     채용 표본과 검증 증거
configs/                    커리큘럼, profile, OSS 계약
data/                       진행 상태와 검증 manifest
lab/                        Kotlin/Java/Spring 실행 실습
scripts/                    생성, 수집, 전송, 검증
tests/                      Python contract/fixture 테스트
```

라이선스는 [MIT License](./LICENSE)를 따릅니다.
