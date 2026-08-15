from __future__ import annotations

import copy
from datetime import date, datetime, timezone
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import generate_backend_daily as daily


class BackendDailyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tracks = daily.load_ps_tracks(daily.PS_CONFIG)

    def valid_update(self, **changes: str) -> dict[str, str]:
        update = {
            "title": "Spring AI 2.0.0",
            "date": "2026-08-07",
            "link": "https://github.com/spring-projects/spring-ai/releases/tag/v2.0.0",
            "source": "Spring AI",
        }
        update.update(changes)
        return update

    def progress(self, solved: list[str] | None = None) -> dict[str, list[str]]:
        return {"backend_completed": [], "ps_solved": solved or []}

    def write_json(self, path: Path, payload: object) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def invoke_main(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch("sys.argv", argv),
            mock.patch("sys.stdout", stdout),
            mock.patch("sys.stderr", stderr),
        ):
            result = daily.main()
        return result, stdout.getvalue(), stderr.getvalue()

    def test_real_ps_catalog_has_unique_items(self) -> None:
        problem_ids = [
            problem["id"]
            for track in self.tracks
            for problem in track["problems"]
        ]

        self.assertEqual(len(problem_ids), 40)
        self.assertEqual(len(problem_ids), len(set(problem_ids)))

    def test_report_has_exactly_ps_and_spring_update_sections(self) -> None:
        report = daily.render_report(
            date(2026, 8, 15),
            self.tracks,
            self.progress(),
            daily.SpringUpdateBrief("available", self.valid_update()),
        )

        headings = [line for line in report.splitlines() if line.startswith("## ")]
        self.assertEqual(headings, ["## 오늘의 PS", "## 공식 Spring 새소식"])
        self.assertIn("진행: PS 0/40", report)
        self.assertNotIn("백엔드 실무", report)
        self.assertNotIn("OSS 기여 준비", report)
        self.assertNotIn("연결 CS 지식", report)

    def test_report_uses_the_first_unsolved_ps_problem(self) -> None:
        first = self.tracks[0]["problems"][0]
        second = self.tracks[0]["problems"][1]
        report = daily.render_report(
            date(2026, 8, 15),
            self.tracks,
            self.progress([first["id"]]),
            daily.SpringUpdateBrief("empty"),
        )

        self.assertIn(second["url"], report)
        self.assertNotIn(f"완료 ID: `{first['id']}`", report)
        self.assertIn(f"완료 처리: `./career-feed done ps {second['id']}`", report)
        self.assertIn("진행: PS 1/40", report)

    def test_report_shows_completion_when_every_ps_problem_is_solved(self) -> None:
        solved = [
            problem["id"]
            for track in self.tracks
            for problem in track["problems"]
        ]

        report = daily.render_report(
            date(2026, 8, 15),
            self.tracks,
            self.progress(solved),
            daily.SpringUpdateBrief("empty"),
        )

        self.assertIn("진행: PS 40/40", report)
        self.assertIn("등록된 PS 문제를 모두 풀었습니다.", report)

    def test_valid_spring_update_has_only_trusted_fields_and_escaped_title(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spring-updates.json"
            self.write_json(
                path,
                self.valid_update(title="[Spring] *AI* #2"),
            )
            brief = daily.load_spring_update_brief(path, date(2026, 8, 15))

        report = daily.render_report(
            date(2026, 8, 15), self.tracks, self.progress(), brief
        )
        assert brief.item is not None
        self.assertEqual(set(brief.item), {"title", "date", "link", "source"})
        self.assertIn(r"### [\[Spring\] \*AI\* \#2]", report)
        self.assertIn("- 날짜: 2026-08-07", report)
        self.assertIn("- 출처: Spring AI", report)

    def test_spring_update_requires_the_exact_schema(self) -> None:
        invalid_payloads = (
            [],
            {**self.valid_update(), "summary": "not allowed"},
            {key: value for key, value in self.valid_update().items() if key != "date"},
            {**self.valid_update(), "title": 2},
            {**self.valid_update(), "title": "line one\n## injected"},
        )
        for index, payload in enumerate(invalid_payloads):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "spring-updates.json"
                self.write_json(path, payload)
                with self.assertRaises(RuntimeError):
                    daily.load_spring_update(path, date(2026, 8, 15))

    def test_spring_update_source_and_release_path_must_match(self) -> None:
        invalid_items = (
            self.valid_update(source="Spring Framework"),
            self.valid_update(
                source="Spring Boot",
                link="https://github.com/spring-projects/spring-ai/releases/tag/v2.0.0",
            ),
            self.valid_update(link="https://evil.example/releases/tag/v2.0.0"),
            self.valid_update(
                link=(
                    "https://github.com/spring-projects/spring-ai/releases/tag/"
                    "v2.0.0?download=1"
                )
            ),
            self.valid_update(
                link=(
                    "https://github.com/spring-projects/spring-ai/releases/tag/"
                    "nested/v2.0.0"
                )
            ),
        )
        for index, item in enumerate(invalid_items):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "spring-updates.json"
                self.write_json(path, item)
                with self.assertRaises(RuntimeError):
                    daily.load_spring_update(path, date(2026, 8, 15))

    def test_spring_update_date_must_be_current_and_canonical(self) -> None:
        invalid_dates = ("2026-08-16", "2026-07-31", "2026-8-7", "not-a-date")
        for value in invalid_dates:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "spring-updates.json"
                self.write_json(path, self.valid_update(date=value))
                with self.assertRaises(RuntimeError):
                    daily.load_spring_update(path, date(2026, 8, 15))

        with tempfile.TemporaryDirectory() as directory:
            boundary = Path(directory) / "spring-updates.json"
            self.write_json(boundary, self.valid_update(date="2026-08-01"))
            self.assertIsNotNone(daily.load_spring_update(boundary, date(2026, 8, 15)))

    def test_null_spring_result_is_a_normal_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spring-updates.json"
            self.write_json(path, None)
            brief = daily.load_spring_update_brief(path, date(2026, 8, 15))

        report = daily.render_report(
            date(2026, 8, 15), self.tracks, self.progress(), brief
        )
        self.assertEqual(brief.status, "empty")
        self.assertIn(
            "최근 14일 내 공식 Spring Boot 또는 Spring AI 릴리스가 없습니다.",
            report,
        )

    def test_missing_malformed_or_untrusted_spring_result_fails_only_its_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.json"
            malformed = root / "malformed.json"
            malformed.write_text("{", encoding="utf-8")
            non_utf8 = root / "non-utf8.json"
            non_utf8.write_bytes(b"\xff")
            untrusted = root / "untrusted.json"
            self.write_json(
                untrusted,
                self.valid_update(link="https://example.com/releases/tag/v2.0.0"),
            )

            for path in (missing, malformed, non_utf8, untrusted):
                with self.subTest(path=path.name):
                    brief = daily.load_spring_update_brief(path, date(2026, 8, 15))
                    report = daily.render_report(
                        date(2026, 8, 15), self.tracks, self.progress(), brief
                    )
                    self.assertEqual(brief.status, "unavailable")
                    self.assertIn(self.tracks[0]["problems"][0]["url"], report)
                    self.assertIn("수집 결과 누락 또는 계약 오류로 fail-closed", report)

    def test_default_and_explicit_spring_update_option_contract(self) -> None:
        with mock.patch("sys.argv", ["generate_backend_daily.py", "--stdout-only"]):
            args = daily.parse_args()
        self.assertEqual(args.spring_updates, daily.SPRING_UPDATES_FILE)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            update_path = root / "custom-update.json"
            output_path = root / "backend-daily.md"
            self.write_json(update_path, self.valid_update())
            result, stdout, stderr = self.invoke_main(
                [
                    "generate_backend_daily.py",
                    "--date",
                    "2026-08-15",
                    "--spring-updates",
                    str(update_path),
                    "--output",
                    str(output_path),
                    "--stdout",
                ]
            )

            self.assertEqual(result, 0, stderr)
            self.assertTrue(output_path.is_file())
            self.assertIn("Spring AI 2.0.0", output_path.read_text(encoding="utf-8"))
            self.assertIn("Spring AI 2.0.0", stdout)

    def test_main_missing_spring_file_still_generates_the_ps_brief(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_path = root / "backend-daily.md"
            missing = root / "missing.json"
            result, stdout, stderr = self.invoke_main(
                [
                    "generate_backend_daily.py",
                    "--date",
                    "2026-08-15",
                    "--spring-updates",
                    str(missing),
                    "--output",
                    str(output_path),
                    "--stdout",
                ]
            )

            report = output_path.read_text(encoding="utf-8")
            self.assertEqual(result, 0, stderr)
            self.assertIn(self.tracks[0]["problems"][0]["url"], report)
            self.assertIn("fail-closed", report)
            self.assertEqual(report, stdout)

    def test_daily_main_does_not_load_curriculum_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            update_path = Path(directory) / "spring-updates.json"
            self.write_json(update_path, self.valid_update())
            argv = [
                "generate_backend_daily.py",
                "--date",
                "2026-08-15",
                "--spring-updates",
                str(update_path),
                "--stdout-only",
            ]
            with (
                mock.patch.object(
                    daily,
                    "load_backend_lessons",
                    side_effect=AssertionError("curriculum loaded"),
                ),
                mock.patch.object(
                    daily,
                    "load_verified_backend_lessons",
                    side_effect=AssertionError("manifest loaded"),
                ),
            ):
                result, stdout, stderr = self.invoke_main(argv)

        self.assertEqual(result, 0, stderr)
        self.assertIn("## 오늘의 PS", stdout)

    def test_stdout_only_mode_does_not_write_the_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_path = root / "backend-daily.md"
            update_path = root / "spring-updates.json"
            self.write_json(update_path, self.valid_update())
            result, stdout, stderr = self.invoke_main(
                [
                    "generate_backend_daily.py",
                    "--date",
                    "2026-08-15",
                    "--spring-updates",
                    str(update_path),
                    "--output",
                    str(output_path),
                    "--stdout-only",
                ]
            )

            self.assertFalse(output_path.exists())
        self.assertEqual(result, 0)
        self.assertIn("# Career Feed - Backend Daily", stdout)
        self.assertEqual(stderr, "")

    def test_configured_timezone_drives_the_implicit_date_label(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule_path = root / "delivery-schedule.json"
            self.write_json(
                schedule_path,
                {
                    "schema_version": 1,
                    "enabled": True,
                    "timezone": "Pacific/Kiritimati",
                    "local_time": "09:00",
                },
            )
            schedule = daily.sync_schedule.load_schedule(schedule_path)
            reference_now = datetime(2026, 8, 14, 20, 0, tzinfo=timezone.utc)
            report_date = daily.resolve_date(None, schedule.timezone, now=reference_now)

        self.assertEqual(report_date, date(2026, 8, 15))
        report = daily.render_report(
            report_date,
            self.tracks,
            self.progress(),
            daily.SpringUpdateBrief("empty"),
            schedule.timezone,
        )
        self.assertIn("기준일: 2026-08-15 · Pacific/Kiritimati", report)

    def test_generator_compares_release_date_with_local_report_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule_path = root / "delivery-schedule.json"
            self.write_json(
                schedule_path,
                {
                    "schema_version": 1,
                    "enabled": True,
                    "timezone": "Pacific/Kiritimati",
                    "local_time": "09:00",
                },
            )
            update_path = root / "spring-updates.json"
            self.write_json(update_path, self.valid_update(date="2026-08-15"))
            output_path = root / "backend-daily.md"

            result, stdout, stderr = self.invoke_main(
                [
                    "generate_backend_daily.py",
                    "--date",
                    "2026-08-15",
                    "--schedule-config",
                    str(schedule_path),
                    "--spring-updates",
                    str(update_path),
                    "--output",
                    str(output_path),
                    "--stdout",
                ]
            )

            report = output_path.read_text(encoding="utf-8")
        self.assertEqual(result, 0, stderr)
        self.assertEqual(report, stdout)
        self.assertIn("Spring AI 2.0.0", report)
        self.assertNotIn("fail-closed", report)

    def test_invalid_schedule_config_fails_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule_path = root / "invalid-schedule.json"
            schedule_path.write_text("{}", encoding="utf-8")
            output_path = root / "backend-daily.md"
            result, _, stderr = self.invoke_main(
                [
                    "generate_backend_daily.py",
                    "--date",
                    "2026-08-15",
                    "--schedule-config",
                    str(schedule_path),
                    "--output",
                    str(output_path),
                ]
            )

            self.assertFalse(output_path.exists())
        self.assertEqual(result, 1)
        self.assertIn("Failed to generate Backend Daily", stderr)

    def test_daily_ignores_legacy_backend_progress_but_rejects_unknown_ps_ids(self) -> None:
        progress = {"backend_completed": ["legacy-id"], "ps_solved": []}
        daily.validate_ps_progress_ids(self.tracks, progress)

        progress["ps_solved"] = ["missing"]
        with self.assertRaisesRegex(RuntimeError, "Unknown solved PS"):
            daily.validate_ps_progress_ids(self.tracks, progress)

    def test_progress_file_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            self.write_json(
                path,
                {"backend_completed": [], "ps_solved": ["same", "same"]},
            )
            with self.assertRaisesRegex(RuntimeError, "duplicate ids"):
                daily.load_progress(path)

    def test_boolean_ps_level_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ps.json"
            payload = json.loads(daily.PS_CONFIG.read_text(encoding="utf-8"))
            payload["tracks"][0]["problems"][0]["level"] = True
            self.write_json(path, payload)
            with self.assertRaisesRegex(RuntimeError, "level must be"):
                daily.load_ps_tracks(path)

    def test_duplicate_ps_track_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ps.json"
            payload = json.loads(daily.PS_CONFIG.read_text(encoding="utf-8"))
            payload["tracks"].append(copy.deepcopy(payload["tracks"][0]))
            payload["tracks"][-1]["problems"] = [
                {**payload["tracks"][-1]["problems"][0], "id": "unique-problem"}
            ]
            self.write_json(path, payload)
            with self.assertRaisesRegex(RuntimeError, "Duplicate PS track id"):
                daily.load_ps_tracks(path)


if __name__ == "__main__":
    unittest.main()
