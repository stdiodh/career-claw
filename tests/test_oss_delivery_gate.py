from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import check_oss_delivery_gate as gate
from scripts import record_oss_shadow as record


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)
RUN_DATES = (
    "2026-06-15",
    "2026-06-22",
    "2026-06-29",
    "2026-07-06",
    "2026-07-13",
)


class OssDeliveryGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = "spring-projects/spring-boot"
        self.other_repository = "micrometer-metrics/micrometer"
        self.repositories = {self.repository, self.other_repository}
        self.locked = {
            "schema_version": 3,
            "status": "LOCKED",
            "requirements": dict(gate.REQUIREMENTS),
            "scheduled_workflow": dict(gate.SCHEDULED_WORKFLOW),
            "shadow_contract_sha256": gate.CURRENT_SHADOW_CONTRACT,
            "runs": [],
            "candidate_reviews": [],
            "approved_at": None,
        }

    def provenance(self, run_id: int, attempt: int = 1) -> dict[str, object]:
        return {
            **gate.SCHEDULED_WORKFLOW,
            "github_run_id": str(run_id),
            "run_attempt": attempt,
            "head_sha": f"{run_id:040x}",
            "workflow_sha": f"{run_id + 1000:040x}",
        }

    def candidate_key(self, number: int) -> str:
        repositories = sorted(self.repositories)
        repository = repositories[(number - 1) % len(repositories)]
        return f"{repository}#{number}"

    def shadow_run(
        self,
        index: int,
        run_date: str,
        candidate_numbers: list[int],
        *,
        github_run_id: int | None = None,
        attempt: int = 1,
        complete: bool = True,
        detail_count: int | None = None,
    ) -> dict[str, object]:
        run_id = github_run_id or 1000 + index
        seed = index * 10 + attempt
        run_at = datetime.fromisoformat(f"{run_date}T00:37:00+00:00") + timedelta(
            hours=attempt - 1
        )
        workflow_recorded_at = run_at + timedelta(minutes=13)
        attested_at = workflow_recorded_at + timedelta(minutes=10)
        timestamp = lambda value: value.isoformat().replace("+00:00", "Z")
        return {
            "run_id": f"github-{run_id}-attempt-{attempt}",
            "run_at": timestamp(run_at),
            "workflow_recorded_at": timestamp(workflow_recorded_at),
            "attested_at": timestamp(attested_at),
            "metadata_sha256": f"sha256:{seed + 1:064x}",
            "artifact_sha256": f"sha256:{seed + 101:064x}",
            "markdown_sha256": f"sha256:{seed + 201:064x}",
            "shadow_contract_sha256": gate.CURRENT_SHADOW_CONTRACT,
            "provenance": self.provenance(run_id, attempt),
            "collector_complete": complete,
            "collector_exit_code": 0 if complete else 2,
            "request_count": 2 * len(self.repositories)
            + 3 * (len(candidate_numbers) if detail_count is None else detail_count),
            "rate_limits": {
                "core": {
                    "remaining": 40,
                    "reset_at": f"{run_date}T01:37:00Z",
                },
                "search": {
                    "remaining": 8,
                    "reset_at": f"{run_date}T01:37:00Z",
                },
            },
            "http_403_count": 0,
            "http_429_count": 0,
            "discord_delivery_count": 0,
            "sort_accuracy_percent": 100,
            "freshness_accuracy_percent": 100,
            "warnings": [],
            "repository_failures": [],
            "repository_keys": sorted(self.repositories),
            "candidate_keys": [self.candidate_key(number) for number in candidate_numbers],
        }

    def gate_with_evidence(
        self,
        run_dates: tuple[str, ...] = RUN_DATES,
        source_indices: tuple[int, ...] = (0, 1, 2, 3, 4),
        *,
        approved: bool = True,
    ) -> dict[str, object]:
        payload = copy.deepcopy(self.locked)
        assignments = {
            index: [
                number
                for number in range(1, 11)
                if source_indices[(number - 1) % len(source_indices)] == index
            ]
            for index in range(len(run_dates))
        }
        payload["runs"] = [
            self.shadow_run(index, run_date, assignments.get(index, []))
            for index, run_date in enumerate(run_dates)
        ]
        payload["candidate_reviews"] = [
            {
                "candidate_key": self.candidate_key(number),
                "source_run_id": (
                    "github-"
                    f"{1000 + source_indices[(number - 1) % len(source_indices)]}"
                    "-attempt-1"
                ),
                "reviewed_at": "2026-07-14T00:00:00Z",
                "reviewer": "backend-reviewer",
                "notes": f"Reviewed candidate {number} against the frozen gates.",
                "relevant": True,
                "scope_clear": True,
                "hard_gate_false_positive": False,
                "false_positive_reason": None,
            }
            for number in range(1, 11)
        ]
        if approved:
            payload["status"] = "APPROVED"
            payload["approved_at"] = "2026-07-15T00:00:00Z"
        return payload

    def test_tracked_default_is_valid_and_locked(self) -> None:
        payload = gate.read_object(gate.DEFAULT_GATE)
        result = gate.evaluate_gate(
            payload,
            gate.allowed_repositories(gate.read_object(gate.DEFAULT_REPOSITORIES)),
            now=NOW,
        )

        self.assertEqual(payload["schema_version"], 3)
        self.assertEqual(payload["shadow_contract_sha256"], gate.CURRENT_SHADOW_CONTRACT)
        self.assertEqual(payload["scheduled_workflow"], gate.SCHEDULED_WORKFLOW)
        self.assertEqual(result["status"], "LOCKED")
        self.assertFalse(result["approved"])

    def test_five_consecutive_first_attempt_weeks_and_ten_reviews_are_approved(self) -> None:
        result = gate.evaluate_gate(
            self.gate_with_evidence(), self.repositories, now=NOW
        )

        self.assertTrue(result["approved"])
        self.assertEqual(result["observed_runs"], 5)
        self.assertEqual(result["qualifying_weeks"], 5)
        self.assertEqual(result["consecutive_qualifying_weeks"], 5)
        self.assertEqual(result["unique_candidates"], 10)
        self.assertEqual(result["relevance_percent"], 100)
        self.assertEqual(result["scope_clarity_percent"], 100)

    def test_rerun_is_recorded_but_only_first_attempt_qualifies(self) -> None:
        payload = copy.deepcopy(self.locked)
        first = self.shadow_run(0, RUN_DATES[0], [], github_run_id=7000)
        rerun = self.shadow_run(
            1,
            RUN_DATES[0],
            [],
            github_run_id=7000,
            attempt=2,
        )
        payload["runs"] = [first, rerun]

        result = gate.evaluate_gate(payload, self.repositories, now=NOW)

        self.assertEqual(result["observed_runs"], 2)
        self.assertEqual(result["qualifying_weeks"], 1)
        self.assertEqual(result["consecutive_qualifying_weeks"], 1)

    def test_rerun_timestamps_must_follow_attempt_order(self) -> None:
        payload = copy.deepcopy(self.locked)
        first = self.shadow_run(0, RUN_DATES[0], [], github_run_id=7001)
        rerun = self.shadow_run(
            1,
            RUN_DATES[0],
            [],
            github_run_id=7001,
            attempt=2,
        )
        rerun["run_at"] = "2026-06-15T00:36:00Z"
        rerun["workflow_recorded_at"] = "2026-06-15T00:49:00Z"
        rerun["attested_at"] = "2026-06-15T00:59:00Z"
        payload["runs"] = [first, rerun]

        with self.assertRaisesRegex(gate.GateError, "increase by attempt"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_failed_first_attempt_breaks_the_consecutive_window(self) -> None:
        run_dates = (
            "2026-06-15",
            "2026-06-22",
            "2026-06-29",
            "2026-07-06",
            "2026-07-13",
        )
        payload = copy.deepcopy(self.locked)
        payload["runs"] = [
            self.shadow_run(index, run_date, [], complete=index != 2)
            for index, run_date in enumerate(run_dates)
        ]

        result = gate.evaluate_gate(payload, self.repositories, now=NOW)
        self.assertEqual(result["qualifying_weeks"], 4)
        self.assertEqual(result["consecutive_qualifying_weeks"], 2)

        payload["status"] = "APPROVED"
        payload["approved_at"] = "2026-07-15T00:00:00Z"
        with self.assertRaisesRegex(gate.GateError, "does not satisfy"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_failed_run_preserves_partial_rate_limit_evidence(self) -> None:
        payload = copy.deepcopy(self.locked)
        failed = self.shadow_run(0, RUN_DATES[0], [], complete=False)
        failed["rate_limits"] = {"core": failed["rate_limits"]["core"]}
        payload["runs"] = [failed]

        result = gate.evaluate_gate(payload, self.repositories, now=NOW)

        self.assertEqual(result["observed_runs"], 1)
        self.assertEqual(result["qualifying_weeks"], 0)

    def test_incomplete_artifact_hashes_must_still_be_unique(self) -> None:
        payload = copy.deepcopy(self.locked)
        first = self.shadow_run(0, RUN_DATES[0], [], complete=False)
        second = self.shadow_run(1, RUN_DATES[1], [], complete=False)
        second["artifact_sha256"] = first["artifact_sha256"]
        payload["runs"] = [first, second]

        with self.assertRaisesRegex(gate.GateError, "artifact_sha256"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_run_repository_coverage_must_match_current_allowlist(self) -> None:
        payload = copy.deepcopy(self.locked)
        run = self.shadow_run(0, RUN_DATES[0], [])
        run["repository_keys"] = []
        payload["runs"] = [run]

        with self.assertRaisesRegex(gate.GateError, "repository coverage"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_provenance_hashes_and_contract_are_strict(self) -> None:
        cases = (
            ("top contract", ("shadow_contract_sha256", "sha256:" + "0" * 64), "stale"),
            ("run contract", ("run.shadow_contract_sha256", "sha256:" + "0" * 64), "current code"),
            ("repository", ("run.provenance.repository", "someone/example"), "does not match"),
            ("head sha", ("run.provenance.head_sha", "not-a-sha"), "commit SHA"),
            ("metadata hash", ("run.metadata_sha256", "sha256:bad"), "metadata_sha256"),
            ("artifact hash", ("run.artifact_sha256", "sha256:bad"), "JSON and Markdown hashes"),
        )
        for name, (field, value), message in cases:
            with self.subTest(name=name):
                payload = copy.deepcopy(self.locked)
                payload["runs"] = [self.shadow_run(0, RUN_DATES[0], [])]
                target: dict[str, object] = payload
                parts = field.split(".")
                if parts[0] == "run":
                    target = payload["runs"][0]
                    parts = parts[1:]
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = value
                with self.assertRaisesRegex(gate.GateError, message):
                    gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_checker_enforces_recorder_request_markdown_and_candidate_limits(self) -> None:
        cases: list[tuple[str, dict[str, object], str]] = []

        zero_requests = copy.deepcopy(self.locked)
        zero_requests["runs"] = [self.shadow_run(0, RUN_DATES[0], [])]
        zero_requests["runs"][0]["request_count"] = 0
        cases.append(("zero requests", zero_requests, "repository coverage"))

        duplicate_markdown = copy.deepcopy(self.locked)
        duplicate_markdown["runs"] = [
            self.shadow_run(0, RUN_DATES[0], []),
            self.shadow_run(1, RUN_DATES[1], []),
        ]
        duplicate_markdown["runs"][1]["markdown_sha256"] = (
            duplicate_markdown["runs"][0]["markdown_sha256"]
        )
        cases.append(("duplicate markdown", duplicate_markdown, "markdown_sha256"))

        late_metadata = copy.deepcopy(self.locked)
        late_metadata["runs"] = [self.shadow_run(0, RUN_DATES[0], [])]
        late_metadata["runs"][0]["workflow_recorded_at"] = (
            f"{RUN_DATES[0]}T00:54:00Z"
        )
        cases.append(("late metadata", late_metadata, "future or reversed"))

        too_many_candidates = copy.deepcopy(self.locked)
        too_many_candidates["runs"] = [self.shadow_run(0, RUN_DATES[0], [1, 2, 3])]
        cases.append(("candidate overflow", too_many_candidates, "artifact contract"))

        same_repository = copy.deepcopy(self.locked)
        same_repository["runs"] = [self.shadow_run(0, RUN_DATES[0], [1])]
        same_repository["runs"][0]["candidate_keys"] = [
            f"{self.repository}#1",
            f"{self.repository}#2",
        ]
        cases.append(
            ("repository READY overflow", same_repository, "per-repository READY")
        )

        request_overflow = copy.deepcopy(self.locked)
        request_overflow["runs"] = [self.shadow_run(0, RUN_DATES[0], [])]
        request_overflow["runs"][0]["request_count"] = (
            2 * len(self.repositories) + 3 * gate.DETAIL_LIMIT + 1
        )
        cases.append(("request overflow", request_overflow, "allowlist request plan"))

        for name, payload, message in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(gate.GateError, message):
                    gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_clean_run_request_count_must_match_repository_and_detail_plan(self) -> None:
        payload = self.gate_with_evidence()
        for run in payload["runs"]:
            run["request_count"] = len(self.repositories)

        with self.assertRaisesRegex(gate.GateError, "repository coverage"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_ready_candidates_require_their_detail_request_budget(self) -> None:
        payload = self.gate_with_evidence()
        for run in payload["runs"]:
            run["request_count"] = 2 * len(self.repositories)

        with self.assertRaisesRegex(gate.GateError, "repository coverage"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_two_selected_candidates_allow_eight_detailed_candidates(self) -> None:
        payload = copy.deepcopy(self.locked)
        payload["runs"] = [
            self.shadow_run(0, RUN_DATES[0], [1, 2], detail_count=8)
        ]

        result = gate.evaluate_gate(payload, self.repositories, now=NOW)

        self.assertEqual(result["observed_runs"], 1)
        self.assertEqual(result["qualifying_weeks"], 1)

    def test_date_only_timestamp_fails_closed_as_gate_error(self) -> None:
        payload = self.gate_with_evidence()
        payload["approved_at"] = "2026-07-15Z"

        with self.assertRaisesRegex(gate.GateError, "ISO-8601 UTC"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_false_positive_requires_a_controlled_reason_and_blocks_approval(self) -> None:
        payload = self.gate_with_evidence()
        review = payload["candidate_reviews"][0]
        review["hard_gate_false_positive"] = True

        with self.assertRaisesRegex(gate.GateError, "controlled reason"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

        review["false_positive_reason"] = "assigned"
        with self.assertRaisesRegex(gate.GateError, "does not satisfy"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

        review["hard_gate_false_positive"] = False
        with self.assertRaisesRegex(gate.GateError, "must not have"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_future_run_review_and_approval_are_rejected(self) -> None:
        cases = ("run", "review", "approval")
        for case in cases:
            with self.subTest(case=case):
                payload = self.gate_with_evidence()
                if case == "run":
                    payload["runs"][-1]["attested_at"] = "2099-07-08T01:00:00Z"
                elif case == "review":
                    payload["candidate_reviews"][0]["reviewed_at"] = (
                        "2099-07-09T00:00:00Z"
                    )
                else:
                    payload["approved_at"] = "2099-07-10T00:00:00Z"
                with self.assertRaisesRegex(gate.GateError, "future"):
                    gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_review_and_approval_must_follow_attestation(self) -> None:
        payload = self.gate_with_evidence()
        payload["runs"][-1]["attested_at"] = "2026-07-15T12:00:00Z"
        for review in payload["candidate_reviews"]:
            review["reviewed_at"] = "2026-07-15T13:00:00Z"
        payload["approved_at"] = "2026-07-15T11:00:00Z"

        with self.assertRaisesRegex(gate.GateError, "predates its latest evidence"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_review_must_not_precede_its_source_attestation(self) -> None:
        payload = self.gate_with_evidence()
        payload["candidate_reviews"][0]["reviewed_at"] = (
            "2026-06-15T00:59:00Z"
        )

        with self.assertRaisesRegex(gate.GateError, "follow its attestation"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_review_must_reference_a_candidate_in_its_source_artifact(self) -> None:
        payload = self.gate_with_evidence()
        payload["candidate_reviews"][0]["source_run_id"] = (
            payload["candidate_reviews"][1]["source_run_id"]
        )

        with self.assertRaisesRegex(gate.GateError, "source artifact"):
            gate.evaluate_gate(payload, self.repositories, now=NOW)

    def test_workflow_metadata_hashes_bind_the_source_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "oss-candidates.json"
            markdown = root / "oss-candidates.md"
            metadata = root / "oss-run-metadata.json"
            artifact.write_bytes(b'{"artifact":"original"}\n')
            markdown.write_text("# Original\n", encoding="utf-8")
            metadata.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "recorded_at": "2026-07-06T01:00:00Z",
                        "shadow_contract_sha256": gate.CURRENT_SHADOW_CONTRACT,
                        "collector_exit_code": 0,
                        "discord_delivery_count": 0,
                        "artifact_sha256": record.file_hash_or_none(artifact),
                        "markdown_sha256": record.file_hash_or_none(markdown),
                        "provenance": self.provenance(9000),
                    }
                ),
                encoding="utf-8",
            )

            record.validate_metadata(metadata, artifact, markdown)
            artifact.write_bytes(b'{"artifact":"tampered"}\n')

            with self.assertRaisesRegex(record.EvidenceError, "Artifact SHA-256"):
                record.validate_metadata(metadata, artifact, markdown)

    def test_github_output_contains_only_the_delivery_decision_counts(self) -> None:
        locked_result = gate.evaluate_gate(self.locked, self.repositories, now=NOW)
        approved_result = gate.evaluate_gate(
            self.gate_with_evidence(), self.repositories, now=NOW
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locked_path = root / "locked-output"
            approved_path = root / "approved-output"
            gate.write_github_output(locked_path, locked_result)
            gate.write_github_output(approved_path, approved_result)

            self.assertEqual(
                locked_path.read_text(encoding="utf-8"),
                "approved=false\nqualifying_weeks=0\nunique_candidates=0\n",
            )
            self.assertEqual(
                approved_path.read_text(encoding="utf-8"),
                "approved=true\nqualifying_weeks=5\nunique_candidates=10\n",
            )


if __name__ == "__main__":
    unittest.main()
