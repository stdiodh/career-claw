# Runtime Configuration

> Language: [한국어](../../kr/getting-started/runtime-configuration.md) | [English](./runtime-configuration.md)

Career Feed forks can configure schedule times and Discord delivery without editing workflow YAML.

The GitHub UI location is `Settings > Secrets and variables > Actions`.

First-time users should follow [Fork Setup Guide](fork-setup.md). This page is the reference for supported settings.

## Secrets and Variables

Secrets are sensitive values. Variables are non-sensitive runtime settings.

| Type | Store | Examples |
| --- | --- | --- |
| Secrets | API keys, webhook URLs, client secrets | `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY` |
| Variables | Locale list, provider names, timezone, target time, delivery flag | `CAREER_FEED_ENABLED_LOCALES`, `CAREER_FEED_TIMEZONE` |

Do not put Discord Webhook URLs, API keys, or client secrets in Variables.

## Required Secrets

| Secret | Required | Used by |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Daily Backend Brief and News Daily generation |
| `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY` | Yes for `ko-KR` delivery | Daily Backend Brief |
| `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY` | Yes for `en-US` delivery | Daily Backend Brief |
| `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY` | Yes for `ko-KR` delivery | Dev News Daily |
| `DISCORD_WEBHOOK_EN_US_NEWS_DAILY` | Yes for `en-US` delivery | Dev News Daily |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Compatibility fallback | `ko-KR` Daily Backend Brief |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Compatibility fallback | `ko-KR` Dev News Daily |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Yes for delivery | Backend Career Site Radar |
| `NAVER_CLIENT_ID` | Optional | Korean news source enrichment |
| `NAVER_CLIENT_SECRET` | Optional | Korean news source enrichment |
| `BRAVE_SEARCH_API_KEY` | Optional | English search provider enrichment |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | Workflow failure alert |

Missing `DISCORD_WEBHOOK_CAREER_FEED_OPS` must only skip the optional alert.

## Supported Variables

| Name | Required | Default | Example | Description |
| --- | --- | --- | --- | --- |
| `CAREER_FEED_ENABLED_LOCALES` | Optional | `ko-KR` | `ko-KR,en-US` | Comma-separated locale list |
| `CAREER_FEED_DEFAULT_LOCALE` | Optional | `ko-KR` | `ko-KR` | Default locale for compatibility |
| `CAREER_FEED_SEARCH_PROVIDERS_KO_KR` | Optional | `naver,rss,github` | `naver,rss,github` | `ko-KR` provider order |
| `CAREER_FEED_SEARCH_PROVIDERS_EN_US` | Optional | `brave,rss,github` | `brave,rss,github` | `en-US` provider order |
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

## Locale Artifacts

Daily workflows write canonical artifacts under locale-specific directories.

| Workflow | Canonical output |
| --- | --- |
| Daily Backend Brief | `reports/briefs/{locale}/backend-daily.md` |
| Dev News Daily | `reports/briefs/{locale}/news-daily.md` |

Daily workflows also write candidate and ops artifacts under `reports/candidates/{locale}/` and `reports/ops/{locale}/`.

During the v0.2 compatibility window, affected `ko-KR` workflows also write legacy mirror files:

- `reports/briefs/kr-tech-daily.md`
- `reports/briefs/kr-tech-news-daily.md`
- `reports/briefs/kr-backend-career-weekly.md`

New forks should use canonical paths and locale-specific Secret names.

## Provider Fallback

Provider names are non-sensitive Variables. Provider credentials are Secrets.

If one configured provider is unavailable, Career Feed records a warning and continues with the remaining providers. `en-US` does not require Naver secrets, and `ko-KR` does not require Brave Search.

## Dry-run Relationship

Daily Backend Brief and Dev News Daily support `dry_run=true`.

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
