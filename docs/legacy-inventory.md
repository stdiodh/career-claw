# Legacy Inventory

기준: `README.md`, `LEGACY.md`, `git ls-files`, `git grep`, `rg`, `git log -- <path>`.

| 상태 | 파일 경로 | 삭제 사유 | 대체 파일/기능 | 참조 확인 | 위험도 | 롤백 방법 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KEEP | `.env.example` | 해당 없음 | 환경변수 템플릿 | README secrets, `git grep` | HIGH | `git checkout HEAD^ -- .env.example` | secret 값 없이 이름만 유지 |
| KEEP | `.gitattributes` | 해당 없음 | Git 속성 | `git grep app/gradlew` | LOW | `git checkout HEAD^ -- .gitattributes` | Gradle wrapper LF 유지 |
| KEEP | `.gitignore` | 해당 없음 | ignore 정책 | `git grep reports/`, app/infra local state | MEDIUM | `git checkout HEAD^ -- .gitignore` | 생성 reports와 build 산출물 보호 |
| KEEP | `AGENTS.md` | 해당 없음 | 저장소 작업 규칙 | 사용자 제공 규칙, `git grep` | MEDIUM | `git checkout HEAD^ -- AGENTS.md` | app/infra 수정 금지 포함 |
| KEEP | `LEGACY.md` | 해당 없음 | 레거시 삭제 정책 | README, docs/operations 링크 | LOW | `git checkout HEAD^ -- LEGACY.md` | 이번 변경에서 추가 |
| KEEP | `README.md` | 해당 없음 | 운영 기준 문서 | 전체 운영 맵 기준 | MEDIUM | `git checkout HEAD^ -- README.md` | 현재 운영 경로 source of truth |
| KEEP | `.github/codex/prompts/kr-tech-daily-brief.md` | 해당 없음 | Daily Backend prompt | README, workflow, validate.sh | HIGH | `git checkout HEAD^ -- .github/codex/prompts/kr-tech-daily-brief.md` | 활성 Codex 입력 |
| KEEP | `.github/codex/prompts/kr-tech-news-daily.md` | 해당 없음 | News Daily prompt | README, workflow, validate.sh | HIGH | `git checkout HEAD^ -- .github/codex/prompts/kr-tech-news-daily.md` | 활성 Codex 입력 |
| KEEP | `.github/workflows/kr-backend-career-weekly.yml` | 해당 없음 | Career Site Radar workflow | README, validate.sh | HIGH | `git checkout HEAD^ -- .github/workflows/kr-backend-career-weekly.yml` | 활성 수동 workflow |
| KEEP | `.github/workflows/kr-tech-daily.yml` | 해당 없음 | Daily Backend workflow | README, validate.sh | HIGH | `git checkout HEAD^ -- .github/workflows/kr-tech-daily.yml` | 활성 schedule/catch-up |
| KEEP | `.github/workflows/kr-tech-news-daily.yml` | 해당 없음 | News Daily workflow | README, validate.sh | HIGH | `git checkout HEAD^ -- .github/workflows/kr-tech-news-daily.yml` | 활성 schedule/catch-up |
| KEEP | `.github/workflows/mark-ps-solved.yml` | 해당 없음 | PS progress workflow | README, validate.sh | HIGH | `git checkout HEAD^ -- .github/workflows/mark-ps-solved.yml` | 활성 수동 workflow |
| UNKNOWN | `app/.dockerignore` | README 운영 경로 미기재 | 없음 | `git grep app/`, AGENTS 수정 금지 | HIGH | `git checkout HEAD^ -- app/.dockerignore` | app은 별도 PR에서 판단 |
| UNKNOWN | `app/Dockerfile` | README 운영 경로 미기재 | 없음 | infra compose 참조, AGENTS 수정 금지 | HIGH | `git checkout HEAD^ -- app/Dockerfile` | 삭제 금지 |
| UNKNOWN | `app/HELP.md` | README 운영 경로 미기재 | 없음 | app 내부 문서 | HIGH | `git checkout HEAD^ -- app/HELP.md` | 삭제 금지 |
| UNKNOWN | `app/build.gradle.kts` | README 운영 경로 미기재 | 없음 | app Gradle build | HIGH | `git checkout HEAD^ -- app/build.gradle.kts` | 삭제 금지 |
| UNKNOWN | `app/gradle/wrapper/gradle-wrapper.jar` | README 운영 경로 미기재 | 없음 | Gradle wrapper | HIGH | `git checkout HEAD^ -- app/gradle/wrapper/gradle-wrapper.jar` | 삭제 금지 |
| UNKNOWN | `app/gradle/wrapper/gradle-wrapper.properties` | README 운영 경로 미기재 | 없음 | Gradle wrapper | HIGH | `git checkout HEAD^ -- app/gradle/wrapper/gradle-wrapper.properties` | 삭제 금지 |
| UNKNOWN | `app/gradlew` | README 운영 경로 미기재 | 없음 | `.gitattributes`, Gradle wrapper | HIGH | `git checkout HEAD^ -- app/gradlew` | 삭제 금지 |
| UNKNOWN | `app/gradlew.bat` | README 운영 경로 미기재 | 없음 | Gradle wrapper | HIGH | `git checkout HEAD^ -- app/gradlew.bat` | 삭제 금지 |
| UNKNOWN | `app/settings.gradle.kts` | README 운영 경로 미기재 | 없음 | app Gradle build | HIGH | `git checkout HEAD^ -- app/settings.gradle.kts` | 삭제 금지 |
| UNKNOWN | `app/src/main/kotlin/com/stdiodh/career_claw/CareerClawApplication.kt` | README 운영 경로 미기재 | 없음 | app source | HIGH | `git checkout HEAD^ -- app/src/main/kotlin/com/stdiodh/career_claw/CareerClawApplication.kt` | 삭제 금지 |
| UNKNOWN | `app/src/main/kotlin/com/stdiodh/career_claw/HealthController.kt` | README 운영 경로 미기재 | 없음 | app source | HIGH | `git checkout HEAD^ -- app/src/main/kotlin/com/stdiodh/career_claw/HealthController.kt` | 삭제 금지 |
| UNKNOWN | `app/src/main/resources/application.yaml` | README 운영 경로 미기재 | 없음 | app runtime config | HIGH | `git checkout HEAD^ -- app/src/main/resources/application.yaml` | 삭제 금지 |
| UNKNOWN | `app/src/test/kotlin/com/stdiodh/career_claw/CareerClawApplicationTests.kt` | README 운영 경로 미기재 | 없음 | app tests | HIGH | `git checkout HEAD^ -- app/src/test/kotlin/com/stdiodh/career_claw/CareerClawApplicationTests.kt` | 삭제 금지 |
| KEEP | `configs/audience-profile.json` | 해당 없음 | 사용자 프로필 config | README, workflow prompt, validate.sh | MEDIUM | `git checkout HEAD^ -- configs/audience-profile.json` | Daily 입력 |
| KEEP | `configs/backend-core-cs-curriculum.json` | 해당 없음 | CS Core config | README, scripts, validate.sh | MEDIUM | `git checkout HEAD^ -- configs/backend-core-cs-curriculum.json` | Daily Backend 후보 생성 |
| KEEP | `configs/backend-practical-knowledge-curriculum.json` | 해당 없음 | 실무지식 config | README, scripts, validate.sh | MEDIUM | `git checkout HEAD^ -- configs/backend-practical-knowledge-curriculum.json` | Daily Backend 후보 생성 |
| KEEP | `configs/backend-terms-glossary.json` | 해당 없음 | 백엔드 용어 config | README, scripts, validate.sh | MEDIUM | `git checkout HEAD^ -- configs/backend-terms-glossary.json` | Daily Backend 후보 생성 |
| KEEP | `configs/company-career-watchlist.json` | 해당 없음 | 회사 watchlist config | `scripts/collect-kr-feeds.py`, validate.sh | MEDIUM | `git checkout HEAD^ -- configs/company-career-watchlist.json` | README 구조에 보강 |
| KEEP | `configs/kr-sources.json` | 해당 없음 | Daily 후보 source config | README, scripts, validate.sh | HIGH | `git checkout HEAD^ -- configs/kr-sources.json` | Backend/News source |
| KEEP | `configs/oss-repositories.json` | 해당 없음 | OSS 저장소 policy config | README, docs, scripts, validate.sh | HIGH | `git checkout HEAD^ -- configs/oss-repositories.json` | 후보 source of truth |
| KEEP | `configs/programmers-ps-curriculum.json` | 해당 없음 | PS curriculum config | README, scripts, validate.sh | MEDIUM | `git checkout HEAD^ -- configs/programmers-ps-curriculum.json` | 정적 PS 루틴 |
| KEEP | `configs/weekly-career-site-radar.json` | 해당 없음 | Site Radar config | README, workflow, tests | HIGH | `git checkout HEAD^ -- configs/weekly-career-site-radar.json` | 활성 수동 레이더 |
| KEEP | `configs/weekly-career-sources.json` | 해당 없음 | legacy weekly source policy | `scripts/collect-kr-feeds.py` fallback/validation path | MEDIUM | `git checkout HEAD^ -- configs/weekly-career-sources.json` | 삭제 불가, README 구조에 보강 |
| KEEP | `data/oss-progress.json` | 해당 없음 | OSS progress | README, script | MEDIUM | `git checkout HEAD^ -- data/oss-progress.json` | 로컬 정적 기록 |
| KEEP | `data/ps-progress.json` | 해당 없음 | PS progress | README, workflows, scripts | HIGH | `git checkout HEAD^ -- data/ps-progress.json` | workflow commit 대상 |
| KEEP | `data/spring-jvm-blog-topic-progress.json` | 해당 없음 | Spring/JVM topic progress | README, workflow, scripts, validate.sh | HIGH | `git checkout HEAD^ -- data/spring-jvm-blog-topic-progress.json` | workflow commit 대상 |
| KEEP | `docs/backend-growth-curriculum.md` | 해당 없음 | CS Core/용어 운영 문서 | 내용이 현행 Daily Backend 구조와 일치 | LOW | `git checkout HEAD^ -- docs/backend-growth-curriculum.md` | README 참조 보강 |
| KEEP | `docs/daily-growth-ops.md` | 해당 없음 | Daily 운영 확인 문서 | README, docs/operations, validate.sh | LOW | `git checkout HEAD^ -- docs/daily-growth-ops.md` | 활성 운영 문서 |
| KEEP | `docs/daily-spring-jvm-blog-topic-policy.md` | 해당 없음 | Spring/JVM 주제 정책 | validate.sh, 현행 Daily 정책 | LOW | `git checkout HEAD^ -- docs/daily-spring-jvm-blog-topic-policy.md` | README 참조 보강 |
| KEEP | `docs/legacy-inventory.md` | 해당 없음 | 레거시 분류 기록 | README 운영 정책 | LOW | `git checkout HEAD^ -- docs/legacy-inventory.md` | 이번 변경에서 추가 |
| KEEP | `docs/operations.md` | 해당 없음 | 운영 가이드 | README 연계 문서 | LOW | `git checkout HEAD^ -- docs/operations.md` | 정책 링크 보강 |
| KEEP | `docs/oss-candidate-policy.md` | 해당 없음 | OSS 후보 정책 | README, docs/operations, validate.sh | MEDIUM | `git checkout HEAD^ -- docs/oss-candidate-policy.md` | 활성 정책 문서 |
| UNKNOWN | `infra/compose.yaml` | README 운영 경로 미기재 | 없음 | infra 내부 참조, AGENTS 수정 금지 | HIGH | `git checkout HEAD^ -- infra/compose.yaml` | 배포 영향 가능, 삭제 금지 |
| UNKNOWN | `infra/nginx/README.md` | README 운영 경로 미기재 | 없음 | infra 문서 | HIGH | `git checkout HEAD^ -- infra/nginx/README.md` | 삭제 금지 |
| UNKNOWN | `infra/nginx/claw.stdiodh.xyz.conf.example` | README 운영 경로 미기재 | 없음 | nginx example | HIGH | `git checkout HEAD^ -- infra/nginx/claw.stdiodh.xyz.conf.example` | 삭제 금지 |
| UNKNOWN | `infra/nginx/default.conf` | README 운영 경로 미기재 | 없음 | compose/nginx runtime 가능성 | HIGH | `git checkout HEAD^ -- infra/nginx/default.conf` | 삭제 금지 |
| UNKNOWN | `infra/openclaw/openclaw.json` | README 운영 경로 미기재 | 없음 | compose mount | HIGH | `git checkout HEAD^ -- infra/openclaw/openclaw.json` | 삭제 금지 |
| UNKNOWN | `infra/openclaw/workspace/.gitkeep` | README 운영 경로 미기재 | 없음 | compose mount path | HIGH | `git checkout HEAD^ -- infra/openclaw/workspace/.gitkeep` | 삭제 금지 |
| UNKNOWN | `infra/scripts/deploy.sh` | README 운영 경로 미기재 | 없음 | deploy script, compose | HIGH | `git checkout HEAD^ -- infra/scripts/deploy.sh` | 삭제 금지 |
| KEEP | `reports/.gitkeep` | 해당 없음 | reports root contract | workflows create/write reports | MEDIUM | `git checkout HEAD^ -- reports/.gitkeep` | 빈 디렉터리 유지 |
| KEEP | `reports/briefs/.gitkeep` | 해당 없음 | brief output directory contract | workflows, validators | MEDIUM | `git checkout HEAD^ -- reports/briefs/.gitkeep` | 산출물 파일은 ignore |
| KEEP | `reports/candidates/.gitkeep` | 해당 없음 | candidate output directory contract | workflows, scripts | MEDIUM | `git checkout HEAD^ -- reports/candidates/.gitkeep` | 산출물 파일은 ignore |
| KEEP | `scripts/build-daily-news-shortlist.py` | 해당 없음 | News shortlist builder | README, workflow, validate.sh | HIGH | `git checkout HEAD^ -- scripts/build-daily-news-shortlist.py` | 활성 workflow script |
| KEEP | `scripts/check-workflow-schedules.py` | 해당 없음 | schedule validator | README, validate.sh | MEDIUM | `git checkout HEAD^ -- scripts/check-workflow-schedules.py` | 로컬 검증 |
| KEEP | `scripts/collect-kr-feeds.py` | 해당 없음 | 후보 collector | README, workflows, tests | HIGH | `git checkout HEAD^ -- scripts/collect-kr-feeds.py` | 핵심 script |
| KEEP | `scripts/estimate-prompt-budget.py` | 해당 없음 | News token budget | README, workflow, validate.sh | MEDIUM | `git checkout HEAD^ -- scripts/estimate-prompt-budget.py` | 활성 workflow script |
| KEEP | `scripts/evaluate-news-daily-quality.py` | 해당 없음 | News quality report | workflow, docs/operations, validate.sh | MEDIUM | `git checkout HEAD^ -- scripts/evaluate-news-daily-quality.py` | README 구조에 보강 |
| KEEP | `scripts/render-weekly-career-site-radar.py` | 해당 없음 | Site Radar renderer | README, workflow, tests | HIGH | `git checkout HEAD^ -- scripts/render-weekly-career-site-radar.py` | 활성 workflow script |
| KEEP | `scripts/select-ps-problem.py` | 해당 없음 | PS routine helper | validate.sh, collect path | MEDIUM | `git checkout HEAD^ -- scripts/select-ps-problem.py` | 생성 후보 계약 |
| KEEP | `scripts/send-discord.py` | 해당 없음 | Discord sender | workflows, docs/operations, validate.sh | HIGH | `git checkout HEAD^ -- scripts/send-discord.py` | Webhook 전송 |
| KEEP | `scripts/update-oss-progress.py` | 해당 없음 | OSS progress updater | README, docs, validate.sh | MEDIUM | `git checkout HEAD^ -- scripts/update-oss-progress.py` | 로컬 기록 |
| KEEP | `scripts/update-ps-progress.py` | 해당 없음 | PS progress updater | README, workflow, validate.sh | HIGH | `git checkout HEAD^ -- scripts/update-ps-progress.py` | workflow commit 대상 |
| KEEP | `scripts/validate-career-feed-brief.py` | 해당 없음 | Markdown validator | README, workflows, tests | HIGH | `git checkout HEAD^ -- scripts/validate-career-feed-brief.py` | 핵심 검증 |
| KEEP | `scripts/validate.sh` | 해당 없음 | 통합 검증 | README, AGENTS | HIGH | `git checkout HEAD^ -- scripts/validate.sh` | 기본 검증 명령 |
| KEEP | `scripts/write-news-daily-run-summary.py` | 해당 없음 | News run summary | workflow, validate.sh | MEDIUM | `git checkout HEAD^ -- scripts/write-news-daily-run-summary.py` | README 구조에 보강 |
| KEEP | `tests/fixtures/candidates-empty/kr-oss-contribution-opportunities.json` | 해당 없음 | Daily OSS empty fixture | README local validation, validate.sh, tests | MEDIUM | `git checkout HEAD^ -- tests/fixtures/candidates-empty/kr-oss-contribution-opportunities.json` | fixture 보호 |
| KEEP | `tests/fixtures/kr-backend-career-weekly-valid.md` | 해당 없음 | Weekly validator fixture | README, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-backend-career-weekly-valid.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-invalid-blog-title-count.md` | 해당 없음 | Daily negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-invalid-blog-title-count.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-invalid-extension-field.md` | 해당 없음 | Daily negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-invalid-extension-field.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-invalid-fixed-plan.md` | 해당 없음 | Daily negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-invalid-fixed-plan.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-invalid-oversized-title.md` | 해당 없음 | Daily negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-invalid-oversized-title.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-invalid-paar-action-missing.md` | 해당 없음 | Daily negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-invalid-paar-action-missing.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-invalid-reference-domain.md` | 해당 없음 | Daily negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-invalid-reference-domain.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-daily-valid.md` | 해당 없음 | Daily positive fixture | README, tests, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-daily-valid.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-duplicate-url.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-duplicate-url.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-growth-missing.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-growth-missing.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-growth-vague-action.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-growth-vague-action.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-investment-advice.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-investment-advice.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-investment-missing-indicator.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-investment-missing-indicator.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-investment-missing-risk.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-investment-missing-risk.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-price-only.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-price-only.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-related-stock.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-related-stock.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-invalid-too-many-investment.md` | 해당 없음 | News negative fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-invalid-too-many-investment.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-valid-empty.md` | 해당 없음 | News sparse/empty fixture | README, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-valid-empty.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-valid-quality-score-4.md` | 해당 없음 | News quality fixture | validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-valid-quality-score-4.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-valid-sparse.md` | 해당 없음 | News sparse fixture | README, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-valid-sparse.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-valid-tech-investment.md` | 해당 없음 | News mixed fixture | README, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-valid-tech-investment.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-valid-tech-only.md` | 해당 없음 | News tech-only fixture | README, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-valid-tech-only.md` | fixture 보호 |
| KEEP | `tests/fixtures/kr-tech-news-daily-valid.md` | 해당 없음 | News positive fixture | README, validate.sh | MEDIUM | `git checkout HEAD^ -- tests/fixtures/kr-tech-news-daily-valid.md` | fixture 보호 |
| KEEP | `tests/test_daily_oss_contract.py` | 해당 없음 | OSS validator contract tests | validate.sh/test command path | MEDIUM | `git checkout HEAD^ -- tests/test_daily_oss_contract.py` | test 보호 |
| KEEP | `tests/test_oss_reliability_gate.py` | 해당 없음 | OSS reliability gate tests | validate.sh/test command path | MEDIUM | `git checkout HEAD^ -- tests/test_oss_reliability_gate.py` | test 보호 |
| KEEP | `tests/test_weekly_career_collector.py` | 해당 없음 | Weekly site radar tests | validate.sh/test command path | MEDIUM | `git checkout HEAD^ -- tests/test_weekly_career_collector.py` | test 보호 |
| REMOVE | `configs/oss-repositories 2.json` | 추적되지 않은 예전 OSS config 사본, README/워크플로/스크립트 참조 없음 | `configs/oss-repositories.json` | `git grep`, `rg`, `git log --` 결과 없음 | LOW | git 추적 이력 없음. 필요 시 로컬 백업 또는 이전 작업물에서 복구 | already removed before this pass |
| REMOVE | `docs/oss-candidate-policy 2.md` | 추적되지 않은 예전 OSS 정책 문서 사본, README/문서 참조 없음 | `docs/oss-candidate-policy.md` | `git grep`, `rg`, `git log --` 결과 없음 | LOW | git 추적 이력 없음. 필요 시 로컬 백업 또는 이전 작업물에서 복구 | already removed before this pass |

## Deferred

- `app/`: README 운영 경로에는 없지만 Gradle, Docker, application source, test가 있는 HIGH 위험 영역입니다.
  AGENTS.md도 현재 단계에서 수정하지 말라고 명시하므로 이번 정리에서 삭제하지 않습니다.
- `infra/`: compose, nginx, OpenClaw, deploy script가 있고 외부 배포 참조 가능성이 있는 HIGH 위험 영역입니다.
  이번 정리에서 삭제하지 않습니다.
- ignored `reports/` 산출물: workflow와 로컬 검증이 생성하는 파일이며 저장소에는 `.gitkeep`만 유지합니다.
