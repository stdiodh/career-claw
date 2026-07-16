#!/usr/bin/env python3
"""Collect read-only Kotlin/Java/Spring OSS candidates without an LLM."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/oss-repositories.json"
DEFAULT_JSON_OUTPUT = ROOT / "reports/oss-candidates.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "reports/oss-candidates.md"
API_ROOT = "https://api.github.com"
ALLOWED_REPOSITORIES = (
    "spring-projects/spring-boot",
    "spring-projects/spring-framework",
    "detekt/detekt",
    "micrometer-metrics/micrometer",
    "testcontainers/testcontainers-java",
)
MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
EXTERNAL_ASSOCIATIONS = {"NONE", "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR", "CONTRIBUTOR"}
ACTIVITY_EVENTS = {
    "assigned",
    "unassigned",
    "labeled",
    "unlabeled",
    "milestoned",
    "demilestoned",
}
CLAIM_PATTERNS = (
    re.compile(r"\b(?:i(?:'d| would)? like to|i want to) (?:work on|take) this\b", re.I),
    re.compile(r"\bi(?:'m| am| will be| can be)? ?working on this\b", re.I),
    re.compile(r"\b(?:please )?assign (?:this (?:issue )?)?to me\b", re.I),
    re.compile(r"(?:^|\s)/assign(?:\s|$)", re.I),
)
BUILD_COMMAND_PATTERN = re.compile(r"\./gradlew(?: [A-Za-z0-9_.:/-]+)+")
RATE_LIMIT_MAXIMUMS = {"core": 60, "search": 10}


class ConfigurationError(RuntimeError):
    """Raised when the tracked collector contract is invalid."""


class ApiError(RuntimeError):
    """Raised when a read-only GitHub request cannot be trusted."""


@dataclass(frozen=True)
class ApiResponse:
    status: int
    headers: dict[str, str]
    body: Any
    received_at: datetime


@dataclass(frozen=True)
class ExpectedIssue:
    repository: str
    number: int
    created_at: datetime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", type=Path, help="Replay a deterministic API fixture.")
    mode.add_argument(
        "--live-dry-run",
        action="store_true",
        help="Read public GitHub APIs and only write local artifacts.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--now", help="Fixed ISO-8601 UTC time for fixture mode.")
    parser.add_argument("--stdout", action="store_true", help="Print Markdown to stdout.")
    return parser.parse_args()


def read_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Required JSON does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigurationError(f"JSON root must be an object: {path}")
    return payload


def require_non_empty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{field} must be a non-empty string")
    return value


def require_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ConfigurationError(f"{field} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ConfigurationError(f"{field} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise ConfigurationError(f"{field} must not contain duplicates")
    return value


def require_string_mapping(value: object, field: str) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise ConfigurationError(f"{field} must be a non-empty object")
    for key, item in value.items():
        require_non_empty_string(key, f"{field} key")
        require_non_empty_string(item, f"{field}.{key}")
    return value


def parse_config_date(value: object, field: str) -> date:
    raw = require_non_empty_string(value, field)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{field} must use YYYY-MM-DD") from exc


def validate_eligibility_evidence(
    profile: dict[str, Any], repository: str, reviewed_at: date
) -> None:
    evidence = profile.get("eligibility_evidence")
    expected_keys = {
        "repository_url",
        "archived",
        "fork",
        "issues_enabled",
        "default_branch",
        "default_branch_commit_sha",
        "default_branch_commit_url",
        "default_branch_pushed_at",
        "external_merged_pull_request",
        "build_test",
        "jvm_backend_relevant",
    }
    if not isinstance(evidence, dict) or set(evidence) != expected_keys:
        raise ConfigurationError(f"{repository}: eligibility_evidence is incomplete")
    if evidence.get("repository_url") != f"https://github.com/{repository}":
        raise ConfigurationError(f"{repository}: repository_url is invalid")
    if (
        evidence.get("archived") is not False
        or evidence.get("fork") is not False
        or evidence.get("issues_enabled") is not True
        or evidence.get("jvm_backend_relevant") is not True
    ):
        raise ConfigurationError(f"{repository}: allowlist eligibility is not satisfied")
    require_non_empty_string(evidence.get("default_branch"), f"{repository}.default_branch")
    commit_sha = require_non_empty_string(
        evidence.get("default_branch_commit_sha"), f"{repository}.default_branch_commit_sha"
    )
    if re.fullmatch(r"[0-9a-f]{40}", commit_sha) is None or evidence.get(
        "default_branch_commit_url"
    ) != f"https://github.com/{repository}/commit/{commit_sha}":
        raise ConfigurationError(f"{repository}: default branch commit evidence is invalid")

    review_end = datetime(
        reviewed_at.year,
        reviewed_at.month,
        reviewed_at.day,
        tzinfo=timezone.utc,
    ) + timedelta(days=1)
    recent_cutoff = review_end - timedelta(days=90)
    pushed_at = parse_timestamp(evidence.get("default_branch_pushed_at"))
    if pushed_at is None or not recent_cutoff <= pushed_at < review_end:
        raise ConfigurationError(f"{repository}: default branch activity is not within 90 days")

    pull_request = evidence.get("external_merged_pull_request")
    pull_request_keys = {
        "number",
        "url",
        "author_login",
        "author_type",
        "author_association",
        "merged_at",
    }
    if not isinstance(pull_request, dict) or set(pull_request) != pull_request_keys:
        raise ConfigurationError(f"{repository}: external merged PR evidence is incomplete")
    number = pull_request.get("number")
    if type(number) is not int or number <= 0:
        raise ConfigurationError(f"{repository}: external merged PR number is invalid")
    if pull_request.get("url") != f"https://github.com/{repository}/pull/{number}":
        raise ConfigurationError(f"{repository}: external merged PR URL is invalid")
    require_non_empty_string(
        pull_request.get("author_login"), f"{repository}.external_merged_pull_request.author_login"
    )
    if (
        pull_request.get("author_type") != "User"
        or pull_request.get("author_association") not in EXTERNAL_ASSOCIATIONS
    ):
        raise ConfigurationError(f"{repository}: merged PR is not from an external human")
    merged_at = parse_timestamp(pull_request.get("merged_at"))
    if merged_at is None or not recent_cutoff <= merged_at < review_end:
        raise ConfigurationError(f"{repository}: external merged PR is not within 90 days")

    build_test = evidence.get("build_test")
    if not isinstance(build_test, dict) or set(build_test) != {
        "instructions_url",
        "command",
        "proprietary_environment_required",
    }:
        raise ConfigurationError(f"{repository}: build/test evidence is incomplete")
    instructions_url = require_non_empty_string(
        build_test.get("instructions_url"), f"{repository}.build_test.instructions_url"
    )
    command = require_non_empty_string(
        build_test.get("command"), f"{repository}.build_test.command"
    )
    if not instructions_url.startswith("https://") or BUILD_COMMAND_PATTERN.fullmatch(command) is None:
        raise ConfigurationError(f"{repository}: build/test evidence is invalid")
    if build_test.get("proprietary_environment_required") is not False:
        raise ConfigurationError(f"{repository}: proprietary build environment is not allowed")


def load_config(path: Path, as_of: date | None = None) -> dict[str, Any]:
    config = read_object(path)
    if config.get("schema_version") != 2:
        raise ConfigurationError("oss config schema_version must be 2")
    checked_at = parse_config_date(config.get("checked_at"), "checked_at")
    valid_until = parse_config_date(config.get("valid_until"), "valid_until")
    reference_date = as_of or datetime.now(timezone.utc).date()
    if checked_at > reference_date:
        raise ConfigurationError("OSS allowlist review cannot be in the future")
    if valid_until < checked_at or valid_until > checked_at + timedelta(days=92):
        raise ConfigurationError("OSS allowlist validity must end within one quarter")
    if reference_date > valid_until:
        raise ConfigurationError("OSS allowlist review is expired")
    audit = config.get("audit")
    if not isinstance(audit, dict) or set(audit) != {
        "performed_by",
        "performed_by_type",
        "method",
        "human_attested",
    }:
        raise ConfigurationError("OSS allowlist audit provenance is incomplete")
    require_non_empty_string(audit.get("performed_by"), "audit.performed_by")
    require_non_empty_string(audit.get("method"), "audit.method")
    if audit.get("performed_by_type") not in {"AUTOMATED", "HUMAN"}:
        raise ConfigurationError("audit.performed_by_type is invalid")
    if type(audit.get("human_attested")) is not bool:
        raise ConfigurationError("audit.human_attested must be boolean")
    if audit["performed_by_type"] == "AUTOMATED" and audit["human_attested"]:
        raise ConfigurationError("automated allowlist audit cannot claim human attestation")
    excluded = config.get("excluded_repositories")
    if not isinstance(excluded, list) or len(excluded) != 1 or not isinstance(excluded[0], dict):
        raise ConfigurationError("OSS allowlist exclusions must contain the reviewed Security entry")
    exclusion = excluded[0]
    if set(exclusion) != {
        "repository",
        "checked_at",
        "window_start",
        "merged_pull_request_count",
        "external_human_merged_pull_request_count",
        "reason",
        "evidence_url",
    }:
        raise ConfigurationError("OSS allowlist exclusion evidence is incomplete")
    if (
        exclusion.get("repository") != "spring-projects/spring-security"
        or parse_config_date(exclusion.get("checked_at"), "exclusion.checked_at") != checked_at
        or parse_config_date(exclusion.get("window_start"), "exclusion.window_start")
        != checked_at - timedelta(days=90)
        or type(exclusion.get("merged_pull_request_count")) is not int
        or exclusion["merged_pull_request_count"] <= 0
        or exclusion.get("external_human_merged_pull_request_count") != 0
        or exclusion.get("reason") != "no_external_human_merged_pr_within_90_days"
        or not require_non_empty_string(
            exclusion.get("evidence_url"), "exclusion.evidence_url"
        ).startswith("https://github.com/spring-projects/spring-security/pulls?")
    ):
        raise ConfigurationError("Spring Security exclusion evidence is invalid")

    policy = config.get("policy")
    if not isinstance(policy, dict):
        raise ConfigurationError("policy must be an object")
    expected_policy = {
        "lookback_days": 180,
        "fresh_days": 90,
        "warm_days": 180,
        "search_per_repository": 10,
        "preselect_limit": 3,
        "request_limit": 19,
    }
    if policy != expected_policy:
        raise ConfigurationError(f"policy must equal the approved contract: {expected_policy}")

    repositories = config.get("repositories")
    if not isinstance(repositories, list):
        raise ConfigurationError("repositories must be a list")
    names = [profile.get("repository") for profile in repositories if isinstance(profile, dict)]
    if tuple(names) != ALLOWED_REPOSITORIES:
        raise ConfigurationError("repositories must exactly match the five approved allowlist entries")

    for profile in repositories:
        repository = require_non_empty_string(profile.get("repository"), "repository")
        profile_checked_at = parse_config_date(
            profile.get("checked_at"), f"{repository}.checked_at"
        )
        if profile_checked_at != checked_at:
            raise ConfigurationError(f"{repository}.checked_at must match the root review date")
        include = require_string_list(profile.get("include_labels"), f"{repository}.include_labels")
        exclude = require_string_list(profile.get("exclude_labels"), f"{repository}.exclude_labels")
        if set(include) & set(exclude):
            raise ConfigurationError(f"{repository}: include_labels and exclude_labels overlap")
        build_commands = require_string_mapping(
            profile.get("module_label_to_build_command"),
            f"{repository}.module_label_to_build_command",
        )
        for label, command in build_commands.items():
            if BUILD_COMMAND_PATTERN.fullmatch(command) is None:
                raise ConfigurationError(
                    f"{repository}.module_label_to_build_command.{label} is unsafe"
                )
        contribution_types = require_string_mapping(
            profile.get("contribution_type_by_label"),
            f"{repository}.contribution_type_by_label",
        )
        if not set(contribution_types.values()) <= {"code", "test", "docs", "sample"}:
            raise ConfigurationError(f"{repository}: unsupported contribution type")
        default_type = require_non_empty_string(
            profile.get("default_contribution_type"),
            f"{repository}.default_contribution_type",
        )
        if default_type not in {"code", "test", "docs", "sample", "code/test"}:
            raise ConfigurationError(f"{repository}: unsupported default contribution type")
        relevance = require_non_empty_string(
            profile.get("relevance_reason"), f"{repository}.relevance_reason"
        )
        if "\n" in relevance:
            raise ConfigurationError(f"{repository}: relevance_reason must be one line")
        contributing_url = require_non_empty_string(
            profile.get("contributing_url"), f"{repository}.contributing_url"
        )
        if not contributing_url.startswith("https://"):
            raise ConfigurationError(f"{repository}: contributing_url must use HTTPS")
        validate_eligibility_evidence(profile, repository, checked_at)

    planned_requests = len(repositories) * 2 + policy["preselect_limit"] * 3
    if planned_requests != policy["request_limit"]:
        raise ConfigurationError("request_limit must equal the approved maximum request plan")
    return config


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def is_bot(user: object) -> bool:
    if not isinstance(user, dict):
        return False
    login = str(user.get("login", ""))
    return user.get("type") == "Bot" or login.endswith("[bot]")


def valid_timeline_actor(actor: object) -> bool:
    return (
        isinstance(actor, dict)
        and isinstance(actor.get("login"), str)
        and bool(actor["login"].strip())
        and actor.get("type") in {"User", "Bot"}
    )


def valid_assignees(value: object) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, dict)
        and isinstance(item.get("login"), str)
        and bool(item["login"].strip())
        for item in value
    )


def assignee_state(issue: dict[str, Any]) -> str | None:
    if "assignee" not in issue:
        return "invalid_assignees"
    singular = issue.get("assignee")
    assignees = issue.get("assignees")
    if not valid_assignees(assignees):
        return "invalid_assignees"
    if singular is not None and (
        not isinstance(singular, dict)
        or not isinstance(singular.get("login"), str)
        or not singular["login"].strip()
    ):
        return "invalid_assignees"
    if (singular is None) != (not assignees):
        return "invalid_assignees"
    if singular is not None and singular["login"] != assignees[0]["login"]:
        return "invalid_assignees"
    return "assigned" if assignees else None


def header_value(headers: dict[str, str], name: str) -> str:
    lowered = name.lower()
    return next((value for key, value in headers.items() if key.lower() == lowered), "")


def has_next_page(headers: dict[str, str]) -> bool:
    return 'rel="next"' in header_value(headers, "Link")


class HttpTransport:
    def __init__(self, clock: Callable[[], datetime]) -> None:
        self.clock = clock

    def get(self, url: str) -> ApiResponse:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "career-feed-oss-collector",
        }
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
                status = response.status
                response_headers = dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            status = exc.code
            response_headers = dict(exc.headers.items())
        except urllib.error.URLError as exc:
            raise ApiError(f"GitHub GET failed before a response: {type(exc.reason).__name__}") from exc
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ApiError(f"GitHub returned non-JSON data with status {status}") from exc
        return ApiResponse(status, response_headers, body, self.clock())


class FixtureTransport:
    def __init__(self, fixture: dict[str, Any], clock: Callable[[], datetime]) -> None:
        responses = fixture.get("responses")
        if not isinstance(responses, dict):
            raise ConfigurationError("fixture.responses must be an object")
        default_headers = fixture.get("default_headers", {})
        if not isinstance(default_headers, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in default_headers.items()
        ):
            raise ConfigurationError("fixture.default_headers must contain string headers")
        self.responses = responses
        self.default_headers = default_headers
        self.clock = clock

    @staticmethod
    def request_key(url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "api.github.com":
            raise ApiError("fixture request escaped api.github.com")
        if parsed.path == "/search/issues":
            query = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
            match = re.search(r"(?:^|\s)repo:([^\s]+)", query)
            if not match:
                raise ApiError("fixture search request has no repository")
            return f"search:{match.group(1)}"
        label_match = re.fullmatch(r"/repos/([^/]+/[^/]+)/labels", parsed.path)
        if label_match:
            return f"labels:{label_match.group(1)}"
        issue_match = re.fullmatch(
            r"/repos/([^/]+/[^/]+)/issues/(\d+)(?:/(comments|timeline))?", parsed.path
        )
        if issue_match:
            repository, number, suffix = issue_match.groups()
            kind = suffix or "detail"
            return f"{kind}:{repository}#{number}"
        raise ApiError(f"fixture has no endpoint mapping for {parsed.path}")

    def get(self, url: str) -> ApiResponse:
        key = self.request_key(url)
        payload = self.responses.get(key)
        if not isinstance(payload, dict):
            raise ApiError(f"fixture response is missing: {key}")
        status = payload.get("status", 200)
        response_headers = payload.get("headers", {})
        if type(status) is not int or not isinstance(response_headers, dict):
            raise ConfigurationError(f"invalid fixture response: {key}")
        headers = {**self.default_headers, **response_headers}
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in headers.items()):
            raise ConfigurationError(f"invalid fixture headers: {key}")
        return ApiResponse(status, headers, payload.get("body"), self.clock())


class GitHubClient:
    def __init__(self, transport: Any, request_limit: int) -> None:
        self.transport = transport
        self.request_limit = request_limit
        self.request_count = 0
        self.status_counts: Counter[int] = Counter()
        self.rate_limits: dict[str, dict[str, object]] = {}
        self.unexpected_rate_limit_resources: set[str] = set()
        self.rate_limit_header_errors: set[str] = set()

    def get(self, path: str, query: dict[str, object] | None = None) -> ApiResponse:
        if self.request_count >= self.request_limit:
            raise ApiError(f"GitHub request limit exceeded ({self.request_limit})")
        url = f"{API_ROOT}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
        self.request_count += 1
        response = self.transport.get(url)
        self.status_counts.update([response.status])
        self._record_rate_limit(response)
        if response.status != 200:
            resource = header_value(response.headers, "X-RateLimit-Resource") or "unknown"
            raise ApiError(f"GitHub {resource} request returned HTTP {response.status}")
        return response

    def _record_rate_limit(self, response: ApiResponse) -> None:
        resource = header_value(response.headers, "X-RateLimit-Resource")
        remaining = header_value(response.headers, "X-RateLimit-Remaining")
        reset = header_value(response.headers, "X-RateLimit-Reset")
        if not resource or not remaining or not reset:
            self.rate_limit_header_errors.add("incomplete rate-limit headers")
            return
        if resource not in RATE_LIMIT_MAXIMUMS:
            self.unexpected_rate_limit_resources.add(resource)
            return
        try:
            reset_at = datetime.fromtimestamp(int(reset), tz=timezone.utc)
            remaining_count = int(remaining)
        except ValueError:
            self.rate_limit_header_errors.add("invalid rate-limit headers")
            return
        self.rate_limits[resource] = {
            "remaining": remaining_count,
            "reset_at": format_timestamp(reset_at),
        }


def label_names(payload: object) -> list[str]:
    if not isinstance(payload, list):
        raise ApiError("labels response must be a list")
    names: list[str] = []
    for label in payload:
        if not isinstance(label, dict) or not isinstance(label.get("name"), str):
            raise ApiError("labels response contains an invalid label")
        names.append(label["name"])
    return names


def issue_labels(issue: dict[str, Any]) -> list[str] | None:
    labels = issue.get("labels")
    if not isinstance(labels, list):
        return None
    result: list[str] = []
    for label in labels:
        if (
            isinstance(label, dict)
            and isinstance(label.get("name"), str)
            and label["name"].strip()
        ):
            result.append(label["name"])
        elif isinstance(label, str) and label.strip():
            result.append(label)
        else:
            return None
    return result


def expected_issue_url(repository: str, number: int) -> str:
    return f"https://github.com/{repository}/issues/{number}"


def validate_search_issue(
    profile: dict[str, Any], issue: object, cutoff: datetime
) -> tuple[dict[str, Any] | None, str | None]:
    repository = profile["repository"]
    if not isinstance(issue, dict):
        return None, "invalid_search_item"
    number = issue.get("number")
    if type(number) is not int or number <= 0:
        return None, "invalid_issue_number"
    if not isinstance(issue.get("title"), str) or not issue["title"].strip():
        return None, "invalid_title"
    if issue.get("repository_url") != f"{API_ROOT}/repos/{repository}":
        return None, "repository_not_allowlisted"
    if issue.get("html_url") != expected_issue_url(repository, number):
        return None, "issue_url_not_allowlisted"
    if issue.get("state") != "open":
        return None, "closed"
    if "pull_request" in issue:
        return None, "pull_request"
    if type(issue.get("locked")) is not bool:
        return None, "invalid_locked"
    if issue["locked"]:
        return None, "locked"
    assignment = assignee_state(issue)
    if assignment is not None:
        return None, assignment
    labels = issue_labels(issue)
    if labels is None:
        return None, "invalid_labels"
    if not set(labels) & set(profile["include_labels"]):
        return None, "missing_inclusion_label"
    excluded = set(labels) & set(profile["exclude_labels"])
    if excluded:
        return None, f"excluded_label:{sorted(excluded)[0]}"
    created_at = parse_timestamp(issue.get("created_at"))
    updated_at = parse_timestamp(issue.get("updated_at"))
    if created_at is None or updated_at is None:
        return None, "invalid_issue_timestamp"
    observed_at = cutoff + timedelta(days=180)
    if (
        created_at > updated_at
        or created_at > observed_at
        or updated_at > observed_at
    ):
        return None, "invalid_issue_timestamp"
    if updated_at < cutoff:
        return None, "outside_updated_window"
    issue_copy = dict(issue)
    issue_copy["_repository"] = repository
    issue_copy["_profile"] = profile
    issue_copy["_created"] = created_at
    return issue_copy, None


def sort_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            -item["_created"].timestamp(),
            item["_repository"],
            item["number"],
        ),
    )


def comment_claims_work(comment: dict[str, Any]) -> bool:
    if is_bot(comment.get("user")):
        return False
    body = comment.get("body")
    return isinstance(body, str) and any(pattern.search(body) for pattern in CLAIM_PATTERNS)


def is_pull_request_type(value: object) -> bool:
    return (
        isinstance(value, str)
        and re.sub(r"[^a-z]", "", value.casefold()) == "pullrequest"
    )


def contains_pull_request_reference(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if is_pull_request_type(value.get("type")):
        return True
    if any(
        isinstance(key, str)
        and re.sub(r"[^a-z]", "", key.casefold()) == "pullrequest"
        for key in value
    ):
        return True
    return any(
        isinstance(value.get(key), str)
        and "/pull/" in value[key].casefold()
        for key in ("url", "html_url")
    )


def timeline_has_linked_pr(events: list[dict[str, Any]]) -> bool:
    for event in events:
        event_type = event.get("event")
        if not isinstance(event_type, str) or event_type.casefold() not in {
            "cross-referenced",
            "connected",
        }:
            continue
        source = event.get("source")
        source_issue = source.get("issue") if isinstance(source, dict) else None
        if contains_pull_request_reference(source) or contains_pull_request_reference(
            source_issue
        ):
            return True
        subject = event.get("subject")
        if contains_pull_request_reference(subject):
            return True
    return False


def maintainer_activity(
    detail: dict[str, Any],
    comments: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
) -> tuple[datetime | None, bool]:
    activities: list[datetime] = []
    invalid_activity_evidence = False
    if detail.get("author_association") in MAINTAINER_ASSOCIATIONS:
        user = detail.get("user")
        if not valid_timeline_actor(user):
            invalid_activity_evidence = True
        elif not is_bot(user):
            created_at = parse_timestamp(detail.get("created_at"))
            if created_at is None:
                invalid_activity_evidence = True
            else:
                activities.append(created_at)
    for comment in comments:
        if comment.get("author_association") in MAINTAINER_ASSOCIATIONS:
            user = comment.get("user")
            if not valid_timeline_actor(user):
                invalid_activity_evidence = True
            elif not is_bot(user):
                created_at = parse_timestamp(comment.get("created_at"))
                if created_at is None:
                    invalid_activity_evidence = True
                else:
                    activities.append(created_at)
    for event in timeline:
        if event.get("event") in ACTIVITY_EVENTS:
            actor = event.get("actor")
            if not valid_timeline_actor(actor):
                invalid_activity_evidence = True
                continue
            if is_bot(actor):
                continue
            created_at = parse_timestamp(event.get("created_at"))
            if created_at is None:
                invalid_activity_evidence = True
            else:
                activities.append(created_at)
    return (max(activities) if activities else None, invalid_activity_evidence)


def freshness(activity_at: datetime | None, now: datetime) -> tuple[str | None, str | None]:
    if activity_at is None:
        return None, "no_maintainer_activity"
    age = now - activity_at
    if age < timedelta(0):
        return None, "future_maintainer_activity"
    if age <= timedelta(days=90):
        return "FRESH", None
    if age <= timedelta(days=180):
        return "WARM", None
    return None, "maintainer_activity_older_than_180_days"


def contribution_type(profile: dict[str, Any], labels: list[str]) -> str:
    mapping = profile["contribution_type_by_label"]
    return next((mapping[label] for label in mapping if label in labels), profile["default_contribution_type"])


def evaluate_candidate(
    profile: dict[str, Any],
    expected: ExpectedIssue,
    detail: object,
    comments: object,
    timeline: object,
    now: datetime,
    checked_at: datetime,
    comments_paginated: bool = False,
    timeline_paginated: bool = False,
) -> dict[str, Any]:
    repository = profile["repository"]
    hard_failures: list[str] = []
    manual_reasons: list[str] = []
    if not isinstance(detail, dict):
        detail = {}
        hard_failures.append("invalid_issue_detail")
    if not isinstance(comments, list) or not all(isinstance(item, dict) for item in comments):
        comments = []
        hard_failures.append("invalid_comments")
    if not isinstance(timeline, list) or not all(isinstance(item, dict) for item in timeline):
        timeline = []
        hard_failures.append("invalid_timeline")

    if expected.repository != repository:
        hard_failures.append("preselected_repository_mismatch")
    number = detail.get("number")
    if type(number) is not int or number <= 0:
        number = 0
        hard_failures.append("invalid_issue_number")
    elif number != expected.number:
        hard_failures.append("preselected_number_mismatch")
    title = detail.get("title")
    if not isinstance(title, str) or not title.strip():
        title = ""
        hard_failures.append("invalid_title")
    url = detail.get("html_url")
    if url != expected_issue_url(expected.repository, expected.number):
        hard_failures.append("issue_url_not_allowlisted")
    if detail.get("repository_url") != f"{API_ROOT}/repos/{expected.repository}":
        hard_failures.append("repository_not_allowlisted")
    if detail.get("state") != "open":
        hard_failures.append("closed")
    if "pull_request" in detail:
        hard_failures.append("pull_request")
    assignment = assignee_state(detail)
    if assignment is not None:
        hard_failures.append(assignment)
    locked = detail.get("locked")
    if type(locked) is not bool:
        hard_failures.append("invalid_locked")
    elif locked:
        hard_failures.append("locked")

    labels = issue_labels(detail)
    if labels is None:
        labels = []
        hard_failures.append("invalid_labels")
    include_matches = [label for label in profile["include_labels"] if label in labels]
    if not include_matches:
        hard_failures.append("missing_inclusion_label")
    excluded = [label for label in profile["exclude_labels"] if label in labels]
    hard_failures.extend(f"excluded_label:{label}" for label in excluded)
    detail_created_at = parse_timestamp(detail.get("created_at"))
    detail_updated_at = parse_timestamp(detail.get("updated_at"))
    timestamp_invalid = (
        detail_created_at is None
        or detail_updated_at is None
        or detail_created_at > detail_updated_at
        or detail_created_at > now
        or detail_updated_at > now
    )
    if timestamp_invalid:
        hard_failures.append("invalid_issue_timestamp")
        detail_updated_at = None
    elif detail_updated_at < now - timedelta(days=180):
        hard_failures.append("outside_updated_window")
    elif detail_created_at != expected.created_at:
        hard_failures.append("preselected_created_at_mismatch")
    if timeline_has_linked_pr(timeline):
        hard_failures.append("linked_pull_request")

    external_comments = [
        comment
        for comment in comments
        if comment.get("author_association") not in MAINTAINER_ASSOCIATIONS
        and not is_bot(comment.get("user"))
    ]
    if any(comment_claims_work(comment) for comment in external_comments):
        hard_failures.append("claim_comment")
    elif external_comments:
        manual_reasons.append("external_comment_requires_manual_review")
    if comments_paginated:
        manual_reasons.append("comments_pagination_incomplete")
    if timeline_paginated:
        manual_reasons.append("timeline_pagination_incomplete")

    activity_at, invalid_activity = maintainer_activity(detail, comments, timeline)
    if (
        activity_at is not None
        and detail_created_at is not None
        and activity_at < detail_created_at
    ):
        invalid_activity = True
    activity_freshness, activity_failure = freshness(activity_at, now)
    if activity_failure:
        hard_failures.append(activity_failure)
    if invalid_activity:
        manual_reasons.append("invalid_activity_evidence")

    module_mapping = profile["module_label_to_build_command"]
    module_matches = [label for label in module_mapping if label in labels]
    if not module_matches:
        manual_reasons.append("module_mapping_missing")
        module_label = None
        build_command = None
    elif len(module_matches) > 1:
        manual_reasons.append("multiple_module_mappings")
        module_label = None
        build_command = None
    else:
        module_label = module_matches[0]
        build_command = module_mapping[module_label]

    hard_failures = list(dict.fromkeys(hard_failures))
    manual_reasons = list(dict.fromkeys(manual_reasons))
    if hard_failures:
        decision = "EXCLUDED"
    elif manual_reasons:
        decision = "MANUAL_REVIEW"
    else:
        decision = "READY_TO_ASK"
    return {
        "decision": decision,
        "repository": repository,
        "issue_number": expected.number,
        "title": title,
        "url": expected_issue_url(repository, expected.number),
        "created_at": format_timestamp(expected.created_at),
        "updated_at": format_timestamp(detail_updated_at),
        "checked_at": format_timestamp(checked_at),
        "contribution_label": include_matches[0] if include_matches else None,
        "contribution_type": contribution_type(profile, labels),
        "relevance_reason": profile["relevance_reason"],
        "module_label": module_label,
        "build_test_command": build_command,
        "last_maintainer_activity_at": format_timestamp(activity_at),
        "freshness": activity_freshness,
        "exclusion_reasons": hard_failures,
        "manual_review_reasons": manual_reasons,
    }


def error_message(scope: str, exc: Exception) -> str:
    return f"{scope}: {exc}"


def collect_candidates(
    config: dict[str, Any], client: GitHubClient, now: datetime, mode: str
) -> dict[str, Any]:
    policy = config["policy"]
    cutoff = now - timedelta(days=policy["lookback_days"])
    errors: list[str] = []
    warnings: list[str] = []
    repository_results: list[dict[str, Any]] = []
    searchable: list[dict[str, Any]] = []
    precheck_exclusions: list[dict[str, object]] = []

    for profile in config["repositories"]:
        repository = profile["repository"]
        repo_result: dict[str, Any] = {
            "repository": repository,
            "label_contract": "UNKNOWN",
            "missing_labels": [],
            "search_count": 0,
            "eligible_search_count": 0,
            "fail_closed_reason": None,
        }
        repository_results.append(repo_result)
        try:
            labels_response = client.get(
                f"/repos/{repository}/labels", {"per_page": 100}
            )
            live_labels = set(label_names(labels_response.body))
            configured_labels = (
                set(profile["include_labels"])
                | set(profile["exclude_labels"])
                | set(profile["module_label_to_build_command"])
                | set(profile["contribution_type_by_label"])
            )
            missing_labels = sorted(configured_labels - live_labels)
            if missing_labels:
                repo_result["label_contract"] = "FAILED"
                repo_result["missing_labels"] = missing_labels
                if has_next_page(labels_response.headers):
                    repo_result["fail_closed_reason"] = "labels_pagination_incomplete"
                    warnings.append(
                        f"{repository}: configured labels may be on a later labels page"
                    )
                else:
                    repo_result["fail_closed_reason"] = "configured_label_missing"
                    warnings.append(f"{repository}: configured labels are missing")
                continue
            repo_result["label_contract"] = "VERIFIED"
        except (ApiError, ConfigurationError) as exc:
            repo_result["label_contract"] = "FAILED"
            repo_result["fail_closed_reason"] = "labels_request_failed"
            errors.append(error_message(f"{repository} labels", exc))
            continue

        label_expression = ",".join(f'"{label}"' for label in profile["include_labels"])
        search_query = " ".join(
            (
                f"repo:{repository}",
                "is:issue",
                "is:open",
                "archived:false",
                "no:assignee",
                "-linked:pr",
                f"updated:>={cutoff.date().isoformat()}",
                f"label:{label_expression}",
            )
        )
        try:
            search_response = client.get(
                "/search/issues",
                {
                    "q": search_query,
                    "sort": "created",
                    "order": "desc",
                    "per_page": policy["search_per_repository"],
                },
            )
            body = search_response.body
            if not isinstance(body, dict) or not isinstance(body.get("items"), list):
                raise ApiError("search response must contain an items list")
            if body.get("incomplete_results") is not False:
                raise ApiError("search response is incomplete")
            items = body["items"]
            if len(items) > policy["search_per_repository"]:
                raise ApiError("search response exceeds configured per_page")
            repo_result["search_count"] = len(items)
            for issue in items:
                validated, reason = validate_search_issue(profile, issue, cutoff)
                if validated is None:
                    raw_number = issue.get("number") if isinstance(issue, dict) else None
                    precheck_exclusions.append(
                        {
                            "repository": repository,
                            "issue_number": (
                                raw_number
                                if type(raw_number) is int and raw_number > 0
                                else None
                            ),
                            "reason": reason,
                        }
                    )
                else:
                    searchable.append(validated)
                    repo_result["eligible_search_count"] += 1
        except ApiError as exc:
            repo_result["fail_closed_reason"] = "search_request_failed"
            errors.append(error_message(f"{repository} search", exc))

    unique: dict[tuple[str, int], dict[str, Any]] = {}
    for issue in searchable:
        key = (issue["_repository"], issue["number"])
        if key in unique:
            precheck_exclusions.append(
                {
                    "repository": key[0],
                    "issue_number": key[1],
                    "reason": "duplicate_search_result",
                }
            )
            continue
        unique[key] = issue
    preselected = sort_candidates(list(unique.values()))[: policy["preselect_limit"]]

    candidates: list[dict[str, Any]] = []
    last_detail_checked_at: datetime | None = None
    for issue in preselected:
        repository = issue["_repository"]
        number = issue["number"]
        responses: dict[str, ApiResponse] = {}
        request_failed = False
        candidate_checked_at: datetime | None = None
        for kind, suffix in (("detail", ""), ("comments", "/comments"), ("timeline", "/timeline")):
            try:
                query = {"per_page": 100} if suffix else None
                response = client.get(
                    f"/repos/{repository}/issues/{number}{suffix}", query
                )
                responses[kind] = response
                candidate_checked_at = max(
                    filter(None, (candidate_checked_at, response.received_at))
                )
                last_detail_checked_at = max(
                    filter(None, (last_detail_checked_at, response.received_at))
                )
            except ApiError as exc:
                request_failed = True
                errors.append(error_message(f"{repository}#{number} {kind}", exc))
        if not request_failed:
            valid_detail = isinstance(responses["detail"].body, dict)
            valid_comments = isinstance(responses["comments"].body, list) and all(
                isinstance(item, dict) for item in responses["comments"].body
            )
            valid_timeline = isinstance(responses["timeline"].body, list) and all(
                isinstance(item, dict) for item in responses["timeline"].body
            )
            if not (valid_detail and valid_comments and valid_timeline):
                request_failed = True
                errors.append(f"{repository}#{number}: detailed API payload is invalid")
        if request_failed:
            candidates.append(
                {
                    "decision": "EXCLUDED",
                    "repository": repository,
                    "issue_number": number,
                    "title": str(issue.get("title", "")),
                    "url": str(issue.get("html_url", "")),
                    "created_at": format_timestamp(issue.get("_created")),
                    "updated_at": format_timestamp(parse_timestamp(issue.get("updated_at"))),
                    "checked_at": format_timestamp(candidate_checked_at),
                    "contribution_label": None,
                    "contribution_type": issue["_profile"]["default_contribution_type"],
                    "relevance_reason": issue["_profile"]["relevance_reason"],
                    "module_label": None,
                    "build_test_command": None,
                    "last_maintainer_activity_at": None,
                    "freshness": None,
                    "exclusion_reasons": ["api_validation_incomplete"],
                    "manual_review_reasons": [],
                }
            )
            continue
        candidates.append(
            evaluate_candidate(
                issue["_profile"],
                ExpectedIssue(repository, number, issue["_created"]),
                responses["detail"].body,
                responses["comments"].body,
                responses["timeline"].body,
                now,
                responses["timeline"].received_at,
                comments_paginated=has_next_page(responses["comments"].headers),
                timeline_paginated=has_next_page(responses["timeline"].headers),
            )
        )

    generated_at = client.transport.clock()
    errors.extend(sorted(client.rate_limit_header_errors))
    for resource in sorted(client.unexpected_rate_limit_resources):
        errors.append(f"unexpected rate-limit resource: {resource}")
    for bucket in ("core", "search"):
        if bucket not in client.rate_limits:
            errors.append(f"missing {bucket} rate-limit headers")
            continue
        remaining = client.rate_limits[bucket].get("remaining")
        if (
            type(remaining) is not int
            or not 0 <= remaining <= RATE_LIMIT_MAXIMUMS[bucket]
        ):
            errors.append(f"{bucket} rate-limit remaining exceeds anonymous policy")
        reset_at = parse_timestamp(client.rate_limits[bucket].get("reset_at"))
        if reset_at is None:
            errors.append(f"{bucket} rate-limit reset is invalid")
        elif reset_at < generated_at:
            errors.append(f"{bucket} rate-limit reset passed during collection")
        elif reset_at > generated_at + timedelta(days=7):
            errors.append(f"{bucket} rate-limit reset is after the next weekly run")

    if last_detail_checked_at and generated_at - last_detail_checked_at > timedelta(minutes=15):
        errors.append("candidate detail validation is older than 15 minutes")
    complete = not errors
    ready = [candidate for candidate in candidates if candidate["decision"] == "READY_TO_ASK"]
    if not complete:
        ready = []
    return {
        "schema_version": 1,
        "mode": mode,
        "generated_at": format_timestamp(generated_at),
        "checked_at": format_timestamp(last_detail_checked_at),
        "complete": complete,
        "delivery_allowed": complete,
        "request_count": client.request_count,
        "request_limit": client.request_limit,
        "http_status_counts": {
            str(status): count for status, count in sorted(client.status_counts.items())
        },
        "rate_limits": client.rate_limits,
        "repository_results": repository_results,
        "precheck_exclusions": precheck_exclusions,
        "candidates": candidates,
        "ready_to_ask": ready,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "created_at DESC, repository/number 순으로 고른 최신 3개만 상세 검증합니다.",
            "상세 검증에서 탈락해도 4번째 이후 후보를 backfill하지 않습니다.",
            "issue body와 댓글 전문은 artifact에 저장하지 않습니다.",
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Career Feed - OSS Weekly",
        "",
        f"기준 시각: {result['generated_at']}",
        f"상태: {'완전' if result['complete'] else '불완전 · 전송 차단'}",
        f"GitHub API 요청: {result['request_count']}/{result['request_limit']}",
        f"저장소 fail-closed: {sum(item['label_contract'] == 'FAILED' for item in result['repository_results'])}",
        "",
        "> 이 목록은 바로 착수해도 된다는 승인이 아닙니다. 이슈에서 현재 상태와 기여 의사를 먼저 문의하세요.",
        "",
        "## READY_TO_ASK",
        "",
    ]
    if not result["complete"]:
        lines.append("API 또는 labels 계약 검증이 불완전하여 이번 실행에서는 후보를 노출하지 않습니다.")
    elif not result["ready_to_ask"]:
        lines.append("최신 검색 후보 3개 중 READY_TO_ASK 없음")
    else:
        for candidate in result["ready_to_ask"]:
            safe_title = re.sub(r"([\\`*_[\]()<>~|])", r"\\\1", candidate["title"])
            lines.extend(
                [
                    f"### [{candidate['repository']}#{candidate['issue_number']}]({candidate['url']}) — {safe_title}",
                    f"- 생성일: {candidate['created_at']}",
                    f"- 마지막 수정일: {candidate['updated_at']}",
                    f"- 최종 확인일: {candidate['checked_at']}",
                    f"- 기여 라벨/유형: `{candidate['contribution_label']}` · {candidate['contribution_type']}",
                    f"- 관련 이유: {candidate['relevance_reason']}",
                    f"- 첫 30분 검증: `{candidate['build_test_command']}`",
                    "",
                ]
            )
    lines.extend(
        [
            "## 제한",
            "",
            "- 최신 3개만 상세 검증하며 탈락 시 4번째 후보를 자동 보충하지 않습니다.",
            "- 댓글을 기계적으로 확정할 수 없거나 페이지가 잘리면 MANUAL_REVIEW로 분류합니다.",
            "- 이 수집기는 issue를 조회만 하며 comment, assign, label, branch, fork, PR을 만들지 않습니다.",
            "",
        ]
    )
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def fixture_now(fixture: dict[str, Any], value: str | None) -> datetime:
    raw = value or fixture.get("now")
    parsed = parse_timestamp(raw)
    if parsed is None:
        raise ConfigurationError("fixture mode requires a valid --now or fixture.now timestamp")
    return parsed


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        if args.live_dry_run:
            if args.now:
                raise ConfigurationError("--now is only allowed in fixture mode")
            mode = "live-dry-run"
            clock = lambda: datetime.now(timezone.utc)
            now = clock()
            transport: Any = HttpTransport(clock)
        else:
            fixture = read_object(args.fixture)
            mode = "fixture"
            now = fixture_now(fixture, args.now)
            clock = lambda: now
            transport = FixtureTransport(fixture, clock)
        client = GitHubClient(transport, config["policy"]["request_limit"])
        result = collect_candidates(config, client, now, mode)
        markdown = render_markdown(result)
        write_atomic(
            args.json_output,
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        write_atomic(args.markdown_output, markdown)
        if args.stdout:
            print(markdown, end="")
        return 0 if result["complete"] else 2
    except (ConfigurationError, ApiError, OSError) as exc:
        print(f"OSS collector failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
