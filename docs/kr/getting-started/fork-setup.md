# Fork Setup Guide

> Language: [한국어](./fork-setup.md) | [English](../../en/getting-started/fork-setup.md)

Career Feed를 fork한 뒤 GitHub Actions에서 첫 dry-run을 실행하고, generated artifact를 확인한 다음 Discord delivery를 켜는 절차입니다.

이 문서 하나만 따라 하면 첫 dry-run 성공까지 도달하는 것을 목표로 합니다.

상세 설정값은 [Runtime Configuration](runtime-configuration.md), webhook 이름은 [Webhook Setup](webhook-setup.md), 반복 운영 방법은 [Usage Guide](usage.md),
OSS 후보 정책은 [OSS Candidate Policy](../policies/oss-candidate-policy.md)를 참고하세요.

## Before You Start

준비물:

- GitHub 계정
- fork한 Career Feed repository
- OpenAI API key
- Discord Webhook URL
- 선택 사항: Naver 또는 Brave Search API credential

보안 기준:

- 실제 API key, webhook URL, token, client secret은 README, docs, issue, PR, commit, Actions log, screenshot에 쓰지 않습니다.
- API key, Discord Webhook URL, client secret은 GitHub Actions Secrets에 넣습니다.
- timezone, 실행 시간, delivery flag처럼 노출되어도 되는 값만 GitHub Actions Variables에 넣습니다.
- 첫 실행은 반드시 `dry_run=true`, `force_send=false`로 시작합니다.

이 문서의 화면 이미지는 실제 GitHub 화면을 기준으로 합니다.
권한이 필요한 Settings나 workflow input 화면은 fork repository에 로그인한 사용자에게만 보일 수 있습니다.
버튼 이름이나 위치가 조금 달라도 이동 경로와 입력값을 기준으로 따라가면 됩니다.

## Step 1. Fork Repository

GitHub에서 `stdiodh/career-feed`를 fork합니다.

![GitHub repository 상단의 Fork 버튼 위치](../../assets/getting-started/00-repository-fork-button.png)

1. 원본 repository 상단의 `Fork` 버튼을 누릅니다.
2. 내 GitHub 계정 또는 organization 아래에 repository를 만듭니다.
3. fork한 repository의 default branch를 기준으로 이후 단계를 진행합니다.

처음에는 workflow YAML을 직접 수정하지 말고 Secrets와 Variables만 설정하세요.

## Step 2. Enable GitHub Actions

fork repository의 `Actions` 탭을 엽니다.

![GitHub Actions 탭과 workflow 목록 위치](../../assets/getting-started/01-actions-tab-workflow-list.png)

1. repository 상단의 `Actions` 탭을 누릅니다.
2. GitHub가 fork workflow 실행을 막고 있다면 `I understand my workflows, go ahead and enable them` 또는 동등한 활성화 버튼을 누릅니다.
3. 왼쪽 workflow 목록에 `Backend Daily Brief`, `Dev News Daily`, `Backend Career Site Radar`, `Mark PS Solved`가 보이는지 확인합니다.

scheduled run은 default branch에서만 안정적으로 동작합니다.

## Step 3. Add GitHub Actions Secrets

GitHub repository에서 `Settings > Secrets and variables > Actions > Secrets`로 이동합니다.

![GitHub Actions Secrets 화면에서 New repository secret 버튼 위치](../../assets/getting-started/02-secrets-new-repository-secret.png)

1. `Secrets` 탭을 선택합니다.
2. `New repository secret` 버튼을 누릅니다.
3. `Name`에는 아래 표의 secret 이름을 정확히 입력합니다.
4. `Secret`에는 실제 값을 입력합니다.
5. `Add secret` 버튼을 누릅니다.

![GitHub Actions Secrets의 Name, Secret 입력 필드와 Add secret 버튼](../../assets/getting-started/03-secrets-add-secret-form.png)

| Name | Required | Used by |
| --- | --- | --- |
| `OPENAI_API_KEY` | Required | Brief generation |
| `DISCORD_WEBHOOK_KO_KR_BACKEND_DAILY` | `ko-KR` Daily Backend delivery 시 Required | Daily Backend Brief |
| `DISCORD_WEBHOOK_EN_US_BACKEND_DAILY` | `en-US` Daily Backend delivery 시 Required | Daily Backend Brief |
| `DISCORD_WEBHOOK_KO_KR_NEWS_DAILY` | `ko-KR` News Daily delivery 시 Required | Dev News Daily |
| `DISCORD_WEBHOOK_EN_US_NEWS_DAILY` | `en-US` News Daily delivery 시 Required | Dev News Daily |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Compatibility fallback | `ko-KR` Daily Backend Brief |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Compatibility fallback | `ko-KR` Dev News Daily |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Required for Career Radar delivery | Backend Career Site Radar |
| `NAVER_CLIENT_ID` | Optional | `ko-KR` source integration |
| `NAVER_CLIENT_SECRET` | Optional | `ko-KR` source integration |
| `BRAVE_SEARCH_API_KEY` | Optional | `en-US` source integration |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | Ops/debug alerts |

placeholder가 필요하면 `your-openai-api-key`, `your-discord-webhook-url`, `your-naver-client-id`처럼 명확히 가짜 값만 사용합니다.

## Step 4. Add GitHub Actions Variables

GitHub repository에서 `Settings > Secrets and variables > Actions > Variables`로 이동합니다.

![GitHub Actions Variables 탭과 New repository variable 버튼](../../assets/getting-started/04-variables-tab-new-variable.png)

1. `Variables` 탭을 선택합니다.
2. `Repository variables` 영역의 `New repository variable` 버튼을 누릅니다.
3. `Name`에는 아래 표의 variable 이름을 입력합니다.
4. `Value`에는 설정값을 입력합니다.
5. `Add variable` 버튼을 누릅니다.

![GitHub Actions Variables의 Name, Value 입력 필드와 Add variable 버튼](../../assets/getting-started/05-variables-add-variable-form.png)

| Name | Required | Default | First value |
| --- | --- | --- | --- |
| `CAREER_FEED_ENABLED_LOCALES` | Optional | `ko-KR` | `ko-KR` |
| `CAREER_FEED_DEFAULT_LOCALE` | Optional | `ko-KR` | `ko-KR` |
| `CAREER_FEED_SEARCH_PROVIDERS_KO_KR` | Optional | `naver,rss,github` | `naver,rss,github` |
| `CAREER_FEED_SEARCH_PROVIDERS_EN_US` | Optional | `brave,rss,github` | `brave,rss,github` |
| `CAREER_FEED_TIMEZONE` | Optional | `Asia/Seoul` | `Asia/Seoul` |
| `CAREER_FEED_BACKEND_DAILY_TIME` | Optional | `09:00` | `09:00` |
| `CAREER_FEED_NEWS_DAILY_TIME` | Optional | `09:05` | `09:05` |
| `CAREER_FEED_CAREER_WEEKLY_DAY` | Optional | `MON` | `MON` |
| `CAREER_FEED_CAREER_WEEKLY_TIME` | Optional | `09:00` | `09:00` |
| `CAREER_FEED_OSS_RECENT_DAYS` | Optional | `30` | `30` |
| `CAREER_FEED_DISCORD_DELIVERY_ENABLED` | Optional | `false` | `false` |

첫 dry-run 전에는 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`를 유지하세요.
이 값이 `true`가 아니면 `dry_run=false`로 실행하더라도 Discord 전송은 시도되지 않습니다.

시간은 `HH:MM`, 요일은 `MON`부터 `SUN`, timezone은 `Asia/Seoul` 같은 IANA timezone 이름을 사용합니다.

첫 fork 설정은 `CAREER_FEED_ENABLED_LOCALES=ko-KR` 기준으로 시작합니다.
나중에 `en-US` v0.2 foundation을 테스트하려면 `ko-KR,en-US`로 바꾸고, 전송을 켜기 전에 `en-US`용 Discord webhook Secret을 함께 등록합니다.

## Step 5. Run Workflow with Dry Run

GitHub `Actions` 탭에서 `Backend Daily Brief` workflow를 선택합니다.

1. `Run workflow` 버튼을 누릅니다.
2. branch가 default branch인지 확인합니다.
3. `dry_run`은 `true`로 둡니다.
4. `force_send`는 `false`로 둡니다.
5. 메뉴 안의 `Run workflow` 버튼을 눌러 실행합니다.

![GitHub Actions Run workflow 메뉴와 dry-run 입력 위치](../../assets/getting-started/06-actions-run-workflow-inputs.png)

GitHub는 boolean input 이름 대신 description 문구를 checkbox label로 보여줄 수 있습니다.
첫 번째 checkbox는 `dry_run`, 두 번째 checkbox는 `force_send`입니다.
첫 실행에서는 첫 번째 checkbox만 켜고 두 번째 checkbox는 끕니다.

`Run workflow` 버튼이 보이지 않으면 다음을 확인합니다.

- fork에서 GitHub Actions가 활성화되어 있는지 확인합니다.
- workflow 파일이 default branch에 있는지 확인합니다.
- repository에 로그인했고 workflow를 실행할 권한이 있는지 확인합니다.

## Step 6. Review Generated Artifacts

workflow run이 끝나면 Actions summary와 uploaded artifact를 확인합니다.

![GitHub Actions run summary의 Artifacts 영역 위치](../../assets/getting-started/07-actions-artifacts-summary.png)

Daily Backend Brief에서 먼저 볼 파일:

- `reports/briefs/ko-KR/backend-daily.md`
- `reports/ops/ko-KR/backend-daily-validation-report.md`
- `reports/ops/ko-KR/backend-daily-run-summary.md`
- `reports/candidates/ko-KR/oss-contribution-opportunities.json`

확인할 내용:

- generated Markdown이 기대한 언어와 섹션으로 생성되었는지 확인합니다.
- validation report가 `passed`인지 확인합니다.
- OSS candidate artifact의 `safe_candidate_count`와 `stale_issue_filtered_count`를 확인합니다.
- safe 후보가 없으면 OSS 기여 준비 루틴이 출력되는지 확인합니다.

validation이 실패하면 Discord delivery를 켜지 말고 report의 error code와 관련 URL을 먼저 확인하세요.

## Step 7. Enable Discord Delivery

dry-run 결과가 맞을 때만 Discord delivery를 켭니다.

![CAREER_FEED_DISCORD_DELIVERY_ENABLED variable 설정 위치](../../assets/getting-started/08-enable-discord-delivery-variable.png)

1. 필요한 Discord webhook Secret이 등록되어 있는지 확인합니다.
2. `Settings > Secrets and variables > Actions > Variables`로 이동합니다.
3. `CAREER_FEED_DISCORD_DELIVERY_ENABLED` 값을 `true`로 변경합니다.
4. GitHub `Actions` 탭에서 Daily workflow를 다시 수동 실행합니다.
5. Daily workflow에서는 `dry_run=false`, `force_send=false`로 실행합니다.

같은 날짜에 이미 전송한 run이 있고 다시 실제 전송을 확인해야 한다면 `force_send=true`를 사용할 수 있습니다.
처음 live delivery 검증에서는 중복 전송 가능성을 이해한 뒤에만 `force_send=true`를 사용하세요.

Discord 전송이 실제로 일어나려면 아래 조건을 모두 만족해야 합니다.

1. `dry_run=false`
2. `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`
3. 해당 workflow에 필요한 Discord webhook Secret 존재
4. generated brief validation 통과
5. runtime gate 통과
6. delivery lock 또는 중복 방지 정책 통과

dry-run에서는 Discord 메시지가 오지 않는 것이 정상입니다.

## Success Checklist

- [ ] Repository를 fork했습니다.
- [ ] fork에서 GitHub Actions를 활성화했습니다.
- [ ] `OPENAI_API_KEY`를 Secrets에 등록했습니다.
- [ ] 필요한 Discord webhook Secret을 Secrets에 등록했습니다.
- [ ] runtime Variables를 확인했습니다.
- [ ] 첫 dry-run 전 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=false`를 유지했습니다.
- [ ] `Backend Daily Brief`를 `dry_run=true`, `force_send=false`로 실행했습니다.
- [ ] generated brief artifact를 확인했습니다.
- [ ] validation report가 통과했습니다.
- [ ] Discord delivery를 켜기 전에 artifact 내용을 검토했습니다.

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

### validation report가 실패함

- `OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES`: generated brief에 safe candidate artifact에 없는 GitHub issue URL이 들어갔습니다.
- `OSS_ISSUE_URL_NOT_RECENT`: generated brief에 최근성 기준 밖의 오래된 GitHub issue URL이 들어갔습니다.
- `OSS_FALLBACK_CONTAINS_ISSUE_URL`: safe 후보가 0개인데 fallback section에 특정 GitHub issue URL이 들어갔습니다.

이 경우 Discord delivery를 켜지 말고 validation report와 `kr-oss-contribution-opportunities.json`을 먼저 확인합니다.

### OSS 후보가 없음

- `kr-oss-contribution-opportunities.json`의 `safe_candidate_count`를 확인합니다.
- `stale_issue_filtered_count`가 높으면 오래전에 생성된 issue가 최근성 기준으로 제외된 것입니다.
- safe 후보가 없으면 fallback 준비 루틴이 출력되는 것이 정상입니다.

### 시간대 설정 오류

- `Asia/Seoul`처럼 IANA timezone 이름을 사용합니다.
- `Seoul`, `KST`, `America/Los Angeles`는 올바른 timezone 값이 아닙니다.
- runtime gate log의 `reason`과 `timezone` output을 확인합니다.

## Related Documents

- [Usage Guide](usage.md)
- [Runtime Configuration](runtime-configuration.md)
- [Daily Backend Brief](../operations/daily-backend-brief.md)
- [OSS Candidate Policy](../policies/oss-candidate-policy.md)
- [Demo Guide](../demo.md)
- [Local Validation](../operations/local-validation.md)
