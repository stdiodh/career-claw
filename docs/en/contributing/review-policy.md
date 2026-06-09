# Maintainer Review Policy

> Language: [한국어](../../kr/contributing/review-policy.md) | [English](./review-policy.md)

This policy explains how maintainers review documentation, source suggestions, validation changes, and automation updates.

## Review principles

Prefer correctness, small diffs, reproducible checks, and clear scope. A smaller verified change is better than a broad untested rewrite.

## What maintainers look for

- Alignment with active workflows.
- No hardcoded secrets or unsafe URLs.
- Links and paths that stay inside the selected language tree.
- Updated validation when file locations change.

## Why suggestions may be declined

A suggestion may be declined when it is stale, hard to verify, out of scope, unsafe to automate, or too broad for the current release line.

## Automation review boundaries

Automation changes must preserve dry-run review, artifact validation, delivery locks, and disabled-by-default Discord delivery.

## Regional expansion review

New regions or languages need separate routing, clear source policy, and documentation paths. Do not mix language trees in quick-start flows.

## Documentation review

Documentation should be link-checkable, language-specific, and explicit about what is out of scope. Shared assets should remain under `docs/assets/**`.

## Security review

Any change touching Secrets, Discord delivery, API tokens, or workflow permissions needs careful review and relevant validation.

## Decision outcomes

Maintainers may merge, request changes, split a pull request, close as out of scope, or convert the proposal into a roadmap item.
