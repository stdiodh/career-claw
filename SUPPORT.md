# Support

Career Feed is an early open-source automation project operated through GitHub Actions, generated artifacts, validation reports, and optional Discord webhook delivery.

It is not a hosted service, personal career counseling service, or real-time support channel.

## Where to ask

Use GitHub Issues unless GitHub Discussions are enabled for the repository.

Use the issue template that matches the request:

- bug report for workflow or validation failures
- docs improvement for confusing setup or documentation gaps
- source suggestion for new public sources
- OSS candidate suggestion for repository or issue candidates
- feature request for new workflow or configuration ideas

## Before opening an issue

- Check [Fork Setup Guide](docs/fork-setup.md).
- Check [Usage Guide](docs/usage.md).
- Check [Runtime Configuration](docs/runtime-configuration.md).
- Check the workflow run logs.
- Check the validation report artifact.
- Confirm whether the run was `dry_run=true`.
- Confirm the value of `CAREER_FEED_DISCORD_DELIVERY_ENABLED`.

## Do not include secrets

Do not paste any of the following into public issues, PRs, comments, screenshots, or logs:

- OpenAI API key
- Discord webhook URL
- GitHub token
- Naver API credential
- private Discord server or channel detail
- private repository URL
- personal identifiers

If a secret was exposed, rotate it immediately and follow [Security Policy](SECURITY.md).

## What support can cover

- fork setup questions
- GitHub Actions workflow behavior
- dry-run and artifact review
- validation report errors
- runtime Variables and scheduling behavior
- documentation gaps
- source and OSS candidate policy questions

## What support cannot guarantee

- perfect news or career source accuracy
- individual career decisions
- job application outcomes
- real-time GitHub Actions scheduling
- automatic claiming or modification of external GitHub issues

Users should review generated source links, candidate artifacts, and Discord output before acting on a brief.
