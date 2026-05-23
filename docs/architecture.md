# 아키텍처

Career Feed는 GitHub Actions, RSS/Atom 수집, Markdown 리포트, Discord Webhook을 연결해 개발자 커리어 브리핑을 전달하는 자동화 프로젝트다.

## 기본 흐름

```text
GitHub Actions
      |
      v
RSS/Atom source collection
      |
      v
Candidate JSON
      |
      v
Rule-based Markdown brief
      |
      v
Category Discord Webhook
```

기본 일일 알림은 `FREE_MODE`로 실행되며 OpenAI API를 사용하지 않는다. 후보 수집은 `configs/sources.json`, 전송 대상은 `configs/channels.json`, 카테고리 정책은 `refs/categories/*.md`를 기준으로 한다.

## 구성 요소

### GitHub Actions

GitHub Actions는 예약 실행과 수동 실행의 진입점이다. 기본 workflow는 매일 09:03 KST에 후보 수집을 시작하고 09:07 KST부터 채널별 Webhook으로 순차 전송한다.

### RSS/Atom collector

`scripts/collect-feeds.py`는 Python 표준 라이브러리만 사용해 RSS/Atom을 파싱한다. 각 항목의 제목, 원본 URL, 출처, 발행시각, summary를 추출하고 최근 24시간 항목을 우선한다. 항목이 부족하면 최근 72시간까지 확장한다.

### Markdown renderer

`scripts/render-brief.py`는 후보 JSON을 읽어 짧은 Discord용 Markdown을 생성한다. 긴 해설을 만들지 않고 원본 URL 중심으로 구성한다.

### Discord sender

`scripts/send-category-briefs.py`는 `configs/channels.json`을 읽고 enabled 채널의 `brief_file`을 해당 Webhook으로 전송한다. 기존 `scripts/send-discord.py`는 단일 Markdown 파일 전송용으로 유지한다.

### Optional AI workflows

`AI_LIGHT_MODE`는 이미 수집된 후보 JSON만 Codex에 전달해 짧게 정제한다. `AI_SEARCH_MODE`는 live web search를 사용하는 수동 고급 모드이며 자동 실행하지 않는다.

## 초기 MVP에서 제외하는 것

- 상시 실행 서버
- Discord Gateway Bot
- Slash Command
- 데이터베이스 저장
- 로그인/회원 기능
- 웹 대시보드
