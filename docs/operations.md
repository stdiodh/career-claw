# Career Feed 운영 가이드

## 운영 경로

| 경로 | 실행 | 산출물 |
| --- | --- | --- |
| Daily Backend Brief | 평일 08:05 KST 시작, 09:00 KST 전송 | `reports/briefs/kr-tech-daily.md` |
| Korea Dev/AI News Daily | 평일 08:15 KST 시작, 09:05 KST 전송 | `reports/briefs/kr-tech-news-daily.md` |
| Backend Career Site Radar | 수동 실행 | `reports/briefs/kr-backend-career-weekly.md` |
| Mark PS Solved | 수동 실행 | `data/ps-progress.json` |

## Daily Backend Brief

- workflow: `.github/workflows/kr-tech-daily.yml`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-backend`
- prompt: `.github/codex/prompts/kr-tech-daily-brief.md`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-daily.md --type daily-tech`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_DAILY`

## Korea Dev/AI News Daily

- workflow: `.github/workflows/kr-tech-news-daily.yml`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-news`
- prompt: `.github/codex/prompts/kr-tech-news-daily.md`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-news-daily.md --type daily-news`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY`

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

## 검증

```bash
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/render-weekly-career-site-radar.py
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

`reports/` 아래 생성 산출물은 기본적으로 커밋하지 않습니다. Secret 값, API Key, Webhook URL은 코드와 문서 예시에 남기지 않습니다.
