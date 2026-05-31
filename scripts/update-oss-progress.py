#!/usr/bin/env python3
"""Update local OSS review progress without mutating GitHub issues."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
PROGRESS_PATH = Path("data/oss-progress.json")
ISSUE_URL_RE = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/(\d+)/?$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update local OSS progress.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--status", action="store_true", help="Print current OSS progress.")
    action.add_argument("--mark-reviewed", metavar="ISSUE_URL", help="Mark an issue reviewed.")
    action.add_argument("--mark-skipped", metavar="ISSUE_URL", help="Mark an issue skipped.")
    action.add_argument("--mark-attempted", metavar="ISSUE_URL", help="Mark an issue attempted.")
    parser.add_argument("--note", default="", help="Optional note for the progress entry.")
    return parser.parse_args()


def load_progress(path: Path = PROGRESS_PATH) -> dict[str, object]:
    if not path.exists():
        raise RuntimeError(f"Required file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return data


def write_progress(progress: dict[str, object], path: Path = PROGRESS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def normalize_issue_url(url: str) -> tuple[str, str, str]:
    raw_url = url.strip()
    match = ISSUE_URL_RE.match(raw_url)
    if not match:
        raise RuntimeError("OSS progress requires a GitHub issue URL.")
    repository = match.group(1)
    issue_number = match.group(2)
    parsed = urlsplit(raw_url)
    normalized = f"https://github.com/{repository}/issues/{issue_number}"
    if parsed.netloc != "github.com":
        raise RuntimeError("OSS progress only supports github.com issue URLs.")
    return normalized, repository, issue_number


def progress_entries(progress: dict[str, object], key: str) -> list[dict[str, object]]:
    entries = progress.setdefault(key, [])
    if not isinstance(entries, list):
        raise RuntimeError(f"data/oss-progress.json {key} must be an array.")
    return entries


def entry_exists(entries: list[dict[str, object]], issue_url: str) -> bool:
    return any(
        isinstance(entry, dict) and str(entry.get("issue_url", "")).strip() == issue_url
        for entry in entries
    )


def mark_issue(
    progress: dict[str, object],
    key: str,
    issue_url: str,
    note: str,
) -> bool:
    normalized_url, repository, issue_number = normalize_issue_url(issue_url)
    entries = progress_entries(progress, key)
    if entry_exists(entries, normalized_url):
        print(f"Already marked {key}: {normalized_url}")
        return False

    now = datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S KST")
    entries.append(
        {
            "date": datetime.now(tz=KST).strftime("%Y-%m-%d"),
            "issue_url": normalized_url,
            "repository": repository,
            "issue_number": int(issue_number),
            "note": note.strip(),
        }
    )
    progress["last_updated_at"] = now
    print(f"Marked {key}: {normalized_url}")
    return True


def print_status(progress: dict[str, object]) -> None:
    status = {
        "reviewed_count": len(progress.get("reviewed", []))
        if isinstance(progress.get("reviewed", []), list)
        else 0,
        "skipped_count": len(progress.get("skipped", []))
        if isinstance(progress.get("skipped", []), list)
        else 0,
        "attempted_count": len(progress.get("attempted", []))
        if isinstance(progress.get("attempted", []), list)
        else 0,
        "last_updated_at": str(progress.get("last_updated_at", "")).strip(),
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    try:
        progress = load_progress()
        if args.status:
            print_status(progress)
            return 0

        changed = False
        if args.mark_reviewed:
            changed = mark_issue(progress, "reviewed", args.mark_reviewed, args.note)
        elif args.mark_skipped:
            changed = mark_issue(progress, "skipped", args.mark_skipped, args.note)
        elif args.mark_attempted:
            changed = mark_issue(progress, "attempted", args.mark_attempted, args.note)

        if changed:
            write_progress(progress)
        return 0
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
