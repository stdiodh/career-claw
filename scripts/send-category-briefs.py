#!/usr/bin/env python3
"""Send category Markdown briefs to their configured Discord webhooks."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, time as day_time, timedelta
from pathlib import Path
from types import ModuleType
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
DEFAULT_BASE_HOUR = 9
DEFAULT_BASE_MINUTE = 7


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send configured category briefs.")
    parser.add_argument("--channels", default="configs/channels.json")
    parser.add_argument(
        "--category",
        default="all",
        help="Category id to send, or 'all'.",
    )
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="Allow explicitly selected disabled channels to be sent.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate files and chunks without sending Discord messages.",
    )
    return parser.parse_args()


def load_send_discord_module() -> ModuleType:
    script_path = Path(__file__).with_name("send-discord.py")
    spec = importlib.util.spec_from_file_location("send_discord", script_path)
    if not spec or not spec.loader:
        raise RuntimeError("Failed to load scripts/send-discord.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_channels(path: Path, category_filter: str, include_disabled: bool) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    channels = data.get("channels", [])
    if not isinstance(channels, list):
        raise RuntimeError("configs/channels.json must contain a channels array.")

    selected = []
    for channel in channels:
        if not isinstance(channel, dict):
            continue
        category = str(channel.get("id", "")).strip()
        if category_filter != "all" and category != category_filter:
            continue
        enabled = bool(channel.get("enabled", False))
        if not enabled and not include_disabled:
            print(f"Skipping disabled channel: {category}")
            continue
        selected.append(channel)

    return sorted(selected, key=lambda item: int(item.get("send_offset_minutes", 0)))


def scheduled_datetime(offset_minutes: int) -> datetime:
    now = datetime.now(tz=KST)
    base = datetime.combine(
        now.date(),
        day_time(hour=DEFAULT_BASE_HOUR, minute=DEFAULT_BASE_MINUTE),
        tzinfo=KST,
    )
    return base + timedelta(minutes=offset_minutes)


def wait_for_schedule(channel: dict[str, object], base_has_passed: bool) -> None:
    if base_has_passed:
        return
    offset = int(channel.get("send_offset_minutes", 0))
    target = scheduled_datetime(offset)
    now = datetime.now(tz=KST)
    wait_seconds = (target - now).total_seconds()
    if wait_seconds > 0:
        print(f"Waiting {wait_seconds:.0f}s before sending {channel.get('id')}.")
        time.sleep(wait_seconds)


def read_brief(send_discord: ModuleType, path: Path) -> str:
    return send_discord.read_markdown(path)


def send_channel(send_discord: ModuleType, channel: dict[str, object], dry_run: bool) -> tuple[bool, str]:
    category = str(channel.get("id", "")).strip()
    brief_file = Path(str(channel.get("brief_file", "")))
    webhook_env = str(channel.get("webhook_env", "")).strip()

    try:
        content = read_brief(send_discord, brief_file)
        chunks = send_discord.chunk_markdown(content)
        if dry_run:
            return True, f"{category}: dry-run validated {len(chunks)} chunk(s)"

        webhook_url = os.environ.get(webhook_env, "").strip()
        if not webhook_url:
            return False, f"{category}: missing required environment variable {webhook_env}"

        sent_count = send_discord.send_to_discord(webhook_url, chunks)
        return True, f"{category}: sent {sent_count} chunk(s)"
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        return False, f"{category}: {exc}"


def main() -> int:
    args = parse_args()
    try:
        send_discord = load_send_discord_module()
        channels = load_channels(Path(args.channels), args.category, args.include_disabled)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to prepare category sending: {exc}", file=sys.stderr)
        return 1

    if not channels:
        print("No channels selected for sending.")
        return 0

    now = datetime.now(tz=KST)
    base = datetime.combine(
        now.date(),
        day_time(hour=DEFAULT_BASE_HOUR, minute=DEFAULT_BASE_MINUTE),
        tzinfo=KST,
    )
    base_has_passed = args.dry_run or now >= base

    results: list[tuple[bool, str]] = []
    for channel in channels:
        wait_for_schedule(channel, base_has_passed)
        ok, message = send_channel(send_discord, channel, args.dry_run)
        print(message)
        results.append((ok, message))

    failed = [message for ok, message in results if not ok]
    if failed:
        print("Category send completed with failures:", file=sys.stderr)
        for message in failed:
            print(f"- {message}", file=sys.stderr)
        return 1

    print("Category send completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
