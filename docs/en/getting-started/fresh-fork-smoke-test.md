# Fresh Fork Smoke Test

> Language: [한국어](../../kr/getting-started/fresh-fork-smoke-test.md) | [English](./fresh-fork-smoke-test.md)

This checklist helps a first-time Career Feed fork user run `Backend Daily Brief` without editing workflow YAML.

The goal is to review artifacts and validation output before any Discord delivery.

## Prerequisites

Prepare:

- GitHub account
- forked Career Feed repository
- `OPENAI_API_KEY`
- optional Discord webhook URL for later delivery
- optional Naver credentials for later enrichment
- optional Brave Search credentials for later enrichment

Do not place real API keys, webhook URLs, tokens, or private identifiers in docs, issues, pull requests, commits, Actions logs, or screenshots.

## Required first run settings

Use one repository Secret and the safe workflow inputs for the first smoke test.

Repository Secret:

- `OPENAI_API_KEY`

Repository Variables:

- none required

Workflow inputs:

- `dry_run=true` (default)
- `force_send=false`

A `dry_run=true` run should not send Discord messages.

The Discord webhook Secret is needed later only when you enable delivery. Naver and Brave credentials are optional enrichment. They are not required for the first dry-run artifact review.

## Backend Daily Brief smoke test

1. Open `Settings > Secrets and variables > Actions > Secrets` in the fork.
2. Add `OPENAI_API_KEY` as a repository Secret.
3. Do not add repository Variables for the first smoke test.
4. Open the repository `Actions` tab.
5. Select the `Backend Daily Brief` workflow.
6. Click `Run workflow`.
7. Confirm the branch is the default branch.
8. Keep `dry_run` as `true`.
9. Keep `force_send` as `false`.
10. Click `Run workflow`.
11. After the run finishes, open the Actions summary and uploaded artifact.

GitHub may display boolean input descriptions as checkbox labels. The first boolean input is `dry_run`; the second boolean input is `force_send`.

## Expected artifacts

Review these files first.

- `reports/briefs/ko-KR/backend-daily.md`
- `reports/ops/ko-KR/backend-daily-validation-report.md`
- `reports/ops/ko-KR/backend-daily-run-summary.md`
- `reports/candidates/ko-KR/oss-contribution-opportunities.json`

If the current `ko-KR` v0.2.0 workflow and validation report also use `reports/candidates/ko-KR/kr-oss-contribution-opportunities.json`, review that file too.

## What success means

Smoke-test success means:

- the workflow run completes
- `ko-KR` artifacts are created
- the generated brief exists at `reports/briefs/ko-KR/backend-daily.md`
- the validation report passes
- the run summary shows `dry_run=true` and `force_send=false`
- no Discord message is sent

Rich OSS candidates or rich source data are not required for success.

Some days may produce zero safe OSS candidates and use fallback preparation output.

If Naver or Brave credentials are missing, some providers may be skipped and artifacts may be sparse. That is acceptable for the first dry-run.

## When validation fails

Do not enable Discord delivery when validation fails.

1. Open `reports/ops/ko-KR/backend-daily-validation-report.md` first.
2. Check the error code and failed section.
3. Check whether generated GitHub issue URLs exist in the safe candidate artifact.
4. Check whether stale or unsafe issue URLs were included.
5. If the candidate artifact is empty, check whether fallback output includes a specific GitHub issue URL.
6. Check that no secret value or webhook URL appears in logs or artifacts.
7. Before rerunning without changes, separate source scarcity, API failure, and validation-rule failure.

Do not run with `dry_run=false` while validation is failing.

## Before enabling Discord delivery

Check these items before enabling Discord delivery.

- The dry-run artifact is suitable to send as a reviewed draft.
- The validation report passed.
- The run summary showed `dry_run=true` and `force_send=false`.
- `DISCORD_WEBHOOK_CAREER_FEED` or a workflow-specific Discord webhook Secret exists.
- You have a clear reason to set `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`.
- Keep `force_send=false` for the first live send.
- Do not use `force_send=true` unless you understand same-day duplicate delivery risk.
- Set `CAREER_FEED_SCHEDULE_ENABLED=true` only when you want recurring scheduled generation.

Expect actual delivery only when `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`, `dry_run=false`, a Discord webhook Secret exists, validation passes, and delivery lock conditions allow sending.

## Related documents

- [Fork Setup Guide](./fork-setup.md)
- [Runtime Configuration](./runtime-configuration.md)
- [Webhook Setup](./webhook-setup.md)
- [Usage Guide](./usage.md)
