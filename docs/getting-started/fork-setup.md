# Fork Setup Guide

Career Feed를 fork한 사용자가 GitHub Actions에서 dry-run을 실행하고,
artifact를 확인한 뒤 Discord 전송까지 켜는 첫 설정 절차입니다.

자세한 운영 정책은 [Usage Guide](usage.md), 실행 시간 설정은
[Runtime Configuration](runtime-configuration.md), OSS 후보 기준은
[OSS Candidate Policy](../policies/oss-candidate-policy.md)를 참고하세요.

## 대상

다음 사용자에게 맞춰져 있습니다.

- Career Feed를 fork해서 자기 Discord에 브리핑을 받고 싶은 사용자
- Java/Kotlin 백엔드 학습자
- Discord 스터디나 커뮤니티 운영자
- GitHub Actions 기반 자동화를 실험해보고 싶은 개발자

## 준비물

- GitHub 계정
- fork한 Career Feed repository
- OpenAI API key
- Discord Webhook URL
- 선택 사항: Naver API credential

실제 API key, webhook URL, token, client secret은 README, docs, issue, PR, commit, Actions log,
screenshot에 쓰지 마세요.

## 전체 설정 흐름

1. Repository를 fork합니다.
2. fork에서 GitHub Actions를 활성화합니다.
3. GitHub Actions Secrets를 등록합니다.
4. GitHub Actions Variables를 등록합니다.
5. Daily workflow를 `dry_run=true`로 수동 실행합니다.
6. generated brief, candidate artifact, validation report를 확인합니다.
7. 결과가 맞으면 Discord delivery를 활성화합니다.
8. scheduled automation이 원하는 시간에 동작하는지 확인합니다.

## Step 1. Fork repository

GitHub에서 `stdiodh/career-feed`를 fork합니다.

fork한 repository의 기본 branch에서 workflow가 실행됩니다.

처음에는 workflow YAML을 직접 수정하지 말고 Secrets와 Variables만 설정하세요.

## Step 2. Enable GitHub Actions

fork repository의 `Actions` 탭을 엽니다.

GitHub가 fork workflow 실행을 막고 있다면 `I understand my workflows, go ahead and enable them` 또는
동등한 활성화 버튼을 눌러 Actions를 켭니다.

scheduled run은 default branch에서만 안정적으로 동작합니다.

## Step 3. Add GitHub Actions Secrets

GitHub repository에서 `Settings > Secrets and variables > Actions > Secrets`로 이동합니다.

아래 값은 민감값이므로 Variables가 아니라 Secrets에 등록합니다.

| Name | Required | Used by | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Required | Brief generation | OpenAI API key used to generate brief content. |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Required for Daily Backend delivery | Daily Backend Brief | Discord webhook URL for daily backend brief delivery. |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Required for News Daily delivery | Korea Dev/AI News Daily | Discord webhook URL for Korean dev/AI news delivery. |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Required for Career Radar delivery | Backend Career Site Radar | Discord webhook URL for weekly backend career radar delivery. |
| `NAVER_CLIENT_ID` | Optional | News source integration | Naver API client id. |
| `NAVER_CLIENT_SECRET` | Optional | News source integration | Naver API client secret. |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | Ops/debug alerts | Discord webhook URL for workflow operation alerts. |

placeholder를 적어야 한다면 `your-openai-api-key`, `your-discord-webhook-url`,
`your-naver-client-id`처럼 명확히 가짜 값으로만 적습니다.

## Step 4. Add GitHub Actions Variables

GitHub repository에서 `Settings > Secrets and variables > Actions > Variables`로 이동합니다.

아래 값은 비민감 실행 설정입니다.

| Name | Required | Default | Example | Description |
| --- | --- | --- | --- | --- |
| `CAREER_FEED_TIMEZONE` | Optional | `Asia/Seoul` | `Asia/Seoul` | Local timezone used by the runtime gate. |
| `CAREER_FEED_BACKEND_DAILY_TIME` | Optional | `09:00` | `09:00` | Target time for Daily Backend Brief. |
| `CAREER_FEED_NEWS_DAILY_TIME` | Optional | `09:05` | `09:05` | Target time for Korea Dev/AI News Daily. |
| `CAREER_FEED_CAREER_WEEKLY_DAY` | Optional | `MON` | `MON` | Target day for Backend Career Site Radar. |
| `CAREER_FEED_CAREER_WEEKLY_TIME` | Optional | `09:00` | `09:00` | Target time for Backend Career Site Radar. |
| `CAREER_FEED_OSS_RECENT_DAYS` | Optional | `30` | `30` | Maximum age in days for OSS issue candidates based on `created_at`. |
| `CAREER_FEED_DISCORD_DELIVERY_ENABLED` | Optional | `false` | `false` | Enables Discord delivery when dry-run is disabled. |

처음 dry-run 전에는 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`를 유지하세요.

시간은 `HH:MM` 형식입니다.

요일은 `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `SUN` 중 하나입니다.

timezone은 `Asia/Seoul`, `UTC`, `America/Los_Angeles` 같은 IANA timezone 이름을 사용합니다.

## Step 5. Run workflow with dry-run

GitHub `Actions` 탭에서 `Daily Korea Tech Brief` workflow를 선택합니다.

`Run workflow`를 누르고 다음 입력으로 실행합니다.

| Input | Value |
| --- | --- |
| `dry_run` | `true` |
| `force_send` | `false` |

dry-run은 Discord 메시지를 보내지 않습니다.

dry-run은 generated brief와 validation report를 artifact로 확인하기 위한 안전 실행입니다.

## Step 6. Review generated artifacts

workflow run이 끝나면 Actions summary와 uploaded artifact를 확인합니다.

Daily Backend Brief에서 먼저 볼 파일은 다음과 같습니다.

- `reports/briefs/kr-tech-daily.md`
- `reports/ops/backend-daily-validation-report.md`
- `reports/ops/backend-daily-run-summary.md`
- `reports/candidates/kr-oss-contribution-opportunities.json`

확인할 내용은 다음과 같습니다.

- generated Markdown이 기대한 언어와 섹션으로 생성되었는지 확인합니다.
- validation report가 `passed`인지 확인합니다.
- OSS candidate artifact의 `safe_candidate_count`와 `stale_issue_filtered_count`를 확인합니다.
- 오래된 issue가 추천 섹션에 들어가지 않았는지 확인합니다.
- safe 후보가 없으면 OSS 기여 준비 루틴이 출력되는지 확인합니다.

validation이 실패하면 Discord delivery를 켜지 말고 report에 나온 error code와 URL을 먼저 확인하세요.

## Step 7. Enable Discord delivery

dry-run 결과가 맞을 때만 Discord delivery를 켭니다.

1. 필요한 Discord webhook Secret이 등록되어 있는지 확인합니다.
2. `Settings > Secrets and variables > Actions > Variables`에서
   `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`로 변경합니다.
3. Daily workflow를 다시 수동 실행합니다.
4. Daily workflow에서는 `dry_run=false`를 사용합니다.

Discord 전송이 실제로 일어나려면 아래 조건을 모두 만족해야 합니다.

1. `dry_run=false`
2. `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`
3. 해당 workflow에 필요한 Discord webhook Secret 존재
4. generated brief validation 통과
5. runtime gate 통과
6. delivery lock 또는 중복 방지 정책 통과

## Step 8. Understand scheduling

GitHub Actions의 `on.schedule` cron은 repository Variables를 직접 읽어 사용자별 시간으로 바뀌지 않습니다.

Career Feed workflow는 주기적으로 깨어나고, 초반에 runtime gate script가 Variables를 읽어 실행 여부를 판단합니다.

즉, workflow YAML을 수정하지 않고 아래 Variables로 목표 시간을 설정합니다.

- `CAREER_FEED_TIMEZONE`
- `CAREER_FEED_BACKEND_DAILY_TIME`
- `CAREER_FEED_NEWS_DAILY_TIME`
- `CAREER_FEED_CAREER_WEEKLY_DAY`
- `CAREER_FEED_CAREER_WEEKLY_TIME`

manual `workflow_dispatch` 실행은 runtime time window 때문에 막히지 않습니다.

## OSS candidate policy

기본적으로 현재 실행 시점 기준 최근 30일 이내에 생성된 GitHub issue만 OSS 기여 후보로 추천합니다.

기준은 `created_at`입니다.

`updated_at`이 최근이어도 오래전에 생성된 issue는 stale로 보고 제외합니다.

`CAREER_FEED_OSS_RECENT_DAYS`로 기준일을 조정할 수 있지만, 너무 넓게 잡으면 오래된 open issue가 다시 후보 pool에 많이
남을 수 있습니다.

최근 safe 후보가 없으면 오래된 issue를 억지로 추천하지 않고 OSS 기여 준비 루틴을 출력합니다.

fallback은 실패가 아니라 안전한 동작입니다.

자세한 기준은 [OSS Candidate Policy](../policies/oss-candidate-policy.md)를 참고하세요.

## Validation troubleshooting

Validation은 잘못된 브리프가 Discord로 전송되는 것을 막기 위한 안전장치입니다.

validation 실패 시 workflow가 실패하고 Discord 전송은 차단됩니다.

### `OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES`

Generated brief에 safe candidate artifact에 없는 GitHub issue URL이 포함되었습니다.

확인할 것:

- `kr-oss-contribution-opportunities.json`에 해당 URL이 있는지
- 해당 item이 `safe_to_recommend=true`인지
- 해당 item이 `is_recent=true`인지
- LLM 또는 template이 safe candidates 밖의 URL을 만들고 있지 않은지

### `OSS_ISSUE_URL_NOT_RECENT`

Generated brief에 오래된 GitHub issue URL이 포함되었습니다.

해결:

- candidate artifact의 `created_at`을 확인합니다.
- `CAREER_FEED_OSS_RECENT_DAYS` 값을 확인합니다.
- generated brief를 다시 생성합니다.
- 오래된 issue를 수동으로 allowlist에 넣지 않습니다.

### `OSS_FALLBACK_CONTAINS_ISSUE_URL`

safe 후보가 0개인데 fallback section에 GitHub issue URL이 포함되었습니다.

fallback은 준비 루틴이어야 하며 특정 issue URL을 포함하지 않습니다.

## Troubleshooting

### Actions가 실행되지 않음

- fork에서 GitHub Actions가 활성화되어 있는지 확인합니다.
- workflow가 default branch에 있는지 확인합니다.
- manual `workflow_dispatch`가 보이는지 확인합니다.

### OpenAI API key 오류

- `OPENAI_API_KEY`가 Secrets에 등록되어 있는지 확인합니다.
- Variables가 아니라 Secrets에 등록했는지 확인합니다.
- 실제 key를 issue, PR, log, screenshot에 붙여 넣지 않습니다.

### workflow는 성공했는데 Discord 메시지가 오지 않음

확인 순서:

1. `dry_run` 값이 `true`였는지 확인합니다.
2. `CAREER_FEED_DISCORD_DELIVERY_ENABLED`가 `true`인지 확인합니다.
3. webhook Secret 이름이 workflow가 기대하는 이름과 같은지 확인합니다.
4. validation report가 통과했는지 확인합니다.
5. runtime gate log에서 `should_run`과 `reason`을 확인합니다.
6. delivery lock log에서 이미 같은 날짜에 전송되었는지 확인합니다.

dry-run에서는 Discord 메시지가 오지 않는 것이 정상입니다.

### OSS 후보가 없음

- `kr-oss-contribution-opportunities.json`의 `safe_candidate_count`를 확인합니다.
- `stale_issue_filtered_count`가 높다면 최근 window 밖 issue가 많이 제외된 것입니다.
- safe 후보가 없으면 fallback 준비 루틴이 출력되는 것이 정상입니다.

### timezone 설정 오류

- `Seoul`이나 `KST` 대신 `Asia/Seoul`을 사용합니다.
- `America/Los Angeles`처럼 공백이 있는 값은 잘못된 timezone입니다.
- runtime gate log의 `reason`과 `timezone` output을 확인합니다.

### scheduled run 시간이 예상과 다름

- GitHub Actions cron 자체는 Variables로 동적으로 바뀌지 않습니다.
- workflow가 주기적으로 깨어난 뒤 runtime gate가 target time window인지 판단합니다.
- `CAREER_FEED_TIMEZONE`과 workflow별 target time Variable을 확인합니다.

## First run checklist

- [ ] Repository forked
- [ ] GitHub Actions enabled
- [ ] Required Secrets added
- [ ] Runtime Variables reviewed
- [ ] `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false` for first dry-run
- [ ] Manual workflow run completed with `dry_run=true`
- [ ] Generated brief artifact reviewed
- [ ] Validation report passed
- [ ] Discord webhook Secret verified
- [ ] `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true` enabled after dry-run
- [ ] Manual workflow run completed with `dry_run=false`
- [ ] Discord message received

## Before opening an issue

- [ ] I checked the workflow run logs.
- [ ] I checked the validation report artifact.
- [ ] I confirmed whether this was a dry-run.
- [ ] I confirmed the delivery flag value.
- [ ] I confirmed the webhook Secret name.
- [ ] I removed real secrets, webhook URLs, private channel names, and personal identifiers from the issue.

## Related documents

- [Usage Guide](usage.md)
- [Runtime Configuration](runtime-configuration.md)
- [Daily Backend Brief](../operations/daily-backend-brief.md)
- [OSS Candidate Policy](../policies/oss-candidate-policy.md)
- [Demo Guide](../demo.md)
- [Local Validation](../operations/local-validation.md)
