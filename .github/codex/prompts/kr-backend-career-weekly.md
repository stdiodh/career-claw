# Career Feed Backend Career Weekly Prompt

이 프롬프트는 Career Feed의 주간 백엔드 커리어 사이트 레이더 전용이다.

중요:
- OpenAI API 비용이 발생할 수 있다.
- Secret, API Key, Webhook URL은 절대 출력하지 않는다.
- 실제 공고, 대회, 기사, 보도자료, 과거 게시물을 추천하지 않는다.
- 마감일, 회사/주최, 직무/역할, 주최기관, 지원 조건을 생성하지 않는다.
- 최종 Markdown은 반드시 `reports/briefs/kr-backend-career-weekly.md`에 직접 작성한다.

workflow는 `{{KST_NOW}}`를 현재 Asia/Seoul 기준시각으로 치환한다.

## 목표

자동 후보 추천 대신, 사용자가 이번 주 직접 확인할 백엔드 커리어 사이트를 5개 유형별로 정리한다.

## 입력 파일

다음 파일만 primary input으로 사용한다.

- `reports/candidates/weekly-career-site-radar.json`
- `configs/audience-profile.json`

호환용 후보 JSON 파일이 있더라도 본문 생성에는 사용하지 않는다.

## 출력 파일

- `reports/briefs/kr-backend-career-weekly.md`

## 출력 구조

아래 Markdown 구조를 그대로 따른다.

```markdown
# Career Feed - Backend Career Weekly
기준시각: {{KST_NOW}}

이번 주 방향:
- 자동 추천 대신, 직접 확인할 백엔드 커리어 사이트를 5개 유형별로 점검합니다.

## 1. 채용 확인
- NAVER Careers: Tech > Backend, New hire, Intern 필터를 확인합니다. [사이트 보기](https://recruit.navercorp.com/rcrt/list.do)
- 이번 주 확인 기준: 신입, 주니어, 인턴, 채용연계형, Java/Kotlin/Spring/API/DB 키워드만 우선 봅니다.

## 2. 인턴 확인
- Linkareer 인턴: 채용연계형/체험형 인턴 중 IT, 서버, 백엔드, 데이터, 시스템개발 키워드를 확인합니다. [사이트 보기](https://linkareer.com/list/intern?filterBy_activityTypeID=5&filterBy_jobTypes=INTERN&filterBy_status=OPEN&orderBy_direction=DESC&orderBy_field=RECENT&page=1)
- 이번 주 확인 기준: 마케팅/디자인/영업 단독 인턴은 제외하고, 개발 산출물이 남는 인턴만 봅니다.

## 3. 해커톤 확인
- Linkareer 대외활동: 해커톤, 개발, AI 서비스, API 키워드로 확인합니다. [사이트 보기](https://linkareer.com/list/activity)
- 이번 주 확인 기준: API 서버, DB, 인증, GitHub, 배포 URL을 결과물로 남길 수 있는 활동만 봅니다.

## 4. 공모전 확인
- Linkareer 공모전: SW, AI, 데이터, 서비스 개발 공모전을 확인합니다. [사이트 보기](https://linkareer.com/list/contest)
- 이번 주 확인 기준: 단순 아이디어, 마케팅, 콘텐츠 제작 공모전은 제외합니다.

## 5. 경진대회 확인
- DACON: 접수 중 또는 진행 중인 AI/데이터 경진대회를 직접 확인합니다. [사이트 보기](https://dacon.io/competitions)
- 이번 주 확인 기준: 이미 종료된 대회는 제외하고, 백엔드 포트폴리오로 연결할 수 있는 데이터 수집/API/대시보드 아이디어가 있는지 봅니다.

## 이번 주 30분 액션
- 공식 채용 2곳, 인턴 사이트 2곳, 대외활동/대회 사이트 2곳만 열어보고 지원/참가 가능성이 있는 링크를 직접 북마크합니다.
```

## 작성 규칙

- `weekly-career-site-radar.json`의 `sections`와 `sites`만 사용한다.
- JSON에 없는 section, site, URL을 추가하지 않는다.
- 각 site는 `name`, `how_to_check`, `url`을 사용해 한 줄로 쓴다.
- 링크는 반드시 `[사이트 보기](URL)` 형식으로 쓴다.
- 각 section 끝에는 `check_rule`을 `이번 주 확인 기준` 한 줄로 쓴다.
- `keywords`, `exclude_keywords`, `backend_portfolio_angle`은 site 설명을 짧게 다듬는 데만 참고하고, 실제 후보처럼 쓰지 않는다.
- 사이트 레이더이므로 항상 동일한 5개 section을 출력한다.

## 출력 금지

다음을 절대 출력하지 않는다.

- 후보 제목
- 마감일
- 회사/주최
- 직무/역할
- 주최기관
- 지원/참가 조건
- 실제 공고나 대회 추천 문장
- 후보 없음 문장
- 이번 주 기준을 만족하는 후보가 없다는 문장
- `Naver News Search`
- 뉴스 기사, 보도자료, 수상 기사, 개최 완료 기사, 결과 발표 기사, 후기/리뷰/종료 성격 후보
- `원문 확인 필요`, `확인 필요`, `미정`, `알 수 없음`

Markdown 표, 코드블록, 긴 인용문은 사용하지 않는다. raw URL 단독 표기도 쓰지 않는다.

## 최종 지시

최종 응답 요약이 아니라 실제 브리핑 Markdown을 `reports/briefs/kr-backend-career-weekly.md`에 작성한다.
