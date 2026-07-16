#!/usr/bin/env python3
"""Mark one backend lesson or PS problem complete."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    from . import generate_backend_daily as daily
except ImportError:
    import generate_backend_daily as daily


ROOT = daily.ROOT
BACKEND_CONFIG = daily.BACKEND_CONFIG
PS_CONFIG = daily.PS_CONFIG
PROGRESS_FILE = daily.PROGRESS_FILE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("item_type", choices=("backend", "ps"))
    parser.add_argument("item_id")
    parser.add_argument("--progress", type=Path, default=PROGRESS_FILE)
    parser.add_argument("--backend-config", type=Path, default=BACKEND_CONFIG)
    parser.add_argument("--ps-config", type=Path, default=PS_CONFIG)
    return parser.parse_args()


def write_json_atomic(path: Path, payload: dict[str, list[str]]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def mark_complete(
    item_type: str,
    item_id: str,
    progress_path: Path,
    backend_config: Path,
    ps_config: Path,
) -> bool:
    if item_type not in {"backend", "ps"}:
        raise RuntimeError(f"Unsupported item type: {item_type}")
    catalog_lessons = daily.load_backend_lessons(backend_config)
    tracks = daily.load_ps_tracks(ps_config)
    if item_type == "backend":
        verified_lessons = daily.load_verified_backend_lessons(backend_config)
        valid_ids = {lesson["id"] for lesson in verified_lessons}
    else:
        valid_ids = {
            problem["id"]
            for track in tracks
            for problem in track["problems"]
        }
    if item_id not in valid_ids:
        raise RuntimeError(f"Unknown {item_type} id: {item_id}")

    lock_path = progress_path.with_name(f"{progress_path.name}.lock")
    with lock_path.open("a", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        progress = daily.load_progress(progress_path)
        daily.validate_progress_ids(catalog_lessons, tracks, progress)
        key = "backend_completed" if item_type == "backend" else "ps_solved"
        if item_id in progress[key]:
            return False

        progress[key].append(item_id)
        write_json_atomic(progress_path, progress)
        return True


def main() -> int:
    args = parse_args()
    try:
        changed = mark_complete(
            args.item_type,
            args.item_id,
            args.progress,
            args.backend_config,
            args.ps_config,
        )
    except (OSError, RuntimeError) as exc:
        print(f"Failed to update progress: {exc}", file=sys.stderr)
        return 1

    if changed:
        print(f"Marked {args.item_type} item complete: {args.item_id}")
    else:
        print(f"Already complete: {args.item_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
