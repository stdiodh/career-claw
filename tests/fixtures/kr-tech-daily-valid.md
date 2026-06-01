# Career Feed - Backend Daily
기준시각: 2026-05-28 09:10:00 KST

오늘의 방향:
- API 버전 호환성과 HTTP 재시도 의미를 작게 검증하며 해시 루틴을 이어갑니다.

## 1. 오늘의 Spring Boot/JVM 학습
### 주제: 조회 API에도 `@Transactional(readOnly = true)`를 붙이는 이유
- 오늘의 한 줄 질문: 조회만 하는 Service 메서드에도 트랜잭션을 명시해야 할까?
- 왜 지금 볼 만한가: JPA 기반 Spring Boot 애플리케이션에서 조회 로직은 자주 작성되므로, `readOnly = true`를 성능 옵션으로 외우기보다 조회 의도와 flush 흐름을 함께 이해할 가치가 있습니다.
- 실제 개발 문제: 조회 API에서 Entity를 수정하지 않는다고 생각했지만 같은 영속성 컨텍스트 안에서 값이 바뀌면 변경 감지와 flush 동작을 오해할 수 있습니다.
- 핵심 개념: `readOnly = true`는 조회 전용 트랜잭션 의도를 드러내고 JPA provider나 DB 드라이버에 최적화 힌트로 전달될 수 있으며, 오늘은 성능 마법 버튼이 아니라 변경 감지 흐름을 확인하는 출발점으로 봅니다.
- 공식 문서 확인 포인트: Spring transaction read-only attribute, JPA flush, Hibernate dirty checking
- 30분 학습: Spring Framework transaction 문서에서 read-only 속성 설명을 확인하고, JPA flush와 dirty checking 흐름을 3문장으로 정리합니다.
- 30분 실습: 간단한 조회 Service에 `@Transactional`과 `@Transactional(readOnly = true)`를 각각 적용하고 SQL 로그로 flush/update 여부를 비교합니다.
- 기술 블로그 제목 후보:
  1. 조회 API에도 `@Transactional(readOnly = true)`를 붙이는 이유
  2. readOnly 트랜잭션은 성능 옵션일까, 의도 표현일까?
  3. Spring Boot 조회 로직에서 readOnly 트랜잭션 확인하기
- PAAR 글 목차:
  - Problem: 조회 API인데도 트랜잭션을 붙여야 하는지 헷갈리는 상황을 제시합니다.
  - Analyze: Spring transaction의 readOnly 의미와 JPA flush/dirty checking 흐름을 비교합니다.
  - Action: 간단한 Service 예제로 기본 트랜잭션과 readOnly 트랜잭션을 비교합니다.
  - Result: readOnly는 만능 성능 옵션이 아니라 조회 의도 표현과 최적화 힌트로 이해해야 한다는 결론을 정리합니다.
- 완료 기준: readOnly 트랜잭션이 해결하려는 문제를 한 문장으로 설명하고, SQL 로그 또는 테스트 결과를 블로그 초안에 기록합니다.
- 다음에 이어서 볼 주제: 트랜잭션 전파 옵션 중 `REQUIRED`와 `REQUIRES_NEW`의 차이를 작은 예제로 확인합니다.
- 레퍼런스:
  - [Spring Framework 공식 문서](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
  - [Hibernate 공식 문서](https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#pc-dirtychecking)

## 2. 이번 주 PS 성장 루틴
- 이번 주 주제: 해시
- 이번 주 목표: 중복 제거, 빈도 계산, key-value 조회 패턴 익히기
- 현재 진행: 0/5
- 오늘 문제: 폰켓몬
- 플랫폼: Programmers
- 난이도: Level 1
- 먼저 생각할 것: 중복 제거 후 선택 가능한 수와 n/2 중 작은 값을 고릅니다.
- 풀이 후 점검: Set을 쓴 이유를 중복 제거 기준과 시간복잡도 관점에서 2줄로 적습니다.
- 막히면 검색: 프로그래머스 폰켓몬 Kotlin Set
- 링크: [문제 보기](https://school.programmers.co.kr/learn/courses/30/lessons/1845)

## 3. 오픈소스 기여 후보
### 오늘의 OSS 기여 준비 루틴
- 오늘은 바로 추천할 안전한 issue는 없습니다.
- 저장소: spring-projects/spring-boot
- 30분 액션: CONTRIBUTING 문서에서 빌드와 테스트 명령을 확인하고, 로컬에서 어떤 모듈 테스트부터 돌릴지 메모합니다.
- 확인할 문서: CONTRIBUTING.adoc, Build from Source, DCO Signed-off-by 안내
- 다음에 issue를 찾을 때 쓸 GitHub 검색식: `repo:spring-projects/spring-boot is:issue is:open label:"status: ideal-for-contribution" no:assignee`
- 기여 전 매너: 작업 의사를 남기기 전에 최근 댓글과 연결 PR 여부를 먼저 확인합니다.

## 4. 오늘의 백엔드 실무 충전
### 주제: timeout 후 재시도되는 POST API에서 Idempotency-Key 검증하기
- 실무 상황: 클라이언트가 타임아웃 후 같은 결제 생성 요청을 다시 보내면 서버는 첫 요청 성공 여부를 모른 채 두 번째 주문을 만들 수 있습니다.
- 왜 지금 알아야 하는가: 모바일 네트워크와 외부 결제 연동에서는 재시도가 자연스럽게 발생하므로, 쓰기 API는 중복 요청을 전제로 설계해야 합니다.
- 핵심 개념: POST 생성 요청은 별도 idempotency key나 중복 방지 키가 없으면 반복 호출 결과가 달라질 수 있습니다.
- CS Core 연결: 네트워크 timeout은 응답 도착 여부를 보장하지 않으므로, retry가 queueing되거나 중복 실행될 때의 상태 전이를 함께 봐야 합니다.
- 오늘의 백엔드 용어: Idempotency-Key는 같은 쓰기 요청을 식별해 timeout 후 재시도된 POST가 같은 비즈니스 결과를 반환하도록 돕는 키입니다.
- Kotlin/Spring Boot/DB 연결: Spring MVC controller에서 `Idempotency-Key` 헤더를 받고 DB unique index로 중복 생성을 막은 뒤 기존 결과를 반환하는 흐름으로 확인합니다.
- 실패하면 생기는 문제: 결제, 포인트 적립, 재고 차감 같은 변경 작업에서 중복 데이터와 환불/정산 장애가 생깁니다.
- 30분 실습: `/orders` POST를 두 번 호출했을 때 row가 2개 생기는 샘플을 기록한 뒤, `Idempotency-Key` 헤더와 unique index 적용 전후 결과를 비교합니다.
- 증거로 남길 것: 같은 request body를 두 번 보낸 로그, 생성된 row 수, unique index 적용 후 응답 status와 반환 order id를 기록합니다.
- 현업 체크 질문: 이 API는 네트워크 타임아웃 후 자동 재시도되어도 같은 비즈니스 결과를 보장하는가?
- 레퍼런스:
  - [RFC 9110 HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)
  - [MDN Idempotent](https://developer.mozilla.org/en-US/docs/Glossary/Idempotent)
- 검색 키워드: HTTP idempotency POST retry, Idempotency-Key 결제 API 중복 방지
