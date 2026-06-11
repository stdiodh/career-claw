# CLI Setup

> Language: [한국어](../../kr/getting-started/cli-setup.md) | [English](./cli-setup.md)

This optional helper configures a fork with GitHub CLI so you do not need to click through every GitHub Settings page.

The [Fork Setup Guide](fork-setup.md) remains the primary fallback and is the source of truth for GitHub UI setup.

## When To Use It

Use CLI setup when:

- you already forked Career Feed
- GitHub Actions is enabled in the fork
- `gh` is installed and authenticated
- you want to set repository Secrets or Variables from the terminal

Do not use this helper to store real secret values in files, command examples, issues, pull requests, logs, or screenshots.

## Minimal Path

The minimal first dry-run still requires only one repository Secret: `OPENAI_API_KEY`.

1. Fork `stdiodh/career-feed`.
2. Enable GitHub Actions in the fork from the GitHub UI.
3. Authenticate GitHub CLI:

```bash
gh auth login
```

4. From a cloned fork, run:

```bash
scripts/setup-fork.sh --minimal
```

If the repository cannot be inferred from the current directory, pass it explicitly:

```bash
scripts/setup-fork.sh --minimal --repo OWNER/REPO
```

5. Manually run `Backend Daily Brief` from the GitHub Actions UI with `dry_run=true` and `force_send=false`.
6. Review artifacts before enabling Discord delivery.

`--minimal` does not create optional Variables and does not ask for Discord, Naver, or Brave credentials.

## Flags

| Flag | Effect |
| --- | --- |
| `--minimal` | Runs interactive `gh secret set OPENAI_API_KEY` |
| `--with-discord` | Runs interactive `gh secret set DISCORD_WEBHOOK_CAREER_FEED` and sets `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true` |
| `--enable-schedule` | Sets `CAREER_FEED_SCHEDULE_ENABLED=true` |
| `--repo OWNER/REPO` | Targets a repository explicitly |

You can combine flags when you intentionally want the extra setup:

```bash
scripts/setup-fork.sh --minimal --with-discord --repo OWNER/REPO
```

## Discord Option

`--with-discord` configures the generic webhook Secret:

- `DISCORD_WEBHOOK_CAREER_FEED`

It also sets:

- `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`

The script warns before setting the delivery flag. Live Discord delivery still requires `dry_run=false`, a passing validation report, runtime gate pass, and duplicate-delivery policy pass.

Dry-runs should not send Discord messages.

## Schedule Option

Scheduled generation is disabled by default for new forks.

Use this only when you want recurring scheduled generation:

```bash
scripts/setup-fork.sh --enable-schedule --repo OWNER/REPO
```

This sets:

- `CAREER_FEED_SCHEDULE_ENABLED=true`

Manual `workflow_dispatch` runs work without this flag.

Scheduled generation may consume OpenAI API credits when the configured time window matches.

## Advanced Variables

Repository Variables are advanced overrides.

Do not create them during the first smoke test unless you intentionally need to change locale, provider, timezone, target time, delivery, or schedule behavior.

For supported Variables, see [Runtime Configuration](runtime-configuration.md).

## Secret Safety

The helper uses interactive `gh secret set` prompts for Secrets.

It does not pass secret values through command-line arguments and does not write secret values to disk.

Do not run commands such as `gh secret set OPENAI_API_KEY --body real-key-value`.

## Troubleshooting

### gh is missing

Install GitHub CLI, then run:

```bash
gh auth login
```

### gh is not authenticated

Run:

```bash
gh auth login
```

Then rerun the setup command.

### Repository is missing

Run from a cloned fork or pass:

```bash
scripts/setup-fork.sh --minimal --repo OWNER/REPO
```

### Actions are not enabled

Open the fork in GitHub and enable Actions from the `Actions` tab. The CLI helper does not replace this GitHub safety step.

## Related Documents

- [Fork Setup Guide](fork-setup.md)
- [Fresh Fork Smoke Test](fresh-fork-smoke-test.md)
- [Runtime Configuration](runtime-configuration.md)
- [Webhook Setup](webhook-setup.md)
