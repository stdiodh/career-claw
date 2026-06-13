# OSS Application Readiness

This checklist helps evaluate whether Career Feed is ready for a Codex for OSS application.

## Current Readiness

Current score: 8 out of 10 after the prepared v0.2.1 onboarding hardening.

What the repository proves:

- fork-based GitHub Actions automation
- dry-run artifact review before Discord delivery
- validation scripts and fixtures
- secret-safe setup guidance
- first dry-run setup with only `OPENAI_API_KEY`
- schedule-disabled-by-default safety
- generic Discord webhook fallback
- optional GitHub CLI setup helper
- `ko-KR` default supported locale
- `en-US` foundation / experimental preset
- locale-specific webhook Secret naming
- `ko-KR` legacy fallback compatibility
- provider/source policy direction
- contributor and issue triage structure

What it does not prove:

- broad adoption
- production usage
- mature global provider coverage
- mature `en-US` source quality
- hosted product readiness
- ecosystem-critical dependency status

## Pre-Application Checklist

- [ ] README describes the published v0.2.0 release and prepared unpublished v0.2.1 baseline accurately.
- [ ] CHANGELOG includes prepared v0.2.1 notes.
- [ ] Release docs distinguish the published v0.2.0 release from the unpublished v0.2.1 baseline.
- [ ] `ko-KR` remains default supported locale.
- [ ] `en-US` is described as foundation/experimental.
- [ ] Provider scaffolds are not overclaimed.
- [ ] Security docs warn against secret leaks.
- [ ] Issue templates collect locale, workflow, provider/source, validation, and redaction details.
- [ ] Roadmap separates v0.2.x patch work from v0.3.0 feature work.
- [ ] Validation commands pass.

## Remaining Blockers

No hard blocker is known if validation passes.

Recommended before applying:

- Run final validation.
- Review all application wording for unproved adoption claims.
- Confirm no generated `reports/` artifacts are staged.
- Confirm no secret values appear in docs or screenshots.

## Evidence In Repository

- workflow files under `.github/workflows/`
- validation scripts under `scripts/`
- fixture files under `tests/fixtures/`
- locale config under `configs/locales/`
- release docs under `docs/project/`
- localized setup docs under `docs/kr/` and `docs/en/`
- issue templates under `.github/ISSUE_TEMPLATE/`

## Application Position

Career Feed is early but maintainable.

Its OSS value comes from reproducible workflows, validation artifacts, locale-aware setup, human-reviewed delivery, source policy, and safe fork-based automation rather than adoption metrics.
