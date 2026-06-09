# Release Checklist

> Language: [한국어](../../kr/project/release-checklist.md) | [English](./release-checklist.md)

This checklist describes the draft v0.1.0 release gate. Actual GitHub tags and releases remain the source of truth.

## v0.1.0 release goal

Ship the initial public Career Feed workflow set with clear documentation, validation, and disabled-by-default delivery safety.

## v0.1.0 scope

- Daily Backend Brief.
- Korea Dev/AI News Daily.
- Backend Career Site Radar.
- PS progress marker workflow.
- Korean and English documentation entry points.

## v0.1.0 acceptance criteria

- Required docs exist in both language trees.
- `./scripts/validate.sh` passes.
- No generated reports are committed.
- Secrets are documented by name only.

## Pre-release checks

- Confirm workflow files and schedules.
- Confirm documentation links.
- Confirm issue templates point to current language paths.
- Confirm README release status wording matches actual tags.

## Verification commands

```bash
python3 scripts/check-doc-format.py
git diff --check
./scripts/validate.sh
```

## Release note draft

Use [v0.1.0 Release Notes](../release-notes/v0.1.0.md) as the draft note, then update it only when the actual release is cut.
