# Daily Backend Brief

Daily Backend Brief는 평일 오전에 백엔드 학습, PS 루틴, OSS 기여 후보, 실무 충전 내용을 생성해 Discord로 전송합니다.

## 실행 구성

| 항목 | 값 |
| --- | --- |
| workflow | `.github/workflows/kr-tech-daily.yml` |
| prompt | `.github/codex/prompts/kr-tech-daily-brief.md` |
| collector | `python3 scripts/collect-kr-feeds.py --mode daily-backend` |
| validator | `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-daily.md --type daily-tech --candidates-dir reports/candidates` |
| report | `reports/briefs/kr-tech-daily.md` |
| Discord secret | `DISCORD_WEBHOOK_KR_TECH_DAILY` |
| delivery lock | `career-feed-backend-sent-${KST_DATE}` |
| 운영 요약 | `reports/ops/backend-daily-run-summary.json`, `reports/ops/backend-daily-run-summary.md` |

## 후보 파일

Daily Backend Brief는 아래 후보 JSON을 입력으로 사용합니다.

- `reports/candidates/spring-study-topic.json`
- `reports/candidates/ps-weekly-routine.json`
- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/candidates/backend-practical-knowledge.json`
- `reports/candidates/cs-core-daily-topic.json`
- `reports/candidates/backend-term-daily.json`

## 출력 섹션

- 오늘의 Spring Boot/JVM 학습
- 이번 주 PS 성장 루틴
- 오픈소스 기여 후보 또는 OSS 기여 준비 루틴
- 오늘의 백엔드 실무 충전

## Spring/JVM 학습 정책

- `spring-study-topic.json`은 `spring-jvm-study-topics` 카테고리에서 생성하며 Naver query를 사용하지 않습니다.
- Spring 공식 블로그, Spring 문서, OpenJDK/Inside Java, Micrometer/OpenTelemetry 등 공식·표준 레퍼런스를 우선합니다.
- 매일 하나의 작은 Kotlin/Spring Boot/JVM/DB/Cloud/운영 개념을 고릅니다.
- 단순 링크 추천이 아니라 문제 상황, 30분 학습, 30분 실습, PAAR 글 목차를 함께 제공합니다.
- 고정 2주 커리큘럼이 아니라 KST 기준 후보와 공식 레퍼런스를 바탕으로 동적으로 생성합니다.
- `data/spring-jvm-blog-topic-progress.json`으로 최근 7일 내 같은 track/title 반복을 피합니다.

상세 기준은 [Spring/JVM 블로그 주제 정책](./daily-spring-jvm-blog-topic-policy.md)을 따릅니다.

## 실무 충전 정책

- `backend-practical-knowledge.json`, `cs-core-daily-topic.json`, `backend-term-daily.json`은 계속 생성합니다.
- 최종 출력에서는 하나의 실무 충전 카드로 합칩니다.
- 실무 상황 하나를 중심으로 CS Core와 백엔드 용어를 연결하고, 30분 안에 확인 가능한 작은 실습으로 마무리합니다.
- CS Core topic은 `configs/backend-core-cs-curriculum.json`에서 KST 날짜 기반으로 선택합니다.
- 백엔드 용어는 `configs/backend-terms-glossary.json`에서 KST 날짜 기반으로 선택합니다.

상세 기준은 [Backend Growth Curriculum](./backend-growth-curriculum.md)을 따릅니다.

## OSS 후보 정책

- 매 실행마다 현재 GitHub issue 상태를 확인한 뒤 추천합니다. 고정 issue 번호를 추정하지 않습니다.
- primary 저장소는 Spring Security, Spring REST Docs, Spring Boot를 먼저 확인합니다.
- 이후 Gradle, Ktor Documentation, Quarkus, Testcontainers Java, Micronaut Core, Spring Framework 순서로 확장합니다.
- maintainer/member/collaborator가 올렸거나 maintainer가 초보자용으로 분류한 open issue만 추천합니다.
- assignee가 있거나 linked PR/branch가 있거나 누군가 댓글로 작업 의사를 밝힌 issue는 추천하지 않습니다.
- GitHub GraphQL 기반 linked work 확인이 실패하거나 불완전하면 추천하지 않습니다.
- 안전한 후보가 없으면 특정 issue를 추천하지 않고 OSS 기여 준비 루틴을 출력합니다.
- 첫 30분 액션은 읽기, 재현, 문서 위치 확인, 로컬 빌드 확인처럼 PR 전 확인 행동으로 제한합니다.

저장소 profile, scoring, diagnostics, safe candidate gate는 [OSS 후보 저장소 정책](./oss-candidate-policy.md)을 따릅니다.

## Validator 조건

Daily Backend validator는 다음을 확인합니다.

- Spring/JVM 학습과 실무 충전 링크가 허용 도메인인지 확인합니다.
- 포털/언론 도메인을 Spring/JVM 학습과 실무 충전 레퍼런스로 쓰면 실패합니다.
- Markdown의 OSS issue URL이 `kr-oss-contribution-opportunities.json`의 `safe_to_recommend=true` 후보 URL과 다르면 실패합니다.
- PR 생성, 전체 구현, 전체 리팩터링처럼 첫 30분 액션 범위를 넘는 표현을 거부합니다.

운영 artifact 해석은 [Daily Growth Ops](./daily-growth-ops.md)를 봅니다.

