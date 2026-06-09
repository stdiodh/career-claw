# Roadmap

> Language: [한국어](../../kr/project/roadmap.md) | [English](./roadmap.md)

The roadmap keeps future ideas visible without expanding the current operating scope prematurely.

## v0.1.x

- Stabilize current workflows.
- Keep Korean and English documentation paths separated.
- Improve validation and troubleshooting.
- Refine source quality and OSS candidate policy.

## v0.2.x

- Establish the locale-aware engine foundation for `ko-KR` and `en-US`.
- Support `CAREER_FEED_ENABLED_LOCALES=ko-KR,en-US` without workflow YAML edits.
- Keep locale-specific config under `configs/locales/{locale}/`.
- Write daily artifacts under `reports/briefs/{locale}/` and `reports/candidates/{locale}/`.
- Keep `ko-KR` legacy artifact mirrors during the v0.2 compatibility window.
- Introduce provider presets such as `naver,rss,github` and `brave,rss,github`.
- Improve examples and contributor onboarding for forked communities.

## Later

Possible later work includes additional community-maintained locales, richer reporting artifacts, more validation fixtures, and safer source review tooling.

## Out of scope

Persistent services, databases, dashboards, Discord Gateway Bots, Slash Commands, account systems, and recruiting-matching services remain outside the initial roadmap.

## How to suggest roadmap changes

Open an issue with the problem, user impact, validation impact, and why the change belongs in Career Feed rather than an external integration.
