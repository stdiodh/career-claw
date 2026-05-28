# AGENTS.md

이 문서는 Codex가 `Career Feed` 프로젝트에서 작업할 때 따를 규칙을 정의한다.

## 프로젝트 방향

- 이 프로젝트는 GitHub Actions, Codex, Discord Webhook 기반의 개발자 커리어 뉴스 브리핑 자동화 프로젝트다.
- 상시 실행 서버, Discord Gateway Bot, Slash Command, 데이터베이스, 웹 대시보드는 초기 범위에 포함하지 않는다.
- 기본 목표는 매일 Backend Daily Study Brief와 주간 백엔드 커리어 브리핑을 생성한 뒤 Discord Webhook으로 전송하는 것이다.
- Daily 브리핑은 Spring Boot/JVM 학습, Programmers 주차별 PS 루틴, Spring OSS 기여 후보, 한국 개발/AI 뉴스로 구성한다.
- Programmers PS 루틴은 정적 config와 progress 파일만 사용하며 사이트 크롤링이나 제출 결과 자동 수집을 하지 않는다.
- OpenJDK/JBS는 Spring OSS 난이도 모델의 참고로만 사용하고 직접 수집하지 않는다.
- 제품명과 문서명은 `Career Feed`로 통일한다. 저장소 이름이나 로컬 경로명은 환경에 따라 다를 수 있다.
- 현재 기본 운영 경로는 `KR_PREMIUM_MODE` v2 Daily/Weekly workflow다. `FREE_MODE`는 수동 백업으로 유지한다.

## 작업 원칙

- 작은 변경으로 요청한 범위만 해결한다.
- 아직 구현되지 않은 기능은 문서에서 Roadmap 또는 TODO로만 표현한다.
- Secrets, API Key, Webhook URL, 토큰을 코드나 문서 예시에 하드코딩하지 않는다.
- `OPENAI_API_KEY`, `DISCORD_WEBHOOK_URL` 같은 값은 GitHub Secrets 또는 환경변수로만 다룬다.
- GitHub Actions workflow는 사용자가 명시적으로 요청하기 전까지 생성하지 않는다.
- 현재 단계에서 `app/`와 `infra/`는 수정하지 않는다.
- 사용자가 명시적으로 요청하지 않는 한 서버, 배포 workflow, 인프라 설정을 변경하지 않는다.

## 문서와 코드 스타일

- README와 `docs/` 문서는 한국어 중심으로 작성한다.
- 코드 내부 주석은 영어로 작성한다.
- 사용자에게 전달되는 브리핑 문구는 한국어를 기본으로 한다.
- 불필요한 추상화나 대규모 리팩터링을 피한다.

## 검증

- 파일을 추가하거나 수정한 뒤에는 존재 여부와 핵심 키워드를 확인한다.
- 스크립트를 수정한 경우 가능한 범위에서 문법 검사를 수행한다.
- 실행에 필요한 환경변수가 없을 때는 실패 메시지가 명확한지 확인한다.
