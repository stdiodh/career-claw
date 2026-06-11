# Suggested GitHub Labels

> Language: [한국어](./github-labels.md) | [English](../../en/policies/github-labels.md)

| Label | Purpose |
| --- | --- |
| `bug` | 버그 리포트 |
| `docs` | 문서 개선 alias |
| `documentation` | 문서 개선 |
| `locale` | locale 관련 작업 |
| `provider` | provider 또는 search/source integration |
| `workflow` | GitHub Actions workflow 관련 작업 |
| `validation` | 검증 로직 또는 검증 실패 |
| `source-policy` | source reliability와 품질 정책 |
| `release` | 릴리스 planning 또는 checklist |
| `question` | 질문 또는 확인 요청 |
| `help wanted` | 외부 기여자 도움이 필요한 작은 작업 |
| `source` | 정보 출처 제안 |
| `oss-candidate` | OSS 후보 제안 |
| `good first issue` | 초보자 친화 후보 |
| `validation fixture` | 검증 fixture 추가 또는 개선 |
| `release readiness` | 릴리스 준비 작업 |
| `enhancement` | 개선 제안 |

Label은 maintainer가 GitHub UI나 `gh label create`로 수동 생성합니다. 문서 PR만으로 label이 자동 생성되지는 않습니다.

## Issue template mapping

| Template | Labels |
| --- | --- |
| 백엔드 커리어 질문 | `question` |
| 버그 리포트 | `bug` |
| 문서 개선 제안 | `documentation` |
| 정보 출처 제안 | `source`, `enhancement` |
| 깨진 링크 또는 오래된 출처 | `source`, `bug` |
| OSS 기여 후보 제안 | `oss-candidate` |
| 검증 fixture 제안 | `validation fixture`, `good first issue` |
| 릴리스 준비 점검 | `release readiness` |
| 지역 또는 언어 확장 제안 | `enhancement`, `source` |
| 기타 maintainer 질문 | `question` |

필요하면 maintainer가 GitHub UI나 `gh label create`로 수동 생성합니다. Label 생성은 브리핑 workflow 동작에 필수
조건이 아닙니다.
