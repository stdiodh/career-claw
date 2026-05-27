# 비용 정책

Career Feed의 기본 오전 알림은 `KR_PREMIUM_MODE` 하나로 운영한다. OpenAI API 비용이 발생하므로 하루 1회 통합 브리핑, 제한된 후보 수, 품질 검증, 예산 알림을 비용 가드로 둔다. 무료 RSS/Atom 기반 `FREE_MODE`는 수동 백업으로만 유지한다.

## 운영 모드

| 모드 | 용도 | 실행 방식 | 비용 기준 |
| --- | --- | --- | --- |
| `FREE_MODE` | 무료 RSS/Atom 기반 백업 알림 | 수동 실행 전용 | OpenAI API 사용 안 함 |
| `KR_PREMIUM_MODE` | 한국 중심 AI 검색/선별 통합 브리핑 | 매일 자동 | OpenAI API 비용 발생 |
| `AI_LIGHT_MODE` | 후보 JSON만 짧게 정제 | 수동 실행 전용 | 낮은 비용, live web search 없음 |
| `AI_SEARCH_MODE` | 수동 고급 브리핑 | 수동 실행 전용 | 검색량에 따라 비용 증가 |

## 기본 정책

- 기본 오전 알림은 `KR_PREMIUM_MODE`로 운영한다.
- `FREE_MODE` workflow는 `OPENAI_API_KEY`를 요구하지 않는다.
- `Manual Free RSS Career Feed`에는 `OPENAI_API_KEY`를 추가하지 않는다.
- 무료 RSS Daily Overview는 수동 백업으로만 사용하며 AI 비용을 발생시키지 않는다.
- 후보 수집은 `configs/sources.json`에 등록된 RSS/Atom/공식 URL을 기준으로 한다.
- 브리핑은 원본 제목, 1줄 요약, 출처, 발행일, URL 중심으로 구성한다.
- 원문 확인이 필요한 항목은 내용을 추측하지 않고 "원문 확인 필요"라고 표시한다.

## KR_PREMIUM_MODE 제한

- 기존 무료 RSS workflow와 별도 경로로 운영한다.
- 후보 수집은 먼저 `scripts/collect-kr-feeds.py`로 구조화된 JSON을 만든다.
- Naver News Search API는 JSON 응답, `sort=date`, query당 `display <= 20`만 사용한다.
- 기사 전문을 저장하지 않고 제목, URL, 출처, 발행시각, 검색 snippet만 저장한다.
- OpenAI API 사용은 후보 JSON을 정제해 통합 Markdown 브리핑을 만들 때만 허용한다.
- 기본 모델은 `gpt-5.4-mini`를 우선 사용한다.
- 하루 1회 실행을 기본으로 하며, 수동 재실행은 장애 복구나 품질 확인 목적에 한정한다.
- 출력은 `reports/briefs/kr-premium-daily.md` 하나로 제한한다.
- 섹션은 한국 AI 뉴스, 한국 백엔드/개발자 기술 뉴스, 한국 보안/취약점 알림, 국내 커리어 이벤트 4개로 제한한다.
- 후보 입력은 섹션별 상위 후보만 전달하고, 출력 길이를 제한한다.
- live web search 과다 사용을 금지한다. 검색이 필요하면 후보 수집 레이어를 먼저 개선한다.
- OpenAI Billing monthly budget 설정을 권장한다.
- 예산 초과가 우려되면 KR premium workflow를 일시 중지하고 수동 실행으로 전환한다.

### KR_PREMIUM_MODE 월 예상 비용

실제 비용은 검색 호출 수, 입력/출력 토큰 수, 모델 설정, 같은 날 수동 재실행 횟수에 따라 달라진다.

| 운영 방식 | 월 예상 비용 | 기준 |
| --- | ---: | --- |
| `FREE_MODE` | $0 | OpenAI API 미사용 |
| `KR_PREMIUM_MODE` 기본 | 약 $10~20 | 하루 1회 통합 브리핑, `gpt-5.4-mini`, 제한적 live web search |
| `KR_PREMIUM_MODE` 고품질/검색량 증가 | $30~60 이상 가능 | 검색 호출 증가, 후보/출력 길이 증가, 검증 검색 증가 |
| `AI_SEARCH_MODE` 반복 실행 | 예측 어려움 | 수동 실행 횟수와 live web search 사용량에 비례 |

### KR_PREMIUM_MODE 비용 가드

- 하루 1회 schedule만 둔다.
- `workflow_dispatch`는 수동 테스트와 장애 복구에만 사용한다.
- 같은 날 `workflow_dispatch`를 여러 번 실행하지 않는다.
- 카테고리별 별도 AI workflow를 만들지 않는다.
- 실행당 OpenAI 호출은 통합 브리핑 생성 1회로 제한한다.
- 기본 모델은 `gpt-5.4-mini`, reasoning effort는 `low`로 둔다.
- 후보 수와 runtime prompt 크기를 제한한다.
- 출력 파일은 `reports/briefs/kr-premium-daily.md` 하나로 제한한다.
- 출력이 길어지면 warning 또는 실패로 처리한다.
- OpenAI Billing에서 monthly budget과 알림을 설정한다.

### 비용이 커지는 경우

- category별 workflow를 따로 돌릴 때
- live web search 호출이 많을 때
- full model로 바꿀 때
- 출력이 길 때
- 같은 날 `workflow_dispatch`를 여러 번 실행할 때
- 후보 JSON에 너무 많은 항목을 전달할 때

### KR_PREMIUM_MODE Secrets

필수:

- `OPENAI_API_KEY`
- `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`

한국 뉴스 품질 향상 권장:

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`

기본 운영에서 더 이상 필수가 아닌 legacy/manual free RSS Secrets:

- `DISCORD_WEBHOOK_DAILY_OVERVIEW`
- `DISCORD_WEBHOOK_AI_NEWS`
- `DISCORD_WEBHOOK_BACKEND_NEWS`
- `DISCORD_WEBHOOK_SECURITY_ALERTS`
- `DISCORD_WEBHOOK_BACKEND_TECH`
- `DISCORD_WEBHOOK_JOB_FEED`

## AI_LIGHT_MODE 제한

- live web search를 사용하지 않는다.
- `codex-args`에 `--search`를 넣지 않는다.
- 후보 JSON은 카테고리당 최대 5개만 전달한다.
- title은 140자 이하, summary는 160자 이하로 제한한다.
- 카테고리 참조 문서는 500자 이하로 제한한다.
- runtime prompt가 8000자 이상이면 실행을 실패시킨다.

## AI_SEARCH_MODE 제한

- 자동 schedule을 두지 않고 `workflow_dispatch`로만 실행한다.
- `.github/workflows/daily-news.yml`에 `schedule:`이 있으면 정책 위반이다.
- `OPENAI_API_KEY`가 필요하다.
- 비용이 가장 커질 수 있으므로 큰 이슈를 확인해야 할 때만 사용한다.
- 결과는 Discord 전송 전에 artifact로 저장한다.

## Validate 비용 가드

- `daily-feed.yml`에는 `openai/codex-action`, `OPENAI_API_KEY`, `--search`가 없어야 한다.
- `daily-feed.yml`에는 `schedule:`이 없어야 한다.
- `daily-news.yml`에는 `schedule:`이 없어야 한다.
- `ai-brief-manual.yml`에는 `--search`가 없어야 한다.
- `kr-premium-brief.yml`을 제외한 workflow에서 `schedule:`과 `--search`가 동시에 존재하면 실패한다.
- KR premium workflow를 수정할 때는 `OPENAI_API_KEY`가 기존 `daily-feed.yml`에 주입되지 않는지 확인한다.
