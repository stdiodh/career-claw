# Career Feed

Career Feed는 GitHub Actions, 후보 수집 스크립트, Codex 편집, Discord Webhook으로 백엔드 학습/커리어 브리핑을 전송하는 자동화 프로젝트입니다.

## 운영 경로

현재 운영 경로는 3개만 유지합니다.

| 경로 | Workflow | 목적 |
| --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | 평일 백엔드 학습/PS/OSS/뉴스/실무지식 브리핑 |
| Weekly Backend Career Brief | `.github/workflows/kr-backend-career-weekly.yml` | 주간 백엔드 인턴/신입/대외활동 브리핑 |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | PS 풀이 진행도 기록 |

## 자동 실행 시간

| 경로 | 실행 시간 |
| --- | --- |
| Daily Backend Brief | 평일 08:47 KST |
| Weekly Backend Career Brief | 월요일 09:07 KST |
| Mark PS Solved | 자동 실행 없음, 수동 실행 |

## Daily Backend Brief

- workflow: `.github/workflows/kr-tech-daily.yml`
- prompt: `.github/codex/prompts/kr-tech-daily-brief.md`
- collector: `python3 scripts/collect-kr-feeds.py --mode daily-tech`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-daily.md --type daily-tech`
- report: `reports/briefs/kr-tech-daily.md`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_DAILY`

후보 파일:

- `reports/candidates/spring-study-topic.json`
- `reports/candidates/ps-weekly-routine.json`
- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/candidates/kr-dev-ai-news.json`
- `reports/candidates/kr-ai-tech-news.json`
- `reports/candidates/backend-practical-knowledge.json`

Daily OSS 후보 정책:

- OSS 후보는 maintainer/member/collaborator가 올렸거나 maintainer가 초보자용으로 분류한 open issue만 추천합니다.
- assignee가 있거나 linked PR/branch가 있거나 누군가 댓글로 작업 의사를 밝힌 이슈는 추천하지 않습니다.
- linked work 확인이 불완전하면 추천하지 않습니다.
- 후보가 없으면 empty-state를 출력합니다.
- 첫 30분 액션은 읽기, 재현, 문서 위치 확인, 로컬 빌드 확인처럼 PR 전 확인 행동으로 제한합니다.
- 작업 전 issue에 짧게 확인 댓글을 남기는 것을 권장합니다.

## Weekly Backend Career Brief

- workflow: `.github/workflows/kr-backend-career-weekly.yml`
- prompt: `.github/codex/prompts/kr-backend-career-weekly.md`
- collector: `python3 scripts/collect-kr-feeds.py --mode weekly-career`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career`
- report: `reports/briefs/kr-backend-career-weekly.md`
- Discord secret: `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

후보 파일:

- `reports/candidates/kr-backend-career-events.json`
- `reports/candidates/kr-backend-jobs.json`
- `reports/candidates/kr-backend-interns.json`
- `reports/candidates/kr-backend-hackathons.json`
- `reports/candidates/kr-backend-contests.json`
- `reports/candidates/kr-backend-competitions.json`
- `reports/candidates/kr-backend-intern-jobs.json`
- `reports/candidates/kr-backend-entry-jobs.json`
- `reports/candidates/kr-backend-career-activities.json`
- `reports/candidates/kr-backend-company-watchlist.json`

Weekly Career 후보 정책:

- 뉴스 검색 결과는 최종 추천 후보로 사용하지 않습니다.
- 목록 페이지는 discovery source로만 사용하고 최종 추천 후보로 사용하지 않습니다.
- Weekly는 매주 채용, 인턴, 해커톤, 공모전, 경진대회 5개 유형을 따로 확인합니다.
- 각 유형은 fresh 상세 URL 후보를 우선 사용합니다.
- fresh 후보가 없으면 `data/weekly-career-candidate-cache.json`에 남은 지난 후보를 오늘 다시 fetch해 유효할 때만 backfill합니다.
- cache backfill 후보는 Discord 본문에서 `지난 후보를 오늘 다시 확인했고 아직 유효합니다.`처럼 표시됩니다.
- 최종 추천은 채용, 인턴, 해커톤, 공모전, 경진대회 상세 URL을 fetch해 파싱한 후보만 사용합니다.
- 뉴스 기사, 보도자료, 수상 기사, 개최 완료 기사, 결과 발표 기사, 종료된 행사는 제외합니다.
- generic 목록 URL은 최종 후보로 사용하지 않습니다.
- 마감일과 회사/주최는 원문에서 확인된 경우에만 출력합니다.
- 마감일이나 회사/주최를 모르면 만들지 않고 해당 필드를 생략합니다.
- 백엔드 직접 공고가 없으면 IT/시스템개발/응용프로그램개발/API/데이터/AI 서비스처럼 백엔드로 연결 가능한 인턴/활동까지 보수적으로 허용합니다.
- 후보가 없는 유형은 empty-state로 표시합니다.
- 후보가 0개일 때는 artifact의 `diagnostics.coverage`에서 어떤 유형이 왜 비었는지 확인합니다.
- Naver News Search는 Weekly Career 최종 후보 source로 쓰지 않습니다.
- Daily 한국 개발/AI 뉴스와 Weekly Career 후보 수집은 별도 정책으로 관리합니다.

## Mark PS Solved

- workflow: `.github/workflows/mark-ps-solved.yml`
- progress file: `data/ps-progress.json`
- 실행 방식: 수동 실행
- local command: `python3 scripts/update-ps-progress.py --problem-id <problem_id> --note "<memo>"`

현재 상태 확인:

```bash
python3 scripts/update-ps-progress.py --status
```

## 필요한 Secrets

필수:

- `OPENAI_API_KEY`
- `DISCORD_WEBHOOK_KR_TECH_DAILY`
- `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

권장:

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`

OpenAI/Discord secrets는 실행 필수입니다. Naver secrets는 Daily 한국 개발/AI 뉴스 수집용입니다. Weekly Career 최종 후보에는 Naver News Search 결과를 사용하지 않습니다.

Secret 값, API Key, Webhook URL은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## 자동 실행 체크리스트

1. `Settings > Secrets and variables > Actions`에 필수 secrets를 등록합니다.
2. `Settings > Actions > General`에서 Actions 실행이 허용되어 있는지 확인합니다.
3. `Workflow permissions`는 `Read and write permissions`로 설정합니다.
4. `Actions > Daily Korea Tech Brief`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
5. `Actions > Weekly Backend Career Brief`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
6. `Actions > Mark PS Solved`에서 `Enable workflow`가 보이면 눌러 활성화합니다.
7. Daily와 Weekly를 각각 `Run workflow`로 1회 수동 실행해 Discord 도착 여부를 확인합니다.
8. 이후 Daily는 평일 08:47 KST, Weekly는 월요일 09:07 KST에 자동 실행됩니다.

GitHub Actions scheduled workflow는 default branch의 최신 workflow 파일을 기준으로 실행됩니다.
GitHub Actions 부하가 높은 시간대에는 scheduled workflow가 지연될 수 있고, 매우 높은 부하에서는 일부 queued job이 drop될 수 있습니다.
그래서 이 저장소는 00분/30분을 피하고 08:47, 09:07 KST로 실행합니다.
public repository는 장기간 활동이 없으면 scheduled workflow가 자동 비활성화될 수 있으므로 Actions 탭에서 workflow가 enabled 상태인지 확인합니다.

## 로컬 검증

```bash
python3 scripts/check-workflow-schedules.py
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

## 디렉터리 구조

```text
repository-root/
├─ .github/
│  ├─ codex/prompts/
│  │  ├─ kr-backend-career-weekly.md
│  │  └─ kr-tech-daily-brief.md
│  └─ workflows/
│     ├─ kr-backend-career-weekly.yml
│     ├─ kr-tech-daily.yml
│     └─ mark-ps-solved.yml
├─ configs/
│  ├─ audience-profile.json
│  ├─ backend-practical-knowledge-curriculum.json
│  ├─ company-career-watchlist.json
│  ├─ kr-sources.json
│  ├─ oss-repositories.json
│  └─ programmers-ps-curriculum.json
├─ data/
│  └─ ps-progress.json
├─ reports/
│  ├─ briefs/
│  └─ candidates/
├─ scripts/
│  ├─ check-workflow-schedules.py
│  ├─ collect-kr-feeds.py
│  ├─ select-ps-problem.py
│  ├─ send-discord.py
│  ├─ update-ps-progress.py
│  ├─ validate-career-feed-brief.py
│  └─ validate.sh
└─ tests/fixtures/
   ├─ kr-backend-career-weekly-valid.md
   └─ kr-tech-daily-valid.md
```

## 운영 정책

- `reports/` 산출물은 기본적으로 저장소에 커밋하지 않습니다.
- 원본 URL을 보존합니다.
- 긴 요약보다 사용자의 다음 행동과 원문 접근성을 우선합니다.
- Spring OSS 후보는 GitHub issue 기반으로 추천만 하며 자동 댓글, PR 생성, assign은 하지 않습니다.
- OpenJDK/JBS는 난이도 모델 참고로만 사용하고 직접 수집하지 않습니다.
- 기사 전문, Secret 값, Webhook URL은 저장소와 로그에 남기지 않습니다.
