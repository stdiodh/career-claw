# OSS Candidate Suggestion Guide

## Purpose

Career Feed에 OSS 기여 후보를 제안할 때의 기준입니다.

백엔드 지망생과 주니어 개발자가 살펴볼 만한 repository나 issue를 정리할 수 있습니다.

하지만 외부 저장소에서 직접 기여 행동을 수행하지는 않습니다.

OSS 후보 제안은 maintainer와 학습자가 검토할 수 있는 자료입니다.

## What makes an OSS candidate useful

좋은 OSS 후보는 다음 특징을 갖습니다.

- 공개 repository입니다.
- license가 명확합니다.
- README 또는 CONTRIBUTING 문서가 있습니다.
- build 또는 test 방법이 어느 정도 설명되어 있습니다.
- 작은 문서 수정, 테스트 개선, 버그 재현, 예제 보완 같은 입문 가능한 기회가 있습니다.
- 백엔드 학습과의 관련성이 있습니다.
- 외부 maintainer에게 부담을 주지 않는 방식으로 제안됩니다.

## Beginner-friendly signals

beginner-friendly signal은 다음과 같습니다.

- `good first issue`
- `help wanted`
- clear reproduction steps
- small documentation fix
- small test improvement
- clear contribution guide
- simple sample update
- small error message improvement
- well-scoped bug report

label만으로 충분하지는 않습니다.

issue 내용, 최근 활동, contribution guide, build/test 난이도를 함께 봅니다.

## Backend relevance

백엔드 관련성은 다음 형태로 설명할 수 있습니다.

- Java, Spring Boot, Kotlin, JVM 관련 repository
- database, cache, message queue 관련 repository
- API, HTTP, authentication, logging, observability 관련 repository
- build, test, documentation 흐름을 익히기 좋은 backend-adjacent repository
- backend framework 또는 library의 작은 문서·테스트 개선 기회

프론트엔드나 모바일 repository도 backend 학습과 연결점이 명확하면 검토할 수 있습니다.

연결점이 없다면 Career Feed 범위 밖일 수 있습니다.

## Safety boundaries

OSS 후보를 추천할 수 있습니다.

외부 저장소에 자동 댓글을 작성하거나, 자동 PR을 만들거나, issue를 자동 assign하거나, label을 자동 변경하지 않습니다.

외부 maintainer의 정책을 우회하지 않습니다.

외부 저장소에 참여할 때는 해당 repository의 contribution guide와 maintainer 요청을 우선합니다.

## Good examples

좋은 OSS 후보 예시:

> 이 repository는 Java 기반이고 CONTRIBUTING.md가 있으며, `good first issue` label이 붙은 작은 documentation issue가 있습니다.

좋은 OSS 후보 예시:

> 이 issue는 재현 단계가 명확하고 test 추가로 해결할 수 있어 백엔드 입문자가 build/test 흐름을 익히기 좋습니다.

좋은 OSS 후보 예시:

> 이 Spring 관련 library는 README 예제가 오래되었고 maintainer가 documentation contribution을 받고 있습니다.

좋은 OSS 후보 예시:

> 이 repository는 license가 명확하고 최근 activity가 있으며, 작은 error message 개선 issue가 열려 있습니다.

## Weak examples

약한 OSS 후보 예시:

> 유명한 repo라서 넣어 주세요.

약한 OSS 후보 예시:

> license는 모르겠지만 괜찮아 보입니다.

약한 OSS 후보 예시:

> 이 repo에 자동으로 댓글 달아서 우리 프로젝트를 소개해 주세요.

약한 OSS 후보 예시:

> maintainer가 답을 안 하니 자동 PR을 계속 보내면 됩니다.

약한 OSS 후보 예시:

> 보안 취약점 exploit을 따라 해 보면 공부가 됩니다.

이런 제안은 안전성, 검토 가능성, 외부 maintainer 존중 기준을 충족하지 못합니다.

## What Career Feed will not do

다음은 하지 않습니다.

- 외부 저장소 자동 PR, comment, assign, label 변경
- 외부 maintainer에게 특정 issue를 beginner-friendly로 바꾸라고 요구
- license가 불명확하거나 악용 위험이 큰 후보 추천
- 보안 취약점 exploit 중심 이슈를 입문 후보로 추천

## Maintainer checklist

OSS 후보는 다음 기준으로 확인합니다.

- repository가 공개되어 있는가
- license가 명확한가
- README 또는 CONTRIBUTING이 있는가
- build/test 방법이 설명되어 있는가
- beginner-friendly signal이 있는가
- 백엔드 학습과의 관련성이 설명되어 있는가
- 최근 activity가 확인되는가
- 외부 maintainer에게 부담을 주지 않는가
- 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 요구하지 않는가

후보가 좋아 보여도 stale issue, 불명확한 license, 과도한 난이도 때문에 보류될 수 있습니다.

보류는 제안자에 대한 평가가 아니라 학습자 안전과 유지보수 가능성 기준에 따른 판단입니다.
