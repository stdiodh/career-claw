from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts import sync_delivery_schedule as sync_schedule


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github/workflows"
EXPECTED = {
    "backend-daily.yml",
    "mark-progress.yml",
    "oss-weekly.yml",
    "pr-checks.yml",
}
PINNED_ACTION_RE = re.compile(r"^\s*uses:\s+[^\s@]+@[0-9a-f]{40}(?:\s+#\s+v\d+)?$", re.MULTILINE)


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

    def test_only_the_four_product_workflows_are_active(self) -> None:
        self.assertEqual(set(self.paths), EXPECTED)

    def test_every_reusable_action_is_pinned_to_a_commit(self) -> None:
        for name, content in self.contents.items():
            uses_lines = [line for line in content.splitlines() if "uses:" in line]
            with self.subTest(workflow=name):
                self.assertTrue(uses_lines)
                for line in uses_lines:
                    self.assertRegex(line, PINNED_ACTION_RE)

    def test_only_progress_workflow_can_write_contents(self) -> None:
        for name, content in self.contents.items():
            expected = "contents: write" if name == "mark-progress.yml" else "contents: read"
            with self.subTest(workflow=name):
                self.assertIn(expected, content)
                if name != "mark-progress.yml":
                    self.assertNotIn("contents: write", content)

    def test_daily_run_exposes_the_brief_in_summary(self) -> None:
        daily = self.contents["backend-daily.yml"]

        self.assertIn("GITHUB_STEP_SUMMARY", daily)

    def test_daily_collects_spring_updates_fail_soft_before_generation(self) -> None:
        daily = self.contents["backend-daily.yml"]
        collect = daily.index("name: Collect official Spring updates")
        remove_stale = daily.index("rm -f reports/spring-updates.json")
        collector = daily.index("python3 scripts/collect_spring_updates.py")
        generate = daily.index("name: Generate deterministic brief")

        self.assertLess(collect, remove_stale)
        self.assertLess(remove_stale, collector)
        self.assertLess(collector, generate)
        self.assertIn("continue-on-error: true", daily[collect:generate])
        self.assertIn("--live-dry-run", daily[collect:generate])
        self.assertIn(
            "--spring-updates reports/spring-updates.json",
            daily[generate:],
        )

    def test_delivery_workflows_match_the_single_local_time_config(self) -> None:
        schedule = sync_schedule.load_schedule(ROOT / sync_schedule.CONFIG_PATH)
        self.assertFalse(schedule.enabled)
        for relative_path, recurrence in sync_schedule.WORKFLOW_RECURRENCES.items():
            with self.subTest(workflow=relative_path.name):
                self.assertNotIn("  schedule:", self.contents[relative_path.name])

        self.assertEqual(
            sync_schedule.WORKFLOW_RECURRENCES[
                Path(".github/workflows/backend-daily.yml")
            ],
            "* * *",
        )
        self.assertEqual(
            sync_schedule.WORKFLOW_RECURRENCES[
                Path(".github/workflows/oss-weekly.yml")
            ],
            "* * 1",
        )

    def test_discord_delivery_uses_the_canonical_secret_with_migration_fallback(self) -> None:
        binding = (
            "${{ secrets.DISCORD_WEBHOOK_URL || "
            "secrets.DISCORD_WEBHOOK_KR_TECH_DAILY }}"
        )
        for name in ("backend-daily.yml", "oss-weekly.yml"):
            with self.subTest(workflow=name):
                self.assertIn(binding, self.contents[name])

    def test_oss_delivery_requires_collector_gate_variable_and_non_dry_run(self) -> None:
        content = self.contents["oss-weekly.yml"]
        collect = content.index("name: Collect candidates")
        gate = content.index("name: Evaluate tracked Shadow delivery gate")
        delivery = content.index("name: Send verified candidates to Discord")
        metadata = content.index("name: Bind workflow provenance to Shadow evidence")
        artifact = content.index("name: Upload immutable Shadow evidence")
        failure = content.index("name: Fail incomplete collection after evidence upload")

        self.assertLess(collect, gate)
        self.assertLess(gate, delivery)
        self.assertLess(delivery, metadata)
        self.assertLess(metadata, artifact)
        self.assertLess(delivery, failure)
        self.assertIn("github.repository == 'stdiodh/career-feed'", content)
        self.assertIn("github.ref == 'refs/heads/main'", content)
        self.assertIn("steps.collector.outputs.exit_code == '0'", content)
        self.assertIn("steps.delivery-gate.outputs.approved == 'true'", content)
        self.assertIn("vars.OSS_DELIVERY_ENABLED == 'true'", content)
        self.assertIn("inputs.dry_run == false", content)
        self.assertIn("record_oss_shadow.py build-metadata", content)
        self.assertIn("oss-weekly-${{ github.run_id }}-${{ github.run_attempt }}", content)
        self.assertIn("reports/oss-run-metadata.json", content)
        self.assertIn("retention-days: 90", content)
        self.assertIn("rm -f reports/oss-candidates.json", content)
        self.assertLess(
            content.index('echo "sent=yes" >> "${GITHUB_OUTPUT}"'),
            content.index("python3 scripts/send_discord.py"),
        )
        self.assertIn("Count a started delivery conservatively", content)
        self.assertNotIn("cancel-in-progress", content)
        self.assertNotIn("secrets.GITHUB_TOKEN", content)
        self.assertNotIn("github.token", content)


if __name__ == "__main__":
    unittest.main()
