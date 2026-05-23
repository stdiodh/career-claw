# 운영 가이드

이 문서는 Career Feed를 GitHub Actions에서 실행하고 Discord Webhook으로 브리핑을 전송하기 위한 운영 기준을 정리한다.

## GitHub Secrets 설정

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에서 다음 Secrets를 등록한다.

| Secret | 설명 |
| --- | --- |
| `DISCORD_WEBHOOK_AI_NEWS` | AI News 채널 Webhook URL |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | Backend News 채널 Webhook URL |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | Security Alerts 채널 Webhook URL |
| `DISCORD_WEBHOOK_BACKEND_TECH` | Backend Tech Radar 채널 Webhook URL |
| `DISCORD_WEBHOOK_JOB_FEED` | Job Feed 채널 Webhook URL |
| `OPENAI_API_KEY` | 선택형 AI workflow에서만 사용하는 OpenAI API 키 |

주의 사항:

- Secret 값은 코드, 문서 예시, 커밋 로그에 남기지 않는다.
- 로컬 테스트가 필요하면 `.env` 같은 커밋되지 않는 파일이나 셸 환경변수를 사용한다.
- Webhook URL은 토큰과 같은 민감 정보로 취급한다.

## Workflow 실행 방식

### Daily Career Feed

기본 일일 workflow는 `.github/workflows/daily-feed.yml`에 정의되어 있다.

- Workflow 이름: `Daily Career Feed`
- 예약 실행: 매일 `09:03 Asia/Seoul`
- GitHub Actions cron: `3 0 * * *`
- 수동 실행: `workflow_dispatch`
- OpenAI API 사용: 없음

실행 순서는 다음과 같다.

1. RSS/Atom 후보 수집
2. `reports/candidates/{category}.json` 생성
3. 무료 Markdown 브리핑 렌더링
4. 09:07 KST부터 카테고리별 Webhook 순차 전송
5. 후보와 브리핑 artifact 업로드

### Manual AI Light Brief

`.github/workflows/ai-brief-manual.yml`은 수동 실행 전용이다.

- live web search를 사용하지 않는다.
- `OPENAI_API_KEY`가 필요하다.
- 후보 JSON은 카테고리당 최대 5개만 전달한다.
- summary는 항목당 240자 이하로 제한한다.
- runtime prompt가 8000자 이상이면 실패한다.

### Manual AI Search Brief

`.github/workflows/daily-news.yml`은 기존 Codex live web search 기반 workflow를 수동 고급 모드로 보존한 것이다.

- 자동 schedule이 없다.
- `OPENAI_API_KEY`가 필요하다.
- 비용이 커질 수 있으므로 특별한 이슈를 확인해야 할 때만 실행한다.
- 결과는 Discord 전송 전에 artifact로 저장한다.

## 소스 추가 방법

RSS/Atom 소스는 `configs/sources.json`에 추가한다.

```json
{
  "category": "backend-news",
  "name": "Spring Blog",
  "url": "https://spring.io/blog.atom",
  "type": "atom"
}
```

기준:

- 공식 블로그, 공식 릴리스 노트, 공식 보안 공지를 우선한다.
- URL 접근 가능성을 확인한 뒤 추가한다.
- 확실하지 않은 URL은 TODO로 남기고 실제 수집 대상에 넣지 않는다.
- 1차 MVP에서 실제 수집은 `rss`, `atom`만 지원한다.
- `webpage`, `github-releases`는 추후 확장용으로만 둔다.

## 로컬 검증 방법

Secret 없이 기본 파일 구조, Python 문법, 무료 브리핑 렌더링, 전송 dry-run을 확인하려면 다음 명령을 실행한다.

```bash
./scripts/validate.sh
```

실제 Discord 전송은 자동으로 실행하지 않는다. 전송 테스트가 필요하면 대상 Webhook 환경변수를 설정한 뒤 명시적으로 실행한다.

```bash
python3 scripts/send-category-briefs.py
```

기존 단일 파일 전송 스크립트도 유지한다.

```bash
DISCORD_WEBHOOK_URL="..." python3 scripts/send-discord.py reports/sample-daily-news.md
```

## Artifact 확인 방법

일일 workflow는 다음 산출물을 artifact로 업로드한다.

- `reports/candidates/*.json`
- `reports/briefs/*.md`

저장 정책은 다음과 같다.

- `reports/.gitkeep`만 저장소에 유지한다.
- 실행 중 생성된 후보 JSON과 Markdown 브리핑은 기본 커밋 대상이 아니다.
- 장기 보관이 필요해지면 별도의 archive workflow로 분리한다.

## 실패 시 확인할 것

- enabled 채널의 Discord Webhook Secret이 등록되어 있는지 확인한다.
- `configs/channels.json`의 `webhook_env` 값이 Secret 이름과 일치하는지 확인한다.
- `configs/sources.json`의 RSS/Atom URL이 접근 가능한지 확인한다.
- `reports/candidates/{category}.json`이 생성되었는지 확인한다.
- `reports/briefs/{category}.md`가 비어 있지 않은지 확인한다.
- AI workflow 실패 시 runtime prompt 크기 제한에 걸렸는지 확인한다.
- `AI_SEARCH_MODE`는 live web search 비용이 발생할 수 있음을 확인한다.
