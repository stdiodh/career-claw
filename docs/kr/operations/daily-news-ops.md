# Dev News Daily

> Language: [한국어](./daily-news-ops.md) | [English](../../en/operations/daily-news-ops.md)

Dev News Daily는 평일 오전에 한국 개발/AI 뉴스를 정리해 별도 Discord Webhook으로 전송합니다.
이번 phase에서는 locale-aware foundation을 갖고 있으며, 이 문서는 `ko-KR` 기본 preset 기준 예시를 사용합니다.

## 실행 구성

| 항목 | 값 |
| --- | --- |
| workflow | `.github/workflows/dev-news-daily.yml` |
| prompt | `configs/locales/ko-KR/prompts/news-daily.md` |
| collector | `python3 scripts/collect-kr-feeds.py --mode daily-news` |
| shortlist | `python3 scripts/build-daily-news-shortlist.py` |
| token budget | `python3 scripts/estimate-prompt-budget.py` |
| quality report | `python3 scripts/evaluate-news-daily-quality.py` |
| run summary | `python3 scripts/write-news-daily-run-summary.py` |
| validator | `python3 scripts/validate-career-feed-brief.py reports/briefs/ko-KR/news-daily.md --type daily-news --locale ko-KR` |
| report | `reports/briefs/ko-KR/news-daily.md` |
| Discord secret | `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY` (`DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` fallback) |
| delivery lock | `career-feed-ko-KR-news-daily-sent-${LOCAL_DATE}` |

## 후보 파일

- `reports/candidates/ko-KR/dev-ai-news.json`
- `reports/candidates/ko-KR/backend-tech-news.json`
- `reports/candidates/ko-KR/news-shortlist.json`

Codex 입력은 원본 후보 전체가 아니라 track별 compact shortlist인 `news-shortlist.json`을 중심으로
사용합니다.

## 뉴스 정책

- 출력은 `새 기술 이야기`, `주식/투자 이야기`, `기술과 시장 연결`, `오늘의 성장 판단`으로 나눕니다.
- 기본 목표는 총 4개이며, 기술 3개와 투자 1개를 우선합니다.
- 허용 범위는 전체 3~5개, 기술 2~3개, 투자 0~2개입니다.
- 기준을 만족하는 뉴스가 1~2개뿐이면 후보 부족 문구와 함께 전송합니다.
- 기준을 만족하는 뉴스가 0개면 기준을 만족하는 한국 개발/AI 뉴스가 없다는 문구와 성장 판단만 전송합니다.
- 원문 링크가 있으면 원문을 우선 사용하고, Naver News 링크는 fallback으로만 사용합니다.
- 각 기술 항목은 개발자 실무 연결과 백엔드 주니어 학습 액션을 포함해야 합니다.
- Naver secret이 없거나 Naver API가 실패해도 RSS/공식 페이지 후보로 JSON을 생성합니다.

## 투자 섹션 주의사항

주식/투자 이야기는 매수/매도 추천이 아니라 기술 수요와 기업/산업 변화를 읽기 위한 관찰 섹션입니다.

관찰 대상:

- 실적
- CAPEX
- 데이터센터
- GPU/HBM
- 클라우드 투자
- AI 제품 매출
- API/플랫폼 매출

제외 대상:

- 추천주, 관련주/테마주 목록
- 수익 보장
- 명령형 투자 조언
- 급등락만 중심인 기사
- 단순 홍보성 기사

투자 후보 품질이 낮으면 투자 섹션은 생략합니다. 투자 후보가 매우 좋고 기술 후보도 충분할 때만 투자 2개까지 허용합니다.

## 운영 점검 파일

- `reports/ops/ko-KR/news-daily-token-budget.json`: raw 후보 수, shortlist 수, prompt 문자 수, rough
  token 추정치
- `reports/ops/ko-KR/news-daily-validation-report.md`: validator 상태, 오류 한 줄, stdout/stderr 마지막
  30줄
- `reports/ops/ko-KR/news-daily-quality-report.json`: 비중, 성장 행동, 투자 조언 위험, token 효율
- `reports/ops/ko-KR/news-daily-run-summary.json`: 선택 수, bridge 여부, 성장 판단, quality summary

`configs/audience-profile.json`의 `market_context`는 이전 호환용이며, 현재 기준은
`content_tracks.daily_ratio_policy`와 `content_tracks.investment`입니다.

## 수동 1회 실행

News Daily를 수동으로 다시 보낼 때는 먼저 검증 run과 전송 run을 분리합니다.

1. `Actions > Dev News Daily > Run workflow`를 엽니다.
2. `dry_run=true`, `force_send=false`로 실행해 후보 수집, shortlist 생성, Codex Markdown 생성,
   validator, artifact 업로드를 확인합니다.
3. artifact에서 `reports/ops/ko-KR/news-daily-validation-report.md`를 열어 validator가 통과했는지 확인합니다.
4. 실패하면 같은 artifact의 `reports/briefs/ko-KR/news-daily.md`,
   `reports/candidates/ko-KR/news-shortlist.json`,
   `reports/ops/ko-KR/news-daily-validation-report.md`를 함께 확인합니다.
5. validator 통과 후에만 `dry_run=false`, `force_send=true`로 한 번 전송합니다.

`dry_run=true`에서는 Discord 전송과 delivery lock 저장을 하지 않습니다. `force_send=true`는 오늘 delivery
lock이 있어도 생성, 검증, 전송을 수행하며, 전송 성공 시 delivery lock을 저장합니다.

schedule 실행은 runtime gate가 통과한 경우에만 생성과 전송 단계를 진행합니다.

`workflow_dispatch` 수동 실행은 runtime 시간 window 때문에 막히지 않습니다.

## 로컬 확인

```bash
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/build-daily-news-shortlist.py
python3 scripts/estimate-prompt-budget.py
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
```

News Daily 성장 품질 점검 기준은 [Daily Growth Ops](./daily-growth-ops.md)에도 정리되어 있습니다.
