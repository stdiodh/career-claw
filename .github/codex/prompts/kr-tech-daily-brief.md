# Career Feed Korea Tech Daily Prompt

이 프롬프트는 KR Premium v2의 평일 기술 브리핑 전용이다.

중요:
- OpenAI API 비용이 발생할 수 있다.
- 후보 JSON과 사용자 프로필 JSON을 먼저 읽고, 후보에 없는 항목을 임의로 추가하지 않는다.
- Secret, API Key, Webhook URL은 절대 출력하지 않는다.
- 기사 전문을 복사하거나 저장하지 않는다.
- 최종 Markdown은 반드시 `reports/briefs/kr-tech-daily.md`에 직접 작성한다.

workflow는 `{{KST_NOW}}`를 현재 Asia/Seoul 기준시각으로 치환한다. 이 시각을 기준으로 최신성과 긴급성을 판단한다.

## 목표

한국 기준으로 25살 Kotlin/Spring Boot 백엔드 지망생이 매일 아침 볼 만한 AI 테크 뉴스와 백엔드 기술 뉴스를 선별한다.

## 입력 파일

다음 파일을 읽고 선별 근거로 사용한다.

- `reports/candidates/kr-ai-tech-news.json`
- `reports/candidates/kr-backend-tech-news.json`
- `configs/audience-profile.json`

각 후보의 URL, source URL, published_at, query, relevance, reliability, tags, score, persona_fit_score, backend_fit_score, kotlin_spring_fit_score, security_action_required, exclude_reason을 참고한다.

## 출력 파일

- `reports/briefs/kr-tech-daily.md`

## 출력 구조

아래 Markdown 구조를 그대로 따른다.

```markdown
# Career Feed - Korea Tech Daily
기준시각: {{KST_NOW}}

한 줄 요약:
- 오늘 백엔드 지망생이 먼저 볼 만한 흐름 1문장

## 1. 한국 AI 테크

### 1-1. 제목
- 무슨 일:
- 왜 나에게 중요한가:
- 백엔드 관점:
- 내 액션:
- 출처/시각:
- 링크: [원문 보기](URL)

## 2. 백엔드/개발자 기술

### 2-1. 제목
- 무슨 일:
- 왜 나에게 중요한가:
- Kotlin/Spring Boot 관련성:
- 내 액션:
- 출처/시각:
- 링크: [원문 보기](URL)

## 긴급 체크
- 백엔드 개발자가 바로 확인해야 하는 보안/장애/패치 이슈가 있을 때만 최대 1개
- 없으면 "오늘은 긴급 체크 항목 없음"

## 오늘 할 일
- 최대 3개
```

## 선별 규칙

- 한국 AI 테크는 최대 2개만 포함한다.
- 백엔드/개발자 기술은 최대 3개만 포함한다.
- 긴급 체크는 `security_action_required=true`이거나 백엔드 개발자가 바로 패치/확인해야 하는 경우만 최대 1개 포함한다.
- 주가/투자만 있는 AI 뉴스는 제외한다.
- 일반 소비자 서비스 출시만 있는 뉴스는 제외한다.
- 백엔드 개발자에게 직접 영향이 없으면 제외한다.
- 링크 없는 항목은 제외한다.
- `exclude_reason`이 있으면 기본적으로 제외하고, 포함해야 한다면 이유를 명확히 판단한다.
- "왜 봐야 함" 같은 일반 문구를 반복하지 않는다.
- 모든 항목은 25살 Kotlin/Spring Boot 백엔드 지망생 관점에서 작성한다.
- Discord에서 읽기 쉽게 항목당 6줄 이내로 쓴다.
- Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다.
- 링크는 raw URL 단독 표기가 아니라 `[원문 보기](URL)` 형식으로만 쓴다.

## 오늘 할 일 작성 규칙

- 원문 읽기, 기술 키워드 정리, 포트폴리오 아이디어 기록처럼 행동 중심으로 쓴다.
- 최대 3개만 작성한다.
- 지원/채용/공모전 같은 커리어 이벤트는 이 daily 기술 브리핑에 길게 넣지 않는다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-tech-daily.md`에 작성한다.
