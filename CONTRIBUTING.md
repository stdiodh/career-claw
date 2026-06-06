# Contributing to Career Feed

## Welcome

Career Feed는 백엔드 지망생과 주니어 개발자를 위한 공개 자동 브리핑 workflow입니다.

기여는 프로젝트의 운영 범위를 작게 유지하면서도 학습자에게 실제로 도움이 되는 정보를 더 정확하게 만드는 방향을 환영합니다.

이 저장소는 초기 단계입니다.

큰 사용 지표나 과장된 adoption을 만들기보다, 작은 개선을 검증 가능하게 쌓는 것을 우선합니다.

## Ways to contribute

다음 기여를 환영합니다.

- 백엔드 학습 주제 제안
- Spring Boot, JVM, Kotlin 로드맵 보완
- Programmers PS 루틴 개선 제안
- 주니어 백엔드 실무 지식 주제 제안
- 채용, 인턴, 대외활동, 해커톤, 공모전 출처 제안
- 한국 개발·AI 뉴스 출처 제안
- OSS 기여 후보 저장소나 issue 제안
- beginner-friendly 기준에 대한 의견
- 깨진 링크 제보
- 오래된 문서 수정
- README, docs, issue template 개선

작은 문서 수정도 환영합니다.

## Before opening an issue

이슈를 열기 전에 README와 관련 문서를 먼저 확인해 주세요.

이미 같은 제안이 있는지 기존 issue도 가볍게 확인해 주세요.

제안하는 출처나 OSS 후보는 공개적으로 확인 가능한 링크를 포함해 주세요.

개인정보, secret, API key, token, webhook URL은 이슈에 포함하지 마세요.

## Issue templates

현재 issue template은 다음 용도를 다룹니다.

- 백엔드 커리어 질문
- 정보 출처 제안
- OSS 기여 후보 제안

템플릿은 더 나은 브리핑을 만들기 위한 자료 수집용입니다.

이슈를 작성한다고 해서 Career Feed가 외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 수행하지 않습니다.

OSS 후보는 maintainer와 사용자가 검토할 수 있는 추천 정보로만 다룹니다.

## Pull request guidelines

한 PR에는 하나의 주제를 담아 주세요.

큰 기능, workflow 변경, 운영 정책 변경은 PR 전에 issue로 먼저 논의해 주세요.

불필요한 리팩터링이나 대규모 포맷 변경은 피해주세요.

요청한 범위와 직접 관련된 파일만 수정해 주세요.

문서 변경은 실제 줄바꿈이 있는 Markdown으로 작성해 주세요.

표의 각 행과 목록의 각 항목은 별도 줄로 작성해 주세요.

코드나 script를 변경했다면 가능한 범위에서 관련 검증 명령을 함께 적어 주세요.

## Local validation

기본 검증 명령은 다음과 같습니다.

```bash
./scripts/validate.sh
```

문서나 issue template만 수정했다면 다음 명령도 유용합니다.

```bash
ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p); puts "YAML OK: #{p}" }' .github/ISSUE_TEMPLATE/*.yml
git diff --check
```

검증을 실행하지 못했다면 PR 설명에 이유를 적어 주세요.

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

민감 정보가 노출되었다면 공개 이슈에 값을 붙여 넣지 말고 maintainer에게 먼저 비공개로 알려 주세요.

## Scope boundaries

현재 운영 범위는 GitHub Actions, OpenAI API, Discord Webhook 기반 자동 브리핑 workflow입니다.

현재 범위에 포함하지 않는 항목은 다음과 같습니다.

- 상시 실행 서버
- 데이터베이스
- 웹 대시보드
- Discord Gateway Bot
- Slash Command
- 외부 저장소 자동 댓글
- 외부 저장소 자동 PR
- 외부 저장소 자동 assign
- 외부 저장소 자동 label 변경

이 범위를 넘는 변경은 먼저 issue에서 논의해야 합니다.

## Review policy

Maintainer는 다음 기준으로 issue와 PR을 검토합니다.

- 변경이 Career Feed의 현재 운영 범위에 맞는가
- secret이나 민감 정보가 포함되지 않았는가
- fake metrics나 과장된 adoption 표현이 없는가
- 외부 저장소 maintainer를 방해할 수 있는 자동화가 없는가
- 검증 가능한 작은 변경인가
- 문서와 workflow 설명이 실제 저장소 상태와 맞는가

OpenAI API 결과는 검토 가능한 초안으로만 다룹니다.

무검토 배포나 외부 저장소 자동 행동에는 사용하지 않습니다.

## Code of Conduct

참여자는 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)를 따라야 합니다.

질문과 제안은 학습자를 평가하거나 비난하기 위한 것이 아닙니다.

더 나은 학습·커리어 브리핑을 만들기 위한 자료로 다룹니다.

## Maintainer notes

Maintainer는 프로젝트를 초기 단계의 공개 OSS로 정직하게 설명합니다.

사용 지표, 조직 사용, adoption, downloads, active users를 과장하지 않습니다.

외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 하지 않는 정책을 유지합니다.

제안된 출처와 OSS 후보는 사람이 검토할 수 있는 자료로만 반영합니다.
