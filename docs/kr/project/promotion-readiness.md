# Promotion Readiness

> Language: [한국어](./promotion-readiness.md) | [English](../../en/project/promotion-readiness.md)

이 문서는 v0.2.1 이후 Career Feed를 공개적으로 소개하기 전에 maintainer가 과장 없이 점검할 항목을 정리합니다.

목표는 blind adoption을 요구하는 것이 아니라 early OSS feedback을 안전하게 요청하는 것입니다.

## 1. Repository metadata checklist

- [ ] GitHub repository description이 프로젝트를 짧고 정확하게 설명합니다.
- [ ] social preview image가 설정되어 있고 secret, private Discord 정보, fake metric을 포함하지 않습니다.
- [ ] repository topics가 현재 범위를 반영합니다.
- [ ] README 첫 문단이 fork-based GitHub Actions, OpenAI API, Discord Webhook 기반 자동화라는 점을 분명히 설명합니다.
- [ ] `LICENSE`가 repository 루트에서 보입니다.
- [ ] `CONTRIBUTING.md`와 language별 contributing 문서가 보입니다.
- [ ] `SECURITY.md`와 language별 security 문서가 보입니다.

## 2. Launch asset checklist

- [ ] 1-line pitch를 준비했습니다.
- [ ] 3-sentence explanation을 준비했습니다.
- [ ] demo screenshot list를 준비했습니다.
- [ ] sample output link를 준비했습니다.
- [ ] known limitations를 launch copy에 포함했습니다.
- [ ] who this is for / not for를 명확히 했습니다.
- [ ] feedback을 요청하는 문구를 포함했습니다.
- [ ] adoption, downloads, stars, active users, organization usage를 주장하지 않습니다.

Demo screenshot list:

- GitHub Actions manual dry-run input
- uploaded artifact summary
- generated Backend Daily Markdown artifact
- validation report artifact
- redacted Discord output, delivery를 켠 뒤에만 사용

Sample output links:

- [Sample Output](../getting-started/sample-output.md)
- [Fresh Fork Smoke Test](../getting-started/fresh-fork-smoke-test.md)
- [Demo Guide](../demo.md)

Known limitations:

- Early Public OSS입니다.
- `ko-KR`이 기본 지원 locale입니다.
- `en-US`는 experimental foundation입니다.
- source가 부족한 날에는 sparse 또는 empty output이 정상일 수 있습니다.
- generated output은 career advice accuracy를 보장하지 않습니다.
- Discord delivery는 dry-run과 validation 검토 뒤에만 켭니다.

Who this is for:

- 백엔드 학습자
- 주니어 개발자
- Discord 스터디 그룹
- 멘토와 스터디 운영자
- fork 기반 자동화와 validation artifact를 검토하려는 OSS contributor

Who this is not for:

- 프로덕션 백엔드 runtime, framework, database를 찾는 사용자
- hosted SaaS dashboard를 기대하는 사용자
- 자동 취업 지원, 자동 OSS PR, 자동 issue claiming을 원하는 사용자
- 검토 없이 Discord에 자동으로 게시할 도구를 원하는 사용자

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
Career Feed v0.2.1 이후 공개 피드백을 받고 싶습니다. GitHub Actions, OpenAI API, Discord Webhook으로 백엔드 학습, 개발/AI 뉴스, OSS 기여 준비 자료를 dry-run artifact로 생성하고 검증하는 Early Public OSS입니다. 프로덕션 의존성이나 커리어 조언 정답지가 아니라 fork해서 검토 가능한 자동화 흐름입니다. fresh fork smoke test를 따라 보고 막히는 지점이나 source 제안을 issue로 알려 주세요.
```

### English short post

```text
Career Feed is looking for early feedback after v0.2.1. It is an Early Public OSS project that uses GitHub Actions, the OpenAI API, and Discord Webhooks to generate reviewable dry-run artifacts for backend learning, dev/AI news, and OSS contribution preparation. It is not a production dependency or career-advice oracle. Try the fresh-fork smoke test and open an issue with setup friction, artifact feedback, or source suggestions.
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
