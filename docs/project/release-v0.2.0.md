# v0.2.0 Release Baseline

This document mirrors the v0.2.0 repository baseline for reviewers and maintainers.

It does not replace the GitHub Release or tag history. The tag and workflow files remain the source of truth for exact behavior.

## Summary

Career Feed v0.2.0 adds the locale-aware foundation after the v0.1.0 fork-based workflow baseline.

The release keeps `ko-KR` as the default supported locale and adds an `en-US` foundation for testing locale-specific prompts, config, artifacts, validation fixtures, and Discord webhook naming.

## What Changed From v0.1.0

- Daily Backend Brief and Dev News Daily now resolve enabled locales through `scripts/locale_config.py`.
- `CAREER_FEED_ENABLED_LOCALES` can enable `ko-KR` and `en-US` without editing workflow YAML.
- Locale config moved to `configs/locales/{locale}/`.
- Daily workflow artifacts use locale-specific canonical paths.
- Daily Discord webhook Secret names are locale-specific.
- `ko-KR` legacy webhook fallbacks and legacy mirror artifacts remain during the v0.2 compatibility window.
- Provider presets are documented for `ko-KR` and `en-US`.

## Locale-Aware Foundation

The supported locale list is currently:

- `ko-KR`
- `en-US`

The default enabled locale remains `ko-KR`.

`CAREER_FEED_ENABLED_LOCALES=ko-KR,en-US` creates a workflow matrix for the daily workflows. Each locale gets separate config, prompt, candidate, brief, ops, validation, and run summary paths.

## ko-KR Default Support

`ko-KR` is the most complete supported path for the current project scope.

It includes Korean-oriented source assumptions, existing workflow behavior, legacy webhook fallback names, legacy artifact mirrors, and the strongest documentation coverage.

## en-US Foundation / Experimental Preset

`en-US` is a v0.2 foundation, not a mature global product.

It currently proves:

- locale-specific config and prompts exist
- `en-US` artifacts can be routed separately
- `en-US` webhook Secret names are recognized
- validation fixtures exist for English daily backend and news briefs
- provider preset naming supports `brave,rss,github`

It does not yet prove mature English source quality, complete provider implementation, or broad global readiness.

## Discord Webhook Secret Naming

Daily Backend Brief:

- `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY`
- `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY`
- `DISCORD_WEBHOOK_KR_TECH_DAILY` as the `ko-KR` compatibility fallback

Dev News Daily:

- `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY`
- `DISCORD_WEBHOOK_EN_US_NEWS_DAILY`
- `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` as the `ko-KR` compatibility fallback

Backend Career Site Radar:

- `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

Optional failure alerts:

- `DISCORD_WEBHOOK_CAREER_FEED_OPS`

Webhook URLs must stay in GitHub Secrets or local environment variables. They must not appear in docs, issues, logs, fixtures, screenshots, or commits.

## Provider Scaffold Status

| Provider | Current status |
| --- | --- |
| Naver | Optional `ko-KR` news enrichment path when credentials are present |
| RSS / Atom | Active source input through locale config and collector logic |
| GitHub | Active OSS candidate discovery path with safety validation |
| Brave Search | `en-US` preset foundation and optional credential warning; deeper integration remains planned work |

Provider marker classes exist under `scripts/search_providers/`, but the v0.2 collector still keeps most implementation in `scripts/collect-kr-feeds.py`.

## Canonical Artifact Paths

Daily Backend Brief:

- `reports/briefs/{locale}/backend-daily.md`
- `reports/candidates/{locale}/`
- `reports/ops/{locale}/backend-daily-validation-report.md`
- `reports/ops/{locale}/backend-daily-run-summary.json`
- `reports/ops/{locale}/backend-daily-run-summary.md`

Dev News Daily:

- `reports/briefs/{locale}/news-daily.md`
- `reports/candidates/{locale}/news-shortlist.json`
- `reports/ops/{locale}/news-daily-validation-report.md`
- `reports/ops/{locale}/news-daily-quality-report.json`
- `reports/ops/{locale}/news-daily-token-budget.json`
- `reports/ops/{locale}/news-daily-run-summary.json`
- `reports/ops/{locale}/news-daily-run-summary.md`

Backend Career Site Radar:

- `reports/briefs/ko-KR/backend-career-weekly.md`
- `reports/candidates/ko-KR/weekly-career-site-radar.json`

## ko-KR Legacy Mirrors

During v0.2.x, `ko-KR` daily workflows also write compatibility mirror paths:

- `reports/briefs/kr-tech-daily.md`
- `reports/briefs/kr-tech-news-daily.md`
- `reports/briefs/kr-backend-career-weekly.md`

Daily validation and Codex summary mirrors also exist for affected `ko-KR` workflows.

New docs and forks should prefer canonical locale-specific paths.

## Validation Commands

Run these before release or PR review:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

Useful targeted checks:

```bash
python3 scripts/locale_config.py matrix
python3 scripts/locale_config.py paths --locale ko-KR --feed backend-daily
python3 scripts/locale_config.py paths --locale en-US --feed news-daily
```

## Known Limitations

- `en-US` is still experimental/foundational.
- Backend Career Site Radar remains `ko-KR` centered.
- Provider abstraction is not fully separated from the collector yet.
- Sparse or empty News Daily output can be valid when source quality is low.
- No usage, adoption, production, star, download, or active-user metric is claimed.

## Upgrade Notes

Existing `ko-KR` fork users can keep legacy daily webhook Secret names during v0.2.x.

New forks should use locale-specific Secret names and canonical artifact paths.

If enabling `en-US`, add the matching `en-US` webhook Secrets before turning on Discord delivery.

## v0.2.1 Patch Candidates

- Correct stale historical v0.1 wording in release, security, issue, and maintainer docs.
- Add or improve provider/source policy docs.
- Improve issue templates for locale and artifact triage.
- Strengthen validation docs around locale fixtures and canonical paths.
- Add Codex for OSS readiness documentation.

## v0.3.0 Roadmap Candidates

- Mature the `en-US` provider path.
- Split provider implementations more cleanly from `collect-kr-feeds.py`.
- Add provider output validation fixtures.
- Improve source quality scoring and source policy checks.
- Explore additional community-maintained locales only after review capacity exists.
