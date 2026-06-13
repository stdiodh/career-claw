# Codex for OSS Application

This document helps the maintainer prepare an honest Codex for OSS application.

## 1. Project Summary

Career Feed is an early public OSS project for fork-based GitHub Actions automation that generates backend learning, developer news, OSS candidate, and career-signal briefs.

Outputs are reviewable Markdown artifacts before optional Discord Webhook delivery.

## 2. Target Users

- Korean Java/Kotlin backend learners using the `ko-KR` default path.
- Discord study groups and mentoring groups that want reviewable daily or weekly prompts.
- English-speaking testers evaluating the `en-US` v0.2 foundation.
- Contributors improving docs, fixtures, validation, and source policy.

## 3. OSS Value

Career Feed turns scattered public learning and career signals into reproducible, reviewable workflow artifacts.

Its value is maintainability, safety, and reviewability rather than adoption metrics.

## 4. Current Default-Branch Maturity

Current support:

- `ko-KR` default supported locale.
- `en-US` foundation / experimental preset.
- Daily Backend Brief.
- Dev News Daily.
- Backend Career Site Radar for `ko-KR`.
- Mark PS progress workflow.
- Locale-specific daily webhook Secret names.
- `ko-KR` legacy webhook fallback during v0.2.x.
- First Backend Daily dry-run with only `OPENAI_API_KEY`.
- Repository Variables documented as optional overrides.
- Scheduled generation disabled by default with `CAREER_FEED_SCHEDULE_ENABLED=false`.
- Generic `DISCORD_WEBHOOK_CAREER_FEED` fallback after specific and legacy webhook Secrets.
- Optional GitHub CLI setup helper at `scripts/setup-fork.sh`.
- Validation scripts and fixtures.

Current limitations:

- `en-US` source/provider maturity is not complete.
- Provider marker modules are not a mature provider system.
- No adoption, production usage, user count, star, download, or ecosystem-critical metric is claimed.

## 5. Evidence Available In The Repo

- `.github/workflows/`
- `scripts/validate.sh`
- `scripts/check-doc-format.py`
- `tests/fixtures/`
- `configs/locales/`
- `CHANGELOG.md`
- `docs/project/release-v0.2.0.md`
- `docs/project/v0.2-compatibility.md`
- `.github/ISSUE_TEMPLATE/`
- localized docs under `docs/kr/` and `docs/en/`

## 6. Why Codex Would Help

Codex can help maintain this repository by making repetitive review work easier:

- draft and review briefing prompts
- summarize source candidates
- check docs for consistency
- propose validation fixtures
- inspect workflow changes
- help triage small issues
- review provider expansion proposals

## 7. API Credit Usage

API credits would be used for:

- maintainer-reviewed briefing generation
- source summarization
- validation report generation
- OSS candidate triage
- release workflow checks
- documentation and code review assistance
- locale/provider expansion review
- safe automation improvements

Credits would not be used for unchecked public posting, automatic external repository comments, automatic PR creation, issue assignment, or label changes.

## 8. Safety And Human Review

Safety controls:

- `dry_run=true` artifact review
- Discord delivery disabled by default
- validation before delivery
- delivery locks for daily workflows
- Secrets and Variables separation
- source policy
- issue template redaction warnings
- no automatic external repository mutation

## 9. Current Limitations

- Early project.
- No adoption metrics claimed.
- `en-US` is foundation/experimental.
- Provider abstraction is still evolving.
- Output quality depends on source quality, validation, and maintainer review.

## 10. Pre-Application Checklist

- [ ] Final validation passes.
- [ ] README and release docs distinguish the published v0.2.0 release from the prepared unpublished v0.2.1 baseline.
- [ ] No fake metrics are present.
- [ ] No secret values are present.
- [ ] `ko-KR` compatibility is documented.
- [ ] `en-US` limitations are documented.
- [ ] Provider scaffold status is clear.
- [ ] Roadmap separates patch and feature work.

## 11. Remaining Blockers

No hard blocker is known if validation passes.

Recommended follow-up before submission:

- Review application answers for overclaims.
- Confirm screenshots are redacted.
- Confirm no generated `reports/` artifacts are committed.

## 12. Suggested Application Answers

### A. Why this repository is suitable for Codex for OSS

Career Feed is an early but actively maintained fork-based GitHub Actions and Discord Webhook project for backend learning, career signals, and beginner-friendly OSS candidate review. It is suitable for Codex for OSS because it has reproducible workflows, validation artifacts, locale-aware setup, human-reviewed delivery, source policy, and safe automation boundaries. The project does not claim broad adoption or production dependency status; its value is helping maintainers and contributors improve reviewable learning and source-review workflows.

### B. How API credits would be used

API credits would support maintainer-reviewed briefing generation, source summarization, validation report generation, OSS candidate triage, release workflow checks, documentation review, provider expansion review, and safe automation improvements. Credits would not be used for unchecked public posting, automatic comments on external repositories, automatic pull requests, issue assignment, or label changes.
