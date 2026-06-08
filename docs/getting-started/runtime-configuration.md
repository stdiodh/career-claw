# Runtime Configuration

Career Feed fork는 workflow YAML을 직접 수정하지 않고도 실행 시간과 Discord 전송 여부를 설정할 수 있습니다.

설정 위치는 GitHub repository의 `Settings > Secrets and variables > Actions`입니다.

민감한 값은 Secrets에 넣고, 시간대나 실행 시간 같은 운영 설정은 Variables에 넣습니다.

처음 fork에서 실행한다면 이 문서보다 [Fork Setup Guide](fork-setup.md)를 먼저 따라가세요.

## 요약

처음 fork했다면 다음 순서로 설정합니다.

1. GitHub Actions를 fork에서 활성화합니다.
2. 필요한 Secrets를 등록합니다.
3. 필요한 Variables를 등록합니다.
4. Daily workflow를 `dry_run=true`로 수동 실행합니다.
5. artifact와 validation report를 확인합니다.
6. Discord 전송을 원할 때만 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`로 바꿉니다.
7. 다시 수동 실행하거나 다음 scheduled run을 기다립니다.

Discord Webhook URL, API key, client secret은 Variables에 넣지 않습니다.

실제 secret 값은 README, docs, issue, PR, commit message, Actions log, screenshot에 쓰지 않습니다.

## Secrets와 Variables

Secrets는 외부에 노출되면 안 되는 값입니다.

Variables는 노출되어도 보안 사고가 되지 않는 실행 설정값입니다.

두 값을 분리합니다.

| 구분 | 저장할 값 | 예시 |
| --- | --- | --- |
| Secrets | API key, Webhook URL, client secret | `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY` |
| Variables | timezone, 실행 시간, 요일, delivery flag | `CAREER_FEED_TIMEZONE`, `CAREER_FEED_BACKEND_DAILY_TIME` |

## 필수 Secrets

브리핑 생성과 Discord 전송에 사용하는 민감값입니다.

| Secret | Required | 사용처 |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Daily Backend Brief와 News Daily 초안 생성 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Discord 전송 시 Yes | Daily Backend Brief 전송 |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Discord 전송 시 Yes | Korea Dev/AI News Daily 전송 |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Discord 전송 시 Yes | Backend Career Site Radar 전송 |
| `NAVER_CLIENT_ID` | Optional | 한국 뉴스 후보 수집 보강 |
| `NAVER_CLIENT_SECRET` | Optional | 한국 뉴스 후보 수집 보강 |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | workflow 실패 알림 |

`DISCORD_WEBHOOK_CAREER_FEED_OPS`가 없어도 실패 알림 전송만 건너뛰어야 하며, 그 이유만으로 workflow가 실패하면 안 됩니다.

## 지원 Variables

Variables는 `Settings > Secrets and variables > Actions > Variables`에 등록합니다.

값을 비워 두면 기본값을 사용합니다.

| Name | Required | Default | Example | Description |
| --- | --- | --- | --- | --- |
| `CAREER_FEED_TIMEZONE` | Optional | `Asia/Seoul` | `Asia/Seoul` | runtime gate가 사용할 기준 시간대 |
| `CAREER_FEED_BACKEND_DAILY_TIME` | Optional | `09:00` | `09:00` | Daily Backend Brief 실행 희망 시간 |
| `CAREER_FEED_NEWS_DAILY_TIME` | Optional | `09:05` | `09:05` | Korea Dev/AI News Daily 실행 희망 시간 |
| `CAREER_FEED_CAREER_WEEKLY_DAY` | Optional | `MON` | `MON` | Backend Career Site Radar 실행 요일 |
| `CAREER_FEED_CAREER_WEEKLY_TIME` | Optional | `09:00` | `09:00` | Backend Career Site Radar 실행 희망 시간 |
| `CAREER_FEED_OSS_RECENT_DAYS` | Optional | `30` | `30` | OSS 후보 `created_at` freshness 기준일 |
| `CAREER_FEED_DISCORD_DELIVERY_ENABLED` | Optional | `false` | `false` | Discord 전송 활성화 여부 |

`CAREER_FEED_OSS_RECENT_DAYS`는 Daily Backend Brief의 OSS 후보 추천에서 `created_at` 기준 최근 N일 hard gate로 사용합니다.

최종 Markdown validator도 같은 값을 기준으로 OSS 섹션의 GitHub issue URL을 다시 검증합니다.
candidate artifact allowlist에 없거나 `created_at` window 밖인 issue URL은 Discord 전송 전에 실패합니다.

값이 비어 있으면 30을 사용합니다.

숫자가 아니거나 0 이하이면 30을 사용하고 warning을 남깁니다.

365를 초과하면 365로 clamp하고 warning을 남깁니다.

값을 너무 넓게 잡으면 오래된 open issue가 후보 pool에 더 많이 남을 수 있으므로, 기본 30일을 먼저 사용하는 것을 권장합니다.

## 시간 형식

시간은 항상 `HH:MM` 형식입니다.

허용 예시:

- `09:00`
- `18:30`
- `23:45`

거부 예시:

- `9:00`
- `24:00`
- `09:60`
- `morning`

잘못된 값이 들어오면 runtime gate는 비싼 작업을 시작하지 않고 skip reason에 설정 오류를 남깁니다.

## Timezone 예시

`CAREER_FEED_TIMEZONE`은 Python `zoneinfo`가 인식하는 IANA timezone 이름이어야 합니다.

예시:

- `Asia/Seoul`
- `UTC`
- `America/Los_Angeles`

잘못된 예시:

- `Seoul`
- `KST`
- `America/Los Angeles`

알 수 없는 timezone은 `Asia/Seoul`로 조용히 fallback하지 않습니다.

runtime gate는 `invalid_config` skip reason을 남깁니다.

## 요일 형식

`CAREER_FEED_CAREER_WEEKLY_DAY`는 다음 값만 사용합니다.

| 값 | 의미 |
| --- | --- |
| `MON` | Monday |
| `TUE` | Tuesday |
| `WED` | Wednesday |
| `THU` | Thursday |
| `FRI` | Friday |
| `SAT` | Saturday |
| `SUN` | Sunday |

소문자는 대문자로 normalize합니다.

목록에 없는 값은 설정 오류로 처리합니다.

올바른 예시:

- `MON`
- `TUE`
- `FRI`

잘못된 예시:

- `Monday`
- `mon-day`
- `1`

## Runtime Gate 방식

GitHub Actions의 `on.schedule` cron은 repository Variables를 직접 참조할 수 없습니다.

그래서 workflow YAML의 cron을 사용자별 시간으로 바꾸지 않습니다.

대신 workflow가 `5,35 * * * *` cron으로 주기적으로 깨어나고, 초반에 `scripts/should-run-now.py`를 실행합니다.

runtime gate는 다음을 수행합니다.

1. 현재 UTC 시각을 구합니다.
2. `CAREER_FEED_TIMEZONE` 기준 local time으로 변환합니다.
3. workflow type에 맞는 target time을 읽습니다.
4. target time 이후 30분 미만 window인지 확인합니다.
5. 실행 시간이 아니면 `should_run=false`를 GitHub Actions output에 씁니다.
6. 실행 시간이면 `should_run=true`를 쓰고 기존 생성, 검증, 전송 흐름을 계속합니다.

Daily workflow는 기존 동작을 보존하기 위해 local weekday 기준 월요일부터 금요일까지만 scheduled run을 통과시킵니다.

수동 `workflow_dispatch` 실행은 시간 window와 요일 비교를 통과하지 않아도 `should_run=true`로 처리합니다.

## GitHub Actions Output

runtime gate는 최신 방식인 `$GITHUB_OUTPUT`에 값을 씁니다.

주요 output은 다음과 같습니다.

| Output | 의미 |
| --- | --- |
| `should_run` | 이후 workflow를 계속할지 여부 |
| `reason` | 실행 또는 skip 이유 |
| `timezone` | 해석된 timezone |
| `target_time` | workflow별 target time |
| `local_now` | timezone 기준 현재 시각 |
| `local_date` | delivery lock에 사용할 local date |

`::set-output`은 사용하지 않습니다.

## Discord 전송 우선순위

Discord 전송은 다음 순서로 결정합니다.

1. `dry_run=true`이면 무조건 전송하지 않습니다.
2. `workflow_dispatch`에서 명시적으로 delivery를 끈 경우 전송하지 않습니다.
3. `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`이면 전송하지 않습니다.
4. 필요한 Discord Webhook secret이 없으면 전송하지 않고 명확한 오류를 냅니다.
5. 위 조건을 모두 통과하면 전송할 수 있습니다.

처음 fork한 사용자의 실수 전송을 막기 위해 `CAREER_FEED_DISCORD_DELIVERY_ENABLED` 기본값은 `false`입니다.

Daily workflow는 Discord 전송이 성공했을 때만 delivery lock marker를 저장합니다.

Backend Career Site Radar는 이번 Phase에서 별도 delivery lock을 추가하지 않습니다.

scheduled run은 runtime gate의 30분 미만 window로 중복 실행 위험을 낮춥니다.

## Dry-run 관계

Daily Backend Brief와 Korea Dev/AI News Daily는 `dry_run=true`로 수동 실행할 수 있습니다.

이 경우 후보 수집, 초안 생성, validator, artifact 업로드는 실행됩니다.

Discord 전송과 delivery lock 저장은 하지 않습니다.

`CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`로 설정되어 있어도 `dry_run=true`가 우선합니다.

## 10분 설정 절차

처음 fork했다면 아래 값만 먼저 설정해도 됩니다.

1. Secret `OPENAI_API_KEY`를 등록합니다.
2. Discord 전송을 테스트할 channel의 Webhook URL을 필요한 Secret에 등록합니다.
3. Variable `CAREER_FEED_TIMEZONE`을 원하는 timezone으로 설정합니다.
4. Variable `CAREER_FEED_BACKEND_DAILY_TIME` 또는 `CAREER_FEED_NEWS_DAILY_TIME`을 원하는 시간으로 설정합니다.
5. Variable `CAREER_FEED_DISCORD_DELIVERY_ENABLED`는 처음에는 `false`로 둡니다.
6. GitHub Actions에서 Daily workflow를 `dry_run=true`로 실행합니다.
7. artifact와 validation report를 확인합니다.
8. 실제 전송을 원할 때 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`로 바꿉니다.

Webhook URL placeholder를 문서나 commit에 적지 않습니다.

GitHub Secrets 화면에만 실제 값을 입력합니다.

## 로컬 확인

`.env.example`은 GitHub Actions Variables를 대신 설정하는 파일이 아닙니다.

다만 로컬 테스트와 문서 참고용으로 같은 이름의 예시 값을 제공합니다.

runtime gate만 로컬에서 확인하려면 다음 명령을 실행합니다.

```bash
python3 scripts/should-run-now.py --workflow backend_daily
python3 scripts/should-run-now.py --workflow news_daily
python3 scripts/should-run-now.py --workflow career_weekly
```

특정 UTC 시각을 넣어 확인할 수도 있습니다.

```bash
python3 scripts/should-run-now.py --workflow backend_daily --now-utc 2026-06-08T00:05:00Z
```

## 자주 발생하는 설정 실수

- `CAREER_FEED_DISCORD_DELIVERY_ENABLED`를 `true`로 바꾸지 않아 Discord 전송이 skip됩니다.
- `dry_run=true`로 실행해 놓고 Discord 메시지를 기다립니다.
- Webhook URL을 Variables에 넣습니다.
- `09:00` 대신 `9:00`을 입력합니다.
- `America/Los Angeles`처럼 공백이 있는 timezone 이름을 입력합니다.
- weekly 요일을 `Monday`로 입력합니다.
- Secret 이름을 workflow가 기대하는 이름과 다르게 만듭니다.
- fork에서 GitHub Actions를 활성화하지 않습니다.

## 이번 Phase 한계

runtime gate와 Discord delivery flag는 workflow 초반 실행 여부를 제어합니다.

OSS 후보 최근 N일 필터링은 Daily Backend Brief 후보 수집 단계에서 적용합니다.

최종 Markdown validator도 safe candidate artifact allowlist와 `created_at` recency를 다시 확인합니다.

브리핑 내부 기준시각과 일부 표시 문구는 기존 KST 중심 정책을 유지합니다.
