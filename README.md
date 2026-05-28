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
- `reports/candidates/kr-backend-intern-jobs.json`
- `reports/candidates/kr-backend-entry-jobs.json`
- `reports/candidates/kr-backend-career-activities.json`
- `reports/candidates/kr-backend-company-watchlist.json`

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

OpenAI/Discord secrets는 실행 필수입니다. Naver secrets는 한국 뉴스/채용 후보 품질 향상용입니다. Naver secrets가 없으면 fallback 후보만 사용되어 품질이 낮을 수 있습니다.

Secret 값, API Key, Webhook URL은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## 최초 운영 체크리스트

1. `Settings > Secrets and variables > Actions`에 필수 secrets를 등록합니다.
2. `Settings > Actions > General`에서 Actions 실행을 허용합니다.
3. `Workflow permissions`는 `Read and write permissions`로 설정합니다.
4. `Actions > Daily Korea Tech Brief`에서 workflow가 disabled 상태라면 `Enable workflow`를 누릅니다.
5. `Run workflow`로 Daily를 1회 수동 실행합니다.
6. Discord에 Daily 메시지가 도착했는지 확인합니다.
7. `Actions > Weekly Backend Career Brief`에서 workflow가 disabled 상태라면 `Enable workflow`를 누릅니다.
8. `Run workflow`로 Weekly를 1회 수동 실행합니다.
9. Discord에 Weekly 메시지가 도착했는지 확인합니다.
10. `Mark PS Solved`는 문제 풀이 후 `problem_id`를 넣어 수동 실행합니다.

## 로컬 검증

```bash
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
