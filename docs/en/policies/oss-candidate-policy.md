# OSS Candidate Policy

> Language: [한국어](../../kr/policies/oss-candidate-policy.md) | [English](./oss-candidate-policy.md)

This policy defines when Career Feed may recommend an OSS issue as a safe first-contribution candidate.

## Purpose

The goal is to recommend safe, recent, beginner-friendly Java/Kotlin backend issues or render a preparation fallback when no safe issue exists.

## Recent issue rule

Issues must satisfy the configured `created_at` recency window. `CAREER_FEED_OSS_RECENT_DAYS` defaults to 30 when unset or invalid and is clamped to a safe maximum.

## Safe candidate requirements

A safe candidate is open, recent, unassigned, not already linked to active work, aligned with preferred contribution types, and backed by maintainer or beginner-friendly signals.

## Fallback behavior

When no safe candidate exists, the brief must not invent or force an issue URL. It should provide a preparation routine instead.

## Validation errors

Validation can reject issue URLs not found in safe candidates, fallback sections that still contain issue URLs, missing recency evidence, or unsafe candidate metadata.

## Maintainer checklist

- Confirm repository profile.
- Confirm recency.
- Confirm no linked work.
- Confirm allowed contribution type.
- Confirm fallback output is issue-free when needed.
