# Release Checklist

> Language: [한국어](../../kr/project/release-checklist.md) | [English](./release-checklist.md)

This checklist describes the current v0.2.x release gate. Actual GitHub tags and releases remain the source of truth.

Current release-state distinction:

- Latest published release/tag: `v0.2.0`.
- Prepared unpublished patch baseline: `v0.2.1` docs/onboarding updates dated 2026-06-11.
- `v0.1.0` remains the historical first public OSS baseline for fork-based automation.
- Do not imply that `v0.2.1` has a tag or GitHub Release unless the maintainer intentionally publishes it.

## v0.2.x release goal

Keep the v0.2.x locale-aware foundation accurate, compatible, and reviewable while planning small patches and larger v0.3.0 provider work separately.

## v0.2.x readiness

- Confirm locale-aware artifact paths under `reports/briefs/{locale}/`, `reports/candidates/{locale}/`, and `reports/ops/{locale}/`.
- Keep `ko-KR` as the default supported locale.
- Describe `en-US` only as an experimental foundation.
- Start from dry-run artifact review.
- Keep Discord delivery disabled by default.
- Require generated brief validation before Discord delivery.

## Current v0.2.x scope

- Daily Backend Brief.
- Dev News Daily.
- Backend Career Site Radar for the `ko-KR` path.
- PS progress marker workflow.
- `ko-KR` as the default supported locale.
- `en-US` as a foundation / experimental preset.
- Locale-specific daily Discord webhook Secret names.
- `ko-KR` legacy webhook fallback names and mirror artifacts during v0.2.x.
- First Backend Daily dry-run with only `OPENAI_API_KEY`.
- Repository Variables as optional overrides.
- Generic `DISCORD_WEBHOOK_CAREER_FEED` fallback.
- Scheduled generation disabled by default.

## v0.2.x acceptance criteria

- Required docs exist in both language trees.
- `./scripts/validate.sh` passes.
- No generated reports are committed.
- Secrets are documented by name only.
- `ko-KR` legacy fallback behavior remains documented.
- `en-US` is not described as mature global support.
- Provider marker modules are not overclaimed as a complete provider system.

## Pre-release checks

- Confirm workflow files and schedules.
- Confirm documentation links.
- Confirm issue templates point to current language paths.
- Confirm README release status and release links match the real tag state.
- Confirm a `v0.2.1` tag and GitHub Release are created only if the maintainer intentionally publishes them.
- Confirm Korean, English, and shared release docs stay consistent when release-state wording changes.
- Confirm [shared release checklist](../../project/release-checklist.md).
- Confirm [v0.2 compatibility notes](../../project/v0.2-compatibility.md).

## Verification commands

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

## Release note draft

Use `CHANGELOG.md`, [v0.2.0 Release Notes](../release-notes/v0.2.0.md), and [shared v0.2 baseline](../../project/release-v0.2.0.md) as the release reference set.

Do not rewrite published release history. Add corrections through docs or a later patch release.

## Maintainer Manual Follow-ups

- Rename the GitHub milestone `v0.1.x contributor onboarding` to `contributor onboarding` or `v0.2.x contributor onboarding`.
- Keep issues #14-#17 as starter tasks if they are still relevant.
- Do not treat this checklist as evidence that issue metadata was changed from repository files.
