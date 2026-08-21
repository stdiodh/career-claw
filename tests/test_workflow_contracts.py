from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github/workflows"
EXPECTED = {"oss-weekly.yml", "pr-checks.yml"}
PINNED_ACTION_RE = re.compile(
    r"^\s*uses:\s+[^\s@]+@[0-9a-f]{40}(?:\s+#\s+v\d+)?$",
    re.MULTILINE,
)


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = {
            path.name: path
            for path in WORKFLOW_DIR.iterdir()
            if path.is_file() and path.suffix in {".yml", ".yaml"}
        }
        cls.contents = {
            name: path.read_text(encoding="utf-8") for name, path in cls.paths.items()
        }

    def test_only_the_recommendation_workflows_are_active(self) -> None:
        self.assertEqual(set(self.paths), EXPECTED)

    def test_every_reusable_action_is_pinned_to_a_commit(self) -> None:
        for name, content in self.contents.items():
            uses_lines = [line for line in content.splitlines() if "uses:" in line]
            with self.subTest(workflow=name):
                self.assertTrue(uses_lines)
                for line in uses_lines:
                    self.assertRegex(line, PINNED_ACTION_RE)

    def test_workflows_are_read_only_and_not_scheduled(self) -> None:
        for name, content in self.contents.items():
            with self.subTest(workflow=name):
                self.assertIn("contents: read", content)
                self.assertNotIn("contents: write", content)
                self.assertNotIn("schedule:", content)
                self.assertNotIn("DISCORD_WEBHOOK", content)

    def test_recommendation_workflow_uploads_generated_artifacts(self) -> None:
        content = self.contents["oss-weekly.yml"]

        self.assertIn("--live-dry-run", content)
        self.assertIn("reports/oss-candidates.json", content)
        self.assertIn("reports/oss-candidates.md", content)
        self.assertIn("GITHUB_STEP_SUMMARY", content)
        self.assertIn("retention-days: 14", content)

    def test_pr_checks_do_not_install_the_removed_jvm_lab(self) -> None:
        content = self.contents["pr-checks.yml"]

        self.assertIn("./scripts/validate.sh", content)
        self.assertNotIn("setup-java", content)
        self.assertNotIn("RUN_POSTGRES_TESTS", content)


if __name__ == "__main__":
    unittest.main()
