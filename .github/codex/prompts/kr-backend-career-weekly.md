# Career Feed Backend Career Weekly Prompt

이 프롬프트는 KR Premium v2의 주간 백엔드 커리어 브리핑 전용이다.

중요:
- OpenAI API 비용이 발생할 수 있다.
- 후보 JSON과 사용자 프로필 JSON을 먼저 읽고, 후보에 없는 항목을 임의로 추가하지 않는다.
- Secret, API Key, Webhook URL은 절대 출력하지 않는다.
- 공고/대회 전문을 복사하거나 저장하지 않는다.
- 최종 Markdown은 반드시 `reports/briefs/kr-backend-career-weekly.md`에 직접 작성한다.

workflow는 `{{KST_NOW}}`를 현재 Asia/Seoul 기준시각으로 치환한다. 이 시각을 기준으로 마감 여부와 지원 가능성을 판단한다.

## 목표

4년제 대학교를 다니는 25살 Kotlin/Spring Boot 백엔드 지망생이 이번 주 확인할 만한 인턴, 신입/주니어 포지션, 해커톤, 공모전, 경진대회를 추천한다.

## 입력 파일

다음 파일을 읽고 선별 근거로 사용한다.

- `reports/candidates/kr-backend-career-events.json`
- `configs/audience-profile.json`

각 후보의 URL, source URL, published_at, query, reliability, tags, score, persona_fit_score, backend_fit_score, kotlin_spring_fit_score, student_fit_score, deadline_urgency_score, actionability_score, exclude_reason을 참고한다.

## 출력 파일

- `reports/briefs/kr-backend-career-weekly.md`

## 출력 구조

아래 Markdown 구조를 그대로 따른다.

```markdown
# Career Feed - Backend Career Weekly
기준시각: {{KST_NOW}}

이번 주 요약:
- 이번 주 지원/참가 관점에서 가장 중요한 판단 1문장

## 이번 주 추천 TOP 5

### 1. 제목
- 유형: 인턴/신입/해커톤/공모전/경진대회/교육
- 대상 적합성:
- 백엔드 적합성:
- Kotlin/Spring Boot 관련성:
- 마감:
- 왜 나에게 맞는가:
- 내 액션:
- 출처:
- 링크: [원문 보기](URL)

## 마감 임박
- 7일 이내 마감만 표시
- 없으면 "이번 주 마감 임박 항목 없음"

## 포트폴리오 관점 추천
- 포트폴리오에 남기기 좋은 항목 최대 3개

## 제외한 후보
- 최대 5개
- 제외 이유 포함
```

## 선별 규칙

- 이번 주 추천은 최대 5개만 포함한다.
- 마감 지난 항목은 추천하지 않는다.
- 시니어/경력직 전용은 추천하지 않는다.
- 백엔드 관련성이 낮으면 추천하지 않는다.
- 단순 교육 광고는 제외한다.
- 출처와 링크가 없으면 제외한다.
- 지원 가능성이 불명확하면 "확인 필요"라고 표시한다.
- 모든 추천은 25살 Kotlin/Spring Boot 백엔드 지망생 기준으로 쓴다.
- `exclude_reason`이 있으면 추천에서 제외하고, 필요하면 `제외한 후보`에 이유를 적는다.
- 링크는 raw URL 단독 표기가 아니라 `[원문 보기](URL)` 형식으로만 쓴다.
- Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다.

## 점수 해석 기준

- 백엔드/서버/API/Spring/Kotlin/Java 직접 관련 후보를 우선한다.
- 인턴/신입/주니어/대학생 지원 가능 후보를 우선한다.
- 마감일이 명확하고 아직 지나지 않은 후보를 우선한다.
- 포트폴리오에 쓸 수 있는 대회/해커톤을 우선한다.
- 공식 페이지 또는 채용 플랫폼 출처를 우선한다.
- 한국 지역 또는 한국어 공고를 우선한다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-backend-career-weekly.md`에 작성한다.
