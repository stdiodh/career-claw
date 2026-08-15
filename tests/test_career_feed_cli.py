from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "career-feed"
SPRING_FIXTURE = ROOT / "tests/fixtures/spring-updates.json"


class CareerFeedCliTests(unittest.TestCase):
    def run_cli(
        self,
        *arguments: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(CLI), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def test_no_arguments_prints_today_without_writing_a_report(self) -> None:
        env = os.environ.copy()
        env["CAREER_FEED_SPRING_FIXTURE"] = str(SPRING_FIXTURE)

        result = self.run_cli(env=env)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("# Career Feed - Backend Daily", result.stdout)
        self.assertEqual(
            [line for line in result.stdout.splitlines() if line.startswith("## ")],
            ["## 오늘의 PS", "## 공식 Spring 새소식"],
        )
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
        self.assertIn("./career-feed oss", result.stdout)
        self.assertIn("오늘 또는 지정일 브리핑 보기", today_result.stdout)

    def test_oss_runs_the_read_only_live_collector_and_prints_to_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            fake_python = fake_bin / "python3"
            fake_python.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$@"\n',
                encoding="utf-8",
            )
            fake_python.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

            result = self.run_cli("oss", env=env)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                str(ROOT / "scripts/collect_oss_candidates.py"),
                "--live-dry-run",
                "--stdout",
            ],
        )
        self.assertEqual(result.stderr, "")

    def test_oss_rejects_additional_arguments(self) -> None:
        result = self.run_cli("oss", "--fixture", "fixture.json")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "oss 명령은 추가 옵션을 받지 않습니다.\n")

    def test_today_uses_the_spring_fixture_and_preserves_the_date_argument(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            call_log = root / "calls.log"
            fake_python = fake_bin / "python3"
            fake_python.write_text(
                "#!/bin/sh\n"
                "printf 'CALL\\n' >> \"${CAREER_FEED_CALL_LOG}\"\n"
                "printf '%s\\n' \"$@\" >> \"${CAREER_FEED_CALL_LOG}\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
            env["CAREER_FEED_CALL_LOG"] = str(call_log)
            env["CAREER_FEED_SPRING_FIXTURE"] = str(SPRING_FIXTURE)

            result = self.run_cli("today", "--date", "2026-08-15", env=env)
            calls = [
                block.splitlines()
                for block in call_log.read_text(encoding="utf-8").split("CALL\n")
                if block
            ]

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            calls[0][:5],
            [
                str(ROOT / "scripts/collect_spring_updates.py"),
                "--fixture",
                str(SPRING_FIXTURE),
                "--as-of",
                "2026-08-15",
            ],
        )
        self.assertEqual(calls[0][5], "--output")
        self.assertEqual(
            calls[1],
            [
                str(ROOT / "scripts/generate_backend_daily.py"),
                "--stdout-only",
                "--spring-updates",
                calls[0][6],
                "--date",
                "2026-08-15",
            ],
        )
        self.assertFalse(Path(calls[0][6]).parent.exists())

    def test_historical_date_selects_the_release_available_on_that_date(self) -> None:
        env = os.environ.copy()
        env["CAREER_FEED_SPRING_FIXTURE"] = str(SPRING_FIXTURE)

        result = self.run_cli("today", "--date", "2026-08-04", env=env)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Spring AI", result.stdout)
        self.assertIn("v1.0.1", result.stdout)
        self.assertIn("2026-08-04", result.stdout)
        self.assertNotIn("수집 결과 누락 또는 계약 오류", result.stdout)

    def test_today_passes_a_missing_spring_path_when_collection_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            fake_python = fake_bin / "python3"
            fake_python.write_text(
                "#!/bin/sh\n"
                "case \"$1\" in\n"
                "  */collect_spring_updates.py) exit 1 ;;\n"
                "  *) printf '%s\\n' \"$@\" ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

            result = self.run_cli("today", "--date=2026-08-15", env=env)

        generator_arguments = result.stdout.splitlines()
        spring_updates = Path(generator_arguments[3])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            generator_arguments[:3],
            [
                str(ROOT / "scripts/generate_backend_daily.py"),
                "--stdout-only",
                "--spring-updates",
            ],
        )
        self.assertEqual(generator_arguments[4], "--date=2026-08-15")
        self.assertEqual(spring_updates.name, "missing-spring-updates.json")
        self.assertFalse(spring_updates.parent.exists())
        self.assertIn("PS 브리핑은 계속 생성합니다", result.stderr)

    def test_today_keeps_ps_available_when_spring_collection_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ.copy()
            env["CAREER_FEED_SPRING_FIXTURE"] = str(
                Path(directory) / "missing-spring-fixture.json"
            )

            result = self.run_cli("today", "--date", "2026-08-15", env=env)

        self.assertEqual(result.returncode, 0)
        self.assertIn("## 오늘의 PS", result.stdout)
        self.assertIn("## 공식 Spring 새소식", result.stdout)
        self.assertIn("수집 결과 누락 또는 계약 오류로 fail-closed", result.stdout)
        self.assertIn("PS 브리핑은 계속 생성합니다", result.stderr)

    def test_today_rejects_output_options_instead_of_silently_ignoring_them(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "backend-daily.md"

            result = self.run_cli("today", "--output", str(output))

            self.assertFalse(output.exists())
        self.assertEqual(result.returncode, 2)
        self.assertIn("--date YYYY-MM-DD 옵션만", result.stderr)


if __name__ == "__main__":
    unittest.main()
