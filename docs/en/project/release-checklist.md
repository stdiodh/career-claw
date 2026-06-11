# Release Checklist

> Language: [한국어](../../kr/project/release-checklist.md) | [English](./release-checklist.md)

This checklist describes the current v0.2.x release gate. Actual GitHub tags and releases remain the source of truth.

`v0.1.0` remains the historical first public OSS baseline for fork-based automation.

## v0.2.x release goal

Keep the v0.2.0 locale-aware foundation accurate, compatible, and reviewable while planning small v0.2.1 patches and larger v0.3.0 provider work separately.

## v0.2.x readiness

- Confirm locale-aware artifact paths under `reports/briefs/{locale}/`, `reports/candidates/{locale}/`, and `reports/ops/{locale}/`.
- Keep `ko-KR` as the default supported locale.
- Describe `en-US` only as an experimental foundation.
- Start from dry-run artifact review.
- Keep Discord delivery disabled by default.
- Require generated brief validation before Discord delivery.

## Current v0.2.0 scope

- Daily Backend Brief.
- Dev News Daily.
- Backend Career Site Radar for the `ko-KR` path.
- PS progress marker workflow.
- `ko-KR` as the default supported locale.
- `en-US` as a foundation / experimental preset.
- Locale-specific daily Discord webhook Secret names.
- `ko-KR` legacy webhook fallback names and mirror artifacts during v0.2.x.

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
- Confirm README release status wording matches actual tags.
- Confirm [shared release checklist](../../project/release-checklist.md).
- Confirm [v0.2 compatibility notes](../../project/v0.2-compatibility.md).

## Verification commands

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

## Release note draft

Use [v0.2.0 Release Notes](../release-notes/v0.2.0.md) and [shared v0.2 baseline](../../project/release-v0.2.0.md) as the current reference.

Do not rewrite published release history. Add corrections through docs or a later patch release.
