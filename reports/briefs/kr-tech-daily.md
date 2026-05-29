# Career Feed - Backend Daily

기준시각: 2026-05-28 17:50:53 KST

오늘의 방향:
- API 버전 호환성과 HTTP 재시도 의미를 작게 검증하고, 해시 문제와 문서형 OSS 이슈로 부담 없이 이어갑니다.

## 1. 오늘의 Spring Boot/JVM 학습

### 주제: Spring Framework 7 API Versioning으로 v1/v2 컨트롤러 분리하기
- 왜 지금 볼 만한가: Spring Framework 7은 API versioning을 공식 지원하고 Spring Boot 4 세대와 함께 쓰이므로, URL/헤더 버전 전략을 직접 비교해볼 가치가 있습니다.
- 핵심 개념: `ApiVersionConfigurer`로 요청 버전 위치를 정하고, 컨트롤러 매핑에서 지원 버전을 선언해 미지원 버전 요청이 400으로 처리되는지 확인합니다.
- 30분 실습: Kotlin Spring Boot 샘플에 `API-Version` 헤더 기반 v1/v2 컨트롤러를 만들고, `curl` 또는 MockMvc로 버전 없음, v1, v2, v3 요청 결과를 비교합니다.
- 완료 기준: v1과 v2 응답이 분리되고, 지원하지 않는 v3 요청이 실패하며, 테스트 또는 명령 기록에 상태 코드 차이가 남습니다.
- 확장해서 볼 것: path segment 방식, deprecated version 응답 헤더, `RestClient` 기본 버전 설정
- 참고 링크: [공식 문서 보기](https://docs.spring.io/spring-framework/reference/7.0/web/webmvc/mvc-config/api-version.html)
- 레퍼런스: [Spring Framework 7 GA](https://spring.io/blog/2025/11/13/spring-framework-7-0-general-availability)

## 2. 이번 주 PS 성장 루틴

- 이번 주 주제: 해시
- 이번 주 목표: Key-value 기반 조회와 중복/빈도 처리를 익힙니다.
- 현재 진행: 0/5
- 오늘 문제: 폰켓몬
- 플랫폼: Programmers
- 난이도: Level 1
- 먼저 생각할 것: 중복 제거 후 선택 가능한 종류 수와 `n / 2` 중 작은 값을 고릅니다.
- 풀이 후 점검: `Set`을 쓴 이유를 중복 제거 기준과 시간복잡도 관점에서 2줄로 적습니다.
- 막히면 검색: 프로그래머스 폰켓몬 Kotlin Set, Kotlin distinct size
- 링크: [문제 보기](https://school.programmers.co.kr/learn/courses/30/lessons/1845)

## 3. 오픈소스 기여 후보

### 후보: Remove duplicated Spring Boot configuration properties documentation
- 상태 확인: maintainer/member가 연 이슈이고, 담당자 없음, 연결 PR/branch 없음, claim 댓글 없음이 확인되었습니다.
- 난이도 밴드: P5-like
- 저장소: micrometer-metrics/micrometer
- 기여 유형: docs
- 왜 시도해볼 만한가: Spring Boot 설정 문서를 중복 복사하지 않고 Micrometer 쪽 문서에서 JavaDoc 또는 공식 위치로 연결하는 문서 정리 이슈라 첫 범위를 작게 잡을 수 있습니다.
- 첫 30분 액션: `CONTRIBUTING.md`와 docs 빌드 경로를 확인한 뒤, registry 문서에서 Spring Boot configuration properties를 직접 나열한 위치 1개만 찾습니다.
- 기여 전 매너: 구현 전에 이슈에 “중복 설정 표기 위치를 먼저 확인하고 작은 문서 정리 범위로 접근해도 될까요?”라고 범위를 확인합니다.
- 확인할 파일/키워드: docs, registry, Spring Boot configuration properties, JavaDoc, Config
- 주의할 점: 설정 동작이나 API를 바꾸지 말고 문서 링크/중복 제거 가능성 확인까지만 첫 액션으로 제한합니다.
- 링크: [Issue 보기](https://github.com/micrometer-metrics/micrometer/issues/4982)

## 4. 한국 최신 개발/AI 뉴스

- 오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다.

## 5. 주니어 백엔드 실무지식

### 주제: 결제 생성 API에서 POST 재시도가 중복 주문을 만드는 상황
- 실무 상황: 클라이언트가 타임아웃 후 같은 결제 생성 요청을 다시 보내면 서버는 첫 요청 성공 여부를 모른 채 두 번째 주문을 만들 수 있습니다.
- 큰 흐름: HTTP method의 idempotency 의미를 API 설계와 재시도 정책에 연결해 봅니다.
- 핵심 개념: `PUT`은 같은 리소스 교체라 재시도 의미를 맞추기 쉽지만, `POST` 생성 요청은 별도 idempotency key나 중복 방지 키가 없으면 반복 호출 결과가 달라질 수 있습니다.
- 실패하면 생기는 문제: 결제, 포인트 적립, 재고 차감 같은 변경 작업에서 중복 데이터와 환불/정산 장애가 생깁니다.
- 30분 실습: `/orders` POST를 두 번 호출했을 때 row가 2개 생기는 샘플을 만든 뒤, `Idempotency-Key` 헤더와 unique key로 같은 요청은 같은 결과를 돌려주도록 바꿔봅니다.
- 현업 체크 질문: 이 API는 네트워크 타임아웃 후 자동 재시도되어도 같은 비즈니스 결과를 보장하는가?
- 레퍼런스: [RFC 9110 HTTP Semantics](https://datatracker.ietf.org/doc/html/rfc9110)
- 실무 참고: [MDN Idempotent](https://developer.mozilla.org/en-US/docs/Glossary/Idempotent)
- 검색 키워드: HTTP idempotency POST retry, Idempotency-Key 결제 API 중복 방지
