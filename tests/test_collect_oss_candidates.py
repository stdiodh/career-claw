from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import collect_oss_candidates as collector


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests/fixtures/oss-api-responses.json"
NOW = datetime(2026, 8, 20, 9, tzinfo=timezone.utc)


class CapturingFixtureTransport(collector.FixtureTransport):
    def __init__(self, fixture: dict[str, object]) -> None:
        super().__init__(fixture, lambda: NOW)
        self.urls: list[str] = []

    def get(self, url: str) -> collector.ApiResponse:
        self.urls.append(url)
        return super().get(url)


class FakeHttpResponse:
    status = 200

    def __init__(self) -> None:
        self.headers = {
            "X-RateLimit-Resource": "core",
            "X-RateLimit-Remaining": "59",
        }

    def __enter__(self) -> "FakeHttpResponse":
        return self

    def __exit__(self, *arguments: object) -> None:
        return None

    def read(self) -> bytes:
        return b'{"ok": true}'


class OssCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = collector.load_config(collector.DEFAULT_CONFIG, NOW.date())
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def run_fixture(
        self, fixture: dict[str, object] | None = None
    ) -> tuple[dict[str, object], CapturingFixtureTransport]:
        transport = CapturingFixtureTransport(fixture or copy.deepcopy(self.fixture))
        client = collector.GitHubClient(
            transport,
            self.config["policy"]["request_limit"],
        )
        return (
            collector.collect_candidates(self.config, client, NOW, "fixture"),
            transport,
        )

    def candidate(
        self,
        result: dict[str, object],
        repository: str,
        number: int,
    ) -> dict[str, object]:
        return next(
            item
            for item in result["shortlist"]
            if item["repository"] == repository and item["issue_number"] == number
        )

    def test_config_is_the_exact_tier_a_scoring_contract(self) -> None:
        self.assertEqual(self.config["schema_version"], 4)
        self.assertEqual(
            tuple(item["repository"] for item in self.config["repositories"]),
            collector.TIER_A_REPOSITORIES,
        )
        self.assertEqual(self.config["policy"]["shortlist_limit"], 5)
        self.assertEqual(self.config["policy"]["recommendation_limit"], 3)
        self.assertEqual(self.config["policy"]["request_limit"], 21)
        self.assertEqual(sum(self.config["scoring"].values()), 100)

    def test_fixture_returns_three_ranked_recommendations(self) -> None:
        result, transport = self.run_fixture()

        self.assertTrue(result["complete"])
        self.assertEqual(result["schema_version"], 4)
        self.assertEqual(result["request_count"], 21)
        self.assertEqual(len(result["shortlist"]), 5)
        self.assertEqual(
            [
                (item["repository"], item["issue_number"], item["category"])
                for item in result["recommendations"]
            ],
            [
                (
                    "spring-projects/spring-restdocs",
                    201,
                    "Best actionable candidate",
                ),
                ("spring-projects/spring-boot", 301, "Safe docs/test candidate"),
                ("spring-projects/spring-security", 101, "Learning candidate"),
            ],
        )
        self.assertTrue(all(item["score"] == 100 for item in result["recommendations"]))
        self.assertTrue(all(url.startswith(collector.API_ROOT) for url in transport.urls))
        self.assertNotIn("focused OAuth2 regression", json.dumps(result))

    def test_claim_and_undecided_design_are_not_recommended(self) -> None:
        result, _ = self.run_fixture()
        claimed = self.candidate(result, "spring-projects/spring-security", 102)
        undecided = self.candidate(result, "spring-projects/spring-restdocs", 202)

        self.assertEqual(claimed["decision"], "EXCLUDED")
        self.assertIn("work_already_claimed", claimed["exclusion_reasons"])
        self.assertEqual(undecided["decision"], "MANUAL_REVIEW")
        self.assertIn("design_not_decided", undecided["manual_review_reasons"])

    def test_assignment_and_linked_pull_request_are_hard_gates(self) -> None:
        cases = ("assignment", "linked_pull_request")
        for case in cases:
            with self.subTest(case=case):
                fixture = copy.deepcopy(self.fixture)
                detail = fixture["responses"]["detail:spring-projects/spring-security#101"][
                    "body"
                ]
                if case == "assignment":
                    assignee = {"login": "someone", "type": "User"}
                    detail["assignee"] = assignee
                    detail["assignees"] = [assignee]
                else:
                    fixture["responses"][
                        "timeline:spring-projects/spring-security#101"
                    ]["body"] = [
                        {
                            "event": "cross-referenced",
                            "source": {
                                "issue": {
                                    "html_url": (
                                        "https://github.com/spring-projects/"
                                        "spring-security/pull/900"
                                    ),
                                    "pull_request": {},
                                }
                            },
                        }
                    ]
                result, _ = self.run_fixture(fixture)
                candidate = self.candidate(
                    result, "spring-projects/spring-security", 101
                )
                self.assertEqual(candidate["decision"], "EXCLUDED")
                expected = "assigned" if case == "assignment" else "linked_pull_request"
                self.assertIn(expected, candidate["exclusion_reasons"])

    def test_search_prefilter_excludes_assigned_results(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        issue = fixture["responses"]["search:spring-projects/spring-security"]["body"][
            "items"
        ][0]
        assignee = {"login": "someone", "type": "User"}
        issue["assignee"] = assignee
        issue["assignees"] = [assignee]

        result, _ = self.run_fixture(fixture)

        self.assertEqual(len(result["shortlist"]), 4)
        self.assertIn(
            {
                "repository": "spring-projects/spring-security",
                "issue_number": 101,
                "reason": "assigned",
            },
            result["precheck_exclusions"],
        )

    def test_incomplete_api_evidence_blocks_all_recommendations(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        del fixture["responses"]["timeline:spring-projects/spring-boot#301"]

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertEqual(result["recommendations"], [])
        self.assertTrue(any("Fixture response is missing" in error for error in result["errors"]))

    def test_comments_or_timeline_pagination_blocks_recommendations(self) -> None:
        for response_key in (
            "comments:spring-projects/spring-security#101",
            "timeline:spring-projects/spring-security#101",
        ):
            with self.subTest(response_key=response_key):
                fixture = copy.deepcopy(self.fixture)
                fixture["responses"][response_key]["headers"] = {
                    "Link": '<https://api.github.com/next>; rel="next"'
                }

                result, _ = self.run_fixture(fixture)

                self.assertFalse(result["complete"])
                self.assertEqual(result["recommendations"], [])
                self.assertTrue(
                    any("pagination is incomplete" in error for error in result["errors"])
                )

    def test_score_breakdown_stays_within_the_guide_weights(self) -> None:
        profile = self.config["repositories"][0]
        score, breakdown = collector.score_candidate(
            profile,
            ["theme: documentation"],
            {
                "body_substantive": True,
                "scope_defined": False,
                "acceptance_criteria_present": False,
                "reproduction_present": False,
            },
            timedelta(days=120),
        )

        self.assertEqual(score, 74)
        self.assertEqual(
            breakdown,
            {
                "skill_fit": 30,
                "contribution_signal": 12,
                "scope_clarity": 7,
                "validation": 10,
                "maintainer_activity": 5,
                "learning_value": 10,
            },
        )
        self.assertLessEqual(score, 100)

    def test_config_rejects_expiry_and_unsafe_build_commands(self) -> None:
        cases = ("expired", "unsafe")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                if case == "expired":
                    config["valid_until"] = "2026-08-19"
                else:
                    config["repositories"][0]["build_command"] = "./gradlew test; env"
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaises(collector.ConfigurationError):
                    collector.load_config(path, NOW.date())

    def test_repository_config_validation_preserves_error_contracts(self) -> None:
        cases = {
            "missing_key": (
                lambda profile: profile.pop("build_command"),
                "repository contract is incomplete",
            ),
            "strong_signal_without_discovery": (
                lambda profile: profile["strong_signal_labels"].append("help wanted"),
                "strong signals must be discovery labels",
            ),
            "overlapping_labels": (
                lambda profile: profile["exclude_labels"].append(
                    profile["discovery_labels"][0]
                ),
                "discovery and exclusion labels overlap",
            ),
            "invalid_contribution_type": (
                lambda profile: profile["contribution_type_by_label"].update(
                    {"type: feature": "feature"}
                ),
                "contribution type mapping is invalid",
            ),
        }
        for name, (mutate, message) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                mutate(config["repositories"][0])
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(config), encoding="utf-8")

                with self.assertRaisesRegex(collector.ConfigurationError, message):
                    collector.load_config(path, NOW.date())

    def test_live_transport_never_sends_authorization(self) -> None:
        captured: list[object] = []

        def fake_urlopen(request: object, timeout: int) -> FakeHttpResponse:
            captured.append(request)
            self.assertEqual(timeout, 20)
            return FakeHttpResponse()

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            response = collector.LiveTransport(lambda: NOW).get(
                "https://api.github.com/repos/spring-projects/spring-boot"
            )

        headers = dict(captured[0].header_items())
        self.assertEqual(response.body, {"ok": True})
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("GITHUB_TOKEN", json.dumps(headers))

    def test_markdown_has_the_daily_contract_and_escapes_titles(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["responses"]["detail:spring-projects/spring-restdocs#201"]["body"][
            "title"
        ] = "Clarify [unsafe](https://example.com) *title*"
        result, _ = self.run_fixture(fixture)

        markdown = collector.render_markdown(result)

        self.assertIn("# Daily OSS Contribution", markdown)
        self.assertIn("## Recommendation 1", markdown)
        self.assertIn("## Excluded", markdown)
        self.assertIn("## Today", markdown)
        self.assertIn(r"Clarify \[unsafe\]\(https://example.com\) \*title\*", markdown)
        self.assertNotIn("I'd like to work on this issue", markdown)

    def test_fixture_cli_writes_deterministic_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = [
                sys.executable,
                str(ROOT / "scripts/collect_oss_candidates.py"),
                "--fixture",
                str(FIXTURE_PATH),
                "--json-output",
                str(root / "result.json"),
                "--markdown-output",
                str(root / "result.md"),
            ]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            first_json = (root / "result.json").read_text(encoding="utf-8")
            first_markdown = (root / "result.md").read_text(encoding="utf-8")
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            second_json = (root / "result.json").read_text(encoding="utf-8")
            second_markdown = (root / "result.md").read_text(encoding="utf-8")

        self.assertEqual(first.returncode, 0, msg=first.stderr)
        self.assertEqual(second.returncode, 0, msg=second.stderr)
        self.assertEqual(first_json, second_json)
        self.assertEqual(first_markdown, second_markdown)
        self.assertIn("# Daily OSS Contribution", first_markdown)


if __name__ == "__main__":
    unittest.main()
