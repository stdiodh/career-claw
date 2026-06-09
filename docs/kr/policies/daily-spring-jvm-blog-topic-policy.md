# Daily Spring/JVM Blog Topic Policy

> Language: [한국어](./daily-spring-jvm-blog-topic-policy.md) | [English](../../en/policies/daily-spring-jvm-blog-topic-policy.md)

Daily Backend Brief의 1번 `오늘의 Spring Boot/JVM 학습` 섹션을 하루 1개 기술 블로그 주제로 운영하기 위한 기준입니다.

## 목적

- 매일 하나의 작은 Kotlin/Spring Boot/JVM/DB/Cloud/운영 개념을 추천합니다.
- 단순 링크 모음이 아니라 30~60분 안에 학습, 실습, 기술 블로그 초안 작성까지 이어지게 합니다.
- 고정 2주 커리큘럼이나 Day 1/Day 2 일정표를 만들지 않고, KST 실행 시점의 후보와 공식 레퍼런스를 기준으로 동적으로 생성합니다.

## 주제 선택 기준

- 하루에 한 주제만 선택합니다.
- 30분 학습과 30분 실습으로 확인 가능한 작은 개념이어야 합니다.
- Kotlin/Spring Boot 백엔드 주니어가 실제 API, DB, 운영, 보안, 테스트, 배포에서 마주칠 수 있는 문제와 연결합니다.
- 최근 12개월 내 공식 문서나 릴리즈 노트 변화가 있으면 가점으로 보되, 오래 가는 백엔드 기본기도 허용합니다.
- 후보 제목이 기사형이거나 큰 개념이면 그대로 쓰지 않고 작은 블로그 주제로 좁힙니다.
- `data/spring-jvm-blog-topic-progress.json`의 최근 7일 기록을 보고 같은 track 또는 title 반복을 피합니다.

## 후보 JSON 구조

`reports/candidates/spring-study-topic.json`은 `today` 객체에 다음 필드를 포함합니다.

- `track`
- `level`
- `one_line_question`
- `problem_situation`
- `official_doc_keywords`
- `learning_steps_30m`
- `practice_steps_30m`
- `blog_title_candidates`
- `paar_outline`
- `done_criteria`
- `next_topic`

필수 필드를 채우지 못하거나 최근 7일 회피 조건 때문에 fallback을 쓰면 `diagnostics.fallback_used`와
`diagnostics.fallback_reasons`에 이유를 남깁니다.

## 제외 기준

- 고정 2주 계획, 14일 커리큘럼, Day 1/Day 2 목록
- Spring Boot 완전 정복, JVM 총정리, Kafka 전체 구조처럼 책 목차형 주제
- 실습 없는 트렌드 설명
- 포털 검색 결과, 일반 언론 기사, 홍보성 글 기반 주제
- 문제 상황 없이 블로그 제목만 있는 주제

## PAAR 출력 규칙

- Problem: 실제 개발 중 생길 수 있는 혼란, 장애, 유지보수 문제를 제시합니다.
- Analyze: 공식 문서 기반으로 원인과 선택지를 분석합니다.
- Action: 작은 코드, 설정, 로그, 테스트, curl, DB 쿼리 등 손으로 확인 가능한 행동을 제시합니다.
- Result: 결과, 트레이드오프, 실무 판단 기준, 다음 학습을 정리합니다.

## 30분 학습/실습 기준

- 30분 학습은 공식 문서에서 확인할 키워드와 읽기 목표를 2개 이상 행동으로 쪼갭니다.
- 30분 실습은 손으로 확인 가능한 행동 2개 이상이어야 합니다.
- 좋은 실습은 SQL 로그 비교, 테스트 추가, 설정 변경, actuator endpoint 확인, curl 요청 비교처럼 결과가 남습니다.
- 나쁜 실습은 “공부한다”, “예제를 구현한다”, “문서를 읽는다”처럼 확인 결과가 불분명합니다.

## 허용 레퍼런스 정책

- 우선순위는 공식 문서, 표준 문서, 릴리즈 노트입니다.
- Spring, Hibernate, OpenJDK, Kotlin 공식 문서, Gradle, Micrometer, OpenTelemetry, Docker,
  Kubernetes, 주요 Cloud 공식 문서를 우선합니다.
- AWS는 `docs.aws.amazon.com` 문서를 우선하며 `aws.amazon.com` 전체 도메인을 일반 허용하지 않습니다.
- 보조 레퍼런스는 신뢰 가능한 엔지니어링 블로그만 허용합니다.
- Naver 뉴스/검색/블로그, 일반 언론, 홍보성 페이지는 1번 섹션 레퍼런스로 사용하지 않습니다.
- 단, `d2.naver.com`은 엔지니어링 블로그로 허용합니다.

## 예시

좋은 주제:

- 조회 API에도 `@Transactional(readOnly = true)`를 붙이는 이유
- Actuator health endpoint를 운영에서 그대로 노출하면 왜 위험할까?
- Testcontainers로 Repository 테스트의 DB 차이를 어떻게 줄일까?

나쁜 주제:

- Spring Transaction 완전 정복
- Spring Boot 운영 모니터링 총정리
- JVM 전체 구조 마스터하기

## Validator 품질 기준

Daily Backend validator는 1번 섹션에서 다음을 확인합니다.

- `## 1. 오늘의 Spring Boot/JVM 학습` 섹션 존재
- 정확히 하나의 `### 주제` 존재
- 오늘의 한 줄 질문, 실제 개발 문제, 30분 학습, 30분 실습, 기술 블로그 제목 후보, PAAR 글 목차, 완료 기준, 레퍼런스 필드 존재
- 기술 블로그 제목 후보 3개 존재
- PAAR 글 목차에 Problem, Analyze, Action, Result 존재
- 30분 학습과 30분 실습에 각각 2개 이상의 구체적 행동 존재
- Day 1, Day 2, 2주, 14일, 커리큘럼 전체 같은 고정 일정 표현 금지
- 완전 정복, 총정리, 전체 구조, 마스터하기 같은 큰 제목 표현 금지
- 레퍼런스 URL이 허용 도메인이며 포털/언론 도메인이 아님
