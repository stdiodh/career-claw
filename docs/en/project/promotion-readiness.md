# Promotion Readiness

> Language: [한국어](../../kr/project/promotion-readiness.md) | [English](./promotion-readiness.md)

This document helps the maintainer promote Career Feed honestly for the v0.2.1 release.

The goal is to ask for early OSS feedback, not blind adoption.

## 1. Repository metadata checklist

- [ ] GitHub repository description is clear and accurate.
- [ ] Social preview image is configured and does not include secrets, private Discord details, or fake metrics.
- [ ] Repository topics match the current scope.
- [ ] README first paragraph clearly says this is fork-based GitHub Actions, OpenAI API, and Discord Webhook automation.
- [ ] `LICENSE` is visible at the repository root.
- [ ] `CONTRIBUTING.md` and localized contributing docs are visible.
- [ ] `SECURITY.md` and localized security docs are visible.

## 2. Launch asset checklist

- [ ] 1-line pitch is ready.
- [ ] 3-sentence explanation is ready.
- [ ] Demo screenshot list is ready.
- [ ] Sample output links are ready.
- [ ] Known limitations are included in launch copy.
- [ ] Who this is for / not for is clear.
- [ ] The copy asks for feedback.
- [ ] The copy does not claim adoption, downloads, stars, active users, or organization usage.

Demo screenshot list:

- GitHub Actions manual dry-run input
- uploaded artifact summary
- generated Backend Daily Markdown artifact
- validation report artifact
- redacted Discord output, only after delivery has been enabled

Sample output links:

- [Sample Output](../getting-started/sample-output.md)
- [Fresh Fork Smoke Test](../getting-started/fresh-fork-smoke-test.md)
- [Demo Guide](../demo.md)

Known limitations:

- It is Early Public OSS.
- `ko-KR` is the default supported locale.
- `en-US` is an experimental foundation.
- Sparse or empty output can be normal when source quality is insufficient.
- Generated output does not guarantee career advice accuracy.
- Discord delivery should be enabled only after dry-run and validation review.

Who this is for:

- backend learners
- junior developers
- Discord study groups
- mentors and study maintainers
- OSS contributors who want to review fork-based automation and validation artifacts

Who this is not for:

- users looking for a production backend runtime, framework, or database
- users expecting a hosted SaaS dashboard
- users looking for automatic job applications, automatic OSS PRs, or automatic issue claiming
- users who want unchecked automatic Discord posting

## 3. Suggested GitHub topics

- `github-actions`
- `openai`
- `codex`
- `discord-webhook`
- `backend`
- `java`
- `kotlin`
- `learning`
- `career`
- `oss`
- `ko-kr`
- `developer-tools`

## 4. Honest launch copy

### Korean short post

```text
Career Feed v0.2.1 공개 피드백을 받고 싶습니다. GitHub Actions, OpenAI API, Discord Webhook으로 백엔드 학습, 개발/AI 뉴스, OSS 기여 준비 자료를 dry-run artifact로 생성하고 검증하는 Early Public OSS입니다. 프로덕션 의존성이나 커리어 조언 정답지가 아니라 fork해서 검토 가능한 자동화 흐름입니다. fresh fork smoke test를 따라 보고 막히는 지점이나 source 제안을 issue로 알려 주세요.
```

### English short post

```text
Career Feed v0.2.1 is looking for early feedback. It is an Early Public OSS project that uses GitHub Actions, the OpenAI API, and Discord Webhooks to generate reviewable dry-run artifacts for backend learning, dev/AI news, and OSS contribution preparation. It is not a production dependency or career-advice oracle. Try the fresh-fork smoke test and open an issue with setup friction, artifact feedback, or source suggestions.
```

### Hacker News Show HN style title

```text
Show HN: Career Feed - fork-based GitHub Actions briefs for backend learning
```

### Product Hunt style tagline

```text
Reviewable backend learning and OSS prep briefs from a GitHub Actions fork.
```

## 5. What not to say

- Do not claim broad adoption.
- Do not claim career advice accuracy.
- Do not claim autonomous OSS contribution.
- Do not claim production dependency status.
- Do not claim stars, downloads, active users, or organization usage unless public evidence exists and the maintainer has permission to summarize it.
- Do not imply generated output can replace mentors, official docs, maintainers, or personal judgment.

## Pre-post checklist

- [ ] `python3 scripts/check-doc-format.py` passed.
- [ ] `git diff --check` passed.
- [ ] README links still work.
- [ ] Sample output links still work.
- [ ] Screenshots are redacted and do not include private Discord names, webhook URLs, API keys, tokens, private repositories, or personal identifiers.
- [ ] Promotion copy asks for feedback, not blind adoption.
- [ ] Adoption evidence follows [Adoption Evidence](./adoption-evidence.md).
