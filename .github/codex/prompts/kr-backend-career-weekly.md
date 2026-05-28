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

사용자가 이번 주 실제로 지원하거나 참가할 수 있는 백엔드 커리어 후보를 5개 유형별로 확인한다. 뉴스 기사나 검색 결과를 공고처럼 해석하지 말고, 실제 상세 URL이 있는 후보만 사용한다.

## 입력 파일

다음 파일을 읽고 선별 근거로 사용한다.

- `reports/candidates/kr-backend-career-events.json`
- `reports/candidates/kr-backend-jobs.json`
- `reports/candidates/kr-backend-interns.json`
- `reports/candidates/kr-backend-hackathons.json`
- `reports/candidates/kr-backend-contests.json`
- `reports/candidates/kr-backend-competitions.json`
- `reports/candidates/kr-backend-intern-jobs.json`
- `reports/candidates/kr-backend-entry-jobs.json`
- `reports/candidates/kr-backend-career-activities.json`
- `reports/candidates/kr-backend-company-watchlist.json`
- `configs/audience-profile.json`

후보의 `weekly_category`, `category_label`, `title`, `url`, `source_url`, `source`, `source_kind`, `source_confidence`, `is_detail_url`, `is_generic_url`, `is_news_article`, `is_active`, `selection_tier`, `freshness_tier`, `verification_status`, `company_or_host`, `company_or_host_confidence`, `type`, `role`, `deadline_text`, `deadline_status`, `deadline_confidence`, `days_until_deadline`, `target`, `tech_or_output_keywords`, `process_or_deliverable`, `summary`, `score`, `exclude_reason`을 참고한다.

선별 우선순위:
- `kr-backend-career-events.json`의 `selected_by_category`가 있으면 우선 사용한다.
- 없으면 5개 유형 split 파일의 `selected`를 사용한다.
- 그래도 없으면 각 파일의 `items`에서 직접 고른다.
- 어떤 경우에도 뉴스, generic URL, expired, `exclude_reason`이 있는 후보는 사용하지 않는다.

## 출력 파일

- `reports/briefs/kr-backend-career-weekly.md`

## 출력 구조

아래 Markdown 구조를 그대로 따른다. 5개 유형 섹션은 항상 출력하고, 각 유형은 후보 0개 또는 1개만 출력한다.

```markdown
# Career Feed - Backend Career Weekly
기준시각: {{KST_NOW}}

이번 주 요약:
- 이번 주 실제 지원/참가 가능한 백엔드 커리어 후보를 5개 유형별로 확인합니다.

## 1. 이번 주 유형별 백엔드 커리어 후보

### 1. 채용
#### 후보: 공고명
- 유형:
- 마감:
- 회사/주최:
- 직무/역할:
- 지원/참가 조건:
- 기술/산출물 키워드:
- 전형/제출물:
- 확인 상태:
- 이번 주 액션:
- 출처:
- 링크: [원문 보기](URL)

### 2. 인턴
- 이번 주 기준을 만족하는 인턴 후보가 없습니다.

### 3. 해커톤
#### 후보: 활동명
- 유형:
- 마감:
- 회사/주최:
- 직무/역할:
- 지원/참가 조건:
- 기술/산출물 키워드:
- 만들 수 있는 백엔드 산출물:
- 확인 상태:
- 이번 주 액션:
- 출처:
- 링크: [원문 보기](URL)

### 4. 공모전
- 이번 주 기준을 만족하는 공모전 후보가 없습니다.

### 5. 경진대회
- 이번 주 기준을 만족하는 경진대회 후보가 없습니다.

## 2. 마감 임박
- [D-3] 후보명 - 2026-06-01 KST - [원문 보기](URL)

## 3. 다음 주에도 추적할 후보
- 지난 후보를 오늘 다시 확인했고 아직 유효합니다: 후보명 - [원문 보기](URL)
```

후보가 없으면 각 유형에 아래 문장 중 해당 문장만 쓴다.

- 이번 주 기준을 만족하는 채용 후보가 없습니다.
- 이번 주 기준을 만족하는 인턴 후보가 없습니다.
- 이번 주 기준을 만족하는 해커톤 후보가 없습니다.
- 이번 주 기준을 만족하는 공모전 후보가 없습니다.
- 이번 주 기준을 만족하는 경진대회 후보가 없습니다.

마감 임박 후보가 없으면 `## 2. 마감 임박` 아래에 아래 문장만 쓴다.

- 이번 주 마감 임박 항목은 없습니다.

다음 주 추적 후보가 없으면 `## 3. 다음 주에도 추적할 후보` 아래에 아래 문장만 쓴다.

- 다음 주로 넘겨 추적할 후보는 없습니다.

## 선별 규칙

- Discord 본문에는 유형별 최고 후보 1개만 출력한다.
- 좋은 후보가 2개 이상이어도 나머지는 JSON artifact에만 둔다.
- 최종 추천은 실제 공고/활동 상세 URL만 허용한다.
- `source_kind`는 `official_company_career_detail`, `job_platform_detail`, `activity_platform_detail`, `government_program_detail` 중 하나여야 한다.
- `selection_tier`가 `backend_direct`, `backend_adjacent`, `portfolio_activity` 중 하나인 후보를 사용할 수 있다.
- `is_detail_url: true`, `is_news_article: false`, `is_active: true`, `exclude_reason` 없음인 후보만 추천한다.
- 현재 KST 날짜 기준으로 종료되지 않은 후보만 추천한다.
- 플랫폼 메인, 목록, 검색 URL은 본문에 넣지 않는다.
- `deadline_status`가 `closed`인 항목은 추천하지 않는다.
- 마감일이 원문에서 명확히 확인되고 `deadline_confidence: high`이면 `마감`을 출력한다.
- 마감일이 없으면 `마감` 필드를 생략한다.
- `deadline_status: rolling`이면 `마감: 상시채용`, `deadline_status: until_filled`이면 `마감: 채용 시 마감`을 출력할 수 있다.
- 마감 임박 섹션은 `deadline_confidence: high`이고 `days_until_deadline <= 7`인 후보만 표시한다.
- deadline unknown 후보는 마감 임박 섹션에 넣지 않는다.
- 다음 주 추적 섹션은 `freshness_tier: cached_revalidated`인 후보만 표시한다.
- 시니어/경력직 전용은 추천하지 않는다.
- 경력 3년 이상 또는 5년 이상 조건은 추천하지 않는다.
- 프론트엔드, 디자인, 마케팅, 영업, PM 단독 후보는 추천하지 않는다.
- 단순 교육 광고, 부트캠프 광고, 강의, 서포터즈는 추천하지 않는다.
- Naver News Search 후보, 뉴스 기사, 보도자료, 수상 기사, 개최 완료 기사, 결과 발표 기사, 후기/리뷰/종료 성격 후보는 추천하지 않는다.
- 과거 연도 행사와 마감 지난 후보는 추천하지 않는다.
- `source_kind: unknown`, `generic_listing`, `search_result`, `news_article`, `press_release`, `blog_post` 후보는 추천하지 않는다.
- 후보를 억지로 만들지 않는다.

## 필드 작성 규칙

- `유형`은 채용, 인턴, 해커톤, 공모전, 경진대회 중 하나로 정규화한다.
- `마감`, `회사/주최`, `전형/제출물`, `만들 수 있는 백엔드 산출물`은 확인된 경우에만 출력한다. 확인되지 않으면 필드 자체를 생략한다.
- `회사/주최`는 채용이면 실제 회사명, 활동이면 실제 주최기관 또는 운영기관을 쓴다.
- `company_or_host_confidence: high`일 때만 `회사/주최`를 출력한다.
- 원문에서 회사/주최를 확인할 수 없으면 필드를 생략한다.
- `회사/주최: NAVER`는 URL domain이 `recruit.navercorp.com`인 NAVER 공식 채용 공고일 때만 허용한다.
- `직무/역할`은 채용이면 실제 직무명, 활동이면 팀 안에서 백엔드로 맡을 수 있는 역할을 쓴다.
- `지원/참가 조건`은 실제 조건만 짧게 쓴다.
- `기술/산출물 키워드`는 Java, Kotlin, Spring Boot, REST API, DB, MySQL, PostgreSQL, Redis, Kafka, AWS, Docker, Kubernetes, AI API, LLM, Python 중 실제 관련 키워드만 쓴다.
- 기술/산출물 키워드가 원문에 없으면 과장하지 말고 `백엔드, API, DB` 정도로 제한한다.
- `전형/제출물`은 확인된 경우에만 출력한다. 채용이면 서류, 코딩테스트, 과제, 면접 등을 쓰고, 활동이면 기획서, GitHub, 발표자료, 결과물 URL, 모델/API 제출물 등을 쓴다.
- `확인 상태`는 아래 중 하나로만 쓴다.
- 이번 주 새로 발견한 상세 페이지 후보입니다.
- 지난 후보를 오늘 다시 확인했고 아직 유효합니다.
- 공식/플랫폼 상세 페이지에서 확인했습니다.
- `이번 주 액션`은 딱 하나의 행동만 쓴다.

## 출력 금지

최종 Markdown에는 내부 점수, 추천 사유 검토용 필드명, 제외 목록, diagnostics를 출력하지 않는다.

다음을 절대 출력하지 않는다.

- `Naver News Search`
- 뉴스 기사 또는 보도자료를 공고처럼 요약한 항목
- `pubDate` 또는 `published_at`을 마감일로 사용한 항목
- 현재 날짜에서 임의로 계산한 마감일
- 제목이나 원문에 없는 회사명
- 검색 출처를 회사/주최로 쓴 항목
- `회사/주최: NAVER`를 검색 출처 때문에 쓴 항목
- `마감: 원문 확인 필요`, `마감: 확인 필요`, `마감: 미정`, `마감: 알 수 없음`
- 오래된 뉴스 기사에서 활동을 현재 모집 중처럼 쓴 항목

Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다. 링크는 raw URL 단독 표기가 아니라 `[원문 보기](URL)` 형식으로만 쓴다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-backend-career-weekly.md`에 작성한다.
