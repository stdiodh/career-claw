# Roadmap

> Language: [한국어](./roadmap.md) | [English](../../en/project/roadmap.md)

This roadmap describes direction, not a delivery promise.

Items below are planned or being explored. They should not be described as current behavior until implemented and validated.

## v0.1.x

- Improve source configuration examples.
- Add more Java/Kotlin backend source presets.
- Improve validation report readability.
- Add more sample output fixtures.
- Improve demo screenshots and redaction guidance.
- Add contributor-friendly test fixtures.
- Clarify per-workflow setup examples for fork users.

## v0.2.x

- `ko-KR`와 experimental `en-US` preset을 대상으로 locale-aware engine foundation을 만든다.
- workflow YAML 수정 없이 `CAREER_FEED_ENABLED_LOCALES=ko-KR,en-US`로 locale별 dry-run artifact를 생성한다.
- locale별 config를 `configs/locales/{locale}/` 아래에 둔다.
- daily artifact를 `reports/briefs/{locale}/`, `reports/candidates/{locale}/` 아래에 쓴다.
- v0.2 compatibility 기간에는 `ko-KR` legacy artifact mirror를 유지한다.
- `naver,rss,github`, `brave,rss,github` 같은 provider preset을 도입한다.
- fork 커뮤니티용 예시와 contributor onboarding을 보강한다.

## Later

- Explore optional dashboard summary for local artifacts.
- Support more community-maintained source lists and locales.
- Improve duplicate delivery protection beyond the initial lock model.
- Explore additional sample briefs for study groups and mentoring contexts.

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

## How to suggest roadmap changes

Open an issue or PR with:

- the user problem
- the affected workflow or document
- why existing docs or configuration do not solve it
- safety and validation impact
- a small first step if possible

Do not include fake adoption data, private user information, API keys, or webhook URLs in roadmap suggestions.
