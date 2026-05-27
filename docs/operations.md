# 운영 가이드

이 문서는 Career Feed를 GitHub Actions에서 실행하고 Discord Webhook으로 브리핑을 전송하기 위한 운영 기준을 정리한다.

## GitHub Secrets 설정

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에서 다음 Secrets를 등록한다. 기본 오전 알림은 `KR_PREMIUM_MODE`이며, 무료 RSS Webhook Secret은 기본 운영 필수가 아니다.

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

| Secret | 필요한 경우 |
| --- | --- |
| `DISCORD_WEBHOOK_DAILY_OVERVIEW` | 수동 무료 RSS Daily Overview 전송이 필요할 때 |
| `DISCORD_WEBHOOK_AI_NEWS` | 수동 무료 RSS AI News 전송이 필요할 때 |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | 수동 무료 RSS Backend News 전송이 필요할 때 |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | 수동 무료 RSS Security Alerts 전송이 필요할 때 |

주의 사항:

- Secret 값은 코드, 문서 예시, 커밋 로그에 남기지 않는다.
- 로컬 테스트가 필요하면 `.env` 같은 커밋되지 않는 파일이나 셸 환경변수를 사용한다.
- Webhook URL은 토큰과 같은 민감 정보로 취급한다.

## MVP 운영 범위

현재 기본 오전 알림 경로는 GitHub Actions, 한국 후보 수집, AI 편집, 품질 검증, 단일 Discord Webhook 전송이다. `FREE_MODE`는 수동 백업 경로로만 유지한다. `app/`와 `infra/`는 이 경로에서 사용하지 않으며, 서버 또는 인프라 확장을 진행할 때 재검토한다.

## Workflow 실행 방식

### Daily Korea Premium Brief

기본 일일 workflow는 `.github/workflows/kr-premium-brief.yml`에 정의되어 있다.

- Workflow 이름: `Daily Korea Premium Brief`
- 예약 실행 요청: 매일 `09:15 Asia/Seoul`
- GitHub Actions cron: `15 0 * * *`
- 수동 실행: `workflow_dispatch`
- 필수 Secrets: `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`
- 권장 Secrets: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`

실행 순서는 다음과 같다.

1. 한국 후보 수집
2. `reports/candidates/kr-*.json` 생성
3. KR Premium AI 편집 프롬프트 생성
4. Codex Action으로 `reports/briefs/kr-premium-daily.md` 생성
5. 품질 검증
6. `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` 하나로 Discord 전송
7. 후보와 브리핑 artifact 업로드

### Manual Free RSS Career Feed

무료 RSS 백업 workflow는 `.github/workflows/daily-feed.yml`에 정의되어 있다.

- Workflow 이름: `Manual Free RSS Career Feed`
- 예약 실행 없음
- 수동 실행: `workflow_dispatch`
- OpenAI API 사용: 없음
- legacy/manual free RSS Webhook Secret이 있을 때만 Discord 전송 가능

실행 순서는 다음과 같다.

1. RSS/Atom 후보 수집
2. `reports/candidates/{category}.json` 생성
3. 무료 Markdown 브리핑 렌더링
4. Daily Overview 렌더링
5. Daily Overview와 legacy 무료 카테고리별 Webhook 순차 전송
6. 후보와 브리핑 artifact 업로드

### KR_PREMIUM_MODE 후보 수집

`KR_PREMIUM_MODE`는 기본 오전 알림이며, 기존 무료 RSS workflow는 삭제하지 않고 수동 백업으로 유지한다. 한국 기준 고품질 브리핑을 만들기 위한 별도 후보 pool을 먼저 생성한다.

- 스크립트: `scripts/collect-kr-feeds.py`
- 설정: `configs/kr-sources.json`
- 선택 환경변수: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`
- Naver News Search API는 JSON 응답, `sort=date`, query당 `display <= 20`만 사용한다.
- Naver Secret이 없으면 warning을 출력하고 RSS/공식 URL 후보만 수집한다.
- RSS/Atom은 공개 RSS만 사용하고, 안정적이지 않은 공식 페이지는 config의 `reference_pages`에만 보관한다.
- 기사 전문은 저장하지 않고 제목, URL, 출처, 발행시각, 검색 snippet만 저장한다.

출력 파일은 다음과 같다.

| 카테고리 | 출력 파일 |
| --- | --- |
| 한국 AI 뉴스 | `reports/candidates/kr-ai-news.json` |
| 한국 백엔드/개발자 기술 뉴스 | `reports/candidates/kr-backend-news.json` |
| 한국 보안/취약점 알림 | `reports/candidates/kr-security-alerts.json` |
| 국내 커리어 이벤트 | `reports/candidates/kr-career-events.json` |

Secret 없이 스키마만 검증하려면 dry-run을 실행한다.

```bash
python3 scripts/collect-kr-feeds.py --dry-run
```

실제 후보 수집은 Naver API Secret을 셸 환경변수나 GitHub Actions Secrets로 주입한 뒤 실행한다.

```bash
python3 scripts/collect-kr-feeds.py
```

### KR_PREMIUM_MODE 비용 운영 기준

`KR_PREMIUM_MODE`는 OpenAI API 비용이 발생한다. 비용은 검색 호출 수, 토큰 수, 모델 설정, 수동 재실행 횟수에 따라 달라진다.

| 운영 방식 | 월 예상 비용 | 기준 |
| --- | ---: | --- |
| `FREE_MODE` | $0 | OpenAI API 미사용 |
| `KR_PREMIUM_MODE` 기본 | 약 $10~20 | 하루 1회 통합 브리핑, `gpt-5.4-mini` 기준 |
| `KR_PREMIUM_MODE` 고품질/검색량 증가 | $30~60 이상 가능 | live web search와 출력 길이 증가 |

운영 가드는 다음과 같다.

- 하루 1회 schedule만 둔다.
- 카테고리별 별도 AI workflow를 만들지 않는다.
- 기본 모델은 `gpt-5.4-mini`로 둔다.
- 후보 수와 출력 길이를 제한한다.
- OpenAI Billing monthly budget 설정을 권장한다.
- 같은 날 `workflow_dispatch`를 여러 번 실행하지 않는다.

### KR_PREMIUM_MODE 품질 검증

AI가 생성한 `reports/briefs/kr-premium-daily.md`는 Discord 전송 전에 `scripts/validate-kr-premium-brief.py`로 검증한다.

검증 기준은 다음과 같다.

- 파일이 존재하고 비어 있지 않아야 한다.
- `기준시각`과 KST 시각이 있어야 한다.
- 한국 AI 뉴스, 한국 백엔드/개발자 기술 뉴스, 한국 보안/취약점 알림, 국내 인턴십/해커톤/공모전/경진대회 섹션이 모두 있어야 한다.
- 각 섹션에는 최소 1개 항목이 있거나 "오늘 확인된 주요 항목 없음" 계열 문구가 있어야 한다.
- 전체 링크가 최소 4개 이상이어야 한다.
- 일반적인 "왜 봐야 함" placeholder 문구가 2회 이상 나오면 실패한다.
- 각 항목은 무슨 일, 왜 봐야 함, 내 액션, 출처, 시각, 신뢰도, 링크 중 최소 4개 이상을 포함해야 한다.
- 커리어 이벤트 항목은 유형, 대상, 마감 중 최소 2개 이상을 포함해야 한다.
- "링크 없음"은 실패로 처리하고, "출처 없음"은 warning으로 표시한다.

로컬에서 다음 명령으로 검증할 수 있다.

```bash
python3 scripts/validate-kr-premium-brief.py reports/briefs/kr-premium-daily.md
```

## 시간 정책

Daily Korea Premium Brief의 시간은 정확 보장이 아니라 목표 시각으로 운영한다. GitHub Actions schedule은 GitHub 인프라 상태에 따라 지연되거나 누락될 수 있다.

- GitHub Actions cron은 UTC 기준이며 `15 0 * * *`는 09:15 KST 실행 요청이다.
- 기본 오전 알림은 `Daily Korea Premium Brief` 하나만 사용한다.
- 무료 RSS workflow에는 schedule이 없다.

목표 전송 시각은 다음과 같다.

| 메시지 | 목표 시각 |
| --- | --- |
| KR Premium 통합 브리핑 | 09:15 KST |

더 정확한 실행 시각이 필요하면 GitHub Actions schedule만으로는 부족하며, 외부 scheduler가 `repository_dispatch` 또는 `workflow_dispatch`를 호출하는 구조를 별도로 검토한다.

### 수동 실행 전 체크리스트

1. 변경 사항이 `main` 브랜치에 push되어 있는지 확인한다.
2. GitHub Actions에 `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`가 등록되어 있는지 확인한다.
3. 한국 뉴스 품질을 위해 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`이 등록되어 있는지 확인한다.
4. `.github/workflows/kr-premium-brief.yml`의 workflow 이름이 `Daily Korea Premium Brief`인지 확인한다.
5. `.github/workflows/daily-feed.yml`에 `schedule:`이 없는지 확인한다.
6. 로컬에서 `./scripts/validate.sh`가 통과했는지 확인한다.
6. 로컬에서 `./scripts/validate.sh`가 통과했는지 확인한다.

### GitHub Actions 수동 실행 방법

1. GitHub 저장소의 `Actions` 탭으로 이동한다.
2. 왼쪽 workflow 목록에서 `Daily Korea Premium Brief`를 선택한다.
3. `Run workflow`를 선택한다.
4. branch를 `main`으로 선택한다.
5. 실행을 시작하고 완료 상태가 성공인지 확인한다.

### 수동 실행 후 확인 체크리스트

1. workflow 실행 로그에서 한국 후보 수집, AI 브리핑 생성, 품질 검증, Discord 전송 단계가 성공했는지 확인한다.
2. artifact를 다운로드한다.
3. `reports/candidates/kr-*.json`이 포함되어 있는지 확인한다.
4. `reports/briefs/kr-premium-daily.md`가 포함되어 있는지 확인한다.
5. Discord에 KR Premium 통합 브리핑이 도착했는지 확인한다.

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

1. GitHub Actions의 `Daily Korea Premium Brief` 실행 이력이 있는지 확인한다.
2. schedule 이벤트가 지연되거나 누락되지 않았는지 확인한다.
3. `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`가 등록되어 있는지 확인한다.
4. `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`이 등록되어 있는지 확인한다.
5. Discord Webhook이 삭제되거나 대상 채널 권한이 변경되지 않았는지 확인한다.
6. 후보 수집 또는 Codex Action 단계에서 오류가 반복되는지 확인한다.
7. `reports/candidates/kr-*.json`과 `reports/briefs/kr-premium-daily.md` artifact가 생성되었는지 확인한다.

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

Secret 없이 기본 파일 구조, Python 문법, KR Premium 후보 스키마, 수동 무료 RSS dry-run을 확인하려면 다음 명령을 실행한다.

```bash
./scripts/validate.sh
```

KR_PREMIUM_MODE 후보 수집 스키마만 확인하려면 다음 명령을 실행한다.

```bash
python3 scripts/collect-kr-feeds.py --dry-run
```

수동 무료 RSS 전송 테스트가 필요하면 legacy Webhook 환경변수를 설정한 뒤 명시적으로 실행한다.

```bash
python3 scripts/send-category-briefs.py
```

기존 단일 파일 전송 스크립트도 유지한다.

```bash
DISCORD_WEBHOOK_URL="..." python3 scripts/send-discord.py reports/sample-daily-news.md
```

## Artifact 확인 방법

기본 일일 workflow는 다음 산출물을 artifact로 업로드한다.

- `reports/candidates/kr-*.json`
- `reports/briefs/kr-premium-daily.md`

저장 정책은 다음과 같다.

- `reports/.gitkeep`만 저장소에 유지한다.
- 실행 중 생성된 후보 JSON과 Markdown 브리핑은 기본 커밋 대상이 아니다.
- 장기 보관이 필요해지면 별도의 archive workflow로 분리한다.

## Discord 메시지 포맷

Discord에서 브리핑 본문을 먼저 읽을 수 있도록 링크와 embed preview를 제한한다.

- `scripts/send-discord.py`는 Discord webhook payload에 `SUPPRESS_EMBEDS` flag를 설정한다.
- Daily Overview의 대표 링크는 카테고리별 제목 링크 1개만 표시한다.
- KR Premium Brief의 항목 링크 텍스트는 `[원문 보기](URL)` 형식을 기본으로 한다.
- 한 항목에서 같은 URL을 본문과 별도 원본 보기 섹션에 중복해서 쓰지 않는다.
- Markdown 표는 사용하지 않는다.

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
10. `KR_PREMIUM_MODE`: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 누락 또는 Naver API 인증 실패 여부를 확인한다.

## GitHub Secrets 정리

`Daily Korea Premium Brief`가 기본 오전 알림으로 동작하고 `Manual Free RSS Career Feed`의 schedule 제거가 배포된 뒤에는 기존 무료 RSS Webhook Secret을 삭제할 수 있다.

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

주의: `daily-feed.yml`의 schedule 제거가 배포되기 전에는 기존 무료 Webhook Secret을 삭제하지 않는다. 삭제하면 기존 무료 workflow가 매일 실패할 수 있다.
