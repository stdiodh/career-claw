# Career Feed Backend Daily Prompt

이 프롬프트는 Career Feed의 평일 Backend Daily Study Brief 전용이다.

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

뉴스 요약이 중심이 아니다. Spring Boot/JVM 학습, Programmers 주차별 PS 성장 루틴, Spring 오픈소스 첫 기여 후보, 한국 최신 개발/AI 뉴스, 주니어 백엔드 실무지식 1개를 짧고 실천 가능한 학습 흐름으로 연결하는 것이 목표다.

## 입력 파일

다음 파일을 읽고 선별 근거로 사용한다.

- `reports/candidates/spring-study-topic.json`
- `reports/candidates/ps-weekly-routine.json`
- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/candidates/kr-dev-ai-news.json`
- `reports/candidates/kr-ai-tech-news.json`
- `reports/candidates/backend-practical-knowledge.json`
- `configs/audience-profile.json`

입력 파일 사용 범위:

- Spring 학습 후보는 1번 섹션에만 사용한다.
- PS 루틴 후보는 2번 섹션에만 사용한다.
- OSS 후보는 3번 섹션에만 사용한다.
- `kr-dev-ai-news.json` 또는 `kr-ai-tech-news.json`은 4번 뉴스 섹션에만 사용한다.
- `backend-practical-knowledge.json`은 5번 실무지식 섹션에만 사용한다.

Spring 학습 후보는 title, summary, url, source, published_at, query, tags, score, backend_fit_score, kotlin_spring_fit_score, exclude_reason을 참고한다.
PS 루틴 후보는 current_track, today_problem, advance_recommendation을 참고한다.
오픈소스 후보는 `items` 배열의 repository, issue_number, state, author, author_association, maintainer_authored, assignees, has_assignee, linked_prs_count, linked_branches_count, linked_work_check, has_linked_work, comments_checked_count, has_claim_comment, safe_to_recommend, labels, updated_at, summary, contribution_type, difficulty_band, why_beginner_friendly, first_30_min_action, pre_contribution_etiquette, status_check, risk_reason, exclude_reason, score를 참고한다.
개발/AI 뉴스 후보는 title, summary, url, source, publisher, published_at, tags, score, exclude_reason을 참고한다.
실무지식 후보는 today.title, today.summary, today.core_concept, today.practice_30m, today.check_question, today.search_keywords를 참고한다.

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
- 완료 기준:
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
- 풀이 후 점검:
- 막히면 검색:
- 링크: [문제 보기](URL)

## 3. 오픈소스 기여 후보
### 후보: ...
- 상태 확인:
- 난이도 밴드: P5-like / P4-like
- 저장소:
- 기여 유형:
- 왜 시도해볼 만한가:
- 첫 30분 액션:
- 기여 전 매너:
- 확인할 파일/키워드:
- 주의할 점:
- 링크: [Issue 보기](URL)

후보가 없으면 아래 문장만 쓴다.
- 오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다.

## 4. 한국 최신 개발/AI 뉴스
### 뉴스: ...
- 제목:
- 출처/게시:
- 핵심:
- 실무 연결:
- 검색 키워드:
- 링크: [원문 보기](URL)

뉴스가 없으면 아래 문장만 쓴다.
- 오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다.

## 5. 주니어 백엔드 실무지식
### 주제: ...
- 큰 흐름:
- 핵심 개념:
- 30분 실습:
- 현업 체크 질문:
- 검색 키워드:
```

## 선별 규칙

- Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다.
- Discord에서 읽기 쉽게 각 섹션은 짧고 실천 가능하게 쓴다.
- "왜 나에게 중요한가" 문구를 쓰지 않는다.
- 내부 추천 점수나 적합도 필드명을 출력하지 않는다.
- "백엔드 관점" 문구를 쓰지 않는다.
- "긴급 체크" 문구를 쓰지 않는다.
- Secret 값이나 Webhook URL을 출력하지 않는다.
- 링크는 raw URL 단독 표기가 아니라 `[원문 보기](URL)`, `[문제 보기](URL)`, `[Issue 보기](URL)` 형식으로 쓴다.

## 1번 Spring Boot/JVM 학습 규칙

- 반드시 `spring-study-topic.json`에서 후보 1개를 고른다.
- 후보에 없는 Spring 주제를 임의 생성하지 않는다.
- 공식 문서나 reference page는 참고 링크로 사용할 수 있다.
- 공식 문서나 reference page를 4번 뉴스로 재사용하지 않는다.
- 후보가 뉴스성 제목이어도 학습 주제로 바꿔 쓴다.
- "읽어본다"보다 "확인한다", "테스트한다", "재현한다"처럼 끝나는 행동을 쓴다.
- `완료 기준`은 30분 안에 끝났는지 확인 가능한 문장으로 쓴다.
- 1번 섹션에는 `검색 키워드:` 필드를 쓰지 않는다.
- Spring 학습 섹션을 뉴스처럼 쓰지 않는다.

## 2번 PS 성장 루틴 규칙

- PS는 반드시 `ps-weekly-routine.json`의 current_track, today_problem, advance_recommendation을 따른다.
- Programmers 문제만 추천한다.
- BOJ, acmicpc, 백준 문제는 추천하지 않는다.
- 매일 랜덤 문제가 아니라 현재 track 기준으로 이어지는 루틴이어야 한다.
- 같은 주차에서는 current_track을 유지한다.
- 문제 정답 코드, 완성 풀이, 정답 설명은 제공하지 않는다.
- 힌트는 `first_thought` 수준의 첫 사고 방향까지만 제공한다.
- `풀이 후 점검`은 풀이가 끝난 뒤 남길 학습 포인트를 1문장으로 쓴다.
- 2번 섹션에는 `오늘 목표:` 필드를 쓰지 않는다.

## 3번 오픈소스 기여 후보 규칙

- `kr-oss-contribution-opportunities.json`에서 최대 1개만 고른다.
- `kr-oss-contribution-opportunities.json`의 `items` 중 `safe_to_recommend: true`인 후보만 사용한다.
- `safe_to_recommend`가 없거나 false이면 사용하지 않는다.
- `linked_work_check`가 `verified`가 아니면 사용하지 않는다.
- `has_assignee`, `has_linked_work`, `has_claim_comment`가 하나라도 true이면 사용하지 않는다.
- 후보가 없으면 지정된 없음 문장만 쓴다.
- 오픈소스 후보는 P5-like 또는 P4-like만 추천한다.
- maintainer/member/collaborator가 열었거나 maintainer가 초보자용으로 triage한 open issue만 추천한다.
- assignee가 있거나 linked PR/branch가 있거나 댓글에서 누군가 작업 의사를 밝힌 이슈는 추천하지 않는다.
- too_hard, unclear, security vulnerability, CVE, release blocker, breaking change, major API, deep internals 후보는 제외한다.
- API 변경이 필요한 이슈는 첫 기여 후보로 넓히지 않고, docs/test/repro 중심 후보만 다룬다.
- issue 내용을 과장하지 않는다.
- `상태 확인`은 candidate JSON의 `status_check`를 우선 사용한다.
- `기여 전 매너`는 candidate JSON의 `pre_contribution_etiquette`를 우선 사용한다.
- `상태 확인`에는 maintainer 작성 여부, 담당자 없음, 연결 PR/branch 없음, claim 댓글 없음 중 후보 JSON에서 확인된 사실만 쓴다.
- 첫 30분 액션은 CONTRIBUTING.md 확인, 로컬 빌드 실행, 실패 재현, 관련 파일 1~2개 읽기, 문서/테스트 위치 확인, issue 재현 조건 정리처럼 실제 확인 행동이어야 한다.
- `기여 전 매너`에는 issue에 짧게 확인 댓글을 남긴 뒤 작은 범위로 진행하도록 쓴다.
- Spring Data 문서 기여라면 `src/docs/asciidoc`, `mvn package -Pdistribute`, DCO Signed-off-by, issue reference 확인을 반영한다.
- "코드를 수정한다", "PR을 만든다", "구현부터 시작한다", "전체 구조를 파악한다"처럼 범위가 크거나 결과부터 요구하는 행동은 쓰지 않는다.

## 4번 한국 최신 개발/AI 뉴스 규칙

- 4번 뉴스는 `kr-dev-ai-news.json` 또는 `kr-ai-tech-news.json`의 실제 후보 item에서만 고른다.
- `spring-study-topic.json`, `kr-backend-tech-news.json`, Spring/JVM 학습 후보, 공식 reference page를 뉴스로 재사용하지 않는다.
- 후보에 없는 뉴스를 임의로 만들지 않는다.
- 기사 제목은 후보의 title을 왜곡하지 않는다.
- `핵심`과 `실무 연결`만 짧게 재작성한다.
- `공부로 연결할 점`이라는 필드는 쓰지 않고 반드시 `실무 연결`을 쓴다.
- 링크는 반드시 해당 뉴스/게시글 원문 URL이어야 한다.
- 학습 문서 URL, 공식 reference URL, GitHub issue URL, 문제 링크를 뉴스 링크로 넣지 않는다.
- `exclude_reason`이 있으면 제외한다.
- `published_at`이 있으면 기준시각 기준 최근 7일 이내 후보를 우선한다.
- 최근 7일 후보가 없고 품질 좋은 후보가 있으면 최대 14일 이내까지만 허용한다.
- 한국 기업, 한국 기관, 한국 언론, 국내 테크블로그와 직접 관련된 글을 우선한다.
- 단순 투자/주가/관련주/홍보성 제품 출시/소비자 서비스 출시만 다루는 뉴스는 제외한다.
- 개발자 실무, AI API, 인프라, 플랫폼, 백엔드 운영, 클라우드, 데이터, 보안, 생산성, 개발 조직 관점으로 연결 가능한 글을 우선한다.
- 후보가 부족하면 Spring Boot 문서나 외부 공식 문서를 대체 뉴스로 만들지 말고, 지정된 없음 문장만 쓴다.

뉴스 링크 금지 도메인/유형:

- `docs.spring.io`
- `spring.io`
- `github.com`
- `kotlinlang.org`
- `docs.oracle.com`
- `programmers.co.kr`
- `school.programmers.co.kr`
- API reference
- 공식 문서
- 문제 링크
- GitHub issue 링크
- 일반 튜토리얼 문서
- Spring Boot reference page
- Spring Framework reference page

## 5번 주니어 백엔드 실무지식 규칙

- `backend-practical-knowledge.json`의 `today`만 사용한다.
- 임의로 다른 주제를 만들지 않는다.
- `### 주제:`에는 `title`만 쓴다.
- 책 목차처럼 보이는 장, 부록, 챕터 표현을 붙이지 않는다.
- `큰 흐름`은 `summary` 기반으로 쓴다.
- `핵심 개념`은 `core_concept` 기반으로 쓴다.
- `30분 실습`은 `practice_30m` 기반으로 쓴다.
- `현업 체크 질문`은 `check_question` 기반으로 쓴다.
- `검색 키워드`는 `search_keywords` 배열을 쉼표로 연결한다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-tech-daily.md`에 작성한다.
