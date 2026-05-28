# Discord 채널 설정

KR Premium v2 기본 알림은 Daily Tech와 Weekly Career를 서로 다른 Discord 채널/Webhook으로 받는다.

## 기본 운영 채널

| 알림 | Workflow | Secret |
| --- | --- | --- |
| Daily Korea Tech Brief | `.github/workflows/kr-tech-daily.yml` | `DISCORD_WEBHOOK_KR_TECH_DAILY` |
| Weekly Backend Career Brief | `.github/workflows/kr-backend-career-weekly.yml` | `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` |

추천 채널 구성:

- `#career-tech-daily`: `DISCORD_WEBHOOK_KR_TECH_DAILY`
- `#career-backend-weekly`: `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

`Daily Korea Tech Brief`는 현재 뉴스 브리핑보다 Backend Daily Study Brief에 가깝다. 매일 Spring Boot/JVM 학습, Programmers 주차별 PS 루틴, Spring OSS 기여 후보, 한국 개발/AI 뉴스가 같은 채널로 전송된다.

`DISCORD_WEBHOOK_KR_PREMIUM_BRIEF`는 기존 4섹션 통합 브리핑을 수동으로 보낼 때만 쓰는 legacy/manual Secret으로 남긴다.

## Legacy/manual free RSS 채널

`configs/channels.json`은 legacy/manual free RSS 백업 workflow를 위한 설정이다. 실제 Webhook URL은 파일에 저장하지 않고 GitHub Secrets 또는 로컬 환경변수로만 주입한다.

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

무료 RSS 백업 workflow를 계속 수동 Discord 전송까지 유지하고 싶으면 아래 Secrets를 보존한다.

| 카테고리 | Secret |
| --- | --- |
| Daily Overview | `DISCORD_WEBHOOK_DAILY_OVERVIEW` |
| AI News | `DISCORD_WEBHOOK_AI_NEWS` |
| Backend News | `DISCORD_WEBHOOK_BACKEND_NEWS` |
| Security Alerts | `DISCORD_WEBHOOK_SECURITY_ALERTS` |
| Backend Tech | `DISCORD_WEBHOOK_BACKEND_TECH` |
| Job Feed | `DISCORD_WEBHOOK_JOB_FEED` |

무료 RSS 백업을 Discord로 보내지 않을 계획이면 위 legacy Webhook Secrets는 삭제 가능하다. 실제 GitHub Secrets 삭제는 GitHub UI에서 직접 수행한다.

## Legacy/manual free RSS 전송 순서

`Manual Free RSS Career Feed`를 수동 실행하면 legacy 무료 카테고리를 순차 전송한다. 이 workflow에는 schedule이 없다.

- `daily-overview`: 09:07
- `ai-news`: 09:08
- `backend-news`: 09:09
- `security-alerts`: 09:10
- `backend-tech`: 09:11, 기본 비활성화
- `job-feed`: 09:12, 기본 비활성화

## 메시지 형식

KR Premium v2 메시지는 Discord에서 바로 읽기 쉽게 짧은 Markdown으로 출력한다.

- 원문 링크는 `[원문 보기](URL)` 형식을 사용한다.
- Programmers 문제 링크는 `[문제 보기](URL)` 형식을 사용한다.
- GitHub issue 링크는 `[Issue 보기](URL)` 형식을 사용한다.
- `scripts/send-discord.py`는 Discord webhook payload에 `SUPPRESS_EMBEDS` flag를 설정한다.
- 긴 메시지는 `Career Feed - Backend Daily (1/3)`처럼 report 제목 기반 chunk header를 붙인다.
- Markdown 표는 사용하지 않는다.
- 같은 URL을 한 항목 안에서 중복해서 쓰지 않는다.

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않는다.
