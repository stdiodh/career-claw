# Usage Guide

> Language: [한국어](../../kr/getting-started/usage.md) | [English](./usage.md)

## Overview

Career Feed is operated through GitHub Actions workflows. It is not a desktop app, hosted dashboard, Discord Gateway Bot, or Slash Command service.

The normal loop is small:

1. Run local validation.
2. Open GitHub Actions.
3. Choose the workflow.
4. Run dry-run or artifact-only mode.
5. Review summary and artifacts.
6. Enable Discord delivery only after review.
7. Update PS progress with `Mark PS Solved` when needed.

Generated `reports/` files are runtime artifacts and are not normally committed.

## First-time fork setup

If this is your first fork run, start with [Fork Setup Guide](fork-setup.md).

Use this guide after setup when you need routine operation details.

## Who should use this

Use this guide if you maintain a Career Feed fork, run workflows for a study group, or review workflow behavior.

Career Feed helps backend learners, junior developers, mentors, and study groups maintain repeatable briefs. It does not replace human review.

## Before you start

Confirm that you are operating the intended repository and use a test Discord channel for first live delivery.

Never paste real API keys, webhook URLs, credentials, private channel names, or personal identifiers into public issues, pull requests, screenshots, or docs.

## Repository setup

```bash
git clone https://github.com/stdiodh/career-feed.git
cd career-feed
./scripts/validate.sh
```

If you operate a fork, enable GitHub Actions before relying on schedules.

## Configuration references

First-time setup steps live in [Fork Setup Guide](fork-setup.md). Supported Secrets and Variables live in [Runtime Configuration](runtime-configuration.md).

GitHub cron cannot read repository Variables. Workflows wake up periodically and run `scripts/should-run-now.py` to decide whether to continue.

Manual `workflow_dispatch` runs are not blocked by the runtime time window.

## Running local validation

Run local validation before changing docs, prompts, workflows, or scripts.

```bash
./scripts/validate.sh
```

Documentation-only checks:

```bash
python3 scripts/check-doc-format.py
git diff --check
```

## Running a workflow manually

Open `Actions`, select the workflow, click `Run workflow`, confirm the branch and inputs, then start the run.

| Operating path | GitHub Actions workflow | Main output |
| --- | --- | --- |
| Daily Backend Brief | Daily Korea Tech Brief | `reports/briefs/kr-tech-daily.md` |
| Korea Dev/AI News Daily | Daily Korea Dev AI News | `reports/briefs/kr-tech-news-daily.md` |
| Backend Career Site Radar | Backend Career Site Radar | `reports/briefs/kr-backend-career-weekly.md` |
| Mark PS Solved | Mark PS Solved | `data/ps-progress.json` |

## Recommended first run: dry-run

Run Daily Backend Brief with `dry_run=true` and `force_send=false`.

Check generated brief, candidate JSON files, validation report, and run summary.

Run Korea Dev/AI News Daily the same way. Sparse or empty news days can still be valid.

For Backend Career Site Radar, use `send_to_discord=false` to inspect artifacts first.

For Mark PS Solved, check local status before running if you only need to inspect progress:

```bash
python3 scripts/update-ps-progress.py --status
```

## Reading validation artifacts

Open the completed Actions run, inspect the summary, then download or open the uploaded artifact.

For Daily Backend, inspect the generated brief, candidate JSON, `backend-daily-validation-report.md`, and `backend-daily-run-summary.md`.

For News Daily, inspect shortlist, token budget, quality report, validation report, generated brief, and run summary.

For Site Radar, inspect `weekly-career-site-radar.json` and `kr-backend-career-weekly.md`.

## Sending to Discord

Set `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true` only after a reviewed dry-run.

Daily workflows require `dry_run=false`. Use `force_send=true` only when intentionally bypassing same-day delivery lock.

Backend Career Site Radar uses `send_to_discord=true`.

Delivery is blocked by dry-run, manual delivery option, global delivery flag, missing webhook Secret, or validation failure.

## Marking PS progress

Career Feed does not crawl Programmers submissions.

Run `Mark PS Solved` with a `problem_id` such as `programmers-42577` and optional note.

The workflow updates `data/ps-progress.json` and commits only when a change is detected.

## Common operating modes

| Mode | When to use | Recommended inputs |
| --- | --- | --- |
| Local validation | Before PRs or script changes | `./scripts/validate.sh` |
| Daily Backend dry-run | First backend test | `dry_run=true`, `force_send=false` |
| News Daily dry-run | First news test | `dry_run=true`, `force_send=false` |
| Site Radar artifact-only | Review before sending | `send_to_discord=false` |
| Reviewed Discord send | Send after validation | Delivery enabled |
| PS progress update | Record a solved problem | `problem_id` |

## What to check after a run

- Run status is successful.
- Validation report passed.
- Generated links are relevant and safe.
- Discord delivery state matches the chosen mode.
- No secret-like strings appear in logs or screenshots.

## Troubleshooting

- Missing `Run workflow`: check Actions enablement and default branch.
- Missing Discord message: check `dry_run`, delivery flag, webhook Secret, validation report, runtime gate, and delivery lock.
- Validation failure: inspect the validation report before rerunning.
- Time mismatch: check timezone and target time Variables.

## Safety checklist

- Do not commit `reports/` unless intentionally adding fixtures or examples.
- Do not expose webhook URLs, API keys, private Discord details, or personal identifiers.
- Do not add automation that comments, opens PRs, assigns issues, or changes labels on external repositories.

## Related documents

- [Documentation Index](../README.md)
- [Runtime Configuration](runtime-configuration.md)
- [Demo Guide](../demo.md)
- [Daily Backend Brief](../operations/daily-backend-brief.md)
- [Korea Dev/AI News Daily](../operations/daily-news-ops.md)
- [Backend Career Site Radar](../operations/career-site-radar.md)
- [Local Validation](../operations/local-validation.md)
- [Operations Guide](../operations/operations.md)
- [Security Policy](../SECURITY.md)
