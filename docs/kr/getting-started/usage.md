# Usage Guide

> Language: [한국어](./usage.md) | [English](../../en/getting-started/usage.md)

## Overview

Career Feed is not an installed desktop app, hosted dashboard, Discord Gateway Bot, or Slash Command service.

It is operated through GitHub Actions workflows that generate reviewable Markdown briefs, upload validation artifacts, and optionally send the reviewed result to Discord through Webhook delivery.

The usual operating loop is intentionally small.

1. Fork or clone the repository.
2. Run local validation with `./scripts/validate.sh`.
3. Open the GitHub Actions tab.
4. Select the workflow you want to test.
5. Run the workflow manually in dry-run or artifact-only mode.
6. Review the Actions summary and uploaded artifacts.
7. Enable Discord delivery only after the generated brief looks correct.
8. Update Programmers PS progress with `Mark PS Solved` when needed.

The output is a Markdown briefing and, when delivery is enabled, a Discord message rendered from that briefing.

`reports/` files are generated artifacts and are not normally committed.

## First-time fork setup

If this is your first time running Career Feed from a fork, start with
[Fork Setup Guide](fork-setup.md).

That guide walks through GitHub Secrets, GitHub Actions Variables, dry-run execution,
artifact review, validation troubleshooting, and Discord delivery activation with GitHub UI screenshots where available.

Use this Usage Guide after the first setup when you want to understand routine operation.

## Who should use this

Use this guide if you maintain a Career Feed fork, run the workflows for a study group, or want to understand what happens after pressing `Run workflow`.

It is also useful for reviewers who need to verify that a documentation or workflow change did not alter the operating model.

Career Feed is aimed at backend learners, junior backend developers, mentors, and study groups that want a repeatable daily or weekly briefing workflow.

It does not replace human review.

The maintainer should still read validation reports, inspect generated briefs, and decide whether Discord delivery is appropriate.

## Before you start

Confirm that the repository is the Career Feed repository you intend to operate.

Do not test against a private Discord channel that contains personal messages or private server names unless the output will never be published.

Use a test Discord server or a private test channel for the first live delivery.

Never paste real API keys, webhook URLs, or credentials into issue comments, pull requests, screenshots, or documents.

The first run should be a dry-run or artifact-only run.

For daily workflows, dry-run generates and validates artifacts without sending to Discord.

For Backend Career Site Radar, set `send_to_discord` to `false` when you want to inspect the artifact first.

For Mark PS Solved, confirm the target problem id before running because the workflow commits `data/ps-progress.json` when a change is detected.

## Repository setup

Start from a fork or clone of the repository.

```bash
git clone https://github.com/stdiodh/career-feed.git
cd career-feed
./scripts/validate.sh
```

If you operate a fork, enable GitHub Actions for that fork before relying on scheduled runs.

GitHub scheduled workflows run from the default branch.

If you are testing workflow changes in a pull request branch, prefer manual `workflow_dispatch` runs and artifact review.

Keep `reports/` out of commits unless a specific fixture or example file is intentionally added through a review.

## Configuration references

First-time setup steps live in [Fork Setup Guide](fork-setup.md).
Supported Secrets and Variables live in [Runtime Configuration](runtime-configuration.md).

GitHub Actions cron cannot read repository Variables directly.

The workflows therefore wake up periodically and run `scripts/should-run-now.py` near the beginning of the job.

If the configured local time does not match the current runtime window, the expensive generation and send steps are skipped successfully.

Manual `workflow_dispatch` runs are not blocked by `CAREER_FEED_SCHEDULE_ENABLED` or the runtime time window.

## Running local validation

Run local validation before changing documentation, workflow policy, prompts, or scripts.

```bash
./scripts/validate.sh
```

For documentation-only checks, the format checker is also useful.

```bash
python3 scripts/check-doc-format.py
git diff --check
```

Local validation may generate files under `reports/`.

Those generated files are operating artifacts, not source files.

Do not commit them unless a task explicitly asks for a fixture or public example.

If validation fails, read the first failing message and fix that cause first.

Avoid changing unrelated workflow or script behavior while working on usage documentation.

## Running a workflow manually

Open the repository on GitHub and go to `Actions`.

Select the workflow that matches the operating path you want to test.

Use `Run workflow` from the workflow page.

Confirm the branch, input values, and delivery options before starting the run.

Daily workflows can run on schedule, but manual runs are safer for first verification because you can choose dry-run inputs and inspect artifacts immediately.

For the first Backend Daily dry-run, configure only the `OPENAI_API_KEY` Secret and leave repository Variables unset unless you intentionally need an override.

The active operating workflows are listed below.

| Operating path | GitHub Actions workflow | Main output |
| --- | --- | --- |
| Daily Backend Brief | Backend Daily Brief | `reports/briefs/ko-KR/backend-daily.md` |
| Dev News Daily | Dev News Daily | `reports/briefs/ko-KR/news-daily.md` |
| Backend Career Site Radar | Backend Career Site Radar | `reports/briefs/ko-KR/backend-career-weekly.md` |
| Mark PS Solved | Mark PS Solved | `data/ps-progress.json` |

## Recommended first run: dry-run

Start with dry-run or artifact-only mode so you can inspect the generated content before Discord delivery.

For Daily Backend Brief, run `Backend Daily Brief` with `dry_run=true` and `force_send=false`.

Check the generated brief, candidate JSON files, validation report, and run summary.
In the validation report, confirm that OSS issue URLs in the Markdown came from
`kr-oss-contribution-opportunities.json` safe candidates and that fallback days do not include GitHub issue URLs.

Discord delivery and delivery lock creation should not happen in this mode.

For Dev News Daily, run `Dev News Daily` with `dry_run=true` and `force_send=false`.

Check the shortlist, token budget, quality report, validation report, generated brief, and run summary.

Sparse or empty news days can still be valid when the policy is satisfied.

For Backend Career Site Radar, run `Backend Career Site Radar` with `send_to_discord=false`.

Check the rendered site radar artifact before enabling delivery.

For Mark PS Solved, there is no dry-run input in the workflow.

Use local status checks before running the workflow if you only want to inspect progress.

```bash
python3 scripts/update-ps-progress.py --status
```

## Reading validation artifacts

Open the completed Actions run and inspect the summary first.

Then download or open the uploaded artifact for the run.

For Daily Backend Brief, the most important files are the generated brief, candidate JSON files, `backend-daily-validation-report.md`, and `backend-daily-run-summary.md`.

For Dev News Daily, check `reports/briefs/ko-KR/news-daily.md`, `reports/candidates/ko-KR/news-shortlist.json`, `reports/ops/ko-KR/news-daily-token-budget.json`, `reports/ops/ko-KR/news-daily-quality-report.json`, `reports/ops/ko-KR/news-daily-validation-report.md`, and `reports/ops/ko-KR/news-daily-run-summary.md`.

For Backend Career Site Radar, check `reports/candidates/ko-KR/weekly-career-site-radar.json` and `reports/briefs/ko-KR/backend-career-weekly.md`.

Artifacts should show what was generated, what was skipped, whether Discord delivery was attempted, and whether validation passed.

If a validation report fails, do not send the brief to Discord.

Fix the underlying issue or rerun after the source data is acceptable.

## Sending to Discord

After a dry-run looks correct, run the workflow with Discord delivery enabled.

Set `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true` before expecting any workflow to send to Discord.

For Daily Backend Brief and Dev News Daily, set `dry_run=false`.

Use `force_send=true` only when you intentionally want to send despite an existing delivery lock.

For normal manual delivery after a reviewed dry-run, `force_send=true` is often used for a one-time verified send.

For repeated same-day checks, keep `force_send=false` so the delivery lock can prevent duplicate delivery.

For Backend Career Site Radar, set `send_to_discord=true`.

Delivery is blocked in this priority order: `dry_run=true`, manual delivery option set to false, `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`, then missing webhook secret. Webhook resolution uses the specific Secret first, then a legacy fallback, then `DISCORD_WEBHOOK_CAREER_FEED`.

The Discord message should look like a briefing, not a chat bot conversation.

It should include the generated sections, source links where applicable, and concise Korean guidance for the intended audience.

If Discord delivery fails, inspect the Actions log for a missing secret message, send script error, or rate-limit retry failure.

Do not publish the log if it contains secret-like strings.

## Marking PS progress

Career Feed does not crawl Programmers submissions.

The PS routine uses static curriculum config and `data/ps-progress.json`.

When you solve a problem and want the next daily routine to reflect that progress, run `Mark PS Solved`.

Required input:

- `problem_id`: Programmers problem id in the repository format, such as `programmers-42577`.

Optional input:

- `note`: short solve note for maintainers or study context.

The workflow updates `data/ps-progress.json`, commits it, and pushes the change when the progress file changed.

If the problem was already marked solved, the workflow may complete without a new commit.

## Common operating modes

| Mode | When to use | Recommended inputs |
| --- | --- | --- |
| Local validation | Before opening a PR or changing docs/scripts | `./scripts/validate.sh` |
| Daily Backend dry-run | First daily backend test or content review | `dry_run=true`, `force_send=false` |
| News Daily dry-run | First news test or sparse/empty policy review | `dry_run=true`, `force_send=false` |
| Site Radar artifact-only | Review static site radar output before sending | `send_to_discord=false` |
| Reviewed Discord send | Send after artifacts and validation pass | Delivery enabled for the selected workflow |
| PS progress update | Record a solved Programmers problem | `problem_id` and optional `note` |

These modes are intentionally narrow.

They do not start a server, open a dashboard, create Discord slash commands, or change external repositories.

## What to check after a run

Check the run status in GitHub Actions.

Read the Actions summary and uploaded artifacts.

Confirm that validation passed before using the generated brief.

Confirm that generated links are relevant and safe for the target section.

Confirm that dry-run did not send to Discord.

Confirm that a real send delivered exactly once to the intended test or operating channel.

Confirm that delivery lock behavior matches the selected inputs.

Confirm that `reports/` generated files are not staged for commit.

For PS progress updates, confirm that only the expected progress file changed.

## Troubleshooting

If a secret is missing, the relevant workflow step should print a clear missing secret message.

Register the secret in GitHub Actions settings and rerun the workflow.

If a Discord message does not arrive, confirm that the workflow was not run in dry-run or artifact-only mode.

Then check `CAREER_FEED_DISCORD_DELIVERY_ENABLED`, the webhook secret name, delivery lock status, and send step outcome.

If only a dry-run artifact exists and nothing was delivered, that is expected for `dry_run=true`, `send_to_discord=false`, or `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`.

Review the artifact, then run again with delivery enabled when the content is acceptable.

If it is a sparse or empty news day, check the News Daily validation report and quality report.

Sparse or empty output can be a successful run when the brief says why there were too few qualifying items and follows the policy.

If a validation report fails, do not force delivery.

Use the reported file path, section name, or validation error to fix the source, prompt, fixture, or generated content.

For OSS URL validation failures such as `OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES`,
`OSS_ISSUE_URL_NOT_RECENT`, or `OSS_FALLBACK_CONTAINS_ISSUE_URL`, check
[Fork Setup Guide](fork-setup.md) and [OSS Candidate Policy](../policies/oss-candidate-policy.md).

If PS progress commit fails, check whether GitHub Actions has write permission, whether the branch is protected, and whether `data/ps-progress.json` actually changed.

If a workflow only runs manually and not on schedule, confirm that the workflow has a schedule, is enabled on the default branch, and has not been disabled by repository inactivity.

Backend Career Site Radar can run manually or through its weekly runtime gate.

Mark PS Solved is a manual operating path by design.

## Safety checklist

- Do not expose real webhook URLs in logs, issues, PRs, screenshots, or documents.
- Do not expose API keys, tokens, Naver credentials, or Discord webhook values.
- Redact Discord server names, channel names, usernames, avatars, user ids, and private URLs in screenshots.
- Do not add automatic comments, PRs, assigns, or label changes to external repositories.
- Do not treat workflow success as enough; inspect the validation report and generated brief.
- Start with dry-run or artifact-only mode for a new setup.
- Use a test Discord channel before operating a public or shared channel.
- Keep generated `reports/` artifacts out of normal commits.
- Do not make Career Feed look like a web dashboard, hosted matching service, Gateway Bot, or Slash Command product.

## Related documents

- [Documentation Index](../README.md)
- [Runtime Configuration](runtime-configuration.md)
- [Demo guide](../demo.md)
- [Daily Backend Brief](../operations/daily-backend-brief.md)
- [Dev News Daily](../operations/daily-news-ops.md)
- [Backend Career Site Radar](../operations/career-site-radar.md)
- [Local validation guide](../operations/local-validation.md)
- [Operations guide](../operations/operations.md)
- [Security policy](../SECURITY.md)
