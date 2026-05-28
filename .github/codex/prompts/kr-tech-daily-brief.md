# Career Feed Backend Daily Prompt

이 프롬프트는 KR Premium v2의 평일 Backend Daily Study Brief 전용이다.

중요:
- OpenAI API 비용이 발생할 수 있다.
- 후보 JSON과 사용자 프로필 JSON을 먼저 읽고, 후보에 없는 항목을 임의로 추가하지 않는다.
- Secret, API Key, Webhook URL은 절대 출력하지 않는다.
- 기사 전문을 복사하거나 저장하지 않는다.
- 문제 정답 코드나 풀이 코드는 제공하지 않는다.
- 최종 Markdown은 반드시 `reports/briefs/kr-tech-daily.md`에 직접 작성한다.

workflow는 `{{KST_NOW}}`를 현재 Asia/Seoul 기준시각으로 치환한다. 이 시각을 기준으로 학습 우선순위와 최신성을 판단한다.

## 목표

한국 기준으로 25살 Kotlin/Spring Boot 백엔드 지망생이 매일 아침 30~60분 동안 이어서 공부할 수 있는 Backend Daily Study Brief를 만든다.

뉴스 요약이 중심이 아니다. Spring Boot/JVM 학습, Programmers 주차별 PS 성장 루틴, Spring 오픈소스 첫 기여 후보, 한국 개발/AI 뉴스 1개를 학습 행동으로 연결하는 것이 목표다.

## 입력 파일

다음 파일을 읽고 선별 근거로 사용한다.

- `reports/candidates/spring-study-topic.json`
- `reports/candidates/ps-weekly-routine.json`
- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/candidates/kr-dev-ai-news.json`
- `configs/audience-profile.json`

Spring 학습 후보는 title, summary, url, source, published_at, query, tags, score, backend_fit_score, kotlin_spring_fit_score, exclude_reason을 참고한다.
PS 루틴 후보는 current_track, today_problem, advance_recommendation을 참고한다.
오픈소스 후보는 repository, issue_number, labels, updated_at, summary, contribution_type, difficulty_band, why_beginner_friendly, first_30_min_action, risk_reason, exclude_reason, score를 참고한다.
개발/AI 뉴스 후보는 title, summary, url, source, published_at, tags, score, exclude_reason을 참고한다.

## 출력 파일

- `reports/briefs/kr-tech-daily.md`

## 출력 구조

아래 Markdown 구조를 그대로 따른다.

```markdown
# Career Feed - Backend Daily
기준시각: {{KST_NOW}}

오늘의 방향:
- 오늘 공부하면 좋은 흐름 1문장

## 1. 오늘의 Spring Boot/JVM 학습
### 주제: ...
- 핵심 개념:
- 30분 실습:
- 검색 키워드:
- 확장해서 볼 것:
- 참고 링크: [원문 보기](URL)

## 2. 이번 주 PS 성장 루틴
- 이번 주 주제:
- 이번 주 목표:
- 현재 진행:
- 오늘 문제:
- 플랫폼: Programmers
- 난이도:
- 먼저 생각할 것:
- 오늘 목표:
- 막히면 검색:
- 링크: [문제 보기](URL)

## 3. 오픈소스 기여 후보
### 후보: ...
- 난이도 밴드: P5-like / P4-like
- 저장소:
- 기여 유형:
- 왜 시도해볼 만한가:
- 첫 30분 액션:
- 확인할 파일/키워드:
- 주의할 점:
- 링크: [Issue 보기](URL)

후보가 없으면 아래 문장만 쓴다.
- 오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다.

## 4. 한국 개발/AI 뉴스
### 뉴스: ...
- 제목:
- 핵심:
- 공부로 연결할 점:
- 검색 키워드:
- 링크: [원문 보기](URL)

## 오늘 할 일
1. ...
2. ...
3. 풀었다면 Mark PS Solved workflow로 기록한다.
```

## 선별 규칙

- PS는 반드시 Programmers 문제만 추천한다.
- BOJ, acmicpc, 백준 문제는 추천하지 않는다.
- PS는 매일 랜덤 문제가 아니라 `ps-weekly-routine.json`의 current_track을 따르는 주차별 성장 루틴이다.
- 같은 주차에서는 current_track을 유지한다.
- solved 상태와 advance_recommendation을 참고해 현재 진행과 오늘 목표를 쓴다.
- 문제 정답 코드, 정답 풀이, 완성 코드는 제공하지 않는다.
- 힌트는 `first_thought` 수준의 첫 사고 방향까지만 제공한다.
- 오늘 할 일에는 "풀었다면 Mark PS Solved workflow로 기록"을 짧게 포함한다.
- "왜 나에게 중요한가" 문구를 쓰지 않는다.
- "Kotlin/Spring Boot 관련성" 문구를 쓰지 않는다.
- "백엔드 관점" 문구를 쓰지 않는다.
- "긴급 체크" 문구를 쓰지 않는다.
- AI/보안 뉴스는 최대 1개만 포함한다.
- 보안/공급망 뉴스가 메인 주제로 반복되면 안 된다.
- 오픈소스 기여 후보는 최대 1개만 포함한다.
- 오픈소스 후보는 P5-like 또는 P4-like만 추천한다.
- too_hard, unclear, security vulnerability, CVE, release blocker, deep internals 후보는 제외한다.
- issue 내용을 과장하지 않는다.
- 첫 30분 액션은 읽기, 재현, 문서 확인, 로컬 빌드처럼 사용자가 직접 확인할 수 있는 행동으로 쓴다.
- 주가/투자만 있는 AI 뉴스는 제외한다.
- 일반 소비자 서비스 출시만 있는 뉴스는 제외한다.
- 링크 없는 항목은 제외한다.
- `exclude_reason`이 있으면 기본적으로 제외하고, 포함해야 한다면 이유를 명확히 판단한다.
- 모든 항목은 25살 Kotlin/Spring Boot 백엔드 지망생 관점에서 작성한다.
- Discord에서 읽기 쉽게 항목당 7줄 이내로 쓴다.
- Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다.
- 링크는 raw URL 단독 표기가 아니라 `[원문 보기](URL)`, `[문제 보기](URL)`, `[Issue 보기](URL)` 형식으로 쓴다.

## 섹션 작성 규칙

- 오늘의 Spring Boot/JVM 학습은 `spring-study-topic.json`에서 백엔드 학습으로 연결하기 쉬운 후보를 1개 고른다.
- 후보가 뉴스성 항목이어도 제목을 그대로 요약하지 말고 학습 주제로 바꿔 쓴다.
- 이번 주 PS 성장 루틴은 `ps-weekly-routine.json`의 current_track과 today_problem만 사용한다.
- 오픈소스 기여 후보가 없으면 지정된 없음 문장만 쓴다.
- 한국 개발/AI 뉴스는 최대 1개만 포함하고, 학습으로 연결할 수 없으면 생략 대신 "오늘은 학습으로 연결할 만한 개발/AI 뉴스가 없습니다."라고 쓴다.
- 오늘 할 일은 번호 목록 3개로 작성한다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-tech-daily.md`에 작성한다.
