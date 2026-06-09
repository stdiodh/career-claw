# Demo Guide

> Language: [한국어](../kr/demo.md) | [English](./demo.md)

Use this guide when showing Career Feed in a README, issue, pull request, or short walkthrough.

## Demo Flow

1. Open the repository README and choose Korean or English start.
2. Show the fork setup path and dry-run workflow input.
3. Open generated artifacts, validation reports, and run summaries.
4. Explain that Discord delivery remains disabled until explicitly enabled.

## What to Show

- The language gateway.
- A dry-run workflow dispatch.
- Generated `reports/briefs/*.md` artifacts.
- Validation reports and sparse or fallback behavior.

## What Not to Show

Do not show real API keys, webhook URLs, private logs, private repository data, or personal Discord channel details.

## Screenshot Rules

Blur repository secrets, account identifiers, private webhook names, and unrelated browser tabs. Prefer screenshots from dry-run artifacts.

## Optional GIF

A short GIF can show opening Actions, selecting a workflow, running `dry_run=true`, and downloading artifacts. Keep it short and avoid credentials.

## Related Documents

- [Fork Setup Guide](./getting-started/fork-setup.md)
- [Sample Output](./getting-started/sample-output.md)
- [Usage Guide](./getting-started/usage.md)
