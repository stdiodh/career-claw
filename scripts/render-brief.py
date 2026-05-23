#!/usr/bin/env python3
"""Render short Markdown briefs from collected candidates."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
SUMMARY_LIMIT = 140
TITLE_LIMIT = 120
ORIGINAL_TITLE_LIMIT = 72
TARGET_MARKDOWN_LENGTH = 1200


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render free Markdown briefs.")
    parser.add_argument("--channels", default="configs/channels.json")
    parser.add_argument(
        "--category",
        default="all",
        help="Category id to render, or 'all'.",
    )
    return parser.parse_args()


def truncate_text(value: str, limit: int) -> str:
    cleaned = " ".join((value or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: max(limit - 3, 0)].rstrip()}..."


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=KST)
    return parsed.astimezone(KST)


def format_kst(value: str) -> str:
    parsed = parse_datetime(value)
    if not parsed:
        return "원문 확인 필요"
    return parsed.strftime("%Y-%m-%d %H:%M")


def load_channels(path: Path, category_filter: str) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    channels = data.get("channels", [])
    if not isinstance(channels, list):
        raise RuntimeError("configs/channels.json must contain a channels array.")
    if category_filter == "all":
        return [channel for channel in channels if isinstance(channel, dict)]
    return [
        channel
        for channel in channels
        if isinstance(channel, dict) and str(channel.get("id", "")) == category_filter
    ]


def load_candidates(path: Path, category: str) -> list[dict[str, object]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("category") != category:
        raise RuntimeError(f"Candidate file category mismatch: {path}")
    items = data.get("items", [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def sort_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    def sort_key(item: dict[str, object]) -> tuple[int, str]:
        score = item.get("score", 0)
        if not isinstance(score, int):
            score = 0
        published_at = str(item.get("published_at", ""))
        return score, published_at

    return sorted(items, key=sort_key, reverse=True)


def render_item(index: int, item: dict[str, object]) -> list[str]:
    title = truncate_text(str(item.get("title", "")).strip() or "제목 확인 필요", TITLE_LIMIT)
    url = str(item.get("url", "")).strip()
    summary = truncate_text(str(item.get("summary", "")).strip(), SUMMARY_LIMIT)
    if not summary:
        summary = "원문 확인 필요"
    source = str(item.get("source", "")).strip() or "출처 확인 필요"
    published = format_kst(str(item.get("published_at", "")))
    keywords = item.get("matched_keywords", [])
    if isinstance(keywords, list) and keywords:
        keyword_text = ", ".join(str(keyword) for keyword in keywords[:5])
    else:
        keyword_text = "없음"

    return [
        f"## {index}. [{title}]({url})",
        f"- 요약: {summary}",
        f"- 출처: {source}",
        f"- 발행: {published}",
        f"- 키워드: {keyword_text}",
    ]


def trim_markdown(markdown: str) -> str:
    if len(markdown) <= TARGET_MARKDOWN_LENGTH:
        return markdown

    lines = markdown.splitlines()
    trimmed = []
    for line in lines:
        if line.startswith("- 요약: "):
            line = truncate_text(line, 84)
        trimmed.append(line)
    return "\n".join(trimmed).strip() + "\n"


def render_brief(channel: dict[str, object], items: list[dict[str, object]]) -> str:
    name = str(channel.get("name", "")).strip() or str(channel.get("id", "")).strip()
    max_items = int(channel.get("max_items", 3))
    selected = sort_items(items)[:max_items]
    generated_at = datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M KST")

    lines = [
        f"# Career Feed - {name}",
        "",
        f"기준시각: {generated_at}",
        "",
    ]

    if not selected:
        lines.extend(["오늘 확인된 주요 항목이 없습니다.", ""])
        return "\n".join(lines).strip() + "\n"

    for index, item in enumerate(selected, start=1):
        lines.extend(render_item(index, item))
        lines.append("")

    lines.append("## 원본 보기")
    for item in selected:
        title = truncate_text(str(item.get("title", "")).strip() or "원문", ORIGINAL_TITLE_LIMIT)
        url = str(item.get("url", "")).strip()
        lines.append(f"- [{title}]({url})")

    return trim_markdown("\n".join(lines).strip() + "\n")


def main() -> int:
    args = parse_args()
    try:
        channels = load_channels(Path(args.channels), args.category)
        for channel in channels:
            category = str(channel.get("id", "")).strip()
            candidate_file = Path(str(channel.get("candidate_file", "")))
            brief_file = Path(str(channel.get("brief_file", "")))
            items = load_candidates(candidate_file, category)
            markdown = render_brief(channel, items)
            brief_file.parent.mkdir(parents=True, exist_ok=True)
            brief_file.write_text(markdown, encoding="utf-8")
            print(f"Wrote brief: {brief_file}")
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to render brief: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
