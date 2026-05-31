#!/usr/bin/env python3
"""Estimate News Daily prompt and shortlist token budget."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
DEFAULT_PROMPT_FILE = Path(".github/codex/prompts/kr-tech-news-daily.md")
DEFAULT_SHORTLIST_FILE = Path("reports/candidates/kr-tech-news-shortlist.json")
DEFAULT_OUTPUT_FILE = Path("reports/ops/news-daily-token-budget.json")
DEFAULT_REPORT_FILE = Path("reports/briefs/kr-tech-news-daily.md")
DEFAULT_RAW_CANDIDATE_FILES = [
    Path("reports/candidates/kr-dev-ai-news.json"),
    Path("reports/candidates/kr-ai-tech-news.json"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, default=DEFAULT_PROMPT_FILE)
    parser.add_argument("--shortlist-file", type=Path, default=DEFAULT_SHORTLIST_FILE)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--report-file", type=Path, default=DEFAULT_REPORT_FILE)
    parser.add_argument(
        "--raw-candidate-file",
        action="append",
        type=Path,
        default=[],
        help="Raw candidate JSON file to count. Defaults to the two News Daily candidate files.",
    )
    parser.add_argument("--kst-now", default="")
    return parser.parse_args()


def now_kst() -> str:
    return datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S KST")


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def item_count(path: Path) -> int:
    payload = read_json_object(path)
    candidate_count = payload.get("candidate_count")
    if isinstance(candidate_count, int):
        return candidate_count
    items = payload.get("items", [])
    return len(items) if isinstance(items, list) else 0


def shortlist_count(path: Path) -> int:
    payload = read_json_object(path)
    count = payload.get("shortlist_count")
    if isinstance(count, int):
        return count
    items = payload.get("items", [])
    return len(items) if isinstance(items, list) else 0


def runtime_context(
    kst_now: str,
    shortlist_file: Path,
    report_file: Path,
    raw_candidate_files: list[Path],
) -> str:
    fallback_files = "\n".join(f"- {path}" for path in raw_candidate_files)
    return (
        "\n\n## Runtime Context\n\n"
        f"- KST_NOW: {kst_now}\n"
        f"- SHORTLIST_FILE: {shortlist_file}\n"
        f"- OUTPUT_FILE: {report_file}\n"
        "- FALLBACK_CANDIDATE_FILES:\n"
        f"{fallback_files}\n"
    )


def rough_tokens(chars: int) -> int:
    return max(1, math.ceil(chars / 3))


def main() -> int:
    args = parse_args()
    raw_candidate_files = args.raw_candidate_file or DEFAULT_RAW_CANDIDATE_FILES
    kst_now = args.kst_now or now_kst()

    prompt_text = read_text_if_exists(args.prompt_file)
    context = runtime_context(
        kst_now,
        args.shortlist_file,
        args.report_file,
        raw_candidate_files,
    )
    runtime_prompt_text = prompt_text + context
    shortlist_text = read_text_if_exists(args.shortlist_file)
    estimated_prompt_chars = len(runtime_prompt_text) + len(shortlist_text)

    payload = {
        "generated_at_kst": now_kst(),
        "prompt_file": str(args.prompt_file),
        "shortlist_file": str(args.shortlist_file),
        "output_file": str(args.report_file),
        "runtime_prompt_chars": len(runtime_prompt_text),
        "runtime_prompt_bytes": len(runtime_prompt_text.encode("utf-8")),
        "shortlist_json_chars": len(shortlist_text),
        "shortlist_json_bytes": len(shortlist_text.encode("utf-8")),
        "raw_candidate_count_total": sum(item_count(path) for path in raw_candidate_files),
        "shortlist_count": shortlist_count(args.shortlist_file),
        "estimated_prompt_chars": estimated_prompt_chars,
        "estimated_prompt_tokens_rough": rough_tokens(estimated_prompt_chars),
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Wrote News Daily token budget "
        f"({payload['estimated_prompt_tokens_rough']} rough token(s)): {args.output_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
