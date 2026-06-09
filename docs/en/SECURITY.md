# Security Policy

> Language: [한국어](../kr/SECURITY.md) | [English](./SECURITY.md)

This security policy covers the GitHub Actions, OpenAI API, Discord Webhook, documentation, and script scope of Career Feed.

## Supported versions

Security guidance applies to the current default branch and the latest v0.1.x release line while the project is in early public development.

## Supported scope

The main operational paths are Daily Backend Brief, Korea Dev/AI News Daily, Backend Career Site Radar, and the PS progress marker workflow.

## Not in scope

Persistent servers, databases, hosted dashboards, Discord Gateway Bots, Slash Commands, user account systems, and recruiting-matching services are outside the current operating scope.

## Sensitive information

Do not place OpenAI API keys, Discord Webhook URLs, GitHub tokens, Naver API credentials, personal email addresses, or other credentials in issues, pull requests, commits, logs, or examples.

## Reporting a vulnerability or secret exposure

If private vulnerability reporting is enabled, use it. Otherwise contact the maintainer through an existing public maintainer channel without pasting secret values publicly.

## Secret handling

Secrets belong in GitHub Actions Secrets or local environment variables. Documentation should name variables such as `OPENAI_API_KEY` without showing real values.

## Discord webhook safety

Discord delivery is disabled by default. Use `dry_run=true` to review artifacts, then enable delivery only after validation output looks correct.

## GitHub Actions logs

Review logs before sharing them. Remove tokens, webhook URLs, private repository names, and personal data from excerpts.

## Automation boundaries

Career Feed must not automatically comment on external repositories, assign issues, open pull requests, or modify labels while collecting OSS candidates.

## Maintainer response

Maintainers should acknowledge credible reports, remove exposed secrets from active use, rotate affected credentials, and document any required follow-up.

## Safe handling checklist

- Revoke or rotate exposed credentials.
- Remove the secret from repository content and logs when possible.
- Verify workflows still use GitHub Secrets or environment variables.
- Re-run relevant validation after the fix.
