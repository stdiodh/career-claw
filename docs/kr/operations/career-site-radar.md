# Backend Career Site Radar

> Language: [한국어](./career-site-radar.md) | [English](../../en/operations/career-site-radar.md)

Backend Career Site Radar는 자동 추천 피드가 아니라, 수동 또는 주간 schedule로 실행하는 커리어 사이트 확인용 브리핑입니다.
이번 phase에서는 workflow 파일명과 canonical output path만 global-friendly이며, source preset은 `ko-KR` 중심으로 유지합니다.

## 실행 구성

| 항목 | 값 |
| --- | --- |
| workflow | `.github/workflows/backend-career-weekly.yml` |
| config | `configs/weekly-career-site-radar.json` |
| collector | `python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run` |
| renderer | `python3 scripts/render-weekly-career-site-radar.py` |
| validator | `python3 scripts/validate-career-feed-brief.py reports/briefs/ko-KR/backend-career-weekly.md --type weekly-career --locale ko-KR` |
| report | `reports/briefs/ko-KR/backend-career-weekly.md` |
| Discord secret | `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` |

## 출력 파일

- `reports/candidates/ko-KR/weekly-career-site-radar.json`
- `reports/briefs/ko-KR/backend-career-weekly.md`

호환용 JSON 파일:

- `reports/candidates/kr-backend-career-events.json`
- `reports/candidates/kr-backend-jobs.json`
- `reports/candidates/kr-backend-interns.json`
- `reports/candidates/kr-backend-hackathons.json`
- `reports/candidates/kr-backend-contests.json`
- `reports/candidates/kr-backend-competitions.json`

호환용 JSON 파일은 `items: []`와 `diagnostics.status: disabled`만 담습니다.

## Site Radar 정책

- 자동 추천이나 자동 파싱 결과를 제공하지 않습니다.
- Discord로 공식 채용 사이트, 채용·인턴 플랫폼, 대외활동/대회 플랫폼과 검색 키워드를 전송합니다.
- 마감일, 회사/주최, 직무/역할은 사용자가 원문에서 직접 판단합니다.
- 이 방식은 자동 파싱 오류와 hallucination을 피하기 위한 선택입니다.
- 본문은 정적 site radar config에서 생성하며 AI 생성 단계로 재작성하지 않습니다.
- 사이트는 중복 없이 출력하고, 같은 서비스의 여러 경로는 `links` 배열로 관리합니다.
- `data/weekly-career-candidate-cache.json`은 삭제되었고 workflow에서 업데이트하거나 commit하지 않습니다.

## 수동 실행 방법

1. `Actions > Backend Career Site Radar`를 엽니다.
2. `Run workflow`를 선택합니다.
3. `send_to_discord`를 `true`로 둡니다.
4. Discord에서 사이트와 검색 키워드를 확인합니다.

주간 schedule 시간은 GitHub Actions Variable `CAREER_FEED_CAREER_WEEKLY_DAY`와
`CAREER_FEED_CAREER_WEEKLY_TIME`으로 설정합니다.

Discord 전송은 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`일 때만 시도합니다.

## 로컬 확인

```bash
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/render-weekly-career-site-radar.py
python3 scripts/validate-career-feed-brief.py reports/briefs/ko-KR/backend-career-weekly.md --type weekly-career --locale ko-KR
```
