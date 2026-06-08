# Contributing to Career Feed

## Welcome

기여해 주셔서 감사합니다.

Career Feed는 백엔드 지망생과 주니어 개발자가 학습 주제, 커리어 정보, OSS 후보, 기술 뉴스, PS 루틴을 덜 막막하게 탐색하도록 돕는 공개 workflow입니다.

초기 단계의 공개 OSS입니다.

큰 사용 지표나 과장된 adoption을 주장하지 않고, maintainer가 검토할 수 있는 작은 자동화와 문서 개선을 꾸준히 쌓는 것을 우선합니다.

## Project purpose

GitHub Actions, OpenAI API, Discord Webhook 기반으로 브리핑 초안과 검증 가능한 자료를 만듭니다.

주요 목적은 학습자에게 확정적인 정답을 주는 것이 아니라, 오늘 살펴볼 수 있는 학습·커리어 탐색의 시작점을 제공하는 것입니다.

브리핑과 제안은 사람이 검토할 수 있는 자료로 취급합니다.

외부 저장소나 외부 커뮤니티에 자동으로 행동하는 시스템이 아닙니다.

## Ways to contribute

다음과 같은 기여를 환영합니다.

- 백엔드 학습 주제 제안
- Spring, JVM, DB, Redis, AWS, System Design 관련 roadmap 개선
- Programmers PS 루틴 개선 제안
- 채용, 인턴, 대외활동, 부트캠프, 컨퍼런스, 뉴스 출처 제안
- 회사 기술 블로그와 공식 문서 출처 제안
- beginner-friendly OSS 후보 제안
- 깨진 링크 또는 오래된 출처 신고
- 문서 개선
- 검증 스크립트 개선
- 지역 또는 언어 확장 아이디어 제안

제안은 작고 검토 가능할수록 반영하기 쉽습니다.

처음 기여한다면 [Contributor Task Ideas](docs/project/contributor-tasks.md)에서 작은 작업 후보를 먼저 확인해 주세요.

## What makes a good contribution

좋은 기여는 다음 특징을 갖습니다.

- 무엇을 바꾸려는지 분명합니다.
- 왜 백엔드 학습자나 주니어 개발자에게 도움이 되는지 설명합니다.
- 공개적으로 확인 가능한 URL, 근거, 예시를 포함합니다.
- 자동화를 바로 실행하라는 명령이 아니라, maintainer가 검토할 수 있는 자료를 제공합니다.
- secret, credential, private link, 개인 정보를 포함하지 않습니다.
- 한 PR에 하나의 주제만 담습니다.

상세 기준은 [Good suggestion criteria](docs/contributing/good-suggestion-criteria.md)를 참고해 주세요.

## Before opening an issue

이슈를 열기 전에 README와 관련 문서를 먼저 확인해 주세요.

fork 실행이나 설정에서 막혔다면 [Fork Setup Guide](docs/getting-started/fork-setup.md)와
[Runtime Configuration](docs/getting-started/runtime-configuration.md)을 먼저 확인해 주세요.

demo나 screenshot 제안은 [Demo guide](docs/demo.md)의 redaction 기준을 따릅니다.

이미 같은 제안이 있는지 기존 issue와 PR도 가볍게 확인해 주세요.

제안하는 출처나 OSS 후보가 공개적으로 접근 가능한지 확인해 주세요.

광고, 제휴, 자기 홍보 성격이 있다면 숨기지 말고 명확히 밝혀 주세요.

민감 정보, API key, token, webhook URL, 개인 연락처는 이슈에 포함하지 마세요.

## Issue types

현재 이슈는 다음 흐름을 중심으로 받습니다.

- 백엔드 커리어 질문
- 정보 출처 제안
- OSS 기여 후보 제안
- 문서 개선 제안
- 깨진 링크 또는 오래된 출처 제보
- 지역 또는 언어 확장 아이디어

이슈 템플릿은 더 나은 브리핑을 만들기 위한 자료 수집용입니다.

이슈를 작성한다고 해서 Career Feed가 외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 수행하지 않습니다.

## Pull request guidelines

한 PR에는 하나의 주제를 담아 주세요.

문서 수정 PR은 어떤 문서를 왜 바꾸는지 설명해 주세요.

가능하면 문서 변경, workflow 변경, validator 변경은 서로 다른 PR로 분리해 주세요.

큰 기능, 새 지역, 새 workflow, 자동화 정책 변경은 PR 전에 issue로 먼저 논의해 주세요.

불필요한 리팩터링, 대규모 포맷 변경, 관련 없는 파일 변경은 피해주세요.

요청한 범위와 직접 관련된 파일만 수정해 주세요.

코드나 script를 변경했다면 가능한 범위에서 관련 검증 명령을 함께 적어 주세요.

generated brief, validator, Discord delivery 정책을 바꾸는 경우 dry-run artifact 또는 validation report를 확인해 주세요.

이번 프로젝트의 기본 방향과 맞지 않는 PR은 수정 요청을 받거나 닫힐 수 있습니다.

## Development setup

저장소를 로컬에서 확인하려면 다음 명령으로 시작합니다.

```bash
git clone https://github.com/stdiodh/career-feed.git
cd career-feed
./scripts/validate.sh
```

문서만 수정했다면 다음 명령도 함께 확인해 주세요.

```bash
python3 scripts/check-doc-format.py
git diff --check
```

Daily Backend 후보 수집 dry-run은 다음 명령으로 확인할 수 있습니다.

```bash
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
```

GitHub Actions 수동 실행과 artifact 확인 흐름은 [Usage Guide](docs/getting-started/usage.md)를 참고해 주세요.

## Commit convention

커밋 메시지는 Angular 스타일을 권장합니다.

기본 형식은 scope가 필요할 때 `type(scope): subject`를 사용합니다.

scope가 필요 없다면 `type: subject`를 사용합니다.

허용하는 type은 다음과 같습니다.

- `feat`
- `fix`
- `docs`
- `style`
- `refactor`
- `test`
- `chore`

문서만 바꾸는 PR은 대부분 `docs:`를 사용합니다.

subject는 짧고 명확하게 작성합니다.

subject 끝에는 마침표를 붙이지 않습니다.

예시는 다음과 같습니다.

```text
docs: update demo asset guide
docs(contributing): clarify PR checklist
fix: correct broken documentation link
test: add validator fixture
chore: refresh generated report ignore rules
```

## Pull request template

PR template 위치는 `.github/pull_request_template.md`입니다.

PR을 열 때는 변경 내용, 변경 이유, 검증 결과를 반드시 채워 주세요.

문서만 바꾼 PR도 `git diff --check` 결과를 적어 주세요.

관련 문서 포맷 검증을 실행했다면 그 결과도 적어 주세요.

secret, webhook, private identifier 체크박스는 직접 확인한 뒤 표시해 주세요.

demo asset을 추가하거나 교체한 경우 redaction을 사람이 직접 확인했다고 적어 주세요.

workflow, secrets, issue template, validator 정책을 바꾸는 PR은 범위를 명확히 적어 주세요.

그런 변경은 가능하면 PR 전에 issue로 먼저 논의해 주세요.

## Local validation

기본 검증 명령은 다음과 같습니다.

```bash
./scripts/validate.sh
```

문서만 수정했다면 다음 명령도 함께 확인해 주세요.

```bash
git diff --check
```

문서 줄 수, 숨은 문자, README 링크 같은 추가 검증이 필요한 경우 PR 설명에 실행한 명령을 적어 주세요.

검증을 실행하지 못했다면 이유를 명확히 적어 주세요.

pytest가 로컬 환경에 설치되어 있지 않을 수 있습니다.

그 경우 저장소의 직접 실행 테스트와 `./scripts/validate.sh` 결과를 우선 적고, pytest 미실행 이유를 PR에 남겨 주세요.

## File management

`reports/` 아래 생성 산출물은 기본적으로 커밋하지 않습니다.

demo asset은 `docs/assets/demo/`에만 둡니다.

큰 mp4, raw recording, 긴 영상 파일은 저장소에 직접 커밋하지 않습니다.

긴 영상은 GitHub Release asset, PR attachment, project page, external video link 등으로 분리해 주세요.

placeholder 파일은 만들지 않습니다.

링크를 맞추기 위해 빈 이미지 파일을 추가하지 않습니다.

secret, token, webhook URL, private repository URL, 개인 식별자가 포함된 파일은 커밋하지 않습니다.

## Documentation contribution rules

문서는 실제 줄바꿈이 있는 Markdown으로 작성합니다.

한 줄짜리 압축 Markdown을 만들지 않습니다.

escaped newline 문자열로 줄바꿈을 흉내 내지 않습니다.

표의 각 행은 별도 줄로 작성합니다.

목록의 각 항목은 별도 줄로 작성합니다.

heading 앞뒤에는 빈 줄을 둡니다.

fake metrics나 과장된 OSS 영향력 주장을 문서에 넣지 않습니다.

자세한 문서 기여 흐름은 [Contribution guide index](docs/contributing/README.md)를 참고해 주세요.

## Source suggestion rules

정보 출처를 제안할 때는 URL, 출처 종류, 지역, 언어, 업데이트 주기, 주의점을 함께 적어 주세요.

출처가 공개적으로 접근 가능한지 확인해 주세요.

로그인 뒤 개인화된 정보만 제공하는 출처는 반영하기 어렵습니다.

paywall 뒤에 핵심 정보가 있는 출처도 제한될 수 있습니다.

불법 scraping이나 약관 위반 위험이 큰 출처는 받지 않습니다.

자세한 기준은 [Source suggestion guide](docs/contributing/source-suggestion-guide.md)를 참고해 주세요.

## OSS candidate suggestion rules

OSS 후보를 제안할 때는 repository URL, 관련 issue URL, beginner-friendly signal, 백엔드 학습과의 관련성을 적어 주세요.

좋은 후보는 공개 repository이고, license가 명확하며, README 또는 CONTRIBUTING이 있고, build/test 방법이 어느 정도 설명되어 있습니다.

`good first issue`, `help wanted`, 작은 문서 수정, 작은 테스트 개선 같은 signal은 검토에 도움이 됩니다.

issue URL을 제안한다면 기본적으로 최근 30일 이내 `created_at` issue인지 확인해 주세요.
`updated_at`만 최근인 오래된 issue는 추천 후보에서 제외될 수 있습니다.

OSS 후보를 추천할 수 있지만 외부 저장소에 자동 PR, 자동 comment, 자동 assign, 자동 label 변경을 하지 않습니다.

자세한 기준은 [OSS candidate suggestion guide](docs/contributing/oss-candidate-guide.md)를 참고해 주세요.
최종 추천 정책은 [OSS Candidate Policy](docs/policies/oss-candidate-policy.md)를 따릅니다.

## Backend career question rules

백엔드 커리어 질문에는 현재 학습 단계, 관심 기술 스택, 목표, 시도해 본 것, 막힌 지점, 원하는 도움의 형태를 적어 주세요.

질문은 평가나 비난을 위한 자료가 아닙니다.

질문은 더 나은 학습·커리어 브리핑을 만들기 위한 자료입니다.

전화번호, 주소, 주민등록번호, 사적인 계정, 비공개 회사 정보, API key, webhook URL은 올리지 마세요.

자세한 작성 기준은 [Backend career question guide](docs/contributing/backend-career-question-guide.md)를 참고해 주세요.

## International and regional suggestions

지역 또는 언어 확장 제안은 환영하지만, 바로 workflow에 반영되지는 않습니다.

새 지역 제안에는 region, locale, language, timezone, source reliability, public availability를 함께 적어 주세요.

예를 들어 `region=jp`, `locale=ja-JP`, `language=ja`, `timezone=Asia/Tokyo`처럼 구체적으로 적으면 검토가 쉬워집니다.

해당 지역의 공개 출처를 maintainer가 검토할 수 있는지도 중요합니다.

모든 국가를 이미 지원한다고 주장하지 않습니다.

지역 확장은 maintainer review와 source policy가 준비된 뒤에만 진행합니다.

## Secret safety

다음 값은 절대 commit, issue, PR, log, 문서 예시에 포함하지 마세요.

- OpenAI API key
- Discord Webhook URL
- GitHub token
- Naver API credentials
- OpenAI organization ID
- 개인 이메일
- 기타 credentials

필요한 값은 GitHub Secrets 또는 로컬 환경변수로만 다룹니다.

민감 정보가 노출되었다면 공개 이슈에 값을 붙여 넣지 말고 maintainer가 공개한 기존 연락 경로를 사용해 먼저 알려 주세요.

## Automation boundaries

Maintainer-reviewed automation입니다.

OpenAI API는 브리핑 초안, 검증 리포트, 학습 주제 우선순위화, OSS 후보 정리에 사용할 수 있습니다.

외부 저장소에 자동 댓글을 작성하거나, 자동 PR을 만들거나, issue를 자동 assign하거나, label을 자동 변경하지 않습니다.

무검토 배포나 외부 maintainer에게 부담을 주는 자동화는 프로젝트 범위 밖입니다.

## Maintainer review policy

Maintainer는 제안을 다음 기준으로 검토합니다.

- 프로젝트 범위와 맞는가
- 백엔드 학습자에게 실제로 도움이 되는가
- 출처가 공개적이고 검증 가능한가
- 개인정보, secret, credential 위험이 없는가
- 특정 회사나 서비스 홍보로 오해될 가능성이 있는가

거절은 contributor 개인에 대한 평가가 아니라 프로젝트 범위, 안전성, 유지보수 가능성 기준에 따른 판단입니다.

자세한 기준은 [Maintainer review policy](docs/contributing/review-policy.md)를 참고해 주세요.

## Code of Conduct

참여자는 [Code of Conduct](CODE_OF_CONDUCT.md)를 따라야 합니다.

초보자 질문을 비난하지 않습니다.

지역, 언어, 배경, 경력 수준이 다른 contributor를 존중합니다.

제안이 거절될 수 있으며, 거절은 사람에 대한 평가가 아닙니다.

## Related documents

- [Contribution guide index](docs/contributing/README.md)
- [Contributor Task Ideas](docs/project/contributor-tasks.md)
- [Roadmap](docs/project/roadmap.md)
- [Good suggestion criteria](docs/contributing/good-suggestion-criteria.md)
- [Source suggestion guide](docs/contributing/source-suggestion-guide.md)
- [OSS candidate suggestion guide](docs/contributing/oss-candidate-guide.md)
- [Backend career question guide](docs/contributing/backend-career-question-guide.md)
- [Maintainer review policy](docs/contributing/review-policy.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
