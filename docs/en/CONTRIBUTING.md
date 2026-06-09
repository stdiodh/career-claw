# Contributing to Career Feed

> Language: [한국어](../kr/CONTRIBUTING.md) | [English](./CONTRIBUTING.md)

Career Feed welcomes small, reviewable contributions that improve documentation, validation, examples, source policy, and backend learning quality.

Start with a focused issue or pull request. Keep unrelated refactors out of contribution branches.

## Welcome

You can contribute even if you are not changing automation code. Documentation, sample outputs, validation fixtures, and source review rules are important parts of this project.

## Project purpose

Career Feed generates scheduled Markdown briefs through GitHub Actions, then reviews artifacts before optional Discord Webhook delivery. The initial scope does not include a persistent server, database, dashboard, Gateway Bot, or Slash Command service.

## Ways to contribute

- Improve setup and operations documentation.
- Suggest reliable public sources for Dev News Daily or career site radar.
- Improve examples and validation fixtures.
- Propose Java/Kotlin backend learning topics.
- Suggest safe OSS contribution candidates.

## What makes a good contribution

Good contributions are small, verifiable, and aligned with the current workflows. Include the reason for the change and the check you ran.

## Before opening an issue

Search existing issues and documents first. If you are reporting a behavior problem, include the workflow name, command, input, and relevant artifact path.

## Issue types

Use the closest issue template. Career Feed accepts backend career questions, bug reports, docs improvements, source suggestions, broken or outdated source reports, OSS candidate suggestions, validation fixture ideas, release readiness tasks, regional or language expansion ideas, and maintainer questions.

Blank issues are disabled, so choose the closest structured template.

## Pull request guidelines

- Keep diffs focused.
- Do not commit generated `reports/` output.
- Do not hardcode secrets or webhook URLs.
- Update validation when document paths or required files change.

## Development setup

Pull Request Checks run automatically when a PR is opened or updated.

Before opening a PR, run `python3 scripts/check-doc-format.py`, `git diff --check`, and `./scripts/validate.sh` locally when possible.

## Commit convention

Use the repository commit convention: `type(scope): subject`. Examples include `docs(onboarding): update setup guide` and `fix(validation): tighten OSS candidate check`.

## Pull request template

Follow `.github/pull_request_template.md`. Describe what changed, why it changed, important code or document examples, and what reviewers should check.
