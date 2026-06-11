# Source Policy

This shared policy defines what makes a source acceptable for Career Feed.

Career Feed should favor reviewable, public, reliable sources over noisy or promotional feeds.

## Reliability Tiers

| Tier | Examples | Notes |
| --- | --- | --- |
| Official | vendor docs, product blogs, standards docs, official career pages | Preferred for learning references and source-of-truth links |
| Major media | established technology or business media | Useful for news context when original source is not available |
| Platform | GitHub, public hiring platforms, competition platforms | Useful when public and relevant |
| Aggregator | portals and link aggregators | Use carefully; prefer original source links |
| Unknown | unreviewed domains | Avoid until reviewed |

## Accepted Source Traits

- Publicly accessible without private credentials.
- Stable URL and clear source identity.
- Relevant to backend learning, developer news, OSS candidates, or career signals.
- Low spam or affiliate pressure.
- Respectful of rate limits and terms of use.
- Helpful to the configured locale and audience.

## Rejected Source Traits

- Requires private login or personal account context.
- Contains credentials, private Discord links, or private repository details.
- Mainly advertorial, affiliate, referral, or SEO content.
- Reposts content without a useful original source.
- Encourages investment decisions without risk context.
- Cannot be validated or reviewed by maintainers.

## Locale Expectations

`ko-KR` sources may assume Korean developer and career context.

`en-US` sources should be treated as foundation/experimental until provider quality, examples, and validation prove maturity.

Locale expansion proposals must include source review capacity, not just a list of URLs.

## News Daily Rules

News items should be developer-relevant and avoid investment advice.

Sparse or empty output is acceptable when too few sources meet quality criteria.

Do not force weak items into a brief just to hit a count.

## OSS Candidate Rules

OSS candidates must be safe for beginner review:

- open issue
- no assignee
- no linked work
- no claim comment
- recent enough by `created_at`
- maintainer or beginner-friendly signal
- scoped first action before contribution

Career Feed does not automatically comment, assign, label, claim, or open pull requests on external repositories.

## Contributor Checklist

When suggesting a source, include:

- URL
- locale
- source type
- update cadence
- reliability tier
- why it helps the target audience
- risks such as paywall, scraping restrictions, ads, duplicates, or stale content

Never include API keys, webhook URLs, tokens, private links, or personal identifiers.
