from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "career-feed"


class CareerFeedCliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(CLI), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_no_arguments_prints_today_without_writing_a_report(self) -> None:
        result = self.run_cli()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("# Career Feed - Backend Daily", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_done_marks_the_explicit_item(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            progress = Path(directory) / "progress.json"
            progress.write_text(
                json.dumps({"backend_completed": [], "ps_solved": []}),
                encoding="utf-8",
            )

            result = self.run_cli(
                "done",
                "ps",
                "programmers-1845",
                "--progress",
                str(progress),
            )

            payload = json.loads(progress.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(payload["ps_solved"], ["programmers-1845"])

    def test_help_is_available_without_loading_the_catalog(self) -> None:
        result = self.run_cli("--help")
        today_result = self.run_cli("today", "--help")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(today_result.returncode, 0)
        self.assertIn("./career-feed done <backend|ps> <완료 ID>", result.stdout)
        self.assertIn("오늘 또는 지정일 브리핑 보기", today_result.stdout)

    def test_today_rejects_output_options_instead_of_silently_ignoring_them(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "backend-daily.md"

            result = self.run_cli("today", "--output", str(output))

            self.assertFalse(output.exists())
        self.assertEqual(result.returncode, 2)
        self.assertIn("--date YYYY-MM-DD 옵션만", result.stderr)


if __name__ == "__main__":
    unittest.main()
