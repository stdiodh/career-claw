# GitHub Labels

> Language: [한국어](../../kr/policies/github-labels.md) | [English](./github-labels.md)

Labels help contributors and maintainers triage issues without adding process overhead.

## Purpose

Use labels to clarify contribution type, review state, source category, and maintainer priority.

## Suggested labels

Labels are created manually by maintainers in GitHub. This repository documents suggested labels, but a docs-only PR does not create labels automatically.

Recommended labels include:

- `bug`
- `docs`
- `documentation`
- `locale`
- `provider`
- `workflow`
- `validation`
- `validation fixture`
- `source`
- `source-policy`
- `release`
- `release readiness`
- `good first issue`
- `help wanted`
- `oss-candidate`
- `question`
- `enhancement`

## Contributor labels

Contributor-facing labels should identify `good first issue`, `help wanted`, `source`, `provider`, `locale`, `oss-candidate`, `validation fixture`, `question`, and `documentation`.

## Maintainer labels

Maintainer labels may track duplicate, invalid, wontfix, release readiness, and issue type labels.

## Issue template mapping

| Template | Labels |
| --- | --- |
| Backend career question | `question` |
| Bug report | `bug` |
| Docs improvement | `documentation` |
| Source suggestion | `source`, `enhancement` |
| Broken link or outdated source | `source`, `bug` |
| OSS candidate suggestion | `oss-candidate` |
| Validation fixture | `validation fixture`, `good first issue` |
| Release readiness | `release readiness` |
| Regional or language expansion | `enhancement`, `source` |
| Other maintainer question | `question` |

## Review checklist

- Label name is clear.
- Label does not duplicate an existing concept.
- Label supports current workflows.
- Label can be applied consistently.
