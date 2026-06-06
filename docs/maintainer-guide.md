# Maintainer Guide

이 문서는 Career Feed maintainer가 daily/weekly workflow를 안전하게 운영하기 위한 체크리스트입니다.

## Daily workflow dry-run checklist

전송 전에 다음을 확인합니다.

- `dry_run=true`로 실행했는가?
- `force_send=false`로 실행했는가?
- 생성된 artifact를 확인했는가?
- validator가 실패하지 않았는가?
- 중복 전송 가능성이 없는가?
- Discord Webhook URL이 로그에 노출되지 않았는가?

## Validation before send

가능한 경우 다음 명령을 확인합니다.

    git diff --check
    python3 scripts/check-workflow-schedules.py
    ./scripts/validate.sh

Daily Backend Brief:

    python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run

Korea Dev/AI News Daily:

    python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run

Backend Career Site Radar:

    python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
    python3 scripts/render-weekly-career-site-radar.py

## Secrets safety checklist

다음 값은 절대 커밋하지 않습니다.

- OpenAI API key
- Discord Webhook URL
- GitHub token
- Naver API credentials

노출이 의심되면 즉시 secret을 폐기하고 재발급합니다.

## What not to automate

Career Feed는 다음 행동을 자동화하지 않습니다.

- 외부 저장소에 댓글 작성
- 외부 저장소에 PR 생성
- 외부 저장소 issue assign
- 외부 저장소 label 변경
- 사용자의 커리어 판단 단정
- 채용 공고의 합격 가능성 평가

## Issue suggestion review

제안을 검토할 때 다음을 확인합니다.

- 백엔드 지망생에게 실제로 도움이 되는가?
- 출처가 공개적이고 확인 가능한가?
- 광고성 목적이 강하지 않은가?
- 업데이트 빈도가 너무 낮지 않은가?
- beginner-friendly 여부를 설명할 수 있는가?
- workflow scope를 지나치게 넓히지 않는가?

## OSS candidate review

OSS 후보는 추천만 합니다.

외부 저장소에 실제 기여하기 전에는 다음을 직접 확인해야 합니다.

- README
- CONTRIBUTING
- build guide
- test command
- issue context
- license
- 최근 commit과 issue 활동
