#!/usr/bin/env python3
"""Select the next static Programmers PS problem for the current weekly track."""

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
OUTPUT_PATH = Path("reports/candidates/ps-weekly-routine.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a weekly Programmers PS routine problem."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the recommendation output without modifying progress.",
    )
    parser.add_argument(
        "--record-assignment",
        action="store_true",
        help="Record the selected problem in data/ps-progress.json.",
    )
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
    raise RuntimeError(f"Unknown current_track in progress: {track_id}")


def get_problems(track: dict[str, object]) -> list[dict[str, object]]:
    problems = track.get("problems", [])
    if not isinstance(problems, list):
        raise RuntimeError(f"Track must contain a problems array: {track.get('id')}")
    return [problem for problem in problems if isinstance(problem, dict)]


def problem_ids(entries: object) -> set[str]:
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


def problem_level(problem: dict[str, object]) -> int:
    try:
        return int(problem.get("level", 0))
    except (TypeError, ValueError):
        return 0


def select_problem(
    track: dict[str, object],
    progress: dict[str, object],
) -> dict[str, object] | None:
    solved_ids = problem_ids(progress.get("solved", []))
    candidates = [
        (index, problem)
        for index, problem in enumerate(get_problems(track))
        if str(problem.get("id", "")).strip() not in solved_ids
    ]
    if not candidates:
        return None

    _, selected = min(candidates, key=lambda item: (problem_level(item[1]), item[0]))
    return selected


def build_advance_recommendation(
    track: dict[str, object],
    progress: dict[str, object],
) -> dict[str, object]:
    solved_ids = problem_ids(progress.get("solved", []))
    solved_problems = [
        problem
        for problem in get_problems(track)
        if str(problem.get("id", "")).strip() in solved_ids
    ]
    rule = track.get("advance_rule", {})
    if not isinstance(rule, dict):
        rule = {}

    min_solved = int(rule.get("min_solved", 0) or 0)
    target_level_count = int(rule.get("max_level_solved", 0) or 0)
    target_level = int(progress.get("target_level") or track.get("default_target_level") or 0)
    target_level_solved = [
        problem for problem in solved_problems if problem_level(problem) >= target_level
    ]

    if bool(progress.get("manual_advance_requested")) and bool(
        rule.get("allow_manual_advance", False)
    ):
        return {
            "can_advance": True,
            "reason": "수동 track 이동 요청이 설정되어 있습니다.",
        }
    if len(target_level_solved) < target_level_count:
        return {
            "can_advance": False,
            "reason": "target_level 문제를 아직 충분히 풀지 않았습니다.",
        }
    if len(solved_problems) < min_solved:
        return {
            "can_advance": False,
            "reason": "현재 track에서 해결한 문제가 아직 충분하지 않습니다.",
        }
    return {
        "can_advance": True,
        "reason": "현재 track의 최소 진행 조건을 충족했습니다.",
    }


def build_output(
    track: dict[str, object],
    progress: dict[str, object],
    selected: dict[str, object] | None,
) -> dict[str, object]:
    problems = get_problems(track)
    solved_ids = problem_ids(progress.get("solved", []))
    solved_count = sum(
        1 for problem in problems if str(problem.get("id", "")).strip() in solved_ids
    )
    target_level = int(progress.get("target_level") or track.get("default_target_level") or 0)

    return {
        "category": "ps-weekly-routine",
        "generated_at": datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S KST"),
        "current_track": {
            "id": str(track.get("id", "")).strip(),
            "name": str(track.get("name", "")).strip(),
            "goal": str(track.get("goal", "")).strip(),
            "week_started_at": str(progress.get("week_started_at", "")).strip(),
            "target_level": target_level,
            "progress": f"{solved_count}/{len(problems)}",
        },
        "today_problem": selected,
        "advance_recommendation": build_advance_recommendation(track, progress),
    }


def record_assignment(
    progress: dict[str, object],
    selected: dict[str, object] | None,
) -> None:
    if selected is None:
        return

    assigned = progress.setdefault("assigned", [])
    if not isinstance(assigned, list):
        raise RuntimeError("data/ps-progress.json assigned must be an array.")

    problem_id = str(selected.get("id", "")).strip()
    assigned.append(
        {
            "date": datetime.now(tz=KST).strftime("%Y-%m-%d"),
            "problem_id": problem_id,
        }
    )
    progress["last_recommended_problem_id"] = problem_id


def main() -> int:
    args = parse_args()
    try:
        curriculum = load_json(CURRICULUM_PATH)
        progress = load_json(PROGRESS_PATH)
        current_track = str(progress.get("current_track", "")).strip()
        if not current_track:
            raise RuntimeError("data/ps-progress.json current_track is required.")

        track = get_track(curriculum, current_track)
        selected = select_problem(track, progress)
        output = build_output(track, progress, selected)
        write_json(OUTPUT_PATH, output)

        if args.record_assignment and not args.dry_run:
            record_assignment(progress, selected)
            write_json(PROGRESS_PATH, progress)

        if selected is None:
            print(f"Wrote PS routine with no remaining problem: {OUTPUT_PATH}")
        else:
            print(
                "Wrote PS routine: "
                f"{selected.get('id')} / {selected.get('title')} -> {OUTPUT_PATH}"
            )
        if args.record_assignment and args.dry_run:
            print("Dry-run: assignment was not recorded.")
        return 0
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
