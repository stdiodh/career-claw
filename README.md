# Career Feed

Career Feed는 AI와 백엔드 개발자에게 필요한 최신 기술 뉴스, 보안 알림, 채용공고 후보를 Discord로 전달하는 자동 브리핑 프로젝트입니다.

기본 운영은 OpenAI API를 사용하지 않는 `FREE_MODE`입니다. 코드가 RSS/Atom/공식 URL에서 후보를 수집하고, 규칙 기반으로 짧은 Markdown 브리핑을 만든 뒤 카테고리별 Discord Webhook으로 전송합니다. AI는 필요할 때만 수동으로 짧은 정제에 사용합니다.

## 운영 모드

| 모드 | 용도 | 기본 실행 여부 |
| --- | --- | --- |
| `FREE_MODE` | RSS 수집, 규칙 기반 요약, 카테고리별 Discord 전송 | 매일 실행 |
| `AI_LIGHT_MODE` | 수집된 후보 JSON을 Codex가 짧게 정제, live web search 없음 | 수동 실행 |
| `AI_SEARCH_MODE` | Codex live web search 기반 고급 브리핑 | 수동 실행 |

매일 09:07 KST 알림은 `FREE_MODE`로 운영하며 `OPENAI_API_KEY`가 없어도 실행됩니다.

## 핵심 기능

- 매일 `09:03 Asia/Seoul` 후보 수집 시작, `09:07`부터 카테고리별 순차 전송
- RSS/Atom 기반 후보 URL 수집
- 원본 URL 보존
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

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에 다음 Secrets를 등록합니다.

| Secret | 설명 | 필수 범위 |
| --- | --- | --- |
| `DISCORD_WEBHOOK_AI_NEWS` | AI News 채널 Webhook URL | `ai-news` enabled |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | Backend News 채널 Webhook URL | `backend-news` enabled |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | Security Alerts 채널 Webhook URL | `security-alerts` enabled |
| `DISCORD_WEBHOOK_BACKEND_TECH` | Backend Tech Radar 채널 Webhook URL | 채널 활성화 또는 수동 전송 시 |
| `DISCORD_WEBHOOK_JOB_FEED` | Job Feed 채널 Webhook URL | 채널 활성화 또는 수동 전송 시 |
| `OPENAI_API_KEY` | 선택형 AI workflow 실행용 | `AI_LIGHT_MODE`, `AI_SEARCH_MODE` |

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## Workflow

### Daily Career Feed

`.github/workflows/daily-feed.yml`

- 매일 `00:03 UTC`, 즉 `09:03 Asia/Seoul` 실행
- `OPENAI_API_KEY` 불필요
- Codex Action과 live web search를 사용하지 않음
- 후보와 브리핑을 artifact로 업로드

### Manual AI Light Brief

`.github/workflows/ai-brief-manual.yml`

- `workflow_dispatch` 전용
- 후보 JSON을 최대 5개씩만 Codex에 전달
- `--search` 미사용
- 저비용 mini 계열 모델과 low effort 설정

### Manual AI Search Brief

`.github/workflows/daily-news.yml`

- 기존 live web search 기반 workflow를 수동 전용 고급 모드로 보존
- 자동 schedule 없음
- 비용이 커질 수 있으므로 특별한 경우에만 실행

## 로컬 검증

Secret 없이 파일 구조, Python 문법, 무료 브리핑 렌더링, 전송 dry-run을 확인할 수 있습니다.

```bash
./scripts/validate.sh
```

실제 Discord 전송은 명시적으로 실행할 때만 수행합니다.

```bash
python3 scripts/send-category-briefs.py
```

## 디렉터리 구조

```text
career-feed/
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
```

## 운영 정책

- `reports/` 산출물은 기본적으로 저장소에 커밋하지 않는다.
- 원본 URL을 반드시 보존한다.
- 긴 요약보다 원문 링크 접근성을 우선한다.
- GitHub Actions workflow는 기본적으로 `FREE_MODE`를 사용한다.
- AI 사용은 수동 보조 기능으로 제한한다.
