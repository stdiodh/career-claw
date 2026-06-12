# Roadmap

> Language: [한국어](../../kr/project/roadmap.md) | [English](./roadmap.md)

The roadmap keeps future ideas visible without expanding the current operating scope prematurely.

## Current Baseline

Latest published release baseline: `v0.2.0`.

Prepared unpublished patch baseline: `v0.2.1` docs/onboarding updates.

The current default branch provides fork-based GitHub Actions workflows, one-secret first dry-run setup, optional Variables, schedule-disabled-by-default safety, dry-run artifacts, validation, optional Discord Webhook delivery, `ko-KR` default support, and an `en-US` foundation / experimental preset.

## v0.2.x Patch Candidates

- Documentation corrections around v0.2 behavior.
- Validation hardening for locale config and fixtures.
- Minor fixture fixes.
- Issue template cleanup.
- Release note corrections.
- Compatibility clarifications for webhook fallback and artifact mirrors.
- Safe bug fixes that preserve `ko-KR` behavior.

## v0.3.0 Feature Candidates

- Deeper `en-US` provider maturity.
- Additional provider implementation after source policy review.
- Richer provider output validation.
- Improved source quality scoring.
- Better OSS candidate filtering.
- Locale expansion beyond `ko-KR` and `en-US` only when review capacity exists.
- Optional workflow improvements.
- Better artifact summaries.

## Out of scope

Persistent services, databases, dashboards, Discord Gateway Bots, Slash Commands, account systems, and recruiting-matching services remain outside the initial roadmap.

## Shared Planning Docs

- [Shared Roadmap](../../project/roadmap.md)
- [v0.2.1 Plan](../../project/v0.2.1-plan.md)
- [v0.3.0 Roadmap](../../project/v0.3.0-roadmap.md)

## How to suggest roadmap changes

Open an issue with the problem, user impact, validation impact, and why the change belongs in Career Feed rather than an external integration.
