# Roadmap Expansion Opportunities

This roadmap review separates small readiness fixes from larger product expansion ideas. It does not describe shipped behavior unless the evidence exists in repository files.

## P0: Application And Onboarding Readiness

| Item | User value | Likely files | Acceptance criteria | Validation | Codex-for-OSS strength | Beginner safe |
| --- | --- | --- | --- | --- | --- | --- |
| Collect public fork-trial report template usage | Gives reviewers evidence without fake metrics | `.github/ISSUE_TEMPLATE/fork-trial-report.yml`, `docs/en/project/adoption-evidence.md`, `docs/kr/project/adoption-evidence.md` | A public redacted issue includes workflow, locale, dry-run inputs, artifact paths, validation result, and permission to summarize | `python3 scripts/check-doc-format.py` | High | Yes |
| Keep root application packet current | Gives maintainer paste-ready and reviewer-safe application text | `docs/codex-for-oss-application.md`, `docs/README.md` | Application packet includes Korean short answers, API credit plan, claims to avoid, evidence list, reviewer concerns, final checklist | `python3 scripts/check-doc-format.py` | High | Yes |
| Keep generated report boundary visible | Prevents ignored `reports/` output from being committed accidentally | `README.md`, `.github/pull_request_template.md`, `docs/kr/getting-started/usage.md`, `docs/en/getting-started/usage.md` | PR checklist asks whether generated reports were intentionally excluded or justified | `git diff --check` | Medium | Yes |
| Add visible API credit warning | Prevents surprise costs when enabling scheduled generation | `README.md`, `docs/kr/getting-started/fork-setup.md`, `docs/en/getting-started/fork-setup.md`, `scripts/setup-fork.sh` | Users see that OpenAI generation can consume API credits and schedule should stay disabled until intentional | `python3 scripts/check-doc-format.py` | Medium | Yes |
| Keep maturity wording conservative | Prevents reviewers from reading current support as broader than evidence proves | `README.md`, `docs/project/release-v0.2.0.md`, release notes, application docs | `ko-KR` is described as the most complete supported path, `en-US` stays foundation/experimental, and no adoption claims appear without public evidence | `python3 scripts/check-doc-format.py` | High | Yes |
| Track Korean/English divergence | Prevents first-time English contributors from following stale or thinner setup and contribution docs | `.github/ISSUE_TEMPLATE/docs-improvement.yml`, `.github/pull_request_template.md`, `docs/README.md`, localized setup/support/security/contributor docs | User-facing behavior changes include a Korean/English docs check or an explicit note that only one language changed | `python3 scripts/check-doc-format.py` | Medium | Yes |

## P1: Source Quality And Provider Maturity

| Item | User value | Likely files | Acceptance criteria | Validation | Codex-for-OSS strength | Beginner safe |
| --- | --- | --- | --- | --- | --- | --- |
| Add provider output fixtures | Makes provider behavior reviewable before more locales are claimed | `tests/fixtures/**`, `scripts/collect-kr-feeds.py`, `scripts/search_providers/**`, `docs/project/provider-expansion.md` | Fixture covers provider output shape, missing credential fallback, and no secret leakage | `./scripts/validate.sh` | High | Partial |
| Improve `en-US` source review notes | Makes experimental status actionable | `configs/locales/en-US/sources.json`, `docs/en/project/provider-expansion.md`, `docs/project/source-policy.md` | Each source has reliability rationale and caveat; docs still call `en-US` experimental | `python3 scripts/check-doc-format.py` | High | Yes |
| Split provider logic in small steps | Reduces long-term collector maintenance risk | `scripts/collect-kr-feeds.py`, `scripts/search_providers/**`, `tests/**` | One provider behavior moves behind a tested provider module without changing artifact schema | `./scripts/validate.sh` | Medium | No |
| Source quality report artifact | Helps maintainers review why items were selected or skipped | `scripts/build-daily-news-shortlist.py`, `scripts/evaluate-news-daily-quality.py`, `reports/ops/**`, `docs/project/validation.md` | A report lists selected, filtered, sparse, and fallback reasons without credentials | `./scripts/validate.sh` | Medium | Partial |

## P2: Product Expansion And Ecosystem Integrations

| Item | User value | Likely files | Acceptance criteria | Validation | Codex-for-OSS strength | Beginner safe |
| --- | --- | --- | --- | --- | --- | --- |
| Additional locale template pack | Lets communities adapt Career Feed beyond `ko-KR` and experimental `en-US` | `configs/locales/{locale}/**`, `docs/project/provider-expansion.md`, `docs/kr/project/roadmap.md`, `docs/en/project/roadmap.md` | New locale has audience profile, source policy note, prompts, validation fixture, and reviewer capacity note | `./scripts/validate.sh` | Medium | Partial |
| Community template catalog | Helps new contributors suggest sources and configs safely | `docs/en/contributing/**`, `docs/kr/contributing/**`, `.github/ISSUE_TEMPLATE/source-suggestion.yml` | Catalog separates docs-only suggestions from provider-code changes and includes source reliability risks | `python3 scripts/check-doc-format.py` | Medium | Yes |
| Optional dashboard concept | Could make artifacts easier to inspect, but conflicts with current no-server scope unless carefully planned | `docs/project/roadmap.md`, future app or static artifact viewer files | Roadmap issue defines static or artifact-only approach before any server/dashboard work begins | `git diff --check` | Low | No |
| MCP/Codex integration notes | Could improve maintainer review loops and application story | `docs/codex-for-oss-application.md`, `docs/project/roadmap.md`, future workflow docs | Notes describe human-reviewed Codex use only; no external repo mutation or unchecked publishing | `python3 scripts/check-doc-format.py` | Medium | Partial |
| Maintainer automation for release review | Reduces release checklist drift | `scripts/**`, `.github/workflows/pr-checks.yml`, `docs/project/release-checklist.md` | Check confirms docs, workflows, no metrics, no generated reports staged, and no secret-like values | `./scripts/validate.sh` | High | Partial |

## Expansion Principles

- Prove current behavior with workflow, script, fixture, or doc evidence before promoting it.
- Treat each locale as a source-quality and reviewer-capacity commitment.
- Keep provider credentials as Secrets and provider names as Variables.
- Prefer sparse or empty output over low-quality forced content.
- Keep external repository interactions read-only.
- Keep generated artifacts reviewable before delivery.
- Do not introduce servers, databases, dashboards, Gateway Bots, or Slash Commands without a separate scope decision.

## Three-Release Innovation Path

Release A:

- Gather public fork-trial evidence.
- Add one provider fixture.
- Improve source-quality notes for `en-US`.

Release B:

- Split one provider into a tested module.
- Add source-quality report artifacts.
- Expand beginner contribution docs with real issue outcomes.

Release C:

- Evaluate a third locale only if reviewer capacity exists.
- Consider static artifact review UX before any hosted dashboard.
- Publish a maintainer automation checklist that supports release review and Codex application updates.
