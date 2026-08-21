from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "career-feed"


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

    def test_no_arguments_runs_the_read_only_collector(self) -> None:
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

            result = self.run_cli(env=env)

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

    def test_help_describes_only_the_recommendation_commands(self) -> None:
        result = self.run_cli("--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("./career-feed          공개 GitHub API로 후보 확인", result.stdout)
        self.assertIn("./career-feed check", result.stdout)
        self.assertNotIn("today", result.stdout)
        self.assertNotIn("done", result.stdout)
        self.assertNotIn("Discord", result.stdout)

    def test_check_rejects_additional_arguments(self) -> None:
        result = self.run_cli("check", "extra")

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "check 명령은 추가 옵션을 받지 않습니다.\n")

    def test_removed_commands_are_rejected(self) -> None:
        for command in ("today", "done", "oss"):
            with self.subTest(command=command):
                result = self.run_cli(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn(f"알 수 없는 명령: {command}", result.stderr)


if __name__ == "__main__":
    unittest.main()
