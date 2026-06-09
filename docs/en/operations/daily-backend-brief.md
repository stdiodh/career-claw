# Daily Backend Brief

> Language: [한국어](../../kr/operations/daily-backend-brief.md) | [English](./daily-backend-brief.md)

Daily Backend Brief is the main locale-aware daily study workflow for Java/Kotlin backend learners.

## Purpose

The brief combines Spring Boot/JVM study, Programmers PS practice, OSS contribution preparation, and practical backend knowledge into one validated artifact.

## Workflow

The workflow file is `.github/workflows/backend-daily.yml`. It supports schedule and manual dispatch with dry-run and force-send controls.
It uses `CAREER_FEED_ENABLED_LOCALES` to write separate canonical artifacts for each enabled locale.

## Inputs

Important inputs and variables include `dry_run`, `force_send`, `CAREER_FEED_TIMEZONE`, `CAREER_FEED_BACKEND_DAILY_TIME`, `CAREER_FEED_OSS_RECENT_DAYS`, and Discord delivery controls.

## Artifacts

Review candidate JSON files, `reports/briefs/{locale}/backend-daily.md`, validation reports, and backend daily run summaries.

## Validation

Validation checks required sections, Spring/JVM study policy, OSS safe candidate policy, source domains, and forbidden fixed-curriculum wording.

## Discord delivery

Delivery is disabled by default and skipped during `dry_run=true`. Send only after validation passes and delivery is enabled.

## Related documents

- [Runtime Configuration](../getting-started/runtime-configuration.md)
- [OSS Candidate Policy](../policies/oss-candidate-policy.md)
- [Daily Spring/JVM Blog Topic Policy](../policies/daily-spring-jvm-blog-topic-policy.md)
