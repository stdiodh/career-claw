# Webhook Setup

> Language: [한국어](../../kr/getting-started/webhook-setup.md) | [English](./webhook-setup.md)

Discord webhook URLs are Secrets. Do not paste real webhook URLs into docs, issues, pull requests, logs, screenshots, or examples.

## Delivery Model

Career Feed uses Discord Webhook delivery, not a Discord Gateway Bot or Slash Command service.

Delivery is disabled by default. A workflow sends to Discord only when:

- `dry_run=false`
- `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`
- a generic or workflow-specific webhook Secret exists
- validation passes
- delivery lock rules allow the send

## Secret Naming

New forks can enable delivery with one generic Secret:

- `DISCORD_WEBHOOK_CAREER_FEED`

Daily workflows can also use locale-specific webhook Secrets.

| Workflow | Locale | Preferred Secret | Legacy fallback | Generic fallback |
| --- | --- | --- | --- | --- |
| Daily Backend Brief | `ko-KR` | `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY` | `DISCORD_WEBHOOK_KR_TECH_DAILY` | `DISCORD_WEBHOOK_CAREER_FEED` |
| Daily Backend Brief | `en-US` | `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY` | none | `DISCORD_WEBHOOK_CAREER_FEED` |
| Dev News Daily | `ko-KR` | `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY` | `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | `DISCORD_WEBHOOK_CAREER_FEED` |
| Dev News Daily | `en-US` | `DISCORD_WEBHOOK_EN_US_NEWS_DAILY` | none | `DISCORD_WEBHOOK_CAREER_FEED` |
| Backend Career Site Radar | `ko-KR` | `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | none | `DISCORD_WEBHOOK_CAREER_FEED` |

Resolution order is preferred Secret, legacy fallback, then `DISCORD_WEBHOOK_CAREER_FEED`.

Optional failure alerts use `DISCORD_WEBHOOK_CAREER_FEED_OPS`. If it is missing, failure alert delivery should be skipped without failing the workflow.

## Variables

Webhook URLs are not Variables.

Use Variables only for non-sensitive settings:

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

`ko-KR` is the default supported locale.

During v0.2.x, existing forks can keep these legacy webhook Secret names:

- `DISCORD_WEBHOOK_KR_TECH_DAILY`
- `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY`

New forks can start with `DISCORD_WEBHOOK_CAREER_FEED`. Use the preferred locale-specific names when you want separate channels per feed or locale.

## en-US Foundation

`en-US` is a v0.2 foundation / experimental preset.

To test it, set:

```text
CAREER_FEED_ENABLED_LOCALES=ko-KR,en-US
```

Then add `DISCORD_WEBHOOK_CAREER_FEED` or the locale-specific Secrets:

- `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY`
- `DISCORD_WEBHOOK_EN_US_NEWS_DAILY`

Do this before enabling Discord delivery. Review `en-US` artifacts first because source/provider maturity is still experimental.

## Safe Setup Order

1. Add `OPENAI_API_KEY` as a Secret.
2. Run the Backend Daily workflow with `dry_run=true`.
3. Review artifacts and validation reports.
4. Add `DISCORD_WEBHOOK_CAREER_FEED` or the specific webhook Secret for the locale and workflow you want to test.
5. Set `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`.
6. Run with `dry_run=false` only after validation is clean.
7. Set `CAREER_FEED_SCHEDULE_ENABLED=true` only when recurring scheduled generation is intended.

## Validation

Run:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

For locale path checks:

```bash
python3 scripts/locale_config.py paths --locale ko-KR --feed backend-daily
python3 scripts/locale_config.py paths --locale en-US --feed backend-daily
python3 scripts/locale_config.py paths --locale ko-KR --feed news-daily
python3 scripts/locale_config.py paths --locale en-US --feed news-daily
```
