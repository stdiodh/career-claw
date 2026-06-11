# Validation

This shared document lists the current v0.2 validation expectations.

## Required Checks

Run these before opening or merging a PR whenever possible:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

## What `./scripts/validate.sh` Covers

The validation script checks:

- Python syntax for scripts.
- Active workflow file names, versions, schedules, and permissions.
- Documentation formatting and issue template YAML.
- Required config, prompt, docs, fixture, and workflow files.
- Removed legacy workflow/script references.
- Collector dry-runs for current workflows.
- Daily Backend, News Daily, OSS reliability, and weekly career fixtures.
- `ko-KR` and `en-US` foundation fixture validation.
- Generated brief validation behavior.
- Whitespace errors in the current diff.

## Locale Checks

For locale or webhook changes, also run:

```bash
python3 scripts/locale_config.py matrix
python3 scripts/locale_config.py paths --locale ko-KR --feed backend-daily
python3 scripts/locale_config.py paths --locale en-US --feed backend-daily
python3 scripts/locale_config.py paths --locale ko-KR --feed news-daily
python3 scripts/locale_config.py paths --locale en-US --feed news-daily
```

Expected behavior:

- `ko-KR` paths include legacy mirror outputs during v0.2.x.
- `en-US` paths do not include legacy mirror outputs.
- Unsupported locales fail clearly.

## Artifact Expectations

Daily Backend Brief:

- `reports/briefs/{locale}/backend-daily.md`
- `reports/candidates/{locale}/`
- `reports/ops/{locale}/backend-daily-validation-report.md`
- `reports/ops/{locale}/backend-daily-run-summary.json`

Dev News Daily:

- `reports/briefs/{locale}/news-daily.md`
- `reports/candidates/{locale}/news-shortlist.json`
- `reports/ops/{locale}/news-daily-validation-report.md`
- `reports/ops/{locale}/news-daily-quality-report.json`
- `reports/ops/{locale}/news-daily-run-summary.json`

Backend Career Site Radar:

- `reports/briefs/ko-KR/backend-career-weekly.md`
- `reports/candidates/ko-KR/weekly-career-site-radar.json`

Generated `reports/` files are not committed by default.

## If Validation Fails

Fix failures caused by the current change.

If a failure is pre-existing, document the command, failure, and affected file in the PR body instead of hiding it.

Never paste secrets, webhook URLs, API keys, GitHub tokens, private Discord details, or private repository details into validation logs.
