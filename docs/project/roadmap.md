# Roadmap

This shared roadmap separates current behavior from patch candidates and larger feature work.

## Current Baseline

Current release baseline: `v0.2.0`.

What v0.2.0 currently supports:

- fork-based GitHub Actions automation
- dry-run artifact review
- optional Discord Webhook delivery
- Daily Backend Brief
- Dev News Daily
- Backend Career Site Radar for `ko-KR`
- Mark PS progress workflow
- `ko-KR` as the default supported locale
- `en-US` as a foundation / experimental preset
- locale-specific daily webhook Secret names
- `ko-KR` legacy webhook fallback names during v0.2.x
- provider preset foundation for Naver, RSS, GitHub, and Brave Search

## v0.2.1 Patch Candidates

Patch candidates should be small and safe:

- documentation corrections
- validation hardening
- minor fixture fixes
- issue template cleanup
- release note corrections
- compatibility clarifications
- safe bug fixes that preserve `ko-KR` behavior

See [v0.2.1 Plan](./v0.2.1-plan.md).

## v0.3.0 Feature Candidates

Feature candidates should be planned as separate issues:

- deeper `en-US` provider maturity
- additional search engine/provider implementation
- richer provider validation
- improved source quality scoring
- better OSS candidate filtering
- locale expansion beyond `ko-KR` and `en-US`
- optional workflow improvements
- better artifact summaries

See [v0.3.0 Roadmap](./v0.3.0-roadmap.md).

## Non-Goals

Career Feed does not currently plan:

- persistent servers
- databases
- hosted dashboards
- Discord Gateway Bots
- Slash Commands
- account systems
- recruiting matching
- automatic external repository comments
- automatic external pull requests
- automatic external issue assignment or label changes

## Planning Rules

- Current behavior must be backed by code, workflows, docs, or fixtures.
- Planned work must not be described as shipped.
- Do not claim adoption metrics that are not evidenced in the repository.
- Preserve `ko-KR` v0.2 compatibility unless a later breaking release is planned.
- Keep `en-US` described as foundation/experimental until source and provider maturity improves.
