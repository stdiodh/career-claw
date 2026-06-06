# Codex Open Source Support Program Application Notes

이 문서는 Codex Open Source Support Program 신청을 위해 Career Feed의 목적, maintainer 역할, 생태계 중요성, API credits 사용 계획을 정리합니다.

개인 이메일, OpenAI organization ID, API key, token, webhook URL 같은 비공개 정보는 이 문서에 포함하지 않습니다.

## Project summary

Career Feed는 백엔드 지망생과 주니어 개발자가 “무엇부터 시작해야 하는지” 몰라 겪는 막막함을 줄이기 위한 초기 단계의 공개 OSS입니다.

GitHub Actions, OpenAI API, Discord Webhook으로 백엔드 학습 주제, PS 루틴, OSS 기여 후보, 한국 개발·AI 뉴스, 커리어 사이트 레이더를 자동 생성·검증·전송합니다.

## Maintainer role

`@stdiodh` is the primary maintainer responsible for:

- GitHub Actions workflow maintenance
- OpenAI API based briefing generation and validation
- backend learning topic and career source curation
- Discord Webhook delivery operations
- documentation and roadmap management
- issue template based suggestion review

## Ecosystem importance

Career Feed는 백엔드 프레임워크나 런타임처럼 production dependency가 되는 프로젝트는 아닙니다.

대신 백엔드 생태계에 진입하려는 지망생과 주니어 개발자의 onboarding friction을 줄이는 공개 성장 인프라를 목표로 합니다.

이 프로젝트는 학습 주제, 커리어 정보, OSS 후보, 실무 지식, 한국 개발·AI 뉴스를 반복 가능한 브리핑으로 정리해 개인 학습자, Discord 스터디, 멘토링 그룹이 재사용할 수 있게 합니다.

따라서 생태계에서의 중요성은 “핵심 패키지 의존성”이 아니라 “새로운 백엔드 개발자가 더 꾸준하고 안전하게 학습·기여 루틴을 만들도록 돕는 공개 운영 workflow”에 있습니다.

## Fit for the program

### Korean draft

career-feed는 백엔드 지망생들이 “무엇부터 시작해야 하는지” 몰라 겪는 막막함을 줄이기 위한 초기 단계의 공개 OSS입니다. GitHub Actions, OpenAI API, Discord Webhook으로 백엔드 학습 주제, PS 루틴, OSS 기여 후보, 한국 개발·AI 뉴스, 커리어 사이트 레이더를 자동 생성·검증·전송합니다. 아직 사용 지표는 작지만, 운영 문서, 검증 스크립트, 기여 템플릿을 기반으로 성실하게 유지관리 중입니다.

### Shorter Korean draft

career-feed는 백엔드 지망생의 정보 과부하와 시작점 부재를 줄이기 위한 초기 단계의 공개 OSS입니다. GitHub Actions, OpenAI API, Discord Webhook으로 학습 주제, 커리어 정보, OSS 기여 후보, 개발·AI 뉴스를 생성·검증·전송합니다. 아직 사용 지표는 작지만 운영 문서, 검증 스크립트, issue template을 기반으로 성실하게 유지관리 중입니다.

## API credits usage plan

### Korean draft

API 크레딧은 백엔드 지망생을 위한 daily/weekly 브리핑 생성, 학습 주제 우선순위화, 채용·인턴·대외활동 정보 요약, OSS 기여 후보 선별, 이슈로 접수된 고민 분류와 답변 초안 생성에 사용하겠습니다. 자동 댓글이나 무검토 PR 생성은 하지 않고, maintainer가 검토 가능한 브리핑·검증 리포트 생성에 제한해 사용하겠습니다.

### Shorter Korean draft

API 크레딧은 daily/weekly 브리핑 생성, 학습 주제 우선순위화, 커리어 정보 요약, OSS 후보 선별, issue 고민 분류와 답변 초안 생성에 사용하겠습니다. 자동 댓글, 자동 PR, 무검토 배포에는 사용하지 않고 maintainer가 검토 가능한 브리핑과 검증 리포트 생성에 제한하겠습니다.

## Additional note

저는 백엔드 지망생들이 정보 부족보다 “어디서 시작해야 할지 모르는 막막함” 때문에 어려움을 겪는다고 느꼈습니다. career-feed를 통해 그 고충을 공개적으로 기록하고, 학습·채용·OSS 기여 정보를 꾸준히 정리해 누구나 재사용할 수 있는 성장 피드로 발전시키고 싶습니다. 아직 작은 프로젝트지만 성실하게 유지관리하며 실제 도움이 되는 OSS로 키우겠습니다.

## Role description

저는 career-feed의 primary maintainer입니다. GitHub Actions, OpenAI API, Discord Webhook 기반으로 백엔드 지망생과 주니어 개발자를 위한 daily/weekly 브리핑 workflow를 설계하고 유지관리합니다. 백엔드 학습 주제, 커리어 정보 출처, OSS 기여 후보, 검증 스크립트, 문서와 로드맵 관리를 담당합니다.

## What not to claim

다음 표현은 사용하지 않습니다.

- 널리 사용되는 백엔드 핵심 라이브러리입니다.
- 많은 회사와 조직이 사용 중입니다.
- 다운로드 수가 많습니다.
- 이미 큰 커뮤니티를 보유하고 있습니다.
- 외부 OSS 기여를 자동으로 수행합니다.

## Honest positioning

사용할 수 있는 표현은 다음과 같습니다.

- 초기 단계의 공개 OSS입니다.
- 백엔드 지망생의 막막함을 줄이기 위한 성장 피드입니다.
- 사용 지표는 아직 작지만 성실하게 유지관리 중입니다.
- GitHub Actions, OpenAI API, Discord Webhook 기반의 maintainer automation workflow입니다.
- 백엔드 생태계의 핵심 패키지는 아니지만, 입문자와 주니어 개발자의 생태계 진입을 돕는 공개 운영 기반을 목표로 합니다.
