# Career Feed - Backend Daily
기준시각: 2026-05-28 09:10:00 KST

오늘의 방향:
- 설정 흐름을 작게 확인하고, 해시 문제와 성능 지표 감각을 함께 이어갑니다.

## 1. 오늘의 Spring Boot/JVM 학습
### 주제: Spring Boot 설정 값 바인딩 흐름
- 핵심 개념: `application.yml` 값이 설정 클래스에 바인딩되는 흐름을 확인합니다.
- 30분 실습: 작은 설정 클래스를 만들고 테스트에서 값 주입을 확인합니다.
- 완료 기준: 테스트에서 yml 값이 설정 클래스에 바인딩되는 것을 assert합니다.
- 확장해서 볼 것: validation, profile별 설정 분리
- 참고 링크: [원문 보기](https://docs.spring.io/spring-boot/reference/features/external-config.html)

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
### 후보: Support java.util.Pattern for LIKE query method predicates
- 상태 확인: maintainer가 연 이슈이고, 담당자 없음, 연결 PR/branch 없음, 작업 claim 댓글 없음이 확인되었습니다.
- 난이도 밴드: P5-like
- 저장소: spring-projects/spring-data-commons
- 기여 유형: docs
- 왜 시도해볼 만한가: 문서 위치 확인과 예제 검증 중심으로 첫 기여 범위를 작게 잡을 수 있습니다.
- 첫 30분 액션: `src/docs/asciidoc`에서 LIKE/query method 관련 문서 위치를 찾고, `mvn package -Pdistribute` 문서 빌드 경로를 확인합니다.
- 기여 전 매너: 작업 전 이슈에 “문서 위치를 확인해보고 작은 PR을 준비해도 괜찮을까요?”라고 짧게 확인합니다.
- 확인할 파일/키워드: src/docs/asciidoc, LIKE, query method predicates, Pattern, DCO Signed-off-by
- 주의할 점: API 동작 변경으로 넓히지 말고 문서 보강 범위로만 시작하며, PR을 준비하게 되면 issue reference를 확인합니다.
- 링크: [Issue 보기](https://github.com/spring-projects/spring-data-commons/issues/3417)

## 4. 한국 최신 개발/AI 뉴스
- 오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다.

## 5. 주니어 백엔드 실무지식
### 주제: 처리량과 응답 시간
- 큰 흐름: 서비스 성능을 볼 때 요청 수와 요청별 소요 시간을 나눠서 봅니다.
- 핵심 개념: 처리량은 단위 시간당 처리 요청 수이고, 응답 시간은 한 요청이 끝나는 데 걸리는 시간입니다.
- 30분 실습: 간단한 API를 기준으로 평균 응답 시간, p95 응답 시간, 초당 요청 수를 표로 정리합니다.
- 현업 체크 질문: 응답 시간이 느린 것과 처리량이 부족한 것은 어떤 상황에서 다르게 나타나는가?
- 검색 키워드: 처리량 응답 시간 p95, backend throughput latency
