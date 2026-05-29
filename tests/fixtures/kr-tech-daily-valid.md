# Career Feed - Backend Daily
기준시각: 2026-05-28 09:10:00 KST

오늘의 방향:
- API 버전 호환성과 HTTP 재시도 의미를 작게 검증하며 해시 루틴을 이어갑니다.

## 1. 오늘의 Spring Boot/JVM 학습
### 주제: Spring Framework 7 API Versioning으로 v1/v2 컨트롤러 분리하기
- 왜 지금 볼 만한가: Spring Framework 7의 API versioning은 REST API 진화와 하위 호환성 유지 연습에 바로 연결됩니다.
- 핵심 개념: 요청 버전 위치를 정하고 컨트롤러 매핑에서 지원 버전을 선언해 미지원 버전 요청을 분리합니다.
- 30분 실습: `API-Version` 헤더 기반 v1/v2 컨트롤러를 만들고, MockMvc로 v1, v2, v3 요청 상태 코드를 비교합니다.
- 완료 기준: v1과 v2 응답이 분리되고 지원하지 않는 v3 요청이 실패하는 테스트가 남습니다.
- 확장해서 볼 것: path segment 방식, deprecated version 응답 헤더, RestClient 기본 버전 설정
- 레퍼런스:
  - [공식 문서](https://docs.spring.io/spring-framework/reference/7.0/web/webmvc/mvc-config/api-version.html)
  - [릴리즈 노트](https://spring.io/blog/2025/11/13/spring-framework-7-0-general-availability)

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
