#!/usr/bin/env python3
"""Check Career Feed workflow trigger and schedule guards."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DAILY_WORKFLOW = Path(".github/workflows/kr-tech-daily.yml")
NEWS_DAILY_WORKFLOW = Path(".github/workflows/kr-tech-news-daily.yml")
WEEKLY_WORKFLOW = Path(".github/workflows/kr-backend-career-weekly.yml")
MARK_PS_WORKFLOW = Path(".github/workflows/mark-ps-solved.yml")

REMOVED_WORKFLOWS = [
    Path(".github/workflows/ai-brief-" "manual.yml"),
    Path(".github/workflows/daily-" "feed.yml"),
    Path(".github/workflows/daily-" "news.yml"),
    Path(".github/workflows/kr-" "premium-brief.yml"),
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_required(path: Path) -> str:
    if not path.exists():
        fail(f"missing workflow file: {path}")
    return path.read_text(encoding="utf-8")


def has_quoted_value(text: str, key: str, value: str) -> bool:
    pattern = rf"{re.escape(key)}\s*:\s*(['\"]){re.escape(value)}\1"
    return bool(re.search(pattern, text))


def require_contains(text: str, needle: str, path: Path) -> None:
    if needle not in text:
        fail(f"{path}: missing required text: {needle}")


def require_absent(text: str, needle: str, path: Path) -> None:
    if needle in text:
        fail(f"{path}: forbidden text found: {needle}")


def check_scheduled_workflow(
    path: Path,
    *,
    label: str,
    crons: list[str],
    secret: str,
    forbidden_secret: str,
    concurrency_group: str,
    lock_key_prefix: str,
    content_permission: str,
    wait_step_name: str,
    wait_time: str,
    collector_mode: str,
    validator_type: str,
    requires_ps_progress_commit: bool = False,
) -> None:
    text = read_required(path)
    for cron in crons:
        if not has_quoted_value(text, "cron", cron):
            fail(f"{path}: missing schedule cron: {cron}")
    if not has_quoted_value(text, "timezone", "Asia/Seoul"):
        fail(f"{path}: missing schedule timezone: Asia/Seoul")
    require_contains(text, "workflow_dispatch:", path)
    require_contains(text, "dry_run:", path)
    require_contains(text, "force_send:", path)
    require_contains(text, secret, path)
    require_absent(text, forbidden_secret, path)
    require_contains(text, "validate-career-feed-brief.py", path)
    require_contains(text, f"--type {validator_type}", path)
    require_contains(text, f"collect-kr-feeds.py --mode {collector_mode}", path)
    require_contains(text, "EVENT_NAME: ${{ github.event_name }}", path)
    require_contains(text, "EVENT_SCHEDULE: ${{ github.event.schedule }}", path)
    require_contains(text, "delivery_lock_key=", path)
    require_contains(text, lock_key_prefix, path)
    require_contains(text, "actions/cache/restore@v4", path)
    require_contains(text, "actions/cache/save@v4", path)
    require_contains(text, "should_send", path)
    require_contains(text, "dry_run", path)
    require_contains(text, "force_send", path)
    require_contains(text, wait_step_name, path)
    require_contains(
        text,
        "if: github.event_name == 'schedule' && steps.delivery.outputs.should_send == 'true'",
        path,
    )
    require_contains(text, 'now_epoch="$(TZ=Asia/Seoul date +%s)"', path)
    require_contains(
        text,
        f'target_epoch="$(TZ=Asia/Seoul date -d "${{today_kst}} {wait_time}" +%s)"',
        path,
    )
    require_contains(text, 'sleep "${wait_seconds}"', path)
    require_contains(text, "concurrency:", path)
    require_contains(text, f"group: {concurrency_group}", path)
    require_contains(text, "cancel-in-progress: false", path)
    require_contains(text, "timeout-minutes: 75", path)
    require_contains(text, f"contents: {content_permission}", path)
    require_contains(text, "actions: read", path)
    if content_permission == "read":
        require_absent(text, "contents: write", path)
    if requires_ps_progress_commit:
        require_contains(text, "persist-credentials: true", path)
        require_contains(text, "Commit Programmers assignment progress", path)
        require_contains(text, "commit-ps-progress", path)
        require_contains(text, "data/ps-progress.json", path)
        require_contains(text, "git push", path)
    else:
        require_absent(text, "Commit Programmers assignment progress", path)
        require_absent(text, "data/ps-progress.json", path)
        require_absent(text, "git push", path)
    require_contains(text, "if: always()", path)
    require_contains(text, "retention-days: 14", path)
    require_contains(text, "DISCORD_WEBHOOK_CAREER_FEED_OPS", path)
    require_absent(text, "DISCORD_WEBHOOK_KR_" "PREMIUM_BRIEF", path)
    require_absent(text, "validate-kr-" "premium-brief.py", path)
    print(f"ok: {label} schedules = {', '.join(crons)} Asia/Seoul")


def check_mark_ps_workflow() -> None:
    text = read_required(MARK_PS_WORKFLOW)
    require_contains(text, "workflow_dispatch:", MARK_PS_WORKFLOW)
    require_absent(text, "schedule:", MARK_PS_WORKFLOW)
    require_absent(text, "cron:", MARK_PS_WORKFLOW)
    print("ok: Mark PS Solved has workflow_dispatch only")


def check_weekly_site_radar_workflow() -> None:
    text = read_required(WEEKLY_WORKFLOW)
    require_contains(text, "workflow_dispatch:", WEEKLY_WORKFLOW)
    require_contains(text, "Backend Career Site Radar", WEEKLY_WORKFLOW)
    require_contains(text, "permissions:", WEEKLY_WORKFLOW)
    require_contains(text, "contents: read", WEEKLY_WORKFLOW)
    require_contains(text, "send_to_discord", WEEKLY_WORKFLOW)
    require_contains(text, "DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY", WEEKLY_WORKFLOW)
    require_contains(text, "render-weekly-career-site-radar.py", WEEKLY_WORKFLOW)
    require_contains(text, "validate-career-feed-brief.py", WEEKLY_WORKFLOW)
    require_contains(
        text,
        "group: career-feed-backend-career-site-radar-${{ github.ref }}",
        WEEKLY_WORKFLOW,
    )
    require_absent(text, "schedule:", WEEKLY_WORKFLOW)
    require_absent(text, "cron:", WEEKLY_WORKFLOW)
    require_absent(text, "openai/codex-action", WEEKLY_WORKFLOW)
    require_absent(text, "OPENAI_API_KEY", WEEKLY_WORKFLOW)
    require_absent(text, "NAVER_CLIENT_ID", WEEKLY_WORKFLOW)
    require_absent(text, "NAVER_CLIENT_SECRET", WEEKLY_WORKFLOW)
    require_absent(text, "git commit", WEEKLY_WORKFLOW)
    print("ok: Backend Career Site Radar has workflow_dispatch only")


def check_removed_workflows_absent() -> None:
    existing = [str(path) for path in REMOVED_WORKFLOWS if path.exists()]
    if existing:
        fail(f"removed workflow file(s) must not exist: {', '.join(existing)}")


def main() -> int:
    try:
        check_removed_workflows_absent()
        check_scheduled_workflow(
            DAILY_WORKFLOW,
            label="Daily Backend Brief",
            crons=["5 8 * * 1-5", "25 9 * * 1-5"],
            secret="DISCORD_WEBHOOK_KR_TECH_DAILY",
            forbidden_secret="DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY",
            concurrency_group="career-feed-backend-daily-${{ github.ref }}",
            lock_key_prefix="career-feed-backend-sent-",
            content_permission="write",
            wait_step_name="Wait until 09:00 KST before Discord send",
            wait_time="09:00:00",
            collector_mode="daily-backend",
            validator_type="daily-tech",
            requires_ps_progress_commit=True,
        )
        check_scheduled_workflow(
            NEWS_DAILY_WORKFLOW,
            label="Daily Korea Dev AI News",
            crons=["15 8 * * 1-5", "30 9 * * 1-5"],
            secret="DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY",
            forbidden_secret="DISCORD_WEBHOOK_KR_TECH_DAILY",
            concurrency_group="career-feed-news-daily-${{ github.ref }}",
            lock_key_prefix="career-feed-news-sent-",
            content_permission="read",
            wait_step_name="Wait until 09:05 KST before Discord send",
            wait_time="09:05:00",
            collector_mode="daily-news",
            validator_type="daily-news",
        )
        check_weekly_site_radar_workflow()
        check_mark_ps_workflow()
    except RuntimeError as exc:
        print(f"schedule guard failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
