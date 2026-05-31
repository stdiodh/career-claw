# Career Feed

Career Feed는 GitHub Actions, 후보 수집 스크립트, Codex 편집, Discord Webhook으로 백엔드 학습/커리어 브리핑을 전송하는 자동화 프로젝트입니다.

## 운영 경로

현재 운영 경로는 4개만 유지합니다.

| 경로 | Workflow | 목적 |
| --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | 평일 백엔드 학습/PS/OSS/실무지식/CS Core/용어 브리핑 |
| Korea Dev/AI News Daily | `.github/workflows/kr-tech-news-daily.yml` | 평일 한국 개발/AI 뉴스 피드 |
| Backend Career Site Radar | `.github/workflows/kr-backend-career-weekly.yml` | 수동 실행형 백엔드 커리어 사이트 레이더 |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | PS 풀이 진행도 기록 |

## 자동 실행 시간

| 경로 | 실행 시간 |
| --- | --- |
| Daily Backend Brief | 평일 08:05 KST 시작, 09:00 KST 전송. 09:25 KST catch-up 실행 |
| Korea Dev/AI News Daily | 평일 08:15 KST 시작, 09:05 KST 전송. 09:30 KST catch-up 실행 |
| Backend Career Site Radar | 자동 실행 없음, 수동 실행 |
| Mark PS Solved | 자동 실행 없음, 수동 실행 |

## Daily Backend Brief

- workflow: `.github/workflows/kr-tech-daily.yml`
- prompt: `.github/codex/prompts/kr-tech-daily-brief.md`
- collector: `python3 scripts/collect-kr-feeds.py --mode daily-backend`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-daily.md --type daily-tech --candidates-dir reports/candidates`
- report: `reports/briefs/kr-tech-daily.md`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_DAILY`
- delivery lock: `career-feed-backend-sent-${KST_DATE}`

후보 파일:

- `reports/candidates/spring-study-topic.json`
- `reports/candidates/ps-weekly-routine.json`
- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/candidates/backend-practical-knowledge.json`
- `reports/candidates/cs-core-daily-topic.json`
- `reports/candidates/backend-term-daily.json`

Daily 수집 소스 정책:

- `spring-study-topic.json`은 `spring-jvm-study-topics` 카테고리에서 생성하며 Naver query를 사용하지 않습니다.
- Spring/JVM 학습 후보는 Spring 공식 블로그, Spring 문서, OpenJDK/Inside Java, Micrometer/OpenTelemetry 등 공식·표준 레퍼런스를 우선합니다.
- 실무지식 curriculum은 `situation`, `failure_mode`, `practice_steps`, `official_refs`를 포함해 브리핑 모델이 실패 상황과 30분 실습을 데이터에서 직접 읽도록 합니다.
- CS Core curriculum은 `configs/backend-core-cs-curriculum.json`에서 KST 날짜 기반으로 1개 topic을 선택하며, computer architecture, OS, network, database, JVM runtime 트랙을 순환합니다.
- 백엔드 용어 glossary는 `configs/backend-terms-glossary.json`에서 KST 날짜 기반으로 1개 term을 선택하며, 정의보다 실무 상황, 오해 위험, Spring/API 연결을 우선합니다.
- validator는 1번 Spring/JVM 학습과 4번 실무지식 링크가 허용 도메인 밖이거나 포털/언론 도메인이면 실패합니다.

출력 섹션:

- 오늘의 Spring Boot/JVM 학습
- 이번 주 PS 성장 루틴
- 오픈소스 기여 후보 또는 OSS 기여 준비 루틴
- 주니어 백엔드 실무지식
- 오늘의 CS Core & 백엔드 용어

Daily OSS 후보 정책:

- OSS 후보는 maintainer/member/collaborator가 올렸거나 maintainer가 초보자용으로 분류한 open issue만 추천합니다.
- `configs/oss-repositories.json`의 저장소별 priority, ecosystem tag, beginner label, avoid label/title keyword, 선호 기여 유형, 로컬 확인 힌트를 scoring과 후보 evidence에 반영합니다.
- 저장소 profile 관리 기준은 `docs/oss-candidate-policy.md`에 정리합니다.
- assignee가 있거나 linked PR/branch가 있거나 누군가 댓글로 작업 의사를 밝힌 이슈는 추천하지 않습니다.
- linked work 확인이 불완전하면 추천하지 않습니다.
- linked PR/branch 확인은 GitHub GraphQL 보조 검증을 통과해야 하며, 검증이 실패하거나 불완전하면 추천하지 않습니다.
- GitHub API 실패, rate limit, repository 접근 실패는 후보 JSON의 `diagnostics`와 `source_errors`에 남깁니다.
- Daily Backend validator는 `kr-oss-contribution-opportunities.json`을 함께 읽고, Markdown의 OSS issue URL이 `safe_to_recommend=true` 후보 URL과 다르면 실패합니다.
- 안전한 후보가 없으면 특정 issue를 추천하지 않고 OSS 기여 준비 루틴을 출력합니다.
- 첫 30분 액션은 읽기, 재현, 문서 위치 확인, 로컬 빌드 확인처럼 PR 전 확인 행동으로 제한합니다.
- 작업 전 issue에 짧게 확인 댓글을 남기는 것을 권장합니다.

## Korea Dev/AI News Daily

- workflow: `.github/workflows/kr-tech-news-daily.yml`
- prompt: `.github/codex/prompts/kr-tech-news-daily.md`
- collector: `python3 scripts/collect-kr-feeds.py --mode daily-news`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-news-daily.md --type daily-news`
- report: `reports/briefs/kr-tech-news-daily.md`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY`
- delivery lock: `career-feed-news-sent-${KST_DATE}`

후보 파일:

- `reports/candidates/kr-dev-ai-news.json`
- `reports/candidates/kr-ai-tech-news.json`

News Daily 정책:

- 한국 개발/AI 뉴스 3~5개를 별도 Discord 웹훅으로 전송합니다.
- 기준을 만족하는 뉴스가 1~2개뿐이면 후보 부족 문구와 함께 그대로 전송하고, 0개면 기준을 만족하는 한국 개발/AI 뉴스가 없다는 문구만 전송합니다.
- 원문 링크가 있으면 원문을 우선 사용하고, Naver News 링크는 fallback으로만 사용합니다.
- 주가, 관련주, 투자 의견 중심 기사와 단순 홍보성 기사는 제외합니다.
- 각 항목은 개발자 실무 연결과 백엔드 주니어 관점을 포함해야 합니다.
- Naver secret이 없거나 Naver API가 실패해도 RSS/공식 페이지 후보로 JSON을 생성합니다.

## Daily 운영 옵션

Backend Daily와 News Daily의 `workflow_dispatch`는 같은 입력을 사용합니다.

- `dry_run=true`: 후보 생성, Codex 생성, validator, artifact 업로드까지만 수행하고 Discord 전송과 delivery lock 저장은 하지 않습니다.
- `force_send=true`: 같은 날짜의 delivery lock이 있어도 Discord 전송을 수행합니다.
- 기본 scheduled run은 `dry_run=false`, `force_send=false`입니다.

중복 전송 방지:

- Discord 전송 성공 후에만 GitHub Actions cache에 delivery lock marker를 저장합니다.
- 같은 날짜 lock이 있고 `force_send=false`이면 Discord 전송을 skip합니다.
- `dry_run=true` 또는 Discord 전송 실패 시 lock을 저장하지 않습니다.

GitHub Actions scheduled workflow는 Actions 부하에 따라 지연되거나 실행이 누락될 수 있습니다. Backend Daily는 09:25 KST, News Daily는 09:30 KST에 catch-up schedule을 한 번 더 두고, delivery lock으로 중복 전송을 막습니다.

운영 요약:

- Backend Daily: `reports/ops/backend-daily-run-summary.json`, `reports/ops/backend-daily-run-summary.md`
- News Daily: `reports/ops/news-daily-run-summary.json`, `reports/ops/news-daily-run-summary.md`
- 실패 알림 선택 secret: `DISCORD_WEBHOOK_CAREER_FEED_OPS`
- Daily Growth 운영 확인 방법: `docs/daily-growth-ops.md`

## Backend Career Site Radar

- workflow: `.github/workflows/kr-backend-career-weekly.yml`
- config: `configs/weekly-career-site-radar.json`
- collector: `python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run`
- renderer: `python3 scripts/render-weekly-career-site-radar.py`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career`
- report: `reports/briefs/kr-backend-career-weekly.md`
- Discord secret: `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

출력 파일:

- `reports/candidates/weekly-career-site-radar.json`
- `reports/briefs/kr-backend-career-weekly.md`

호환용 JSON 파일:

- `reports/candidates/kr-backend-career-events.json`
- `reports/candidates/kr-backend-jobs.json`
- `reports/candidates/kr-backend-interns.json`
- `reports/candidates/kr-backend-hackathons.json`
- `reports/candidates/kr-backend-contests.json`
- `reports/candidates/kr-backend-competitions.json`

Site Radar 정책:

- Weekly Backend Career는 더 이상 자동 추천 피드가 아닙니다.
- 사용자가 필요할 때 Actions에서 수동 실행하는 Career Site Radar입니다.
- 실행하면 Discord로 공식 채용 사이트, 채용·인턴 플랫폼, 대외활동/대회 플랫폼과 검색 키워드가 전송됩니다.
- 마감일, 회사/주최, 직무/역할은 사용자가 원문에서 직접 판단합니다.
- 이 방식은 자동 파싱 오류와 hallucination을 피하기 위한 선택입니다.
- Weekly 본문은 정적 site radar config에서 생성하며 AI 생성 단계로 재작성하지 않습니다.
- 사이트는 중복 없이 출력하고, 같은 서비스의 여러 경로는 `links` 배열로 관리합니다.
- 호환용 JSON 파일은 `items: []`와 `diagnostics.status: disabled`만 담습니다.
- `data/weekly-career-candidate-cache.json`은 삭제되었고 workflow에서 업데이트하거나 commit하지 않습니다.

수동 실행 방법:

1. `Actions > Backend Career Site Radar`를 엽니다.
2. `Run workflow`를 선택합니다.
3. `send_to_discord`를 `true`로 둡니다.
4. Discord에서 사이트와 검색 키워드를 확인합니다.

## Mark PS Solved

- workflow: `.github/workflows/mark-ps-solved.yml`
- progress file: `data/ps-progress.json`
- 실행 방식: 수동 실행
- local command: `python3 scripts/update-ps-progress.py --problem-id <problem_id> --note "<memo>"`

현재 상태 확인:

```bash
python3 scripts/update-ps-progress.py --status
```

## OSS Progress Notes

- progress file: `data/oss-progress.json`
- local command: `python3 scripts/update-oss-progress.py --status`
- mark reviewed/skipped/attempted: `python3 scripts/update-oss-progress.py --mark-reviewed <GitHub issue URL> --note "<memo>"`

이 기록은 로컬 정적 JSON만 수정하며 GitHub issue에 댓글, assign, label 변경을 하지 않습니다.

## 필요한 Secrets

| 경로 | Secrets |
| --- | --- |
| Daily Backend Brief | `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY` |
| Korea Dev/AI News Daily | `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` |
| Backend Career Site Radar | `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` |
| Mark PS Solved | 없음 |

`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`은 Korea Dev/AI News Daily 품질 향상용 선택 secret입니다. Backend Daily와 Career Site Radar에서는 사용하지 않습니다.
`DISCORD_WEBHOOK_CAREER_FEED_OPS`는 workflow 실패 알림용 선택 secret입니다. 없으면 실패 알림만 skip합니다.

Secret 값, API Key, Webhook URL은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## Actions 체크리스트

1. `Settings > Secrets and variables > Actions`에 필요한 secrets를 등록합니다.
2. `Settings > Actions > General`에서 Actions 실행이 허용되어 있는지 확인합니다.
3. `Actions > Daily Korea Tech Brief`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
4. `Actions > Daily Korea Dev AI News`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
5. `Actions > Backend Career Site Radar`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
6. `Actions > Mark PS Solved`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
7. Backend Daily와 News Daily를 먼저 `dry_run=true`, `force_send=false`로 실행해 artifact와 validator를 확인합니다.
8. 실제 전송 검증은 `dry_run=false`, `force_send=true`로 실행합니다.
9. 같은 날 다시 `dry_run=false`, `force_send=false`로 실행해 delivery lock skip을 확인합니다.
10. 이후 Backend Daily는 평일 09:00 KST 전후, News Daily는 평일 09:05 KST 전후에 도착합니다.

GitHub Actions scheduled workflow는 default branch의 최신 workflow 파일을 기준으로 실행됩니다.
GitHub Actions 부하가 높은 시간대에는 scheduled workflow가 지연될 수 있고, 매우 높은 부하에서는 일부 queued job이 drop될 수 있습니다.
그래서 Backend Daily와 News Daily는 00분/30분을 피하고 각각 08:05, 08:15 KST에 시작하며, catch-up schedule과 delivery lock으로 지연/누락과 중복 전송 위험을 완화합니다.
public repository는 장기간 활동이 없으면 scheduled workflow가 자동 비활성화될 수 있으므로 Actions 탭에서 workflow가 enabled 상태인지 확인합니다.

## 로컬 검증

```bash
python3 scripts/check-workflow-schedules.py
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/render-weekly-career-site-radar.py
python3 scripts/update-oss-progress.py --status
python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-sparse.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-empty.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

## 디렉터리 구조

```text
repository-root/
├─ .github/
│  ├─ codex/prompts/
│  │  ├─ kr-tech-daily-brief.md
│  │  └─ kr-tech-news-daily.md
│  └─ workflows/
│     ├─ kr-backend-career-weekly.yml
│     ├─ kr-tech-news-daily.yml
│     ├─ kr-tech-daily.yml
│     └─ mark-ps-solved.yml
├─ configs/
│  ├─ audience-profile.json
│  ├─ backend-core-cs-curriculum.json
│  ├─ backend-practical-knowledge-curriculum.json
│  ├─ backend-terms-glossary.json
│  ├─ company-career-watchlist.json
│  ├─ kr-sources.json
│  ├─ oss-repositories.json
│  ├─ programmers-ps-curriculum.json
│  └─ weekly-career-site-radar.json
├─ data/
│  ├─ oss-progress.json
│  └─ ps-progress.json
├─ reports/
│  ├─ briefs/
│  ├─ candidates/
│  └─ ops/
├─ scripts/
│  ├─ check-workflow-schedules.py
│  ├─ collect-kr-feeds.py
│  ├─ render-weekly-career-site-radar.py
│  ├─ select-ps-problem.py
│  ├─ send-discord.py
│  ├─ update-oss-progress.py
│  ├─ update-ps-progress.py
│  ├─ validate-career-feed-brief.py
│  └─ validate.sh
└─ tests/fixtures/
   ├─ kr-backend-career-weekly-valid.md
   ├─ kr-tech-daily-valid.md
   ├─ kr-tech-news-daily-valid-empty.md
   ├─ kr-tech-news-daily-valid-sparse.md
   └─ kr-tech-news-daily-valid.md
```

## 운영 정책

- `reports/` 산출물은 기본적으로 저장소에 커밋하지 않습니다.
- 원본 URL을 보존합니다.
- 긴 요약보다 사용자의 다음 행동과 원문 접근성을 우선합니다.
- Spring OSS 후보는 GitHub issue 기반으로 추천만 하며 자동 댓글, PR 생성, assign은 하지 않습니다.
- OpenJDK/JBS는 난이도 모델 참고로만 사용하고 직접 수집하지 않습니다.
- 기사 전문, Secret 값, Webhook URL은 저장소와 로그에 남기지 않습니다.
