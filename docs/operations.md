# Career Feed 운영 가이드

레거시 파일 제거 기준은 [LEGACY.md](../LEGACY.md)를 따른다.

## 운영 경로

| 경로 | 실행 | 산출물 |
| --- | --- | --- |
| Daily Backend Brief | 평일 08:05 KST 시작, 09:00 KST 전송. 09:25 KST catch-up 실행 | `reports/briefs/kr-tech-daily.md` |
| Korea Dev/AI News Daily | 평일 08:15 KST 시작, 09:05 KST 전송. 09:30 KST catch-up 실행 | `reports/briefs/kr-tech-news-daily.md` |
| Backend Career Site Radar | 수동 실행 | `reports/briefs/kr-backend-career-weekly.md` |
| Mark PS Solved | 수동 실행 | `data/ps-progress.json` |

## Daily Backend Brief

- workflow: `.github/workflows/kr-tech-daily.yml`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-backend`
- prompt: `.github/codex/prompts/kr-tech-daily-brief.md`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-daily.md --type daily-tech --candidates-dir reports/candidates`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_DAILY`
- delivery lock: `career-feed-backend-sent-${KST_DATE}`
- 운영 요약: `reports/ops/backend-daily-run-summary.json`, `reports/ops/backend-daily-run-summary.md`

OSS 후보는 `configs/oss-repositories.json`의 저장소별 priority, ecosystem tag, beginner label, avoid label/title keyword, 선호 기여 유형, 로컬 확인 힌트를 scoring과 후보 evidence에 반영합니다. 저장소 profile 관리 기준은 `docs/oss-candidate-policy.md`를 따릅니다.
Daily Growth 운영 요약과 artifact 해석 방법은 `docs/daily-growth-ops.md`를 따릅니다.

## Korea Dev/AI News Daily

- workflow: `.github/workflows/kr-tech-news-daily.yml`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-news`
- shortlist 생성: `python3 scripts/build-daily-news-shortlist.py`
- prompt budget 기록: `python3 scripts/estimate-prompt-budget.py`
- quality report 기록: `python3 scripts/evaluate-news-daily-quality.py`
- run summary 기록: `python3 scripts/write-news-daily-run-summary.py`
- prompt: `.github/codex/prompts/kr-tech-news-daily.md`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-news-daily.md --type daily-news`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY`
- delivery lock: `career-feed-news-sent-${KST_DATE}`
- 운영 요약: `reports/ops/news-daily-run-summary.json`, `reports/ops/news-daily-run-summary.md`

News Daily는 기본 목표를 기술 3개 + 투자 1개, 총 4개로 둡니다. 허용 범위는 전체 3~5개, 기술 2~3개, 투자 0~2개입니다. 기준을 만족하는 뉴스가 1~2개뿐이면 후보 부족 문구와 함께 정상 성공으로 보고, 0개면 기준을 만족하는 한국 개발/AI 뉴스가 없다는 문구와 성장 판단만 전송합니다. 출력은 `새 기술 이야기`, `주식/투자 이야기`, `기술과 시장 연결`, `오늘의 성장 판단`으로 분리합니다. Codex 입력은 원본 후보 전체가 아니라 track별 compact shortlist를 중심으로 사용하고, `reports/ops/news-daily-token-budget.json`에 raw 후보 수, tech/investment shortlist 수, rough token 추정치를 기록합니다. `reports/ops/news-daily-quality-report.json`은 비중, 성장 행동, 투자 조언 위험, 가격 움직임 중심 위험, token 효율을 운영 관찰용으로 기록합니다.

주식/투자 이야기는 매수/매도 추천이 아니라 기술 수요와 기업/산업 변화를 읽는 관찰 섹션입니다. 실적, CAPEX, 데이터센터, GPU/HBM, 클라우드, AI 제품 매출, API/플랫폼 매출을 봅니다. 투자 후보 품질이 낮으면 투자 섹션은 생략하고, 투자 후보가 매우 좋고 기술 후보도 충분할 때만 투자 2개까지 허용합니다. 추천주, 관련주/테마주 목록, 수익 보장, 명령형 투자 조언, 급등락만 중심인 기사는 제외합니다. `configs/audience-profile.json`의 `market_context`는 이전 호환용이며, 현재 기준은 `content_tracks.daily_ratio_policy`와 `content_tracks.investment`입니다. Naver secret 누락이나 Naver API 실패는 warning/source error로 기록하고 RSS/공식 페이지 후보만으로도 JSON을 생성합니다.

## Daily 운영 안정성

- `workflow_dispatch` 입력은 Backend Daily와 News Daily 모두 `dry_run`, `force_send`를 사용합니다.
- `dry_run=true`이면 Discord 전송과 delivery lock 저장을 하지 않습니다.
- `force_send=true`이면 같은 날짜 delivery lock이 있어도 전송합니다.
- Discord 전송 성공 후에만 GitHub Actions cache에 delivery lock marker를 저장합니다.
- 같은 날짜 lock이 있고 `force_send=false`이면 Discord 전송을 skip합니다.
- Discord 429/5xx는 `scripts/send-discord.py`에서 재시도합니다.
- 실패 알림 선택 secret은 `DISCORD_WEBHOOK_CAREER_FEED_OPS`입니다. 없으면 실패 알림만 skip합니다.
- GitHub Actions scheduled workflow는 부하에 따라 지연되거나 실행이 누락될 수 있으므로 catch-up schedule과 delivery lock으로 보완합니다.

## Backend Career Site Radar

- workflow: `.github/workflows/kr-backend-career-weekly.yml`
- site radar JSON 생성: `python3 scripts/collect-kr-feeds.py --mode weekly-career`
- Markdown 생성: `python3 scripts/render-weekly-career-site-radar.py`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career`
- Discord secret: `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

## Mark PS Solved

- workflow: `.github/workflows/mark-ps-solved.yml`
- 진행 파일: `data/ps-progress.json`
- 상태 확인: `python3 scripts/update-ps-progress.py --status`
- 풀이 기록: `python3 scripts/update-ps-progress.py --problem-id <problem_id> --note "<memo>"`

## OSS Progress Notes

- 진행 파일: `data/oss-progress.json`
- 상태 확인: `python3 scripts/update-oss-progress.py --status`
- 검토 기록: `python3 scripts/update-oss-progress.py --mark-reviewed <GitHub issue URL> --note "<memo>"`
- GitHub issue 댓글, assign, label 변경은 하지 않습니다.

## 검증

```bash
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/build-daily-news-shortlist.py
python3 scripts/estimate-prompt-budget.py
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/render-weekly-career-site-radar.py
python3 scripts/update-oss-progress.py --status
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-sparse.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-empty.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-tech-investment.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-tech-only.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

`reports/` 아래 생성 산출물은 기본적으로 커밋하지 않습니다. Secret 값, API Key, Webhook URL은 코드와 문서 예시에 남기지 않습니다.
