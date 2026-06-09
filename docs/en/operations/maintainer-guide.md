# Maintainer Guide

> Language: [한국어](../../kr/operations/maintainer-guide.md) | [English](./maintainer-guide.md)

This guide lists recurring maintainer checks for the current Career Feed scope.

## Daily checks

- Confirm scheduled workflows are not repeatedly failing.
- Review validation errors before enabling delivery changes.
- Check sparse or no-candidate states before treating them as failures.

## Release checks

Use [Release Checklist](../project/release-checklist.md) and the shared [v0.2 release checklist](../../project/release-checklist.md). Verify docs, validation, issue templates, compatibility notes, and README status before tagging.

## Secrets safety checklist

- Secrets exist only in GitHub Secrets or local environment variables.
- Logs and docs do not expose real values.
- Discord delivery remains disabled unless intentionally enabled.

## Review boundaries

Keep reviews focused on active workflows and current release scope. Move large future ideas to roadmap discussion.

For v0.2.x, preserve `ko-KR` fallback behavior and describe `en-US` as foundation/experimental unless implementation evidence changes.

## OSS candidate review

Check recency, assignment, linked work, beginner labels, contribution type, and fallback behavior. Do not recommend stale or claimed issues.
