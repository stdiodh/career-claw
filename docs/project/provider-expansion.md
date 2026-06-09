# Provider Expansion

This shared guide describes the v0.2 provider direction without claiming more maturity than the repository proves.

## Current Status

| Provider | Locale role | Status |
| --- | --- | --- |
| Naver News Search | `ko-KR` news enrichment | Optional credential-backed path in the current collector |
| RSS / Atom | `ko-KR`, `en-US` source input | Active source input through locale config and collector logic |
| GitHub | OSS candidate discovery | Active candidate path with safety validation |
| Brave Search | `en-US` search preset | Foundation/scaffold with optional credential warning; deeper collection behavior remains planned |

Provider marker modules exist in `scripts/search_providers/`.

The v0.2 collector still keeps most behavior in `scripts/collect-kr-feeds.py` for compatibility.

## Locale Relationship

Provider presets are configured by locale:

- `CAREER_FEED_SEARCH_PROVIDERS_KO_KR=naver,rss,github`
- `CAREER_FEED_SEARCH_PROVIDERS_EN_US=brave,rss,github`

Provider names are Variables.

Provider credentials are Secrets.

`ko-KR` should not require Brave Search. `en-US` should not require Naver credentials.

## Expansion Rules

A provider proposal should include:

- target locale
- provider name
- credential requirements
- data shape
- rate-limit or terms-of-use risks
- source quality risks
- artifact paths affected
- validation commands
- fallback behavior when credentials are missing

Do not add a provider only because an API exists. The provider must improve source quality for the target workflow.

## Output Expectations

Provider output should preserve enough metadata for review:

- title
- canonical URL
- source label
- summary or snippet
- published or observed timestamp when available
- reliability tier when applicable
- reason the candidate is relevant

Generated candidate JSON must not contain credentials or webhook URLs.

## Validation Expectations

Before a provider PR is reviewable, run:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```

Provider behavior changes should add or update a small fixture, smoke check, or source-policy note.

## Out Of Scope For v0.2.x

- Treating provider marker modules as a complete provider system.
- Removing `ko-KR` legacy behavior to simplify provider code.
- Claiming mature `en-US` source quality before validation and source review prove it.
- Adding scraping that ignores robots, paywalls, private APIs, or login-only data.
