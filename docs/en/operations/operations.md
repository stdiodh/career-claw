# Operations Guide

> Language: [한국어](../../kr/operations/operations.md) | [English](./operations.md)

Career Feed operations are intentionally limited to four GitHub Actions paths.

## Operating paths

| Operating path | Scope | Main output |
| --- | --- | --- |
| Daily Backend Brief | Locale-aware | `reports/briefs/{locale}/backend-daily.md` |
| Dev News Daily | Locale-aware foundation | `reports/briefs/{locale}/news-daily.md` |
| Backend Career Site Radar | `ko-KR` centered in this phase | `reports/briefs/ko-KR/backend-career-weekly.md` |
| PS progress marker workflow | Locale-independent | `data/ps-progress.json` |

## Actions checklist

Check workflow inputs, runtime variables, delivery controls, generated artifacts, validation reports, and run summaries.

## Delivery policy

Use dry-run first. Discord delivery should happen only when validation passes and the relevant delivery setting is enabled.

## Validation

Run `./scripts/validate.sh` after script, workflow, config, or broad documentation changes.

## Related documents

- [Daily Backend Brief](./daily-backend-brief.md)
- [Dev News Daily](./daily-news-ops.md)
- [Backend Career Site Radar](./career-site-radar.md)
- [Runtime Configuration](../getting-started/runtime-configuration.md)
