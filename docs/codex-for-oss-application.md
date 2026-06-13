# Codex for OSS Application Packet

This is the root application packet for Career Feed. It is written for the maintainer to review before submitting an OpenAI Codex for OSS application.

## Current Position

Career Feed is an Early Public OSS repository for fork-based GitHub Actions automation. It uses the OpenAI API to generate reviewable Markdown drafts for backend learning, developer news, OSS contribution preparation, and career-source checks. Discord Webhook delivery is optional and gated by dry-run defaults, validation, delivery flags, webhook availability, and delivery locks.

The project should be positioned as maintainable, safe, and reviewable early OSS. It should not be positioned as a broadly adopted product or production dependency.

## Paste-Ready Korean Answers

Each answer below is intended to stay under 500 characters.

### Project Suitability

```text
Career Feed는 Early Public OSS 단계의 fork 기반 GitHub Actions 자동화입니다. 백엔드 학습, 개발/AI 뉴스, OSS 후보 검토, 커리어 신호를 OpenAI API로 Markdown artifact 초안으로 만들고, validation과 dry-run 검토 뒤에만 선택적으로 Discord Webhook 전송을 허용합니다. 넓은 사용 지표는 아직 주장하지 않습니다.
```

### API Credit Use

```text
API credits는 maintainer가 검토할 수 있는 Daily Backend Brief, 개발/AI 뉴스 요약, OSS 후보 note, validation summary, 문서 일관성 점검, provider/source review 초안 생성에 사용합니다. 외부 저장소 자동 comment, PR, assign, label 변경이나 검토 없는 Discord 전송에는 사용하지 않습니다.
```

### Maintenance Workflow

```text
유지보수는 작은 PR, issue template, validation fixture, release checklist, dry-run artifact review를 중심으로 합니다. 기본 검증은 git diff --check, python3 scripts/check-doc-format.py, ./scripts/validate.sh이며 generated reports는 기본 commit 대상이 아닙니다.
```

### Honest Metrics Statement

```text
현재 Career Feed는 stars, forks, downloads, active users, organization usage, production usage 같은 adoption metric을 주장하지 않습니다. 신청서에는 repository 파일, workflow, validation, fixture, redacted demo, 공개 issue feedback처럼 검증 가능한 근거만 사용합니다.
```

## Honest Lack-Of-Metric Language

Use this wording:

- "No adoption metrics are claimed yet."
- "The project is fork-ready and seeking early public feedback."
- "The repository evidence is workflow, validation, documentation, fixture, and redacted demo evidence."
- "Public fork-trial reports can become future evidence only after redaction and permission checks."

Do not turn private Discord use, local tests, or generated reports into public adoption claims.

## Second-Pass Rejection Risk Review

| Rejection risk | Current strength | What to say honestly | What not to say |
| --- | --- | --- | --- |
| Weak usage evidence | Weak | No adoption metrics are claimed yet; the repo is fork-ready and seeking public fork-trial feedback. | Do not imply active users, teams, organizations, production use, downloads, or stars. |
| Weak ecosystem impact | Moderate | Career Feed helps backend learners and study groups turn learning, news, OSS prep, and career-source checks into reviewable artifacts. | Do not call it ecosystem-critical infrastructure or a widely used dependency. |
| Unclear maintenance workflow | Moderate | Maintenance is based on small PRs, issue templates, validation fixtures, PR checks, release checklist, and dry-run artifact review. | Do not claim public triage history or recurring outside contributions unless public evidence exists. |
| Unclear API-credit use | Moderate | Credits support maintainer-reviewed drafts, source summaries, validation summaries, release notes, and Korean/English docs consistency review. | Do not present credits as a way to generate fake evidence, unchecked posts, or external repo automation. |
| Generated-content safety | Moderate | Output is reviewable Markdown guarded by validation and delivery controls. | Do not describe generated output as final career advice or final OSS maintainer judgment. |
| Locale maturity | Mixed | `ko-KR` is the most complete supported path; `en-US` is a v0.2 foundation/experimental preset. | Do not claim mature global provider coverage. |

## Evidence Strength Table

| Claim area | Evidence available now | Evidence still missing |
| --- | --- | --- |
| Repository readiness | README, workflow files, validation scripts, tests, fixtures, docs gateway, issue templates, PR template | Independent public fork-trial reports |
| Safety controls | dry-run defaults, validation, delivery flags, webhook Secret checks, delivery locks, no external repo mutation policy | Public incident/triage history showing the controls in practice |
| Maintenance process | release checklist, changelog, PR checks, issue templates, contributor task docs | Public examples of issue triage and outside PR review |
| API-credit purpose | application packet, localized application docs, source-policy docs, validation docs | Actual credit allocation details from the application form |
| Ecosystem impact | backend learner and study-group workflow docs, demo assets, examples | Public user feedback that says the workflow helped a real fork or group |

Before submitting, the maintainer should treat any public fork-trial issue or study-group feedback as optional evidence only after redaction, permission, and no-metric wording checks.

## File Evidence List

Application evidence should cite exact files:

- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `.github/workflows/backend-daily.yml`
- `.github/workflows/dev-news-daily.yml`
- `.github/workflows/backend-career-weekly.yml`
- `.github/workflows/pr-checks.yml`
- `.github/ISSUE_TEMPLATE/fork-trial-report.yml`
- `.github/ISSUE_TEMPLATE/source-suggestion.yml`
- `.github/ISSUE_TEMPLATE/validation-fixture.yml`
- `.github/pull_request_template.md`
- `scripts/validate.sh`
- `scripts/check-doc-format.py`
- `scripts/should-run-now.py`
- `scripts/validate-career-feed-brief.py`
- `tests/test_oss_reliability_gate.py`
- `tests/fixtures/**`
- `docs/oss-readiness-review.md`
- `docs/ux-onboarding-review.md`
- `docs/roadmap-expansion-opportunities.md`
- `docs/project/source-policy.md`
- `docs/project/provider-expansion.md`
- `docs/en/project/adoption-evidence.md`
- `docs/kr/project/adoption-evidence.md`
- `docs/assets/demo/**`

## API Credit Use Plan

Credits should be used for maintainer-reviewed work:

- Daily Backend Brief draft generation.
- Dev/AI news candidate summarization.
- Spring Boot, JVM, Kotlin, backend topic prioritization.
- OSS candidate note drafting and safety explanation.
- Validation summary drafting.
- Release checklist and changelog review.
- Documentation consistency checks across Korean and English docs.
- Provider/source review notes.
- Future locale prompt review when reviewer capacity exists.

Credits should not be used for:

- unchecked public posting.
- external repository comments.
- automatic external pull requests.
- external issue assignment.
- external label changes.
- Discord delivery without dry-run review and validation.
- generating fake usage or adoption evidence.

## Human-Only Fields Checklist

Before submission, the maintainer must fill or verify:

- [ ] Applicant name and account identity.
- [ ] Repository URL.
- [ ] OpenAI account or organization identifier, if the form asks for it.
- [ ] Contact email.
- [ ] Any billing or credit-allocation fields.
- [ ] Whether the latest tag should remain `v0.2.0` or a prepared `v0.2.1` release should be published first.
- [ ] Whether screenshots are redacted and acceptable to reference.
- [ ] Whether any public fork-trial or feedback issue can be summarized.

## Claims To Avoid

Avoid these claims unless future public evidence proves them:

- broad adoption.
- production usage.
- ecosystem-critical dependency status.
- mature global provider coverage.
- mature `en-US` source quality.
- active user counts.
- stars, forks, or download totals.
- organization usage.
- that generated output is final career advice.
- that OSS candidate recommendations replace external maintainer judgment.
- that Codex/OpenAI output is posted without human review.

## Reviewer Concerns And Responses

| Reviewer concern | Honest response |
| --- | --- |
| "Is this widely used?" | No usage metric is claimed. The application is based on repository readiness, validation, docs, and safe maintainer workflow. |
| "Is this just a newsletter generator?" | Newsletter automation is one adjacent category, but Career Feed combines fork setup, locale routing, dry-run artifacts, validation, OSS candidate gates, and Discord delivery controls. |
| "Can it spam Discord?" | Daily workflows default to `dry_run=true`; delivery also requires the delivery flag, webhook Secret, validation pass, runtime gate, and lock policy. |
| "Can it mutate external OSS repositories?" | No. It does not auto-comment, auto-PR, auto-assign, or auto-label external repositories. |
| "Is `en-US` mature?" | No. It is a v0.2 foundation/experimental preset. |
| "Why are credits useful?" | They reduce maintainer workload for reviewable drafts, source summaries, validation summaries, and documentation review. |
| "What evidence proves maintainability?" | `scripts/validate.sh`, PR checks, fixtures, release docs, issue templates, and no-metric guardrails. |

## Final Submission Checklist

- [ ] `git diff --check` passes.
- [ ] `python3 scripts/check-doc-format.py` passes.
- [ ] `./scripts/validate.sh` passes or any sandbox-specific retry is documented.
- [ ] Korean paste-ready answers are still under 500 characters if the form requires that limit.
- [ ] No secret values or webhook URLs appear in docs, screenshots, reports, or issues.
- [ ] No generated `reports/` artifacts are staged.
- [ ] No adoption metric is claimed without public evidence.
- [ ] `ko-KR` is described as the default supported locale.
- [ ] `en-US` is described as foundation/experimental.
- [ ] Provider modules are not overclaimed as a mature provider system.
- [ ] Human-only fields are filled by the maintainer.
