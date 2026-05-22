# 아키텍처

Career Feed는 GitHub Actions, Codex, Markdown 리포트, Discord Webhook을 연결해 매일 개발자 커리어 브리핑을 전달하는 자동화 프로젝트다.

## 전체 흐름

```text
GitHub Actions
      |
      v
Codex live web search
      |
      v
Markdown report
      |
      v
Discord Webhook
      |
      v
Discord channel
```

## 구성 요소

### GitHub Actions

GitHub Actions는 예약 실행과 수동 실행의 진입점이다. 매일 정해진 시간에 브리핑 작업을 실행하고, 필요할 때 `workflow_dispatch`로 같은 작업을 수동 실행할 수 있도록 한다.

초기 MVP에서는 별도 서버를 운영하지 않고 GitHub Actions 실행 환경 안에서 작업을 완료한다.

### Codex

Codex는 live web search를 사용해 최근 24시간의 AI, 백엔드, 클라우드, 보안, 오픈소스 릴리스 관련 정보를 확인한다. 공식 출처, 릴리스 노트, 보안 공지를 우선해 검토하고 3~5개 주요 항목만 선별한다.

### Markdown report

선별된 항목은 Discord에서 읽기 쉬운 Markdown 리포트로 정리한다. 리포트는 날짜, 분류, 요약, 실무 관점의 의미, 출처 링크를 포함하는 형식을 지향한다.

생성된 일일 리포트 파일은 기본적으로 커밋하지 않는다. 저장소에는 `reports/.gitkeep`만 유지해 디렉터리 구조를 보존한다.

### Discord Webhook

Discord Webhook은 생성된 Markdown 리포트를 지정된 Discord 채널로 전송한다. Webhook URL은 `DISCORD_WEBHOOK_URL` 환경변수 또는 GitHub Secrets로만 주입한다.

## 초기 MVP에서 제외하는 것

- OpenClaw 연동
- 상시 실행 서버
- Discord Gateway Bot
- Slash Command
- 데이터베이스 저장
- 로그인/회원 기능
- 웹 대시보드
