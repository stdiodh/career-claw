# Good Suggestion Criteria

## Summary

Career Feed의 제안은 maintainer가 검토할 수 있는 자료여야 합니다.

좋은 제안은 자동화가 바로 실행할 명령이 아니라, 프로젝트 목적에 맞는지 판단할 수 있는 맥락을 제공합니다.

Career Feed는 초기 단계의 공개 OSS이므로 큰 claim보다 작은 근거를 더 중요하게 봅니다.

제안은 백엔드 지망생과 주니어 개발자의 학습·커리어 탐색에 도움이 되는지 설명해야 합니다.

## What a good suggestion includes

좋은 제안에는 다음이 포함됩니다.

- 무엇을 제안하는지 명확한 제목
- 누구에게 도움이 되는지에 대한 설명
- 왜 백엔드 학습 또는 커리어 준비와 관련 있는지에 대한 설명
- 공개적으로 확인 가능한 URL이나 근거
- 지역, 언어, 업데이트 주기, 주의점
- 광고성 또는 제휴성 여부
- maintainer가 검토할 수 있는 범위의 요청
- 자동화가 외부 저장소에 행동하지 않는다는 이해

좋은 제안은 "추가해 주세요"에서 끝나지 않습니다.

좋은 제안은 왜 추가할 가치가 있는지 설명합니다.

## What makes a suggestion hard to review

다음 제안은 검토하기 어렵습니다.

- URL이나 근거가 없습니다.
- 백엔드 학습과의 관련성이 설명되지 않습니다.
- 특정 회사나 서비스 홍보처럼 보이지만 광고성 여부를 밝히지 않습니다.
- 로그인 뒤 개인화된 정보만 확인할 수 있습니다.
- 업데이트 주기나 만료 위험을 알 수 없습니다.
- 외부 저장소에 자동 댓글이나 PR을 요구합니다.
- API key, token, credential 같은 민감 정보를 포함합니다.
- 너무 큰 workflow 변경을 한 번에 요구합니다.

검토하기 어려운 제안은 더 많은 맥락을 요청받을 수 있습니다.

프로젝트 범위와 맞지 않으면 닫힐 수 있습니다.

## Good examples

좋은 출처 제안 예시:

> 이 출처는 한국 백엔드 인턴 공고를 주 1회 이상 업데이트하며, 로그인 없이 확인 가능하고, Spring/Java 관련 공고가 자주 올라옵니다.

좋은 OSS 후보 제안 예시:

> 이 OSS repository는 CONTRIBUTING.md와 good first issue label이 있고, Java 기반이라 백엔드 입문자가 빌드와 테스트 흐름을 익히기 좋습니다.

좋은 학습 주제 제안 예시:

> 이 주제는 Redis cache invalidation을 처음 접하는 사람에게 도움이 되며, Daily Backend Brief의 10분 학습 카드로 적합합니다.

좋은 지역 제안 예시:

> 이 지역 제안은 `region=jp`, `locale=ja-JP`, `timezone=Asia/Tokyo` 기준이며, 공개 채용 페이지와 기술 블로그만 포함합니다.

좋은 커리어 질문 예시:

> Java 문법과 SQL 기본은 공부했고 Spring Boot 프로젝트를 시작하려는데, 게시판 이후 어떤 주제가 백엔드 포트폴리오에 적합한지 모르겠습니다.

좋은 검증 개선 예시:

> README가 raw 기준 한 줄로 압축되는 문제를 막기 위해 heading과 table row 물리 줄바꿈을 검사하는 문서 포맷 검증을 추가하면 좋겠습니다.

## Weak examples

약한 제안 예시:

> 좋은 사이트 같아요.

약한 제안 예시:

> 여기 유명하니까 추가해 주세요.

약한 제안 예시:

> 이 repo에 자동으로 댓글 달아 주세요.

약한 제안 예시:

> 내 서비스 홍보도 같이 넣어 주세요.

약한 제안 예시:

> 채용 정보를 크롤링해서 다 가져오면 됩니다.

약한 제안 예시:

> 이 API key를 써서 확인하면 됩니다.

이런 제안은 목적, 근거, 안전성, maintainer review 가능성이 부족합니다.

## Region and language metadata

지역과 언어가 관련된 제안에는 metadata를 적어 주세요.

권장 metadata는 다음과 같습니다.

- `region`
- `locale`
- `language`
- `timezone`
- source type
- public availability
- update frequency
- review caveats

한국어 문서가 항상 한국 전용인 것은 아닙니다.

영어 문서가 항상 미국 전용인 것도 아닙니다.

language, country, feed를 구분해서 설명해 주세요.

## Evidence and source quality

근거는 공개적으로 확인 가능해야 합니다.

가능하면 공식 문서, 공개 repository, 공개 채용 페이지, 공개 기술 블로그를 사용합니다.

개인화된 검색 결과, 비공개 링크, 로그인 뒤 화면만으로는 검토하기 어렵습니다.

광고성 출처나 제휴 가능성이 있는 출처는 투명하게 밝히면 검토할 수 있습니다.

숨기면 신뢰도가 낮아집니다.

## Maintainer checklist

Maintainer는 제안을 볼 때 다음을 확인합니다.

- 제안이 프로젝트 범위와 맞는가
- 백엔드 학습자 또는 주니어 개발자에게 도움이 되는가
- 공개적으로 확인 가능한 근거가 있는가
- 지역과 언어 metadata가 충분한가
- secret, credential, 개인정보가 없는가
- 광고성 또는 제휴성 위험이 투명한가
- 외부 저장소에 자동 행동을 요구하지 않는가
- 유지보수 부담이 감당 가능한가

이 기준을 통과해도 모든 제안이 바로 반영되는 것은 아닙니다.

반영 시점은 maintainer의 검토 여력과 현재 roadmap에 따라 달라질 수 있습니다.
