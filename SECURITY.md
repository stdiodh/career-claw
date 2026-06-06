# Security Policy

## 지원 범위

Career Feed는 GitHub Actions, OpenAI API, Discord Webhook 기반의 자동 브리핑 workflow를 운영합니다.

현재 운영 범위에 포함하지 않는 것은 다음과 같습니다.

- 상시 실행 서버
- 데이터베이스
- 웹 대시보드
- Discord Gateway Bot
- Slash Command
- 외부 저장소 자동 댓글 또는 자동 PR

## 민감 정보

다음 값은 코드, 문서 예시, 커밋 로그, 이슈, PR에 포함하면 안 됩니다.

- OpenAI API key
- Discord Webhook URL
- GitHub token
- Naver API credentials
- 기타 서비스 credentials
- 개인 이메일, 전화번호, 주소 등 민감한 개인정보

## 취약점 또는 민감 정보 노출 제보

민감 정보가 노출되었거나 보안 문제가 의심된다면 공개 이슈에 secret 값을 직접 올리지 마세요.

우선 maintainer에게 연락하거나, secret 값을 제거한 상태로 문제 상황만 설명해 주세요.

노출된 secret은 즉시 폐기하고 새 값으로 교체해야 합니다.

## 자동화 정책

Career Feed는 외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 하지 않습니다.

OSS 후보는 추천과 검증 보조 목적으로만 사용합니다.

## API 사용 안전 원칙

- OpenAI API 출력은 검토 없이 공식 답변처럼 사용하지 않습니다.
- 채용 결과, 개인 역량, 합격 가능성에 대해 단정하지 않습니다.
- 민감 정보나 개인정보를 prompt에 넣지 않습니다.
- Discord 전송 전 validator와 maintainer 검토 흐름을 우선합니다.
