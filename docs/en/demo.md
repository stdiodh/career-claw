# Demo Guide

> Language: [한국어](../kr/demo.md) | [English](./demo.md)

Use this guide when showing Career Feed in a README, issue, pull request, or short walkthrough.

## Demo Flow

1. Open the repository README and choose Korean or English start.
2. Show the fork setup path and dry-run workflow input.
3. Open generated artifacts, validation reports, and run summaries.
4. Explain that Discord delivery remains disabled until explicitly enabled.

The current repository includes mock redacted screenshots for this flow.
They are explanatory demo images, not live GitHub or Discord captures.

![GitHub Actions manual dry-run mock screen](../assets/demo/github-actions-dispatch-redacted.png)

![Actions summary and artifacts mock screen](../assets/demo/actions-summary-redacted.png)

![Validation report and generated brief preview mock screen](../assets/demo/validation-report-redacted.png)

![Discord briefing mock screen](../assets/demo/discord-brief-redacted.png)

## What to Show

- The language gateway.
- A dry-run workflow dispatch.
- Generated `reports/briefs/*.md` artifacts.
- Validation reports and sparse or fallback behavior.

## What Not to Show

Do not show real API keys, webhook URLs, private logs, private repository data, or personal Discord channel details.

## Screenshot Rules

Blur repository secrets, account identifiers, private webhook names, and unrelated browser tabs. Prefer screenshots from dry-run artifacts.

Current linked files:

- `docs/assets/demo/github-actions-dispatch-redacted.png`
- `docs/assets/demo/actions-summary-redacted.png`
- `docs/assets/demo/validation-report-redacted.png`
- `docs/assets/demo/discord-brief-redacted.png`

## Optional GIF

A short GIF can show opening Actions, selecting a workflow, running `dry_run=true`, and downloading artifacts. Keep it short and avoid credentials.

## Related Documents

- [Fork Setup Guide](./getting-started/fork-setup.md)
- [Sample Output](./getting-started/sample-output.md)
- [Usage Guide](./getting-started/usage.md)
