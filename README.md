# Career Feed

Career Feed는 AI와 백엔드 개발자에게 필요한 최신 기술 뉴스, 보안 알림, 채용공고 후보를 Discord로 전달하는 자동 브리핑 프로젝트입니다.

기본 운영은 OpenAI API를 사용하지 않는 `FREE_MODE`입니다. 코드가 RSS/Atom/공식 URL에서 후보를 수집하고, 규칙 기반으로 짧은 Markdown 브리핑을 만든 뒤 카테고리별 Discord Webhook으로 전송합니다. AI는 필요할 때만 수동으로 짧은 정제에 사용합니다.

## 프로젝트 이름 정책

- 제품명과 문서명은 `Career Feed`로 통일합니다.
- 저장소 이름이나 로컬 경로명은 환경에 따라 다를 수 있으며, 제품명을 의미하지 않습니다.
- 현재 운영 MVP는 GitHub Actions, RSS/Atom 수집, Markdown 생성, Discord Webhook 전송으로 구성합니다.

## 운영 모드

| 모드 | 용도 | 기본 실행 여부 |
| --- | --- | --- |
| `FREE_MODE` | 무료 RSS/Atom 수집, 규칙 기반 요약, 카테고리별 Discord 전송 | 매일 자동 |
| `KR_PREMIUM_MODE` | 한국 중심 AI 검색/선별 통합 브리핑 | 매일 자동 가능, OpenAI 비용 발생 |
| `AI_LIGHT_MODE` | 수집된 후보 JSON만 Codex가 짧게 정제, live web search 없음 | 수동 실행 |
| `AI_SEARCH_MODE` | Codex live web search 기반 수동 고급 브리핑 | 수동 실행 |

기본 매일 알림은 `FREE_MODE`가 담당하며 `OPENAI_API_KEY`가 없어도 실행됩니다. `KR_PREMIUM_MODE`는 별도 workflow로 운영하고, `Daily Career Feed`에는 `OPENAI_API_KEY`를 추가하지 않습니다.

## 핵심 기능

- 매일 `09:03 Asia/Seoul` 실행 요청, `09:07` Daily Overview 전송 후 카테고리별 순차 전송
- RSS/Atom 기반 후보 URL 수집
- 원본 URL 보존
- 후보가 없어도 "오늘 확인된 주요 항목이 없습니다." 메시지 생성
- 카테고리별 최대 항목 수 제한
- Discord Webhook 카테고리 분리
- 선택형 AI 정제 workflow 제공
- live web search workflow는 수동 고급 모드로만 보존

초기 범위에 포함하지 않는 항목은 다음과 같습니다.

- 상시 실행 서버
- Discord Gateway Bot
- Slash Command
- 데이터베이스 저장
- 로그인/회원 기능
- 웹 대시보드

`app/`와 `infra/`는 현재 `FREE_MODE` MVP 운영 경로에서 사용하지 않습니다. 서버 또는 인프라 확장을 진행할 때 재검토합니다.

## 아키텍처

```text
GitHub Actions
        |
        v
RSS/Atom/official URL collection
        |
        v
reports/candidates/{category}.json
        |
        v
Rule-based Markdown renderer
        |
        v
reports/briefs/{category}.md
        |
        v
Category Discord Webhooks
```

선택형 AI 정제는 이미 생성된 후보 JSON과 `refs/categories/*.md`만 사용합니다. `AI_LIGHT_MODE`에서는 `--search`를 사용하지 않습니다.

## 필요한 Secrets

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에 다음 Secrets를 등록합니다. `FREE_MODE` MVP 운영에는 enabled 채널의 Webhook Secret만 필수입니다.

### MVP 필수 Secrets

| Secret | 설명 |
| --- | --- |
| `DISCORD_WEBHOOK_DAILY_OVERVIEW` | Daily Overview 채널 Webhook URL |
| `DISCORD_WEBHOOK_AI_NEWS` | AI News 채널 Webhook URL |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | Backend News 채널 Webhook URL |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | Security Alerts 채널 Webhook URL |

### 선택 Secrets

| Secret | 필요한 경우 |
| --- | --- |
| `DISCORD_WEBHOOK_BACKEND_TECH` | Backend Tech Radar 채널을 활성화하거나 수동 전송할 때 |
| `DISCORD_WEBHOOK_JOB_FEED` | Job Feed 채널을 활성화하거나 수동 전송할 때 |
| `OPENAI_API_KEY` | `AI_LIGHT_MODE`, `AI_SEARCH_MODE` 수동 workflow를 실행할 때 |
| `NAVER_CLIENT_ID` | `KR_PREMIUM_MODE` 후보 수집에서 Naver News Search API를 사용할 때 |
| `NAVER_CLIENT_SECRET` | `KR_PREMIUM_MODE` 후보 수집에서 Naver News Search API를 사용할 때 |

### KR_PREMIUM_MODE 필수 Secrets

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | 한국 중심 AI 브리핑 생성에 사용하는 OpenAI API Key |
| `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` | KR Premium 통합 브리핑을 전송할 Discord Webhook URL |

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## Workflow

### Daily Career Feed

`.github/workflows/daily-feed.yml`

- 유일한 자동 실행 workflow
- 매일 `00:03 UTC`, 즉 `09:03 Asia/Seoul` 실행 요청
- 일찍 시작되면 내부 대기 후 `09:07`부터 Daily Overview와 카테고리별 상세 전송
- `OPENAI_API_KEY` 불필요
- Codex Action과 live web search를 사용하지 않음
- 후보와 브리핑을 artifact로 업로드

### Manual AI Light Brief

`.github/workflows/ai-brief-manual.yml`

- `workflow_dispatch` 전용
- 후보 JSON을 최대 5개씩만 Codex에 전달
- `OPENAI_API_KEY` 필요
- `--search` 미사용
- 저비용 mini 계열 모델과 low effort 설정

### Manual AI Search Brief

`.github/workflows/daily-news.yml`

- 기존 live web search 기반 workflow를 수동 전용 고급 모드로 보존
- 자동 schedule 없음
- `OPENAI_API_KEY` 필요
- `--search` 사용
- 비용이 커질 수 있으므로 특별한 경우에만 실행

### Daily Korea Premium Brief

`.github/workflows/kr-premium-brief.yml`

- `KR_PREMIUM_MODE` 전용 workflow
- 매일 `00:15 UTC`, 즉 `09:15 Asia/Seoul` 실행 요청
- `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` 필요
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`은 선택 사항
- `gpt-5.4-mini`, low effort, 제한적 live web search 사용
- 통합 Markdown 1개를 생성하고 Discord Webhook 1개로 전송

### KR Premium Candidate Collection

`scripts/collect-kr-feeds.py`

- 한국 AI 뉴스, 백엔드/개발자 기술 뉴스, 보안 알림, 커리어 이벤트 후보 pool 생성
- Naver News Search API는 JSON 응답, `sort=date`, query당 `display <= 20`만 사용
- RSS/Atom은 `configs/kr-sources.json`에 명시된 공개 RSS만 사용
- 기사 전문은 저장하지 않고 제목, URL, 출처, 발행시각, 검색 snippet만 저장
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`이 있으면 Naver News Search API 사용
- Naver Secret이 없으면 warning 후 RSS/공식 URL 후보만 수집
- `--dry-run`은 Secret과 네트워크 호출 없이 빈 스키마 JSON을 생성

## 비용 정책 요약

`FREE_MODE`는 OpenAI API를 사용하지 않으며, `KR_PREMIUM_MODE`부터 OpenAI 비용이 발생합니다.

| 운영 방식 | 월 예상 비용 | 비고 |
| --- | ---: | --- |
| `FREE_MODE` | $0 | RSS/Atom 기반, OpenAI API 불필요 |
| `KR_PREMIUM_MODE` 기본 | 약 $10~20 | 하루 1회 통합 브리핑, `gpt-5.4-mini` 기준 |
| `KR_PREMIUM_MODE` 고품질/검색량 증가 | $30~60 이상 가능 | live web search 호출, 출력 길이, 토큰 수 증가 시 |
| `AI_SEARCH_MODE` 반복 수동 실행 | 예측 어려움 | 실행 횟수와 검색량에 따라 비용 증가 |

비용 가드는 다음과 같습니다.

- KR premium schedule은 하루 1회만 둔다.
- 카테고리별 별도 AI workflow를 만들지 않는다.
- 기본 모델은 `gpt-5.4-mini`로 둔다.
- 후보 수와 출력 길이를 제한한다.
- OpenAI Billing monthly budget 설정을 권장한다.
- `workflow_dispatch`를 같은 날 여러 번 실행하지 않는다.

## 로컬 검증

Secret 없이 파일 구조, Python 문법, 무료 브리핑 렌더링, 전송 dry-run을 확인할 수 있습니다.

```bash
./scripts/validate.sh
```

KR_PREMIUM_MODE 후보 JSON 스키마만 확인하려면 다음을 실행합니다.

```bash
python3 scripts/collect-kr-feeds.py --dry-run
```

실제 Discord 전송은 명시적으로 실행할 때만 수행합니다.

```bash
python3 scripts/send-category-briefs.py
```

## 디렉터리 구조

```text
repository-root/
├─ .github/
│  ├─ codex/prompts/
│  │  ├─ compact-brief.md
│  │  └─ daily-news.md
│  └─ workflows/
│     ├─ ai-brief-manual.yml
│     ├─ daily-feed.yml
│     └─ daily-news.yml
├─ configs/
│  ├─ channels.json
│  ├─ kr-sources.json
│  └─ sources.json
├─ docs/
│  ├─ channels.md
│  ├─ cost-policy.md
│  └─ operations.md
├─ refs/categories/
├─ reports/
│  ├─ briefs/
│  └─ candidates/
└─ scripts/
   ├─ collect-kr-feeds.py
   └─ ...
```

## 운영 정책

- `reports/` 산출물은 기본적으로 저장소에 커밋하지 않는다.
- 원본 URL을 반드시 보존한다.
- 긴 요약보다 원문 링크 접근성을 우선한다.
- GitHub Actions workflow는 기본적으로 `FREE_MODE`를 사용한다.
- AI 사용은 수동 보조 기능으로 제한한다.
- KR_PREMIUM_MODE도 먼저 구조화된 후보 JSON을 만든 뒤 AI 정제에 넘긴다.
- 기사 전문, Secret 값, Webhook URL은 저장소와 로그에 남기지 않는다.
