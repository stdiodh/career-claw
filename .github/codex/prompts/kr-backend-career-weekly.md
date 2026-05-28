# Career Feed Backend Career Weekly Prompt

이 프롬프트는 Career Feed의 주간 백엔드 커리어 브리핑 전용이다.

중요:
- OpenAI API 비용이 발생할 수 있다.
- 후보 JSON과 사용자 프로필 JSON을 먼저 읽고, 후보에 없는 항목을 임의로 추가하지 않는다.
- Secret, API Key, Webhook URL은 절대 출력하지 않는다.
- 공고/대회 전문을 복사하거나 저장하지 않는다.
- 최종 Markdown은 반드시 `reports/briefs/kr-backend-career-weekly.md`에 직접 작성한다.

workflow는 `{{KST_NOW}}`를 현재 Asia/Seoul 기준시각으로 치환한다. 이 시각을 기준으로 마감 여부와 지원 가능성을 판단한다.

## 목표

사용자가 이번 주 실제로 지원하거나 참가할 수 있는 백엔드 커리어 기회만 짧게 선별한다. 내부 추천 근거 설명보다 마감, 회사/주최, 역할, 지원 조건, 전형/제출물, 이번 주 액션을 우선한다.

## 입력 파일

다음 파일을 읽고 선별 근거로 사용한다. split 후보 파일이 없으면 `kr-backend-career-events.json`만으로 작성한다.

- `reports/candidates/kr-backend-career-events.json`
- `reports/candidates/kr-backend-intern-jobs.json`
- `reports/candidates/kr-backend-entry-jobs.json`
- `reports/candidates/kr-backend-career-activities.json`
- `reports/candidates/kr-backend-company-watchlist.json`
- `configs/audience-profile.json`

후보의 `title`, `url`, `source_url`, `source`, `company_or_host`, `type`, `role`, `deadline_text`, `deadline_status`, `days_until_deadline`, `target`, `tech_keywords`, `process_or_deliverable`, `summary`, `score`, `deadline_clarity_score`, `backend_fit_score`, `entry_fit_score`, `portfolio_fit_score`, `source_reliability_score`, `actionability_score`, `exclude_reason`을 참고한다.

## 출력 파일

- `reports/briefs/kr-backend-career-weekly.md`

## 출력 구조

아래 Markdown 구조를 그대로 따른다.

```markdown
# Career Feed - Backend Career Weekly
기준시각: {{KST_NOW}}

이번 주 요약:
- 이번 주 지원/참가 관점에서 가장 먼저 확인할 흐름 1문장

## 1. 이번 주 백엔드 커리어 기회 TOP 5

### 1. 공고/활동 제목
- 유형: 인턴/신입/주니어/해커톤/공모전/경진대회
- 마감: YYYY-MM-DD HH:mm KST (D-n) / 상시채용 / 채용 시 마감
- 회사/주최:
- 직무/역할:
- 지원 조건:
- 기술 키워드:
- 전형/제출물:
- 이번 주 액션:
- 출처:
- 링크: [원문 보기](URL)

## 2. 마감 임박
- [D-2] 회사명 백엔드 인턴 - 2026-06-03 23:59 KST - [원문 보기](URL)

## 3. 포트폴리오로 남기기 좋은 대외활동

### 활동명
- 유형: 해커톤/공모전/경진대회
- 마감:
- 주최:
- 만들 수 있는 백엔드 산출물:
- 기술 키워드:
- 이번 주 액션:
- 링크: [원문 보기](URL)
```

TOP 5 후보가 없으면 `## 1. 이번 주 백엔드 커리어 기회 TOP 5` 아래에 아래 문장만 쓴다.

- 이번 주 기준을 만족하는 백엔드 커리어 기회가 없습니다.

마감 임박 후보가 없으면 `## 2. 마감 임박` 아래에 아래 문장만 쓴다.

- 이번 주 마감 임박 항목은 없습니다.

포트폴리오 후보가 없으면 `## 3. 포트폴리오로 남기기 좋은 대외활동` 아래에 아래 문장만 쓴다.

- 이번 주 포트폴리오용 대외활동 후보는 없습니다.

## 선별 규칙

- TOP 5는 최대 5개만 포함한다.
- TOP 5에는 상세 공고/상세 활동 URL만 사용한다.
- 플랫폼 메인, 목록, 검색 URL은 TOP 5에 넣지 않는다.
- `exclude_reason`이 있으면 추천하지 않는다.
- `deadline_status`가 `closed`인 항목은 추천하지 않는다.
- TOP 5는 마감이 명확한 후보를 우선한다.
- TOP 5의 `마감`에는 `원문 확인 필요`, `확인 필요`, `미정`, `알 수 없음`을 쓰지 않는다.
- 허용되는 마감 표현은 `YYYY-MM-DD HH:mm KST (D-n)`, `YYYY-MM-DD KST (D-n)`, `상시채용`, `채용 시 마감`뿐이다.
- `상시채용`과 `채용 시 마감`은 후보 JSON 또는 원문 요약에 그렇게 표시된 경우만 사용한다.
- 시니어/경력직 전용은 추천하지 않는다.
- 경력 3년 이상 또는 5년 이상 조건은 추천하지 않는다.
- 프론트엔드, 디자인, 마케팅, 영업, PM 단독 후보는 추천하지 않는다.
- 단순 교육 광고, 부트캠프 광고, 강의, 서포터즈는 추천하지 않는다.
- 기사형 뉴스가 실제 공고 상세 URL로 연결되지 않으면 TOP 5에 넣지 않는다.
- 신입/인턴/주니어 백엔드 채용을 해커톤/공모전보다 우선하되, 포트폴리오 전환성이 매우 높은 활동은 1~2개 포함할 수 있다.
- 동일 회사/동일 유형이 너무 많으면 다양성을 고려하되, 품질이 높은 후보를 우선한다.

## 필드 작성 규칙

- `유형`은 인턴, 신입, 주니어, 해커톤, 공모전, 경진대회 중 하나로 정규화한다.
- `회사/주최`는 채용이면 회사명, 대외활동이면 주최기관 또는 운영기관을 쓴다.
- `직무/역할`은 채용이면 실제 직무명, 대외활동이면 팀 안에서 백엔드로 맡을 수 있는 역할을 쓴다.
- `지원 조건`은 실제 조건만 짧게 쓴다. 불명확한 후보는 TOP 5 우선순위를 낮춘다.
- `기술 키워드`는 Java, Kotlin, Spring Boot, REST API, DB, MySQL, PostgreSQL, Redis, Kafka, AWS, Docker, Kubernetes, AI API, LLM, Python 중 실제 관련 키워드만 쓴다.
- 기술 키워드가 원문에 없으면 과장하지 말고 `백엔드, API, DB` 정도로 제한한다.
- `전형/제출물`은 채용이면 서류, 코딩테스트, 과제, 면접 등을 쓰고, 대외활동이면 기획서, GitHub, 발표자료, 결과물 URL, 모델/API 제출물 등을 쓴다.
- `이번 주 액션`은 딱 하나의 행동만 쓴다.
- `이번 주 액션`에는 "원문을 확인합니다"처럼 막연한 문장을 쓰지 않는다.

## 출력 금지

최종 Markdown에는 아래 문구를 절대 출력하지 않는다.

- 대상 적합성
- 백엔드 적합성
- Kotlin/Spring Boot 관련성
- 왜 나에게 맞는가
- 내 액션
- 제외한 후보
- 원문 확인 필요
- 확인 필요
- 미정

Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다. 링크는 raw URL 단독 표기가 아니라 `[원문 보기](URL)` 형식으로만 쓴다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-backend-career-weekly.md`에 작성한다.
