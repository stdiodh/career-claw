# Security Alerts

## 목적
백엔드와 플랫폼 운영자가 패치나 대응 여부를 확인해야 하는 보안 이슈를 짧게 알린다.

## 포함할 정보
- CVE 및 취약점 공지
- supply chain, npm, PyPI, container 이미지 이슈
- Docker, Kubernetes, cloud incident
- 실제 패치, 설정 변경, 완화 조치가 필요한 공지

## 제외할 정보
- 공포 조장성 기사
- 패치나 대응 방법이 없는 추측성 글
- 오래된 취약점의 재포장 기사

## 우선순위 키워드
- cve
- vulnerability
- exploit
- patch
- advisory
- supply chain
- npm
- pypi
- docker
- kubernetes
- cloud
- incident
- critical
- high severity

## 제외 키워드
- rumor
- unconfirmed
- sensational
- fear
- 광고
- 공포

## 추천 출처
- 공식 블로그
- 공식 릴리스 노트
- GitHub Release
- 공식 보안 공지
- 신뢰할 수 있는 기술 매체

## 출력 규칙
- 최대 3개만 출력
- 각 항목은 제목, 핵심 1줄, 왜 봐야 함 1줄, 원본 URL, 출처, 발행일만 포함
- 긴 해설 금지
- 추측 금지
- 원문 확인이 필요하면 "원문 확인 필요"라고 표시
