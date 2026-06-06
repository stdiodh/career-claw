# Open Source Readiness Review

## 판단

Career Feed는 현재 대규모 오픈소스 프로젝트나 널리 사용되는 백엔드 라이브러리로 보기는 어렵습니다.

그러나 오픈소스 프로젝트로서의 방향성은 적합합니다. 이유는 공개 문제의식, 재사용 가능한 workflow, issue 기반 기여 경로, maintainer automation, 보안·운영 정책 문서화가 존재하기 때문입니다.

Codex Open Source Support Program에 신청할 때는 “널리 쓰이는 핵심 패키지”가 아니라 “초기 단계의 공개 maintainer automation 프로젝트”로 설명하는 것이 정직합니다.

## 강점

- 백엔드 지망생과 주니어 개발자의 실제 고충을 다룹니다.
- GitHub Actions, OpenAI API, Discord Webhook 기반으로 운영 방식이 명확합니다.
- 상시 서버, DB, 웹 대시보드 없이 작은 scope로 운영됩니다.
- issue template을 통해 커리어 질문, 정보 출처, OSS 후보 제안을 받을 수 있습니다.
- API 사용 정책과 자동화 제한을 명확히 둘 수 있습니다.
- maintainer가 직접 검토하는 흐름을 전제로 합니다.
- 교육, 멘토링, 스터디에서 재사용 가능한 구조를 목표로 합니다.

## 약점

- stars, forks, downloads, active users 같은 공개 사용 지표가 아직 작습니다.
- 백엔드 런타임이나 프레임워크처럼 production dependency가 아닙니다.
- 실제 커뮤니티 사용 사례와 외부 기여가 아직 부족합니다.
- 자동 생성 브리핑의 품질을 꾸준히 검증해야 합니다.
- 채용·인턴·대외활동 정보는 최신성 검증이 중요합니다.

## 보완 계획

- README와 docs를 실제 줄바꿈이 있는 Markdown으로 유지합니다.
- issue templates가 GitHub issue forms로 정상 동작하도록 YAML을 검증합니다.
- `docs/ecosystem-importance.md`에 프로젝트의 의미와 한계를 정직하게 설명합니다.
- `docs/oss-program-application.md`에 신청서 복사용 문구를 정리합니다.
- sample briefings를 추가해 사용자가 결과물을 이해할 수 있게 합니다.
- maintainer guide를 정리해 dry-run, validator, secret safety를 명확히 합니다.
- 외부 사용 사례가 생기면 README에 과장 없이 추가합니다.

## 신청 포지셔닝

이 프로젝트는 다음 문장으로 설명하는 것이 가장 적합합니다.

> Career Feed는 백엔드 지망생과 주니어 개발자가 정보 과부하와 시작점 부재로 겪는 막막함을 줄이기 위한 초기 단계의 공개 OSS입니다. GitHub Actions, OpenAI API, Discord Webhook으로 학습·커리어·OSS 후보 브리핑을 생성하고, maintainer가 검토 가능한 운영 workflow로 유지합니다.

## 제출 전 체크리스트

- README가 실제 줄바꿈이 있는가?
- CONTRIBUTING이 기여 경로를 명확히 설명하는가?
- LICENSE가 표준 MIT License 형식인가?
- SECURITY가 secret 노출 금지와 자동화 제한을 설명하는가?
- issue template YAML이 정상 parse되는가?
- fake metrics가 없는가?
- API credits 사용 계획이 maintainer 검토 중심인가?
- 외부 저장소에 자동 행동을 하지 않는다는 점이 명확한가?
