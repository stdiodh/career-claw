# Security Policy

## 지원 범위

Career Feed는 GitHub Actions, OpenAI API, Discord Webhook 기반의 자동 브리핑 workflow를 운영합니다. 현재
상시 실행 서버, 데이터베이스, 웹 대시보드, Discord Gateway Bot은 운영 범위에 포함하지 않습니다.

## 민감 정보

다음 값은 코드, 문서 예시, 커밋 로그, 이슈, PR에 포함하면 안 됩니다.

- OpenAI API key
- Discord Webhook URL
- GitHub token
- Naver API credentials
- 기타 서비스 credentials

## 취약점 또는 민감 정보 노출 제보

민감 정보가 노출되었거나 보안 문제가 의심된다면 공개 이슈에 secret 값을 직접 올리지 말고, maintainer에게 먼저 연락해 주세요.

## 자동화 정책

Career Feed는 외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 하지 않습니다. OSS 후보는 추천과 검증 보조
목적으로만 사용합니다.
