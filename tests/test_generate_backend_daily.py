from __future__ import annotations

import json
import copy
import io
import shutil
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

from scripts import generate_backend_daily as daily


class BackendDailyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lessons = daily.load_verified_backend_lessons()
        cls.tracks = daily.load_ps_tracks(daily.PS_CONFIG)

    def write_valid_oss_contracts(self, directory: Path) -> tuple[Path, Path]:
        config_path = directory / "oss-repositories.json"
        config_path.write_bytes(daily.OSS_CONFIG.read_bytes())

        gate_path = directory / "oss-delivery-gate.json"
        gate = json.loads(daily.OSS_GATE.read_text(encoding="utf-8"))
        gate.update(
            {
                "status": "LOCKED",
                "shadow_contract_sha256": daily.oss_gate.CURRENT_SHADOW_CONTRACT,
                "runs": [],
                "candidate_reviews": [],
                "approved_at": None,
            }
        )
        gate_path.write_text(json.dumps(gate), encoding="utf-8")
        return config_path, gate_path

    def test_real_catalogs_have_unique_items(self) -> None:
        lesson_ids = [lesson["id"] for lesson in self.lessons]
        problem_ids = [
            problem["id"]
            for track in self.tracks
            for problem in track["problems"]
        ]

        self.assertGreater(len(lesson_ids), 0)
        self.assertEqual(len(lesson_ids), 16)
        self.assertGreater(len(problem_ids), 0)
        self.assertEqual(len(lesson_ids), len(set(lesson_ids)))
        self.assertEqual(len(problem_ids), len(set(problem_ids)))

    def test_report_uses_first_incomplete_items(self) -> None:
        progress = {
            "backend_completed": [self.lessons[0]["id"]],
            "ps_solved": [self.tracks[0]["problems"][0]["id"]],
        }

        report = daily.render_report(
            date(2026, 7, 16), self.lessons, self.tracks, progress
        )

        self.assertIn(self.lessons[1]["title"], report)
        self.assertNotIn(f"완료 ID: `{self.lessons[0]['id']}`", report)
        self.assertIn(self.tracks[0]["problems"][1]["url"], report)
        self.assertIn("막히면 볼 힌트: ||", report)
        self.assertIn("남길 증거:", report)
        self.assertIn("검증 profile: `jvm-spring-2026q3-v1`", report)
        self.assertIn("검증 test ID:", report)
        self.assertIn("백엔드 1/", report)
        self.assertIn("기준일: 2026-07-16 · Asia/Seoul", report)
        self.assertNotIn("OPENAI_API_KEY", report)

    def test_report_has_four_ordered_sections_without_practical_cs_duplication(self) -> None:
        report_date = date(2026, 7, 17)
        progress = {
            "backend_completed": [self.lessons[0]["id"]],
            "ps_solved": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            config_path, gate_path = self.write_valid_oss_contracts(Path(directory))
            report = daily.render_report(
                report_date,
                self.lessons,
                self.tracks,
                progress,
                config_path,
                gate_path,
            )

        headings = [line for line in report.splitlines() if line.startswith("## ")]
        self.assertEqual(
            headings,
            [
                "## 오늘의 백엔드 실무",
                "## 오늘의 PS",
                "## 오늘의 OSS 기여 준비",
                "## 오늘의 백엔드 연결 CS 지식",
            ],
        )
        practical_section = report.split("## 오늘의 PS", 1)[0]
        practical_lesson = self.lessons[1]
        self.assertIn(practical_lesson["title"], practical_section)
        self.assertNotIn(practical_lesson["core_concept"], practical_section)
        self.assertNotIn(practical_lesson["failure_mode"], practical_section)
        self.assertNotIn(practical_lesson["check_question"], practical_section)

        cs_lesson = practical_lesson
        self.assertIn(
            f"### {practical_lesson['track']} — {practical_lesson['title']}",
            report,
        )
        self.assertEqual(report.count(cs_lesson["core_concept"]), 1)
        self.assertEqual(report.count(cs_lesson["failure_mode"]), 1)
        self.assertEqual(report.count(cs_lesson["check_question"]), 1)
        for reference in cs_lesson["official_refs"][:2]:
            self.assertEqual(report.count(f"]({reference})"), 1)

    def test_cs_rotation_fallback_is_date_based_and_ignores_unverified_lessons(self) -> None:
        first_date = date(2026, 7, 17)
        second_date = date(2026, 7, 18)
        first_lesson = daily.select_cs_lesson(self.lessons, first_date)
        second_lesson = daily.select_cs_lesson(self.lessons, second_date)
        self.assertIsNotNone(first_lesson)
        self.assertIsNotNone(second_lesson)
        assert first_lesson is not None and second_lesson is not None
        self.assertNotEqual(first_lesson["id"], second_lesson["id"])

        completed = {
            "backend_completed": [lesson["id"] for lesson in self.lessons],
            "ps_solved": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            config_path, gate_path = self.write_valid_oss_contracts(Path(directory))
            first_report = daily.render_report(
                first_date,
                self.lessons,
                self.tracks,
                completed,
                config_path,
                gate_path,
            )
            second_report = daily.render_report(
                second_date,
                self.lessons,
                self.tracks,
                completed,
                config_path,
                gate_path,
            )
        self.assertIn(first_lesson["core_concept"], first_report)
        self.assertIn(second_lesson["core_concept"], second_report)

        unverified = copy.deepcopy(self.lessons[0])
        unverified["_verification"] = {}
        only_verified = self.lessons[1]
        for report_date in (first_date, second_date):
            with self.subTest(report_date=report_date):
                selected = daily.select_cs_lesson(
                    [unverified, only_verified], report_date
                )
                self.assertEqual(selected["id"], only_verified["id"])

    def test_oss_prep_rotates_validated_profiles_and_hides_locked_candidates(self) -> None:
        report_date = date(2026, 7, 17)
        progress = {"backend_completed": [], "ps_solved": []}
        with tempfile.TemporaryDirectory() as directory:
            config_path, gate_path = self.write_valid_oss_contracts(Path(directory))
            config = daily.oss_collector.load_config(config_path, as_of=report_date)
            profile = daily.select_rotating_item(config["repositories"], report_date)
            next_profile = daily.select_rotating_item(
                config["repositories"], date(2026, 7, 18)
            )
            report = daily.render_report(
                report_date,
                self.lessons,
                self.tracks,
                progress,
                config_path,
                gate_path,
            )

        self.assertIsNotNone(profile)
        self.assertIsNotNone(next_profile)
        assert profile is not None and next_profile is not None
        self.assertNotEqual(profile["repository"], next_profile["repository"])
        oss_section = report.split("## 오늘의 OSS 기여 준비", 1)[1].split(
            "## 오늘의 백엔드 연결 CS 지식", 1
        )[0]
        repository = profile["repository"]
        build_command = profile["eligibility_evidence"]["build_test"]["command"]
        self.assertIn(f"https://github.com/{repository}", oss_section)
        self.assertIn(profile["relevance_reason"], oss_section)
        self.assertIn(profile["contributing_url"], oss_section)
        self.assertIn(build_command, oss_section)
        self.assertIn("전송 gate: `LOCKED`", oss_section)
        self.assertIn("연속 0/4주", oss_section)
        self.assertIn("후보 리뷰 0/10개", oss_section)
        self.assertNotIn("/issues/", oss_section)
        self.assertNotIn("READY_TO_ASK", oss_section)

    def test_invalid_oss_contracts_degrade_only_the_oss_section(self) -> None:
        report_date = date(2026, 7, 17)
        progress = {"backend_completed": [], "ps_solved": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path, gate_path = self.write_valid_oss_contracts(root)

            malformed_config = root / "malformed-config.json"
            malformed_config.write_text("{}", encoding="utf-8")
            expired_config = root / "expired-config.json"
            expired = json.loads(config_path.read_text(encoding="utf-8"))
            expired["valid_until"] = expired["checked_at"]
            expired_config.write_text(json.dumps(expired), encoding="utf-8")
            malformed_gate = root / "malformed-gate.json"
            malformed_gate.write_text("{}", encoding="utf-8")

            cases = (
                (malformed_config, gate_path),
                (expired_config, gate_path),
                (config_path, malformed_gate),
            )
            for selected_config, selected_gate in cases:
                with self.subTest(config=selected_config.name, gate=selected_gate.name):
                    report = daily.render_report(
                        report_date,
                        self.lessons,
                        self.tracks,
                        progress,
                        selected_config,
                        selected_gate,
                    )
                    oss_section = report.split(
                        "## 오늘의 OSS 기여 준비", 1
                    )[1].split("## 오늘의 백엔드 연결 CS 지식", 1)[0]
                    self.assertIn("OSS 계약을 검증하지 못해", oss_section)
                    self.assertIn(self.lessons[0]["title"], report)
                    self.assertIn(self.tracks[0]["problems"][0]["url"], report)
                    self.assertIn(self.lessons[0]["core_concept"], report)

    def test_approved_oss_prep_still_does_not_render_issue_candidates(self) -> None:
        report_date = date(2026, 7, 17)
        config = daily.oss_collector.load_config(
            daily.OSS_CONFIG, as_of=report_date
        )
        approved_brief = {
            "available": True,
            "profile": config["repositories"][0],
            "progress": {
                "status": "APPROVED",
                "consecutive_qualifying_weeks": 4,
                "unique_candidates": 10,
            },
            "requirements": daily.oss_gate.REQUIREMENTS,
        }
        with mock.patch.object(
            daily, "load_oss_brief", return_value=approved_brief
        ):
            report = daily.render_report(
                report_date,
                self.lessons,
                self.tracks,
                {"backend_completed": [], "ps_solved": []},
            )

        oss_section = report.split("## 오늘의 OSS 기여 준비", 1)[1].split(
            "## 오늘의 백엔드 연결 CS 지식", 1
        )[0]
        self.assertIn("전송 gate: `APPROVED`", oss_section)
        self.assertNotIn("/issues/", oss_section)
        self.assertNotIn("READY_TO_ASK", oss_section)

    def test_configured_timezone_drives_implicit_date_label_and_rotation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule_path = root / "delivery-schedule.json"
            schedule_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "timezone": "Pacific/Kiritimati",
                        "local_time": "09:00",
                    }
                ),
                encoding="utf-8",
            )
            schedule = daily.sync_schedule.load_schedule(schedule_path)
            reference_now = datetime(2026, 7, 16, 20, 0, tzinfo=timezone.utc)
            report_date = daily.resolve_date(
                None, schedule.timezone, now=reference_now
            )
            self.assertEqual(report_date, date(2026, 7, 17))

            config_path, gate_path = self.write_valid_oss_contracts(root)
            completed = {
                "backend_completed": [lesson["id"] for lesson in self.lessons],
                "ps_solved": [],
            }
            with mock.patch.object(
                daily.oss_gate,
                "evaluate_gate",
                wraps=daily.oss_gate.evaluate_gate,
            ) as evaluate_gate:
                report = daily.render_report(
                    report_date,
                    self.lessons,
                    self.tracks,
                    completed,
                    config_path,
                    gate_path,
                    schedule.timezone,
                    schedule.hour,
                    schedule.minute,
                )
            config = daily.oss_collector.load_config(
                config_path, as_of=report_date
            )
            evaluated_at = evaluate_gate.call_args.kwargs["now"]

        expected_profile = daily.select_rotating_item(
            config["repositories"], report_date
        )
        expected_cs = daily.select_cs_lesson(self.lessons, report_date)
        self.assertIsNotNone(expected_profile)
        self.assertIsNotNone(expected_cs)
        assert expected_profile is not None and expected_cs is not None
        self.assertEqual(
            evaluated_at,
            datetime(2026, 7, 16, 19, 0, tzinfo=timezone.utc),
        )
        self.assertIn("기준일: 2026-07-17 · Pacific/Kiritimati", report)
        self.assertIn(expected_profile["repository"], report)
        self.assertIn(expected_cs["core_concept"], report)
        self.assertEqual(
            daily.resolve_date(
                "2026-08-01", schedule.timezone, now=reference_now
            ),
            date(2026, 8, 1),
        )

    def test_invalid_schedule_config_fails_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule_path = root / "invalid-schedule.json"
            schedule_path.write_text("{}", encoding="utf-8")
            output_path = root / "backend-daily.md"
            argv = [
                "generate_backend_daily.py",
                "--date",
                "2026-07-17",
                "--schedule-config",
                str(schedule_path),
                "--output",
                str(output_path),
            ]
            stderr = io.StringIO()
            with mock.patch("sys.argv", argv), mock.patch("sys.stderr", stderr):
                result = daily.main()
            self.assertFalse(output_path.exists())

        self.assertEqual(result, 1)
        self.assertIn("Failed to generate Backend Daily", stderr.getvalue())

    def test_unknown_progress_id_is_rejected(self) -> None:
        progress = {"backend_completed": ["missing"], "ps_solved": []}
        with self.assertRaisesRegex(RuntimeError, "Unknown completed backend"):
            daily.validate_progress_ids(self.lessons, self.tracks, progress)

    def test_progress_file_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            path.write_text(
                json.dumps(
                    {
                        "backend_completed": ["same", "same"],
                        "ps_solved": [],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "duplicate ids"):
                daily.load_progress(path)

    def test_boolean_ps_level_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ps.json"
            payload = json.loads(daily.PS_CONFIG.read_text(encoding="utf-8"))
            payload["tracks"][0]["problems"][0]["level"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")

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
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Duplicate PS track id"):
                daily.load_ps_tracks(path)

    def test_lab_source_change_fails_closed_before_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lab = root / "lab"
            shutil.copytree(
                daily.LAB_DIR,
                lab,
                ignore=shutil.ignore_patterns(".gradle", ".kotlin", "build"),
            )
            source = lab / "src/main/kotlin/dev/careerfeed/lab/CareerLabApplication.kt"
            source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "verification is not current"):
                daily.load_verified_backend_lessons(
                    daily.BACKEND_CONFIG,
                    daily.MATRIX_CONFIG,
                    daily.PROFILE_CONFIG,
                    daily.TAXONOMY_CONFIG,
                    daily.VERIFICATION_MANIFEST,
                    lab,
                )


if __name__ == "__main__":
    unittest.main()
