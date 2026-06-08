# Source Suggestion Guide

## What counts as a source

Career Feed에서 source는 브리핑 후보를 만들 때 참고할 수 있는 공개 정보 출처를 의미합니다.

source는 학습 주제, 뉴스, 채용, 인턴, 대외활동, OSS 기여 후보, 공식 문서, 기술 블로그를 포함할 수 있습니다.

source는 maintainer가 직접 검토할 수 있어야 합니다.

비공개 링크, 개인 계정 화면, 로그인 뒤 개인화된 정보만 있는 페이지는 source로 다루기 어렵습니다.

## Recommended source types

추천할 수 있는 source type은 다음과 같습니다.

- 기술 뉴스
- 회사 기술 블로그
- 채용 공고
- 인턴 공고
- 대외활동
- 컨퍼런스 또는 세미나
- 백엔드 학습 자료
- 공식 문서
- OSS contribution guide
- 공개 repository issue list

source type을 명확히 적으면 검토가 빨라집니다.

## Source quality checklist

좋은 출처 제안은 다음 기준을 만족합니다.

- 공개 접근이 가능합니다.
- 업데이트 주기를 어느 정도 확인할 수 있습니다.
- 특정 지역 또는 언어와의 관련성이 명확합니다.
- 광고성 여부가 투명합니다.
- 백엔드 학습자에게 왜 도움이 되는지 설명할 수 있습니다.
- 만료 공고나 오래된 글만 쌓이는 출처가 아닙니다.
- 개인정보 제출 없이 주요 정보를 확인할 수 있습니다.
- 약관 위반 가능성이 낮습니다.

모든 항목을 완벽히 만족해야 하는 것은 아닙니다.

하지만 부족한 항목은 제안에 함께 적어 주세요.

## Region-specific source suggestions

지역 기반 출처를 제안할 때는 metadata를 포함해 주세요.

권장 metadata는 다음과 같습니다.

- region
- locale
- language
- timezone
- source category
- public availability
- update frequency
- caveats

예를 들어 한국 채용 출처는 `region=kr`, `locale=ko-KR`, `timezone=Asia/Seoul`처럼 적을 수 있습니다.

일본 출처라면 `region=jp`, `locale=ja-JP`, `timezone=Asia/Tokyo`처럼 적을 수 있습니다.

지역 제안은 바로 workflow에 반영되지 않습니다.

source reliability와 maintainer review 가능성을 먼저 확인합니다.

## Examples of strong source suggestions

강한 제안 예시:

> 이 회사 기술 블로그는 Java, Spring Boot, MySQL 장애 대응 글을 공개로 제공하며 RSS가 있고 최근 3개월에도 글이 올라왔습니다.

강한 제안 예시:

> 이 채용 페이지는 한국 백엔드 인턴 공고를 공개 URL로 제공하고, 로그인 없이 공고 상세를 확인할 수 있습니다.

강한 제안 예시:

> 이 컨퍼런스 페이지는 backend, cloud, database 세션 목록을 공개하고 발표 자료 링크를 사후 공개합니다.

강한 제안 예시:

> 이 공식 문서는 Redis cache invalidation과 TTL 관련 개념을 설명해 Daily Backend Brief 학습 카드의 참고 자료로 적합합니다.

## Examples of weak source suggestions

약한 제안 예시:

> 여기 유명한 곳입니다.

약한 제안 예시:

> 로그인해서 보면 좋은 정보가 많습니다.

약한 제안 예시:

> 제 서비스도 같이 홍보해 주세요.

약한 제안 예시:

> 이 사이트를 전부 크롤링하면 됩니다.

약한 제안 예시:

> 이 credential로 들어가면 확인할 수 있습니다.

이런 제안은 검토 가능한 정보와 안전 기준이 부족합니다.

## Sources that may be rejected

다음 출처는 거절될 수 있습니다.

- 로그인 뒤 개인화된 정보만 제공하는 출처
- paywall 뒤에 핵심 정보가 있는 출처
- 개인정보를 수집해야 주요 정보를 확인할 수 있는 출처
- 불법 scraping이나 약관 위반 위험이 큰 출처
- 광고 또는 홍보 목적이 숨겨진 출처
- 만료 공고만 많은 출처
- 업데이트가 중단된 것으로 보이는 출처
- 백엔드 학습 또는 커리어 준비와의 관련성이 불명확한 출처

거절은 제안자에 대한 평가가 아닙니다.

프로젝트 범위와 안전 기준에 따른 판단입니다.

## Privacy and scraping boundaries

출처를 자동으로 무제한 수집하지 않습니다.

개인정보를 요구하는 출처는 신중하게 다룹니다.

비공개 정보나 credential을 이용한 접근은 허용하지 않습니다.

robots, terms, rate limit, public access 조건을 존중해야 합니다.

채용 정보나 커리어 정보는 사람에게 영향을 줄 수 있으므로 과장된 표현을 피합니다.

수집 가능 여부가 불확실하면 먼저 maintainer review를 요청합니다.

## Maintainer review flow

Source suggestion은 다음 순서로 검토합니다.

- 출처 URL이 공개적으로 접근 가능한지 확인합니다.
- source type과 region metadata가 충분한지 확인합니다.
- 백엔드 학습자에게 도움이 되는지 확인합니다.
- 광고성 또는 제휴성 위험을 확인합니다.
- 개인정보와 scraping 위험을 확인합니다.
- 업데이트 주기와 만료 위험을 확인합니다.
- 현재 workflow와 문서 범위에 맞는지 확인합니다.

검토 결과는 accepted, accepted with edits, needs more context, out of scope, declined for safety 중 하나일 수 있습니다.

필요하면 더 작은 범위로 다시 제안해 달라고 요청할 수 있습니다.
