# Release Checklist

This shared checklist is for v0.2.x patch planning and later release preparation.

Do not create a tag or publish a GitHub Release until the maintainer intentionally does so.

## Release Baseline

- Current release baseline: `v0.2.1`.
- Current default supported locale: `ko-KR`.
- Current experimental foundation locale: `en-US`.
- Current operating model: fork-based GitHub Actions, dry-run artifacts, validation, optional Discord Webhook delivery.
- Current onboarding model: first Backend Daily dry-run needs only `OPENAI_API_KEY`; repository Variables are optional overrides.

## Pre-Release Checks

- [ ] `CHANGELOG.md` describes the target release accurately.
- [ ] README status and release links match the real tag state.
- [ ] `docs/project/release-v0.2.0.md` remains accurate for the v0.2 baseline.
- [ ] `docs/project/v0.2-compatibility.md` covers any compatibility-sensitive change.
- [ ] Korean and English user-facing docs stay consistent when behavior changes.
- [ ] No fake usage metric, adoption claim, star count, download count, production claim, or ecosystem-critical claim is added.
- [ ] No secret, token, API key, Discord webhook URL, or private identifier appears in docs, fixtures, logs, screenshots, or commits.

## Locale Checks

- [ ] `ko-KR` remains the default enabled locale unless a breaking change is planned.
- [ ] `en-US` is described as foundation/experimental unless source maturity proves otherwise.
- [ ] `CAREER_FEED_ENABLED_LOCALES` behavior matches `scripts/locale_config.py`.
- [ ] Canonical daily artifact paths use `reports/briefs/{locale}/`, `reports/candidates/{locale}/`, and `reports/ops/{locale}/`.
- [ ] `ko-KR` legacy fallback behavior remains documented during v0.2.x.

## Webhook Checks

- [ ] Daily Backend `ko-KR` delivery accepts `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY`.
- [ ] Daily Backend `ko-KR` fallback accepts `DISCORD_WEBHOOK_KR_TECH_DAILY`.
- [ ] Daily Backend `en-US` delivery accepts `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY`.
- [ ] News Daily `ko-KR` delivery accepts `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY`.
- [ ] News Daily `ko-KR` fallback accepts `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY`.
- [ ] News Daily `en-US` delivery accepts `DISCORD_WEBHOOK_EN_US_NEWS_DAILY`.
- [ ] Backend Career Site Radar uses `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`.
- [ ] Optional ops failure alert uses `DISCORD_WEBHOOK_CAREER_FEED_OPS` and skips safely when missing.

## Provider Checks

- [ ] Provider status is described as current behavior, scaffold, or planned work.
- [ ] Naver assumptions are limited to the `ko-KR` path.
- [ ] Brave Search is not overclaimed beyond the v0.2 `en-US` foundation.
- [ ] RSS/reference sources and GitHub OSS candidate paths are documented with validation expectations.
- [ ] Source quality and spam/low-quality source risks are documented.

## Validation Commands

Run:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

For locale-sensitive changes, also run:

```bash
python3 scripts/locale_config.py matrix
python3 scripts/locale_config.py paths --locale ko-KR --feed backend-daily
python3 scripts/locale_config.py paths --locale en-US --feed backend-daily
python3 scripts/locale_config.py paths --locale ko-KR --feed news-daily
python3 scripts/locale_config.py paths --locale en-US --feed news-daily
```

## Release Notes

Release notes should include:

- What changed.
- Why the change matters.
- Which locale paths are affected.
- Validation commands run.
- Known limitations.
- Upgrade notes.
- Whether any compatibility behavior changes.

Do not rewrite existing release history. Add corrections in the next patch release notes or documentation.
