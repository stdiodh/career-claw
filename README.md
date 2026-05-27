# Career Feed

Career Feed는 GitHub Actions, 후보 수집 스크립트, Codex 편집, Discord Webhook으로 개발자 커리어 브리핑을 전송하는 자동화 프로젝트입니다.

기본 자동 알림은 `KR_PREMIUM_MODE`의 v2 구조입니다.

- 평일 09:10 KST: `Daily Korea Tech Brief`
- 월요일 09:30 KST: `Weekly Backend Career Brief`

기존 4섹션 통합 `Daily Korea Premium Brief`는 너무 넓어져서 manual legacy workflow로만 보존합니다. 무료 RSS/Atom 기반 `FREE_MODE`도 삭제하지 않고 수동 백업 workflow로 유지합니다.

## 프로젝트 이름 정책

- 제품명과 문서명은 `Career Feed`로 통일합니다.
- 저장소 이름이나 로컬 경로명은 환경에 따라 다를 수 있으며, 제품명을 의미하지 않습니다.
- 현재 기본 운영은 GitHub Actions, 한국 후보 수집, AI 편집, Markdown 검증, 분리된 Discord Webhook 전송으로 구성합니다.

## 운영 모드

| 모드 | 용도 | 기본 실행 여부 |
| --- | --- | --- |
| `KR_PREMIUM_MODE` v2 | 한국 AI 테크/백엔드 기술 daily, 백엔드 커리어 weekly | 자동 |
| Legacy KR Premium | 기존 4섹션 통합 브리핑 | 수동 백업 |
| `FREE_MODE` | 무료 RSS/Atom 수집, 규칙 기반 요약 | 수동 백업 |
| `AI_LIGHT_MODE` | 수집된 후보 JSON만 Codex가 짧게 정제, live web search 없음 | 수동 실행 |
| `AI_SEARCH_MODE` | Codex live web search 기반 수동 고급 브리핑 | 수동 실행 |

## 핵심 기능

- 25살 Kotlin/Spring Boot 백엔드 지망생 기준의 한국어 액션 리스트 생성
- Naver News Search API, RSS, 공식 페이지, GitHub Issues 기반 후보 pool 생성
- Daily Tech: 한국 AI 테크, 백엔드/개발자 기술, 오픈소스 기여 후보를 선별
- Weekly Career: 백엔드 인턴, 신입/주니어, 해커톤, 공모전, 경진대회만 선별
- Daily Tech는 Spring Boot/Kotlin/JVM GitHub issue 기반 오픈소스 기여 후보를 최대 1개 포함
- 보안 알림은 기본 daily 알림에서 제외하고 legacy/manual 백업으로만 유지
- Codex Action의 `output-file`은 summary 파일로만 사용하고, 실제 브리핑 파일은 workspace에 직접 작성
- Discord Webhook은 Daily Tech와 Weekly Career를 분리해 사용

초기 범위에 포함하지 않는 항목은 다음과 같습니다.

- 상시 실행 서버
- Discord Gateway Bot
- Slash Command
- 데이터베이스 저장
- 로그인/회원 기능
- 웹 대시보드

`app/`와 `infra/`는 현재 기본 오전 알림 운영 경로에서 사용하지 않습니다. 서버 또는 인프라 확장을 진행할 때 재검토합니다.

## 기본 아키텍처

```text
GitHub Actions
        |
        v
KR candidate collection
Naver News Search API + RSS/official references
        |
        v
reports/candidates/*.json
        |
        v
Codex KR Premium v2 editor
        |
        v
reports/briefs/*.md
        |
        v
DISCORD_WEBHOOK_KR_TECH_DAILY
DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY
```

Daily Tech 출력:

- `reports/candidates/kr-ai-tech-news.json`
- `reports/candidates/kr-backend-tech-news.json`
- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/briefs/kr-tech-daily.md`

Weekly Career 출력:

- `reports/candidates/kr-backend-career-events.json`
- `reports/briefs/kr-backend-career-weekly.md`

## 필요한 Secrets

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에 다음 Secrets를 등록합니다.

### 기본 운영 유지 Secrets

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | Codex 편집에 사용하는 OpenAI API Key |
| `NAVER_CLIENT_ID` | Naver News Search API 후보 수집용 |
| `NAVER_CLIENT_SECRET` | Naver News Search API 후보 수집용 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Daily Korea Tech Brief를 전송할 Discord Webhook URL |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Weekly Backend Career Brief를 전송할 Discord Webhook URL |

Daily workflow의 필수 검사는 `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY`를 대상으로 합니다. Weekly workflow의 필수 검사는 `OPENAI_API_KEY`, `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`를 대상으로 합니다. Naver Secrets가 없으면 RSS/공식 URL 후보만 수집하므로 품질이 낮아질 수 있습니다.

### Legacy/manual KR Premium용 선택 Secret

| Secret | 설명 |
| --- | --- |
| `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` | 기존 4섹션 통합 manual legacy 브리핑 전송이 필요할 때 |

### Legacy/manual free RSS용 선택 Secrets

| Secret | 설명 |
| --- | --- |
| `DISCORD_WEBHOOK_DAILY_OVERVIEW` | 수동 무료 RSS Daily Overview 전송이 필요할 때 |
| `DISCORD_WEBHOOK_AI_NEWS` | 수동 무료 RSS AI News 전송이 필요할 때 |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | 수동 무료 RSS Backend News 전송이 필요할 때 |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | 수동 무료 RSS Security Alerts 전송이 필요할 때 |
| `DISCORD_WEBHOOK_BACKEND_TECH` | legacy Backend Tech 전송이 필요할 때 |
| `DISCORD_WEBHOOK_JOB_FEED` | legacy Job Feed 전송이 필요할 때 |

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## Workflow

### Daily Korea Tech Brief

`.github/workflows/kr-tech-daily.yml`

- 평일 `00:10 UTC`, 즉 `09:10 Asia/Seoul` 실행 요청
- `workflow_dispatch` 수동 실행 가능
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-tech`
- 입력 후보: `kr-ai-tech-news.json`, `kr-backend-tech-news.json`, `kr-oss-contribution-opportunities.json`
- prompt: `.github/codex/prompts/kr-tech-daily-brief.md`
- 실제 report: `reports/briefs/kr-tech-daily.md`
- Codex summary: `reports/briefs/kr-tech-daily-codex-summary.md`
- 검증: `python3 scripts/validate-kr-premium-brief.py reports/briefs/kr-tech-daily.md --type daily-tech`
- Discord Secret: `DISCORD_WEBHOOK_KR_TECH_DAILY`

### Weekly Backend Career Brief

`.github/workflows/kr-backend-career-weekly.yml`

- 월요일 `00:30 UTC`, 즉 `09:30 Asia/Seoul` 실행 요청
- `workflow_dispatch` 수동 실행 가능
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode weekly-career`
- 입력 후보: `kr-backend-career-events.json`
- prompt: `.github/codex/prompts/kr-backend-career-weekly.md`
- 실제 report: `reports/briefs/kr-backend-career-weekly.md`
- Codex summary: `reports/briefs/kr-backend-career-weekly-codex-summary.md`
- 검증: `python3 scripts/validate-kr-premium-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career`
- Discord Secret: `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

### Manual Legacy Korea Premium Brief

`.github/workflows/kr-premium-brief.yml`

- 기존 4섹션 통합 브리핑을 수동 백업으로 보존
- 자동 schedule 없음
- prompt: `.github/codex/prompts/kr-premium-brief.md`
- 실제 report: `reports/briefs/kr-premium-daily.md`

### Manual Free RSS Career Feed

`.github/workflows/daily-feed.yml`

- 수동 백업 workflow
- 자동 schedule 없음
- `OPENAI_API_KEY` 불필요
- Codex Action과 live web search를 사용하지 않음

### Manual AI Light / Search Brief

- `.github/workflows/ai-brief-manual.yml`: 후보 JSON만 정제, `--search` 미사용
- `.github/workflows/daily-news.yml`: live web search 기반 수동 고급 모드

## 로컬 검증

Secret 없이 파일 구조, Python 문법, 무료 브리핑 렌더링, validation fixture를 확인할 수 있습니다.

```bash
./scripts/validate.sh
```

KR Premium v2 후보 JSON 스키마만 확인하려면 다음을 실행합니다.

```bash
python3 scripts/collect-kr-feeds.py --dry-run
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
```

실제 Discord 전송은 workflow 또는 전송 스크립트를 명시적으로 실행할 때만 수행합니다.

## 디렉터리 구조

```text
repository-root/
├─ .github/
│  ├─ codex/prompts/
│  │  ├─ compact-brief.md
│  │  ├─ daily-news.md
│  │  ├─ kr-backend-career-weekly.md
│  │  ├─ kr-premium-brief.md
│  │  └─ kr-tech-daily-brief.md
│  └─ workflows/
│     ├─ ai-brief-manual.yml
│     ├─ daily-feed.yml
│     ├─ daily-news.yml
│     ├─ kr-backend-career-weekly.yml
│     ├─ kr-premium-brief.yml
│     └─ kr-tech-daily.yml
├─ configs/
│  ├─ audience-profile.json
│  ├─ channels.json
│  ├─ kr-sources.json
│  └─ sources.json
├─ docs/
├─ refs/categories/
├─ reports/
│  ├─ briefs/
│  └─ candidates/
└─ scripts/
```

## 운영 정책

- `reports/` 산출물은 기본적으로 저장소에 커밋하지 않는다.
- 원본 URL을 반드시 보존한다.
- 긴 요약보다 원문 링크 접근성과 사용자의 다음 행동을 우선한다.
- 기본 자동 알림은 KR Premium v2 Daily/Weekly workflow가 담당한다.
- 기존 무료 RSS workflow와 legacy KR Premium workflow는 수동 백업으로만 사용한다.
- 오픈소스 후보는 GitHub issue 기반으로 추천만 하며 자동 댓글, PR 생성, assign은 하지 않는다.
- 보안 알림은 기본 daily에 포함하지 않고 legacy/manual 백업으로만 다룬다.
- 기사 전문, Secret 값, Webhook URL은 저장소와 로그에 남기지 않는다.

## GitHub Secrets 정리

남길 Secrets:

```text
OPENAI_API_KEY
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
DISCORD_WEBHOOK_KR_TECH_DAILY
DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY
```

legacy/manual로만 남길 수 있는 Secrets:

```text
DISCORD_WEBHOOK_KR_PREMIUM_BRIEF
DISCORD_WEBHOOK_DAILY_OVERVIEW
DISCORD_WEBHOOK_AI_NEWS
DISCORD_WEBHOOK_BACKEND_NEWS
DISCORD_WEBHOOK_SECURITY_ALERTS
DISCORD_WEBHOOK_BACKEND_TECH
DISCORD_WEBHOOK_JOB_FEED
```

실제 GitHub Secrets 삭제는 이 저장소에서 자동으로 수행하지 않습니다. 새 Daily/Weekly workflow의 Discord 도착을 확인한 뒤 GitHub UI에서 직접 정리합니다.
