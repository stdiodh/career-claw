# Changelog

All notable changes to Career Feed are tracked here.

This project is still an early open-source automation tool. Release notes describe the repository state at the time of release and do not claim production-grade stability.

## [Unreleased]

### Changed

- Documented the v0.2 locale-aware foundation for `ko-KR` and `en-US`.
- Clarified canonical locale artifact paths and `ko-KR` legacy mirror paths.
- Clarified that `en-US` is an experimental preset, not a fully global service.

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

- Security guidance now clarifies initial v0.1.x support scope and secret reporting expectations.
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
