# Provider Expansion

> Language: [한국어](./provider-expansion.md) | [English](../../en/project/provider-expansion.md)

이 문서는 현재 provider maturity를 과장하지 않으면서 provider 확장을 제안하는 방법을 설명합니다.

공통 baseline은 [Provider Expansion](../../project/provider-expansion.md)을 참고하세요.

## Current Provider Status

| Provider | Locale | Status |
| --- | --- | --- |
| Naver News Search | `ko-KR` | 한국 뉴스 후보를 보강하는 optional credential-backed path |
| RSS / Atom | `ko-KR`, `en-US` | locale config와 collector logic을 통한 active source input |
| GitHub | OSS candidates | safety validation이 있는 active candidate path |
| Brave Search | `en-US` | foundation/scaffold이며 deeper behavior는 planned work |

Provider marker module은 `scripts/search_providers/` 아래에 있지만, v0.2에서는 대부분의 수집 동작이 아직 `scripts/collect-kr-feeds.py`에 남아 있습니다.

## How To Propose Provider Work

source/provider issue에는 아래 내용을 포함해 주세요.

- target locale
- provider name
- 공개 source 예시
- credential requirement
- expected candidate fields
- validation impact
- credential이 없을 때의 failure behavior
- spam 또는 low-quality source 위험

첫 PR은 작게 유지합니다. 문서와 fixture만 추가하는 것도 좋은 첫 단계입니다.

## Review Criteria

Maintainer는 아래를 확인합니다.

- provider가 target locale의 source quality를 실제로 높이는지
- secret이 GitHub Secrets 또는 환경변수에만 남는지
- credential이 없을 때 안전하게 skip되는지
- candidate output을 검증할 수 있는지
- `ko-KR` compatibility behavior가 유지되는지
- 필요한 경우 `en-US`가 foundation/experimental로 정직하게 설명되는지

## Validation

검증 명령:

```bash
git diff --check
python3 scripts/check-doc-format.py
./scripts/validate.sh
```
