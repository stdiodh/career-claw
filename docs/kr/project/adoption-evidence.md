# Adoption Evidence

> Language: [한국어](./adoption-evidence.md) | [English](../../en/project/adoption-evidence.md)

이 문서는 Career Feed의 실제 사용과 피드백 신호를 안전하게 모으는 기준입니다.

현재 이 프로젝트는 넓은 adoption, downloads, stars, active users, organization usage를 주장하지 않습니다.

## Purpose

목표는 초기 사용자와 기여자가 공개 issue로 남길 수 있는 검증 가능한 피드백만 모으는 것입니다.

README, release note, application 문서에 사용할 수 있는 evidence는 public, redacted, permission-aware 상태여야 합니다.

## Acceptable evidence

다음 evidence는 사용할 수 있습니다.

- public issue feedback
- fork setup success reports
- study group trial notes
- source suggestions
- validation fixture contributions
- bug reports with artifact paths

좋은 evidence는 구체적인 workflow, locale, artifact path, dry-run 설정, validation 결과를 포함합니다.

예:

- `Backend Daily Brief`
- `ko-KR`
- `dry_run=true`, `force_send=false`
- `reports/briefs/ko-KR/backend-daily.md`
- `reports/ops/ko-KR/backend-daily-validation-report.md`

## Evidence not acceptable

다음 항목은 README, application 문서, release 문구에 사용하지 않습니다.

- fake stars
- fake downloads
- private user claims without permission
- private Discord screenshots
- API keys or webhook URLs
- unverifiable adoption stories

private Discord channel 이름, 초대 링크, 사용자 이름, 프로필 이미지, 메시지 screenshot은 공개 evidence로 받지 않습니다.

## Suggested issue format: fork trial report

제목:

```text
[Fork trial] Backend Daily dry-run on ko-KR
```

본문:

```markdown
## Trial context

- Repository state: fresh fork / existing fork
- Guide used: Fresh Fork Smoke Test / Fork Setup Guide / other
- Locale: ko-KR
- Workflow: Backend Daily Brief

## First run settings

- Repository Secret configured: OPENAI_API_KEY
- Repository Variables added: none / list overrides used
- dry_run=true
- force_send=false
- Discord delivery stayed disabled

## Artifact paths checked

- reports/briefs/ko-KR/backend-daily.md
- reports/ops/ko-KR/backend-daily-validation-report.md
- reports/ops/ko-KR/backend-daily-run-summary.md
- reports/candidates/ko-KR/oss-contribution-opportunities.json

## Result

- What worked:
- What was confusing:
- Validation result:
- Discord delivery stayed disabled: yes/no

## Safety

- I removed API keys, webhook URLs, tokens, private links, and private identifiers.
- Maintainers may summarize this public issue in docs: yes/no
```

## Suggested issue format: study group trial feedback

제목:

```text
[Study group feedback] Backend Daily dry-run review
```

본문:

```markdown
## Trial context

- Group type: Discord study group / mentoring group / small peer group
- Private names, invite links, and screenshots omitted: yes/no
- Workflow reviewed:
- Locale:

## How the artifact was used

- Study prompt review:
- Discussion or mentoring use:
- Source or topic quality:
- Missing or confusing sections:

## Safety and permission

- No private Discord screenshots are included.
- No API keys, webhook URLs, tokens, private links, or private identifiers are included.
- Maintainers may summarize this public issue in docs: yes/no
```

## Maintainer review checklist

Before accepting evidence into README, application docs, release notes, or ecosystem docs, check the following.

- [ ] Evidence is from a public issue, pull request, or public discussion.
- [ ] The reporter did not include API keys, webhook URLs, tokens, private links, private screenshots, or private identifiers.
- [ ] Any study group or user claim has explicit permission to summarize.
- [ ] The evidence includes enough context to verify workflow, locale, artifact path, or validation result.
- [ ] The summary does not imply broad adoption, production usage, downloads, stars, active users, or organization usage.
- [ ] The wording says what happened in the trial, not what all users experience.
- [ ] Sparse source data, empty safe candidate days, and validation failures are treated as valid feedback signals.
- [ ] Private screenshots are not copied into repository docs.

## Safe summary wording

Use careful wording.

Acceptable:

```text
A public fork trial report confirmed that a maintainer could complete a ko-KR Backend Daily dry-run and review generated artifacts without enabling Discord delivery.
```

Not acceptable:

```text
Many teams use Career Feed in production.
```

Do not turn one public trial into adoption metrics.
