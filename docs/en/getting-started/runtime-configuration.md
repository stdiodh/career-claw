# Runtime Configuration

> Language: [한국어](../../kr/getting-started/runtime-configuration.md) | [English](./runtime-configuration.md)

Career Feed forks can configure schedule times and Discord delivery without editing workflow YAML.

The GitHub UI location is `Settings > Secrets and variables > Actions`.

First-time users should follow [Fork Setup Guide](fork-setup.md). This page is the reference for supported settings.

## Secrets and Variables

Secrets are sensitive values. Variables are non-sensitive runtime settings.

| Type | Store | Examples |
| --- | --- | --- |
| Secrets | API keys, webhook URLs, client secrets | `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY` |
| Variables | Timezone, target time, weekday, delivery flag | `CAREER_FEED_TIMEZONE`, `CAREER_FEED_BACKEND_DAILY_TIME` |

Do not put Discord Webhook URLs, API keys, or client secrets in Variables.

## Required Secrets

| Secret | Required | Used by |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Daily Backend Brief and News Daily generation |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Yes for delivery | Daily Backend Brief |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Yes for delivery | Korea Dev/AI News Daily |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Yes for delivery | Backend Career Site Radar |
| `NAVER_CLIENT_ID` | Optional | Korean news source enrichment |
| `NAVER_CLIENT_SECRET` | Optional | Korean news source enrichment |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | Workflow failure alert |

Missing `DISCORD_WEBHOOK_CAREER_FEED_OPS` must only skip the optional alert.

## Supported Variables

| Name | Required | Default | Example | Description |
| --- | --- | --- | --- | --- |
| `CAREER_FEED_TIMEZONE` | Optional | `Asia/Seoul` | `Asia/Seoul` | Timezone for runtime gate |
| `CAREER_FEED_BACKEND_DAILY_TIME` | Optional | `09:00` | `09:00` | Daily Backend target time |
| `CAREER_FEED_NEWS_DAILY_TIME` | Optional | `09:05` | `09:05` | News Daily target time |
| `CAREER_FEED_CAREER_WEEKLY_DAY` | Optional | `MON` | `MON` | Site Radar target weekday |
| `CAREER_FEED_CAREER_WEEKLY_TIME` | Optional | `09:00` | `09:00` | Site Radar target time |
| `CAREER_FEED_OSS_RECENT_DAYS` | Optional | `30` | `30` | OSS issue `created_at` freshness window |
| `CAREER_FEED_DISCORD_DELIVERY_ENABLED` | Optional | `false` | `false` | Enables Discord delivery |

`CAREER_FEED_OSS_RECENT_DAYS` is a hard gate for Daily Backend OSS candidates and final Markdown validation.

## Time Format

Use `HH:MM`.

Allowed: `09:00`, `18:30`, `23:45`.

Rejected: `9:00`, `24:00`, `09:60`, `morning`.

## Timezone Examples

Use an IANA timezone name such as `Asia/Seoul`, `UTC`, or `America/Los_Angeles`.

Invalid examples: `Seoul`, `KST`, `America/Los Angeles`.

Invalid timezone values produce an `invalid_config` skip reason instead of silently falling back.

## Weekday Format

Use `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, or `SUN`.

Lowercase values are normalized. Other values are configuration errors.

## Runtime Gate Behavior

GitHub Actions `on.schedule` cron cannot read repository Variables directly.

Career Feed workflows wake up periodically with `5,35 * * * *`, then run `scripts/should-run-now.py` early in the job.

The runtime gate converts current UTC time to the configured timezone, reads the workflow target time, checks the 30-minute window, and either continues or exits successfully with a skip reason.

Manual `workflow_dispatch` runs are not blocked by the runtime time window.

## GitHub Actions Output

| Output | Meaning |
| --- | --- |
| `should_run` | Whether later workflow steps continue |
| `reason` | Run or skip reason |
| `timezone` | Parsed timezone |
| `target_time` | Workflow target time |
| `local_now` | Current local time |
| `local_date` | Local date for delivery lock |

The workflows write to `$GITHUB_OUTPUT`, not deprecated `::set-output`.

## Discord Delivery Priority

1. `dry_run=true` always blocks delivery.
2. Manual delivery option can block delivery.
3. `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false` blocks delivery.
4. Missing required Discord webhook Secret blocks delivery with a clear error.
5. Delivery can proceed only after validation passes.

The default delivery flag is `false` to prevent accidental fork sends.

## Dry-run Relationship

Daily Backend Brief and Korea Dev/AI News Daily support `dry_run=true`.

Dry-run still collects candidates, generates drafts, validates output, and uploads artifacts.

Dry-run does not send to Discord and does not write the delivery lock.

## Local Checks

`.env.example` is not a substitute for GitHub Actions Variables.

Check the runtime gate locally:

```bash
python3 scripts/should-run-now.py --workflow backend_daily
python3 scripts/should-run-now.py --workflow news_daily
python3 scripts/should-run-now.py --workflow career_weekly
```

Check a specific UTC time:

```bash
python3 scripts/should-run-now.py --workflow backend_daily --now-utc 2026-06-08T00:05:00Z
```

## Common Configuration Mistakes

- Waiting for Discord while `dry_run=true`.
- Forgetting `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`.
- Putting webhook URLs in Variables.
- Using `9:00` instead of `09:00`.
- Using `America/Los Angeles` with a space.
- Using `Monday` instead of `MON`.
- Misspelling a Secret name.

## Current Phase Limits

Runtime gate and delivery flag control whether workflows continue and whether Discord delivery is attempted.

Daily Backend OSS recency filtering uses `created_at`, and final Markdown validation checks the safe candidate allowlist again.
