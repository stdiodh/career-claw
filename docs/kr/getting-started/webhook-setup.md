# Webhook Setup

> Language: [한국어](./webhook-setup.md) | [English](../../en/getting-started/webhook-setup.md)

Discord Webhook URL은 Secret입니다. 실제 webhook URL을 docs, issue, PR, log, screenshot, 예시에 붙여 넣지 마세요.

## Delivery Model

Career Feed는 Discord Webhook으로 전송합니다.

Discord Gateway Bot이나 Slash Command service를 사용하지 않습니다.

기본값은 전송 비활성화입니다. Discord 전송은 아래 조건을 모두 만족할 때만 진행됩니다.

- `dry_run=false`
- `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`
- generic 또는 workflow-specific webhook Secret이 있음
- validator 통과
- delivery lock 규칙상 전송 가능

## Secret Naming

새 fork는 generic Secret 하나로 Discord delivery를 시작할 수 있습니다.

- `DISCORD_WEBHOOK_CAREER_FEED`

Daily workflow는 locale-specific webhook Secret도 사용할 수 있습니다.

| Workflow | Locale | Preferred Secret | Legacy fallback | Generic fallback |
| --- | --- | --- | --- | --- |
| Daily Backend Brief | `ko-KR` | `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY` | `DISCORD_WEBHOOK_KR_TECH_DAILY` | `DISCORD_WEBHOOK_CAREER_FEED` |
| Daily Backend Brief | `en-US` | `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY` | none | `DISCORD_WEBHOOK_CAREER_FEED` |
| Dev News Daily | `ko-KR` | `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY` | `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | `DISCORD_WEBHOOK_CAREER_FEED` |
| Dev News Daily | `en-US` | `DISCORD_WEBHOOK_EN_US_NEWS_DAILY` | none | `DISCORD_WEBHOOK_CAREER_FEED` |
| Backend Career Site Radar | `ko-KR` | `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | none | `DISCORD_WEBHOOK_CAREER_FEED` |

해석 순서는 preferred Secret, legacy fallback, `DISCORD_WEBHOOK_CAREER_FEED`입니다.

선택 실패 알림은 `DISCORD_WEBHOOK_CAREER_FEED_OPS`를 사용합니다. 이 Secret이 없으면 실패 알림 전송만 건너뛰어야 하며 workflow 실패 원인이 되면 안 됩니다.

## Variables

Webhook URL은 Variable이 아닙니다.

Variables에는 노출되어도 보안 사고가 되지 않는 설정만 넣습니다.

- `CAREER_FEED_ENABLED_LOCALES`
- `CAREER_FEED_DEFAULT_LOCALE`
- `CAREER_FEED_SEARCH_PROVIDERS_KO_KR`
- `CAREER_FEED_SEARCH_PROVIDERS_EN_US`
- `CAREER_FEED_TIMEZONE`
- `CAREER_FEED_BACKEND_DAILY_TIME`
- `CAREER_FEED_NEWS_DAILY_TIME`
- `CAREER_FEED_CAREER_WEEKLY_DAY`
- `CAREER_FEED_CAREER_WEEKLY_TIME`
- `CAREER_FEED_OSS_RECENT_DAYS`
- `CAREER_FEED_SCHEDULE_ENABLED`
- `CAREER_FEED_DISCORD_DELIVERY_ENABLED`

## ko-KR Compatibility

`ko-KR`은 기본 지원 locale입니다.

v0.2.x 동안 기존 fork는 아래 legacy webhook Secret 이름을 계속 사용할 수 있습니다.

- `DISCORD_WEBHOOK_KR_TECH_DAILY`
- `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY`

새 fork는 `DISCORD_WEBHOOK_CAREER_FEED`로 시작할 수 있습니다. feed 또는 locale별로 다른 채널을 쓰고 싶을 때 preferred locale-specific 이름을 사용하세요.

## en-US Foundation

`en-US`는 v0.2 foundation / experimental preset입니다.

테스트하려면 다음 Variable을 설정합니다.

```text
CAREER_FEED_ENABLED_LOCALES=ko-KR,en-US
```

그리고 `DISCORD_WEBHOOK_CAREER_FEED` 또는 아래 locale-specific Secret을 추가합니다.

- `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY`
- `DISCORD_WEBHOOK_EN_US_NEWS_DAILY`

Discord delivery를 켜기 전에 먼저 등록하세요. `en-US` source/provider maturity는 아직 실험 단계이므로 artifact를 먼저 검토합니다.

## Safe Setup Order

1. `OPENAI_API_KEY`를 Secret으로 등록합니다.
2. Backend Daily workflow를 `dry_run=true`로 실행합니다.
3. artifact와 validation report를 검토합니다.
4. `DISCORD_WEBHOOK_CAREER_FEED` 또는 테스트할 locale과 workflow에 맞는 webhook Secret을 등록합니다.
5. `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`로 바꿉니다.
6. validator가 통과한 뒤에만 `dry_run=false`로 실행합니다.
7. 반복 scheduled generation이 필요할 때만 `CAREER_FEED_SCHEDULE_ENABLED=true`를 설정합니다.

## Validation

검증 명령:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

Locale path 확인:

```bash
python3 scripts/locale_config.py paths --locale ko-KR --feed backend-daily
python3 scripts/locale_config.py paths --locale en-US --feed backend-daily
python3 scripts/locale_config.py paths --locale ko-KR --feed news-daily
python3 scripts/locale_config.py paths --locale en-US --feed news-daily
```
