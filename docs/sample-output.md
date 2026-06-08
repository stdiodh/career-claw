# Sample Output

This page points to reviewable sample outputs for Career Feed.

Samples are documentation examples, not live adoption claims.

Use placeholders and redacted content only. Do not include real webhook URLs, private Discord details, API keys, or personal identifiers.

## Available examples

| Example | File | Notes |
| --- | --- | --- |
| Daily Backend Brief | [examples/daily-backend-brief.example.md](examples/daily-backend-brief.example.md) | Shows the expected Markdown shape for a daily backend brief. |
| Backend Career Site Radar | [examples/career-site-radar.example.md](examples/career-site-radar.example.md) | Shows weekly career site radar output shape. |

## What to check in samples

- Links use public or placeholder URLs.
- No Discord webhook URL appears.
- No API key, token, credential, or private channel name appears.
- OSS candidate output does not imply automatic external GitHub actions.
- Fallback output is allowed when no safe OSS candidate exists.

## Adding a new sample

When adding a new sample:

1. Use redacted or placeholder data.
2. Keep the sample small enough to review in a PR.
3. Make clear whether it is generated output, hand-written example output, or fixture output.
4. Link it from this page only after the file exists.
5. Run documentation validation before opening a PR.

Recommended validation:

```bash
python3 scripts/check-doc-format.py
git diff --check
```

## Related documents

- [Fork Setup Guide](fork-setup.md)
- [Usage Guide](usage.md)
- [Demo Guide](demo.md)
- [Local Validation](local-validation.md)
