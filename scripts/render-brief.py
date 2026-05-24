#!/usr/bin/env python3
"""Render short Markdown briefs from collected candidates."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
SUMMARY_LIMIT = 100
TITLE_LIMIT = 68
TOP_TITLE_LIMIT = 48
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
        return [
            channel
            for channel in channels
            if isinstance(channel, dict) and str(channel.get("candidate_file", "")).strip()
        ]
    return [
        channel
        for channel in channels
        if (
            isinstance(channel, dict)
            and str(channel.get("id", "")) == category_filter
            and str(channel.get("candidate_file", "")).strip()
        )
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
    summary = truncate_text(str(item.get("summary", "")).strip(), SUMMARY_LIMIT)
    if not summary:
        summary = "원문 확인 필요"
    source = str(item.get("source", "")).strip() or "출처 확인 필요"
    published = format_kst(str(item.get("published_at", "")))
    reason = build_reason(str(item.get("category", "")), item)

    return [
        f"## {index}. {title}",
        f"- 핵심: {summary}",
        f"- 왜 봐야 함: {reason}",
        f"- 출처: {source} / {published}",
    ]


def item_keywords(item: dict[str, object]) -> set[str]:
    keywords = item.get("matched_keywords", [])
    values = {str(keyword).lower() for keyword in keywords if str(keyword).strip()} if isinstance(keywords, list) else set()
    searchable = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    for token in re.split(r"[^a-z0-9.+#-]+", searchable):
        if token:
            values.add(token)
    return values


def build_reason(category: str, item: dict[str, object]) -> str:
    keywords = item_keywords(item)
    if category == "security-alerts" and keywords & {"cve", "patch", "advisory", "vulnerability", "critical"}:
        return "패치 또는 영향 범위 확인이 필요합니다."
    if category == "backend-news" and keywords & {"release", "lts", "migration", "breaking", "upgrade"}:
        return "업그레이드/마이그레이션 영향 확인이 필요합니다."
    if category == "ai-news" and keywords & {"api", "sdk", "agent", "coding", "copilot", "developer"}:
        return "개발 워크플로 또는 API 사용 방식 변화 확인이 필요합니다."
    if category == "backend-tech":
        return "학습 또는 도입 후보로 볼 만한지 원문 확인이 필요합니다."
    if category == "job-feed":
        return "지원 조건과 성장 가능성 확인이 필요합니다."
    return "실무 영향 여부를 원문에서 확인할 필요가 있습니다."


def trim_markdown(markdown: str) -> str:
    if len(markdown) <= TARGET_MARKDOWN_LENGTH:
        return markdown

    lines = markdown.splitlines()
    trimmed = []
    for line in lines:
        if line.startswith("- 핵심: "):
            line = truncate_text(line, 68)
        if line.startswith("- 왜 봐야 함: "):
            line = truncate_text(line, 52)
        trimmed.append(line)
    return "\n".join(trimmed).strip() + "\n"


def build_brief_markdown(
    name: str,
    generated_at: str,
    selected: list[dict[str, object]],
) -> str:
    lines = [
        f"# Career Feed - {name}",
        f"기준시각: {generated_at}",
        "",
    ]

    if not selected:
        lines.extend(
            [
                "오늘 확인된 주요 항목이 없습니다.",
                "",
                "## 원본 보기",
                "- 오늘은 확인할 원본 링크가 없습니다.",
            ]
        )
        return "\n".join(lines).strip() + "\n"

    lines.extend(
        [
            "오늘의 요약:",
            f"- 총 {len(selected)}개 항목",
            f"- 가장 먼저 볼 항목: {truncate_text(str(selected[0].get('title', '')), TOP_TITLE_LIMIT)}",
            "",
        ]
    )

    for index, item in enumerate(selected, start=1):
        lines.extend(render_item(index, item))
        lines.append("")

    lines.append("## 원본 보기")
    for index, item in enumerate(selected, start=1):
        url = str(item.get("url", "")).strip()
        lines.append(f"- [원문 {index}]({url})")

    return "\n".join(lines).strip() + "\n"


def render_brief(channel: dict[str, object], items: list[dict[str, object]]) -> str:
    name = str(channel.get("name", "")).strip() or str(channel.get("id", "")).strip()
    max_items = int(channel.get("max_items", 3))
    category = str(channel.get("id", "")).strip()
    selected = [dict(item, category=category) for item in sort_items(items)[:max_items]]
    generated_at = datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M KST")

    if not selected:
        return build_brief_markdown(name, generated_at, selected)

    for item_count in range(len(selected), 0, -1):
        markdown = trim_markdown(build_brief_markdown(name, generated_at, selected[:item_count]))
        if len(markdown) <= TARGET_MARKDOWN_LENGTH or item_count == 1:
            return markdown

    return build_brief_markdown(name, generated_at, [])


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
