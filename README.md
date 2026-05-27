# Career Feed

Career Feed는 AI와 백엔드 개발자에게 필요한 최신 기술 뉴스, 보안 알림, 채용공고 후보를 Discord로 전달하는 자동 브리핑 프로젝트입니다.

기본 오전 알림은 한국 중심 고품질 통합 브리핑인 `KR_PREMIUM_MODE`입니다. 무료 RSS/Atom 기반 `FREE_MODE`는 삭제하지 않고 수동 백업 workflow로만 유지합니다.

## 프로젝트 이름 정책

- 제품명과 문서명은 `Career Feed`로 통일합니다.
- 저장소 이름이나 로컬 경로명은 환경에 따라 다를 수 있으며, 제품명을 의미하지 않습니다.
- 현재 기본 운영은 GitHub Actions, 한국 후보 수집, AI 편집, Markdown 검증, 단일 Discord Webhook 전송으로 구성합니다.

## 운영 모드

| 모드 | 용도 | 기본 실행 여부 |
| --- | --- | --- |
| `FREE_MODE` | 무료 RSS/Atom 수집, 규칙 기반 요약, 카테고리별 Discord 전송 | 수동 백업 |
| `KR_PREMIUM_MODE` | 한국 중심 AI 검색/선별 통합 브리핑 | 매일 자동, OpenAI 비용 발생 |
| `AI_LIGHT_MODE` | 수집된 후보 JSON만 Codex가 짧게 정제, live web search 없음 | 수동 실행 |
| `AI_SEARCH_MODE` | Codex live web search 기반 수동 고급 브리핑 | 수동 실행 |

기본 매일 오전 알림은 `KR_PREMIUM_MODE`가 담당합니다. `FREE_MODE`는 `Manual Free RSS Career Feed`에서 수동 백업으로만 실행하며, `OPENAI_API_KEY` 없이 동작합니다.

## 핵심 기능

- 매일 `09:15 Asia/Seoul` 목표로 KR Premium 통합 브리핑 전송
- RSS/Atom 기반 후보 URL 수집
- Naver News Search API 기반 한국 뉴스 후보 수집
- 원본 URL 보존
- 후보가 없어도 "오늘 확인된 주요 항목이 없습니다." 메시지 생성
- Discord Webhook은 기본 운영에서 `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` 하나만 사용
- 선택형 AI 정제 workflow 제공
- 무료 RSS workflow와 live web search workflow는 수동 백업/고급 모드로만 보존

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
reports/candidates/kr-*.json
        |
        v
Codex KR premium editor
        |
        v
reports/briefs/kr-premium-daily.md
        |
        v
DISCORD_WEBHOOK_KR_PREMIUM_BRIEF
```

무료 RSS 백업 workflow는 기존 `configs/sources.json`, `configs/channels.json`, `refs/categories/*.md`를 계속 사용합니다. `AI_LIGHT_MODE`에서는 `--search`를 사용하지 않습니다.

## 필요한 Secrets

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에 다음 Secrets를 등록합니다. 기본 오전 알림에는 KR Premium Secrets만 필요합니다.

### 기본 운영 필수 Secrets

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | 한국 중심 AI 브리핑 생성에 사용하는 OpenAI API Key |
| `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` | KR Premium 통합 브리핑을 전송할 Discord Webhook URL |

### 한국 뉴스 품질 향상 권장 Secrets

| Secret | 필요한 경우 |
| --- | --- |
| `NAVER_CLIENT_ID` | `KR_PREMIUM_MODE` 후보 수집에서 Naver News Search API를 사용할 때 |
| `NAVER_CLIENT_SECRET` | `KR_PREMIUM_MODE` 후보 수집에서 Naver News Search API를 사용할 때 |

### Legacy/manual free RSS용 선택 Secrets

| Secret | 설명 |
| --- | --- |
| `DISCORD_WEBHOOK_DAILY_OVERVIEW` | 수동 무료 RSS Daily Overview 전송이 필요할 때 |
| `DISCORD_WEBHOOK_AI_NEWS` | 수동 무료 RSS AI News 전송이 필요할 때 |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | 수동 무료 RSS Backend News 전송이 필요할 때 |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | 수동 무료 RSS Security Alerts 전송이 필요할 때 |

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## Workflow

### Manual Free RSS Career Feed

`.github/workflows/daily-feed.yml`

- 수동 백업 workflow
- 자동 schedule 없음
- 기존 해외 RSS/Atom 중심 무료 브리핑을 필요할 때만 실행
- legacy/manual free RSS용 Webhook Secret이 있을 때 전송 가능
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
│  │  ├─ daily-news.md
│  │  └─ kr-premium-brief.md
│  └─ workflows/
│     ├─ ai-brief-manual.yml
│     ├─ daily-feed.yml
│     ├─ daily-news.yml
│     └─ kr-premium-brief.yml
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
- GitHub Actions 기본 오전 알림은 `KR_PREMIUM_MODE`를 사용한다.
- 무료 RSS workflow는 수동 백업으로만 사용한다.
- 기존 무료 RSS Webhook Secret은 기본 운영 필수가 아니다.
- KR_PREMIUM_MODE도 먼저 구조화된 후보 JSON을 만든 뒤 AI 정제에 넘긴다.
- 기사 전문, Secret 값, Webhook URL은 저장소와 로그에 남기지 않는다.

## GitHub Secrets 정리

`Daily Korea Premium Brief`가 기본 오전 알림으로 동작하고 `Manual Free RSS Career Feed`의 schedule 제거가 배포된 뒤에는 기존 무료 RSS Webhook Secret을 삭제할 수 있습니다.

삭제해도 되는 legacy/manual free RSS Secrets:

```text
DISCORD_WEBHOOK_DAILY_OVERVIEW
DISCORD_WEBHOOK_AI_NEWS
DISCORD_WEBHOOK_BACKEND_NEWS
DISCORD_WEBHOOK_SECURITY_ALERTS
DISCORD_WEBHOOK_BACKEND_TECH
DISCORD_WEBHOOK_JOB_FEED
```

남길 Secrets:

```text
OPENAI_API_KEY
DISCORD_WEBHOOK_KR_PREMIUM_BRIEF
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
```

주의: `daily-feed.yml`의 schedule 제거가 배포되기 전에는 기존 무료 Webhook Secret을 삭제하지 않습니다. 삭제하면 기존 무료 workflow가 매일 실패할 수 있습니다.
