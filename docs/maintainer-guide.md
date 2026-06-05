# Maintainer Guide

## Daily workflow dry-run checklist

- `dry_run=true`, `force_send=false`로 먼저 실행합니다.
- 생성된 briefing artifact와 validation report를 확인합니다.
- Discord 전송 전 delivery lock과 skip reason artifact를 확인합니다.

## Validation-before-send checklist

- `python3 scripts/check-workflow-schedules.py`
- `python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run`
- `python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run`
- `python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run`
- `./scripts/validate.sh`

## Secrets safety checklist

- `OPENAI_API_KEY`, Discord Webhook URL, GitHub token, Naver credentials를 문서나 commit에 남기지 않습니다.
- sample command에는 secret 값을 직접 쓰지 않습니다.
- 공개 이슈에 secret 원문을 요청하지 않습니다.

## What not to automate

- 외부 저장소 자동 댓글
- 외부 저장소 자동 PR
- 자동 assign 또는 label 변경
- maintainer 검토 없는 공식 답변
- maintainer 검토 없는 Discord 전송

## How to review issue suggestions

- 출처 URL이 공개적으로 확인 가능한지 확인합니다.
- 백엔드 지망생 또는 주니어 개발자에게 실제 도움이 되는지 확인합니다.
- 광고성, 중복, 오래된 정보 가능성을 확인합니다.
- 반복 가능한 브리핑 workflow에 넣을 수 있는지 판단합니다.

## How to select OSS candidates safely

- 저장소의 `CONTRIBUTING`, build guide, test command를 확인합니다.
- good first issue 또는 beginner-friendly label만으로 난이도를 단정하지 않습니다.
- 오래된 issue, 응답 없는 저장소, 재현 불가능한 이슈는 후보에서 낮게 평가합니다.
- 외부 프로젝트에 부담을 주지 않는 방식으로 접근합니다.
