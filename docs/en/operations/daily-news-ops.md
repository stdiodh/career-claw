# Dev News Daily

> Language: [한국어](../../kr/operations/daily-news-ops.md) | [English](./daily-news-ops.md)

Dev News Daily reviews locale-specific developer and AI news candidates, then renders a validated Markdown brief.

## Purpose

The workflow helps readers identify developer-relevant news without turning the brief into investment advice or generic market commentary.

For `ko-KR`, it focuses on Korean developer and AI news sources.
For `en-US`, it uses the English preset foundation and configured provider list.

## Workflow

The workflow file is `.github/workflows/dev-news-daily.yml`. It collects candidates, builds a shortlist, estimates prompt budget, evaluates quality, writes a run summary, and optionally sends to Discord.
It uses the locale-aware foundation to write canonical artifacts under `reports/briefs/{locale}/`, `reports/candidates/{locale}/`, and `reports/ops/{locale}/`.

## Candidate policy

Candidates should have stable URLs, clear timestamps, developer relevance, and enough context for quality scoring. Duplicate URLs are rejected.

## Sparse and empty days

A sparse or empty day can be valid when too few sources meet quality criteria. The workflow should explain the state rather than forcing weak items.

## Artifacts

Review `reports/candidates/{locale}/news-shortlist.json`, `reports/ops/{locale}/news-daily-quality-report.json`, `reports/ops/{locale}/news-daily-token-budget.json`, and `reports/briefs/{locale}/news-daily.md`.

## Manual run

Use workflow dispatch with `dry_run=true` first. Enable delivery only after artifacts and validation output look correct.

## Validation

The validator checks duplicate links, investment-advice wording, objective metrics, risk context, item counts, and growth-action quality.
