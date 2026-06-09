# Maintainer Review Policy

> Language: [한국어](./review-policy.md) | [English](../../en/contributing/review-policy.md)

## Review principles

Career Feed maintainer review는 제안자를 평가하기 위한 절차가 아닙니다.

Review는 프로젝트 범위, 학습자에게 주는 가치, 안전성, 유지보수 가능성을 확인하기 위한 절차입니다.

초기 단계의 공개 OSS입니다.

따라서 작고 검토 가능한 제안을 우선합니다.

과장된 영향력 주장이나 fake metrics보다 공개 근거와 명확한 범위를 더 중요하게 봅니다.

## What maintainers look for

다음 기준을 확인합니다.

- project scope와 맞는가
- 백엔드 학습자에게 도움이 되는가
- 주니어 개발자의 커리어 탐색에 도움이 되는가
- 출처가 공개적이고 검증 가능한가
- 자동화가 안전한가
- 개인정보나 secret 위험이 없는가
- 특정 회사나 서비스 홍보로 오해될 가능성이 있는가
- 지역 또는 언어 확장 시 maintainer가 검토 가능한가
- 유지보수 부담이 현재 프로젝트 단계에 맞는가

모든 기준을 완벽히 충족해야 하는 것은 아닙니다.

부족한 정보가 있으면 maintainer가 추가 맥락을 요청할 수 있습니다.

## Why suggestions may be declined

제안은 여러 이유로 거절될 수 있습니다.

- 프로젝트 범위 밖입니다.
- 백엔드 학습 또는 커리어 준비와의 관련성이 약합니다.
- 공개적으로 확인 가능한 근거가 부족합니다.
- secret, credential, 개인정보 위험이 있습니다.
- 광고성 또는 제휴성이 숨겨져 있습니다.
- 불법 scraping이나 약관 위반 위험이 있습니다.
- 외부 저장소 maintainer에게 부담을 줄 수 있습니다.
- 유지보수 부담이 현재 단계에 비해 큽니다.
- 새 workflow나 새 지역 추가가 충분히 설계되지 않았습니다.

거절은 contributor 개인에 대한 평가가 아닙니다.

거절은 프로젝트 범위, 안전성, 유지보수 가능성 기준에 따른 판단입니다.

## Automation review boundaries

Maintainer-reviewed automation을 사용합니다.

자동화는 브리핑 초안, 검증 리포트, 학습 주제 우선순위화, OSS 후보 정리에 사용할 수 있습니다.

자동화가 외부 저장소에 직접 행동하는 것은 허용하지 않습니다.

외부 저장소에 자동 댓글을 작성하거나, 자동 PR을 만들거나, issue를 자동 assign하거나, label을 자동 변경하지 않습니다.

자동화 정책 변경은 PR 전에 issue로 논의해야 합니다.

## Regional expansion review

지역 확장은 source reliability와 maintainer review 가능성을 먼저 봅니다.

새 지역 제안에는 region, locale, language, timezone이 필요합니다.

source가 공개적으로 접근 가능한지도 중요합니다.

해당 지역의 채용, 뉴스, 이벤트 출처가 개인정보나 약관 위험 없이 검토 가능한지 확인합니다.

자동 번역만으로 오해가 생길 수 있는 영역은 보수적으로 봅니다.

모든 국가를 한 번에 지원하는 방식은 지양합니다.

작은 country or region pack 단위의 제안을 선호합니다.

## Documentation review

문서 PR은 실제 줄바꿈이 있는 Markdown이어야 합니다.

표의 각 행은 별도 줄이어야 합니다.

목록의 각 항목은 별도 줄이어야 합니다.

heading 앞뒤에는 빈 줄을 둡니다.

문서에는 secret, credential, 개인 이메일, private contact, webhook URL을 넣지 않습니다.

문서에는 stars, forks, downloads, active users, adoption 같은 수치를 임의로 쓰지 않습니다.

과장된 OSS 영향력 표현은 수정 요청을 받을 수 있습니다.

## Security review

공개 issue, PR, 문서에 민감 정보가 포함되었는지 확인합니다.

OpenAI API key, Discord Webhook URL, GitHub token, Naver API credentials, 개인 정보는 공개하면 안 됩니다.

민감 정보가 포함된 경우 수정 요청이나 삭제 요청이 우선됩니다.

외부 저장소에 자동 행동을 추가하는 제안은 보안과 maintainer respect 관점에서 거절될 수 있습니다.

수집 정책이 불명확한 source는 보류될 수 있습니다.

## Decision outcomes

검토 결과는 다음 중 하나일 수 있습니다.

- accepted
- accepted with edits
- needs more context
- out of scope
- declined for safety
- declined for maintenance burden

accepted는 현재 형태로 반영 가능하다는 뜻입니다.

accepted with edits는 방향은 맞지만 문구, 범위, 링크, 검증을 수정해야 한다는 뜻입니다.

needs more context는 URL, 지역, 언어, 업데이트 주기, 관련성 설명이 더 필요하다는 뜻입니다.

out of scope는 현재 Career Feed 범위 밖이라는 뜻입니다.

declined for safety는 개인정보, credential, scraping, 외부 maintainer 압박 위험이 크다는 뜻입니다.

declined for maintenance burden은 현재 단계에서 유지하기 어렵다는 뜻입니다.

## Maintainer communication

가능하면 어떤 기준 때문에 수정이나 거절이 필요한지 설명합니다.

Contributor는 요청받은 맥락을 보완하거나 더 작은 제안으로 나눌 수 있습니다.

같은 요청을 반복해서 압박하기보다 기준에 맞게 정리하는 것이 좋습니다.

프로젝트의 안전성과 유지보수 가능성이 우선입니다.
