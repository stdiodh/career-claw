from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import verify_curriculum


class CurriculumVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = {
            "schema_version": 2,
            "profile_id": "profile-1",
            "lessons": [{"id": "lesson-1", "title": "Original"}],
        }
        self.profile = {
            "schema_version": 1,
            "profile_id": "profile-1",
            "created_at": "2026-07-16",
            "jdk": {"version": "21.0.11+10-LTS"},
            "version": "1",
        }
        self.taxonomy = {
            "schema_version": 1,
            "competencies": [
                {"id": "spring-mvc-api", "coverage_area": "web", "aliases": ["Spring"]}
            ],
            "market_keywords": {"SPRING": ["Spring"]},
            "market_demand_threshold": {
                "sample_size": 1,
                "minimum_occurrences": 1,
                "minimum_companies": 1,
                "maximum_postings_per_company": 1,
                "maximum_industry_share_percent": 100,
            },
        }
        self.job_market = {
            "schema_version": 1,
            "status": "COMPLETE",
            "checked_at": "2026-07-16",
            "window_start": "2026-07-01",
            "valid_until": "2026-09-30",
            "method": {
                "sample_size": 1,
                "market_demand_threshold": 1,
                "minimum_companies": 1,
                "maximum_per_company": 1,
                "maximum_industry_share_percent": 100,
            },
            "postings": [
                {
                    "company": "Example",
                    "role": "Backend",
                    "experience": "ENTRY",
                    "scope_rule": "INTERNSHIP_ENTRY_OR_MAX_3Y",
                    "scope_verified": True,
                    "industry": "software",
                    "date_posted": "2026-07-10",
                    "source_url": "https://example.com/job/1",
                    "keyword_ids": ["SPRING"],
                }
            ],
            "frequency": {"SPRING": 1},
            "market_supported_ids": ["SPRING"],
        }
        self.lab_revision = "sha256:lab"
        self.entry = {
            "id": "lesson-1",
            "tier": "CORE",
            "core_type": "JVM_CORE",
            "competency_ids": ["spring-mvc-api"],
            "necessity_evidence": {"kind": "MARKET", "keyword_ids": ["SPRING"]},
            "scores": {
                "necessity": 2,
                "source_fit": 2,
                "stack_relevance": 2,
                "failure_reproduction": 2,
                "executable_evidence": 2,
            },
            "source_claims": [
                {
                    "claim": "Spring validates request inputs.",
                    "url": "https://example.com/reference",
                    "revision": "v1",
                    "revision_url": "https://example.com/source/tree/v1",
                    "reviewed_at": "2026-07-16",
                }
            ],
            "lab": {
                "path": "lab/src/test/Test.kt",
                "verify_command": "./lab/gradlew test",
                "test_ids": ["LAB-TEST-001"],
                "expected_assertions": ["invalid input is rejected"],
            },
        }
        self.matrix = {
            "schema_version": 1,
            "profile_id": "profile-1",
            "lab_revision": self.lab_revision,
            "job_market_audit": "audits/job-market-2026q3.json",
            "required_competencies": ["spring-mvc-api"],
            "lessons": [self.entry],
        }

    def manifest_for_current_contract(self) -> dict[str, object]:
        contract = verify_curriculum.lesson_contract(
            self.backend["lessons"][0],
            self.entry,
            self.profile,
            self.taxonomy,
            self.job_market,
            self.lab_revision,
        )
        return {
            "schema_version": 1,
            "profile_id": "profile-1",
            "lab_revision": self.lab_revision,
            "verification_runtime": "21.0.11+10-LTS",
            "verified_at": "2026-07-16",
            "commands": [
                "docker run --rm --platform linux/amd64 -v \"$PWD:/workspace\" "
                "-w /workspace eclipse-temurin:21.0.11_10-jdk "
                "./lab/gradlew -p lab clean test --no-daemon --no-build-cache",
                "./lab/gradlew -p lab postgresTest --rerun-tasks --no-daemon",
            ],
            "lessons": {
                "lesson-1": {
                    "status": "VERIFIED",
                    "contract_hash": contract,
                    "assertions": {"LAB-TEST-001": "PASS"},
                }
            },
        }

    def test_matching_contract_is_verified(self) -> None:
        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            self.manifest_for_current_contract(),
            self.lab_revision,
        )

        self.assertTrue(summary["valid"], summary["errors"])
        self.assertEqual(summary["verified_lesson_ids"], ["lesson-1"])

    def test_changed_lesson_fails_closed_as_stale(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.backend["lessons"][0]["title"] = "Changed"

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertEqual(summary["stale_lesson_ids"], ["lesson-1"])

    def test_assertion_keys_must_exactly_match_matrix_test_ids(self) -> None:
        manifest = self.manifest_for_current_contract()
        manifest["lessons"]["lesson-1"]["assertions"] = {"LAB-OTHER-001": "PASS"}

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertEqual(summary["stale_lesson_ids"], ["lesson-1"])

    def test_taxonomy_change_invalidates_existing_contract(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.taxonomy["competencies"][0]["aliases"].append("Web MVC")

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertEqual(summary["stale_lesson_ids"], ["lesson-1"])

    def test_job_market_change_invalidates_existing_contract(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["postings"][0]["source_url"] = "https://example.com/job/changed"

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertEqual(summary["stale_lesson_ids"], ["lesson-1"])

    def test_market_evidence_below_threshold_fails_closed(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["method"]["market_demand_threshold"] = 2
        self.taxonomy["market_demand_threshold"]["minimum_occurrences"] = 2
        self.job_market["market_supported_ids"] = []

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("below the frozen threshold" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_job_market_sample_limits_cannot_weaken_the_taxonomy(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["method"]["minimum_companies"] = 2

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("minimum_companies" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_job_market_scope_attestation_is_required(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["postings"][0]["scope_verified"] = False

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("scope attestation" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_job_market_scope_code_rejects_senior_requirement(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["postings"][0]["experience"] = "TEN_PLUS_YEARS"

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("scope attestation" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_expired_job_market_audit_fails_closed(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["checked_at"] = "2000-02-01"
        self.job_market["window_start"] = "2000-01-01"
        self.job_market["valid_until"] = "2000-03-31"
        self.job_market["postings"][0]["date_posted"] = "2000-01-15"

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("has expired" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_future_job_market_audit_fails_closed(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.job_market["checked_at"] = "2099-02-01"
        self.job_market["window_start"] = "2099-01-01"
        self.job_market["valid_until"] = "2099-03-31"
        self.job_market["postings"][0]["date_posted"] = "2099-01-15"

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("must not be in the future" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_future_manifest_date_fails_closed(self) -> None:
        manifest = self.manifest_for_current_contract()
        manifest["verified_at"] = "2099-01-01"

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("manifest dates must not be in the future" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_invalid_or_future_source_review_date_fails_closed(self) -> None:
        for reviewed_at in ("9999-99-99", "2099-01-01"):
            with self.subTest(reviewed_at=reviewed_at):
                manifest = self.manifest_for_current_contract()
                self.entry["source_claims"][0]["reviewed_at"] = reviewed_at

                summary = verify_curriculum.evaluate_curriculum(
                    self.backend,
                    self.matrix,
                    self.profile,
                    self.taxonomy,
                    self.job_market,
                    manifest,
                    self.lab_revision,
                )

                self.assertFalse(summary["valid"])
                self.assertTrue(
                    any("source claim reviewed_at" in error for error in summary["errors"]),
                    summary["errors"],
                )
                self.entry["source_claims"][0]["reviewed_at"] = "2026-07-16"

    def test_mutable_source_revision_is_rejected(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.entry["source_claims"][0]["revision_url"] = (
            "https://github.com/example/project/tree/main"
        )

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("must pin a version" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_manifest_evidence_metadata_is_required(self) -> None:
        manifest = self.manifest_for_current_contract()
        del manifest["commands"]

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("manifest commands" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_expected_assertions_must_be_strings_and_match_test_ids(self) -> None:
        manifest = self.manifest_for_current_contract()
        self.entry["lab"]["expected_assertions"] = [None]

        summary = verify_curriculum.evaluate_curriculum(
            self.backend,
            self.matrix,
            self.profile,
            self.taxonomy,
            self.job_market,
            manifest,
            self.lab_revision,
        )

        self.assertFalse(summary["valid"])
        self.assertTrue(
            any("expected_assertions" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_lab_revision_ignores_build_cache_but_not_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lab = Path(directory)
            source = lab / "src/Test.kt"
            source.parent.mkdir(parents=True)
            source.write_text("class Test", encoding="utf-8")
            cache = lab / ".gradle/cache.bin"
            cache.parent.mkdir()
            cache.write_bytes(b"first")

            first = verify_curriculum.calculate_lab_revision(lab)
            cache.write_bytes(b"second")
            self.assertEqual(first, verify_curriculum.calculate_lab_revision(lab))

            source.write_text("class Changed", encoding="utf-8")
            self.assertNotEqual(first, verify_curriculum.calculate_lab_revision(lab))

    def test_managed_dependency_profile_must_match_gradle_lock(self) -> None:
        profile = verify_curriculum.read_object(verify_curriculum.PROFILE_CONFIG)
        profile["managed_dependencies"]["spring_security"] = "999.0.0"

        errors = verify_curriculum.validate_lab_profile(
            verify_curriculum.LAB_DIR,
            profile,
        )

        self.assertTrue(
            any("spring-security-core" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
