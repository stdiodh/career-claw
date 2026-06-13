# UX Onboarding Review

This review evaluates Career Feed as a first-time visitor, first-time fork user, first-time contributor, OSS reviewer, and innovation reviewer.

## First-Time Visitor Journey

Expected path:

1. Open `README.md`.
2. Understand the 30-second overview.
3. Choose `docs/kr/README.md` or `docs/en/README.md`.
4. Inspect sample outputs and demo assets.
5. Decide whether to fork, contribute, or only review the roadmap.

What works:

- `README.md` states the target audience, outputs, status, supported locales, and non-goals early.
- The language gateway is visible at the top.
- Redacted demo assets show dispatch, artifacts, validation, and Discord output.
- The project status says Early Public OSS and avoids adoption claims.

Friction:

- A visitor may still need to read several docs to understand which files are current behavior and which are roadmap.
- `app/` and `infra/` can distract from the no-server current operating path.
- `docs/project/**` has many shared docs, so the gateway must stay current.

30-second understanding test:

- Can the visitor say this is fork-based GitHub Actions automation? Yes, from `README.md`.
- Can the visitor say who it is for? Mostly yes: backend learners, Discord study groups, mentoring groups.
- Can the visitor say what is safe before Discord? Yes: dry-run artifacts and validation.
- Can the visitor identify the current status? Yes: Early Public OSS with no adoption metrics claimed.

## First-Time Fork User Journey

Expected path:

1. Fork repository.
2. Enable GitHub Actions.
3. Add `OPENAI_API_KEY` as a Secret.
4. Run `Backend Daily Brief` with `dry_run=true`, `force_send=false`.
5. Review uploaded artifacts and validation report.
6. Add Discord webhook Secret and delivery variable only after review.

What works:

- `docs/kr/getting-started/fork-setup.md` and `docs/en/getting-started/fork-setup.md` explain the one-secret first dry-run.
- `docs/kr/getting-started/fresh-fork-smoke-test.md` and `docs/en/getting-started/fresh-fork-smoke-test.md` provide shorter checklists.
- Setup screenshots in `docs/assets/getting-started/**` reduce GitHub UI ambiguity.
- `scripts/setup-fork.sh` offers an optional GitHub CLI path.

Friction:

- GitHub boolean checkbox labels can still be confusing, although the docs warn about this.
- API credit/cost expectations should stay visible near schedule and dry-run setup.
- Users may expect rich source output on the first run even when optional provider credentials are absent.

5-minute dry-run readiness test:

- Required Secret documented: `OPENAI_API_KEY`.
- Required Variables documented: none for first Backend Daily dry-run.
- Safe inputs documented: `dry_run=true`, `force_send=false`.
- Generated artifact paths documented: yes.
- Discord non-delivery expectation documented: yes.
- Validation-failure stop condition documented: yes.

## First-Time Contributor Journey

Expected path:

1. Read `CONTRIBUTING.md`.
2. Choose Korean or English guide.
3. Open `docs/kr/project/contributor-tasks.md` or `docs/en/project/contributor-tasks.md`.
4. Pick a docs, source suggestion, fixture, provider note, or validation improvement.
5. Run the smallest relevant check.
6. Open a PR using `.github/pull_request_template.md`.

What works:

- Root and localized contributing docs stress small, reviewable changes.
- Issue templates cover docs, sources, bugs, fixtures, OSS candidates, fork-trial reports, and regional expansion.
- `docs/kr/project/contributor-tasks.md` gives scoped starter tasks.
- The English task guide now gives similarly concrete starter tasks.

Friction:

- New contributors may not know which validation command maps to their change.
- Provider changes can look easy but touch source quality, credentials, and fallback behavior.
- Generated `reports/` files appear locally after validation and must stay out of commits.

## OSS Reviewer Journey

Reviewer questions:

- Does the repository look maintained? Yes, via `CHANGELOG.md`, release docs, validation, issue templates, and PR checks.
- Does it have safety posture? Yes, via Secret handling, dry-run defaults, validation, delivery locks, and no external repo mutation.
- Does it avoid inflated claims? Yes, multiple docs prohibit fake metrics and unverified adoption claims.
- Does it explain API credit use? Yes, especially in `docs/codex-for-oss-application.md` and localized application docs.

Reviewer friction:

- No public adoption metrics are claimed.
- The project should avoid saying "active users" or "production usage" until public evidence exists.
- Ecosystem impact is currently educational and workflow-level, not dependency-critical.

## Innovation Reviewer Journey

What is common:

- Scheduled GitHub Actions.
- Discord webhook delivery.
- AI-generated summaries.
- Good-first-issue discovery and source curation.

What is meaningfully differentiated:

- Fork-first setup with one-secret dry-run.
- Locale-aware artifact paths and prompt/config routing.
- Validation-before-delivery with generated reports.
- Conservative OSS candidate safety gates and fallback when no safe candidate exists.
- Explicit no-server/no-dashboard/no-bot constraint.

What is current:

- Daily Backend Brief.
- Dev News Daily.
- Backend Career Site Radar for `ko-KR`.
- Mark PS Solved.
- `ko-KR` default support.
- `en-US` foundation/experimental preset.

What is future:

- Mature provider abstraction.
- Stronger `en-US` source quality.
- More locales.
- Source quality scoring.
- Optional dashboard.
- Deeper Codex/MCP integrations.

## Second-Pass Confusion Map

| User type | Likely confusion | Evidence path | Low-risk fix or guardrail |
| --- | --- | --- | --- |
| First-time visitor | The repo has `app/` and `infra/`, so it may look like a server product. | `README.md`, `LEGACY.md`, `app/**`, `infra/**` | Keep no-server scope visible and treat those paths as legacy/prototype. |
| First-time visitor | `v0.2.1` appears in docs even though the latest published release is `v0.2.0`. | `README.md`, `CHANGELOG.md`, `docs/project/v0.2.1-plan.md` | Keep "latest published" and "prepared unpublished" language together. |
| First-time fork user | Sparse output can look broken when optional provider credentials are absent. | `tests/fixtures/kr-tech-news-daily-valid-sparse.md`, `tests/fixtures/kr-tech-news-daily-valid-empty.md` | Explain sparse/empty output as a safe result when sources do not meet policy. |
| First-time contributor | Generated files under `reports/` can look like files to commit. | `.gitignore`, `reports/**`, `.github/pull_request_template.md` | Keep generated artifacts ignored and require PR checklist confirmation. |
| First-time contributor | Provider tasks look like simple config edits but can affect source quality and credentials. | `docs/project/provider-expansion.md`, `scripts/collect-kr-feeds.py` | Keep provider-code tasks out of beginner-safe lanes unless fixtures are included. |
| Reviewer | Root and shared Codex application docs may look duplicative. | `docs/codex-for-oss-application.md`, `docs/project/codex-for-oss-application.md`, `docs/README.md` | Treat the root packet as current and the shared project doc as a positioning reference. |
| Reviewer | `en-US` may look like mature global support. | `README.md`, `docs/project/release-v0.2.0.md`, `docs/project/provider-expansion.md` | Keep `en-US` labelled foundation/experimental until source quality evidence exists. |
| Reviewer | API credits may look like content-generation spend without maintenance value. | `docs/codex-for-oss-application.md`, localized application docs | Tie credits to maintainer-reviewed drafts, summaries, validation, and docs consistency checks. |

## Korean And English Divergence Risks

The Korean and English documentation trees have matching paths, but not equal depth. This is acceptable while Korean remains the primary documentation language, but it can block first-time English contributors when setup, support, security, or contribution details diverge.

Priority parity areas:

- setup and first dry-run behavior
- security and secret-handling expectations
- support and issue-routing expectations
- contributor starter tasks and validation commands
- current status vs roadmap language

The PR template now asks reviewers to check both Korean and English docs when user-facing behavior changes. The docs-improvement issue template now includes a Korean/English divergence category.

## Generated, Legacy, And Roadmap Boundaries

Keep these boundaries visible in onboarding docs:

- `reports/**` is generated review output, not a default commit target.
- `app/**` and `infra/**` are legacy/prototype paths, not required for current operation.
- `v0.2.0` is the latest published release until a newer tag exists.
- `v0.2.1` is prepared/unpublished documentation and onboarding work until release.
- Dashboard, slash command, Gateway Bot, database, and hosted-service ideas are roadmap or out of scope, not current setup requirements.

## Friction Points

1. Shared docs are numerous and can feel scattered.
2. `app/` and `infra/` can confuse visitors about current scope.
3. `en-US` support can be misread as mature global support.
4. Generated `reports/` artifacts appear after validation but are not default commit candidates.
5. API credit cost warning is easy to miss if users skip CLI docs.
6. Provider credential absence can produce sparse output that still counts as a safe first-run result.
7. External adoption evidence is intentionally weak today.

## Recommended README And Doc Navigation Changes

- Keep the language gateway at the top of `README.md`.
- Keep first dry-run setup visible before Discord delivery setup.
- Link review/application artifacts from `docs/README.md`.
- Keep `reports/` ignore policy visible in README and PR template.
- Keep `app/` and `infra/` classified as legacy/prototype unless the project scope changes.
- Keep no-metric language in README, application docs, release notes, and PR template.

## Recommended Screenshots Or Demo Artifacts

Existing useful assets:

- `docs/assets/getting-started/00-repository-fork-button.png`
- `docs/assets/getting-started/01-actions-tab-workflow-list.png`
- `docs/assets/getting-started/02-secrets-new-repository-secret.png`
- `docs/assets/getting-started/06-actions-run-workflow-inputs.png`
- `docs/assets/getting-started/07-actions-artifacts-summary.png`
- `docs/assets/getting-started/08-enable-discord-delivery-variable.png`
- `docs/assets/demo/github-actions-dispatch-redacted.png`
- `docs/assets/demo/actions-summary-redacted.png`
- `docs/assets/demo/validation-report-redacted.png`
- `docs/assets/demo/discord-brief-redacted.png`

Recommended additions:

- A redacted first-fork run summary showing `dry_run=true`.
- A redacted validation failure example showing the stop-before-delivery rule.
- A redacted sparse/empty News Daily example explaining why sparse output can pass.

## Quickstart Clarity Checklist

- [x] The first required Secret is named.
- [x] Optional Discord and provider Secrets are separated from first-run setup.
- [x] Repository Variables are optional for first dry-run.
- [x] `dry_run=true` and `force_send=false` are documented.
- [x] Artifact paths are documented.
- [x] Validation failure blocks Discord delivery.
- [x] Generated reports are not committed by default.
- [x] No adoption metrics are claimed.
- [x] API credit and schedule cost warnings are visible in the reviewed docs.

## Remaining UX Risks

- First users still need GitHub Actions familiarity.
- The safest first run still requires an OpenAI API key.
- Source scarcity can make output sparse and feel like failure.
- A public user can leak secrets in issue text despite warnings; templates reduce but cannot eliminate that risk.
