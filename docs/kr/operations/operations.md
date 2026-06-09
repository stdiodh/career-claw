# Career Feed 운영 가이드

> Language: [한국어](./operations.md) | [English](../../en/operations/operations.md)

레거시 파일 제거 기준은 [LEGACY.md](../../../LEGACY.md)를 따른다.

## 운영 경로

| 경로 | 실행 | 산출물 |
| --- | --- | --- |
| Daily Backend Brief | locale-aware daily workflow, `CAREER_FEED_BACKEND_DAILY_TIME` 기준 평일 runtime gate 실행 | `reports/briefs/{locale}/backend-daily.md` |
| Dev News Daily | locale-aware foundation, `CAREER_FEED_NEWS_DAILY_TIME` 기준 평일 runtime gate 실행 | `reports/briefs/{locale}/news-daily.md` |
| Backend Career Site Radar | 이번 phase에서는 `ko-KR` 중심, 주간 runtime gate 실행 또는 수동 실행 | `reports/briefs/ko-KR/backend-career-weekly.md` |
| Mark PS Solved | 수동 실행 | `data/ps-progress.json` |

## 상세 운영 문서

- [Daily Backend Brief](./daily-backend-brief.md)
- [Dev News Daily](./daily-news-ops.md)
- [Backend Career Site Radar](./career-site-radar.md)
- [로컬 검증 가이드](./local-validation.md)
- [Daily Growth Ops](./daily-growth-ops.md)

## Daily 운영 안정성

- Backend Daily와 News Daily의 `workflow_dispatch` 입력은 `dry_run`, `force_send`를 사용합니다.
- `dry_run=true`이면 Discord 전송과 delivery lock 저장을 하지 않습니다.
- `force_send=true`이면 같은 날짜 delivery lock이 있어도 전송합니다.
- Discord 전송 성공 후에만 GitHub Actions cache에 delivery lock marker를 저장합니다.
- 같은 날짜 lock이 있고 `force_send=false`이면 Discord 전송을 skip합니다.
- Discord 429/5xx는 `scripts/send-discord.py`에서 재시도합니다.
- 실패 알림 선택 secret은 `DISCORD_WEBHOOK_CAREER_FEED_OPS`입니다. 없으면 실패 알림만 skip합니다.
- GitHub Actions scheduled workflow는 부하에 따라 지연되거나 실행이 누락될 수 있으므로 30분 runtime gate window와
  delivery lock으로 보완합니다.

## Actions 체크리스트

fork를 처음 설정하는 사용자는 이미지가 포함된 [Fork Setup Guide](../getting-started/fork-setup.md)를 먼저 따라갑니다.

1. `Settings > Secrets and variables > Actions`에 필요한 secrets를 등록합니다.
2. `Settings > Actions > General`에서 Actions 실행이 허용되어 있는지 확인합니다.
3. Actions 탭에서 4개 운영 경로가 enabled 상태인지 확인합니다.
4. Backend Daily와 News Daily를 먼저 `dry_run=true`, `force_send=false`로 실행해 artifact와
   validator를 확인합니다.
5. 실제 전송 검증 전에 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`를 설정합니다.
6. 실제 전송 검증은 `dry_run=false`, `force_send=true`로 실행합니다.
7. 같은 날 다시 `dry_run=false`, `force_send=false`로 실행해 delivery lock skip을 확인합니다.
8. 이후 Daily workflow는 설정한 timezone과 target time 기준으로 실행됩니다.

GitHub Actions scheduled workflow는 default branch의 최신 workflow 파일을 기준으로 실행됩니다. Public
repository는 장기간 활동이 없으면 scheduled workflow가 자동 비활성화될 수 있으므로 Actions 탭에서 workflow 상태를
확인합니다.

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

전체 검증 명령은 [로컬 검증 가이드](./local-validation.md)를 따릅니다.

```bash
python3 scripts/check-workflow-schedules.py
./scripts/validate.sh
git diff --check
```

`reports/` 아래 생성 산출물은 기본적으로 커밋하지 않습니다. Secret 값, API Key, Webhook URL은 코드와 문서 예시에 남기지
않습니다.
