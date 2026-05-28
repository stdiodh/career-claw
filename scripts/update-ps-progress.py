#!/usr/bin/env python3
"""Update static Programmers PS routine progress."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
CURRICULUM_PATH = Path("configs/programmers-ps-curriculum.json")
PROGRESS_PATH = Path("data/ps-progress.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update PS routine progress.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--status", action="store_true", help="Print current PS status.")
    action.add_argument("--mark-solved", metavar="PROBLEM_ID", help="Mark a problem solved.")
    action.add_argument("--advance-track", metavar="TRACK_ID", help="Move to another track.")
    parser.add_argument("--notes", default="", help="Optional notes for --mark-solved.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise RuntimeError(f"Required file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return data


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def get_tracks(curriculum: dict[str, object]) -> list[dict[str, object]]:
    tracks = curriculum.get("tracks", [])
    if not isinstance(tracks, list):
        raise RuntimeError("configs/programmers-ps-curriculum.json must contain tracks.")
    return [track for track in tracks if isinstance(track, dict)]


def get_track(curriculum: dict[str, object], track_id: str) -> dict[str, object]:
    for track in get_tracks(curriculum):
        if str(track.get("id", "")).strip() == track_id:
            return track
    raise RuntimeError(f"Unknown track: {track_id}")


def get_problem_index(
    curriculum: dict[str, object],
) -> dict[str, tuple[str, dict[str, object]]]:
    index = {}
    for track in get_tracks(curriculum):
        track_id = str(track.get("id", "")).strip()
        problems = track.get("problems", [])
        if not isinstance(problems, list):
            raise RuntimeError(f"Track must contain a problems array: {track_id}")
        for problem in problems:
            if not isinstance(problem, dict):
                continue
            problem_id = str(problem.get("id", "")).strip()
            if problem_id:
                index[problem_id] = (track_id, problem)
    return index


def progress_problem_ids(entries: object) -> set[str]:
    if not isinstance(entries, list):
        return set()

    ids = set()
    for entry in entries:
        if isinstance(entry, dict):
            problem_id = str(entry.get("problem_id", "")).strip()
        else:
            problem_id = str(entry).strip()
        if problem_id:
            ids.add(problem_id)
    return ids


def count_track_solved(track: dict[str, object], progress: dict[str, object]) -> tuple[int, int]:
    solved_ids = progress_problem_ids(progress.get("solved", []))
    problems = track.get("problems", [])
    if not isinstance(problems, list):
        raise RuntimeError(f"Track must contain a problems array: {track.get('id')}")
    total = 0
    solved = 0
    for problem in problems:
        if not isinstance(problem, dict):
            continue
        total += 1
        if str(problem.get("id", "")).strip() in solved_ids:
            solved += 1
    return solved, total


def print_status(curriculum: dict[str, object], progress: dict[str, object]) -> None:
    current_track_id = str(progress.get("current_track", "")).strip()
    track = get_track(curriculum, current_track_id)
    solved_count, total_count = count_track_solved(track, progress)
    status = {
        "current_track": {
            "id": current_track_id,
            "name": str(track.get("name", "")).strip(),
            "week_started_at": str(progress.get("week_started_at", "")).strip(),
            "target_level": progress.get("target_level"),
            "progress": f"{solved_count}/{total_count}",
        },
        "assigned_count": len(progress.get("assigned", []))
        if isinstance(progress.get("assigned", []), list)
        else 0,
        "solved_count": len(progress.get("solved", []))
        if isinstance(progress.get("solved", []), list)
        else 0,
        "completed_tracks": progress.get("completed_tracks", []),
        "manual_advance_requested": bool(progress.get("manual_advance_requested", False)),
        "last_recommended_problem_id": str(
            progress.get("last_recommended_problem_id", "")
        ).strip(),
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))


def mark_solved(
    curriculum: dict[str, object],
    progress: dict[str, object],
    problem_id: str,
    notes: str,
) -> bool:
    problem_index = get_problem_index(curriculum)
    if problem_id not in problem_index:
        raise RuntimeError(f"Unknown problem_id: {problem_id}")

    solved = progress.setdefault("solved", [])
    if not isinstance(solved, list):
        raise RuntimeError("data/ps-progress.json solved must be an array.")

    if problem_id in progress_problem_ids(solved):
        print(f"Already solved: {problem_id}")
        return False

    solved.append(
        {
            "date": datetime.now(tz=KST).strftime("%Y-%m-%d"),
            "problem_id": problem_id,
            "notes": notes.strip(),
        }
    )
    print(f"Marked solved: {problem_id}")
    return True


def completed_track_ids(entries: object) -> set[str]:
    if not isinstance(entries, list):
        return set()
    ids = set()
    for entry in entries:
        if isinstance(entry, dict):
            track_id = str(entry.get("track_id", "")).strip()
        else:
            track_id = str(entry).strip()
        if track_id:
            ids.add(track_id)
    return ids


def advance_track(
    curriculum: dict[str, object],
    progress: dict[str, object],
    next_track_id: str,
) -> bool:
    next_track = get_track(curriculum, next_track_id)
    previous_track_id = str(progress.get("current_track", "")).strip()
    completed_tracks = progress.setdefault("completed_tracks", [])
    if not isinstance(completed_tracks, list):
        raise RuntimeError("data/ps-progress.json completed_tracks must be an array.")

    if previous_track_id and previous_track_id != next_track_id:
        if previous_track_id not in completed_track_ids(completed_tracks):
            completed_tracks.append(previous_track_id)

    progress["current_track"] = next_track_id
    progress["week_started_at"] = datetime.now(tz=KST).strftime("%Y-%m-%d")
    progress["target_level"] = int(
        next_track.get("default_target_level") or progress.get("target_level") or 2
    )
    progress["manual_advance_requested"] = False
    progress["last_recommended_problem_id"] = ""
    print(f"Advanced track: {previous_track_id or '(none)'} -> {next_track_id}")
    return True


def main() -> int:
    args = parse_args()
    try:
        curriculum = load_json(CURRICULUM_PATH)
        progress = load_json(PROGRESS_PATH)

        if args.status:
            print_status(curriculum, progress)
            return 0

        changed = False
        if args.mark_solved:
            changed = mark_solved(
                curriculum,
                progress,
                args.mark_solved.strip(),
                args.notes,
            )
        elif args.advance_track:
            changed = advance_track(curriculum, progress, args.advance_track.strip())

        if changed:
            write_json(PROGRESS_PATH, progress)
        return 0
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
