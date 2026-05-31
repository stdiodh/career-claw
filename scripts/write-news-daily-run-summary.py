#!/usr/bin/env python3
"""Write News Daily run summary artifacts."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
DEFAULT_REPORT_FILE = Path("reports/briefs/kr-tech-news-daily.md")
DEFAULT_SHORTLIST_FILE = Path("reports/candidates/kr-tech-news-shortlist.json")
DEFAULT_BUDGET_FILE = Path("reports/ops/news-daily-token-budget.json")
DEFAULT_OUTPUT_JSON = Path("reports/ops/news-daily-run-summary.json")
DEFAULT_OUTPUT_MD = Path("reports/ops/news-daily-run-summary.md")
DEFAULT_RAW_CANDIDATE_FILES = [
    Path("reports/candidates/kr-dev-ai-news.json"),
    Path("reports/candidates/kr-ai-tech-news.json"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-file", type=Path, default=DEFAULT_REPORT_FILE)
    parser.add_argument("--shortlist-file", type=Path, default=DEFAULT_SHORTLIST_FILE)
    parser.add_argument("--budget-file", type=Path, default=DEFAULT_BUDGET_FILE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--raw-candidate-file",
        action="append",
        type=Path,
        default=[],
        help="Raw candidate JSON file to count. Defaults to the two News Daily candidate files.",
    )
    return parser.parse_args()


def now_kst() -> str:
    return datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S KST")


def read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def raw_candidate_stats(paths: list[Path]) -> tuple[int, set[str]]:
    total = 0
    source_errors: set[str] = set()
    for path in paths:
        data = read_json_object(path)
        items = data.get("items", [])
        fallback_count = len(items) if isinstance(items, list) else 0
        try:
            total += int(data.get("candidate_count", fallback_count) or 0)
        except (TypeError, ValueError):
            total += fallback_count
        errors = data.get("source_errors", [])
        if isinstance(errors, list):
            for error in errors:
                source_errors.add(json.dumps(error, ensure_ascii=False, sort_keys=True))
    return total, source_errors


def section_body(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        flags=re.MULTILINE,
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def section_item_count(markdown: str, heading: str) -> int:
    body = section_body(markdown, heading)
    if not body:
        return 0
    return len(re.findall(r"^###\s+\d+\.\s+", body, flags=re.MULTILINE))


def growth_score(markdown: str) -> int:
    match = re.search(r"^\s*-\s*도움\s*점수\s*:\s*([1-5])\s*$", markdown, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def growth_action_present(markdown: str) -> bool:
    match = re.search(
        r"^\s*-\s*오늘\s*할\s*일\s*1개\s*:\s*(.+?)\s*$",
        markdown,
        flags=re.MULTILINE,
    )
    return bool(match and match.group(1).strip())


def track_count(shortlist: dict[str, object], track: str) -> int:
    explicit = shortlist.get(f"{track}_shortlist_count")
    if isinstance(explicit, int):
        return explicit
    tracks = shortlist.get("tracks", {})
    if not isinstance(tracks, dict):
        return 0
    track_payload = tracks.get(track, {})
    if not isinstance(track_payload, dict):
        return 0
    items = track_payload.get("items", [])
    return len(items) if isinstance(items, list) else 0


def fallback_reason(markdown: str, selected_count: int, skip_reason: str) -> str | None:
    if skip_reason:
        return skip_reason
    if selected_count == 0 and "기준을 만족하는 한국 개발/AI 뉴스가 없습니다" in markdown:
        return "no_qualified_news"
    if 0 < selected_count < 3:
        return "sparse_qualified_news"
    return None


def main() -> int:
    args = parse_args()
    raw_candidate_files = args.raw_candidate_file or DEFAULT_RAW_CANDIDATE_FILES
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)

    raw_count, source_errors = raw_candidate_stats(raw_candidate_files)
    shortlist = read_json_object(args.shortlist_file)
    budget = read_json_object(args.budget_file)
    report = args.report_file.read_text(encoding="utf-8") if args.report_file.exists() else ""

    shortlist_items = shortlist.get("items", [])
    shortlist_count = int(
        shortlist.get(
            "shortlist_count",
            len(shortlist_items) if isinstance(shortlist_items, list) else 0,
        )
        or 0
    )
    for error in shortlist.get("source_errors", []) if isinstance(shortlist.get("source_errors", []), list) else []:
        source_errors.add(json.dumps(error, ensure_ascii=False, sort_keys=True))

    tech_selected_count = section_item_count(report, "새 기술 이야기")
    investment_selected_count = section_item_count(report, "주식/투자 이야기")
    selected_news_count = tech_selected_count + investment_selected_count
    bridge_body = section_body(report, "기술과 시장 연결")
    summary = {
        "feed": "news-daily",
        "generated_at_kst": now_kst(),
        "event_name": os.environ.get("EVENT_NAME", ""),
        "schedule": os.environ.get("EVENT_SCHEDULE", ""),
        "dry_run": os.environ.get("DRY_RUN") == "true",
        "force_send": os.environ.get("FORCE_SEND") == "true",
        "delivery_lock_key": os.environ.get("DELIVERY_LOCK_KEY", ""),
        "delivery_lock_hit": os.environ.get("DELIVERY_LOCK_HIT") == "true",
        "candidate_count_total": raw_count,
        "raw_candidate_count_total": raw_count,
        "shortlist_count": shortlist_count,
        "tech_shortlist_count": track_count(shortlist, "tech"),
        "investment_shortlist_count": track_count(shortlist, "investment"),
        "selected_news_count": selected_news_count,
        "tech_selected_count": tech_selected_count,
        "investment_selected_count": investment_selected_count,
        "bridge_present": bool(bridge_body),
        "growth_score": growth_score(report),
        "growth_action_present": growth_action_present(report),
        "estimated_prompt_chars": int(budget.get("estimated_prompt_chars", 0) or 0),
        "estimated_prompt_tokens_rough": int(budget.get("estimated_prompt_tokens_rough", 0) or 0),
        "estimated_output_tokens_budget_rough": int(
            budget.get("estimated_output_tokens_budget_rough", 0) or 0
        ),
        "fallback_reason": fallback_reason(
            report,
            selected_news_count,
            os.environ.get("SKIP_REASON", ""),
        ),
        "source_errors_count": len(source_errors),
        "discord_send_attempted": os.environ.get("SHOULD_SEND") == "true",
        "discord_send_success": os.environ.get("DISCORD_SEND_OUTCOME") == "success",
        "generation_attempted": os.environ.get("SHOULD_GENERATE") == "true",
    }

    args.output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.output_md.write_text(
        "# News Daily Run Summary\n\n"
        f"- event: {summary['event_name']}\n"
        f"- schedule: {summary['schedule']}\n"
        f"- dry_run: {summary['dry_run']}\n"
        f"- force_send: {summary['force_send']}\n"
        f"- delivery_lock_key: {summary['delivery_lock_key']}\n"
        f"- delivery_lock_hit: {summary['delivery_lock_hit']}\n"
        f"- candidate_count_total: {summary['candidate_count_total']}\n"
        f"- raw_candidate_count_total: {summary['raw_candidate_count_total']}\n"
        f"- shortlist_count: {summary['shortlist_count']}\n"
        f"- tech_shortlist_count: {summary['tech_shortlist_count']}\n"
        f"- investment_shortlist_count: {summary['investment_shortlist_count']}\n"
        f"- selected_news_count: {summary['selected_news_count']}\n"
        f"- tech_selected_count: {summary['tech_selected_count']}\n"
        f"- investment_selected_count: {summary['investment_selected_count']}\n"
        f"- bridge_present: {summary['bridge_present']}\n"
        f"- growth_score: {summary['growth_score']}\n"
        f"- growth_action_present: {summary['growth_action_present']}\n"
        f"- estimated_prompt_chars: {summary['estimated_prompt_chars']}\n"
        f"- estimated_prompt_tokens_rough: {summary['estimated_prompt_tokens_rough']}\n"
        f"- estimated_output_tokens_budget_rough: {summary['estimated_output_tokens_budget_rough']}\n"
        f"- source_errors_count: {summary['source_errors_count']}\n"
        f"- discord_send_attempted: {summary['discord_send_attempted']}\n"
        f"- discord_send_success: {summary['discord_send_success']}\n"
        f"- fallback_reason: {summary['fallback_reason']}\n",
        encoding="utf-8",
    )
    print(f"Wrote News Daily run summary: {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
