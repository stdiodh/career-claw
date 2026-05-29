#!/usr/bin/env python3
"""Check Career Feed workflow trigger and schedule guards."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DAILY_WORKFLOW = Path(".github/workflows/kr-tech-daily.yml")
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
    cron: str,
    secret: str,
    concurrency_group: str,
) -> None:
    text = read_required(path)
    if not has_quoted_value(text, "cron", cron):
        fail(f"{path}: missing schedule cron: {cron}")
    if not has_quoted_value(text, "timezone", "Asia/Seoul"):
        fail(f"{path}: missing schedule timezone: Asia/Seoul")
    require_contains(text, "workflow_dispatch:", path)
    require_contains(text, secret, path)
    require_contains(text, "validate-career-feed-brief.py", path)
    require_contains(text, "Log workflow trigger context", path)
    require_contains(text, "EVENT_NAME: ${{ github.event_name }}", path)
    require_contains(text, "EVENT_SCHEDULE: ${{ github.event.schedule }}", path)
    require_contains(text, "kst_now=$(TZ=Asia/Seoul date", path)
    require_contains(text, "Wait until 09:00 KST before Discord send", path)
    require_contains(text, "if: github.event_name == 'schedule'", path)
    require_contains(text, 'now_epoch="$(TZ=Asia/Seoul date +%s)"', path)
    require_contains(
        text,
        'target_epoch="$(TZ=Asia/Seoul date -d "${today_kst} 09:00:00" +%s)"',
        path,
    )
    require_contains(text, 'sleep "${wait_seconds}"', path)
    require_contains(text, "concurrency:", path)
    require_contains(text, f"group: {concurrency_group}", path)
    require_contains(text, "cancel-in-progress: false", path)
    require_absent(text, "DISCORD_WEBHOOK_KR_" "PREMIUM_BRIEF", path)
    require_absent(text, "validate-kr-" "premium-brief.py", path)
    print(f"ok: {label} schedule = {cron} Asia/Seoul")


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
            cron="5 8 * * 1-5",
            secret="DISCORD_WEBHOOK_KR_TECH_DAILY",
            concurrency_group="career-feed-kr-tech-daily-${{ github.ref }}",
        )
        check_weekly_site_radar_workflow()
        check_mark_ps_workflow()
    except RuntimeError as exc:
        print(f"schedule guard failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
