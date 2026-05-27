# Discord 채널 설정

기본 오전 알림은 `Daily Korea Premium Brief` 하나만 사용하며, Discord 전송도 `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` 하나로 처리한다.

이 문서의 `configs/channels.json`은 legacy/manual free RSS 백업 workflow를 위한 설정이다. 실제 Webhook URL은 파일에 저장하지 않고 GitHub Secrets 또는 로컬 환경변수로만 주입한다.

## 설정 파일

채널 설정은 `configs/channels.json`에서 관리한다.

- `id`: 카테고리 식별자
- `name`: Discord 브리핑 제목에 사용할 이름
- `enabled`: legacy free RSS 기본 전송 여부. 현재 기본 자동 운영에서는 사용하지 않으며 모두 `false`로 둔다.
- `reference`: 카테고리 참조 문서 경로
- `candidate_file`: 후보 JSON 경로
- `brief_file`: 전송할 Markdown 브리핑 경로
- `webhook_env`: Webhook URL을 담은 환경변수 이름
- `send_offset_minutes`: 09:07 KST 기준 지연 시간
- `max_items`: 브리핑에 포함할 최대 항목 수
- `include_in_ai`: AI_LIGHT_MODE 입력 포함 여부

## 기본 운영 Secret

기본 오전 알림은 아래 Secret 하나로 Discord에 전송한다.

| 기능 | Secret |
| --- | --- |
| KR Premium 통합 브리핑 | `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` |

## Legacy/manual free RSS용 선택 Secrets

무료 RSS 백업 workflow를 수동 실행할 때만 아래 Webhook Secret이 필요하다.

| 카테고리 | Secret |
| --- | --- |
| Daily Overview | `DISCORD_WEBHOOK_DAILY_OVERVIEW` |
| AI News | `DISCORD_WEBHOOK_AI_NEWS` |
| Backend News | `DISCORD_WEBHOOK_BACKEND_NEWS` |
| Security Alerts | `DISCORD_WEBHOOK_SECURITY_ALERTS` |

Backend Tech Radar와 Job Feed는 계속 비활성화 상태로 두며, 기본 운영이나 수동 무료 RSS 백업에 Secret이 필요하지 않다.

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않는다.

## Legacy/manual free RSS 전송 순서

`Manual Free RSS Career Feed`를 수동 실행하면 legacy 무료 카테고리를 순차 전송한다. 이 workflow에는 schedule이 없다.

- `daily-overview`: 09:07
- `ai-news`: 09:08
- `backend-news`: 09:09
- `security-alerts`: 09:10
- `backend-tech`: 09:11, 기본 비활성화
- `job-feed`: 09:12, 기본 비활성화

## 메시지 형식

카테고리별 상세 메시지는 원본 링크를 유지하고 아래처럼 짧게 출력한다.

- 핵심: RSS 설명 기반 1줄
- 왜 봐야 함: 카테고리와 키워드 기반 1줄
- 출처: Source / 발행시각

현재 `configs/channels.json`의 무료 RSS 채널은 기본 자동 운영 필수가 아니므로 `enabled=false`로 둔다. 수동 백업 workflow는 필요한 legacy 카테고리를 `--include-disabled`로 명시 실행한다.
