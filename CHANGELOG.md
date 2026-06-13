# Changelog

All notable changes to Career Feed are tracked here.

This project is still an early open-source automation tool. Release notes describe the repository state at the time of release and do not claim production-grade stability.

## [Unreleased]

### Changed

- Clarified that `v0.2.0` is the latest published release and `v0.2.1` remains a prepared unpublished docs/onboarding baseline until the maintainer tags and publishes it.

## [0.2.1] - 2026-06-11

Prepared patch notes for an unpublished v0.2.1 baseline. The maintainer has not created a `v0.2.1` tag or GitHub Release yet.

### Added

- Added `scripts/setup-fork.sh` as an optional GitHub CLI setup helper for fork users.
- Added a generic Discord delivery fallback Secret, `DISCORD_WEBHOOK_CAREER_FEED`, while preserving locale/feed-specific and legacy webhook Secret names.
- Added `CAREER_FEED_SCHEDULE_ENABLED` with scheduled generation disabled by default for new forks.

### Changed

- Simplified first Backend Daily manual dry-run setup so a fresh fork only needs the `OPENAI_API_KEY` repository Secret.
- Clarified that repository Variables are optional overrides, not required first-run setup.
- Changed manual daily workflow defaults so `dry_run=true` and `force_send=false`.
- Kept manual `workflow_dispatch` runs available even when scheduled generation is disabled.
- Updated fork setup, fresh fork smoke test, runtime configuration, webhook setup, Codex application, and promotion readiness docs to match the v0.2.1 onboarding path.

### Safety

- Scheduled events now skip safely with `schedule_disabled` unless `CAREER_FEED_SCHEDULE_ENABLED=true`.
- Discord delivery remains gated by dry-run status, delivery flag, webhook availability, validation, and delivery-lock behavior.
- No usage, adoption, stars, downloads, active users, organization usage, or production deployment metrics are claimed.

## [0.2.0] - 2026-06-10

### Added

- Added the locale-aware runtime foundation for `ko-KR` and `en-US`.
- Added locale-specific config, audience profile, and prompt paths under `configs/locales/{locale}/`.
- Added locale-specific daily artifact paths under `reports/briefs/{locale}/`, `reports/candidates/{locale}/`, and `reports/ops/{locale}/`.
- Added locale-specific Discord webhook Secret names for Daily Backend Brief and Dev News Daily.
- Added provider preset configuration for `naver,rss,github` and `brave,rss,github`.
- Added `en-US` validation fixtures for the v0.2 foundation.

### Changed

- Documented the v0.2 locale-aware foundation for `ko-KR` and `en-US`.
- Clarified canonical locale artifact paths and `ko-KR` legacy mirror paths.
- Clarified that `en-US` is an experimental preset, not a fully global service.
- Kept `ko-KR` as the default supported locale and preserved legacy webhook fallback names during the v0.2 compatibility window.
- Kept Backend Career Site Radar centered on `ko-KR` while using a canonical `reports/briefs/ko-KR/backend-career-weekly.md` output path.

### Known limitations

- `en-US` is a foundation/experimental preset and does not yet have the same source maturity as the `ko-KR` default path.
- Provider marker modules exist, but the v0.2 collector still contains much of the source collection implementation for compatibility.
- Additional locales remain future community-maintained work.
- No usage, adoption, stars, downloads, or production deployment metrics are claimed.

## [0.1.0] - 2026-06-09

### Added

- OSS readiness and impact evidence in the README.
- Redacted demo evidence links for dry-run dispatch, artifact summary, validation report, and Discord output.
- v0.1.0 release checklist and GitHub Release body.
- Contributor task ideas for small documentation, fixture, and validation improvements.
- Roadmap for near-term and later project directions.
- Support guidance for issues, questions, and secret-safe reporting.
- Daily Backend Brief workflow for Java/Kotlin backend learning, PS routine, OSS candidate, and practical backend knowledge briefs.
- Korea Dev/AI News Daily workflow for Korean development and AI news briefing.
- Backend Career Site Radar workflow for weekly public source checks.
- GitHub Actions Variables based runtime configuration.
- GitHub Actions Secrets and Variables separation in setup documentation.
- Runtime gate for scheduled workflow personalization without editing workflow YAML.
- Discord delivery flag with delivery disabled by default.
- dry-run first workflow guidance and artifact review flow.
- Recent OSS candidate filtering based on issue `created_at`.
- Safe OSS candidate artifact diagnostics and fallback routine when no safe recent candidate exists.
- Generated brief validation before Discord delivery.
- Fork-first setup guide.
- Demo guide and sample output documentation.

### Changed

- Issue template labels now match actual GitHub label names.
- Contributor and pull request guidance now points to fork setup, runtime configuration, OSS policy, and release readiness docs.
- README Quick Start points fork users to dry-run, artifact review, and explicit Discord delivery activation.
- Usage docs recommend dry-run before Discord delivery.
- Runtime configuration docs document supported Variables, defaults, and invalid examples.
- OSS candidate policy documents `created_at` recency as a hard gate.

### Security

- Security guidance clarified the v0.1.0 historical baseline and secret reporting expectations.
- Secrets and Variables are documented separately.
- Discord delivery is disabled by default for fork users.
- Generated briefs are validated before delivery.
- The project does not auto-claim, auto-comment, auto-assign, auto-label, or open PRs on external repositories.

### Known limitations

- v0.1.0 is not a stable commercial product release.
- No stars, downloads, active users, or adoption metrics are claimed for v0.1.0.
- Users must review generated links and artifacts before acting on a brief.
- GitHub Actions schedule timing is not real-time.
- External source availability may affect generated content.
- OSS candidate recommendations require human confirmation before contributing.
