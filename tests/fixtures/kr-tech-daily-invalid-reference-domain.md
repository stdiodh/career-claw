# Career Feed - Backend Daily
기준시각: 2026-06-01 09:10:00 KST

오늘의 방향:
- Spring/JVM 주제를 작게 확인합니다.

## 1. 오늘의 Spring Boot/JVM 학습
### 주제: 조회 API에도 `@Transactional(readOnly = true)`를 붙이는 이유
- 오늘의 한 줄 질문: 조회만 하는 Service 메서드에도 트랜잭션을 명시해야 할까?
- 왜 지금 볼 만한가: JPA 조회 로직에서 트랜잭션 의도를 코드로 드러내는 연습은 실무 기본기와 연결됩니다.
- 실제 개발 문제: 조회 API에서 Entity 변경 가능성과 flush 흐름을 모르면 readOnly를 성능 옵션으로만 오해할 수 있습니다.
- 핵심 개념: `readOnly = true`는 조회 의도 표현과 최적화 힌트로 이해해야 합니다.
- 공식 문서 확인 포인트: Spring transaction read-only attribute, Hibernate dirty checking
- 30분 학습:
  - Spring transaction 문서에서 read-only 속성을 확인합니다.
  - Hibernate dirty checking 문서에서 변경 감지 흐름을 확인합니다.
- 30분 실습:
  - 조회 Service에 readOnly 적용 전후 코드를 비교합니다.
  - SQL 로그로 flush/update 여부를 기록합니다.
- 기술 블로그 제목 후보:
  1. 조회 API에도 `@Transactional(readOnly = true)`를 붙이는 이유
  2. readOnly 트랜잭션은 성능 옵션일까, 의도 표현일까?
  3. Spring Boot 조회 로직에서 readOnly 트랜잭션 확인하기
- PAAR 글 목차:
  - Problem: 조회 API 트랜잭션 적용 여부가 헷갈리는 상황을 제시합니다.
  - Analyze: readOnly와 dirty checking 흐름을 비교합니다.
  - Action: Service 예제로 SQL 로그를 비교합니다.
  - Result: readOnly의 역할과 한계를 정리합니다.
- 완료 기준: SQL 로그와 결론을 블로그 초안에 기록합니다.
- 다음에 이어서 볼 주제: 트랜잭션 전파 옵션을 작은 예제로 확인합니다.
- 레퍼런스:
  - [Spring Framework 공식 문서](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
  - [허용되지 않은 AWS 일반 페이지](https://aws.amazon.com/architecture/)

## 2. 이번 주 PS 성장 루틴

## 3. 오픈소스 기여 후보

## 4. 오늘의 백엔드 실무 충전
