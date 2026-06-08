# Legacy Document Inventory

This inventory tracks documents that were reviewed during the documentation cleanup.

It helps maintainers decide whether a document should stay active, be merged, be archived, or be removed.

## Classification

| Status | Meaning |
| --- | --- |
| Active | 현재 사용자/기여자/maintainer 흐름에서 직접 사용 |
| Canonical | 같은 주제의 기준 문서 |
| Merge | 다른 canonical 문서로 내용 통합 필요 |
| Archive | 과거 맥락 보관용, 현재 온보딩에서는 제외 |
| Remove candidate | 완전 중복, 빈 문서, 깨진 문서, 잘못된 과거 문서 |
| Removed | 이번 작업에서 삭제 완료 |

## Reviewed documents

| Document | Current role | Decision | Canonical target | Reason |
| --- | --- | --- | --- | --- |
| `README.md` | 프로젝트 랜딩과 Quick Start | Canonical | N/A | 첫 방문자에게 필요한 가치, Quick Start, 핵심 문서 진입점만 유지 |
| `docs/README.md` | 전체 문서 허브 | Canonical | N/A | 깊은 문서 링크와 사용자 목적별 읽는 순서를 제공 |
| `docs/getting-started/fork-setup.md` | fork 첫 설정 절차 | Canonical | N/A | Secrets, Variables, dry-run, artifact 확인, Discord delivery 흐름의 기준 문서 |
| `docs/getting-started/runtime-configuration.md` | runtime Variables와 Secrets 상세 | Canonical | N/A | README에서 제거한 상세 설정 표의 기준 문서 |
| `docs/getting-started/usage.md` | workflow 실행과 artifact 확인 | Canonical | N/A | 일반 실행, dry-run, Discord 전송 흐름의 기준 문서 |
| `docs/getting-started/sample-output.md` | sample output 안내 | Canonical | N/A | 예시 출력 위치와 검토 기준을 설명 |
| `docs/demo.md` | demo capture guide | Active | N/A | 공개 demo와 screenshot redaction 기준에 필요 |
| `docs/assets/demo/README.md` | demo asset 관리 | Active | N/A | demo asset 추가/교체/삭제 기준에 필요 |
| `docs/operations/daily-backend-brief.md` | Daily Backend Brief 운영 | Canonical | N/A | 후보 파일, output section, validator 조건의 기준 문서 |
| `docs/operations/daily-news-ops.md` | Korea Dev/AI News Daily 운영 | Canonical | N/A | news daily workflow 운영 기준 |
| `docs/operations/career-site-radar.md` | Backend Career Site Radar 운영 | Canonical | N/A | weekly career radar 운영 기준 |
| `docs/operations/daily-growth-ops.md` | Daily growth 운영 참고 | Active | N/A | 현재 dry-run artifact 해석과 daily growth section 운영에 사용 |
| `docs/operations/backend-growth-curriculum.md` | Backend Growth Curriculum | Active | N/A | Daily Backend Brief의 실무 충전 정책이 직접 참조하는 활성 문서 |
| `docs/operations/operations.md` | 운영 가이드 | Active | N/A | 운영 경로와 검증 명령을 묶는 maintainer 참고 문서 |
| `docs/operations/local-validation.md` | 로컬 검증 가이드 | Active | N/A | PR 전 검증 명령과 fixture 검증 기준에 필요 |
| `docs/operations/maintainer-guide.md` | maintainer 체크리스트 | Active | N/A | release, validation-before-send, secret safety 검토에 필요 |
| `docs/policies/oss-candidate-policy.md` | OSS 후보 정책 | Canonical | N/A | created_at recency, safe candidate, fallback 정책의 기준 문서 |
| `docs/policies/daily-spring-jvm-blog-topic-policy.md` | Spring/JVM 주제 정책 | Active | N/A | Daily Backend Brief 학습 주제 선택 기준에 필요 |
| `docs/policies/github-labels.md` | GitHub label 운영 기준 | Active | N/A | contributor issue/PR 분류 기준에 필요 |
| `docs/contributing/README.md` | contribution guide index | Canonical | N/A | 기여자용 세부 문서 진입점 |
| `docs/contributing/good-suggestion-criteria.md` | 좋은 제안 기준 | Active | N/A | issue template과 CONTRIBUTING에서 참조 |
| `docs/contributing/source-suggestion-guide.md` | 출처 제안 기준 | Active | N/A | source suggestion issue template에서 참조 |
| `docs/contributing/oss-candidate-guide.md` | OSS 후보 제안 기준 | Active | N/A | OSS candidate suggestion 흐름에 필요 |
| `docs/contributing/backend-career-question-guide.md` | 백엔드 커리어 질문 기준 | Active | N/A | backend career question issue form에 필요 |
| `docs/contributing/review-policy.md` | maintainer review 기준 | Active | N/A | maintainer review 기준과 automation boundary 설명에 필요 |
| `docs/project/contributor-tasks.md` | 작은 기여 후보 | Active | N/A | 신규 기여자가 첫 작업을 고르는 데 필요 |
| `docs/project/ecosystem-importance.md` | 생태계 의미와 한계 | Active | N/A | 프로젝트 포지셔닝과 과장 방지 기준에 필요 |
| `docs/project/roadmap.md` | roadmap | Canonical | N/A | 현재 범위와 planned/later 항목 구분 기준 |
| `docs/project/release-checklist.md` | release checklist | Canonical | N/A | maintainer용 v0.1.0 릴리스 점검 기준 |
| `docs/release-notes/v0.1.0.md` | release note draft | Active | N/A | 실제 release 생성 전 복사용 초안 |
| `CHANGELOG.md` | 변경 이력 | Canonical | N/A | 릴리스 변경 이력의 기준 문서 |
| `CONTRIBUTING.md` | 전체 기여 방식 | Canonical | N/A | PR/issue 기여 흐름의 기준 문서 |
| `SECURITY.md` | 보안 안내 | Canonical | N/A | secret, webhook, API key 취급의 기준 문서 |
| `SUPPORT.md` | 지원 범위 | Canonical | N/A | 질문과 버그 리포트 안내 기준 |
| `CODE_OF_CONDUCT.md` | 행동 강령 | Canonical | N/A | 커뮤니티 행동 기준 |
| `LEGACY.md` | 레거시 삭제 정책 | Active | N/A | 파일 제거 시 보수적 판단 기준으로 유지 |
| `docs/archive/README.md` | archive 안내 | Canonical | N/A | archive 문서가 현재 source of truth가 아님을 설명 |
| `docs/archive/legacy-inventory.md` | 레거시 분류표 | Canonical | N/A | 이번 cleanup 판단 근거 기록 |
| `docs/archive/oss-program-application.md` | 지원 프로그램 신청 참고 | Archive | `docs/project/ecosystem-importance.md` | 신청서 복사용 과거 맥락은 유용하지만 현재 사용자 온보딩 문서가 아님 |
| `docs/archive/open-source-readiness-review.md` | 공개 준비 검토 기록 | Archive | `docs/project/release-checklist.md` | 과거 공개 준비 판단은 유지하되 current release checklist가 기준 |
| `docs/archive/community-guide.md` | 커뮤니티 재사용 메모 | Archive | `docs/README.md` | 현재 실행/기여 흐름의 기준 문서가 아니므로 보관 |

## Merged

이번 작업에서 긴 본문 통합은 수행하지 않았습니다.

중복으로 보이던 레거시/검토 문서는 현재 canonical 문서의 source of truth가 아니므로 archive로 분리했습니다.

## Removed

이번 작업에서 삭제한 문서는 없습니다.

삭제가 애매한 문서는 archive로 이동했습니다.

## Follow-up candidates

| Document | Suggested next action | Reason |
| --- | --- | --- |
| `docs/archive/community-guide.md` | Merge or keep archived | 커뮤니티 운영 문서로 재활성화할 가치가 있는지 별도 판단 필요 |
| `docs/archive/oss-program-application.md` | Keep archived | 지원 프로그램 신청 맥락만 있어 현재 사용자 문서에는 불필요 |
| `docs/archive/open-source-readiness-review.md` | Keep archived | v0.1.0 release checklist로 현재 기준이 대체됨 |
