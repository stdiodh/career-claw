#!/usr/bin/env python3
"""Render the next backend practice and PS problem without an LLM."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    from . import verify_curriculum
except ImportError:
    import verify_curriculum


ROOT = Path(__file__).resolve().parents[1]
BACKEND_CONFIG = ROOT / "configs/backend-practice.json"
PS_CONFIG = ROOT / "configs/ps-problems.json"
PROGRESS_FILE = ROOT / "data/progress.json"
OUTPUT_FILE = ROOT / "reports/backend-daily.md"
MATRIX_CONFIG = ROOT / "configs/curriculum-matrix.json"
PROFILE_CONFIG = ROOT / "configs/verification-profile.json"
TAXONOMY_CONFIG = ROOT / "configs/competency-taxonomy.json"
JOB_MARKET_AUDIT = ROOT / "audits/job-market-2026q3.json"
VERIFICATION_MANIFEST = ROOT / "data/curriculum-verification.json"
LAB_DIR = ROOT / "lab"
KST = ZoneInfo("Asia/Seoul")

BACKEND_REQUIRED_FIELDS = {
    "id",
    "track",
    "title",
    "setup",
    "situation",
    "core_concept",
    "failure_mode",
    "practice_steps",
    "evidence",
    "official_refs",
    "check_question",
}
PS_REQUIRED_FIELDS = {"id", "title", "url", "level", "first_thought"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format.")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    parser.add_argument("--backend-config", type=Path, default=BACKEND_CONFIG)
    parser.add_argument("--ps-config", type=Path, default=PS_CONFIG)
    parser.add_argument("--progress", type=Path, default=PROGRESS_FILE)
    parser.add_argument("--matrix", type=Path, default=MATRIX_CONFIG)
    parser.add_argument("--profile", type=Path, default=PROFILE_CONFIG)
    parser.add_argument("--taxonomy", type=Path, default=TAXONOMY_CONFIG)
    parser.add_argument("--job-market-audit", type=Path, default=JOB_MARKET_AUDIT)
    parser.add_argument("--verification-manifest", type=Path, default=VERIFICATION_MANIFEST)
    parser.add_argument("--lab", type=Path, default=LAB_DIR)
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return payload


def require_string(value: object, field: str, item_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{item_id}: {field} must be a non-empty string")


def require_string_list(value: object, field: str, item_id: str) -> None:
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"{item_id}: {field} must be a non-empty list")
    for entry in value:
        require_string(entry, field, item_id)


def load_backend_lessons(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    lessons = payload.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        raise RuntimeError(f"lessons must be a non-empty list: {path}")

    seen: set[str] = set()
    for lesson in lessons:
        if not isinstance(lesson, dict):
            raise RuntimeError(f"Every backend lesson must be an object: {path}")
        item_id = str(lesson.get("id", "<missing-id>"))
        missing = sorted(BACKEND_REQUIRED_FIELDS - lesson.keys())
        if missing:
            raise RuntimeError(f"{item_id}: missing backend field(s): {', '.join(missing)}")
        for field in BACKEND_REQUIRED_FIELDS - {"practice_steps", "official_refs"}:
            require_string(lesson[field], field, item_id)
        require_string_list(lesson["practice_steps"], "practice_steps", item_id)
        require_string_list(lesson["official_refs"], "official_refs", item_id)
        for url in lesson["official_refs"]:
            if not url.startswith("https://"):
                raise RuntimeError(f"{item_id}: official_refs must use HTTPS")
        if item_id in seen:
            raise RuntimeError(f"Duplicate backend lesson id: {item_id}")
        seen.add(item_id)

    return lessons


def load_verified_backend_lessons(
    backend_path: Path = BACKEND_CONFIG,
    matrix_path: Path = MATRIX_CONFIG,
    profile_path: Path = PROFILE_CONFIG,
    taxonomy_path: Path = TAXONOMY_CONFIG,
    manifest_path: Path = VERIFICATION_MANIFEST,
    lab_dir: Path = LAB_DIR,
    job_market_path: Path = JOB_MARKET_AUDIT,
) -> list[dict[str, Any]]:
    lessons = load_backend_lessons(backend_path)
    summary = verify_curriculum.verify_paths(
        backend_path,
        matrix_path,
        profile_path,
        taxonomy_path,
        manifest_path,
        lab_dir,
        job_market_path,
    )
    if not summary["valid"]:
        details = "; ".join(summary["errors"])
        raise RuntimeError(f"Curriculum verification is not current: {details}")

    matrix = read_json(matrix_path)
    entries = {
        entry["id"]: entry
        for entry in matrix["lessons"]
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    verified_ids = set(summary["verified_lesson_ids"])
    verified: list[dict[str, Any]] = []
    for lesson in lessons:
        if lesson["id"] not in verified_ids:
            continue
        enriched = dict(lesson)
        enriched["_verification"] = {
            "profile_id": summary["profile_id"],
            "lab_revision": summary["lab_revision"],
            "verify_command": entries[lesson["id"]]["lab"]["verify_command"],
            "test_ids": entries[lesson["id"]]["lab"]["test_ids"],
        }
        verified.append(enriched)

    if not verified:
        raise RuntimeError("No VERIFIED core backend lessons are available")
    return verified


def load_ps_tracks(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    tracks = payload.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise RuntimeError(f"tracks must be a non-empty list: {path}")

    seen_tracks: set[str] = set()
    seen_problems: set[str] = set()
    for track in tracks:
        if not isinstance(track, dict):
            raise RuntimeError(f"Every PS track must be an object: {path}")
        require_string(track.get("id"), "id", "PS track")
        require_string(track.get("name"), "name", str(track["id"]))
        require_string(track.get("goal"), "goal", str(track["id"]))
        if track["id"] in seen_tracks:
            raise RuntimeError(f"Duplicate PS track id: {track['id']}")
        seen_tracks.add(track["id"])
        problems = track.get("problems")
        if not isinstance(problems, list) or not problems:
            raise RuntimeError(f"{track['id']}: problems must be a non-empty list")
        for problem in problems:
            if not isinstance(problem, dict):
                raise RuntimeError(f"{track['id']}: every problem must be an object")
            item_id = str(problem.get("id", "<missing-id>"))
            missing = sorted(PS_REQUIRED_FIELDS - problem.keys())
            if missing:
                raise RuntimeError(f"{item_id}: missing PS field(s): {', '.join(missing)}")
            for field in PS_REQUIRED_FIELDS - {"level"}:
                require_string(problem[field], field, item_id)
            if type(problem["level"]) is not int or problem["level"] < 0:
                raise RuntimeError(f"{item_id}: level must be a non-negative integer")
            if not str(problem["url"]).startswith("https://"):
                raise RuntimeError(f"{item_id}: url must use HTTPS")
            if item_id in seen_problems:
                raise RuntimeError(f"Duplicate PS problem id: {item_id}")
            seen_problems.add(item_id)

    return tracks


def load_progress(path: Path) -> dict[str, list[str]]:
    payload = read_json(path)
    progress: dict[str, list[str]] = {}
    for key in ("backend_completed", "ps_solved"):
        values = payload.get(key)
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise RuntimeError(f"{key} must be a list of ids: {path}")
        if len(values) != len(set(values)):
            raise RuntimeError(f"{key} contains duplicate ids: {path}")
        progress[key] = values
    return progress


def validate_progress_ids(
    lessons: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    progress: dict[str, list[str]],
) -> None:
    lesson_ids = {str(lesson["id"]) for lesson in lessons}
    problem_ids = {
        str(problem["id"])
        for track in tracks
        for problem in track["problems"]
    }
    unknown_lessons = sorted(set(progress["backend_completed"]) - lesson_ids)
    unknown_problems = sorted(set(progress["ps_solved"]) - problem_ids)
    if unknown_lessons:
        raise RuntimeError(f"Unknown completed backend id(s): {', '.join(unknown_lessons)}")
    if unknown_problems:
        raise RuntimeError(f"Unknown solved PS id(s): {', '.join(unknown_problems)}")


def select_backend_lesson(
    lessons: list[dict[str, Any]], completed: set[str]
) -> dict[str, Any] | None:
    return next((lesson for lesson in lessons if lesson["id"] not in completed), None)


def select_ps_problem(
    tracks: list[dict[str, Any]], solved: set[str]
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    for track in tracks:
        for problem in track["problems"]:
            if problem["id"] not in solved:
                return track, problem
    return None


def render_links(urls: list[str]) -> list[str]:
    return [f"  - [참고 자료 {index}]({url})" for index, url in enumerate(urls, start=1)]


def render_report(
    report_date: date,
    lessons: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    progress: dict[str, list[str]],
) -> str:
    lesson_ids = {lesson["id"] for lesson in lessons}
    completed = set(progress["backend_completed"]) & lesson_ids
    solved = set(progress["ps_solved"])
    lesson = select_backend_lesson(lessons, completed)
    ps_selection = select_ps_problem(tracks, solved)

    lines = [
        "# Career Feed - Backend Daily",
        "",
        f"기준일: {report_date.isoformat()} KST",
        "",
        f"진행: 백엔드 {len(completed)}/{len(lessons)} · PS {len(solved)}/{sum(len(track['problems']) for track in tracks)}",
        "",
        "## 오늘의 백엔드 30분 실습",
        "",
    ]

    if lesson is None:
        lines.extend(["모든 백엔드 실습을 완료했습니다. 새 주제를 추가하거나 진행 상태를 초기화하세요.", ""])
    else:
        lines.extend(
            [
                f"### {lesson['title']}",
                f"- 트랙: {lesson['track']}",
                f"- 준비: {lesson['setup']}",
                f"- 상황: {lesson['situation']}",
                f"- 실패 모드: {lesson['failure_mode']}",
                f"- 핵심: {lesson['core_concept']}",
                "",
                "실습:",
            ]
        )
        lines.extend(
            f"{index}. {step}" for index, step in enumerate(lesson["practice_steps"], start=1)
        )
        lines.extend(
            [
                "",
                f"완료 질문: {lesson['check_question']}",
                f"남길 증거: {lesson['evidence']}",
                f"완료 ID: `{lesson['id']}`",
            ]
        )
        verification = lesson.get("_verification")
        if isinstance(verification, dict):
            test_ids = ", ".join(verification["test_ids"])
            lines.extend(
                [
                    f"검증 profile: `{verification['profile_id']}`",
                    f"검증 명령: `{verification['verify_command']}`",
                    f"검증 test ID: `{test_ids}`",
                ]
            )
        lines.extend(["", "참고:"])
        lines.extend(render_links(lesson["official_refs"][:2]))
        lines.append("")

    lines.extend(["## 오늘의 PS", ""])
    if ps_selection is None:
        lines.extend(["등록된 PS 문제를 모두 풀었습니다.", ""])
    else:
        track, problem = ps_selection
        lines.extend(
            [
                f"### [{problem['title']}]({problem['url']})",
                f"- 트랙: {track['name']} — {track['goal']}",
                f"- 난이도: Level {problem['level']}",
                f"- 막히면 볼 힌트: ||{problem['first_thought']}||",
                f"- 완료 ID: `{problem['id']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## 완료 기록",
            "",
            "GitHub Actions의 `Mark Progress`에서 종류와 완료 ID를 입력합니다.",
            "로컬에서는 백엔드 과제에 `python3 scripts/mark_progress.py backend <완료 ID>`, "
            "PS에 `python3 scripts/mark_progress.py ps <완료 ID>`를 실행합니다.",
            "",
        ]
    )
    return "\n".join(lines)


def resolve_date(value: str | None) -> date:
    if value is None:
        return datetime.now(KST).date()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RuntimeError("--date must use YYYY-MM-DD format") from exc


def main() -> int:
    args = parse_args()
    try:
        catalog_lessons = load_backend_lessons(args.backend_config)
        lessons = load_verified_backend_lessons(
            args.backend_config,
            args.matrix,
            args.profile,
            args.taxonomy,
            args.verification_manifest,
            args.lab,
            args.job_market_audit,
        )
        tracks = load_ps_tracks(args.ps_config)
        progress = load_progress(args.progress)
        validate_progress_ids(catalog_lessons, tracks, progress)
        report = render_report(resolve_date(args.date), lessons, tracks, progress)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    except (OSError, RuntimeError) as exc:
        print(f"Failed to generate Backend Daily: {exc}", file=sys.stderr)
        return 1

    if args.stdout:
        print(report, end="")
    print(f"Wrote Backend Daily: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
