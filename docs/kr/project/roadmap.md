# Roadmap

> Language: [한국어](./roadmap.md) | [English](../../en/project/roadmap.md)

This roadmap describes direction, not a delivery promise.

Items below are planned or being explored. They should not be described as current behavior until implemented and validated.

## Current Baseline

현재 baseline은 `v0.2.0`입니다.

Career Feed는 현재 fork-based GitHub Actions workflow, dry-run artifact, validation, optional Discord Webhook delivery, `ko-KR` 기본 지원, `en-US` foundation / experimental preset을 제공합니다.

## v0.2.1 Patch Candidates

- v0.2 behavior 문서 보정
- locale config와 fixture validation hardening
- 작은 fixture 수정
- issue template cleanup
- release note correction
- webhook fallback과 artifact mirror compatibility clarification
- `ko-KR` behavior를 보존하는 safe bug fix

## v0.3.0 Feature Candidates

- deeper `en-US` provider maturity
- source policy review 이후 additional provider implementation
- richer provider output validation
- improved source quality scoring
- better OSS candidate filtering
- review capacity가 있을 때만 `ko-KR`/`en-US` 외 locale expansion
- optional workflow improvements
- better artifact summaries

## Out of scope

The following are not planned for the current operating model:

- automatic job applications
- automatic claiming of external GitHub issues
- automatic comments on external repositories
- automatic PR creation on external repositories
- replacing human review of source links
- replacing personal career decisions
- storing secrets in repository files
- hosted multi-tenant SaaS dashboard
- Discord Gateway Bot or Slash Command service

## Shared Planning Docs

- [Shared Roadmap](../../project/roadmap.md)
- [v0.2.1 Plan](../../project/v0.2.1-plan.md)
- [v0.3.0 Roadmap](../../project/v0.3.0-roadmap.md)

## How to suggest roadmap changes

Open an issue or PR with:

- the user problem
- the affected workflow or document
- why existing docs or configuration do not solve it
- safety and validation impact
- a small first step if possible

Do not include fake adoption data, private user information, API keys, or webhook URLs in roadmap suggestions.
