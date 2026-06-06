# Contributing to Career Feed

Career Feed는 백엔드 지망생과 주니어 개발자가 막막함을 줄이고 꾸준한 성장 루틴을 만들 수 있도록 돕는 공개 프로젝트입니다.

기여는 큰 기능 개발만을 의미하지 않습니다. 좋은 출처 제안, 백엔드 학습 주제 제안, OSS 후보 제안, 문서 개선, 깨진 링크 제보도 모두 중요한 기여입니다.

## 어떤 기여를 받을 수 있나요?

- 백엔드 학습 주제 제안
- Spring/JVM 로드맵 개선
- 채용, 인턴, 대외활동, 커리어 정보 출처 제안
- OSS 기여 후보 저장소 제안
- good first issue 또는 beginner-friendly issue 후보 제안
- 깨진 링크, 수집 실패, 중복 정보 제보
- 백엔드 지망생의 고민과 질문 공유
- README, docs, issue template 개선

## 기여 방식

### 1. 백엔드 커리어 질문 남기기

`.github/ISSUE_TEMPLATE/backend-career-question.yml` 템플릿을 사용해 현재 상황, 막막한 점, 원하는 도움을 남겨 주세요.

### 2. 정보 출처 제안하기

`.github/ISSUE_TEMPLATE/source-suggestion.yml` 템플릿을 사용해 백엔드 학습, 채용, 인턴, 대외활동, 기술 블로그, 뉴스 출처를 제안할 수 있습니다.

### 3. OSS 후보 제안하기

`.github/ISSUE_TEMPLATE/oss-candidate-suggestion.yml` 템플릿을 사용해 백엔드 지망생이 살펴볼 만한 오픈소스 저장소나 issue를 제안할 수 있습니다.

### 4. 문서나 설정 개선하기

작은 오타 수정, README 개선, 운영 문서 보완, validator 설명 개선도 환영합니다.

## 좋은 제안의 기준

- 백엔드 지망생 또는 주니어 개발자에게 실제로 도움이 되는가?
- 출처가 공개적이고 확인 가능한가?
- 특정 회사, 강의, 서비스 홍보만을 목적으로 하지 않는가?
- 초보자가 따라갈 수 있는 설명이 있는가?
- 반복 가능한 브리핑 workflow에 넣을 수 있는가?
- 오래 유지할 수 있는 정보인가?

## Pull Request 원칙

- 한 PR에는 하나의 주제만 담아 주세요.
- secrets, API key, token, webhook URL을 커밋하지 마세요.
- 가능하면 로컬 검증 명령을 실행하고 결과를 적어 주세요.
- 기존 운영 scope를 벗어나는 큰 기능은 먼저 issue로 논의해 주세요.
- 런타임 동작 변경과 문서 변경은 가능하면 분리해 주세요.
- 자동 전송이 발생할 수 있는 workflow는 dry-run 여부를 먼저 확인해 주세요.

## Maintainer policy

- 자동 생성된 브리핑이나 답변은 maintainer 검토 없이 공식 답변처럼 사용하지 않습니다.
- OSS 후보는 추천만 하며, 외부 저장소에 자동 댓글, PR, assign, label 변경을 하지 않습니다.
- 기여자의 고민과 질문은 비난 없이 다룹니다.
- 부정확하거나 오래된 정보는 수정하거나 제거할 수 있습니다.
- 광고성 제안, 무관한 홍보, 민감 정보 노출은 닫거나 수정 요청할 수 있습니다.

## 보안과 개인정보

다음 값은 절대 이슈, PR, 커밋, 문서 예시에 포함하지 마세요.

- OpenAI API key
- Discord Webhook URL
- GitHub token
- Naver API credentials
- 개인 이메일, 전화번호, 주소 등 민감한 개인정보

실수로 secret을 노출했다면 즉시 해당 secret을 폐기하고 새 값으로 교체해 주세요.
