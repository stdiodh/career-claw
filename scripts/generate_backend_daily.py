#!/usr/bin/env python3
"""Render a deterministic PS and official Spring update brief."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo

try:
    from . import sync_delivery_schedule as sync_schedule
except ImportError:
    import sync_delivery_schedule as sync_schedule


ROOT = Path(__file__).resolve().parents[1]
BACKEND_CONFIG = ROOT / "configs/backend-practice.json"
PS_CONFIG = ROOT / "configs/ps-problems.json"
PROGRESS_FILE = ROOT / "data/progress.json"
OUTPUT_FILE = ROOT / "reports/backend-daily.md"
SPRING_UPDATES_FILE = ROOT / "reports/spring-updates.json"
MATRIX_CONFIG = ROOT / "configs/curriculum-matrix.json"
PROFILE_CONFIG = ROOT / "configs/verification-profile.json"
TAXONOMY_CONFIG = ROOT / "configs/competency-taxonomy.json"
JOB_MARKET_AUDIT = ROOT / "audits/job-market-2026q3.json"
VERIFICATION_MANIFEST = ROOT / "data/curriculum-verification.json"
LAB_DIR = ROOT / "lab"
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
SPRING_UPDATE_FIELDS = {"title", "date", "link", "source"}
SPRING_RELEASE_PATHS = {
    "Spring Boot": "/spring-projects/spring-boot/releases/tag/",
    "Spring AI": "/spring-projects/spring-ai/releases/tag/",
}
MARKDOWN_SPECIAL_RE = re.compile(r"([\\`*_[\]()<>~|#])")


@dataclass(frozen=True)
class SpringUpdateBrief:
    status: str
    item: dict[str, str] | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format.")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    parser.add_argument("--ps-config", type=Path, default=PS_CONFIG)
    parser.add_argument("--progress", type=Path, default=PROGRESS_FILE)
    parser.add_argument("--spring-updates", type=Path, default=SPRING_UPDATES_FILE)
    parser.add_argument("--schedule-config", type=Path, default=SCHEDULE_CONFIG)
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument(
        "--stdout",
        action="store_true",
        help="Print the report after writing the output file.",
    )
    output_mode.add_argument(
        "--stdout-only",
        action="store_true",
        help="Print the report without writing the output file.",
    )
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


# These backend catalog helpers remain for the standalone progress command. Daily
# generation below never loads the curriculum, lab, manifest, or OSS contracts.
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
    try:
        from . import verify_curriculum
    except ImportError:
        import verify_curriculum

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
    unknown_lessons = sorted(set(progress["backend_completed"]) - lesson_ids)
    if unknown_lessons:
        raise RuntimeError(f"Unknown completed backend id(s): {', '.join(unknown_lessons)}")
    validate_ps_progress_ids(tracks, progress)


def validate_ps_progress_ids(
    tracks: list[dict[str, Any]], progress: dict[str, list[str]]
) -> None:
    unknown_problems = sorted(set(progress["ps_solved"]) - ps_problem_ids(tracks))
    if unknown_problems:
        raise RuntimeError(f"Unknown solved PS id(s): {', '.join(unknown_problems)}")


def select_ps_problem(
    tracks: list[dict[str, Any]], solved: set[str]
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    for track in tracks:
        for problem in track["problems"]:
            if problem["id"] not in solved:
                return track, problem
    return None


def validate_spring_release_url(link: str, source: str) -> None:
    prefix = SPRING_RELEASE_PATHS[source]
    parsed = urlsplit(link)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith(prefix)
    ):
        raise RuntimeError("Spring update link is outside the official release path")
    tag = unquote(parsed.path.removeprefix(prefix))
    if not tag or "/" in tag or link != f"https://github.com{parsed.path}":
        raise RuntimeError("Spring update release tag path is invalid")


def load_spring_update(path: Path, reference_date: date) -> dict[str, str] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Spring update result does not exist: {path}") from exc
    except UnicodeError as exc:
        raise RuntimeError(f"Spring update result is not valid UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid Spring update JSON in {path}: {exc}") from exc
    if payload is None:
        return None
    if not isinstance(payload, dict) or set(payload) != SPRING_UPDATE_FIELDS:
        raise RuntimeError("Spring update result must match the exact item schema")
    if not all(isinstance(payload[field], str) and payload[field].strip() for field in payload):
        raise RuntimeError("Spring update fields must be non-empty strings")
    title = payload["title"]
    if any(ord(character) < 32 for character in title):
        raise RuntimeError("Spring update title contains control characters")
    source = payload["source"]
    if source not in SPRING_RELEASE_PATHS:
        raise RuntimeError("Spring update source is not allowlisted")
    try:
        published_date = date.fromisoformat(payload["date"])
    except ValueError as exc:
        raise RuntimeError("Spring update date must use YYYY-MM-DD") from exc
    if published_date.isoformat() != payload["date"]:
        raise RuntimeError("Spring update date must use YYYY-MM-DD")
    age = reference_date - published_date
    if age.days < 0:
        raise RuntimeError("Spring update date is in the future")
    if age.days > 14:
        raise RuntimeError("Spring update result is older than 14 days")
    validate_spring_release_url(payload["link"], source)
    return {field: payload[field] for field in ("title", "date", "link", "source")}


def load_spring_update_brief(path: Path, reference_date: date) -> SpringUpdateBrief:
    try:
        item = load_spring_update(path, reference_date)
    except (OSError, RuntimeError):
        return SpringUpdateBrief("unavailable")
    if item is None:
        return SpringUpdateBrief("empty")
    return SpringUpdateBrief("available", item)


def escape_markdown_text(value: str) -> str:
    return MARKDOWN_SPECIAL_RE.sub(r"\\\1", value)


def render_ps_section(
    selection: tuple[dict[str, Any], dict[str, Any]] | None,
) -> list[str]:
    lines = ["## 오늘의 PS", ""]
    if selection is None:
        return lines + ["등록된 PS 문제를 모두 풀었습니다.", ""]

    track, problem = selection
    return lines + [
        f"### [{problem['title']}]({problem['url']})",
        f"- 트랙: {track['name']} — {track['goal']}",
        f"- 난이도: Level {problem['level']}",
        f"- 막히면 볼 힌트: ||{problem['first_thought']}||",
        f"- 완료 ID: `{problem['id']}`",
        f"- 완료 처리: `./career-feed done ps {problem['id']}`",
        "",
    ]


def render_spring_update_section(brief: SpringUpdateBrief) -> list[str]:
    lines = ["## 공식 Spring 새소식", ""]
    if brief.status == "unavailable":
        return lines + [
            "공식 Spring 새소식 수집 결과를 검증하지 못해 오늘은 항목을 노출하지 않습니다.",
            "- 검증 상태: 수집 결과 누락 또는 계약 오류로 fail-closed",
            "",
        ]
    if brief.status == "empty":
        return lines + [
            "최근 14일 내 공식 Spring Boot 또는 Spring AI 릴리스가 없습니다.",
            "",
        ]
    if brief.status != "available" or brief.item is None:
        raise RuntimeError("Unknown Spring update brief status")
    item = brief.item
    return lines + [
        f"### [{escape_markdown_text(item['title'])}]({item['link']})",
        f"- 날짜: {item['date']}",
        f"- 출처: {item['source']}",
        "",
    ]


def render_report(
    report_date: date,
    tracks: list[dict[str, Any]],
    progress: dict[str, list[str]],
    spring_update: SpringUpdateBrief,
    report_timezone: str = DEFAULT_TIMEZONE,
) -> str:
    solved = set(progress["ps_solved"])
    ps_selection = select_ps_problem(tracks, solved)
    lines: list[str] = [
        "# Career Feed - Backend Daily",
        "",
        f"기준일: {report_date.isoformat()} · {report_timezone}",
        "",
        f"진행: PS {len(solved)}/{len(ps_problem_ids(tracks))}",
        "",
    ]
    lines.extend(render_ps_section(ps_selection))
    lines.extend(render_spring_update_section(spring_update))
    lines.extend(
        [
            "---",
            "",
            "로컬에서는 PS 항목의 `완료 처리` 명령을 실행합니다.",
            "GitHub Actions의 `Mark Progress`에서는 PS와 완료 ID를 입력합니다.",
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
        tracks = load_ps_tracks(args.ps_config)
        progress = load_progress(args.progress)
        validate_ps_progress_ids(tracks, progress)
        spring_update = load_spring_update_brief(args.spring_updates, report_date)
        report = render_report(
            report_date,
            tracks,
            progress,
            spring_update,
            schedule.timezone,
        )
        if not args.stdout_only:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
    except (OSError, RuntimeError) as exc:
        print(f"Failed to generate Backend Daily: {exc}", file=sys.stderr)
        return 1

    if args.stdout or args.stdout_only:
        print(report, end="")
    if not args.stdout_only:
        print(f"Wrote Backend Daily: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
