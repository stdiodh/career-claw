#!/usr/bin/env python3
"""Build a capped runtime prompt for AI_LIGHT_MODE."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MAX_ITEMS_PER_CATEGORY = 5
MAX_TITLE_LENGTH = 140
MAX_SUMMARY_LENGTH = 160
MAX_REFERENCE_LENGTH = 500
MAX_PROMPT_LENGTH = 8000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build compact AI input prompt.")
    parser.add_argument("--channels", default="configs/channels.json")
    parser.add_argument("--prompt-template", default=".github/codex/prompts/compact-brief.md")
    parser.add_argument("--output", required=True)
    parser.add_argument("--category", default="all")
    parser.add_argument("--max-items", type=int, default=3)
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="Include disabled channels when a specific category is requested.",
    )
    return parser.parse_args()


def truncate_text(value: str, limit: int) -> str:
    cleaned = " ".join((value or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: max(limit - 3, 0)].rstrip()}..."


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
        if channel.get("include_in_ai") is False:
            continue
        if not str(channel.get("candidate_file", "")).strip():
            continue
        enabled = bool(channel.get("enabled", False))
        if not enabled and not include_disabled:
            continue
        selected.append(channel)
    return selected


def read_reference(path: Path) -> str:
    if not path.exists():
        return "참조 문서 없음"
    return truncate_text(path.read_text(encoding="utf-8"), MAX_REFERENCE_LENGTH)


def load_limited_candidates(path: Path, category: str, max_items: int) -> dict[str, object]:
    if not path.exists():
        return {"category": category, "generated_at": "", "items": []}

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        items = []

    limited_items = []
    for item in items[: min(max_items, MAX_ITEMS_PER_CATEGORY)]:
        if not isinstance(item, dict):
            continue
        limited_items.append(
            {
                "title": truncate_text(str(item.get("title", "")), MAX_TITLE_LENGTH),
                "url": str(item.get("url", "")),
                "source": str(item.get("source", "")),
                "published_at": str(item.get("published_at", "")),
                "summary": truncate_text(str(item.get("summary", "")), MAX_SUMMARY_LENGTH),
                "score": item.get("score", 0),
            }
        )

    return {
        "category": category,
        "generated_at": str(data.get("generated_at", "")),
        "items": limited_items,
    }


def build_category_block(channel: dict[str, object], max_items: int) -> tuple[str, int]:
    category = str(channel.get("id", "")).strip()
    name = str(channel.get("name", category)).strip()
    reference_path = Path(str(channel.get("reference", "")))
    candidate_path = Path(str(channel.get("candidate_file", "")))
    brief_path = str(channel.get("brief_file", "")).strip()
    capped_max_items = min(max_items, MAX_ITEMS_PER_CATEGORY)

    reference = read_reference(reference_path)
    candidates = load_limited_candidates(candidate_path, category, capped_max_items)
    candidate_json = json.dumps(candidates, ensure_ascii=False, separators=(",", ":"))

    block = f"""## Category: {category}

Category name: {name}
Target file: {brief_path}
Max items: {capped_max_items}

### Reference
{reference}

### Candidate JSON
```json
{candidate_json}
```
"""
    return block, len(block)


def build_prompt(template: str, channels: list[dict[str, object]], max_items: int) -> tuple[str, dict[str, int]]:
    sizes: dict[str, int] = {}
    blocks = []
    for channel in channels:
        block, size = build_category_block(channel, max_items)
        category = str(channel.get("id", "")).strip()
        sizes[category] = size
        blocks.append(block)

    runtime = f"""{template.strip()}

## Runtime instructions

아래 입력만 사용해서 AI_LIGHT_MODE 브리핑을 작성한다.

- 각 Category의 Target file 경로에 최종 Markdown을 저장한다.
- Target file 외의 파일은 수정하지 않는다.
- 카테고리별 출력은 1200자 이하로 유지한다.
- 후보 JSON에 없는 사실은 쓰지 않는다.
- 웹 검색, live search, 외부 URL 확인을 하지 않는다.
- 작업이 끝나면 생성한 Target file 목록만 짧게 보고한다.

## Runtime input

{chr(10).join(blocks)}
"""
    return runtime, sizes


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)

    try:
        channels = load_channels(Path(args.channels), args.category, args.include_disabled)
        if not channels:
            raise RuntimeError("No channels selected for AI input.")
        template = Path(args.prompt_template).read_text(encoding="utf-8")
        prompt, sizes = build_prompt(template, channels, args.max_items)
        if len(prompt) >= MAX_PROMPT_LENGTH:
            largest = sorted(sizes.items(), key=lambda item: item[1], reverse=True)
            details = ", ".join(f"{category}={size}" for category, size in largest)
            raise RuntimeError(
                f"Runtime prompt is too large: {len(prompt)} chars. Category sizes: {details}"
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(prompt, encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to build AI input: {exc}", file=sys.stderr)
        return 1

    print(f"Runtime prompt written: {output_path}")
    print(f"Runtime prompt size: {len(prompt)} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
