# Fresh Fork Smoke Test

> Language: [한국어](./fresh-fork-smoke-test.md) | [English](../../en/getting-started/fresh-fork-smoke-test.md)

이 문서는 Career Feed를 처음 fork한 사용자가 workflow YAML을 수정하지 않고 `Backend Daily Brief` dry-run을 확인하는 짧은 체크리스트입니다.

목표는 Discord 전송 없이 artifact와 validation 결과를 먼저 확인하는 것입니다.

## Prerequisites

준비물:

- GitHub 계정
- fork한 Career Feed repository
- `OPENAI_API_KEY`
- 선택 사항: 나중에 delivery를 켤 때 사용할 Discord webhook URL
- 선택 사항: 나중에 source 보강에 사용할 Naver credentials
- 선택 사항: 나중에 source 보강에 사용할 Brave Search credentials

실제 API key, webhook URL, token, private identifier는 docs, issue, PR, commit, Actions log, screenshot에 넣지 않습니다.

## Required first run settings

첫 smoke test에서는 repository Secret 하나와 안전한 workflow input만 사용합니다.

Repository Secret:

- `OPENAI_API_KEY`

Repository Variables:

- 없음

Workflow inputs:

- `dry_run=true` (기본값)
- `force_send=false`

`dry_run=true` 실행은 Discord 메시지를 보내면 안 됩니다.

Discord webhook Secret은 나중에 delivery를 켤 때 필요합니다. Naver와 Brave credentials는 선택 source 보강용입니다. 첫 dry-run artifact 확인만 할 때는 없어도 됩니다.

## Backend Daily Brief smoke test

1. fork repository의 `Settings > Secrets and variables > Actions > Secrets`로 이동합니다.
2. `OPENAI_API_KEY`를 repository Secret으로 등록합니다.
3. 첫 smoke test에서는 repository Variables를 추가하지 않습니다.
4. repository의 `Actions` 탭을 엽니다.
5. `Backend Daily Brief` workflow를 선택합니다.
6. `Run workflow`를 누릅니다.
7. branch가 default branch인지 확인합니다.
8. `dry_run`은 `true`로 둡니다.
9. `force_send`는 `false`로 둡니다.
10. `Run workflow`를 눌러 실행합니다.
11. run이 끝나면 Actions summary와 uploaded artifact를 엽니다.

GitHub가 checkbox label을 description으로 표시할 수 있습니다. 첫 번째 boolean input이 `dry_run`, 두 번째 boolean input이 `force_send`입니다.

## Expected artifacts

먼저 아래 파일을 확인합니다.

- `reports/briefs/ko-KR/backend-daily.md`
- `reports/ops/ko-KR/backend-daily-validation-report.md`
- `reports/ops/ko-KR/backend-daily-run-summary.md`
- `reports/candidates/ko-KR/oss-contribution-opportunities.json`

현재 `ko-KR` v0.2.0 workflow와 validation report가 `reports/candidates/ko-KR/kr-oss-contribution-opportunities.json` 이름을 함께 사용하면 그 파일도 확인합니다.

## What success means

Smoke test 성공은 다음을 뜻합니다.

- workflow run이 완료됩니다.
- `ko-KR` artifact가 생성됩니다.
- generated brief가 `reports/briefs/ko-KR/backend-daily.md`에 있습니다.
- validation report가 통과 상태입니다.
- run summary가 `dry_run=true`, `force_send=false`를 보여줍니다.
- Discord 메시지가 전송되지 않습니다.

OSS 후보나 뉴스성 source가 항상 풍부하게 나오는 것은 성공 조건이 아닙니다.

safe OSS 후보가 0개인 날에는 fallback 준비 루틴이 나올 수 있습니다.

Naver 또는 Brave credential이 없으면 일부 provider가 skip되거나 sparse artifact가 나올 수 있습니다. 첫 dry-run에서는 허용되는 상태입니다.

## When validation fails

validation이 실패하면 Discord delivery를 켜지 않습니다.

1. `reports/ops/ko-KR/backend-daily-validation-report.md`를 먼저 엽니다.
2. error code와 실패한 section을 확인합니다.
3. generated brief의 GitHub issue URL이 safe candidate artifact에 있는지 확인합니다.
4. 오래된 issue나 safe 후보 밖 issue가 포함되었는지 확인합니다.
5. candidate artifact가 비어 있으면 fallback section에 특정 GitHub issue URL이 들어갔는지 확인합니다.
6. Secret 값이나 webhook URL이 log 또는 artifact에 노출되지 않았는지 확인합니다.
7. 수정 없이 재실행하기 전에 source 부족, API failure, validation rule failure 중 어느 경우인지 구분합니다.

검증 실패 상태에서는 `dry_run=false`로 실행하지 않습니다.

## Before enabling Discord delivery

Discord delivery를 켜기 전에 아래 항목을 확인합니다.

- dry-run artifact의 내용이 Discord에 보내도 되는 초안인지 확인합니다.
- validation report가 통과했습니다.
- run summary에서 `dry_run=true`, `force_send=false`였는지 확인했습니다.
- `DISCORD_WEBHOOK_CAREER_FEED` 또는 workflow-specific Discord webhook Secret이 있습니다.
- `CAREER_FEED_DISCORD_DELIVERY_ENABLED`를 `true`로 바꾸는 이유가 명확합니다.
- 첫 실제 전송에서는 `force_send=false`를 유지합니다.
- 같은 날짜 중복 전송 가능성을 이해하지 못했다면 `force_send=true`를 사용하지 않습니다.
- 반복 scheduled generation이 필요할 때만 `CAREER_FEED_SCHEDULE_ENABLED=true`를 설정합니다.

실제 전송은 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`, `dry_run=false`, Discord webhook Secret, validation 통과, delivery lock 조건을 모두 만족할 때만 기대합니다.

## Related documents

- [Fork Setup Guide](./fork-setup.md)
- [Runtime Configuration](./runtime-configuration.md)
- [Webhook Setup](./webhook-setup.md)
- [Usage Guide](./usage.md)
