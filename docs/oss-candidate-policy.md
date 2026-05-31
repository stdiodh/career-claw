# OSS 후보 저장소 정책

Daily Backend Brief의 OSS 후보는 `configs/oss-repositories.json`에 등록된 Spring/JVM/Kotlin 백엔드 생태계 저장소만 대상으로 합니다. 저장소를 많이 늘리기보다, 저장소별로 주니어가 검토해도 되는 이슈 유형을 명확히 적어 scoring 근거로 사용합니다.

## 저장소 profile 필드

- `repository`: GitHub `owner/name` 형식입니다.
- `priority`: `A`, `B`, `C` 중 하나입니다. `A`는 Daily Backend Brief에 가장 적합한 백엔드 학습 가치가 있는 저장소입니다. `B`는 적합하지만 범위를 더 조심해야 하는 저장소입니다. `C`는 생태계 연관성은 있으나 첫 기여 난이도 검증이 더 필요한 저장소입니다.
- `ecosystem_tags`: Spring, JVM, Kotlin, observability, database 같은 생태계 분류입니다.
- `beginner_labels`: 해당 저장소에서 beginner-friendly 근거로 볼 수 있는 label입니다.
- `preferred_contribution_types`: `docs`, `test`, `sample`, `bug-repro` 중 추천할 수 있는 기여 유형입니다.
- `avoid_labels`: 있으면 추천하지 않는 label입니다.
- `avoid_title_keywords`: 제목에 있으면 추천하지 않는 키워드입니다.
- `contribution_guide`: 기여 전 확인할 가이드입니다.
- `local_check_hints`: 첫 30분 로컬 확인에 쓸 명령이나 확인 경로입니다.
- `docs_or_test_hints`: 문서 또는 테스트 위치를 좁히는 힌트입니다.
- `junior_notes`: 왜 주니어 백엔드 개발자에게 적합하거나 조심해야 하는지 적습니다.

## Scoring 원칙

- priority `A`는 가장 큰 가점을 받고, `B`는 작은 가점을 받으며, `C`는 가점을 주지 않습니다.
- 저장소별 `beginner_labels`가 붙은 이슈는 beginner-friendly 근거로 가점 처리합니다.
- 이슈의 contribution type이 저장소별 `preferred_contribution_types`에 포함되어야 추천 후보가 될 수 있습니다.
- `avoid_labels` 또는 `avoid_title_keywords`에 걸리면 백엔드 관련 이슈여도 추천하지 않습니다.
- 후보 JSON에는 `repository_priority`, `repository_ecosystem_tags`, `repository_local_check_hints`, `repository_docs_or_test_hints`, `repository_junior_notes`, `junior_fit_evidence`를 남겨 Markdown 생성과 validator가 근거를 확인할 수 있게 합니다.

## 유지보수 기준

- 저장소 추가보다 기존 저장소 profile의 label과 힌트를 먼저 보강합니다.
- Secret, token, Webhook URL, 실제 credential 값은 config에 넣지 않습니다.
- GitHub issue에는 댓글, assign, label 변경 같은 mutation을 하지 않습니다.
- OpenJDK/JBS는 참고 모델로만 사용하고 직접 수집하지 않습니다.
