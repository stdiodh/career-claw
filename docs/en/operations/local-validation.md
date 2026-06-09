# Local Validation

> Language: [한국어](../../kr/operations/local-validation.md) | [English](./local-validation.md)

Run local validation before opening or updating pull requests whenever possible.

## Recommended command

```bash
./scripts/validate.sh
```

## Documentation checks

For docs-only changes, run:

```bash
python3 scripts/check-doc-format.py
git diff --check
```

## Fixture checks

The full validation script runs valid and invalid fixtures for daily backend, daily news, OSS reliability, schedule checks, and weekly career radar behavior.

## Generated reports

Validation may generate files under `reports/`. Do not commit those generated reports unless a maintainer explicitly asks for them.

## Troubleshooting

If validation fails, read the first failing section name, reproduce the smallest command if possible, fix the scoped issue, and re-run the relevant check.
