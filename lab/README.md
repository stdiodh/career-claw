# Backend Lab

Career Feed 과제의 Kotlin/Java/Spring 주장을 실제 코드와 테스트로 검증하는 최소 실습 모듈이다. 운영 서비스가 아니며 H2는 로컬 기본 검증에만 사용한다.

## 고정 프로필

- JDK toolchain: 21
- Spring Boot: 4.1.0
- Kotlin/KGP: 2.4.10
- Gradle Wrapper: 9.5.0
- 선택적 PostgreSQL: `postgres@sha256:4f736ae292687621d4dbe0d499ffd024a36bd2ee7d8ca6f2ccd4c800f047b394`

모든 Gradle configuration은 `gradle.lockfile`로 고정한다. profile의 Spring Framework, Spring Security, Spring Data JPA, Flyway, Hibernate ORM, Jackson Kotlin 버전과 lock이 다르면 Daily 생성도 실패한다.

## 실행

```bash
./lab/gradlew -p lab test --no-daemon
LAB_EXTERNAL_API_TOKEN=local-only ./lab/gradlew -p lab bootRun
```

`LAB_EXTERNAL_API_TOKEN`은 설정 누락을 시작 시점에 차단하는 연습용 필수 환경변수다. 실제 토큰을 저장소에 기록하지 않는다. 애플리케이션 실행 시 Spring Security가 생성한 임시 비밀번호는 시작 로그에서 확인한다.

Docker가 실행 중일 때만 PostgreSQL 인덱스 검증을 별도로 수행한다.

```bash
./lab/gradlew -p lab postgresTest --no-daemon
```

기본 테스트는 다음 경계를 구분한다.

- 순수 unit: 성능 지표, retry budget, 결제 복구
- MVC slice: DTO validation과 `ProblemDetail`
- JPA slice: migration, lazy loading, projection, pagination
- full integration: 인증·인가, idempotency, request ID, metric, 동시 재고 차감
- 선택 integration: PostgreSQL 17.10의 실제 index plan

각 테스트의 `@DisplayName`에 있는 `LAB-*` 값이 검증 manifest에서 사용하는 안정적인 test ID다.
