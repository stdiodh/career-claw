# CLI Setup

> Language: [한국어](./cli-setup.md) | [English](../../en/getting-started/cli-setup.md)

이 helper는 GitHub CLI로 fork repository를 설정하는 선택 도구입니다. GitHub Settings 화면을 여러 번 클릭하지 않고 Secret과 Variable을 등록할 수 있습니다.

[Fork Setup Guide](fork-setup.md)는 GitHub UI setup의 기본 fallback이며, UI 절차의 source of truth입니다.

## When To Use It

다음 조건을 만족할 때 사용합니다.

- Career Feed를 이미 fork했습니다.
- fork에서 GitHub Actions를 활성화했습니다.
- `gh`가 설치되어 있고 인증되어 있습니다.
- terminal에서 repository Secret 또는 Variable을 설정하고 싶습니다.

실제 secret 값은 파일, command 예시, issue, PR, log, screenshot에 저장하거나 붙여 넣지 않습니다.

## Minimal Path

첫 dry-run 최소 설정은 여전히 repository Secret 하나, `OPENAI_API_KEY`만 필요합니다.

1. `stdiodh/career-feed`를 fork합니다.
2. GitHub UI에서 fork repository의 GitHub Actions를 활성화합니다.
3. GitHub CLI를 인증합니다.

```bash
gh auth login
```

4. clone한 fork 안에서 실행합니다.

```bash
scripts/setup-fork.sh --minimal
```

현재 directory에서 repository를 추론할 수 없으면 명시합니다.

```bash
scripts/setup-fork.sh --minimal --repo OWNER/REPO
```

5. GitHub Actions UI에서 `Backend Daily Brief`를 `dry_run=true`, `force_send=false`로 수동 실행합니다.
6. Discord delivery를 켜기 전에 artifact를 검토합니다.

`--minimal`은 optional Variables를 만들지 않고 Discord, Naver, Brave credential을 묻지 않습니다.

## Flags

| Flag | Effect |
| --- | --- |
| `--minimal` | interactive `gh secret set OPENAI_API_KEY` 실행 |
| `--with-discord` | interactive `gh secret set DISCORD_WEBHOOK_CAREER_FEED` 실행 후 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true` 설정 |
| `--enable-schedule` | `CAREER_FEED_SCHEDULE_ENABLED=true` 설정 |
| `--repo OWNER/REPO` | 대상 repository를 명시 |

추가 설정이 필요할 때만 flag를 조합합니다.

```bash
scripts/setup-fork.sh --minimal --with-discord --repo OWNER/REPO
```

## Discord Option

`--with-discord`는 generic webhook Secret을 설정합니다.

- `DISCORD_WEBHOOK_CAREER_FEED`

그리고 아래 Variable을 설정합니다.

- `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`

스크립트는 delivery flag를 설정하기 전에 경고를 출력합니다. 실제 Discord delivery는 여전히 `dry_run=false`, validation report 통과, runtime gate 통과, duplicate delivery 정책 통과가 필요합니다.

dry-run은 Discord 메시지를 보내면 안 됩니다.

## Schedule Option

새 fork의 scheduled generation은 기본값으로 꺼져 있습니다.

반복 scheduled generation이 필요할 때만 사용합니다.

```bash
scripts/setup-fork.sh --enable-schedule --repo OWNER/REPO
```

이 명령은 아래 Variable을 설정합니다.

- `CAREER_FEED_SCHEDULE_ENABLED=true`

수동 `workflow_dispatch` 실행은 이 flag 없이도 동작합니다.

scheduled generation은 설정한 시간 window가 맞을 때 OpenAI API credit을 사용할 수 있습니다.

## Advanced Variables

Repository Variables는 고급 override입니다.

첫 smoke test에서는 locale, provider, timezone, target time, delivery, schedule 동작을 의도적으로 바꿔야 할 때만 만듭니다.

지원 Variables는 [Runtime Configuration](runtime-configuration.md)을 참고하세요.

## Secret Safety

helper는 Secret 입력에 interactive `gh secret set` prompt를 사용합니다.

secret 값을 command-line argument로 넘기지 않고 disk에 쓰지 않습니다.

`gh secret set OPENAI_API_KEY --body real-key-value` 같은 명령은 사용하지 않습니다.

## Troubleshooting

### gh가 없음

GitHub CLI를 설치한 뒤 인증합니다.

```bash
gh auth login
```

### gh 인증이 안 됨

아래 명령을 실행합니다.

```bash
gh auth login
```

그 다음 setup 명령을 다시 실행합니다.

### Repository를 찾을 수 없음

clone한 fork 안에서 실행하거나 명시합니다.

```bash
scripts/setup-fork.sh --minimal --repo OWNER/REPO
```

### Actions가 비활성화됨

GitHub에서 fork repository를 열고 `Actions` 탭에서 Actions를 활성화합니다. CLI helper는 이 GitHub safety step을 대체하지 않습니다.

## Related Documents

- [Fork Setup Guide](fork-setup.md)
- [Fresh Fork Smoke Test](fresh-fork-smoke-test.md)
- [Runtime Configuration](runtime-configuration.md)
- [Webhook Setup](webhook-setup.md)
