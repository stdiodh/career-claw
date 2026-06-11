# Release Checklist

> Language: [한국어](./release-checklist.md) | [English](../../en/project/release-checklist.md)

This checklist is for maintainers preparing v0.2.x patch releases and later public Career Feed releases.

현재 baseline은 `v0.2.1`입니다.

`v0.1.0`은 과거 첫 fork 기반 릴리스로 유지하고, 새 릴리스 준비 문서는 v0.2.x 이후를 기준으로 작성합니다.

## v0.2.x release goal

v0.2.x의 목표는 locale-aware foundation을 작고 안전하게 유지하면서 `ko-KR` 기존 사용 흐름을 깨지 않는 것입니다.

`en-US`는 foundation/experimental preset으로 다루며, provider와 source maturity가 충분히 검증되기 전까지 완성된 global support로 설명하지 않습니다.

## v0.2.x readiness

- locale-aware artifact path가 `reports/briefs/{locale}/`, `reports/candidates/{locale}/`, `reports/ops/{locale}/` 기준으로 동작하는지 확인합니다.
- `ko-KR`은 기본 지원 locale로 유지합니다.
- `en-US`는 experimental foundation으로만 설명합니다.
- 첫 실행은 dry-run artifact 검토 흐름을 기준으로 안내합니다.
- Discord delivery는 기본 비활성화 상태로 유지합니다.
- Discord 전송 전 generated brief validation이 통과해야 합니다.

## Current v0.2.x scope

Included in current v0.2.x:

- Daily Backend Brief workflow
- Dev News Daily workflow
- Backend Career Site Radar workflow
- PS progress marker workflow
- `ko-KR` default supported locale
- `en-US` foundation / experimental preset
- GitHub Actions Secrets and Variables based setup
- `OPENAI_API_KEY` 하나로 시작하는 첫 Backend Daily dry-run
- optional Repository Variables
- locale-specific daily Discord webhook Secret names
- generic `DISCORD_WEBHOOK_CAREER_FEED` fallback
- `ko-KR` legacy webhook fallback names
- schedule-disabled-by-default safety
- locale-specific daily artifact paths
- `ko-KR` legacy mirror artifact paths
- provider preset foundation for Naver, RSS, GitHub, and Brave Search
- generated brief validation before Discord delivery
- dry-run first artifact review flow

Not included in current v0.2.x:

- mature global provider coverage
- fully mature `en-US` source quality
- locale expansion beyond `ko-KR` and `en-US`
- automatic job applications
- automatic external GitHub issue claiming
- automatic comments on external repositories
- automatic external PR creation
- long-running server
- multi-user SaaS dashboard
- guaranteed news, hiring, or OSS candidate accuracy
- replacing human review of source links or career decisions

## v0.2.x acceptance criteria

Before a v0.2.x patch release:

- [ ] A fresh fork can follow `docs/kr/getting-started/fork-setup.md` to complete a `ko-KR` dry-run.
- [ ] `en-US` is documented as foundation/experimental unless implementation evidence changes.
- [ ] `OPENAI_API_KEY` only first dry-run path and optional Variables are documented.
- [ ] Discord delivery is disabled by default.
- [ ] dry-run generates artifacts without sending Discord messages.
- [ ] Generated brief validation runs before Discord delivery.
- [ ] Stale OSS issue fixtures fail validation.
- [ ] Safe candidate fallback works when no recent candidates exist.
- [ ] README links to current v0.2 docs.
- [ ] `CHANGELOG.md` includes the target release summary.
- [ ] `SECURITY.md` reflects the current release line.
- [ ] `CONTRIBUTING.md` explains small PR expectations.
- [ ] No fake metrics or unverified adoption claims exist.
- [ ] No real secrets appear in docs, samples, screenshots, or fixtures.

## Pre-release checks

### Documentation

- [ ] README Quick Start works from a fresh fork.
- [ ] `docs/kr/getting-started/fork-setup.md` is linked from README.
- [ ] `docs/kr/getting-started/runtime-configuration.md` lists all supported Variables.
- [ ] `docs/kr/policies/oss-candidate-policy.md` explains `created_at` recency.
- [ ] `docs/demo.md` does not link missing images.
- [ ] `docs/kr/getting-started/sample-output.md` uses placeholder links only.
- [ ] `docs/kr/project/contributor-tasks.md` lists small contributor-friendly work.
- [ ] `docs/kr/project/roadmap.md` separates planned work from current behavior.
- [ ] `docs/project/release-v0.2.0.md` matches the actual baseline.
- [ ] `docs/project/v0.2-compatibility.md` describes fallback behavior accurately.
- [ ] No fake metrics or fake adoption claims are present.

### Configuration

- [ ] `.env.example` contains placeholder values only.
- [ ] Secrets and Variables are documented separately.
- [ ] Discord delivery is disabled by default.
- [ ] dry-run is documented as the first run path.

### Workflow

- [ ] Manual dry-run succeeds.
- [ ] Generated Markdown artifact is uploaded.
- [ ] Candidate artifact is uploaded.
- [ ] Validation report artifact is uploaded.
- [ ] Discord delivery is blocked when `dry_run=true`.
- [ ] Discord delivery is blocked when validation fails.
- [ ] Runtime gate logs resolved timezone and target time.

### OSS candidate safety

- [ ] 2023-era issue fixtures are filtered.
- [ ] `created_at` is used instead of `updated_at`.
- [ ] safe candidates are based on the recent issue window.
- [ ] fallback routine is used when safe candidates are empty.
- [ ] generated brief cannot include issue URLs outside the safe candidate artifact.

### Security

- [ ] No API key, token, webhook URL, or credential appears in docs.
- [ ] Screenshots do not expose secrets.
- [ ] GitHub Actions logs do not print secrets.
- [ ] `SECURITY.md` exists and explains secret reporting.
- [ ] Discord webhook URLs are treated as secrets.

### Release

- [ ] `CHANGELOG.md` updated.
- [ ] README links verified.
- [ ] Tests pass.
- [ ] Docs validation passes.
- [ ] Release notes drafted.
- [ ] Target tag name decided.
- [ ] GitHub Release is created manually by the maintainer.

## Verification commands

Run the repository validation command:

```bash
./scripts/validate.sh
```

For documentation-only changes, run:

```bash
git diff --check
python3 scripts/check-doc-format.py
```

If `pytest` is configured in the local environment, targeted tests can also be run with repository-specific test paths.

Do not treat a successful command as enough for release. Review the generated artifacts and sample output manually.

## Release note draft

Use `CHANGELOG.md`, [v0.2.0 Release Notes](../release-notes/v0.2.0.md), and [shared v0.2 baseline](../../project/release-v0.2.0.md) as the release reference set.

Before publishing, confirm that:

- the release date is updated if needed
- no fake usage metric is added
- no secret or webhook URL appears in the body
- limitations remain visible
- the tag is created manually by the maintainer
- published release history is not rewritten
