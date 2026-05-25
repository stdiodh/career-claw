# 비용 정책

Career Feed의 기본 원칙은 매일 실행되는 알림에서 OpenAI API와 live web search를 사용하지 않는 것이다. 비용 절약이 1순위이며, 사용자가 원본 URL을 직접 확인할 수 있도록 링크 중심 브리핑을 만든다.

## 운영 모드

| 모드 | 용도 | 실행 방식 | 비용 기준 |
| --- | --- | --- | --- |
| `FREE_MODE` | 매일 기본 알림 | RSS/Atom 수집, 규칙 기반 선별, Markdown 렌더링, Discord 전송 | OpenAI API 사용 안 함 |
| `AI_LIGHT_MODE` | 선택형 짧은 정제 | 이미 수집된 후보 JSON과 참조 문서만 Codex에 전달 | 수동 실행 전용 |
| `AI_SEARCH_MODE` | 수동 고급 브리핑 | Codex live web search 사용 | 특별한 경우에만 사용 |

## 기본 정책

- 매일 알림은 `FREE_MODE`로 운영한다.
- `FREE_MODE` workflow는 `OPENAI_API_KEY`를 요구하지 않는다.
- 자동 실행 workflow는 `.github/workflows/daily-feed.yml` 하나만 둔다.
- Daily Overview는 `DISCORD_WEBHOOK_DAILY_OVERVIEW`로 전송하며 AI 비용을 발생시키지 않는다.
- 후보 수집은 `configs/sources.json`에 등록된 RSS/Atom/공식 URL을 기준으로 한다.
- 브리핑은 원본 제목, 1줄 요약, 출처, 발행일, URL 중심으로 구성한다.
- 원문 확인이 필요한 항목은 내용을 추측하지 않고 "원문 확인 필요"라고 표시한다.

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
- `daily-news.yml`에는 `schedule:`이 없어야 한다.
- `ai-brief-manual.yml`에는 `--search`가 없어야 한다.
- 모든 workflow에서 `schedule:`과 `--search`가 동시에 존재하면 실패한다.
