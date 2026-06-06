# Demo Assets

## Purpose

This directory stores redacted screenshots and GIF files used by the README and demo documentation.

The assets should show how Career Feed is operated through GitHub Actions, validation artifacts, generated briefs, and Discord Webhook delivery.

They should not make the project look like a web dashboard, hosted service, Gateway Bot, Slash Command product, or hiring recommendation platform.

If no reviewed assets are ready, keep only `.gitkeep`.

assets will be added after redacted capture.

## Allowed assets

Allowed assets include redacted GitHub Actions screenshots, redacted Actions summary screenshots, redacted validation report screenshots, redacted generated briefing screenshots, and redacted Discord briefing screenshots.

Mock data based screenshots are allowed when they accurately represent the operating flow.

Short GIF demos are allowed when they are small enough for repository review.

Actual production screenshots are allowed only after sensitive information has been removed.

Placeholder image files are not allowed.

Do not add an image just so a link can exist.

## Preferred formats

Prefer PNG or WebP for static screenshots.

Prefer GIF for short motion demos that need to appear inline in Markdown.

Avoid committing mp4 files directly to the repository.

For longer video, use a GitHub Release asset, PR attachment, project page, or external video link.

Do not store raw screen recording files here.

## Size guidance

Keep static screenshots as small as practical.

Aim for 1MB or less per PNG or WebP when possible.

Keep GIF demos short.

Aim for 10MB or less when a GIF is committed to the repository.

If a GIF is too large, use static screenshots in README and link to an external video or Release asset instead.

Crop screenshots to the relevant safe area before committing.

## Redaction requirements

Do not expose Discord webhook URLs.

Do not expose OpenAI API keys.

Do not expose Naver credentials.

Do not expose Discord server names, channel names, usernames, avatars, user ids, or private invite details.

Do not expose personal direct messages, private email addresses, account names, or private repository URLs.

Do not expose browser URLs that include tokens or query parameters.

Do not capture Actions logs when secret-like strings are visible.

Use solid redaction blocks or crop sensitive areas.

Do not rely on blur if text may still be recoverable.

## File naming

Use descriptive lowercase filenames.

Recommended names:

- `github-actions-dispatch-redacted.png`
- `actions-summary-redacted.png`
- `validation-report-redacted.png`
- `discord-brief-redacted.png`
- `career-feed-demo.gif`

Keep files directly under `docs/assets/demo/`.

Do not create nested folders unless a future documentation change needs them.

## Review checklist

- The file exists in `docs/assets/demo/`.
- README or demo docs link only to files that exist.
- The asset uses redacted or mock data.
- No webhook, token, API key, credential, private URL, or personal identifier is visible.
- Discord server, channel, user, and avatar details are hidden.
- File size is reasonable for repository review.
- The screenshot reflects the current workflow names, inputs, artifacts, and message shape.
- A reviewer can understand what the asset shows without extra private context.

## Updating assets

Update assets when workflow names, workflow inputs, artifact names, validation reports, or Discord message format changes.

Delete obsolete assets instead of keeping multiple stale versions.

After adding or replacing images, run:

```bash
find docs/assets/demo -maxdepth 1 -type f -print
du -h docs/assets/demo/*
```

If only `.gitkeep` exists, the size command is optional.

Document in the PR whether image or GIF assets were added.

If image or GIF assets were added, document that redaction was manually checked.
