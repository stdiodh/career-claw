# 비용 정책

Career Feed의 기본 오전 알림은 KR Premium v2로 운영한다. OpenAI API 비용이 발생하므로 후보 pool을 먼저 만들고, OpenAI는 편집/선별/요약에만 사용한다.

## 운영 모드별 비용 기준

| 모드 | 용도 | 실행 방식 | 비용 기준 |
| --- | --- | --- | --- |
| KR Premium v2 Daily Tech | 한국 AI 테크 + 백엔드 기술 | 평일 자동 | OpenAI API 비용 발생 |
| KR Premium v2 Weekly Career | 백엔드 인턴/공모전/해커톤/경진대회 | 월요일 자동 | OpenAI API 비용 발생 |
| Legacy KR Premium | 기존 4섹션 통합 브리핑 | 수동 백업 | OpenAI API 비용 발생 |
| `FREE_MODE` | 무료 RSS/Atom 기반 백업 알림 | 수동 실행 전용 | OpenAI API 사용 안 함 |
| `AI_LIGHT_MODE` | 후보 JSON만 짧게 정제 | 수동 실행 전용 | 낮은 비용, live web search 없음 |
| `AI_SEARCH_MODE` | 수동 고급 브리핑 | 수동 실행 전용 | 검색량에 따라 비용 증가 |

## 기본 정책

- `--search`를 사용하지 않는다.
- Naver News Search API, RSS, 공식 URL, GitHub Issues 후보 pool을 먼저 만든다.
- OpenAI는 후보 JSON을 읽고 최종 Markdown을 편집/선별/요약하는 데만 사용한다.
- 모델은 기본적으로 `gpt-5.4-mini`, reasoning effort는 `low`를 사용한다.
- Codex Action의 `output-file`은 summary 파일로만 사용한다.
- 실제 report 파일은 Codex가 workspace의 지정 경로에 직접 작성한다.
- 같은 날 `workflow_dispatch`를 반복 실행하지 않는다.
- reports 산출물은 커밋하지 않는다.

## KR Premium v2 제한

Daily Tech:

- workflow: `.github/workflows/kr-tech-daily.yml`
- schedule: 평일 09:10 KST
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-tech`
- 입력 후보: AI 테크, 백엔드 기술, 오픈소스 기여 후보
- 출력: `reports/briefs/kr-tech-daily.md`

Weekly Career:

- workflow: `.github/workflows/kr-backend-career-weekly.yml`
- schedule: 월요일 09:30 KST
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode weekly-career`
- 입력 후보: 백엔드 커리어 이벤트
- 출력: `reports/briefs/kr-backend-career-weekly.md`

보안 뉴스는 기본 daily 섹션으로 운영하지 않는다. 보안 알림은 legacy/manual 백업으로만 유지한다. Daily Tech는 Spring Boot/Kotlin/JVM GitHub issue 기반 오픈소스 기여 후보를 최대 1개 포함하며, 자동 댓글, PR 생성, assign은 하지 않는다.

## 월 예상 비용

실제 비용은 입력 후보 수, 출력 길이, 수동 재실행 횟수, 모델 가격에 따라 달라진다.

| 운영 방식 | 월 예상 비용 | 기준 |
| --- | ---: | --- |
| `FREE_MODE` | $0 | OpenAI API 미사용 |
| KR Premium v2 Daily + Weekly | 약 $1~5 | 후보 pool 기반, `--search` 미사용 |
| 테스트/실패 반복 많음 | $10 이상 가능 | workflow_dispatch 반복 실행 시 |
| Legacy KR Premium 반복 실행 | 예측 어려움 | 4섹션 통합 출력과 반복 실행에 비례 |
| `AI_SEARCH_MODE` 반복 실행 | 예측 어려움 | live web search 사용량에 비례 |

초기 운영 예산은 월 $10 정도면 충분한 여유를 둔다. 안정화 전에는 Auto recharge를 OFF로 두는 것을 권장한다.

## 비용 가드

- `daily-feed.yml`에는 `openai/codex-action`, `OPENAI_API_KEY`, `--search`, `schedule:`이 없어야 한다.
- `daily-news.yml`에는 `schedule:`이 없어야 한다.
- `ai-brief-manual.yml`에는 `--search`가 없어야 한다.
- `kr-premium-brief.yml`은 legacy manual workflow이므로 `schedule:`이 없어야 한다.
- schedule이 있는 workflow에는 `--search`가 없어야 한다.
- Daily/Weekly workflow의 Codex `output-file`은 실제 report 파일이 아니라 summary 파일이어야 한다.
- Daily Tech workflow는 `DISCORD_WEBHOOK_KR_TECH_DAILY`를 사용해야 한다.
- Weekly Career workflow는 `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`를 사용해야 한다.
- schedule이 있는 workflow는 legacy `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`를 기본 전송에 사용하지 않는다.
- OpenAI Billing에서 monthly budget과 알림을 설정한다.
- 최초 실사용 테스트는 daily 1회, weekly 1회만 실행한다.

## 비용이 커지는 경우

- 같은 workflow를 같은 날 여러 번 수동 실행할 때
- 후보 JSON에 너무 많은 항목을 전달할 때
- 출력 Markdown이 길어질 때
- full model로 바꿀 때
- live web search를 사용하는 workflow를 반복 실행할 때
- 검증 실패 후 원인 확인 없이 재실행할 때

## Secrets 정책

남길 Secrets:

- `OPENAI_API_KEY`
- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `DISCORD_WEBHOOK_KR_TECH_DAILY`
- `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

legacy/manual로만 남길 수 있는 Secrets:

- `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`
- `DISCORD_WEBHOOK_DAILY_OVERVIEW`
- `DISCORD_WEBHOOK_AI_NEWS`
- `DISCORD_WEBHOOK_BACKEND_NEWS`
- `DISCORD_WEBHOOK_SECURITY_ALERTS`
- `DISCORD_WEBHOOK_BACKEND_TECH`
- `DISCORD_WEBHOOK_JOB_FEED`

Secret 값은 코드, 문서, 로그에 출력하지 않는다.
