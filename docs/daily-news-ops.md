# Korea Dev/AI News Daily

Korea Dev/AI News Daily는 평일 오전에 한국 개발/AI 뉴스를 정리해 별도 Discord Webhook으로 전송합니다.

## 실행 구성

| 항목 | 값 |
| --- | --- |
| workflow | `.github/workflows/kr-tech-news-daily.yml` |
| prompt | `.github/codex/prompts/kr-tech-news-daily.md` |
| collector | `python3 scripts/collect-kr-feeds.py --mode daily-news` |
| shortlist | `python3 scripts/build-daily-news-shortlist.py` |
| token budget | `python3 scripts/estimate-prompt-budget.py` |
| quality report | `python3 scripts/evaluate-news-daily-quality.py` |
| run summary | `python3 scripts/write-news-daily-run-summary.py` |
| validator | `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-news-daily.md --type daily-news` |
| report | `reports/briefs/kr-tech-news-daily.md` |
| Discord secret | `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` |
| delivery lock | `career-feed-news-sent-${KST_DATE}` |

## 후보 파일

- `reports/candidates/kr-dev-ai-news.json`
- `reports/candidates/kr-ai-tech-news.json`
- `reports/candidates/kr-tech-news-shortlist.json`

Codex 입력은 원본 후보 전체가 아니라 track별 compact shortlist인 `kr-tech-news-shortlist.json`을 중심으로 사용합니다.

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

- `reports/ops/news-daily-token-budget.json`: raw 후보 수, shortlist 수, prompt 문자 수, rough token 추정치
- `reports/ops/news-daily-quality-report.json`: 비중, 성장 행동, 투자 조언 위험, token 효율
- `reports/ops/news-daily-run-summary.json`: 선택 수, bridge 여부, 성장 판단, quality summary

`configs/audience-profile.json`의 `market_context`는 이전 호환용이며, 현재 기준은 `content_tracks.daily_ratio_policy`와 `content_tracks.investment`입니다.

## 로컬 확인

```bash
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/build-daily-news-shortlist.py
python3 scripts/estimate-prompt-budget.py
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
```

News Daily 성장 품질 점검 기준은 [Daily Growth Ops](./daily-growth-ops.md)에도 정리되어 있습니다.

