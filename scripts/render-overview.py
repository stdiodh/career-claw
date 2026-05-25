#!/usr/bin/env python3
"""Render the free Daily Overview brief from candidate JSON files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, time as day_time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
BASE_HOUR = 9
BASE_MINUTE = 7
TITLE_LIMIT = 78
TARGET_LENGTH = 1000
OVERVIEW_CATEGORY_IDS = ("ai-news", "backend-news", "security-alerts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the Daily Overview brief.")
    parser.add_argument("--channels", default="configs/channels.json")
    return parser.parse_args()


def truncate_text(value: str, limit: int) -> str:
    cleaned = " ".join((value or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: max(limit - 3, 0)].rstrip()}..."


def load_channels(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    channels = data.get("channels", [])
    if not isinstance(channels, list):
        raise RuntimeError("configs/channels.json must contain a channels array.")
    return [channel for channel in channels if isinstance(channel, dict)]


def load_candidates(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def sort_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    def sort_key(item: dict[str, object]) -> tuple[int, str]:
        score = item.get("score", 0)
        if not isinstance(score, int):
            score = 0
        return score, str(item.get("published_at", ""))

    return sorted(items, key=sort_key, reverse=True)


def format_send_time(offset: int) -> str:
    today = datetime.now(tz=KST).date()
    base = datetime.combine(today, day_time(hour=BASE_HOUR, minute=BASE_MINUTE), tzinfo=KST)
    return (base + timedelta(minutes=offset)).strftime("%H:%M")


def render_overview(channels: list[dict[str, object]]) -> tuple[Path, str]:
    overview = next(
        (channel for channel in channels if str(channel.get("id", "")) == "daily-overview"),
        None,
    )
    if not overview:
        raise RuntimeError("daily-overview channel is missing.")

    channel_by_id = {str(channel.get("id", "")).strip(): channel for channel in channels}
    overview_channels = [
        channel_by_id[category_id]
        for category_id in OVERVIEW_CATEGORY_IDS
        if category_id in channel_by_id
    ]

    category_summaries: list[dict[str, object]] = []
    for channel in overview_channels:
        name = str(channel.get("name", "")).strip() or str(channel.get("id", ""))
        offset = int(channel.get("send_offset_minutes", 0))
        items = load_candidates(Path(str(channel.get("candidate_file", ""))))
        sorted_items = sort_items(items)
        representative = sorted_items[0] if sorted_items else None
        category_summaries.append(
            {
                "name": name,
                "count": len(items),
                "send_time": format_send_time(offset),
                "representative": representative,
            }
        )

    total_count = sum(int(summary["count"]) for summary in category_summaries)

    generated_at = datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M KST")
    lines = [
        "# Career Feed - Daily Overview",
        f"기준시각: {generated_at}",
        "",
        "## 오늘의 핵심 요약",
    ]

    if total_count:
        lines.append(f"- 오늘 확인된 주요 항목: 총 {total_count}개")
    else:
        lines.append("- 오늘 확인된 주요 항목이 없습니다.")

    lines.extend(["", "## 카테고리별 상태"])
    for summary in category_summaries:
        name = str(summary["name"])
        count = int(summary["count"])
        send_time = str(summary["send_time"])
        if count:
            lines.append(f"- {name}: {count}개 확인 / {send_time} 전송 예정")
        else:
            lines.append(f"- {name}: 오늘 확인된 주요 항목이 없습니다. / {send_time} 전송 예정")

    lines.extend(["", "## 대표 원본 URL"])
    for summary in category_summaries:
        name = str(summary["name"])
        representative = summary["representative"]
        if isinstance(representative, dict):
            title = truncate_text(str(representative.get("title", "")), TITLE_LIMIT) or "원문"
            url = str(representative.get("url", "")).strip()
            lines.append(f"- {name}: [{title}]({url})")
        else:
            lines.append(f"- {name}: 오늘 확인된 주요 항목이 없습니다.")

    markdown = "\n".join(lines).strip() + "\n"
    if len(markdown) > TARGET_LENGTH:
        compact_lines = lines[: lines.index("## 대표 원본 URL")]
        compact_lines.extend(["## 대표 원본 URL", "- 상세 원본 URL은 카테고리별 브리핑에서 확인합니다."])
        markdown = "\n".join(compact_lines).strip() + "\n"

    return Path(str(overview.get("brief_file", ""))), markdown


def main() -> int:
    args = parse_args()
    try:
        channels = load_channels(Path(args.channels))
        output_path, markdown = render_overview(channels)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote overview: {output_path}")
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to render overview: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
