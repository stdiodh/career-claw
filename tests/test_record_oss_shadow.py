from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import check_oss_delivery_gate as delivery_gate
from scripts import record_oss_shadow


NOW = datetime(2026, 7, 16, 1, 0, tzinfo=timezone.utc)
REPOSITORY = "spring-projects/spring-boot"


class RecordOssShadowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.gate_path = self.root / "gate.json"
        self.repositories_path = self.root / "repositories.json"
        self.artifact_path = self.root / "oss-candidates.json"
        self.markdown_path = self.root / "oss-candidates.md"
        self.metadata_path = self.root / "oss-run-metadata.json"
        self._write_json(self.gate_path, self.locked_gate())
        self._write_json(
            self.repositories_path,
            {
                "policy": dict(record_oss_shadow.EXPECTED_POLICY),
                "repositories": [
                    {
                        "repository": REPOSITORY,
                        "include_labels": ["status: ideal-for-contribution"],
                        "module_label_to_build_command": {
                            "theme: config-data": "./gradlew :core:spring-boot:test"
                        },
                        "contribution_type_by_label": {"documentation": "docs"},
                        "default_contribution_type": "code/test",
                        "relevance_reason": (
                            "Spring Boot backend code and tests are in scope."
                        ),
                    }
                ],
            },
        )
        self.write_success_outputs()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _write_json(path: Path, payload: dict[str, object]) -> None:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def locked_gate() -> dict[str, object]:
        return {
            "schema_version": 3,
            "status": "LOCKED",
            "requirements": dict(delivery_gate.REQUIREMENTS),
            "scheduled_workflow": dict(delivery_gate.SCHEDULED_WORKFLOW),
            "shadow_contract_sha256": delivery_gate.CURRENT_SHADOW_CONTRACT,
            "runs": [],
            "candidate_reviews": [],
            "approved_at": None,
        }

    @staticmethod
    def github_environment(run_id: str = "1001", attempt: int = 1) -> dict[str, str]:
        return {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": delivery_gate.SCHEDULED_WORKFLOW["repository"],
            "GITHUB_WORKFLOW_REF": delivery_gate.SCHEDULED_WORKFLOW["workflow_ref"],
            "GITHUB_WORKFLOW_SHA": "a" * 40,
            "GITHUB_EVENT_NAME": delivery_gate.SCHEDULED_WORKFLOW["event_name"],
            "GITHUB_RUN_ID": run_id,
            "GITHUB_RUN_ATTEMPT": str(attempt),
            "GITHUB_SHA": "b" * 40,
            "GITHUB_REF": delivery_gate.SCHEDULED_WORKFLOW["ref"],
            "RUNNER_ENVIRONMENT": delivery_gate.SCHEDULED_WORKFLOW[
                "runner_environment"
            ],
            "RUNNER_OS": delivery_gate.SCHEDULED_WORKFLOW["runner_os"],
        }

    @staticmethod
    def candidate(number: int, created_at: str) -> dict[str, object]:
        return {
            "decision": "READY_TO_ASK",
            "repository": REPOSITORY,
            "issue_number": number,
            "title": f"Improve backend test {number}",
            "url": f"https://github.com/{REPOSITORY}/issues/{number}",
            "created_at": created_at,
            "updated_at": "2026-07-16T00:20:00Z",
            "checked_at": "2026-07-16T00:46:00Z",
            "contribution_label": "status: ideal-for-contribution",
            "contribution_type": "code/test",
            "relevance_reason": "Spring Boot backend code and tests are in scope.",
            "module_label": "theme: config-data",
            "build_test_command": "./gradlew :core:spring-boot:test",
            "last_maintainer_activity_at": "2026-07-15T00:00:00Z",
            "freshness": "FRESH",
            "exclusion_reasons": [],
            "manual_review_reasons": [],
        }

    @classmethod
    def success_artifact(cls) -> dict[str, object]:
        candidates = [
            cls.candidate(101, "2026-07-15T00:00:00Z"),
            cls.candidate(102, "2026-07-14T00:00:00Z"),
        ]
        return {
            "schema_version": 1,
            "mode": "live-dry-run",
            "generated_at": "2026-07-16T00:47:00Z",
            "checked_at": "2026-07-16T00:46:00Z",
            "complete": True,
            "delivery_allowed": True,
            "request_count": 8,
            "request_limit": record_oss_shadow.EXPECTED_POLICY["request_limit"],
            "http_status_counts": {"200": 8},
            "rate_limits": {
                "core": {
                    "remaining": 57,
                    "reset_at": "2026-07-16T01:30:00Z",
                },
                "search": {
                    "remaining": 7,
                    "reset_at": "2026-07-16T01:30:00Z",
                },
            },
            "repository_results": [
                {
                    "repository": REPOSITORY,
                    "label_contract": "VERIFIED",
                    "missing_labels": [],
                    "search_count": 2,
                    "eligible_search_count": 2,
                    "fail_closed_reason": None,
                }
            ],
            "precheck_exclusions": [],
            "candidates": candidates,
            "ready_to_ask": candidates,
            "errors": [],
            "warnings": [],
            "limitations": list(record_oss_shadow.EXPECTED_LIMITATIONS),
        }

    def write_success_outputs(self) -> None:
        self.write_outputs(self.success_artifact())

    def write_outputs(self, artifact: dict[str, object]) -> None:
        self._write_json(self.artifact_path, artifact)
        self.markdown_path.write_text(
            record_oss_shadow.collector.render_markdown(artifact),
            encoding="utf-8",
        )

    def build_metadata(
        self,
        *,
        run_id: str = "1001",
        attempt: int = 1,
        exit_code: int = 0,
        artifact_path: Path | None = None,
        markdown_path: Path | None = None,
        output_path: Path | None = None,
        now: datetime = NOW,
    ) -> dict[str, object]:
        return record_oss_shadow.build_metadata(
            exit_code,
            False,
            artifact_path or self.artifact_path,
            markdown_path or self.markdown_path,
            output_path or self.metadata_path,
            environ=self.github_environment(run_id, attempt),
            now=now,
        )

    def record_success(
        self, *, run_id: str = "1001", attempt: int = 1
    ) -> dict[str, object]:
        recorded_at = NOW + timedelta(minutes=attempt - 1)
        self.build_metadata(run_id=run_id, attempt=attempt, now=recorded_at)
        return record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            True,
            True,
            self.gate_path,
            self.repositories_path,
            attested_at=record_oss_shadow.utc_timestamp(recorded_at),
            now=recorded_at,
            allow_repository_override=True,
        )

    def test_build_metadata_rejects_local_environment_without_writing(self) -> None:
        output = self.root / "local-metadata.json"

        with mock.patch.dict(
            os.environ, self.github_environment("9999", 1), clear=True
        ):
            with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "GitHub Actions"):
                record_oss_shadow.build_metadata(
                    0,
                    False,
                    self.artifact_path,
                    self.markdown_path,
                    output,
                    environ={},
                    now=NOW,
                )

        self.assertFalse(output.exists())

    def test_successful_run_records_strict_artifact_and_github_provenance(self) -> None:
        metadata = self.build_metadata()
        run = record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            True,
            True,
            self.gate_path,
            self.repositories_path,
            attested_at="2026-07-16T01:00:00Z",
            now=NOW,
            allow_repository_override=True,
        )
        gate = json.loads(self.gate_path.read_text(encoding="utf-8"))

        self.assertEqual(run["run_id"], "github-1001-attempt-1")
        self.assertEqual(run["provenance"], metadata["provenance"])
        self.assertEqual(
            run["metadata_sha256"],
            record_oss_shadow.sha256_bytes(self.metadata_path.read_bytes()),
        )
        self.assertEqual(
            run["artifact_sha256"],
            record_oss_shadow.sha256_bytes(self.artifact_path.read_bytes()),
        )
        self.assertEqual(
            run["markdown_sha256"],
            record_oss_shadow.sha256_bytes(self.markdown_path.read_bytes()),
        )
        self.assertEqual(run["shadow_contract_sha256"], delivery_gate.CURRENT_SHADOW_CONTRACT)
        self.assertEqual(
            run["candidate_keys"],
            [f"{REPOSITORY}#101", f"{REPOSITORY}#102"],
        )
        self.assertEqual(run["http_403_count"], 0)
        self.assertEqual(run["http_429_count"], 0)
        self.assertEqual(run["repository_keys"], [REPOSITORY])
        self.assertEqual(gate["runs"], [run])

    def test_custom_repository_config_is_rejected_by_default(self) -> None:
        self.build_metadata()

        with self.assertRaisesRegex(
            record_oss_shadow.EvidenceError, "bound into the Shadow contract"
        ):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
            )

    def test_markdown_must_be_the_exact_deterministic_rendering(self) -> None:
        self.markdown_path.write_text("# Fabricated\n", encoding="utf-8")
        self.build_metadata()

        with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "deterministic"):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
                allow_repository_override=True,
            )

    def test_fake_minimal_artifact_is_rejected_without_gate_write(self) -> None:
        self._write_json(
            self.artifact_path,
            {
                "schema_version": 1,
                "mode": "live-dry-run",
                "generated_at": "2026-07-16T00:37:00Z",
                "complete": True,
                "delivery_allowed": True,
            },
        )
        self.build_metadata()
        before = self.gate_path.read_bytes()

        with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "exact collector schema"):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
                allow_repository_override=True,
            )

        self.assertEqual(self.gate_path.read_bytes(), before)

    def test_artifact_hash_mismatch_is_rejected_without_gate_write(self) -> None:
        self.build_metadata()
        self.artifact_path.write_text("{}\n", encoding="utf-8")
        before = self.gate_path.read_bytes()

        with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "SHA-256"):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
                allow_repository_override=True,
            )

        self.assertEqual(self.gate_path.read_bytes(), before)

    def test_failed_run_without_artifacts_is_preserved_in_the_ledger(self) -> None:
        missing_artifact = self.root / "missing.json"
        missing_markdown = self.root / "missing.md"
        metadata_path = self.root / "failed-metadata.json"
        self.build_metadata(
            run_id="1002",
            exit_code=1,
            artifact_path=missing_artifact,
            markdown_path=missing_markdown,
            output_path=metadata_path,
        )

        run = record_oss_shadow.record_run(
            metadata_path,
            None,
            None,
            False,
            False,
            self.gate_path,
            self.repositories_path,
            now=NOW,
            allow_repository_override=True,
        )
        gate = json.loads(self.gate_path.read_text(encoding="utf-8"))
        result = delivery_gate.evaluate_gate(
            gate, {REPOSITORY}, now=NOW + timedelta(minutes=1)
        )

        self.assertFalse(run["collector_complete"])
        self.assertEqual(run["collector_exit_code"], 1)
        self.assertIsNone(run["artifact_sha256"])
        self.assertIsNone(run["markdown_sha256"])
        self.assertEqual(run["warnings"], ["collector_artifact_missing"])
        self.assertEqual(result["observed_runs"], 1)
        self.assertEqual(result["qualifying_weeks"], 0)

    def test_failed_artifact_with_partial_rate_limits_is_preserved(self) -> None:
        artifact = self.success_artifact()
        artifact["complete"] = False
        artifact["delivery_allowed"] = False
        artifact["errors"] = ["missing search rate-limit headers"]
        artifact["rate_limits"] = {"core": artifact["rate_limits"]["core"]}
        artifact["rate_limits"]["core"] = {
            "remaining": 61,
            "reset_at": "2026-07-24T01:30:00Z",
        }
        artifact["ready_to_ask"] = []
        self._write_json(self.artifact_path, artifact)
        self.markdown_path.write_text(
            record_oss_shadow.collector.render_markdown(artifact),
            encoding="utf-8",
        )
        self.build_metadata(run_id="1004", exit_code=2)

        run = record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            True,
            True,
            self.gate_path,
            self.repositories_path,
            attested_at="2026-07-16T01:00:00Z",
            now=NOW,
            allow_repository_override=True,
        )
        result = delivery_gate.evaluate_gate(
            json.loads(self.gate_path.read_text(encoding="utf-8")),
            {REPOSITORY},
            now=NOW,
        )

        self.assertFalse(run["collector_complete"])
        self.assertEqual(run["rate_limits"], artifact["rate_limits"])
        self.assertEqual(result["qualifying_weeks"], 0)

    def test_verified_label_contract_search_failure_is_preserved(self) -> None:
        artifact = self.success_artifact()
        artifact.update(
            {
                "complete": False,
                "delivery_allowed": False,
                "request_count": 2,
                "http_status_counts": {"200": 1, "403": 1},
                "rate_limits": {"core": artifact["rate_limits"]["core"]},
                "checked_at": None,
                "precheck_exclusions": [],
                "candidates": [],
                "ready_to_ask": [],
                "errors": ["spring-projects/spring-boot search: HTTP 403"],
            }
        )
        artifact["repository_results"][0].update(
            {
                "search_count": 0,
                "eligible_search_count": 0,
                "fail_closed_reason": "search_request_failed",
            }
        )
        self.write_outputs(artifact)
        self.build_metadata(run_id="1005", exit_code=2)

        run = record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            True,
            True,
            self.gate_path,
            self.repositories_path,
            now=NOW,
            allow_repository_override=True,
        )

        self.assertFalse(run["collector_complete"])
        self.assertEqual(
            run["repository_failures"],
            [{"repository": REPOSITORY, "reason": "search_request_failed"}],
        )

    def test_empty_detail_title_is_valid_only_as_an_excluded_candidate(self) -> None:
        artifact = self.success_artifact()
        excluded = artifact["candidates"][0]
        excluded["decision"] = "EXCLUDED"
        excluded["title"] = ""
        excluded["exclusion_reasons"] = ["invalid_title"]
        artifact["ready_to_ask"] = [artifact["candidates"][1]]
        self.write_outputs(artifact)
        self.build_metadata(run_id="1006")

        run = record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            True,
            True,
            self.gate_path,
            self.repositories_path,
            now=NOW,
            allow_repository_override=True,
        )

        self.assertEqual(run["candidate_keys"], [f"{REPOSITORY}#102"])

    def test_search_counts_must_support_every_detailed_candidate(self) -> None:
        artifact = self.success_artifact()
        artifact["repository_results"][0]["search_count"] = 0
        artifact["repository_results"][0]["eligible_search_count"] = 0
        self.write_outputs(artifact)
        self.build_metadata(run_id="1007")

        with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "search evidence"):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
                allow_repository_override=True,
            )

    def test_preselection_cannot_omit_eligible_candidates(self) -> None:
        artifact = self.success_artifact()
        artifact["candidates"] = []
        artifact["ready_to_ask"] = []
        artifact["checked_at"] = None
        artifact["request_count"] = 2
        artifact["http_status_counts"] = {"200": 2}
        self.write_outputs(artifact)
        self.build_metadata(run_id="1010")

        with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "omitted candidates"):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
                allow_repository_override=True,
            )

    def test_complete_artifact_requires_exact_http_200_counts(self) -> None:
        artifact = self.success_artifact()
        artifact["http_status_counts"] = {"201": artifact["request_count"]}
        self.write_outputs(artifact)
        self.build_metadata(run_id="1011")

        with self.assertRaisesRegex(record_oss_shadow.EvidenceError, "HTTP 200"):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                now=NOW,
                allow_repository_override=True,
            )

    def test_precheck_reason_and_top_snapshot_are_strict(self) -> None:
        cases = (
            (
                "invented precheck",
                lambda artifact: artifact["precheck_exclusions"].append(
                    {
                        "repository": REPOSITORY,
                        "issue_number": 77,
                        "reason": "invented_reason",
                    }
                ),
                "precheck exclusion",
            ),
            (
                "top snapshot mismatch",
                lambda artifact: artifact.update(
                    {"checked_at": "2026-07-16T00:45:00Z"}
                ),
                "artifact snapshot",
            ),
            (
                "missing precheck identity",
                lambda artifact: artifact["precheck_exclusions"].append(
                    {
                        "repository": REPOSITORY,
                        "issue_number": None,
                        "reason": "closed",
                    }
                ),
                "contradicts its issue number",
            ),
        )
        for name, mutate, message in cases:
            with self.subTest(name=name):
                self._write_json(self.gate_path, self.locked_gate())
                artifact = self.success_artifact()
                mutate(artifact)
                self.write_outputs(artifact)
                self.build_metadata(run_id=f"12{len(name)}")
                with self.assertRaisesRegex(record_oss_shadow.EvidenceError, message):
                    record_oss_shadow.record_run(
                        self.metadata_path,
                        self.artifact_path,
                        self.markdown_path,
                        True,
                        True,
                        self.gate_path,
                        self.repositories_path,
                        now=NOW,
                        allow_repository_override=True,
                    )

    def test_ready_candidate_must_match_lookback_profile_and_activity_policy(self) -> None:
        cases = (
            ("lookback", "2025-12-01T00:00:00Z", "frozen lookback"),
            ("build_test_command", "./gradlew arbitrary:test", "build command"),
            ("last_maintainer_activity_at", "2026-04-01T00:00:00Z", "older than 90"),
        )
        for field, value, message in cases:
            with self.subTest(field=field):
                self._write_json(self.gate_path, self.locked_gate())
                artifact = self.success_artifact()
                if field == "lookback":
                    artifact["candidates"][1]["created_at"] = value
                    artifact["candidates"][1]["updated_at"] = "2026-01-01T00:00:00Z"
                elif field == "last_maintainer_activity_at":
                    artifact["candidates"][1]["created_at"] = "2025-12-01T00:00:00Z"
                    artifact["candidates"][1][field] = value
                else:
                    artifact["candidates"][0][field] = value
                self.write_outputs(artifact)
                self.build_metadata(run_id=f"11{len(field)}")
                with self.assertRaisesRegex(record_oss_shadow.EvidenceError, message):
                    record_oss_shadow.record_run(
                        self.metadata_path,
                        self.artifact_path,
                        self.markdown_path,
                        True,
                        True,
                        self.gate_path,
                        self.repositories_path,
                        now=NOW,
                        allow_repository_override=True,
                    )

    def test_stale_detail_failure_artifact_is_preserved_nonqualifying(self) -> None:
        artifact = self.success_artifact()
        artifact["complete"] = False
        artifact["delivery_allowed"] = False
        artifact["checked_at"] = "2026-07-16T00:20:00Z"
        artifact["errors"] = ["candidate detail validation is older than 15 minutes"]
        artifact["ready_to_ask"] = []
        for candidate in artifact["candidates"]:
            candidate["checked_at"] = "2026-07-16T00:20:00Z"
        self.write_outputs(artifact)
        self.build_metadata(run_id="1008", exit_code=2)

        run = record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            True,
            True,
            self.gate_path,
            self.repositories_path,
            now=NOW,
            allow_repository_override=True,
        )

        self.assertFalse(run["collector_complete"])

    def test_exit_one_json_only_output_is_preserved_as_partial_telemetry(self) -> None:
        missing_markdown = self.root / "missing.md"
        self.build_metadata(
            run_id="1009",
            exit_code=1,
            markdown_path=missing_markdown,
        )

        run = record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            None,
            False,
            False,
            self.gate_path,
            self.repositories_path,
            now=NOW,
            allow_repository_override=True,
        )

        self.assertEqual(run["warnings"], ["collector_output_partial"])
        self.assertIsNotNone(run["artifact_sha256"])
        self.assertIsNone(run["markdown_sha256"])

    def test_second_attempt_is_preserved_but_never_qualifies(self) -> None:
        self.build_metadata(run_id="1003", attempt=1)
        record_oss_shadow.record_run(
            self.metadata_path,
            self.artifact_path,
            self.markdown_path,
            False,
            True,
            self.gate_path,
            self.repositories_path,
            attested_at="2026-07-16T01:00:00Z",
            now=NOW,
            allow_repository_override=True,
        )
        rerun_artifact = self.success_artifact()
        rerun_artifact["generated_at"] = "2026-07-16T01:01:00Z"
        rerun_artifact["checked_at"] = "2026-07-16T01:00:00Z"
        for candidate in rerun_artifact["candidates"]:
            candidate["checked_at"] = "2026-07-16T01:00:00Z"
        self._write_json(self.artifact_path, rerun_artifact)
        self.markdown_path.write_text(
            record_oss_shadow.collector.render_markdown(rerun_artifact),
            encoding="utf-8",
        )

        run = self.record_success(run_id="1003", attempt=2)
        gate = json.loads(self.gate_path.read_text(encoding="utf-8"))
        result = delivery_gate.evaluate_gate(
            gate, {REPOSITORY}, now=NOW + timedelta(minutes=1)
        )

        self.assertEqual(run["run_id"], "github-1003-attempt-2")
        self.assertEqual(run["provenance"]["run_attempt"], 2)
        self.assertEqual(result["observed_runs"], 2)
        self.assertEqual(result["qualifying_weeks"], 0)

    def test_reviews_require_fields_reason_and_source_artifact_binding(self) -> None:
        run = self.record_success()
        normal = record_oss_shadow.record_review(
            f"{REPOSITORY}#101",
            str(run["run_id"]),
            "backend-reviewer",
            "The issue is scoped to a reproducible Spring Boot test.",
            True,
            True,
            False,
            None,
            self.gate_path,
            self.repositories_path,
            reviewed_at="2026-07-16T01:01:00Z",
            now=NOW + timedelta(minutes=5),
            allow_repository_override=True,
        )
        false_positive = record_oss_shadow.record_review(
            f"{REPOSITORY}#102",
            str(run["run_id"]),
            "backend-reviewer",
            "A linked pull request appeared after collection.",
            True,
            True,
            True,
            "linked_pull_request",
            self.gate_path,
            self.repositories_path,
            reviewed_at="2026-07-16T01:02:00Z",
            now=NOW + timedelta(minutes=5),
            allow_repository_override=True,
        )
        gate = json.loads(self.gate_path.read_text(encoding="utf-8"))

        self.assertEqual(gate["candidate_reviews"], [normal, false_positive])
        self.assertEqual(normal["reviewer"], "backend-reviewer")
        self.assertTrue(normal["notes"])
        self.assertIsNone(normal["false_positive_reason"])
        self.assertEqual(false_positive["false_positive_reason"], "linked_pull_request")

        base = self.locked_gate()
        base["runs"] = [run]
        invalid_reviews = (
            {
                "candidate_key": f"{REPOSITORY}#103",
                "reviewer": "backend-reviewer",
                "notes": "Not present in the source artifact.",
                "hard_gate_false_positive": False,
                "false_positive_reason": None,
                "message": "source artifact",
            },
            {
                "candidate_key": f"{REPOSITORY}#101",
                "reviewer": "",
                "notes": "Evidence exists.",
                "hard_gate_false_positive": False,
                "false_positive_reason": None,
                "message": "reviewer",
            },
            {
                "candidate_key": f"{REPOSITORY}#101",
                "reviewer": "backend-reviewer",
                "notes": "",
                "hard_gate_false_positive": False,
                "false_positive_reason": None,
                "message": "notes",
            },
            {
                "candidate_key": f"{REPOSITORY}#101",
                "reviewer": "backend-reviewer",
                "notes": "Reason is missing.",
                "hard_gate_false_positive": True,
                "false_positive_reason": None,
                "message": "controlled reason",
            },
            {
                "candidate_key": f"{REPOSITORY}#101",
                "reviewer": "backend-reviewer",
                "notes": "Reason should be absent.",
                "hard_gate_false_positive": False,
                "false_positive_reason": "assigned",
                "message": "must not",
            },
        )
        for case in invalid_reviews:
            with self.subTest(message=case["message"]):
                self._write_json(self.gate_path, base)
                before = self.gate_path.read_bytes()
                with self.assertRaisesRegex(delivery_gate.GateError, str(case["message"])):
                    record_oss_shadow.record_review(
                        str(case["candidate_key"]),
                        str(run["run_id"]),
                        str(case["reviewer"]),
                        str(case["notes"]),
                        True,
                        True,
                        bool(case["hard_gate_false_positive"]),
                        case["false_positive_reason"],
                        self.gate_path,
                        self.repositories_path,
                        reviewed_at="2026-07-16T01:01:00Z",
                        now=NOW + timedelta(minutes=5),
                        allow_repository_override=True,
                    )
                self.assertEqual(self.gate_path.read_bytes(), before)

    def test_approval_refuses_insufficient_evidence_without_a_write(self) -> None:
        before = self.gate_path.read_bytes()

        with self.assertRaisesRegex(delivery_gate.GateError, "does not satisfy"):
            record_oss_shadow.approve_gate(
                self.gate_path,
                self.repositories_path,
                approved_at="2026-07-16T00:59:00Z",
                now=NOW,
                allow_repository_override=True,
            )

        self.assertEqual(self.gate_path.read_bytes(), before)

    def test_gate_write_is_atomic_when_validation_rejects_a_duplicate_run(self) -> None:
        self.record_success()
        before = self.gate_path.read_bytes()

        with self.assertRaises(delivery_gate.GateError):
            record_oss_shadow.record_run(
                self.metadata_path,
                self.artifact_path,
                self.markdown_path,
                True,
                True,
                self.gate_path,
                self.repositories_path,
                attested_at="2026-07-16T01:00:00Z",
                now=NOW,
                allow_repository_override=True,
            )

        self.assertEqual(self.gate_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
