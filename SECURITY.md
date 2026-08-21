# Security Policy

보안 문제는 공개 issue 대신 GitHub의 비공개 Security Advisory로 제보해 주세요.

Career Feed는 Secret이나 credential을 요구하지 않습니다. 수집기는 공개 GitHub REST API에 인증 헤더 없이 GET 요청만 보내며 외부 저장소를 수정하지 않습니다.

다음 정보는 JSON과 Markdown artifact에 저장하지 않습니다.

- issue body와 댓글 전문
- GitHub token, PAT 또는 App key
- 개인 credential과 환경 변수 값

artifact에는 검증에 필요한 issue 식별자, URL, 시각, 계산된 근거와 제외 이유만 남깁니다. 생성되는 `reports/`는 Git에서 무시되며 공유하기 전에 개인 식별 정보가 없는지 확인해야 합니다.

수집기가 예상하지 않은 저장소 URL, 불완전 API 응답, pagination 또는 rate-limit 증거를 만나면 추천을 차단합니다.
