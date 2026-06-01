#!/usr/bin/env python3
"""Smoke tests for the OSS candidate reliability gate."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import urllib.error
from datetime import datetime
from email.message import Message
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "collect-kr-feeds.py"
KST = ZoneInfo("Asia/Seoul")


def load_collector():
    spec = importlib.util.spec_from_file_location("collect_kr_feeds", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load collect-kr-feeds.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


collector = load_collector()


CATEGORY = {
    "positive_labels": ["status: ideal-for-contribution"],
    "negative_keywords": [],
}
DIFFICULTY_MODEL = {
    "p5_like": {
        "positive_labels": ["status: ideal-for-contribution"],
        "positive_keywords": ["documentation", "docs", "test", "reproducer"],
    },
    "p4_like": {
        "positive_labels": ["type: enhancement"],
        "positive_keywords": ["configuration"],
    },
}
PROFILED_OSS_CONFIG = {
    "trusted_maintainers": {},
    "repository_profiles": [
        {
            "repository": "spring-projects/spring-boot",
            "priority": "A",
            "initial_fit_score": 82,
            "ecosystem_tags": ["spring", "backend"],
            "beginner_labels": ["status: ideal-for-contribution"],
            "avoid_labels": ["component: compiler"],
            "avoid_title_keywords": ["compiler redesign"],
            "preferred_contribution_types": ["docs", "test"],
            "contribution_guide": "CONTRIBUTING.adoc",
            "search_queries": [
                {"name": "docs", "query": "is:issue is:open no:assignee documentation"}
            ],
            "local_check_hints": ["./gradlew test"],
            "docs_or_test_hints": ["spring-boot docs"],
            "junior_notes": "문서와 테스트 재현 우선",
        }
    ],
}
CURRENT_TIME = datetime(2026, 6, 1, 9, 0, tzinfo=KST)


def reset_gate() -> None:
    collector.SOURCE_ERRORS.clear()
    collector.OSS_GATE_EXCLUSION_COUNTS.clear()
    collector.OSS_EXCLUDED_CANDIDATE_PREVIEW.clear()
    collector.fetch_github_issue_comments = (
        lambda repository, issue_number, token, expected_count=0: []
    )
    collector.fetch_github_linked_work_check = lambda repository, issue_number, token: (
        collector.GitHubLinkedWorkCheck(
            check_status="verified",
            linked_prs_count=0,
            linked_branches_count=0,
            has_linked_work=False,
            source="test",
            timeline_page_complete=True,
        )
    )


def issue_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "number": 101,
        "state": "open",
        "title": "Improve documentation for getting started tests",
        "html_url": "https://github.com/spring-projects/spring-boot/issues/101",
        "body": "Documentation update with a clear getting started test path. " * 2,
        "user": {"login": "maintainer"},
        "author_association": "MEMBER",
        "labels": [{"name": "status: ideal-for-contribution"}],
        "assignees": [],
        "comments": 0,
        "created_at": "2026-05-01T00:00:00Z",
        "updated_at": "2026-05-30T00:00:00Z",
    }
    payload.update(overrides)
    return payload


def build_candidate(issue: dict[str, object], oss_config: dict[str, object] | None = None):
    return collector.build_oss_issue_candidate(
        CATEGORY,
        DIFFICULTY_MODEL,
        oss_config or PROFILED_OSS_CONFIG,
        "spring-projects/spring-boot",
        issue,
        "token",
        CURRENT_TIME,
    )


def assert_excluded(reason: str, issue: dict[str, object]) -> None:
    reset_gate()
    candidate = build_candidate(issue)
    if candidate is not None:
        raise AssertionError(f"Expected issue to be excluded: {reason}")
    if collector.OSS_GATE_EXCLUSION_COUNTS.get(reason, 0) < 1:
        raise AssertionError(f"Expected exclusion counter for {reason}")


def test_safe_maintainer_authored_issue() -> None:
    reset_gate()
    candidate = build_candidate(issue_payload())
    assert candidate is not None
    assert candidate.safe_to_recommend is True
    assert candidate.maintainer_authored is True
    assert candidate.maintainer_qualified is True
    assert candidate.has_assignee is False
    assert candidate.linked_work_check == "verified"
    assert candidate.linked_prs_count == 0
    assert candidate.linked_branches_count == 0
    assert candidate.score >= 85
    assert candidate.score_breakdown == {
        "technical_fit": 28,
        "external_contribution_signal": 20,
        "scope_clarity": 15,
        "validation_feasibility": 15,
        "maintainer_signal": 10,
        "portfolio_value": 10,
    }
    assert candidate.safety_checks["linked_work_check_complete"] is True
    assert candidate.safety_checks["has_no_linked_work"] is True
    assert "Please let me know" in candidate.suggested_first_comment


def test_safe_maintainer_triaged_issue() -> None:
    reset_gate()
    candidate = build_candidate(
        issue_payload(
            user={"login": "external"},
            author_association="NONE",
            labels=[{"name": "good first issue"}],
        )
    )
    assert candidate is not None
    assert candidate.safe_to_recommend is True
    assert candidate.maintainer_authored is False
    assert candidate.maintainer_triaged is True
    assert candidate.maintainer_qualified is True


def test_repository_profile_is_reflected_in_candidate_evidence() -> None:
    reset_gate()
    candidate = build_candidate(issue_payload(), PROFILED_OSS_CONFIG)
    assert candidate is not None
    assert candidate.repository_priority == "A"
    assert candidate.repository_initial_fit_score == 82
    assert candidate.repository_ecosystem_tags == ["spring", "backend"]
    assert candidate.repository_local_check_hints == ["./gradlew test"]
    assert candidate.repository_docs_or_test_hints == ["spring-boot docs"]
    assert candidate.repository_junior_notes == "문서와 테스트 재현 우선"
    assert "./gradlew test" in candidate.first_30_min_action
    assert any("repository priority A" in item for item in candidate.junior_fit_evidence)
    assert any("ecosystem: spring, backend" in item for item in candidate.junior_fit_evidence)
    assert any("preferred contribution type: docs" in item for item in candidate.junior_fit_evidence)
    assert any("docs/test hint: spring-boot docs" in item for item in candidate.junior_fit_evidence)
    serialized = collector.serialize_oss_issue_candidate(candidate)
    assert serialized["repository_priority"] == "A"
    assert serialized["repository_initial_fit_score"] == 82
    assert serialized["score_breakdown"]["technical_fit"] == 28
    assert serialized["safety_checks"]["has_no_assignee"] is True
    assert serialized["first_30_minute_action"] == serialized["first_30_min_action"]
    assert serialized["suggested_first_comment"]
    assert serialized["junior_fit_evidence"]
    assert serialized["repository_local_check_hints"] == ["./gradlew test"]
    assert serialized["repository_docs_or_test_hints"] == ["spring-boot docs"]


def test_repository_avoid_label_is_excluded() -> None:
    reset_gate()
    candidate = build_candidate(
        issue_payload(labels=[{"name": "status: ideal-for-contribution"}, {"name": "component: compiler"}]),
        PROFILED_OSS_CONFIG,
    )
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("avoid_label", 0) == 1
    assert collector.OSS_EXCLUDED_CANDIDATE_PREVIEW[0]["reason"] == "avoid_label"


def test_repository_avoid_title_keyword_is_excluded() -> None:
    reset_gate()
    candidate = build_candidate(
        issue_payload(title="Compiler redesign docs for getting started tests"),
        PROFILED_OSS_CONFIG,
    )
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("avoid_keyword", 0) == 1


def test_repository_preferred_contribution_types_are_required() -> None:
    reset_gate()
    candidate = build_candidate(
        issue_payload(
            title="Small enhancement for configuration option",
            body="Small enhancement with a clear configuration option and enough details. " * 2,
            labels=[{"name": "status: ideal-for-contribution"}, {"name": "type: enhancement"}],
        ),
        PROFILED_OSS_CONFIG,
    )
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("unsupported_contribution_type", 0) == 1


def test_pull_request_item_is_excluded() -> None:
    assert_excluded("not_issue", issue_payload(pull_request={"url": "https://api.github.com/pr"}))


def test_assigned_issue_is_excluded() -> None:
    assert_excluded("assigned", issue_payload(assignees=[{"login": "someone"}]))


def test_claim_comment_is_excluded() -> None:
    reset_gate()
    collector.fetch_github_issue_comments = (
        lambda repository, issue_number, token, expected_count=0: [
            {"body": "I am working on this, please assign me.", "user": {"login": "dev"}}
        ]
    )
    candidate = build_candidate(issue_payload(comments=1))
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("claimed_in_comments", 0) == 1


def test_linked_work_unknown_is_excluded() -> None:
    reset_gate()
    collector.fetch_github_linked_work_check = lambda repository, issue_number, token: None
    candidate = build_candidate(issue_payload())
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("linked_work_check_incomplete", 0) == 1


def test_linked_branch_is_excluded() -> None:
    reset_gate()
    collector.fetch_github_linked_work_check = lambda repository, issue_number, token: (
        collector.GitHubLinkedWorkCheck(
            check_status="verified",
            linked_prs_count=0,
            linked_branches_count=1,
            has_linked_work=True,
            source="test",
            timeline_page_complete=True,
        )
    )
    candidate = build_candidate(issue_payload())
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("linked_work_exists", 0) == 1


def test_linked_pr_is_excluded() -> None:
    reset_gate()
    collector.fetch_github_linked_work_check = lambda repository, issue_number, token: (
        collector.GitHubLinkedWorkCheck(
            check_status="verified",
            linked_prs_count=1,
            linked_branches_count=0,
            has_linked_work=True,
            source="test",
            timeline_page_complete=True,
        )
    )
    candidate = build_candidate(issue_payload())
    assert candidate is None
    assert collector.OSS_GATE_EXCLUSION_COUNTS.get("linked_work_exists", 0) == 1


def test_graphql_missing_token_records_diagnostic() -> None:
    reset_gate()
    result = collector.fetch_github_graphql_json("query { viewer { login } }", {}, None, "owner/repo", "test")
    assert result is None
    assert collector.SOURCE_ERRORS[-1]["error_type"] == "github_graphql_token_missing"
    assert collector.stable_source_error_type(collector.SOURCE_ERRORS[-1]) == "unauthorized"


def test_rest_rate_limit_records_diagnostic() -> None:
    reset_gate()
    original_urlopen = collector.urllib.request.urlopen
    headers = Message()
    headers["X-RateLimit-Remaining"] = "0"
    collector.urllib.request.urlopen = lambda request, timeout: (_ for _ in ()).throw(
        urllib.error.HTTPError(
            request.full_url,
            403,
            "rate limit",
            headers,
            io.BytesIO(b"API rate limit exceeded"),
        )
    )
    try:
        result = collector.fetch_github_api_json(
            "https://api.github.com/repos/owner/repo/issues",
            None,
            "owner/repo",
            "issues",
        )
    finally:
        collector.urllib.request.urlopen = original_urlopen
    assert result is None
    assert collector.stable_source_error_type(collector.SOURCE_ERRORS[-1]) == "rate_limit"


def test_rest_repository_access_failure_records_diagnostic() -> None:
    reset_gate()
    original_urlopen = collector.urllib.request.urlopen
    collector.urllib.request.urlopen = lambda request, timeout: (_ for _ in ()).throw(
        urllib.error.HTTPError(
            request.full_url,
            404,
            "not found",
            Message(),
            io.BytesIO(b"Not Found"),
        )
    )
    try:
        result = collector.fetch_github_api_json(
            "https://api.github.com/repos/owner/repo/issues",
            None,
            "owner/repo",
            "issues",
        )
    finally:
        collector.urllib.request.urlopen = original_urlopen
    assert result is None
    assert collector.stable_source_error_type(collector.SOURCE_ERRORS[-1]) == "repository_fetch_failed"


def test_source_error_type_counts_are_stable() -> None:
    reset_gate()
    collector.record_source_error(
        "GitHub owner/repo",
        "GitHub API request failed for issue search docs (403): API rate limit exceeded",
        category=collector.OSS_CATEGORY_ID,
        source_type="github_search",
        error_type="github_rate_limit",
    )
    assert collector.oss_source_error_type_counts() == {"rate_limit": 1}


def test_profile_search_queries_drive_collection() -> None:
    reset_gate()
    collected_queries: list[str] = []
    original_fetch = collector.fetch_github_search_issues

    def fake_fetch(repository: str, query: str, token: str | None, search_name: str):
        del token, search_name
        collected_queries.append(collector.github_repository_search_query(repository, query))
        return [issue_payload()]

    try:
        collector.fetch_github_search_issues = fake_fetch
        profile = PROFILED_OSS_CONFIG["repository_profiles"][0]
        issue_sources, diagnostics = collector.collect_profile_github_issues(
            "spring-projects/spring-boot",
            profile,
            "token",
            CURRENT_TIME,
        )
    finally:
        collector.fetch_github_search_issues = original_fetch
    assert len(issue_sources) == 1
    assert "repo:spring-projects/spring-boot" in collected_queries[0]
    assert issue_sources[0][1].startswith("profile_query:docs")
    assert diagnostics[0]["status"] == "ok"


def test_empty_oss_payload_keeps_diagnostics() -> None:
    reset_gate()
    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp) / "candidates"
        category = {"id": collector.OSS_CATEGORY_ID}
        collector.write_category_output(output_dir, category, CURRENT_TIME, [], "daily-backend")
        payload = json.loads((output_dir / f"{collector.OSS_CATEGORY_ID}.json").read_text(encoding="utf-8"))
    diagnostics = payload["diagnostics"]
    assert diagnostics["safe_items_count"] == 0
    assert diagnostics["source_error_type_counts"] == {}
    assert diagnostics["excluded_candidates_preview"] == []
    assert diagnostics["fallback_when_empty"] == "oss-preparation-routine"


def main() -> int:
    tests = [
        test_safe_maintainer_authored_issue,
        test_safe_maintainer_triaged_issue,
        test_repository_profile_is_reflected_in_candidate_evidence,
        test_repository_avoid_label_is_excluded,
        test_repository_avoid_title_keyword_is_excluded,
        test_repository_preferred_contribution_types_are_required,
        test_pull_request_item_is_excluded,
        test_assigned_issue_is_excluded,
        test_claim_comment_is_excluded,
        test_linked_work_unknown_is_excluded,
        test_linked_branch_is_excluded,
        test_linked_pr_is_excluded,
        test_graphql_missing_token_records_diagnostic,
        test_rest_rate_limit_records_diagnostic,
        test_rest_repository_access_failure_records_diagnostic,
        test_source_error_type_counts_are_stable,
        test_profile_search_queries_drive_collection,
        test_empty_oss_payload_keeps_diagnostics,
    ]
    for test in tests:
        test()
    print("OSS reliability gate tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
