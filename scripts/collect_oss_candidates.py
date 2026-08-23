#!/usr/bin/env python3
"""Collect current Spring OSS contribution recommendations without an LLM."""

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
TIER_A_REPOSITORIES = (
    "spring-projects/spring-security",
    "spring-projects/spring-restdocs",
    "spring-projects/spring-boot",
)
CONTRIBUTION_TYPES = ("docs", "sample", "test", "javadoc", "small-bug")
TYPE_PRIORITY = {name: index for index, name in enumerate(CONTRIBUTION_TYPES)}
MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
CLAIM_PATTERNS = (
    re.compile(r"\b(?:i(?:'d| would)? like to|i want to) (?:work on|take) this\b", re.I),
    re.compile(r"\bi(?:'m| am| will be| can be)? ?working on this\b", re.I),
    re.compile(r"\b(?:please )?assign (?:this (?:issue )?)?to me\b", re.I),
    re.compile(r"(?:^|\s)/assign(?:\s|$)", re.I),
    re.compile(
        r"\b(?:create|open|send|submit) (?:a )?(?:pr|pull request)\b",
        re.I,
    ),
)
DESIGN_WARNING_PATTERNS = (
    re.compile(r"\b(?:design|approach|api shape) (?:is )?(?:tbd|undecided)\b", re.I),
    re.compile(r"\b(?:needs?|requires?) (?:more )?(?:design|discussion)\b", re.I),
    re.compile(r"\b(?:open questions?|we still need to decide)\b", re.I),
    re.compile(r"\bpending design\b", re.I),
)
SCOPE_PATTERN = re.compile(
    r"^(?:#{1,6}\s+)(?:scope|description|problem|task|proposed change|observed behavior)\b"
    r"|\b(?:add|change|clarify|document|fix|improve|remove|update)\b.{0,160}"
    r"\b(?:api|behavior|documentation|example|method|module|test)\b",
    re.I | re.M,
)
ACCEPTANCE_PATTERN = re.compile(
    r"^(?:#{1,6}\s+)(?:acceptance criteria|definition of done|expected (?:behavior|result))\b"
    r"|\b(?:should|must)\b.{0,160}\b(?:build|capture|pass|remain|return|work)\b",
    re.I | re.M,
)
REPRODUCTION_PATTERN = re.compile(
    r"^(?:#{1,6}\s+)(?:reproduction|steps to reproduce|verification|test plan)\b"
    r"|(?:^|\s)\./gradlew(?:\s|$)",
    re.I | re.M,
)
BUILD_COMMAND_PATTERN = re.compile(r"\./gradlew(?: [A-Za-z0-9_.:/-]+)+")
MARKDOWN_ESCAPE_PATTERN = re.compile(r"([\\`*_[\]()<>~|])")


class ConfigurationError(RuntimeError):
    """Raised when the tracked recommendation contract is invalid."""


class ApiError(RuntimeError):
    """Raised when a read-only GitHub response cannot be trusted."""


@dataclass(frozen=True)
class ApiResponse:
    status: int
    headers: dict[str, str]
    body: Any
    received_at: datetime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", type=Path, help="Replay a deterministic API fixture.")
    mode.add_argument(
        "--live-dry-run",
        action="store_true",
        help="Read public GitHub APIs without changing external state.",
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


def require_string(value: object, field: str) -> str:
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


def parse_date(value: object, field: str) -> date:
    try:
        return date.fromisoformat(require_string(value, field))
    except ValueError as exc:
        raise ConfigurationError(f"{field} must use YYYY-MM-DD") from exc


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


def validate_repository_config(repository: dict[str, Any]) -> None:
    expected_keys = {
        "repository",
        "tier",
        "discovery_labels",
        "strong_signal_labels",
        "exclude_labels",
        "contribution_type_by_label",
        "default_contribution_type",
        "contributing_url",
        "build_command",
        "relevance_reason",
        "skill_fit",
        "learning_value",
    }
    name = require_string(repository.get("repository"), "repository")
    if set(repository) != expected_keys or repository.get("tier") != "A":
        raise ConfigurationError(f"{name}: repository contract is incomplete")
    discovery = require_string_list(
        repository.get("discovery_labels"), f"{name}.discovery_labels"
    )
    strong = require_string_list(
        repository.get("strong_signal_labels"), f"{name}.strong_signal_labels"
    )
    excluded = require_string_list(
        repository.get("exclude_labels"), f"{name}.exclude_labels"
    )
    if not set(strong) <= set(discovery):
        raise ConfigurationError(f"{name}: strong signals must be discovery labels")
    if set(discovery) & set(excluded):
        raise ConfigurationError(f"{name}: discovery and exclusion labels overlap")
    mapping = repository.get("contribution_type_by_label")
    if not isinstance(mapping, dict) or not mapping:
        raise ConfigurationError(f"{name}: contribution type mapping is required")
    if not all(
        isinstance(label, str)
        and label
        and contribution_type in CONTRIBUTION_TYPES
        for label, contribution_type in mapping.items()
    ):
        raise ConfigurationError(f"{name}: contribution type mapping is invalid")
    if repository.get("default_contribution_type") not in CONTRIBUTION_TYPES:
        raise ConfigurationError(f"{name}: default contribution type is invalid")
    contributing_url = require_string(
        repository.get("contributing_url"), f"{name}.contributing_url"
    )
    if not contributing_url.startswith(f"https://github.com/{name}/"):
        raise ConfigurationError(f"{name}: contributing URL is invalid")
    build_command = require_string(
        repository.get("build_command"), f"{name}.build_command"
    )
    if BUILD_COMMAND_PATTERN.fullmatch(build_command) is None:
        raise ConfigurationError(f"{name}: build command is unsafe")
    relevance = require_string(
        repository.get("relevance_reason"), f"{name}.relevance_reason"
    )
    if "\n" in relevance:
        raise ConfigurationError(f"{name}: relevance reason must be one line")
    if repository.get("skill_fit") != 30 or repository.get("learning_value") != 10:
        raise ConfigurationError(f"{name}: profile score does not match Tier A")


def load_config(path: Path, as_of: date | None = None) -> dict[str, Any]:
    config = read_object(path)
    if config.get("schema_version") != 4:
        raise ConfigurationError("oss config schema_version must be 4")
    reviewed_at = parse_date(config.get("reviewed_at"), "reviewed_at")
    valid_until = parse_date(config.get("valid_until"), "valid_until")
    reference_date = as_of or datetime.now(timezone.utc).date()
    if reviewed_at > reference_date:
        raise ConfigurationError("OSS config review cannot be in the future")
    if valid_until < reviewed_at or valid_until > reviewed_at + timedelta(days=92):
        raise ConfigurationError("OSS config validity must end within one quarter")
    if reference_date > valid_until:
        raise ConfigurationError("OSS config review is expired")

    profile = config.get("profile")
    if not isinstance(profile, dict) or set(profile) != {
        "strengths",
        "preferred_contribution_types",
    }:
        raise ConfigurationError("profile contract is incomplete")
    require_string_list(profile.get("strengths"), "profile.strengths")
    if tuple(require_string_list(
        profile.get("preferred_contribution_types"),
        "profile.preferred_contribution_types",
    )) != CONTRIBUTION_TYPES:
        raise ConfigurationError("preferred contribution type order is invalid")

    expected_policy = {
        "lookback_days": 180,
        "fresh_days": 90,
        "warm_days": 180,
        "search_per_repository": 10,
        "shortlist_limit": 5,
        "recommendation_limit": 3,
        "request_limit": 21,
    }
    if config.get("policy") != expected_policy:
        raise ConfigurationError(f"policy must equal {expected_policy}")
    expected_scoring = {
        "skill_fit": 30,
        "contribution_signal": 20,
        "scope_clarity": 15,
        "validation": 15,
        "maintainer_activity": 10,
        "learning_value": 10,
    }
    if config.get("scoring") != expected_scoring:
        raise ConfigurationError(f"scoring must equal {expected_scoring}")
    if sum(config["scoring"].values()) != 100:
        raise ConfigurationError("scoring weights must total 100")

    repositories = config.get("repositories")
    if not isinstance(repositories, list):
        raise ConfigurationError("repositories must be a list")
    names = tuple(
        item.get("repository") for item in repositories if isinstance(item, dict)
    )
    if names != TIER_A_REPOSITORIES:
        raise ConfigurationError("repositories must exactly match Tier A order")
    for repository in repositories:
        validate_repository_config(repository)
    return config


def header_value(headers: dict[str, str], name: str) -> str | None:
    lowered = name.lower()
    return next((value for key, value in headers.items() if key.lower() == lowered), None)


def has_next_page(headers: dict[str, str]) -> bool:
    link = header_value(headers, "Link") or ""
    return any(
        segment.strip().endswith('rel="next"') for segment in link.split(",")
    )


class LiveTransport:
    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def get(self, url: str) -> ApiResponse:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "career-feed-oss-recommender/1.0",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                status = response.status
                raw = response.read().decode("utf-8")
                headers = dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            raise ApiError(f"GitHub API returned HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ApiError(f"GitHub API request failed: {exc}") from exc
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ApiError("GitHub API returned invalid JSON") from exc
        return ApiResponse(status, headers, body, self.clock())


class FixtureTransport:
    def __init__(
        self,
        fixture: dict[str, Any],
        clock: Callable[[], datetime],
    ) -> None:
        self.fixture = fixture
        self.clock = clock

    @staticmethod
    def response_key(url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if parts[:1] == ["search"] and parts[1:] == ["issues"]:
            query = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
            match = re.search(r"(?:^|\s)repo:([^\s]+)", query)
            if match is None:
                raise ApiError("Fixture search query has no repository")
            return f"search:{match.group(1)}"
        if len(parts) >= 3 and parts[0] == "repos":
            repository = f"{parts[1]}/{parts[2]}"
            if len(parts) == 3:
                return f"repo:{repository}"
            if len(parts) >= 5 and parts[3] == "issues":
                number = parts[4]
                if len(parts) == 5:
                    return f"detail:{repository}#{number}"
                if len(parts) == 6 and parts[5] in {"comments", "timeline"}:
                    return f"{parts[5]}:{repository}#{number}"
        raise ApiError(f"Fixture has no route for {parsed.path}")

    def get(self, url: str) -> ApiResponse:
        key = self.response_key(url)
        responses = self.fixture.get("responses")
        if not isinstance(responses, dict) or key not in responses:
            raise ApiError(f"Fixture response is missing: {key}")
        entry = responses[key]
        if not isinstance(entry, dict):
            raise ApiError(f"Fixture response is invalid: {key}")
        headers = dict(self.fixture.get("default_headers", {}))
        headers.update(entry.get("headers", {}))
        received_at = parse_timestamp(entry.get("received_at")) or self.clock()
        return ApiResponse(entry.get("status", 200), headers, entry.get("body"), received_at)


class GitHubClient:
    def __init__(self, transport: Any, request_limit: int) -> None:
        self.transport = transport
        self.request_limit = request_limit
        self.request_count = 0
        self.status_counts: Counter[int] = Counter()
        self.rate_limits: dict[str, int] = {}

    def get(self, path: str, query: dict[str, object] | None = None) -> ApiResponse:
        if self.request_count >= self.request_limit:
            raise ApiError("GitHub API request limit would be exceeded")
        url = f"{API_ROOT}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        self.request_count += 1
        response = self.transport.get(url)
        self.status_counts[response.status] += 1
        if response.status != 200:
            raise ApiError(f"GitHub API returned HTTP {response.status}")
        resource = header_value(response.headers, "X-RateLimit-Resource")
        remaining = header_value(response.headers, "X-RateLimit-Remaining")
        if resource not in {"core", "search"} or remaining is None:
            raise ApiError("GitHub API rate-limit evidence is incomplete")
        try:
            parsed_remaining = int(remaining)
        except ValueError as exc:
            raise ApiError("GitHub API rate-limit remaining is invalid") from exc
        if parsed_remaining < 0:
            raise ApiError("GitHub API rate limit is exhausted")
        previous = self.rate_limits.get(resource)
        self.rate_limits[resource] = (
            parsed_remaining if previous is None else min(previous, parsed_remaining)
        )
        return response


def label_names(issue: dict[str, Any]) -> list[str] | None:
    labels = issue.get("labels")
    if not isinstance(labels, list):
        return None
    names: list[str] = []
    for label in labels:
        if not isinstance(label, dict) or not isinstance(label.get("name"), str):
            return None
        names.append(label["name"])
    return names


def assignee_reason(issue: dict[str, Any]) -> str | None:
    assignees = issue.get("assignees")
    if not isinstance(assignees, list):
        return "invalid_assignees"
    assignee = issue.get("assignee")
    if assignee is not None or assignees:
        return "assigned"
    return None


def is_bot(user: object) -> bool:
    return isinstance(user, dict) and (
        user.get("type") == "Bot" or str(user.get("login", "")).endswith("[bot]")
    )


def contribution_type(profile: dict[str, Any], labels: list[str]) -> str:
    mapped = [
        value
        for label, value in profile["contribution_type_by_label"].items()
        if label in labels
    ]
    return min(mapped, key=TYPE_PRIORITY.get) if mapped else profile["default_contribution_type"]


def validate_repository(profile: dict[str, Any], payload: object) -> str | None:
    repository = profile["repository"]
    if not isinstance(payload, dict):
        return "invalid_repository_payload"
    if payload.get("full_name") != repository:
        return "repository_identity_mismatch"
    if payload.get("html_url") != f"https://github.com/{repository}":
        return "repository_url_mismatch"
    if payload.get("archived") is not False:
        return "repository_archived"
    if payload.get("fork") is not False:
        return "repository_is_fork"
    if payload.get("has_issues") is not True:
        return "issues_disabled"
    return None


def validate_search_item(
    profile: dict[str, Any],
    item: object,
    now: datetime,
    cutoff: datetime,
) -> tuple[dict[str, Any] | None, str | None]:
    repository = profile["repository"]
    if not isinstance(item, dict):
        return None, "invalid_search_item"
    number = item.get("number")
    if type(number) is not int or number <= 0:
        return None, "invalid_issue_number"
    expected_url = f"https://github.com/{repository}/issues/{number}"
    if item.get("html_url") != expected_url:
        return None, "issue_url_mismatch"
    if item.get("repository_url") != f"{API_ROOT}/repos/{repository}":
        return None, "repository_url_mismatch"
    if item.get("state") != "open" or "pull_request" in item:
        return None, "not_open_issue"
    if item.get("locked") is not False:
        return None, "locked"
    assignment = assignee_reason(item)
    if assignment:
        return None, assignment
    labels = label_names(item)
    if labels is None:
        return None, "invalid_labels"
    if not set(labels) & set(profile["discovery_labels"]):
        return None, "missing_discovery_signal"
    excluded = sorted(set(labels) & set(profile["exclude_labels"]))
    if excluded:
        return None, f"excluded_label:{excluded[0]}"
    created_at = parse_timestamp(item.get("created_at"))
    updated_at = parse_timestamp(item.get("updated_at"))
    if (
        created_at is None
        or updated_at is None
        or created_at > updated_at
        or updated_at > now
        or updated_at < cutoff
    ):
        return None, "invalid_issue_timestamp"
    result = dict(item)
    result["_profile"] = profile
    result["_created_at"] = created_at
    result["_updated_at"] = updated_at
    return result, None


def round_robin(queues: list[list[dict[str, Any]]], limit: int) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    maximum = max((len(queue) for queue in queues), default=0)
    for depth in range(maximum):
        for queue in queues:
            if depth < len(queue):
                result.append(queue[depth])
                if len(result) == limit:
                    return result
    return result


def contains_linked_pull_request(timeline: list[dict[str, Any]]) -> bool:
    for event in timeline:
        if event.get("event") not in {"connected", "cross-referenced"}:
            continue
        source = event.get("source")
        if not isinstance(source, dict):
            continue
        issue = source.get("issue")
        if isinstance(issue, dict) and (
            "pull_request" in issue or "/pull/" in str(issue.get("html_url", ""))
        ):
            return True
    return False


def claims_work(comment: dict[str, Any]) -> bool:
    body = comment.get("body")
    return (
        isinstance(body, str)
        and not is_bot(comment.get("user"))
        and any(pattern.search(body) for pattern in CLAIM_PATTERNS)
    )


def maintainer_activity(
    detail: dict[str, Any], comments: list[dict[str, Any]]
) -> datetime | None:
    timestamps: list[datetime] = []
    if detail.get("author_association") in MAINTAINER_ASSOCIATIONS and not is_bot(
        detail.get("user")
    ):
        created_at = parse_timestamp(detail.get("created_at"))
        if created_at:
            timestamps.append(created_at)
    for comment in comments:
        if comment.get("author_association") not in MAINTAINER_ASSOCIATIONS or is_bot(
            comment.get("user")
        ):
            continue
        timestamp = parse_timestamp(comment.get("updated_at")) or parse_timestamp(
            comment.get("created_at")
        )
        if timestamp:
            timestamps.append(timestamp)
    return max(timestamps, default=None)


def score_candidate(
    profile: dict[str, Any],
    labels: list[str],
    evidence: dict[str, bool],
    activity_age: timedelta | None,
) -> tuple[int, dict[str, int]]:
    signal = 20 if set(labels) & set(profile["strong_signal_labels"]) else 12
    scope = 15 if evidence["scope_defined"] else 7 if evidence["body_substantive"] else 0
    validation = 15 if evidence["reproduction_present"] else 10
    if activity_age is None or activity_age < timedelta(0):
        activity = 0
    elif activity_age <= timedelta(days=90):
        activity = 10
    elif activity_age <= timedelta(days=180):
        activity = 5
    else:
        activity = 0
    breakdown = {
        "skill_fit": profile["skill_fit"],
        "contribution_signal": signal,
        "scope_clarity": scope,
        "validation": validation,
        "maintainer_activity": activity,
        "learning_value": profile["learning_value"],
    }
    return sum(breakdown.values()), breakdown


def evaluate_candidate(
    profile: dict[str, Any],
    expected: dict[str, Any],
    detail: object,
    comments: object,
    timeline: object,
    now: datetime,
    checked_at: datetime,
) -> dict[str, Any]:
    repository = profile["repository"]
    number = expected["number"]
    hard_reasons: list[str] = []
    manual_reasons: list[str] = []
    risks: list[str] = []
    if not isinstance(detail, dict):
        detail = {}
        hard_reasons.append("invalid_issue_detail")
    if not isinstance(comments, list) or not all(isinstance(item, dict) for item in comments):
        comments = []
        hard_reasons.append("invalid_comments")
    if not isinstance(timeline, list) or not all(isinstance(item, dict) for item in timeline):
        timeline = []
        hard_reasons.append("invalid_timeline")

    if detail.get("number") != number:
        hard_reasons.append("issue_number_mismatch")
    if detail.get("html_url") != f"https://github.com/{repository}/issues/{number}":
        hard_reasons.append("issue_url_mismatch")
    if detail.get("repository_url") != f"{API_ROOT}/repos/{repository}":
        hard_reasons.append("repository_url_mismatch")
    if detail.get("state") != "open" or "pull_request" in detail:
        hard_reasons.append("not_open_issue")
    if detail.get("locked") is not False:
        hard_reasons.append("locked")
    assignment = assignee_reason(detail)
    if assignment:
        hard_reasons.append(assignment)
    labels = label_names(detail)
    if labels is None:
        labels = []
        hard_reasons.append("invalid_labels")
    if not set(labels) & set(profile["discovery_labels"]):
        hard_reasons.append("missing_discovery_signal")
    excluded = sorted(set(labels) & set(profile["exclude_labels"]))
    hard_reasons.extend(f"excluded_label:{label}" for label in excluded)

    created_at = parse_timestamp(detail.get("created_at"))
    updated_at = parse_timestamp(detail.get("updated_at"))
    if (
        created_at != expected["_created_at"]
        or updated_at is None
        or updated_at > now
        or updated_at < now - timedelta(days=180)
    ):
        hard_reasons.append("invalid_issue_timestamp")
    if contains_linked_pull_request(timeline):
        hard_reasons.append("linked_pull_request")

    external_comments = [
        comment
        for comment in comments
        if comment.get("author_association") not in MAINTAINER_ASSOCIATIONS
        and not is_bot(comment.get("user"))
    ]
    if any(claims_work(comment) for comment in external_comments):
        hard_reasons.append("work_already_claimed")
    elif external_comments:
        manual_reasons.append("external_comments_require_review")

    raw_body = detail.get("body") if isinstance(detail.get("body"), str) else ""
    body = re.sub(r"<!--.*?-->", "", raw_body, flags=re.S).strip()
    substantive = len(re.sub(r"[\W_]+", "", body)) >= 80
    design_warning = any(pattern.search(body) for pattern in DESIGN_WARNING_PATTERNS)
    evidence = {
        "body_substantive": substantive,
        "scope_defined": substantive and bool(SCOPE_PATTERN.search(body)),
        "acceptance_criteria_present": bool(ACCEPTANCE_PATTERN.search(body)),
        "reproduction_present": bool(REPRODUCTION_PATTERN.search(body)),
    }
    if design_warning:
        manual_reasons.append("design_not_decided")
    if not evidence["scope_defined"]:
        manual_reasons.append("scope_not_clear")
    if not evidence["acceptance_criteria_present"]:
        risks.append("완료 조건을 이슈와 관련 테스트에서 다시 확인해야 합니다.")
    if not evidence["reproduction_present"]:
        risks.append("이슈에 재현 명령이 없어 CONTRIBUTING의 테스트 경로부터 확인해야 합니다.")

    activity_at = maintainer_activity(detail, comments)
    activity_age = now - activity_at if activity_at else None
    if activity_at is None or activity_age is None or activity_age > timedelta(days=180):
        manual_reasons.append("maintainer_activity_not_recent")
    elif activity_age > timedelta(days=90):
        risks.append("Maintainer 활동이 90일보다 오래되어 착수 전 확인이 필요합니다.")

    score, breakdown = score_candidate(profile, labels, evidence, activity_age)
    hard_reasons = list(dict.fromkeys(hard_reasons))
    manual_reasons = list(dict.fromkeys(manual_reasons))
    if hard_reasons:
        decision = "EXCLUDED"
    elif manual_reasons:
        decision = "MANUAL_REVIEW"
    elif score >= 75:
        decision = "RECOMMENDED"
    else:
        decision = "KEEP_FOR_LATER"
    candidate_type = contribution_type(profile, labels)
    if not risks:
        risks.append("착수 직전에 assignee, 댓글과 연결 PR을 다시 확인해야 합니다.")
    return {
        "decision": decision,
        "repository": repository,
        "issue_number": number,
        "title": str(detail.get("title", expected.get("title", ""))),
        "url": f"https://github.com/{repository}/issues/{number}",
        "current_status": "open · unassigned · linked PR/선점 댓글 없음"
        if decision in {"RECOMMENDED", "KEEP_FOR_LATER"}
        else "추가 확인 또는 제외 필요",
        "created_at": format_timestamp(created_at),
        "last_updated": format_timestamp(updated_at),
        "checked_at": format_timestamp(checked_at),
        "last_maintainer_activity_at": format_timestamp(activity_at),
        "contribution_type": candidate_type,
        "difficulty": "Easy" if candidate_type in {"docs", "sample", "javadoc"} else "Medium",
        "score": score,
        "score_breakdown": breakdown,
        "why": profile["relevance_reason"],
        "scope": f"{candidate_type} 유형의 한 가지 이슈로 범위를 제한합니다.",
        "validation": profile["build_command"],
        "contributing_url": profile["contributing_url"],
        "risks": risks,
        "first_action": (
            f"CONTRIBUTING 확인 → `{profile['build_command']}` 기준선 실행 → 이슈 재현"
        ),
        "evidence": evidence,
        "exclusion_reasons": hard_reasons,
        "manual_review_reasons": manual_reasons,
    }


def select_recommendations(candidates: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    eligible = sorted(
        (candidate for candidate in candidates if candidate["decision"] == "RECOMMENDED"),
        key=lambda candidate: (
            -candidate["score"],
            TYPE_PRIORITY[candidate["contribution_type"]],
            candidate["repository"],
            candidate["issue_number"],
        ),
    )
    selected: list[dict[str, Any]] = []
    if eligible:
        selected.append(dict(eligible.pop(0), category="Best actionable candidate"))
    safe_index = next(
        (
            index
            for index, candidate in enumerate(eligible)
            if candidate["contribution_type"] in {"docs", "sample", "test", "javadoc"}
        ),
        None,
    )
    if safe_index is not None and len(selected) < limit:
        selected.append(dict(eligible.pop(safe_index), category="Safe docs/test candidate"))
    while eligible and len(selected) < limit:
        selected.append(dict(eligible.pop(0), category="Learning candidate"))
    for rank, candidate in enumerate(selected, 1):
        candidate["rank"] = rank
    return selected


def build_search_query(profile: dict[str, Any], cutoff: datetime) -> str:
    label_expression = ",".join(
        f'"{label}"' for label in profile["discovery_labels"]
    )
    return " ".join(
        (
            f"repo:{profile['repository']}",
            "is:issue",
            "is:open",
            "no:assignee",
            "-linked:pr",
            f"updated:>={cutoff.date().isoformat()}",
            f"label:{label_expression}",
        )
    )


def collect_candidates(
    config: dict[str, Any],
    client: GitHubClient,
    now: datetime,
    mode: str,
) -> dict[str, Any]:
    policy = config["policy"]
    cutoff = now - timedelta(days=policy["lookback_days"])
    errors: list[str] = []
    repositories: list[dict[str, Any]] = []
    queues: list[list[dict[str, Any]]] = []
    precheck_exclusions: list[dict[str, Any]] = []

    for profile in config["repositories"]:
        repository = profile["repository"]
        state = {"repository": repository, "available": False, "search_count": 0}
        repositories.append(state)
        try:
            repo_response = client.get(f"/repos/{repository}")
            reason = validate_repository(profile, repo_response.body)
            if reason:
                raise ApiError(reason)
            query = build_search_query(profile, cutoff)
            search_response = client.get(
                "/search/issues",
                {
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": policy["search_per_repository"],
                },
            )
            payload = search_response.body
            if not isinstance(payload, dict) or payload.get("incomplete_results") is not False:
                raise ApiError("search result is incomplete")
            items = payload.get("items")
            if not isinstance(items, list):
                raise ApiError("search items are invalid")
            queue: list[dict[str, Any]] = []
            for item in items:
                candidate, exclusion = validate_search_item(profile, item, now, cutoff)
                if exclusion:
                    precheck_exclusions.append(
                        {
                            "repository": repository,
                            "issue_number": item.get("number") if isinstance(item, dict) else None,
                            "reason": exclusion,
                        }
                    )
                elif candidate:
                    queue.append(candidate)
            queue.sort(
                key=lambda item: (
                    TYPE_PRIORITY[contribution_type(profile, label_names(item) or [])],
                    -item["_updated_at"].timestamp(),
                    item["number"],
                )
            )
            queues.append(queue)
            state["available"] = True
            state["search_count"] = len(items)
        except ApiError as exc:
            queues.append([])
            errors.append(f"{repository}: {exc}")

    shortlist = round_robin(queues, policy["shortlist_limit"])
    candidates: list[dict[str, Any]] = []
    checked_at: datetime | None = None
    for item in shortlist:
        repository = item["_profile"]["repository"]
        number = item["number"]
        try:
            detail = client.get(f"/repos/{repository}/issues/{number}")
            comments = client.get(
                f"/repos/{repository}/issues/{number}/comments", {"per_page": 100}
            )
            timeline = client.get(
                f"/repos/{repository}/issues/{number}/timeline", {"per_page": 100}
            )
            if has_next_page(comments.headers) or has_next_page(timeline.headers):
                raise ApiError("comments or timeline pagination is incomplete")
            checked_at = max(
                filter(
                    None,
                    (
                        checked_at,
                        detail.received_at,
                        comments.received_at,
                        timeline.received_at,
                    ),
                )
            )
            candidates.append(
                evaluate_candidate(
                    item["_profile"],
                    item,
                    detail.body,
                    comments.body,
                    timeline.body,
                    now,
                    timeline.received_at,
                )
            )
        except ApiError as exc:
            errors.append(f"{repository}#{number}: {exc}")

    complete = not errors
    recommendations = (
        select_recommendations(candidates, policy["recommendation_limit"])
        if complete
        else []
    )
    return {
        "schema_version": 4,
        "mode": mode,
        "generated_at": format_timestamp(now),
        "checked_at": format_timestamp(checked_at),
        "complete": complete,
        "request_count": client.request_count,
        "request_limit": client.request_limit,
        "rate_limits": client.rate_limits,
        "repositories": repositories,
        "precheck_exclusions": precheck_exclusions,
        "shortlist": candidates,
        "recommendations": recommendations,
        "errors": errors,
        "limitations": [
            "Tier A 세 저장소만 확인합니다.",
            "최대 5개를 상세 검증하고 최대 3개를 추천합니다.",
            "외부 저장소를 읽기만 하며 comment, assign, branch, fork, PR을 만들지 않습니다.",
        ],
    }


def escape_markdown(value: object) -> str:
    return MARKDOWN_ESCAPE_PATTERN.sub(r"\\\1", str(value))


def render_markdown(result: dict[str, Any]) -> str:
    recommendations = result["recommendations"]
    checked = ", ".join(item["repository"] for item in result["repositories"])
    best = (
        f"[{recommendations[0]['repository']}#{recommendations[0]['issue_number']}]"
        f"({recommendations[0]['url']})"
        if recommendations
        else "없음"
    )
    lines = [
        "# Daily OSS Contribution",
        "",
        "## Summary",
        "",
        f"- Checked: {checked}",
        f"- Candidates: {len(result['shortlist'])}",
        f"- Best Candidate: {best}",
        f"- Status: {'complete' if result['complete'] else 'incomplete · recommendations blocked'}",
        f"- Checked At: {result['checked_at'] or result['generated_at']}",
        "",
    ]
    for candidate in recommendations:
        lines.extend(
            [
                f"## Recommendation {candidate['rank']}",
                "",
                f"- Category: {candidate['category']}",
                f"- Repository: `{candidate['repository']}`",
                f"- Issue: [{escape_markdown(candidate['title'])}]({candidate['url']})",
                f"- Current Status: {candidate['current_status']}",
                f"- Type: {candidate['contribution_type']}",
                f"- Score: {candidate['score']}/100",
                f"- Last Updated: {candidate['last_updated']}",
                f"- Difficulty: {candidate['difficulty']}",
                "",
                "### Why",
                "",
                candidate["why"],
                "",
                "### Scope",
                "",
                candidate["scope"],
                "",
                "### Validation",
                "",
                f"`{candidate['validation']}`",
                "",
                "### Risk",
                "",
                *[f"- {risk}" for risk in candidate["risks"]],
                "",
                "### First Action",
                "",
                candidate["first_action"],
                "",
            ]
        )
    lines.extend(["## Excluded", "", "| Candidate | Reason |", "| --- | --- |"])
    excluded = [
        candidate for candidate in result["shortlist"] if candidate["decision"] != "RECOMMENDED"
    ]
    if excluded:
        for candidate in excluded:
            reasons = candidate["exclusion_reasons"] + candidate["manual_review_reasons"]
            lines.append(
                f"| `{candidate['repository']}#{candidate['issue_number']}` | "
                f"{escape_markdown(', '.join(reasons) or candidate['decision'])} |"
            )
    else:
        lines.append("| - | 없음 |")
    lines.extend(
        [
            "",
            "## Today",
            "",
            (
                f"실제로 분석할 후보: [{recommendations[0]['repository']}#"
                f"{recommendations[0]['issue_number']}]({recommendations[0]['url']})"
                if recommendations
                else "실제로 분석할 후보: 없음"
            ),
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in result["limitations"]],
            "",
        ]
    )
    if result["errors"]:
        lines.extend(["## Errors", "", *[f"- {escape_markdown(error)}" for error in result["errors"]], ""])
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
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
    parsed = parse_timestamp(value or fixture.get("now"))
    if parsed is None:
        raise ConfigurationError("fixture time must be an ISO-8601 timestamp")
    return parsed


def main() -> int:
    arguments = parse_args()
    try:
        if arguments.fixture:
            fixture = read_object(arguments.fixture)
            now = fixture_now(fixture, arguments.now)
            transport = FixtureTransport(fixture, lambda: now)
            mode = "fixture"
        else:
            now = datetime.now(timezone.utc)
            transport = LiveTransport()
            mode = "live-dry-run"
        config = load_config(arguments.config, now.date())
        client = GitHubClient(transport, config["policy"]["request_limit"])
        result = collect_candidates(config, client, now, mode)
        markdown = render_markdown(result)
        write_atomic(
            arguments.json_output,
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        write_atomic(arguments.markdown_output, markdown)
        if arguments.stdout:
            print(markdown, end="")
        return 0 if result["complete"] else 2
    except (ConfigurationError, ApiError, OSError) as exc:
        print(f"OSS recommendation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
