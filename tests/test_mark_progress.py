from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import mark_progress


class MarkProgressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.progress_path = Path(self.temp_dir.name) / "progress.json"
        self.progress_path.write_text(
            json.dumps({"backend_completed": [], "ps_solved": []}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_marks_backend_item_once(self) -> None:
        item_id = "api-post-idempotency-payment-duplicate"

        changed = mark_progress.mark_complete(
            "backend",
            item_id,
            self.progress_path,
            mark_progress.BACKEND_CONFIG,
            mark_progress.PS_CONFIG,
        )
        changed_again = mark_progress.mark_complete(
            "backend",
            item_id,
            self.progress_path,
            mark_progress.BACKEND_CONFIG,
            mark_progress.PS_CONFIG,
        )

        payload = json.loads(self.progress_path.read_text(encoding="utf-8"))
        self.assertTrue(changed)
        self.assertFalse(changed_again)
        self.assertEqual(payload["backend_completed"], [item_id])

    def test_marks_ps_item(self) -> None:
        item_id = "programmers-1845"
        mark_progress.mark_complete(
            "ps",
            item_id,
            self.progress_path,
            mark_progress.BACKEND_CONFIG,
            mark_progress.PS_CONFIG,
        )

        payload = json.loads(self.progress_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["ps_solved"], [item_id])

    def test_rejects_unknown_item(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Unknown backend id"):
            mark_progress.mark_complete(
                "backend",
                "not-in-catalog",
                self.progress_path,
                mark_progress.BACKEND_CONFIG,
                mark_progress.PS_CONFIG,
            )

    def test_concurrent_updates_are_not_lost(self) -> None:
        commands = [
            [
                sys.executable,
                str(mark_progress.ROOT / "scripts/mark_progress.py"),
                item_type,
                item_id,
                "--progress",
                str(self.progress_path),
            ]
            for item_type, item_id in (
                ("backend", "server-check-process"),
                ("ps", "programmers-1845"),
            )
        ]
        processes = [
            subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for command in commands
        ]

        results = [process.communicate() for process in processes]
        self.assertTrue(
            all(process.returncode == 0 for process in processes),
            msg=str(results),
        )
        payload = json.loads(self.progress_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["backend_completed"], ["server-check-process"])
        self.assertEqual(payload["ps_solved"], ["programmers-1845"])


if __name__ == "__main__":
    unittest.main()
