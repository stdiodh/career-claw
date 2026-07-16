from __future__ import annotations

import json
import copy
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts import generate_backend_daily as daily


class BackendDailyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lessons = daily.load_verified_backend_lessons()
        cls.tracks = daily.load_ps_tracks(daily.PS_CONFIG)

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
        self.assertNotIn("OPENAI_API_KEY", report)

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
