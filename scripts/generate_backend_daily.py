#!/usr/bin/env python3
"""Render a deterministic backend, PS, OSS-prep, and applied-CS brief."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    from . import check_oss_delivery_gate as oss_gate
    from . import collect_oss_candidates as oss_collector
    from . import sync_delivery_schedule as sync_schedule
    from . import verify_curriculum
except ImportError:
    import check_oss_delivery_gate as oss_gate
    import collect_oss_candidates as oss_collector
    import sync_delivery_schedule as sync_schedule
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
OSS_CONFIG = ROOT / "configs/oss-repositories.json"
OSS_GATE = ROOT / "configs/oss-delivery-gate.json"
SCHEDULE_CONFIG = ROOT / sync_schedule.CONFIG_PATH
DEFAULT_TIMEZONE = "Asia/Seoul"

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
    parser.add_argument("--oss-config", type=Path, default=OSS_CONFIG)
    parser.add_argument("--oss-gate", type=Path, default=OSS_GATE)
    parser.add_argument("--schedule-config", type=Path, default=SCHEDULE_CONFIG)
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


def is_verified_lesson(lesson: dict[str, Any]) -> bool:
    verification = lesson.get("_verification")
    return (
        isinstance(verification, dict)
        and verification.get("status") == "VERIFIED"
    )


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
            "status": "VERIFIED",
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


def ps_problem_ids(tracks: list[dict[str, Any]]) -> set[str]:
    return {
        str(problem["id"])
        for track in tracks
        for problem in track["problems"]
    }


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
    problem_ids = ps_problem_ids(tracks)
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


def select_rotating_item(
    items: list[dict[str, Any]], report_date: date
) -> dict[str, Any] | None:
    if not items:
        return None
    return items[report_date.toordinal() % len(items)]


def select_cs_lesson(
    lessons: list[dict[str, Any]], report_date: date
) -> dict[str, Any] | None:
    verified = [lesson for lesson in lessons if is_verified_lesson(lesson)]
    return select_rotating_item(verified, report_date)


def load_oss_brief(
    report_date: date,
    evaluation_time: datetime,
    config_path: Path = OSS_CONFIG,
    gate_path: Path = OSS_GATE,
) -> dict[str, Any]:
    try:
        config = oss_collector.load_config(config_path, as_of=report_date)
        gate = oss_gate.read_object(gate_path)
        progress = oss_gate.evaluate_gate(
            gate,
            oss_gate.allowed_repositories(config),
            now=evaluation_time,
        )
        profile = select_rotating_item(config["repositories"], report_date)
        if profile is None:
            raise RuntimeError("OSS allowlist has no repository profiles")
    except (OSError, RuntimeError):
        return {"available": False}

    return {
        "available": True,
        "profile": profile,
        "progress": progress,
        "requirements": oss_gate.REQUIREMENTS,
    }


def render_links(urls: list[str]) -> list[str]:
    return [f"  - [참고 자료 {index}]({url})" for index, url in enumerate(urls, start=1)]


def resolve_delivery_datetime(
    report_date: date,
    timezone_name: str,
    hour: int,
    minute: int,
) -> datetime:
    local_delivery = datetime(
        report_date.year,
        report_date.month,
        report_date.day,
        hour,
        minute,
        tzinfo=ZoneInfo(timezone_name),
    )
    return local_delivery.astimezone(timezone.utc)


def render_report(
    report_date: date,
    lessons: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    progress: dict[str, list[str]],
    oss_config_path: Path = OSS_CONFIG,
    oss_gate_path: Path = OSS_GATE,
    report_timezone: str = DEFAULT_TIMEZONE,
    report_hour: int = 9,
    report_minute: int = 0,
) -> str:
    lesson_ids = {lesson["id"] for lesson in lessons}
    completed = set(progress["backend_completed"]) & lesson_ids
    solved = set(progress["ps_solved"])
    lesson = select_backend_lesson(lessons, completed)
    ps_selection = select_ps_problem(tracks, solved)
    cs_lesson = (
        lesson
        if lesson is not None and is_verified_lesson(lesson)
        else select_cs_lesson(lessons, report_date)
    )
    oss_brief = load_oss_brief(
        report_date,
        resolve_delivery_datetime(
            report_date,
            report_timezone,
            report_hour,
            report_minute,
        ),
        oss_config_path,
        oss_gate_path,
    )

    lines = [
        "# Career Feed - Backend Daily",
        "",
        f"기준일: {report_date.isoformat()} · {report_timezone}",
        "",
        f"진행: 백엔드 {len(completed)}/{len(lessons)} · PS {len(solved)}/{len(ps_problem_ids(tracks))}",
        "",
        "## 오늘의 백엔드 실무",
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

    lines.extend(["## 오늘의 OSS 기여 준비", ""])
    if not oss_brief["available"]:
        lines.extend(
            [
                "OSS 계약을 검증하지 못해 오늘은 저장소와 이슈 후보를 노출하지 않습니다.",
                "- 검증 상태: config 또는 gate 계약 오류로 fail-closed",
                "",
            ]
        )
    else:
        profile = oss_brief["profile"]
        gate_progress = oss_brief["progress"]
        requirements = oss_brief["requirements"]
        repository = profile["repository"]
        build_command = profile["eligibility_evidence"]["build_test"]["command"]
        lines.extend(
            [
                f"### [{repository}](https://github.com/{repository})",
                f"- 관련 이유: {profile['relevance_reason']}",
                f"- 기여 가이드: {profile['contributing_url']}",
                f"- 첫 build/test: `{build_command}`",
                f"- 전송 gate: `{gate_progress['status']}`",
                "- Shadow 진행: "
                f"연속 {gate_progress['consecutive_qualifying_weeks']}/"
                f"{requirements['minimum_consecutive_qualifying_weeks']}주 · "
                f"후보 리뷰 {gate_progress['unique_candidates']}/"
                f"{requirements['minimum_unique_candidates']}개",
            ]
        )
        if gate_progress["status"] == "LOCKED":
            lines.append("- 현재는 저장소 온보딩만 제공하며 실제 이슈 후보는 노출하지 않습니다.")
        lines.append("")

    lines.extend(["## 오늘의 백엔드 연결 CS 지식", ""])
    if cs_lesson is None:
        lines.extend(["현재 노출할 수 있는 VERIFIED CS 연결 주제가 없습니다.", ""])
    else:
        lines.extend(
            [
                f"### {cs_lesson['track']} — {cs_lesson['title']}",
                f"- 핵심 개념: {cs_lesson['core_concept']}",
                f"- 실패 모드: {cs_lesson['failure_mode']}",
                f"- 확인 질문: {cs_lesson['check_question']}",
                "",
                "공식 참고:",
            ]
        )
        lines.extend(render_links(cs_lesson["official_refs"][:2]))
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "완료 기록은 GitHub Actions의 `Mark Progress`에서 종류와 완료 ID를 입력합니다.",
            "로컬에서는 백엔드 과제에 `python3 scripts/mark_progress.py backend <완료 ID>`, "
            "PS에 `python3 scripts/mark_progress.py ps <완료 ID>`를 실행합니다.",
            "",
        ]
    )
    return "\n".join(lines)


def resolve_date(
    value: str | None,
    timezone_name: str,
    now: datetime | None = None,
) -> date:
    if value is None:
        current = now or datetime.now(timezone.utc)
        return current.astimezone(ZoneInfo(timezone_name)).date()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RuntimeError("--date must use YYYY-MM-DD format") from exc


def main() -> int:
    args = parse_args()
    try:
        schedule = sync_schedule.load_schedule(args.schedule_config)
        report_date = resolve_date(args.date, schedule.timezone)
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
        report = render_report(
            report_date,
            lessons,
            tracks,
            progress,
            args.oss_config,
            args.oss_gate,
            schedule.timezone,
            schedule.hour,
            schedule.minute,
        )
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
