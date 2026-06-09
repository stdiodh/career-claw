# Backend Career Site Radar

> Language: [한국어](../../kr/operations/career-site-radar.md) | [English](./career-site-radar.md)

Backend Career Site Radar checks configured public career and activity sources on a weekly workflow path.

## Purpose

The radar helps learners review public backend-related opportunities without building a recruiting database or matching service.

## Workflow

The workflow file is `.github/workflows/backend-career-weekly.yml`. It renders weekly radar artifacts and can optionally send to Discord when configured.

## Sources

Sources are configured in `configs/weekly-career-site-radar.json`. Use public, stable pages that can be reviewed without login or private access.

## Manual run

Use workflow dispatch for manual review. Keep delivery disabled while testing new source changes.

## Discord delivery

Discord delivery should summarize public links and review notes, not private application data or personal recommendations.

## Artifacts

Review `reports/candidates/ko-KR/weekly-career-site-radar.json` and `reports/briefs/ko-KR/backend-career-weekly.md`.
