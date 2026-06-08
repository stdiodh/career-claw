# Release Checklist

This checklist is for maintainers preparing a public Career Feed release.

## v0.1.0 release goal

v0.1.0 is the first open-source release intended for fork-based usage.

It is not a stable commercial product release.

The goal is that a Java/Kotlin backend developer can fork the repository, run a dry-run, inspect artifacts, and then explicitly enable Discord delivery.

Users remain responsible for reviewing generated source links, OSS candidates, and Discord output before acting on the brief.

## v0.1.0 scope

Included in v0.1.0:

- Daily Backend Brief workflow
- Korea Dev/AI News Daily workflow
- Backend Career Site Radar workflow
- GitHub Actions based execution
- GitHub Actions Secrets and Variables based setup
- dry-run first operating flow
- Discord webhook delivery
- runtime gate for configurable schedule targets
- recent OSS candidate filtering based on issue `created_at`
- generated brief validation before Discord delivery
- artifact review flow
- fork setup guide
- demo and sample output documentation

Not included in v0.1.0:

- automatic job applications
- automatic external GitHub issue claiming
- automatic comments on external repositories
- automatic external PR creation
- long-running server
- multi-user SaaS dashboard
- guaranteed news, hiring, or OSS candidate accuracy
- replacing human review of source links or career decisions

## v0.1.0 acceptance criteria

v0.1.0 can be released when:

- [ ] A fresh fork can follow `docs/fork-setup.md` to complete dry-run.
- [ ] Required Secrets and optional Variables are documented.
- [ ] Discord delivery is disabled by default.
- [ ] dry-run generates artifacts without sending Discord messages.
- [ ] Generated brief validation runs before Discord delivery.
- [ ] Stale OSS issue fixtures fail validation.
- [ ] Safe candidate fallback works when no recent candidates exist.
- [ ] README links to all major docs.
- [ ] `CHANGELOG.md` includes v0.1.0 summary.
- [ ] `SECURITY.md` or equivalent guidance exists.
- [ ] `CONTRIBUTING.md` explains how to make a small PR.
- [ ] No fake metrics or unverified adoption claims exist.
- [ ] No real secrets appear in docs, samples, screenshots, or fixtures.

## Pre-release checks

### Documentation

- [ ] README Quick Start works from a fresh fork.
- [ ] `docs/fork-setup.md` is linked from README.
- [ ] `docs/runtime-configuration.md` lists all supported Variables.
- [ ] `docs/oss-candidate-policy.md` explains `created_at` recency.
- [ ] `docs/demo.md` does not link missing images.
- [ ] `docs/sample-output.md` uses placeholder links only.
- [ ] `docs/contributor-tasks.md` lists small contributor-friendly work.
- [ ] `docs/roadmap.md` separates planned work from current behavior.
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
- [ ] Tag name decided: `v0.1.0`.
- [ ] GitHub Release is created manually by the maintainer.

## Verification commands

Run the repository validation command:

```bash
./scripts/validate.sh
```

For documentation-only changes, run:

```bash
python3 scripts/check-doc-format.py
git diff --check
```

If `pytest` is configured in the local environment, targeted tests can also be run with repository-specific test paths.

Do not treat a successful command as enough for release. Review the generated artifacts and sample output manually.

## Release note draft

Use [v0.1.0 Release Notes](release-notes/v0.1.0.md) as the GitHub Release body draft.

Before publishing, confirm that:

- the release date is updated if needed
- no fake usage metric is added
- no secret or webhook URL appears in the body
- limitations remain visible
- the tag is created manually by the maintainer
