# 운영 가이드

이 문서는 Career Feed를 GitHub Actions에서 실행하고 Discord Webhook으로 브리핑을 전송하기 위한 운영 기준을 정리한다.

## GitHub Secrets 설정

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에서 다음 Secrets를 등록한다. `FREE_MODE` MVP 운영에는 enabled 채널의 Webhook Secret만 필수다.

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

주의 사항:

- Secret 값은 코드, 문서 예시, 커밋 로그에 남기지 않는다.
- 로컬 테스트가 필요하면 `.env` 같은 커밋되지 않는 파일이나 셸 환경변수를 사용한다.
- Webhook URL은 토큰과 같은 민감 정보로 취급한다.

## MVP 운영 범위

현재 `FREE_MODE` MVP 운영 경로는 GitHub Actions, RSS/Atom 수집, Markdown 생성, Discord Webhook 전송이다. `app/`와 `infra/`는 이 경로에서 사용하지 않으며, 서버 또는 인프라 확장을 진행할 때 재검토한다.

## Workflow 실행 방식

### Daily Career Feed

기본 일일 workflow는 `.github/workflows/daily-feed.yml`에 정의되어 있다.

- Workflow 이름: `Daily Career Feed`
- 예약 실행 요청: 매일 `09:03 Asia/Seoul`
- GitHub Actions cron: `3 0 * * *`
- 수동 실행: `workflow_dispatch`
- OpenAI API 사용: 없음

실행 순서는 다음과 같다.

1. RSS/Atom 후보 수집
2. `reports/candidates/{category}.json` 생성
3. 무료 Markdown 브리핑 렌더링
4. Daily Overview 렌더링
5. 09:07 KST부터 Daily Overview와 카테고리별 Webhook 순차 전송
6. 후보와 브리핑 artifact 업로드

## 시간 정책

Daily Career Feed의 시간은 정확 보장이 아니라 목표 시각으로 운영한다. GitHub Actions schedule은 GitHub 인프라 상태에 따라 지연되거나 누락될 수 있다.

- GitHub Actions cron은 UTC 기준이며 `3 0 * * *`는 09:03 KST 실행 요청이다.
- workflow가 목표 전송 시각보다 일찍 시작되면 `scripts/send-category-briefs.py`가 09:07 KST까지 대기한다.
- workflow가 목표 전송 시각보다 늦게 시작되면 대기하지 않고 즉시 전송한다.
- 예정 전송 시각보다 5분 이상 늦으면 Discord 메시지에 지연 알림 문구를 붙인다.

목표 전송 시각은 다음과 같다.

| 메시지 | 목표 시각 |
| --- | --- |
| Daily Overview | 09:07 KST |
| AI News | 09:08 KST |
| Backend News | 09:09 KST |
| Security Alerts | 09:10 KST |

전송 단계 로그에는 카테고리, 목표 KST 시각, 현재 KST 시각, dry-run 여부가 남는다. 더 정확한 실행 시각이 필요하면 GitHub Actions schedule만으로는 부족하며, 외부 scheduler가 `repository_dispatch` 또는 `workflow_dispatch`를 호출하는 구조를 별도로 검토한다.

### 수동 실행 전 체크리스트

1. 변경 사항이 `main` 브랜치에 push되어 있는지 확인한다.
2. GitHub Actions에 MVP 필수 Secrets 4개가 등록되어 있는지 확인한다.
3. `.github/workflows/daily-feed.yml`의 workflow 이름이 `Daily Career Feed`인지 확인한다.
4. workflow에 `workflow_dispatch`가 있는지 확인한다.
5. workflow가 `OPENAI_API_KEY` 없이 실행되는지 확인한다.
6. 로컬에서 `./scripts/validate.sh`가 통과했는지 확인한다.

### GitHub Actions 수동 실행 방법

1. GitHub 저장소의 `Actions` 탭으로 이동한다.
2. 왼쪽 workflow 목록에서 `Daily Career Feed`를 선택한다.
3. `Run workflow`를 선택한다.
4. branch를 `main`으로 선택한다.
5. 실행을 시작하고 완료 상태가 성공인지 확인한다.

### 수동 실행 후 확인 체크리스트

1. workflow 실행 로그에서 후보 수집, 브리핑 렌더링, Daily Overview 렌더링, Discord 전송 단계가 성공했는지 확인한다.
2. artifact를 다운로드한다.
3. `reports/candidates/*.json`이 포함되어 있는지 확인한다.
4. `reports/briefs/*.md`가 포함되어 있는지 확인한다.
5. Discord에 Daily Overview 메시지가 먼저 도착했는지 확인한다.
6. Discord에 AI News, Backend News, Security Alerts 메시지가 순서대로 도착했는지 확인한다.

### Manual AI Light Brief

`.github/workflows/ai-brief-manual.yml`은 수동 실행 전용이다.

- live web search를 사용하지 않는다.
- `OPENAI_API_KEY`가 필요하다.
- 후보 JSON은 카테고리당 최대 5개만 전달한다.
- summary는 항목당 160자 이하로 제한한다.
- runtime prompt가 8000자 이상이면 실패한다.

### Manual AI Search Brief

`.github/workflows/daily-news.yml`은 기존 Codex live web search 기반 workflow를 수동 고급 모드로 보존한 것이다.

- 자동 schedule이 없다.
- `OPENAI_API_KEY`가 필요하다.
- live web search를 사용할 수 있다.
- 비용이 커질 수 있으므로 특별한 이슈를 확인해야 할 때만 실행한다.
- 결과는 Discord 전송 전에 artifact로 저장한다.

## 매일 메시지가 오지 않았을 때 확인 순서

1. GitHub Actions의 `Daily Career Feed` 실행 이력이 있는지 확인한다.
2. schedule 이벤트가 지연되거나 누락되지 않았는지 확인한다.
3. `DISCORD_WEBHOOK_DAILY_OVERVIEW`와 enabled 카테고리의 Webhook Secret이 등록되어 있는지 확인한다.
4. Discord Webhook이 삭제되거나 대상 채널 권한이 변경되지 않았는지 확인한다.
5. RSS 수집 단계에서 네트워크 오류가 반복되는지 확인한다.
6. `reports/candidates/*.json`과 `reports/briefs/*.md` artifact가 생성되었는지 확인한다.
7. `scripts/send-category-briefs.py` 로그의 성공/실패 카테고리 요약을 확인한다.

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

1. Secret 누락: enabled 채널의 Discord Webhook Secret이 등록되어 있는지 확인한다.
2. Secret 이름 불일치: `configs/channels.json`의 `webhook_env` 값이 GitHub Secrets 이름과 일치하는지 확인한다.
3. RSS 접근 실패: `configs/sources.json`의 RSS/Atom URL이 접근 가능한지 확인한다.
4. 후보 파일 미생성: `reports/candidates/{category}.json`이 생성되었는지 확인한다.
5. brief 파일 미생성: `reports/briefs/{category}.md`가 생성되고 비어 있지 않은지 확인한다.
6. Discord 4xx/5xx: Webhook URL이 삭제되었거나 채널 권한이 변경되지 않았는지 확인한다.
7. GitHub schedule 지연: schedule 이벤트가 지연되거나 누락되지 않았는지 확인한다.
8. AI workflow 실패: runtime prompt 크기 제한에 걸렸는지 확인한다.
9. `AI_SEARCH_MODE`: live web search 비용이 발생할 수 있음을 확인한다.
