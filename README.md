# Career Feed

Career Feed는 GitHub Actions, 후보 수집 스크립트, Codex 편집, Discord Webhook으로 백엔드 학습/커리어 브리핑을 전송하는 자동화 프로젝트입니다.

제품명과 문서명은 `Career Feed`로 통일합니다. 저장소 이름이나 로컬 경로명은 환경에 따라 다를 수 있습니다.

## 운영 경로

현재 운영 경로는 3개만 유지합니다.

| 경로 | Workflow | 목적 |
| --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | 평일 백엔드 학습/PS/OSS/뉴스/실무지식 브리핑 |
| Weekly Backend Career Brief | `.github/workflows/kr-backend-career-weekly.yml` | 주간 백엔드 인턴/신입/대외활동 브리핑 |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | PS 풀이 진행도 기록 |

초기 범위에 포함하지 않는 항목은 상시 실행 서버, Discord Gateway Bot, Slash Command, 데이터베이스, 웹 대시보드입니다.

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

브리핑은 Spring Boot/JVM 학습, Programmers 주차별 PS 루틴, Spring OSS 기여 후보, 한국 최신 개발/AI 뉴스, 주니어 백엔드 실무지식으로 구성합니다. Programmers PS 루틴은 `configs/programmers-ps-curriculum.json`과 `data/ps-progress.json`만 사용하며 사이트 크롤링이나 제출 결과 자동 수집을 하지 않습니다.

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

브리핑은 백엔드 인턴, 신입/주니어 공고, 해커톤, 공모전, 경진대회만 선별합니다. 상세 공고 URL과 마감 품질이 낮은 항목은 validator가 막습니다.

## Mark PS Solved

- workflow: `.github/workflows/mark-ps-solved.yml`
- progress file: `data/ps-progress.json`
- local command: `python3 scripts/update-ps-progress.py --mark-solved <problem_id> --notes "<memo>"`

현재 상태 확인:

```bash
python3 scripts/update-ps-progress.py --status
```

## 필요한 Secrets

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에 다음 Secrets를 등록합니다.

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | Codex 편집에 사용하는 OpenAI API Key |
| `NAVER_CLIENT_ID` | Naver News Search API 후보 수집용 |
| `NAVER_CLIENT_SECRET` | Naver News Search API 후보 수집용 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Daily Backend Brief 전송용 Discord Webhook URL |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Weekly Backend Career Brief 전송용 Discord Webhook URL |

Naver Secrets가 없으면 RSS, 공식 URL, 정적 config 중심으로만 후보를 만들기 때문에 후보 품질이 낮아질 수 있습니다.

Secret 값, API Key, Webhook URL은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## 로컬 검증

```bash
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

실제 Discord 전송은 workflow 또는 `scripts/send-discord.py`를 명시적으로 실행할 때만 수행합니다.

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
