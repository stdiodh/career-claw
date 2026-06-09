# 데모 가이드

> Language: [한국어](./demo.md) | [English](../en/demo.md)

Career Feed를 실행하면 어떤 화면과 결과물을 보게 되는지 빠르게 보여주는 문서입니다.

데모는 제품 홍보 화면이 아니라 운영 흐름 설명입니다.
웹 대시보드, Discord Gateway Bot, Slash Command, 채용 매칭 서비스처럼 보이지 않게 유지합니다.

## Demo Flow

사용자용 데모는 다음 네 장면이면 충분합니다.

1. GitHub Actions에서 `workflow_dispatch`를 실행합니다.
2. Actions summary 또는 validation report를 확인합니다.
3. artifact에서 생성된 Markdown briefing을 확인합니다.
4. Discord에 도착한 redacted briefing 예시를 확인합니다.

현재 저장소에는 이 흐름을 설명하는 mock redacted screenshot이 포함되어 있습니다.
아래 이미지는 실제 GitHub 또는 Discord live capture가 아니라 설명용 mock screenshot입니다.

![GitHub Actions 수동 dry-run mock 화면](../assets/demo/github-actions-dispatch-redacted.png)

![Actions summary와 artifacts mock 화면](../assets/demo/actions-summary-redacted.png)

![Validation report와 generated brief preview mock 화면](../assets/demo/validation-report-redacted.png)

![Discord briefing mock 화면](../assets/demo/discord-brief-redacted.png)

## What to Show

- GitHub Actions manual dispatch 화면
- `dry_run=true` 입력이 보이는 dry-run 실행 화면
- successful dry-run summary
- generated Markdown artifact
- validation report artifact
- Discord delivery 결과

Backend Career Site Radar는 dry-run 장면 대신 `send_to_discord=false`를 보여줍니다.
Mark PS Solved는 branch와 account detail이 안전하게 가려진 경우에만 입력 form과 `data/ps-progress.json` 변경을 보여줍니다.

## What Not to Show

- 실제 API key, token, credential
- Discord webhook URL
- private Discord server, channel, username, avatar, user id
- private repository URL, private organization name, account-specific URL
- 브라우저 주소창의 token, query parameter
- Actions log의 secret-like 문자열
- fake stars, forks, downloads, active users, adoption metrics
- 외부 저장소에 자동 comment, PR, assign, label 변경을 하는 장면
- 아직 존재하지 않는 dashboard, bot, slash command UI

## Screenshot Rules

demo asset은 `docs/assets/demo/` 디렉터리에 둡니다.

현재 링크된 파일:

- `docs/assets/demo/github-actions-dispatch-redacted.png`
- `docs/assets/demo/actions-summary-redacted.png`
- `docs/assets/demo/validation-report-redacted.png`
- `docs/assets/demo/discord-brief-redacted.png`

새 screenshot을 추가할 때는 다음을 지킵니다.

1. redacted 또는 mock data 기반 화면만 사용합니다.
2. crop 또는 solid block redaction을 우선합니다.
3. blur 아래 민감 텍스트가 복구될 수 있는 screenshot은 포함하지 않습니다.
4. README나 docs에서 링크하기 전에 파일이 실제로 존재하는지 확인합니다.
5. placeholder image는 만들지 않습니다.

## Optional GIF

GIF는 필수가 아닙니다.

만든다면 60~90초 이하, 10MB 이하를 권장합니다.
화면 전환 중 주소창, 계정명, 서버명, 사용자명, private URL이 보이면 repository에 넣지 않습니다.

권장 파일명:

- `docs/assets/demo/career-feed-demo.gif`

## Related Documents

- [Sample Output](getting-started/sample-output.md)
- [Fork Setup Guide](getting-started/fork-setup.md)
- [Usage Guide](getting-started/usage.md)
