# Fork Setup Guide

> Language: [한국어](../../kr/getting-started/fork-setup.md) | [English](./fork-setup.md)

This guide gets a forked Career Feed repository to the first successful dry-run, artifact review, and optional Discord delivery.

For setting details, see [Runtime Configuration](runtime-configuration.md). For webhook naming, see [Webhook Setup](webhook-setup.md). For routine operation, see [Usage Guide](usage.md). For OSS rules, see [OSS Candidate Policy](../policies/oss-candidate-policy.md).

If you only need the first check without editing workflow YAML, start with [Fresh Fork Smoke Test](fresh-fork-smoke-test.md).

If you prefer GitHub CLI after enabling Actions, use the optional [CLI Setup](cli-setup.md) helper.

## Before You Start

Prepare these items:

- GitHub account
- Forked Career Feed repository
- OpenAI API key
- Optional Discord Webhook URL for later delivery
- Optional Naver or Brave Search API credentials for later enrichment

Security rules:

- Do not put real API keys, webhook URLs, tokens, or client secrets in docs, issues, pull requests, commits, logs, or screenshots.
- Put API keys, Discord Webhook URLs, and client secrets in GitHub Actions Secrets.
- Repository Variables are optional overrides, not required first-run setup.
- Start the first run with `dry_run=true` and `force_send=false`; `dry_run` now defaults to `true` for manual daily workflows.

The screenshots use real GitHub UI screens. If button names move slightly, follow the navigation path and input values.

## Step 1. Fork Repository

Fork `stdiodh/career-feed` on GitHub.

![Fork button in the GitHub repository header](../../assets/getting-started/00-repository-fork-button.png)

1. Click `Fork` in the original repository header.
2. Create the fork under your account or organization.
3. Continue from the default branch of your fork.

Do not edit workflow YAML first. Configure the required Secret first.

## Step 2. Enable GitHub Actions

Open the `Actions` tab in the fork.

![GitHub Actions tab and workflow list](../../assets/getting-started/01-actions-tab-workflow-list.png)

1. Click the repository `Actions` tab.
2. If GitHub blocks fork workflow execution, click `I understand my workflows, go ahead and enable them` or the equivalent enable button.
3. Confirm that `Backend Daily Brief`, `Dev News Daily`, `Backend Career Site Radar`, and `Mark PS Solved` appear in the workflow list.

Scheduled runs work reliably from the default branch.

## Step 3. Add GitHub Actions Secrets

Go to `Settings > Secrets and variables > Actions > Secrets`.

CLI alternative: after `gh auth login`, run `scripts/setup-fork.sh --minimal` from a cloned fork or see [CLI Setup](cli-setup.md).

![New repository secret button](../../assets/getting-started/02-secrets-new-repository-secret.png)

1. Select the `Secrets` tab.
2. Click `New repository secret`.
3. Enter the exact secret name from the table in `Name`.
4. Enter the real value in `Secret`.
5. Click `Add secret`.

![Secret form fields](../../assets/getting-started/03-secrets-add-secret-form.png)

For the first Backend Daily dry-run, add only one Secret.

| Name | Required | Used by |
| --- | --- | --- |
| `OPENAI_API_KEY` | Required for first dry-run | Brief generation |

Optional delivery and enrichment Secrets can be added later.

| Name | Required | Used by |
| --- | --- | --- |
| `DISCORD_WEBHOOK_CAREER_FEED` | Optional generic delivery Secret | Any Discord delivery |
| `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY` | Optional specific delivery Secret | Daily Backend Brief |
| `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY` | Optional specific delivery Secret | Daily Backend Brief |
| `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY` | Optional specific delivery Secret | Dev News Daily |
| `DISCORD_WEBHOOK_EN_US_NEWS_DAILY` | Optional specific delivery Secret | Dev News Daily |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Compatibility fallback | `ko-KR` Daily Backend Brief |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Compatibility fallback | `ko-KR` Dev News Daily |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Optional specific delivery Secret | Backend Career Site Radar |
| `NAVER_CLIENT_ID` | Optional | `ko-KR` source integration |
| `NAVER_CLIENT_SECRET` | Optional | `ko-KR` source integration |
| `BRAVE_SEARCH_API_KEY` | Optional | `en-US` source integration |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | Ops/debug alerts |

Use obvious placeholders such as `your-openai-api-key` only in docs or examples.

## Step 4. Confirm First Dry-run Defaults

You do not need repository Variables for the first dry-run.

Use the `OPENAI_API_KEY` Secret added above, keep Discord delivery unconfigured, and use the default `ko-KR` locale.

## Step 5. Run Workflow with Dry Run

Open `Actions` and choose `Backend Daily Brief`.

1. Click `Run workflow`.
2. Confirm the branch is the default branch.
3. Keep `dry_run` as `true`.
4. Keep `force_send` as `false`.
5. Click the final `Run workflow` button.

![Run workflow inputs](../../assets/getting-started/06-actions-run-workflow-inputs.png)

GitHub may show boolean input descriptions as checkbox labels. The first checkbox is `dry_run`; the second is `force_send`.

If the button is missing, confirm that Actions are enabled, the workflow exists on the default branch, and you have permission to run it.

## Step 6. Review Generated Artifacts

When the run finishes, open the Actions summary and uploaded artifacts.

![Artifacts section](../../assets/getting-started/07-actions-artifacts-summary.png)

Review these Daily Backend files first:

- `reports/briefs/ko-KR/backend-daily.md`
- `reports/ops/ko-KR/backend-daily-validation-report.md`
- `reports/ops/ko-KR/backend-daily-run-summary.md`
- `reports/candidates/ko-KR/oss-contribution-opportunities.json`

If the artifact includes `reports/candidates/ko-KR/kr-oss-contribution-opportunities.json`, review that file too.

Check that the validation report is `passed`, generated sections look correct, OSS candidate counts are reasonable, and fallback output appears when no safe candidate exists.

Do not enable Discord delivery if validation fails.

## Optional GitHub Actions Variables

Skip this section for the first dry-run.

Repository Variables are optional overrides for schedule, delivery, locale, provider, timezone, and target time behavior.

Go to `Settings > Secrets and variables > Actions > Variables`.

![Variables tab and New repository variable button](../../assets/getting-started/04-variables-tab-new-variable.png)

1. Select the `Variables` tab.
2. Click `New repository variable`.
3. Enter the variable name in `Name`.
4. Enter the setting value in `Value`.
5. Click `Add variable`.

![Variable form fields](../../assets/getting-started/05-variables-add-variable-form.png)

| Name | Required | Default | First value |
| --- | --- | --- | --- |
| `CAREER_FEED_ENABLED_LOCALES` | Optional | `ko-KR` | `ko-KR` |
| `CAREER_FEED_DEFAULT_LOCALE` | Optional | `ko-KR` | `ko-KR` |
| `CAREER_FEED_SEARCH_PROVIDERS_KO_KR` | Optional | `naver,rss,github` | `naver,rss,github` |
| `CAREER_FEED_SEARCH_PROVIDERS_EN_US` | Optional | `brave,rss,github` | `brave,rss,github` |
| `CAREER_FEED_TIMEZONE` | Optional | `Asia/Seoul` | `Asia/Seoul` |
| `CAREER_FEED_BACKEND_DAILY_TIME` | Optional | `09:00` | `09:00` |
| `CAREER_FEED_NEWS_DAILY_TIME` | Optional | `09:05` | `09:05` |
| `CAREER_FEED_CAREER_WEEKLY_DAY` | Optional | `MON` | `MON` |
| `CAREER_FEED_CAREER_WEEKLY_TIME` | Optional | `09:00` | `09:00` |
| `CAREER_FEED_OSS_RECENT_DAYS` | Optional | `30` | `30` |
| `CAREER_FEED_SCHEDULE_ENABLED` | Optional | `false` | `true` |
| `CAREER_FEED_DISCORD_DELIVERY_ENABLED` | Optional | `false` | `false` |

If you create `CAREER_FEED_DISCORD_DELIVERY_ENABLED` later, keep it `false` until artifact review passes.

Use `HH:MM` for time, `MON` through `SUN` for weekdays, and IANA timezone names such as `Asia/Seoul`.

The first fork setup uses the default `ko-KR` locale without setting `CAREER_FEED_ENABLED_LOCALES`.
To test the `en-US` v0.2 foundation later, set `CAREER_FEED_ENABLED_LOCALES=ko-KR,en-US` and review artifacts before enabling delivery.

Set `CAREER_FEED_SCHEDULE_ENABLED=true` only when you want recurring scheduled generation. Manual `workflow_dispatch` runs work even when scheduled generation is disabled.

## Step 7. Enable Discord Delivery

Enable delivery only after dry-run review succeeds.

![Delivery variable setting](../../assets/getting-started/08-enable-discord-delivery-variable.png)

1. Add `DISCORD_WEBHOOK_CAREER_FEED` or a workflow-specific Discord webhook Secret.
2. Go to `Settings > Secrets and variables > Actions > Variables`.
3. Change `CAREER_FEED_DISCORD_DELIVERY_ENABLED` to `true`.
4. Run the Daily workflow again.
5. Use `dry_run=false` and `force_send=false`.

Use `force_send=true` only when you intentionally accept duplicate same-day delivery risk.

Discord delivery requires `dry_run=false`, delivery enabled, a Discord webhook Secret, a passing validation report, runtime gate pass, and duplicate-delivery policy pass.

Specific webhook Secrets take precedence over legacy fallbacks, and legacy fallbacks take precedence over `DISCORD_WEBHOOK_CAREER_FEED`.

## Success Checklist

- [ ] Repository forked
- [ ] GitHub Actions enabled
- [ ] `OPENAI_API_KEY` added to Secrets
- [ ] `Backend Daily Brief` run with `dry_run=true` and `force_send=false`
- [ ] Generated brief artifact reviewed
- [ ] Validation report passed
- [ ] Discord delivery enabled only after artifact review

## Troubleshooting

### Actions does not run

- Confirm GitHub Actions is enabled in the fork.
- Confirm the workflow exists on the default branch.
- Confirm manual `workflow_dispatch` is visible.

### OpenAI API key error

- Confirm `OPENAI_API_KEY` exists in Secrets.
- Confirm it was not added as a Variable.
- Do not paste the real key into issues, logs, or screenshots.

### Workflow succeeds but Discord receives nothing

1. Check whether `dry_run` was `true`.
2. Check whether `CAREER_FEED_DISCORD_DELIVERY_ENABLED` is `true`.
3. Check whether `DISCORD_WEBHOOK_CAREER_FEED` or the workflow-specific webhook Secret exists.
4. Check whether the validation report passed.
5. Check runtime gate output.
6. Check delivery lock output.

### Validation report failed

- `OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES`: the brief used a GitHub issue URL outside the safe candidate artifact.
- `OSS_ISSUE_URL_NOT_RECENT`: the brief used an issue outside the recency window.
- `OSS_FALLBACK_CONTAINS_ISSUE_URL`: fallback output included a specific GitHub issue URL when no safe candidate existed.

Review the validation report and `kr-oss-contribution-opportunities.json` before enabling delivery.

### No OSS candidates

- Check `safe_candidate_count`.
- A high `stale_issue_filtered_count` means old issues were filtered by recency.
- Fallback preparation output is normal when there are no safe candidates.

### Timezone error

- Use IANA timezone names such as `Asia/Seoul`.
- `Seoul`, `KST`, and `America/Los Angeles` are invalid.
- Check the runtime gate `reason` and `timezone` output.

## Related Documents

- [CLI Setup](cli-setup.md)
- [Fresh Fork Smoke Test](fresh-fork-smoke-test.md)
- [Usage Guide](usage.md)
- [Runtime Configuration](runtime-configuration.md)
- [Daily Backend Brief](../operations/daily-backend-brief.md)
- [OSS Candidate Policy](../policies/oss-candidate-policy.md)
- [Demo Guide](../demo.md)
- [Local Validation](../operations/local-validation.md)
