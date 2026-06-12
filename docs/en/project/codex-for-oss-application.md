# Codex for OSS Application

> Language: [한국어](../../kr/project/codex-for-oss-application.md) | [English](./codex-for-oss-application.md)

This document gives maintainers concise and honest material for a Career Feed application to the OpenAI Codex for Open Source program.

## 1. Project summary

Career Feed is an Early Public OSS project for fork-based GitHub Actions automation.

It uses the OpenAI API and Discord Webhook delivery to generate and validate backend learning, developer news, OSS candidate, and career-signal Markdown artifacts.

Discord delivery is optional. The default operating path is dry-run artifact review.

## 2. Why it matters to the backend ecosystem

This project is not a production backend dependency, framework, database, or hosted SaaS.

Its value is in the onboarding layer of the backend ecosystem.

It helps backend learners, junior developers, Discord study groups, and mentors produce reviewable study prompts, news summaries, and OSS contribution preparation material.

## 3. Current evidence in the prepared v0.2.1 baseline

Evidence available in the current default branch after the prepared v0.2.1 docs/onboarding updates includes:

- `ko-KR` as the default supported locale
- `en-US` as an experimental foundation
- Daily Backend Brief, Dev News Daily, Backend Career Site Radar, and PS progress workflows
- locale-aware artifact paths
- locale-specific Discord webhook Secret names
- first Backend Daily dry-run with only `OPENAI_API_KEY`
- repository Variables documented as optional overrides
- Discord delivery disabled by default
- scheduled generation disabled by default with `CAREER_FEED_SCHEDULE_ENABLED=false`
- manual `workflow_dispatch` still available while schedule is disabled
- generic `DISCORD_WEBHOOK_CAREER_FEED` fallback after specific and legacy webhook Secrets
- optional `scripts/setup-fork.sh` GitHub CLI setup helper
- dry-run artifact review
- generated brief validation before delivery
- validation scripts and fixtures
- source policy, issue templates, and release checklist

## 4. Honest limitations

Career Feed is still early public OSS.

It does not claim broad adoption, downloads, stars, active users, organization usage, or production usage.

Usage metrics are not yet claimed.

`en-US` is an experimental foundation, not mature global support.

Output quality depends on source quality, prompts, validation, and maintainer review.

Generated output does not replace career decisions, hiring decisions, or OSS maintainer judgment.

## 5. How API credits would be used

API credits would be used for maintainer-reviewable drafts and summaries.

- Daily Backend Brief generation
- developer and AI news candidate summaries
- Spring Boot, JVM, Kotlin, and backend study topic prioritization
- OSS candidate notes
- validation report and release checklist review
- documentation consistency review
- locale and provider expansion review

## 6. Automation boundaries and safety

Codex/OpenAI output is reviewable draft material, not unchecked public action.

The project does not auto-comment on external repositories.

The project does not create automatic pull requests in external repositories.

The project does not auto-assign external issues.

The project does not auto-label external issues.

Discord delivery is constrained by dry-run behavior, validation, delivery enabled settings, and delivery locks.

Secrets, webhook URLs, API keys, and private identifiers stay out of docs and issues. They belong in GitHub Secrets or environment variables.

## 7. Copy-ready short application text

The text below is under 500 characters.

```text
Career Feed is an Early Public OSS, fork-based GitHub Actions automation project. Its latest published release is v0.2.0, with prepared unpublished v0.2.1 docs/onboarding updates on the default branch. It is not a production backend dependency, framework, database, or hosted SaaS. Usage metrics are not yet claimed.
```

## 8. Copy-ready API credit usage text

The text below is under 500 characters.

```text
API credits would support maintainer-reviewable drafts for backend briefs, dev/AI news summaries, OSS candidate notes, validation reports, and documentation review. Credits would not be used for unchecked public action, external auto-comments, auto-PRs, issue assignment, or label changes; Discord delivery stays gated by dry-run review and validation.
```
