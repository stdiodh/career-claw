from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import collect_oss_candidates as collector


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests/fixtures/oss-api-responses.json"
NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


class CapturingFixtureTransport(collector.FixtureTransport):
    def __init__(self, fixture: dict[str, object]) -> None:
        super().__init__(fixture, lambda: NOW)
        self.urls: list[str] = []

    def get(self, url: str) -> collector.ApiResponse:
        self.urls.append(url)
        return super().get(url)


class OssCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = collector.load_config(collector.DEFAULT_CONFIG, NOW.date())
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.framework_profile = next(
            profile
            for profile in cls.config["repositories"]
            if profile["repository"] == "spring-projects/spring-framework"
        )

    def run_fixture(
        self, fixture: dict[str, object] | None = None
    ) -> tuple[dict[str, object], CapturingFixtureTransport]:
        transport = CapturingFixtureTransport(fixture or copy.deepcopy(self.fixture))
        client = collector.GitHubClient(transport, self.config["policy"]["request_limit"])
        return collector.collect_candidates(self.config, client, NOW, "fixture"), transport

    def add_fixture_issue(
        self,
        fixture: dict[str, object],
        repository: str,
        number: int,
        *,
        created_day: int,
        updated_day: int,
        manual: bool = False,
    ) -> None:
        profile = next(
            item for item in self.config["repositories"] if item["repository"] == repository
        )
        labels = [
            {"name": profile["include_labels"][0]},
            {"name": next(iter(profile["module_label_to_build_command"]))},
        ]
        created_at = f"2026-07-{created_day:02d}T00:00:00Z"
        updated_at = f"2026-07-{updated_day:02d}T00:00:00Z"
        title = f"Add focused regression test {number}"
        url = f"https://github.com/{repository}/issues/{number}"
        search_item = {
            "number": number,
            "title": title,
            "html_url": url,
            "repository_url": f"https://api.github.com/repos/{repository}",
            "state": "open",
            "locked": False,
            "assignee": None,
            "assignees": [],
            "labels": labels,
            "created_at": created_at,
            "updated_at": updated_at,
        }
        body = (
            "## Scope\n"
            "Add a focused regression test in the labeled module for the target behavior.\n\n"
            "## Acceptance criteria\n"
            "The focused test captures the expected result and existing tests remain green.\n\n"
            "## Reproduction\n"
            f"Run {next(iter(profile['module_label_to_build_command'].values()))}."
        )
        if manual:
            body += "\n\nOpen question: we still need to decide which API to change."
        detail = {
            **search_item,
            "user": {"login": "maintainer", "type": "User"},
            "author_association": "MEMBER",
            "body": body,
        }
        responses = fixture["responses"]
        responses[f"search:{repository}"]["body"]["items"].append(search_item)
        responses[f"detail:{repository}#{number}"] = {"body": detail}
        responses[f"comments:{repository}#{number}"] = {"body": []}
        responses[f"timeline:{repository}#{number}"] = {"body": []}

    def framework_detail(self, **updates: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "number": 200,
            "title": "Clarify web binding test",
            "html_url": "https://github.com/spring-projects/spring-framework/issues/200",
            "repository_url": "https://api.github.com/repos/spring-projects/spring-framework",
            "state": "open",
            "locked": False,
            "assignee": None,
            "assignees": [],
            "labels": [
                {"name": "status: ideal-for-contribution"},
                {"name": "in: web"},
            ],
            "user": {"login": "maintainer", "type": "User"},
            "author_association": "MEMBER",
            "created_at": "2026-07-10T00:00:00Z",
            "updated_at": "2026-07-15T00:00:00Z",
            "body": (
                "## Scope\n"
                "Update the web binding test to document the target method behavior.\n\n"
                "## Acceptance criteria\n"
                "- [ ] The focused test captures the expected result.\n"
                "- [ ] Existing web tests remain green.\n\n"
                "## Reproduction\n"
                "Run ./gradlew :spring-web:test before and after the change."
            ),
        }
        payload.update(updates)
        return payload

    def evaluate(
        self,
        detail: dict[str, object] | None = None,
        comments: list[dict[str, object]] | None = None,
        timeline: list[dict[str, object]] | None = None,
        expected: collector.ExpectedIssue | None = None,
        **options: object,
    ) -> dict[str, object]:
        return collector.evaluate_candidate(
            self.framework_profile,
            expected
            or collector.ExpectedIssue(
                "spring-projects/spring-framework",
                200,
                datetime(2026, 7, 10, tzinfo=timezone.utc),
            ),
            detail or self.framework_detail(),
            comments or [],
            timeline or [],
            NOW,
            NOW,
            **options,
        )

    def test_config_is_the_exact_approved_five_repository_contract(self) -> None:
        self.assertEqual(self.config["schema_version"], 3)
        self.assertEqual(
            tuple(profile["repository"] for profile in self.config["repositories"]),
            collector.ALLOWED_REPOSITORIES,
        )
        self.assertEqual(
            self.config["policy"],
            {
                "lookback_days": 180,
                "fresh_days": 90,
                "warm_days": 180,
                "search_per_repository": 10,
                "detail_limit": 8,
                "ready_limit": 2,
                "max_ready_per_repository": 1,
                "request_limit": 34,
            },
        )
        self.assertTrue(all(profile["checked_at"] for profile in self.config["repositories"]))
        self.assertEqual(
            len(self.config["repositories"]) * 2
            + self.config["policy"]["detail_limit"] * 3,
            34,
        )

    def test_round_robin_backfills_until_fourth_and_fifth_candidates_are_ready(self) -> None:
        result, transport = self.run_fixture()

        self.assertTrue(result["complete"])
        self.assertTrue(result["delivery_allowed"])
        self.assertEqual(result["schema_version"], 3)
        self.assertEqual(result["request_count"], 25)
        self.assertEqual(
            [
                (candidate["repository"], candidate["issue_number"], candidate["decision"])
                for candidate in result["candidates"]
            ],
            [
                ("spring-projects/spring-framework", 200, "MANUAL_REVIEW"),
                ("micrometer-metrics/micrometer", 300, "MANUAL_REVIEW"),
                ("testcontainers/testcontainers-java", 400, "EXCLUDED"),
                ("spring-projects/spring-framework", 201, "READY_TO_ASK"),
                ("micrometer-metrics/micrometer", 301, "READY_TO_ASK"),
            ],
        )
        self.assertEqual(
            [
                (candidate["repository"], candidate["issue_number"])
                for candidate in result["ready_to_ask"]
            ],
            [
                ("spring-projects/spring-framework", 201),
                ("micrometer-metrics/micrometer", 301),
            ],
        )
        self.assertFalse(
            result["candidates"][2]["feasibility_evidence"]["current_review_required"]
        )
        self.assertFalse(any("issues/401" in url for url in transport.urls))
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("Thanks for the report", serialized)
        self.assertNotIn("I'd like to work on this", serialized)
        self.assertNotIn("focused test captures the expected result", serialized)

    def test_ready_limit_keeps_one_candidate_per_repository(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        for key, response in fixture["responses"].items():
            if key.startswith("search:"):
                response["body"]["items"] = []
        self.add_fixture_issue(
            fixture,
            "spring-projects/spring-framework",
            501,
            created_day=10,
            updated_day=15,
        )
        self.add_fixture_issue(
            fixture,
            "spring-projects/spring-framework",
            502,
            created_day=9,
            updated_day=14,
        )
        self.add_fixture_issue(
            fixture,
            "micrometer-metrics/micrometer",
            601,
            created_day=8,
            updated_day=15,
            manual=True,
        )
        self.add_fixture_issue(
            fixture,
            "micrometer-metrics/micrometer",
            602,
            created_day=7,
            updated_day=14,
        )

        result, _ = self.run_fixture(fixture)

        self.assertEqual(
            [candidate["issue_number"] for candidate in result["candidates"]],
            [501, 601, 502, 602],
        )
        self.assertEqual(
            [candidate["issue_number"] for candidate in result["ready_to_ask"]],
            [501, 602],
        )
        self.assertEqual(
            [
                candidate["issue_number"]
                for candidate in result["candidates"]
                if candidate["decision"] == "READY_TO_ASK"
            ],
            [501, 502, 602],
        )

    def test_ready_result_cardinality_is_zero_one_or_two(self) -> None:
        zero_fixture = copy.deepcopy(self.fixture)
        for key, response in zero_fixture["responses"].items():
            if key.startswith("search:"):
                response["body"]["items"] = []

        one_fixture = copy.deepcopy(zero_fixture)
        self.add_fixture_issue(
            one_fixture,
            "spring-projects/spring-framework",
            501,
            created_day=10,
            updated_day=15,
        )

        zero, _ = self.run_fixture(zero_fixture)
        one, _ = self.run_fixture(one_fixture)
        two, _ = self.run_fixture()

        self.assertEqual(
            [len(result["ready_to_ask"]) for result in (zero, one, two)],
            [0, 1, 2],
        )

    def test_detail_and_request_limits_stop_after_eight_candidates(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        for key, response in fixture["responses"].items():
            if key.startswith("search:"):
                response["body"]["items"] = []
        repositories = list(collector.ALLOWED_REPOSITORIES)
        for index in range(9):
            self.add_fixture_issue(
                fixture,
                repositories[index % len(repositories)],
                700 + index,
                created_day=1,
                updated_day=15,
                manual=True,
            )

        result, transport = self.run_fixture(fixture)

        self.assertTrue(result["complete"])
        self.assertEqual(len(result["candidates"]), 8)
        self.assertEqual(result["ready_to_ask"], [])
        self.assertEqual(result["request_count"], 34)
        self.assertLessEqual(result["request_count"], result["request_limit"])
        self.assertFalse(any("issues/708" in url for url in transport.urls))

    def test_feasibility_evidence_is_derived_without_persisting_issue_body(self) -> None:
        result = self.evaluate()

        self.assertEqual(result["decision"], "READY_TO_ASK")
        self.assertEqual(
            result["feasibility_evidence"],
            {
                "scope_defined": True,
                "acceptance_criteria_present": True,
                "reproduction_steps_present": True,
                "current_review_required": True,
            },
        )
        self.assertNotIn("focused test captures the expected result", json.dumps(result))

    def test_uncertain_issue_body_requires_manual_review(self) -> None:
        cases = (
            (None, "issue_body_missing", False),
            (
                "<!-- Complete every section before submitting. -->",
                "issue_body_missing",
                False,
            ),
            (
                "Please fix this.",
                "scope_evidence_insufficient",
                False,
            ),
            (
                self.framework_detail()["body"]
                + "\n\nOpen question: we still need to decide which API to change.",
                "design_undecided",
                True,
            ),
            (
                self.framework_detail()["body"]
                + "\n\nI'd like to work on this issue.",
                "issue_author_claims_work",
                True,
            ),
            (
                self.framework_detail()["body"]
                + "\n\nHappy to send a PR once the approach is confirmed.",
                "issue_author_claims_work",
                True,
            ),
            (
                "## Scope\nUpdate the web binding test to document the target method behavior. "
                "Keep the focused change within the spring-web module.\n\n"
                "## Reproduction\nRun ./gradlew :spring-web:test.",
                "acceptance_criteria_missing",
                True,
            ),
            (
                "## Scope\nUpdate the web binding test to document the target method behavior. "
                "Keep the focused change within the spring-web module.\n\n"
                "## Acceptance criteria\nThe focused test captures the expected result.",
                "reproduction_steps_missing",
                True,
            ),
        )
        for body, expected_reason, scope_defined in cases:
            with self.subTest(reason=expected_reason):
                result = self.evaluate(self.framework_detail(body=body))

                self.assertEqual(result["decision"], "MANUAL_REVIEW")
                self.assertIn(expected_reason, result["manual_review_reasons"])
                self.assertIs(
                    result["feasibility_evidence"]["scope_defined"], scope_defined
                )
                self.assertTrue(
                    result["feasibility_evidence"]["current_review_required"]
                )

    def test_empty_searches_complete_without_detail_requests(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        for key, response in fixture["responses"].items():
            if key.startswith("search:"):
                response["body"]["items"] = []

        result, _ = self.run_fixture(fixture)

        self.assertTrue(result["complete"])
        self.assertTrue(result["delivery_allowed"])
        self.assertEqual(result["request_count"], 10)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["ready_to_ask"], [])

    def test_search_is_server_sorted_by_created_desc_with_approved_prefilter(self) -> None:
        _, transport = self.run_fixture()
        search_urls = [url for url in transport.urls if "/search/issues?" in url]

        self.assertEqual(len(search_urls), len(collector.ALLOWED_REPOSITORIES))
        for url in search_urls:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            self.assertEqual(query["sort"], ["created"])
            self.assertEqual(query["order"], ["desc"])
            self.assertEqual(query["per_page"], ["10"])
            search_query = query["q"][0]
            self.assertIn("is:issue", search_query)
            self.assertIn("is:open", search_query)
            self.assertIn("no:assignee", search_query)
            self.assertIn("-linked:pr", search_query)
            self.assertIn("archived:false", search_query)
            self.assertIn("updated:>=2026-01-17", search_query)

    def test_freshness_boundaries_are_inclusive(self) -> None:
        cases = (
            (90, "FRESH", None),
            (91, "WARM", None),
            (180, "WARM", None),
            (181, None, "maintainer_activity_older_than_180_days"),
        )
        for days, expected, reason in cases:
            with self.subTest(days=days):
                self.assertEqual(
                    collector.freshness(NOW - timedelta(days=days), NOW),
                    (expected, reason),
                )

    def test_external_comment_does_not_refresh_old_maintainer_activity(self) -> None:
        detail = self.framework_detail(
            user={"login": "external", "type": "User"},
            author_association="NONE",
            updated_at="2026-07-15T00:00:00Z",
        )
        comments = [
            {
                "user": {"login": "maintainer", "type": "User"},
                "author_association": "MEMBER",
                "body": "Old maintainer response",
                "created_at": "2026-01-16T00:00:00Z",
            },
            {
                "user": {"login": "external-two", "type": "User"},
                "author_association": "NONE",
                "body": "Any update?",
                "created_at": "2026-07-15T00:00:00Z",
            },
        ]

        result = self.evaluate(detail, comments)

        self.assertEqual(result["decision"], "EXCLUDED")
        self.assertIn("maintainer_activity_older_than_180_days", result["exclusion_reasons"])

    def test_bot_activity_is_not_maintainer_activity(self) -> None:
        detail = self.framework_detail(
            user={"login": "external", "type": "User"},
            author_association="NONE",
        )
        timeline = [
            {
                "event": "labeled",
                "actor": {"login": "github-actions[bot]", "type": "Bot"},
                "created_at": "2026-07-15T00:00:00Z",
            }
        ]

        result = self.evaluate(detail, timeline=timeline)

        self.assertEqual(result["decision"], "EXCLUDED")
        self.assertIn("no_maintainer_activity", result["exclusion_reasons"])

    def test_missing_or_malformed_timeline_actor_never_refreshes_activity(self) -> None:
        detail = self.framework_detail(
            user={"login": "external", "type": "User"},
            author_association="NONE",
        )
        actors = (None, {}, {"login": 7, "type": "User"}, {"login": "user"})
        for actor in actors:
            with self.subTest(actor=actor):
                result = self.evaluate(
                    detail,
                    timeline=[
                        {
                            "event": "labeled",
                            "actor": actor,
                            "created_at": "2026-07-15T00:00:00Z",
                        }
                    ],
                )
                self.assertEqual(result["decision"], "EXCLUDED")
                self.assertIn("no_maintainer_activity", result["exclusion_reasons"])
                self.assertIn(
                    "invalid_activity_evidence", result["manual_review_reasons"]
                )

    def test_missing_maintainer_user_never_counts_as_activity(self) -> None:
        detail = self.framework_detail(
            user={"login": "external", "type": "User"},
            author_association="NONE",
        )
        result = self.evaluate(
            detail,
            comments=[
                {
                    "author_association": "MEMBER",
                    "body": "Missing actor evidence",
                    "created_at": "2026-07-15T00:00:00Z",
                }
            ],
        )

        self.assertEqual(result["decision"], "EXCLUDED")
        self.assertIn("no_maintainer_activity", result["exclusion_reasons"])
        self.assertIn("invalid_activity_evidence", result["manual_review_reasons"])

    def test_repository_queue_prioritizes_labels_then_contribution_type(self) -> None:
        profile = {
            "contribution_type_by_label": {
                "test-kind": "test",
                "docs-kind": "docs",
                "sample-kind": "sample",
                "code-kind": "code",
            },
            "default_contribution_type": "code/test",
        }

        def item(number: int, inclusion: str, kind: str | None) -> dict[str, object]:
            labels = [{"name": inclusion}]
            if kind is not None:
                labels.append({"name": kind})
            return {
                "number": number,
                "labels": labels,
                "_profile": profile,
                "_repository": "example/repository",
                "_created": NOW,
                "_updated": NOW,
            }

        items = [
            item(8, "help wanted", "test-kind"),
            item(7, "good first issue", "test-kind"),
            item(6, "status: ideal-for-contribution", None),
            item(5, "status: ideal-for-contribution", "code-kind"),
            item(4, "status: ideal-for-contribution", "sample-kind"),
            item(3, "status: ideal-for-contribution", "docs-kind"),
            item(2, "status: ideal-for-contribution", "test-kind"),
            item(1, "status: first-timers-only", "code-kind"),
        ]

        ordered = collector.sort_repository_candidates(items)

        self.assertEqual([candidate["number"] for candidate in ordered], list(range(1, 9)))

    def test_repository_queue_tie_breaks_by_updated_created_and_identity(self) -> None:
        profile = {
            "contribution_type_by_label": {"test-kind": "test"},
            "default_contribution_type": "code/test",
        }

        def item(number: int, updated: int, created: int) -> dict[str, object]:
            return {
                "number": number,
                "labels": [
                    {"name": "status: ideal-for-contribution"},
                    {"name": "test-kind"},
                ],
                "_profile": profile,
                "_repository": "example/repository",
                "_created": NOW - timedelta(days=created),
                "_updated": NOW - timedelta(days=updated),
            }

        ordered = collector.sort_repository_candidates(
            [item(4, 2, 1), item(3, 1, 2), item(2, 1, 1), item(1, 1, 1)]
        )

        self.assertEqual([candidate["number"] for candidate in ordered], [1, 2, 3, 4])

    def test_closed_pr_assigned_and_excluded_label_are_hard_failures(self) -> None:
        cases = (
            ({"state": "closed"}, "closed"),
            ({"pull_request": {"url": "https://api.github.com/pulls/1"}}, "pull_request"),
            (
                {
                    "assignee": {"login": "worker"},
                    "assignees": [{"login": "worker"}],
                },
                "assigned",
            ),
            (
                {
                    "labels": [
                        {"name": "status: ideal-for-contribution"},
                        {"name": "in: web"},
                        {"name": "status: blocked"},
                    ]
                },
                "excluded_label:status: blocked",
            ),
        )
        for updates, reason in cases:
            with self.subTest(reason=reason):
                result = self.evaluate(self.framework_detail(**updates))
                self.assertEqual(result["decision"], "EXCLUDED")
                self.assertIn(reason, result["exclusion_reasons"])

    def test_linked_and_cross_referenced_pull_requests_are_excluded(self) -> None:
        events = [
            {
                "event": "cross-referenced",
                "source": {
                    "issue": {
                        "html_url": "https://github.com/example/repo/pull/99",
                        "pull_request": {"url": "https://api.github.com/repos/example/repo/pulls/99"},
                    }
                },
            }
        ]

        result = self.evaluate(timeline=events)

        self.assertEqual(result["decision"], "EXCLUDED")
        self.assertIn("linked_pull_request", result["exclusion_reasons"])

    def test_connected_pr_type_and_pull_urls_are_detected_case_insensitively(self) -> None:
        events = (
            {
                "event": "CONNECTED",
                "subject": {"type": "pull_request"},
            },
            {
                "event": "Cross-Referenced",
                "source": {
                    "issue": {
                        "html_url": "https://github.com/example/repo/PULL/42"
                    }
                },
            },
            {
                "event": "connected",
                "subject": {
                    "url": "https://api.github.com/repos/example/repo/pulls/42",
                    "type": "Pull Request",
                },
            },
        )
        for event in events:
            with self.subTest(event=event):
                result = self.evaluate(timeline=[event])
                self.assertEqual(result["decision"], "EXCLUDED")
                self.assertIn("linked_pull_request", result["exclusion_reasons"])

    def test_detail_must_match_preselected_repository_number_and_created_at(self) -> None:
        cases = (
            (
                collector.ExpectedIssue(
                    "other/repository", 200, datetime(2026, 7, 10, tzinfo=timezone.utc)
                ),
                "preselected_repository_mismatch",
            ),
            (
                collector.ExpectedIssue(
                    "spring-projects/spring-framework",
                    201,
                    datetime(2026, 7, 10, tzinfo=timezone.utc),
                ),
                "preselected_number_mismatch",
            ),
            (
                collector.ExpectedIssue(
                    "spring-projects/spring-framework",
                    200,
                    datetime(2026, 7, 9, tzinfo=timezone.utc),
                ),
                "preselected_created_at_mismatch",
            ),
        )
        for expected, reason in cases:
            with self.subTest(reason=reason):
                result = self.evaluate(expected=expected)
                self.assertEqual(result["decision"], "EXCLUDED")
                self.assertIn(reason, result["exclusion_reasons"])

    def test_claim_comment_is_excluded_and_ambiguous_comment_is_manual(self) -> None:
        claim = {
            "user": {"login": "contributor", "type": "User"},
            "author_association": "NONE",
            "body": "Please assign this issue to me",
            "created_at": "2026-07-15T00:00:00Z",
        }
        ambiguous = {**claim, "body": "I reproduced the behavior on Linux."}

        excluded = self.evaluate(comments=[claim])
        manual = self.evaluate(comments=[ambiguous])

        self.assertEqual(excluded["decision"], "EXCLUDED")
        self.assertIn("claim_comment", excluded["exclusion_reasons"])
        self.assertEqual(manual["decision"], "MANUAL_REVIEW")
        self.assertIn(
            "external_comment_requires_manual_review", manual["manual_review_reasons"]
        )

    def test_comments_or_timeline_pagination_is_manual_review(self) -> None:
        comments_result = self.evaluate(comments_paginated=True)
        timeline_result = self.evaluate(timeline_paginated=True)

        self.assertEqual(comments_result["decision"], "MANUAL_REVIEW")
        self.assertIn(
            "comments_pagination_incomplete", comments_result["manual_review_reasons"]
        )
        self.assertEqual(timeline_result["decision"], "MANUAL_REVIEW")
        self.assertIn(
            "timeline_pagination_incomplete", timeline_result["manual_review_reasons"]
        )

    def test_missing_module_mapping_is_manual_review(self) -> None:
        detail = self.framework_detail(
            labels=[{"name": "status: ideal-for-contribution"}]
        )

        result = self.evaluate(detail)

        self.assertEqual(result["decision"], "MANUAL_REVIEW")
        self.assertIn("module_mapping_missing", result["manual_review_reasons"])

    def test_duplicate_search_issue_is_removed_before_queueing(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        items = fixture["responses"]["search:micrometer-metrics/micrometer"]["body"]["items"]
        items.append(copy.deepcopy(items[0]))

        result, _ = self.run_fixture(fixture)

        duplicates = [
            item for item in result["precheck_exclusions"] if item["reason"] == "duplicate_search_result"
        ]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(result["request_count"], 25)

    def test_allowlist_repository_and_url_mismatch_are_rejected(self) -> None:
        search_item = copy.deepcopy(
            self.fixture["responses"]["search:spring-projects/spring-framework"]["body"]["items"][0]
        )
        search_item["html_url"] = "https://github.com/other/repo/issues/200"

        validated, reason = collector.validate_search_issue(
            self.framework_profile, search_item, NOW - timedelta(days=180)
        )

        self.assertIsNone(validated)
        self.assertEqual(reason, "issue_url_not_allowlisted")

    def test_search_requires_title_locked_and_structured_assignees(self) -> None:
        original = self.fixture["responses"]["search:spring-projects/spring-framework"]["body"][
            "items"
        ][0]
        cases = (
            ({"title": {"unexpected": "object"}}, "invalid_title"),
            ({"locked": "false"}, "invalid_locked"),
            ({"assignee": {"login": "worker"}, "assignees": []}, "invalid_assignees"),
            ({"assignees": "nobody"}, "invalid_assignees"),
            ({"assignees": [{}]}, "invalid_assignees"),
        )
        for updates, expected_reason in cases:
            with self.subTest(reason=expected_reason):
                item = {**copy.deepcopy(original), **updates}
                validated, reason = collector.validate_search_issue(
                    self.framework_profile, item, NOW - timedelta(days=180)
                )
                self.assertIsNone(validated)
                self.assertEqual(reason, expected_reason)

    def test_malformed_issue_labels_fail_closed(self) -> None:
        search_item = copy.deepcopy(
            self.fixture["responses"]["search:spring-projects/spring-framework"]["body"][
                "items"
            ][0]
        )
        search_item["labels"].append({"color": "missing-name"})

        validated, reason = collector.validate_search_issue(
            self.framework_profile, search_item, NOW - timedelta(days=180)
        )
        detail = self.framework_detail(
            labels=[
                {"name": "status: ideal-for-contribution"},
                {"name": "in: web"},
                {"color": "missing-name"},
            ]
        )
        candidate = self.evaluate(detail)

        self.assertIsNone(validated)
        self.assertEqual(reason, "invalid_labels")
        self.assertEqual(candidate["decision"], "EXCLUDED")
        self.assertIn("invalid_labels", candidate["exclusion_reasons"])

    def test_search_timestamps_must_be_ordered_and_not_future(self) -> None:
        original = copy.deepcopy(
            self.fixture["responses"]["search:spring-projects/spring-framework"]["body"][
                "items"
            ][0]
        )
        cases = (
            {
                "created_at": "2026-07-15T00:00:00Z",
                "updated_at": "2026-07-14T00:00:00Z",
            },
            {"updated_at": "2026-07-16T00:00:01Z"},
        )
        for updates in cases:
            with self.subTest(updates=updates):
                validated, reason = collector.validate_search_issue(
                    self.framework_profile,
                    {**original, **updates},
                    NOW - timedelta(days=180),
                )
                self.assertIsNone(validated)
                self.assertEqual(reason, "invalid_issue_timestamp")

    def test_invalid_search_number_is_normalized_in_precheck_evidence(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        item = fixture["responses"]["search:spring-projects/spring-framework"]["body"][
            "items"
        ][0]
        item["number"] = "not-an-integer"

        result, _ = self.run_fixture(fixture)
        exclusion = next(
            item
            for item in result["precheck_exclusions"]
            if item["reason"] == "invalid_issue_number"
        )

        self.assertIsNone(exclusion["issue_number"])

    def test_detail_requires_title_locked_and_structured_assignees(self) -> None:
        cases = (
            ({"title": ["not", "a", "string"]}, "invalid_title"),
            ({"locked": 0}, "invalid_locked"),
            ({"assignee": {"login": "worker"}, "assignees": []}, "invalid_assignees"),
            ({"assignees": None}, "invalid_assignees"),
            ({"assignees": [{"id": 1}]}, "invalid_assignees"),
        )
        for updates, reason in cases:
            with self.subTest(reason=reason):
                result = self.evaluate(self.framework_detail(**updates))
                self.assertEqual(result["decision"], "EXCLUDED")
                self.assertIn(reason, result["exclusion_reasons"])

    def test_detail_timestamp_failures_are_normalized_or_fail_closed(self) -> None:
        future = self.evaluate(
            self.framework_detail(updated_at="2026-07-16T00:00:01Z")
        )
        stale = self.evaluate(
            self.framework_detail(
                created_at="2025-12-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
            expected=collector.ExpectedIssue(
                "spring-projects/spring-framework",
                200,
                datetime(2025, 12, 1, tzinfo=timezone.utc),
            ),
        )
        activity_before_creation = self.evaluate(
            self.framework_detail(
                user={"login": "external", "type": "User"},
                author_association="NONE",
            ),
            comments=[
                {
                    "user": {"login": "maintainer", "type": "User"},
                    "author_association": "MEMBER",
                    "body": "Impossible early activity",
                    "created_at": "2026-07-01T00:00:00Z",
                }
            ],
        )

        self.assertEqual(future["decision"], "EXCLUDED")
        self.assertIn("invalid_issue_timestamp", future["exclusion_reasons"])
        self.assertIsNone(future["updated_at"])
        self.assertEqual(stale["decision"], "EXCLUDED")
        self.assertIn("outside_updated_window", stale["exclusion_reasons"])
        self.assertEqual(activity_before_creation["decision"], "MANUAL_REVIEW")
        self.assertIn(
            "invalid_activity_evidence",
            activity_before_creation["manual_review_reasons"],
        )

    def test_rate_limit_window_crossing_marks_run_incomplete(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        reset_at = NOW + timedelta(seconds=30)
        fixture["default_headers"]["X-RateLimit-Reset"] = str(
            int(reset_at.timestamp())
        )
        calls = 0

        def clock() -> datetime:
            nonlocal calls
            calls += 1
            return NOW if calls <= 25 else NOW + timedelta(minutes=1)

        transport = collector.FixtureTransport(fixture, clock)
        result = collector.collect_candidates(
            self.config,
            collector.GitHubClient(transport, 34),
            NOW,
            "fixture",
        )

        self.assertFalse(result["complete"])
        self.assertIn("core rate-limit reset passed during collection", result["errors"])
        self.assertIn("search rate-limit reset passed during collection", result["errors"])

    def test_anonymous_rate_limit_maximums_fail_closed(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["default_headers"]["X-RateLimit-Remaining"] = "61"

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertIn(
            "core rate-limit remaining exceeds anonymous policy", result["errors"]
        )

    def test_unexpected_rate_limit_resource_fails_closed_without_leaking_bucket(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["responses"]["detail:micrometer-metrics/micrometer#300"]["headers"] = {
            "X-RateLimit-Resource": "graphql"
        }

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertIn("unexpected rate-limit resource: graphql", result["errors"])
        self.assertEqual(set(result["rate_limits"]), {"core", "search"})

    def test_one_malformed_rate_limit_header_fails_closed(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["responses"]["detail:micrometer-metrics/micrometer#300"]["headers"] = {
            "X-RateLimit-Reset": "not-an-epoch"
        }

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertIn("invalid rate-limit headers", result["errors"])

    def test_config_rejects_shell_metacharacters_and_newlines_in_build_commands(self) -> None:
        unsafe_commands = (
            "./gradlew test; curl example.com",
            "./gradlew test && whoami",
            "./gradlew test\nwhoami",
            "./gradlew test $(whoami)",
            "./gradlew test | tee output",
        )
        for command in unsafe_commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                config["repositories"][0]["module_label_to_build_command"][
                    "theme: config-data"
                ] = command
                path = Path(directory) / "oss.json"
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaisesRegex(collector.ConfigurationError, "is unsafe"):
                    collector.load_config(path, NOW.date())

    def test_allowlist_review_dates_fail_closed_when_future_stale_or_mismatched(self) -> None:
        cases = (
            (
                "future",
                {"checked_at": "2026-07-17", "valid_until": "2026-10-15"},
                "cannot be in the future",
            ),
            (
                "expired",
                {"checked_at": "2026-04-15", "valid_until": "2026-07-15"},
                "review is expired",
            ),
        )
        for name, updates, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                config.update(updates)
                for profile in config["repositories"]:
                    profile["checked_at"] = updates["checked_at"]
                path = Path(directory) / "oss.json"
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaisesRegex(collector.ConfigurationError, expected):
                    collector.load_config(path, NOW.date())

        with tempfile.TemporaryDirectory() as directory:
            config = copy.deepcopy(self.config)
            config["repositories"][0]["checked_at"] = "2026-07-15"
            path = Path(directory) / "oss.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(collector.ConfigurationError, "must match"):
                collector.load_config(path, NOW.date())

    def test_allowlist_eligibility_evidence_rejects_inactive_or_internal_repositories(self) -> None:
        cases = (
            ("archived", lambda evidence: evidence.__setitem__("archived", True)),
            (
                "stale activity",
                lambda evidence: evidence.__setitem__(
                    "default_branch_pushed_at", "2026-04-17T00:00:00Z"
                ),
            ),
            (
                "bot PR",
                lambda evidence: evidence["external_merged_pull_request"].update(
                    {"author_type": "Bot", "author_association": "NONE"}
                ),
            ),
            (
                "proprietary build",
                lambda evidence: evidence["build_test"].__setitem__(
                    "proprietary_environment_required", True
                ),
            ),
        )
        for name, mutate in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                mutate(config["repositories"][0]["eligibility_evidence"])
                path = Path(directory) / "oss.json"
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaises(collector.ConfigurationError):
                    collector.load_config(path, NOW.date())

        with tempfile.TemporaryDirectory() as directory:
            config = copy.deepcopy(self.config)
            config["excluded_repositories"][0][
                "external_human_merged_pull_request_count"
            ] = 1
            path = Path(directory) / "oss.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(collector.ConfigurationError, "exclusion evidence"):
                collector.load_config(path, NOW.date())

    def test_live_transport_never_adds_an_authorization_header(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        response.__enter__.return_value.status = 200
        response.__enter__.return_value.headers.items.return_value = []
        clock = lambda: datetime(2026, 7, 16, tzinfo=timezone.utc)

        with mock.patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "ignored", "GH_TOKEN": "ignored"},
            clear=True,
        ), mock.patch("urllib.request.urlopen", return_value=response) as urlopen:
            collector.HttpTransport(clock).get("https://api.github.com/rate_limit")

        request = urlopen.call_args.args[0]
        self.assertNotIn("Authorization", request.headers)

    def test_untrusted_issue_title_is_markdown_escaped(self) -> None:
        result, _ = self.run_fixture()
        candidate = self.evaluate(
            self.framework_detail(title="[trusted](https://evil.example) *urgent* |spoof|")
        )
        result["complete"] = True
        result["ready_to_ask"] = [candidate]

        markdown = collector.render_markdown(result)

        self.assertNotIn("[trusted](https://evil.example)", markdown)
        self.assertIn(r"\[trusted\]\(https://evil.example\)", markdown)
        self.assertIn(r"\*urgent\*", markdown)
        self.assertIn(
            "실행 가능성 근거: 범위 있음 · 완료 조건 있음 · 재현 있음",
            markdown,
        )
        self.assertIn("첫 30분:", markdown)
        self.assertIn("기준선 확인 → issue 재현 절차 실행", markdown)
        self.assertIn("선정 이유:", markdown)
        self.assertIn("현재 검토 필요: 예", markdown)
        self.assertIn("maintainer 문의 초안:", markdown)
        self.assertIn("Hi, is this issue still available?", markdown)
        self.assertNotIn("target method behavior", markdown)

    def test_api_partial_failure_marks_incomplete_and_blocks_candidates(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["responses"]["labels:spring-projects/spring-boot"]["status"] = 403

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertFalse(result["delivery_allowed"])
        self.assertEqual(result["ready_to_ask"], [])
        self.assertTrue(result["errors"])

    def test_non_200_success_class_status_still_fails_closed(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        for response in fixture["responses"].values():
            response["status"] = 201

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertEqual(result["ready_to_ask"], [])
        self.assertGreater(result["http_status_counts"].get("201", 0), 0)

    def test_invalid_detail_payload_marks_entire_run_incomplete(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["responses"]["comments:micrometer-metrics/micrometer#300"]["body"] = {
            "message": "unexpected object"
        }

        result, _ = self.run_fixture(fixture)

        self.assertFalse(result["complete"])
        self.assertEqual(result["ready_to_ask"], [])
        self.assertTrue(
            any("detailed API payload is invalid" in error for error in result["errors"])
        )

    def test_labels_pagination_succeeds_when_configured_labels_are_on_first_page(
        self,
    ) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["responses"]["labels:spring-projects/spring-boot"]["headers"] = {
            "Link": '<https://api.github.com/repositories/1/labels?page=2>; rel="next"'
        }

        result, _ = self.run_fixture(fixture)
        boot = result["repository_results"][0]

        self.assertTrue(result["complete"])
        self.assertEqual(boot["label_contract"], "VERIFIED")
        self.assertIsNone(boot["fail_closed_reason"])
        self.assertEqual(boot["missing_labels"], [])

    def test_labels_pagination_fails_closed_when_configured_label_is_missing(
        self,
    ) -> None:
        fixture = copy.deepcopy(self.fixture)
        labels = fixture["responses"]["labels:spring-projects/spring-boot"]["body"]
        labels[:] = [label for label in labels if label["name"] != "status: blocked"]
        fixture["responses"]["labels:spring-projects/spring-boot"]["headers"] = {
            "Link": '<https://api.github.com/repositories/1/labels?page=2>; rel="next"'
        }

        result, _ = self.run_fixture(fixture)
        boot = result["repository_results"][0]

        self.assertTrue(result["complete"])
        self.assertEqual(boot["label_contract"], "FAILED")
        self.assertEqual(boot["fail_closed_reason"], "labels_pagination_incomplete")
        self.assertEqual(boot["missing_labels"], ["status: blocked"])
        self.assertEqual(boot["search_count"], 0)
        self.assertTrue(result["warnings"])

    def test_missing_configured_label_fails_only_that_repository_closed(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        labels = fixture["responses"]["labels:spring-projects/spring-boot"]["body"]
        labels[:] = [label for label in labels if label["name"] != "status: blocked"]

        result, _ = self.run_fixture(fixture)
        boot = result["repository_results"][0]

        self.assertTrue(result["complete"])
        self.assertEqual(boot["fail_closed_reason"], "configured_label_missing")
        self.assertEqual(boot["missing_labels"], ["status: blocked"])

    def test_request_limit_raises_before_the_next_request(self) -> None:
        transport = collector.FixtureTransport(self.fixture, lambda: NOW)
        client = collector.GitHubClient(transport, 1)
        client.get("/repos/spring-projects/spring-boot/labels", {"per_page": 100})

        with self.assertRaisesRegex(collector.ApiError, "request limit exceeded"):
            client.get("/repos/spring-projects/spring-framework/labels", {"per_page": 100})
        self.assertEqual(client.request_count, 1)

    def test_fixture_cli_writes_deterministic_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            command = [
                sys.executable,
                str(ROOT / "scripts/collect_oss_candidates.py"),
                "--fixture",
                str(FIXTURE_PATH),
                "--now",
                "2026-07-16T00:00:00Z",
                "--json-output",
                str(output / "oss.json"),
                "--markdown-output",
                str(output / "oss.md"),
            ]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            first_json = (output / "oss.json").read_text(encoding="utf-8")
            first_markdown = (output / "oss.md").read_text(encoding="utf-8")
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first_json, (output / "oss.json").read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, (output / "oss.md").read_text(encoding="utf-8"))
            self.assertIn("READY_TO_ASK", first_markdown)


if __name__ == "__main__":
    unittest.main()
