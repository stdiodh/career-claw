# Demo Guide

## Purpose

This document explains how to show what Career Feed produces after it runs.

The demo should help a new maintainer understand the operating path without exposing private credentials, private Discord details, or misleading product claims.

The goal is to show the real shape of the workflow output: GitHub Actions input, validation artifacts, generated Markdown briefs, and a redacted Discord message.

The demo is documentation and asset guidance only.

It does not add a web dashboard, Discord Gateway Bot, Slash Command, job matching service, or hosted application.

## Demo scope

Career Feed is not a browser UI product.

The demo should focus on GitHub Actions and Discord output instead of a dashboard walkthrough.

Prefer a redacted dry-run or mock data based output over a live run that shows real secrets.

If a live Discord delivery is shown, use a test server or a carefully redacted screenshot.

Do not show real webhook URLs, API keys, private Discord server names, private channel names, user ids, user avatars, account names, personal email, or private repository URLs.

The demo may mention that regional expansion is possible with reviewed source metadata, but it must not claim that every country or language is already supported.

The demo must not imply that Career Feed writes comments, opens pull requests, assigns issues, or changes labels in external repositories.

## What the demo should show

The recommended demo has four scenes.

1. GitHub Actions에서 `workflow_dispatch`를 실행하는 장면.
2. Actions summary 또는 validation report를 확인하는 장면.
3. artifacts 또는 `reports/`에서 생성된 briefing을 확인하는 장면.
4. Discord에 도착한 redacted briefing 예시를 확인하는 장면.

These scenes are enough to explain what happens when the project runs.

They show inputs, validation, generated output, and final delivery without pretending that there is a separate application UI.

If screenshots are not ready, keep only the asset directory README and `.gitkeep`.

assets will be added after redacted capture.

## Recommended demo flow

For a short GIF, target 60~90 seconds.

Keep the flow direct and avoid showing setup screens that contain credentials.

Start from the GitHub Actions workflow page.

Select `Daily Korea Tech Brief` or `Daily Korea Dev AI News`.

Open `Run workflow`.

Show the dry-run input or artifact-only delivery option.

Start the workflow or show a completed redacted run.

Open the Actions summary.

Open the uploaded artifact list.

Preview the generated Markdown brief.

End with a redacted Discord message that shows the briefing format.

Use short captions or callouts instead of long explanatory overlays.

Avoid zooming into browser chrome if the address bar contains private repository paths, tokens, query parameters, or user account identifiers.

## Screenshot checklist

Recommended screenshot files:

- `github-actions-dispatch-redacted.png`
- `actions-summary-redacted.png`
- `validation-report-redacted.png`
- `discord-brief-redacted.png`

Each screenshot must be reviewed before commit.

Use redacted or mock data.

Do not link a screenshot from README or this document unless the file exists in `docs/assets/demo/`.

If the image is not ready, describe the intended asset and keep the asset file absent.

## GIF checklist

Recommended GIF file:

- `career-feed-demo.gif`

Keep the GIF 60~90 seconds or shorter.

Keep the width at 1280px or lower when possible.

Do not show secrets, webhook URLs, private channels, usernames, avatars, user ids, or private repository URLs.

Keep captions and callouts short.

Check the file size before committing.

If the GIF is too large, prefer static screenshots in the README and put the video elsewhere.

When storing a GIF in the repository, keep it as small as practical.

A good target is 10MB or less.

## Video recording guidance

Do not commit large mp4 files directly to the repository by default.

If a longer video is needed, use a GitHub Release asset, PR attachment, project page, or external video link.

Prefer GIF or static screenshots in README because they are easier to review in a documentation PR.

Do not record real secret entry.

Avoid showing the GitHub Secrets screen.

Even secret names can provide operational hints, so prefer mock screens or written documentation for that part.

Do not show browser address bars that contain tokens, query parameters, private repository paths, or account-specific URLs.

Do not include Discord direct messages or private server navigation.

## Redaction rules

Discord webhook URLs must not be visible.

OpenAI API keys must not be visible.

Naver credentials must not be visible.

Discord server identifiers, channel identifiers, user identifiers, usernames, and avatars must not be visible.

Personal direct messages, private email addresses, and account names must not be visible.

Private repository URLs must not be visible.

Browser address bars must not show token or query parameter values.

Actions logs must not be captured if they contain secret-like strings.

If a screenshot needs redaction, apply the redaction before adding it to `docs/assets/demo/`.

Use solid blocks or cropping for redaction rather than blur when the text might still be recoverable.

## Example demo storyboard

| Time | Scene | What to show | Caption |
| --- | --- | --- | --- |
| 0-10s | GitHub Actions | Select Daily Backend Brief workflow | Run the workflow manually in dry-run mode |
| 10-25s | Workflow inputs | Show dry-run option | Start with dry-run before Discord delivery |
| 25-45s | Actions summary | Show validation report | Review generated artifacts and validation output |
| 45-65s | Report preview | Show generated brief artifact | Check the brief before sending |
| 65-90s | Discord | Show redacted brief message | A reviewed brief can be delivered to Discord |

The same structure can be reused for Korea Dev/AI News Daily.

For Backend Career Site Radar, replace the dry-run scene with `send_to_discord=false`.

For Mark PS Solved, show the input form and the resulting `data/ps-progress.json` change only if the branch and account details are safe to reveal.

## Example captions

Use short captions that explain the operating model.

- Run the workflow manually.
- Start with dry-run.
- Review validation artifacts.
- Check the generated brief.
- Send only after review.
- Discord receives the reviewed briefing.
- PS progress is updated by a manual workflow.

Avoid captions that imply a hosted dashboard, autonomous bot, or hiring recommendation engine.

## What not to show

Do not show real secret values.

Do not show webhook URLs.

Do not show private Discord server names, channel names, usernames, avatars, or user ids.

Do not show private repository URLs or private organization names.

Do not show Discord direct messages.

Do not show fake adoption metrics, stars, forks, active users, downloads, or customer counts.

Do not show an automated comment or PR being created in an external repository.

Do not show a Slash Command flow.

Do not show a web dashboard unless the project actually adds one in the future.

Do not include a screenshot that still has recoverable sensitive text under blur.

## Asset naming convention

Use the `docs/assets/demo/` directory for demo assets.

Recommended paths:

- `docs/assets/demo/github-actions-dispatch-redacted.png`
- `docs/assets/demo/actions-summary-redacted.png`
- `docs/assets/demo/validation-report-redacted.png`
- `docs/assets/demo/discord-brief-redacted.png`
- `docs/assets/demo/career-feed-demo.gif`

Only link files that actually exist.

If assets are not ready, keep `.gitkeep` and document that assets will be added after redacted capture.

Do not create placeholder image files.

## Keeping demo assets up to date

Review demo assets when workflow names, inputs, artifact names, or Discord message format changes.

Remove or replace screenshots that show outdated UI labels.

Keep screenshots focused on the smallest safe area that explains the step.

After adding or replacing an asset, verify the file exists.

```bash
find docs/assets/demo -maxdepth 1 -type f -print
```

If an image or GIF is added, check file size.

```bash
du -h docs/assets/demo/*
```

Before a PR is merged, leave a review note confirming that sensitive information was checked manually.

## Related documents

- [README.md](../README.md)
- [Usage guide](usage.md)
- [Daily Backend Brief](daily-backend-brief.md)
- [Korea Dev/AI News Daily](daily-news-ops.md)
- [Backend Career Site Radar](career-site-radar.md)
- [Local validation guide](local-validation.md)
- [Security policy](../SECURITY.md)
