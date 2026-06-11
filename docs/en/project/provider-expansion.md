# Provider Expansion

> Language: [한국어](../../kr/project/provider-expansion.md) | [English](./provider-expansion.md)

This guide describes how contributors can propose provider work without overclaiming current maturity.

For the shared baseline, see [Provider Expansion](../../project/provider-expansion.md).

## Current Provider Status

| Provider | Locale | Status |
| --- | --- | --- |
| Naver News Search | `ko-KR` | Optional credential-backed path for Korean news candidates |
| RSS / Atom | `ko-KR`, `en-US` | Active source input through locale config and collector logic |
| GitHub | OSS candidates | Active candidate path with safety validation |
| Brave Search | `en-US` | Foundation/scaffold; deeper behavior remains planned |

Provider marker modules live in `scripts/search_providers/`, but v0.2 still keeps most collection behavior in `scripts/collect-kr-feeds.py`.

## How To Propose Provider Work

Open a source/provider issue with:

- target locale
- provider name
- example public sources
- credential requirements
- expected candidate fields
- validation impact
- failure behavior when credentials are missing
- spam or low-quality source risks

Keep the first PR small. Documentation and fixtures are acceptable first steps.

## Review Criteria

Maintainers should check:

- whether the provider improves source quality for the target locale
- whether secrets remain in GitHub Secrets or environment variables
- whether missing credentials fail safely
- whether candidate output can be validated
- whether `ko-KR` compatibility behavior remains intact
- whether `en-US` is still described honestly as foundation/experimental when applicable

## Validation

Run:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```
