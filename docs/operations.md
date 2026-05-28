# Career Feed 운영 가이드

## 운영 경로

| 경로 | 실행 | 산출물 |
| --- | --- | --- |
| Daily Backend Brief | 평일 08:47 KST | `reports/briefs/kr-tech-daily.md` |
| Weekly Backend Career Brief | 월요일 09:07 KST | `reports/briefs/kr-backend-career-weekly.md` |
| Mark PS Solved | 수동 실행 | `data/ps-progress.json` |

## Daily Backend Brief

- workflow: `.github/workflows/kr-tech-daily.yml`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-tech`
- prompt: `.github/codex/prompts/kr-tech-daily-brief.md`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-tech-daily.md --type daily-tech`
- Discord secret: `DISCORD_WEBHOOK_KR_TECH_DAILY`

## Weekly Backend Career Brief

- workflow: `.github/workflows/kr-backend-career-weekly.yml`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode weekly-career`
- prompt: `.github/codex/prompts/kr-backend-career-weekly.md`
- validator: `python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career`
- Discord secret: `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`

## Mark PS Solved

- workflow: `.github/workflows/mark-ps-solved.yml`
- 진행 파일: `data/ps-progress.json`
- 상태 확인: `python3 scripts/update-ps-progress.py --status`
- 풀이 기록: `python3 scripts/update-ps-progress.py --problem-id <problem_id> --note "<memo>"`

## 검증

```bash
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

`reports/` 아래 생성 산출물은 기본적으로 커밋하지 않습니다. Secret 값, API Key, Webhook URL은 코드와 문서 예시에 남기지 않습니다.
