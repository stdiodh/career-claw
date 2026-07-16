# Security Policy

보안 문제는 공개 Issue 대신 GitHub의 비공개 Security Advisory로 제보해 주세요.

Career Feed의 운영 Secret 값은 선택적 Discord Webhook 하나뿐입니다. 표준 repository secret 이름은 `DISCORD_WEBHOOK_URL`이며, 기존 저장소의 `DISCORD_WEBHOOK_KR_TECH_DAILY`는 같은 값의 migration fallback으로만 지원합니다. 둘 다 설정하지 않습니다.

OSS 수집기는 인증 헤더 없이 공개 issue를 GET으로만 조회합니다. `GITHUB_TOKEN`, 개인 PAT, GitHub App private key와 installation token은 지원하지 않습니다. issue body와 댓글 전문, credential, token은 artifact에 저장하지 않습니다.

실제 Webhook URL과 개인 식별 정보가 Issue, 로그, 브리핑, config에 포함되지 않도록 확인해 주세요.

Webhook이 노출되었다면 즉시 Discord에서 기존 Webhook을 폐기하고 새 URL로 교체하세요. 저장소 이력에서 문자열만 지우는 것으로는 폐기되지 않습니다.
