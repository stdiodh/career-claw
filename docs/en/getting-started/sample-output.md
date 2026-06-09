# Sample Output

> Language: [한국어](../../kr/getting-started/sample-output.md) | [English](./sample-output.md)

This page shows small, reviewable examples of what Career Feed generates.

The samples are documentation examples. They are not live usage or adoption claims.

## Available Examples

| Output | File | Notes |
| --- | --- | --- |
| Daily Backend Brief | [daily-backend-brief.example.md](../examples/daily-backend-brief.example.md) | Daily backend learning, PS routine, OSS preparation, and practical knowledge example |
| Dev News Daily | [korea-dev-ai-news-daily.example.md](../examples/korea-dev-ai-news-daily.example.md) | Locale-specific developer and AI news review example |
| Backend Career Site Radar | [career-site-radar.example.md](../examples/career-site-radar.example.md) | Weekly career site radar example |

## What to Check

- Use only public URLs or obvious placeholders.
- Do not include Discord webhook URLs, API keys, tokens, credentials, or private channel names.
- Do not imply automatic comments, pull requests, assignments, or label changes on external repositories.
- Fallback output is acceptable when no safe OSS candidate exists.

## Adding a Sample

1. Use redacted or placeholder data.
2. Keep the sample small enough to review in a pull request.
3. State whether it is generated output, hand-written example output, or fixture output.
4. Link it only after the file exists.
5. Run documentation validation.

```bash
python3 scripts/check-doc-format.py
git diff --check
```

## Related Documents

- [Fork Setup Guide](fork-setup.md)
- [Usage Guide](usage.md)
- [Demo Guide](../demo.md)
- [Local Validation](../operations/local-validation.md)
