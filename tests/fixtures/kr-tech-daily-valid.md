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

## 4. 주니어 백엔드 실무지식
### 주제: 결제 생성 API에서 POST 재시도가 중복 주문을 만드는 상황
- 실무 상황: 클라이언트가 타임아웃 후 같은 결제 생성 요청을 다시 보내면 서버는 첫 요청 성공 여부를 모른 채 두 번째 주문을 만들 수 있습니다.
- 핵심 개념: POST 생성 요청은 별도 idempotency key나 중복 방지 키가 없으면 반복 호출 결과가 달라질 수 있습니다.
- 실패하면 생기는 문제: 결제, 포인트 적립, 재고 차감 같은 변경 작업에서 중복 데이터와 환불/정산 장애가 생깁니다.
- 30분 실습: `/orders` POST를 두 번 호출했을 때 row가 2개 생기는 샘플을 만든 뒤, `Idempotency-Key` 헤더와 unique key로 같은 요청은 같은 결과를 돌려주도록 바꿔봅니다.
- 현업 체크 질문: 이 API는 네트워크 타임아웃 후 자동 재시도되어도 같은 비즈니스 결과를 보장하는가?
- 레퍼런스:
  - [RFC 9110 HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)
  - [MDN Idempotent](https://developer.mozilla.org/en-US/docs/Glossary/Idempotent)
- 검색 키워드: HTTP idempotency POST retry, Idempotency-Key 결제 API 중복 방지

## 5. 오늘의 CS Core & 백엔드 용어
### CS Core: TCP 연결 생성과 timeout을 외부 API 호출 장애로 연결하기
- 트랙: network
- 왜 백엔드에 중요한가: 외부 API 장애는 연결 실패, 응답 지연, TLS 문제 중 어디에서 막혔는지에 따라 대응이 달라집니다.
- 핵심 개념: TCP 연결은 handshake로 세션을 만든 뒤 데이터를 주고받으며, connect timeout과 read timeout은 실패 위치가 다릅니다.
- 10~20분 확인: HTTP client 설정에서 connect timeout과 read timeout 값을 찾아보고, 장애 로그에 timeout 종류가 남는지 확인합니다.
- 완료 기준: connect timeout과 read timeout을 구분한 메모 2줄과 현재 프로젝트 설정 위치를 남깁니다.
- 면접 연결 질문: connect timeout과 read timeout은 장애 원인 추적에서 어떻게 다르게 해석해야 하는가?
- 레퍼런스:
  - [RFC 9293 TCP](https://datatracker.ietf.org/doc/html/rfc9293)
  - [Spring REST Clients](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html)

### 백엔드 용어: Connection Pool
- 한 줄 정의: DB나 외부 서버 연결을 매번 새로 만들지 않고 재사용하는 연결 묶음입니다.
- 실무 상황: pool이 너무 작으면 요청이 대기하고, 너무 크면 DB나 외부 API 서버를 압박합니다.
- 오해하면 생기는 문제: pool 크기를 키우면 항상 성능이 좋아진다고 보면 병목을 DB로 옮기고 장애 범위를 키울 수 있습니다.
- Spring/API 연결: Spring Boot DataSource는 HikariCP 설정으로 maximumPoolSize와 connectionTimeout을 조정합니다.
- 확인 질문: 현재 DB connection pool 대기 시간과 활성 connection 수를 보고 있는가?
- 레퍼런스:
  - [Spring Boot SQL Databases](https://docs.spring.io/spring-boot/reference/data/sql.html)
  - [HikariCP](https://github.com/brettwooldridge/HikariCP)
