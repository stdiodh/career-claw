from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import sync_delivery_schedule as sync_schedule


ROOT = Path(__file__).resolve().parents[1]


class DeliveryScheduleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "configs").mkdir()
        (self.root / ".github/workflows").mkdir(parents=True)
        self.write_config()
        for relative_path in sync_schedule.WORKFLOW_RECURRENCES:
            path = self.root / relative_path
            path.write_text(
                "name: Test\n\n"
                "on:\n"
                "  schedule:\n"
                '    - cron: "17 4 * * *"\n'
                "  workflow_dispatch:\n\n"
                "jobs: {}\n",
                encoding="utf-8",
            )
        for source_path in sync_schedule.delivery_gate.SHADOW_CONTRACT_PATHS:
            relative_path = source_path.relative_to(sync_schedule.delivery_gate.ROOT)
            path = self.root / relative_path
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"fixture for {relative_path}\n", encoding="utf-8")
        self.write_gate()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_config(self, **overrides: object) -> None:
        payload: dict[str, object] = {
            "schema_version": 1,
            "enabled": True,
            "timezone": "Asia/Seoul",
            "local_time": "09:00",
        }
        payload.update(overrides)
        (self.root / sync_schedule.CONFIG_PATH).write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def write_gate(self, **overrides: object) -> None:
        payload: dict[str, object] = {
            "status": "LOCKED",
            "shadow_contract_sha256": "sha256:" + "0" * 64,
            "runs": [],
            "candidate_reviews": [],
            "approved_at": None,
        }
        payload.update(overrides)
        (self.root / sync_schedule.GATE_PATH).write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    def test_repository_default_is_nine_am_in_seoul(self) -> None:
        schedule = sync_schedule.load_schedule(ROOT / sync_schedule.CONFIG_PATH)

        self.assertEqual(schedule.timezone, "Asia/Seoul")
        self.assertFalse(schedule.enabled)
        self.assertEqual(schedule.hour, 9)
        self.assertEqual(schedule.minute, 0)
        self.assertEqual(
            sync_schedule.calculate_shadow_contract(ROOT),
            sync_schedule.delivery_gate.CURRENT_SHADOW_CONTRACT,
        )

    def test_unknown_config_key_is_rejected(self) -> None:
        self.write_config(extra="value")

        with self.assertRaisesRegex(sync_schedule.ScheduleError, "unknown key"):
            sync_schedule.load_schedule(self.root / sync_schedule.CONFIG_PATH)

    def test_disabled_schedule_removes_and_can_restore_triggers(self) -> None:
        self.write_config(enabled=False)

        sync_schedule.synchronize(self.root)

        for relative_path in sync_schedule.WORKFLOW_RECURRENCES:
            content = (self.root / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("  schedule:", content)
            self.assertIn("  workflow_dispatch:", content)

        self.write_config(enabled=True)
        sync_schedule.synchronize(self.root)

        for relative_path in sync_schedule.WORKFLOW_RECURRENCES:
            content = (self.root / relative_path).read_text(encoding="utf-8")
            self.assertIn("  schedule:", content)

    def test_missing_config_key_is_rejected(self) -> None:
        path = self.root / sync_schedule.CONFIG_PATH
        path.write_text(
            json.dumps({"schema_version": 1, "timezone": "Asia/Seoul"}),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(sync_schedule.ScheduleError, "missing key"):
            sync_schedule.load_schedule(path)

    def test_invalid_local_times_are_rejected(self) -> None:
        for value in ("9:00", "24:00", "09:60", 900):
            with self.subTest(value=value):
                self.write_config(local_time=value)
                with self.assertRaisesRegex(
                    sync_schedule.ScheduleError, "zero-padded 24-hour HH:MM"
                ):
                    sync_schedule.load_schedule(self.root / sync_schedule.CONFIG_PATH)

    def test_unknown_iana_timezones_are_rejected(self) -> None:
        for value in ("Mars/Olympus_Mons", "../UTC"):
            with self.subTest(value=value):
                self.write_config(timezone=value)
                with self.assertRaisesRegex(
                    sync_schedule.ScheduleError, "Unknown IANA timezone"
                ):
                    sync_schedule.load_schedule(self.root / sync_schedule.CONFIG_PATH)

    def test_sync_uses_one_local_time_and_preserves_recurrence(self) -> None:
        self.write_config(timezone="America/New_York", local_time="23:45")

        changed = sync_schedule.synchronize(self.root)

        self.assertEqual(
            set(changed),
            {*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH},
        )
        daily = (self.root / ".github/workflows/backend-daily.yml").read_text(
            encoding="utf-8"
        )
        weekly = (self.root / ".github/workflows/oss-weekly.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('cron: "45 23 * * *"', daily)
        self.assertIn('cron: "45 23 * * 1"', weekly)
        self.assertIn('timezone: "America/New_York"', daily)
        self.assertIn('timezone: "America/New_York"', weekly)
        gate = json.loads((self.root / sync_schedule.GATE_PATH).read_text(encoding="utf-8"))
        self.assertEqual(
            gate["shadow_contract_sha256"],
            sync_schedule.calculate_shadow_contract(self.root),
        )

    def test_sync_refuses_without_writing_when_shadow_evidence_exists(self) -> None:
        self.write_gate(runs=[{"sentinel": "preserve"}])
        before = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }

        with self.assertRaisesRegex(sync_schedule.ScheduleError, "Refusing to change"):
            sync_schedule.synchronize(self.root)

        after = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }
        self.assertEqual(after, before)

    def test_sync_refuses_without_writing_when_gate_is_approved(self) -> None:
        self.write_gate(status="APPROVED", approved_at="2026-07-17T00:00:00Z")
        before = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }

        with self.assertRaisesRegex(sync_schedule.ScheduleError, "Refusing to change"):
            sync_schedule.synchronize(self.root)

        after = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }
        self.assertEqual(after, before)

    def test_sync_is_deterministic_and_check_detects_drift(self) -> None:
        initial = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }
        with self.assertRaisesRegex(
            sync_schedule.ScheduleError,
            r"backend-daily\.yml.*oss-weekly\.yml.*oss-delivery-gate\.json",
        ):
            sync_schedule.synchronize(self.root, check=True)
        before = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }
        self.assertEqual(before, initial)

        first_changed = sync_schedule.synchronize(self.root)
        after_first = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }
        second_changed = sync_schedule.synchronize(self.root)
        after_second = {
            path: (self.root / path).read_text(encoding="utf-8")
            for path in (*sync_schedule.WORKFLOW_RECURRENCES, sync_schedule.GATE_PATH)
        }

        self.assertTrue(first_changed)
        self.assertNotEqual(before, after_first)
        self.assertEqual(second_changed, [])
        self.assertEqual(after_first, after_second)
        self.assertEqual(sync_schedule.synchronize(self.root, check=True), [])


if __name__ == "__main__":
    unittest.main()
