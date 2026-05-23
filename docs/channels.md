# Discord 채널 설정

Career Feed는 카테고리별 Discord Webhook을 사용한다. 실제 Webhook URL은 파일에 저장하지 않고 GitHub Secrets 또는 로컬 환경변수로만 주입한다.

## 설정 파일

채널 설정은 `configs/channels.json`에서 관리한다.

- `id`: 카테고리 식별자
- `name`: Discord 브리핑 제목에 사용할 이름
- `enabled`: 기본 전송 여부
- `reference`: 카테고리 참조 문서 경로
- `candidate_file`: 후보 JSON 경로
- `brief_file`: 전송할 Markdown 브리핑 경로
- `webhook_env`: Webhook URL을 담은 환경변수 이름
- `send_offset_minutes`: 09:07 KST 기준 지연 시간
- `max_items`: 브리핑에 포함할 최대 항목 수

## 필요한 Secrets

| 카테고리 | Secret |
| --- | --- |
| AI News | `DISCORD_WEBHOOK_AI_NEWS` |
| Backend News | `DISCORD_WEBHOOK_BACKEND_NEWS` |
| Security Alerts | `DISCORD_WEBHOOK_SECURITY_ALERTS` |
| Backend Tech Radar | `DISCORD_WEBHOOK_BACKEND_TECH` |
| Job Feed | `DISCORD_WEBHOOK_JOB_FEED` |

## 전송 순서

기본 workflow는 09:07 KST를 기준으로 `send_offset_minutes` 순서대로 전송한다.

- `ai-news`: 09:07
- `backend-news`: 09:08
- `security-alerts`: 09:09
- `backend-tech`: 09:10, 기본 비활성화
- `job-feed`: 09:11, 기본 비활성화

`enabled=false`인 채널은 기본 전송에서 제외된다. `enabled=true`인데 해당 `webhook_env` Secret이 없으면 명확한 오류로 실패한다.
