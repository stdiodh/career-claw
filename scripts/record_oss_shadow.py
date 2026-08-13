#!/usr/bin/env python3
"""Build and record GitHub Actions OSS Shadow evidence."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

try:
    from . import check_oss_delivery_gate as delivery_gate
    from . import collect_oss_candidates as collector
except ImportError:
    import check_oss_delivery_gate as delivery_gate
    import collect_oss_candidates as collector


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = ROOT / "configs/oss-delivery-gate.json"
DEFAULT_REPOSITORIES = ROOT / "configs/oss-repositories.json"
DEFAULT_ARTIFACT = ROOT / "reports/oss-candidates.json"
DEFAULT_MARKDOWN = ROOT / "reports/oss-candidates.md"
DEFAULT_METADATA = ROOT / "reports/oss-run-metadata.json"
METADATA_KEYS = {
    "schema_version",
    "recorded_at",
    "shadow_contract_sha256",
    "collector_exit_code",
    "discord_delivery_count",
    "artifact_sha256",
    "markdown_sha256",
    "provenance",
}
ARTIFACT_KEYS = {
    "schema_version",
    "mode",
    "generated_at",
    "checked_at",
    "complete",
    "delivery_allowed",
    "request_count",
    "request_limit",
    "http_status_counts",
    "rate_limits",
    "repository_results",
    "precheck_exclusions",
    "candidates",
    "ready_to_ask",
    "errors",
    "warnings",
    "limitations",
}
REPOSITORY_RESULT_KEYS = {
    "repository",
    "label_contract",
    "missing_labels",
    "search_count",
    "eligible_search_count",
    "fail_closed_reason",
}
PRECHECK_EXCLUSION_KEYS = {"repository", "issue_number", "reason"}
CANDIDATE_KEYS = {
    "decision",
    "repository",
    "issue_number",
    "title",
    "url",
    "created_at",
    "updated_at",
    "checked_at",
    "contribution_label",
    "contribution_type",
    "relevance_reason",
    "module_label",
    "build_test_command",
    "last_maintainer_activity_at",
    "freshness",
    "feasibility_evidence",
    "exclusion_reasons",
    "manual_review_reasons",
}
FEASIBILITY_EVIDENCE_KEYS = {
    "scope_defined",
    "acceptance_criteria_present",
    "reproduction_steps_present",
    "current_review_required",
}
EXPECTED_LIMITATIONS = [
    "created_at DESC, repository/number 순으로 고른 최신 3개만 상세 검증합니다.",
    "상세 검증에서 탈락해도 4번째 이후 후보를 backfill하지 않습니다.",
    "issue body와 댓글 전문은 artifact에 저장하지 않습니다.",
]
REPOSITORY_FAILURE_REASONS = {
    "configured_label_missing",
    "labels_pagination_incomplete",
    "labels_request_failed",
    "search_request_failed",
}
PRECHECK_REASONS = {
    "assigned",
    "closed",
    "duplicate_search_result",
    "invalid_assignees",
    "invalid_issue_number",
    "invalid_issue_timestamp",
    "invalid_labels",
    "invalid_locked",
    "invalid_search_item",
    "invalid_title",
    "issue_url_not_allowlisted",
    "locked",
    "missing_inclusion_label",
    "outside_updated_window",
    "pull_request",
    "repository_not_allowlisted",
}
EXPECTED_POLICY = {
    "lookback_days": 180,
    "fresh_days": 90,
    "warm_days": 180,
    "search_per_repository": 10,
    "preselect_limit": 3,
    "request_limit": 19,
}


class EvidenceError(RuntimeError):
    """Raised when workflow metadata or an artifact cannot be trusted."""


def yes_no(value: str) -> bool:
    normalized = value.casefold()
    if normalized == "yes":
        return True
    if normalized == "no":
        return False
    raise argparse.ArgumentTypeError("expected yes or no")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    metadata = subparsers.add_parser(
        "build-metadata", help="Bind actual workflow context, exit code, and output hashes"
    )
    metadata.add_argument("--collector-exit-code", type=int, required=True)
    metadata.add_argument("--discord-sent", type=yes_no, required=True)
    metadata.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    metadata.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    metadata.add_argument("--output", type=Path, default=DEFAULT_METADATA)

    run = subparsers.add_parser(
        "record-run", help="Record one scheduled workflow observation"
    )
    run.add_argument("metadata", type=Path)
    run.add_argument("--artifact", type=Path)
    run.add_argument("--markdown", type=Path)
    run.add_argument("--sort-accurate", type=yes_no, required=True)
    run.add_argument("--freshness-accurate", type=yes_no, required=True)
    run.add_argument("--attested-at")

    review = subparsers.add_parser(
        "record-review", help="Record one manual READY candidate review"
    )
    review.add_argument("candidate_key")
    review.add_argument("--source-run-id", required=True)
    review.add_argument("--reviewed-at")
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", required=True)
    review.add_argument("--relevant", type=yes_no, required=True)
    review.add_argument("--scope-clear", type=yes_no, required=True)
    review.add_argument("--hard-gate-false-positive", type=yes_no, required=True)
    review.add_argument(
        "--false-positive-reason",
        choices=sorted(delivery_gate.FALSE_POSITIVE_REASONS),
    )

    approve = subparsers.add_parser("approve", help="Approve only a satisfied gate")
    approve.add_argument("--approved-at")

    for subparser in (run, review, approve):
        subparser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
        subparser.add_argument("--repositories", type=Path, default=DEFAULT_REPOSITORIES)
    return parser.parse_args()


def utc_timestamp(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise EvidenceError("Current time must be timezone-aware")
    return current.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def sha256_bytes(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def read_json_bytes(path: Path, description: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError(f"{description} does not exist: {path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"{description} is not valid UTF-8 JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise EvidenceError(f"{description} root must be an object")
    return payload, raw


def file_hash_or_none(path: Path) -> str | None:
    try:
        return sha256_bytes(path.read_bytes())
    except FileNotFoundError:
        return None


def repository_contract(
    payload: dict[str, Any],
) -> tuple[set[str], dict[str, dict[str, Any]], dict[str, int]]:
    repositories = delivery_gate.allowed_repositories(payload)
    if payload.get("policy") != EXPECTED_POLICY:
        raise EvidenceError("OSS repository policy does not match the recorder contract")
    entries = payload.get("repositories")
    profiles: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise EvidenceError("OSS repository profile must be an object")
        repository = entry.get("repository")
        include_labels = entry.get("include_labels")
        exclude_labels = entry.get("exclude_labels", [])
        module_commands = entry.get("module_label_to_build_command")
        contribution_types = entry.get("contribution_type_by_label")
        default_type = entry.get("default_contribution_type")
        relevance_reason = entry.get("relevance_reason")
        if (
            repository not in repositories
            or not isinstance(include_labels, list)
            or not include_labels
            or not all(isinstance(label, str) and label for label in include_labels)
            or not isinstance(exclude_labels, list)
            or not all(isinstance(label, str) and label for label in exclude_labels)
            or len(exclude_labels) != len(set(exclude_labels))
            or bool(set(include_labels) & set(exclude_labels))
            or not isinstance(module_commands, dict)
            or not module_commands
            or not all(
                isinstance(label, str)
                and label
                and isinstance(command, str)
                and collector.BUILD_COMMAND_PATTERN.fullmatch(command)
                for label, command in module_commands.items()
            )
            or not isinstance(contribution_types, dict)
            or not all(
                isinstance(label, str)
                and label
                and value in {"code", "test", "docs", "sample"}
                for label, value in contribution_types.items()
            )
            or default_type not in {"code", "test", "docs", "sample", "code/test"}
            or not isinstance(relevance_reason, str)
            or not relevance_reason.strip()
        ):
            raise EvidenceError("OSS repository profile is incompatible with the recorder")
        profiles[repository] = entry
    if set(profiles) != repositories:
        raise EvidenceError("OSS repository profiles do not match the allowlist")
    return repositories, profiles, dict(EXPECTED_POLICY)


def require_bound_repository_contract(
    path: Path, allow_repository_override: bool
) -> None:
    if allow_repository_override:
        return
    try:
        matches = path.read_bytes() == DEFAULT_REPOSITORIES.read_bytes()
    except FileNotFoundError as exc:
        raise EvidenceError(f"OSS repository contract does not exist: {path}") from exc
    if not matches:
        raise EvidenceError(
            "OSS evidence must use the repository config bound into the Shadow contract"
        )


def workflow_provenance(environ: Mapping[str, str]) -> dict[str, Any]:
    if environ.get("GITHUB_ACTIONS") != "true":
        raise EvidenceError("Workflow metadata can only be built inside GitHub Actions")
    run_id = environ.get("GITHUB_RUN_ID", "")
    attempt = environ.get("GITHUB_RUN_ATTEMPT", "")
    if not run_id.isdigit() or int(run_id) <= 0 or not attempt.isdigit() or int(attempt) <= 0:
        raise EvidenceError("GitHub Actions run identity is invalid")
    provenance = {
        "repository": environ.get("GITHUB_REPOSITORY"),
        "workflow_ref": environ.get("GITHUB_WORKFLOW_REF"),
        "workflow_sha": environ.get("GITHUB_WORKFLOW_SHA"),
        "event_name": environ.get("GITHUB_EVENT_NAME"),
        "github_run_id": run_id,
        "run_attempt": int(attempt),
        "head_sha": environ.get("GITHUB_SHA"),
        "ref": environ.get("GITHUB_REF"),
        "runner_environment": environ.get("RUNNER_ENVIRONMENT"),
        "runner_os": environ.get("RUNNER_OS"),
    }
    if not all(value is not None for value in provenance.values()):
        raise EvidenceError("GitHub Actions provenance environment is incomplete")
    return provenance


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = (path.stat().st_mode & 0o777) if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_metadata(
    collector_exit_code: int,
    discord_sent: bool,
    artifact_path: Path = DEFAULT_ARTIFACT,
    markdown_path: Path = DEFAULT_MARKDOWN,
    output_path: Path = DEFAULT_METADATA,
    environ: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    if type(collector_exit_code) is not int or not 0 <= collector_exit_code <= 255:
        raise EvidenceError("collector exit code must be between 0 and 255")
    if type(discord_sent) is not bool:
        raise EvidenceError("discord_sent must be boolean")
    artifact_hash = file_hash_or_none(artifact_path)
    markdown_hash = file_hash_or_none(markdown_path)
    if collector_exit_code in {0, 2} and (
        artifact_hash is None or markdown_hash is None
    ):
        raise EvidenceError("Collector exit 0 or 2 requires JSON and Markdown artifacts")
    payload = {
        "schema_version": 1,
        "recorded_at": utc_timestamp(now),
        "shadow_contract_sha256": delivery_gate.CURRENT_SHADOW_CONTRACT,
        "collector_exit_code": collector_exit_code,
        "discord_delivery_count": int(discord_sent),
        "artifact_sha256": artifact_hash,
        "markdown_sha256": markdown_hash,
        "provenance": workflow_provenance(os.environ if environ is None else environ),
    }
    write_json_atomic(output_path, payload)
    return payload


def validate_metadata(
    metadata_path: Path,
    artifact_path: Path | None,
    markdown_path: Path | None,
) -> tuple[dict[str, Any], str, bytes | None, bytes | None]:
    metadata, metadata_raw = read_json_bytes(metadata_path, "OSS run metadata")
    if set(metadata) != METADATA_KEYS or metadata.get("schema_version") != 1:
        raise EvidenceError("OSS run metadata does not match schema 1")
    if metadata.get("shadow_contract_sha256") != delivery_gate.CURRENT_SHADOW_CONTRACT:
        raise EvidenceError("OSS run metadata uses a stale Shadow contract")
    delivery_gate.parse_utc(metadata.get("recorded_at"), "recorded_at")
    provenance = metadata.get("provenance")
    delivery_gate.validate_provenance(provenance, 0)
    exit_code = metadata.get("collector_exit_code")
    delivery_count = metadata.get("discord_delivery_count")
    if type(exit_code) is not int or not 0 <= exit_code <= 255:
        raise EvidenceError("OSS run metadata collector exit code is invalid")
    if type(delivery_count) is not int or delivery_count not in {0, 1}:
        raise EvidenceError("OSS run metadata Discord delivery count is invalid")

    artifact_raw = artifact_path.read_bytes() if artifact_path is not None else None
    markdown_raw = markdown_path.read_bytes() if markdown_path is not None else None
    expected_artifact_hash = metadata.get("artifact_sha256")
    expected_markdown_hash = metadata.get("markdown_sha256")
    if (artifact_raw is None) != (expected_artifact_hash is None):
        raise EvidenceError("Artifact presence does not match workflow metadata")
    if (markdown_raw is None) != (expected_markdown_hash is None):
        raise EvidenceError("Markdown presence does not match workflow metadata")
    if artifact_raw is not None and sha256_bytes(artifact_raw) != expected_artifact_hash:
        raise EvidenceError("Artifact SHA-256 does not match workflow metadata")
    if markdown_raw is not None and sha256_bytes(markdown_raw) != expected_markdown_hash:
        raise EvidenceError("Markdown SHA-256 does not match workflow metadata")
    if exit_code in {0, 2} and (artifact_raw is None or markdown_raw is None):
        raise EvidenceError("Collector exit 0 or 2 must preserve both artifacts")
    return metadata, sha256_bytes(metadata_raw), artifact_raw, markdown_raw


def validate_status_counts(
    value: object, request_count: int, complete: bool
) -> tuple[int, int]:
    if not isinstance(value, dict):
        raise EvidenceError("OSS artifact needs HTTP status counts")
    total = 0
    parsed: dict[int, int] = {}
    for status, count in value.items():
        if (
            not isinstance(status, str)
            or re.fullmatch(r"[1-5][0-9]{2}", status) is None
            or type(count) is not int
            or count < 0
        ):
            raise EvidenceError("OSS artifact HTTP status counts are invalid")
        parsed[int(status)] = count
        total += count
    if total > request_count or (complete and total != request_count):
        raise EvidenceError("OSS artifact HTTP status counts do not match request_count")
    if complete and parsed != {200: request_count}:
        raise EvidenceError("Complete OSS artifacts require exact HTTP 200 counts")
    return parsed.get(403, 0), parsed.get(429, 0)


def candidate_identity(candidate: object, repositories: set[str]) -> str:
    if not isinstance(candidate, dict) or set(candidate) != CANDIDATE_KEYS:
        raise EvidenceError("Every OSS artifact candidate must be an object")
    repository = candidate.get("repository")
    number = candidate.get("issue_number")
    if (
        repository not in repositories
        or type(number) is not int
        or number <= 0
        or candidate.get("url") != f"https://github.com/{repository}/issues/{number}"
    ):
        raise EvidenceError("OSS artifact candidate identity is invalid")
    return f"{repository}#{number}"


def validate_artifact(
    raw: bytes,
    repositories: set[str],
    profiles: dict[str, dict[str, Any]],
    policy: dict[str, int],
    metadata_exit_code: int,
) -> dict[str, Any]:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("OSS artifact is not valid UTF-8 JSON") from exc
    if not isinstance(payload, dict) or set(payload) != ARTIFACT_KEYS:
        raise EvidenceError("OSS artifact does not match the exact collector schema")
    if payload.get("schema_version") != 2 or payload.get("mode") != "live-dry-run":
        raise EvidenceError("Only schema 2 live-dry-run artifacts can be recorded")

    generated_at = delivery_gate.parse_utc(payload.get("generated_at"), "generated_at")
    complete = payload.get("complete")
    delivery_allowed = payload.get("delivery_allowed")
    errors = payload.get("errors")
    warnings = payload.get("warnings")
    if (
        type(complete) is not bool
        or type(delivery_allowed) is not bool
        or not isinstance(errors, list)
        or not all(isinstance(value, str) and value.strip() for value in errors)
        or not isinstance(warnings, list)
        or not all(isinstance(value, str) and value.strip() for value in warnings)
        or len(errors) != len(set(errors))
        or len(warnings) != len(set(warnings))
        or complete != (not errors)
        or delivery_allowed != complete
    ):
        raise EvidenceError("OSS artifact completion and error fields are contradictory")
    if (complete and metadata_exit_code != 0) or (
        not complete and metadata_exit_code == 0
    ):
        raise EvidenceError("Workflow exit code contradicts the collector artifact")

    request_count = payload.get("request_count")
    if (
        payload.get("request_limit") != policy["request_limit"]
        or type(request_count) is not int
        or not len(repositories) <= request_count <= policy["request_limit"]
    ):
        raise EvidenceError("OSS artifact violates the configured request contract")
    http_403_count, http_429_count = validate_status_counts(
        payload.get("http_status_counts"), request_count, complete
    )
    rate_limits = payload.get("rate_limits")
    if complete:
        delivery_gate.validate_rate_limits(rate_limits, generated_at, required=True)
    elif rate_limits is not None and not isinstance(rate_limits, dict):
        raise EvidenceError("OSS artifact rate_limits must be an object")

    repository_results = payload.get("repository_results")
    if not isinstance(repository_results, list) or len(repository_results) != len(repositories):
        raise EvidenceError("OSS artifact needs one result for every allowlisted repository")
    seen_repositories: set[str] = set()
    repository_failures: list[dict[str, str]] = []
    verified_repository_count = 0
    for result in repository_results:
        if (
            not isinstance(result, dict)
            or set(result) != REPOSITORY_RESULT_KEYS
            or result.get("repository") not in repositories
            or result.get("label_contract") not in {"VERIFIED", "FAILED"}
            or not isinstance(result.get("missing_labels"), list)
            or not all(
                isinstance(label, str) and label.strip()
                for label in result["missing_labels"]
            )
            or type(result.get("search_count")) is not int
            or not 0 <= result["search_count"] <= policy["search_per_repository"]
            or type(result.get("eligible_search_count")) is not int
            or not 0 <= result["eligible_search_count"] <= result["search_count"]
        ):
            raise EvidenceError("OSS artifact repository result is invalid")
        repository = result["repository"]
        if repository in seen_repositories:
            raise EvidenceError("OSS artifact repository results contain duplicates")
        seen_repositories.add(repository)
        reason = result.get("fail_closed_reason")
        if reason is not None and reason not in REPOSITORY_FAILURE_REASONS:
            raise EvidenceError("OSS artifact repository failure reason is invalid")
        if result["label_contract"] == "VERIFIED":
            verified_repository_count += 1
            if result["missing_labels"] or reason not in {None, "search_request_failed"}:
                raise EvidenceError("Verified OSS label contract evidence is contradictory")
        elif reason not in {
            "configured_label_missing",
            "labels_pagination_incomplete",
            "labels_request_failed",
        }:
            raise EvidenceError("Failed OSS label contracts need a label failure reason")
        if reason is not None:
            repository_failures.append({"repository": repository, "reason": reason})
    if seen_repositories != repositories:
        raise EvidenceError("OSS artifact repository result set does not match the allowlist")

    precheck_exclusions = payload.get("precheck_exclusions")
    if not isinstance(precheck_exclusions, list):
        raise EvidenceError("OSS artifact precheck_exclusions must be a list")
    invalid_prechecks_by_repository = {repository: 0 for repository in repositories}
    duplicate_prechecks_by_repository = {repository: 0 for repository in repositories}
    for exclusion in precheck_exclusions:
        repository = exclusion.get("repository") if isinstance(exclusion, dict) else None
        reason = exclusion.get("reason") if isinstance(exclusion, dict) else None
        profile = profiles.get(repository, {})
        controlled_reason = reason in PRECHECK_REASONS or (
            isinstance(reason, str)
            and reason.startswith("excluded_label:")
            and reason.removeprefix("excluded_label:") in profile.get("exclude_labels", [])
        )
        if (
            not isinstance(exclusion, dict)
            or set(exclusion) != PRECHECK_EXCLUSION_KEYS
            or repository not in repositories
            or (
                exclusion.get("issue_number") is not None
                and (
                    type(exclusion["issue_number"]) is not int
                    or exclusion["issue_number"] <= 0
                )
            )
            or not controlled_reason
        ):
            raise EvidenceError("OSS artifact precheck exclusion is invalid")
        if reason == "duplicate_search_result":
            if exclusion["issue_number"] is None:
                raise EvidenceError("Duplicate OSS search evidence needs an issue number")
            duplicate_prechecks_by_repository[repository] += 1
        else:
            if (
                reason in {"invalid_search_item", "invalid_issue_number"}
                and exclusion["issue_number"] is not None
            ) or (
                reason not in {"invalid_search_item", "invalid_issue_number"}
                and exclusion["issue_number"] is None
            ):
                raise EvidenceError("OSS precheck reason contradicts its issue number")
            invalid_prechecks_by_repository[repository] += 1

    if payload.get("limitations") != EXPECTED_LIMITATIONS:
        raise EvidenceError("OSS artifact limitations do not match the collector contract")

    artifact_checked_at = payload.get("checked_at")
    parsed_artifact_checked_at = (
        None
        if artifact_checked_at is None
        else delivery_gate.parse_utc(artifact_checked_at, "checked_at")
    )
    if parsed_artifact_checked_at is not None and (
        parsed_artifact_checked_at > generated_at
    ):
        raise EvidenceError("OSS artifact validation cannot be in the future")
    if (
        parsed_artifact_checked_at is not None
        and generated_at - parsed_artifact_checked_at > timedelta(minutes=15)
        and (
            complete
            or "candidate detail validation is older than 15 minutes" not in errors
        )
    ):
        raise EvidenceError("OSS artifact validation must be at most 15 minutes old")

    candidates = payload.get("candidates")
    ready = payload.get("ready_to_ask")
    if not isinstance(candidates, list) or len(candidates) > 3 or not isinstance(ready, list):
        raise EvidenceError("OSS artifact candidate collections are invalid")
    expected_request_count = (
        len(repositories) + verified_repository_count + 3 * len(candidates)
    )
    if request_count != expected_request_count:
        raise EvidenceError("OSS artifact request_count contradicts repository and candidate work")
    candidate_keys: list[str] = []
    candidate_counts_by_repository = {repository: 0 for repository in repositories}
    candidate_checked_times: list[datetime] = []
    created_order: list[tuple[float, str, int]] = []
    expected_ready: list[dict[str, Any]] = []
    for candidate in candidates:
        key = candidate_identity(candidate, repositories)
        if key in candidate_keys:
            raise EvidenceError("OSS artifact candidates contain duplicates")
        candidate_keys.append(key)
        candidate_repository = candidate["repository"]
        candidate_counts_by_repository[candidate_repository] += 1
        created_at = delivery_gate.parse_utc(candidate.get("created_at"), f"{key}.created_at")
        if created_at > generated_at:
            raise EvidenceError("OSS candidate creation time cannot be in the future")
        checked_value = candidate.get("checked_at")
        checked_at = (
            None
            if checked_value is None
            else delivery_gate.parse_utc(checked_value, f"{key}.checked_at")
        )
        if complete and checked_at is None:
            raise EvidenceError("Complete OSS candidates need a validation timestamp")
        if checked_at is not None:
            candidate_checked_times.append(checked_at)
            if parsed_artifact_checked_at is None or checked_at > parsed_artifact_checked_at:
                raise EvidenceError("OSS candidate validation exceeds the artifact snapshot")
        if checked_at is not None and (
            checked_at > generated_at
        ):
            raise EvidenceError("OSS candidate validation cannot be in the future")
        if (
            checked_at is not None
            and generated_at - checked_at > timedelta(minutes=15)
            and (
                complete
                or "candidate detail validation is older than 15 minutes" not in errors
            )
        ):
            raise EvidenceError("OSS candidate validation must be at most 15 minutes old")
        if (
            not isinstance(candidate.get("title"), str)
            or not isinstance(candidate.get("contribution_type"), str)
            or not isinstance(candidate.get("relevance_reason"), str)
            or not isinstance(candidate.get("exclusion_reasons"), list)
            or not all(
                isinstance(reason, str) and reason.strip()
                for reason in candidate["exclusion_reasons"]
            )
            or not isinstance(candidate.get("manual_review_reasons"), list)
            or not all(
                isinstance(reason, str) and reason.strip()
                for reason in candidate["manual_review_reasons"]
            )
            or len(candidate["exclusion_reasons"])
            != len(set(candidate["exclusion_reasons"]))
            or len(candidate["manual_review_reasons"])
            != len(set(candidate["manual_review_reasons"]))
            or any(
                value is not None and not isinstance(value, str)
                for value in (
                    candidate.get("updated_at"),
                    candidate.get("contribution_label"),
                    candidate.get("module_label"),
                    candidate.get("build_test_command"),
                    candidate.get("last_maintainer_activity_at"),
                    candidate.get("freshness"),
                )
            )
        ):
            raise EvidenceError("OSS artifact candidate fields are invalid")
        repository, number = key.rsplit("#", 1)
        created_order.append((-created_at.timestamp(), repository, int(number)))
        decision = candidate.get("decision")
        if decision not in {"READY_TO_ASK", "MANUAL_REVIEW", "EXCLUDED"}:
            raise EvidenceError("OSS artifact candidate decision is invalid")
        exclusion_reasons = candidate["exclusion_reasons"]
        manual_review_reasons = candidate["manual_review_reasons"]
        feasibility = candidate.get("feasibility_evidence")
        if (
            not isinstance(feasibility, dict)
            or set(feasibility) != FEASIBILITY_EVIDENCE_KEYS
            or not all(type(value) is bool for value in feasibility.values())
        ):
            raise EvidenceError("OSS candidate feasibility evidence is invalid")
        if feasibility["current_review_required"] != (decision != "EXCLUDED"):
            raise EvidenceError("OSS candidate current-review evidence contradicts its decision")
        if (
            (decision == "READY_TO_ASK" and (exclusion_reasons or manual_review_reasons))
            or (decision == "MANUAL_REVIEW" and (exclusion_reasons or not manual_review_reasons))
            or (decision == "EXCLUDED" and not exclusion_reasons)
        ):
            raise EvidenceError("OSS candidate decision contradicts its reason lists")

        profile = profiles[repository]
        title = candidate["title"]
        if not title.strip() and not (
            decision == "EXCLUDED" and "invalid_title" in exclusion_reasons
        ):
            raise EvidenceError("OSS candidate title contradicts its exclusion evidence")
        updated_value = candidate.get("updated_at")
        updated_at = (
            None
            if updated_value is None
            else delivery_gate.parse_utc(updated_value, f"{key}.updated_at")
        )
        if updated_at is None:
            if decision != "EXCLUDED" or "invalid_issue_timestamp" not in exclusion_reasons:
                raise EvidenceError("OSS candidate needs a valid updated_at timestamp")
        elif not created_at <= updated_at <= generated_at:
            raise EvidenceError("OSS candidate updated_at is outside its collection window")
        elif (
            updated_at
            < generated_at - timedelta(days=policy["lookback_days"], minutes=15)
            and not (
                decision == "EXCLUDED"
                and "outside_updated_window" in exclusion_reasons
            )
        ):
            raise EvidenceError("OSS candidate updated_at is outside the frozen lookback")
        if (
            updated_at is not None
            and checked_at is not None
            and updated_at > checked_at + timedelta(minutes=15)
        ):
            raise EvidenceError("OSS candidate updated_at exceeds its response snapshot")

        contribution_label = candidate.get("contribution_label")
        if contribution_label is not None and contribution_label not in profile["include_labels"]:
            raise EvidenceError("OSS candidate contribution label is outside its repository contract")
        allowed_types = {
            profile["default_contribution_type"],
            *profile["contribution_type_by_label"].values(),
        }
        if candidate["contribution_type"] not in allowed_types:
            raise EvidenceError("OSS candidate contribution type is outside its repository contract")
        if candidate["relevance_reason"] != profile["relevance_reason"]:
            raise EvidenceError("OSS candidate relevance reason does not match its repository")

        module_label = candidate.get("module_label")
        build_command = candidate.get("build_test_command")
        module_commands = profile["module_label_to_build_command"]
        if (module_label is None) != (build_command is None) or (
            module_label is not None and module_commands.get(module_label) != build_command
        ):
            raise EvidenceError("OSS candidate module and build command do not match its repository")

        activity_value = candidate.get("last_maintainer_activity_at")
        activity_at = (
            None
            if activity_value is None
            else delivery_gate.parse_utc(activity_value, f"{key}.last_maintainer_activity_at")
        )
        freshness = candidate.get("freshness")
        if freshness not in {None, "FRESH", "WARM"}:
            raise EvidenceError("OSS candidate freshness is outside the frozen policy")
        if activity_at is None and freshness is not None:
            raise EvidenceError("OSS candidate freshness needs maintainer activity")
        if activity_at is not None and activity_at < created_at and not (
            decision != "READY_TO_ASK"
            and "invalid_activity_evidence" in manual_review_reasons
        ):
            raise EvidenceError("OSS maintainer activity predates issue creation")
        if activity_at is not None and activity_at > generated_at and not (
            freshness is None and "future_maintainer_activity" in exclusion_reasons
        ):
            raise EvidenceError("Future maintainer activity needs exclusion evidence")
        if (
            activity_at is not None
            and checked_at is not None
            and activity_at > checked_at + timedelta(minutes=15)
            and not (
                freshness is None
                and decision == "EXCLUDED"
                and "future_maintainer_activity" in exclusion_reasons
            )
        ):
            raise EvidenceError("OSS maintainer activity exceeds its response snapshot")
        if activity_at is not None and activity_at <= generated_at:
            activity_age = generated_at - activity_at
            tolerance = timedelta(minutes=15)
            if freshness == "FRESH" and activity_age > timedelta(days=90) + tolerance:
                raise EvidenceError("OSS candidate FRESH activity is older than 90 days")
            if freshness == "WARM" and not (
                timedelta(days=90) - tolerance
                < activity_age
                <= timedelta(days=180) + tolerance
            ):
                raise EvidenceError("OSS candidate WARM activity is outside 91-180 days")
        if decision == "READY_TO_ASK":
            if (
                contribution_label is None
                or module_label is None
                or activity_at is None
                or freshness not in {"FRESH", "WARM"}
                or not feasibility["scope_defined"]
                or not feasibility["acceptance_criteria_present"]
                or not feasibility["reproduction_steps_present"]
            ):
                raise EvidenceError("READY_TO_ASK candidates need executable scope evidence")
            expected_ready.append(candidate)
    if created_order != sorted(created_order):
        raise EvidenceError("OSS artifact candidates are not sorted by the frozen policy")
    expected_checked_at = max(candidate_checked_times) if candidate_checked_times else None
    if parsed_artifact_checked_at != expected_checked_at:
        raise EvidenceError("OSS artifact checked_at does not match candidate snapshots")
    results_by_repository = {
        result["repository"]: result for result in repository_results
    }
    unique_eligible_total = 0
    for repository, result in results_by_repository.items():
        eligible_count = result["eligible_search_count"]
        unique_eligible_count = (
            eligible_count - duplicate_prechecks_by_repository[repository]
        )
        unique_eligible_total += unique_eligible_count
        if (
            unique_eligible_count < 0
            or candidate_counts_by_repository[repository] > unique_eligible_count
            or eligible_count + invalid_prechecks_by_repository[repository]
            != result["search_count"]
            or duplicate_prechecks_by_repository[repository] > max(0, eligible_count - 1)
        ):
            raise EvidenceError("OSS artifact search evidence contradicts its candidates")
    if len(candidates) != min(policy["preselect_limit"], unique_eligible_total):
        raise EvidenceError("OSS artifact omitted candidates from the frozen preselection")
    if ready != (expected_ready if complete else []):
        raise EvidenceError("OSS artifact ready_to_ask does not match candidate decisions")

    return {
        "run_at": payload["generated_at"],
        "collector_complete": complete,
        "request_count": request_count,
        "rate_limits": rate_limits if isinstance(rate_limits, dict) else None,
        "http_403_count": http_403_count,
        "http_429_count": http_429_count,
        "warnings": list(dict.fromkeys(warnings)),
        "repository_failures": repository_failures,
        "repository_keys": sorted(repositories),
        "candidate_keys": [
            candidate_identity(candidate, repositories) for candidate in ready
        ],
    }


def mutate_gate(
    gate_path: Path,
    repositories_path: Path,
    mutation: Callable[[dict[str, Any]], Any],
    now: datetime | None = None,
) -> tuple[Any, dict[str, int | bool | str]]:
    lock_path = gate_path.with_name(f"{gate_path.name}.lock")
    with lock_path.open("a", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        payload = delivery_gate.read_object(gate_path)
        if payload.get("status") != "LOCKED":
            raise EvidenceError("Relock the OSS delivery gate before changing evidence")
        mutation_result = mutation(payload)
        repositories = delivery_gate.allowed_repositories(
            delivery_gate.read_object(repositories_path)
        )
        result = delivery_gate.evaluate_gate(payload, repositories, now=now)
        write_json_atomic(gate_path, payload)
        return mutation_result, result


def record_run(
    metadata_path: Path,
    artifact_path: Path | None,
    markdown_path: Path | None,
    sort_accurate: bool,
    freshness_accurate: bool,
    gate_path: Path = DEFAULT_GATE,
    repositories_path: Path = DEFAULT_REPOSITORIES,
    attested_at: str | None = None,
    now: datetime | None = None,
    allow_repository_override: bool = False,
) -> dict[str, Any]:
    if type(sort_accurate) is not bool or type(freshness_accurate) is not bool:
        raise EvidenceError("Sort and freshness decisions must be booleans")
    require_bound_repository_contract(repositories_path, allow_repository_override)
    metadata, metadata_hash, artifact_raw, markdown_raw = validate_metadata(
        metadata_path, artifact_path, markdown_path
    )
    repository_payload = delivery_gate.read_object(repositories_path)
    repositories, profiles, policy = repository_contract(repository_payload)
    exit_code = metadata["collector_exit_code"]
    if exit_code in {0, 2}:
        if artifact_raw is None or markdown_raw is None:
            raise EvidenceError("Collector exit 0 or 2 requires both artifacts")
        derived = validate_artifact(
            artifact_raw,
            repositories,
            profiles,
            policy,
            exit_code,
        )
        artifact_payload = json.loads(artifact_raw.decode("utf-8"))
        expected_markdown = collector.render_markdown(artifact_payload).encode("utf-8")
        if markdown_raw != expected_markdown:
            raise EvidenceError("OSS Markdown does not match the deterministic JSON rendering")
    else:
        if artifact_raw is not None:
            try:
                artifact_raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise EvidenceError("Partial OSS JSON must be valid UTF-8") from exc
        if markdown_raw is not None:
            try:
                markdown_text = markdown_raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise EvidenceError("Partial OSS Markdown must be valid UTF-8") from exc
            if not markdown_text.strip():
                raise EvidenceError("Partial OSS Markdown must not be empty")
        derived = {
            "run_at": metadata["recorded_at"],
            "collector_complete": False,
            "request_count": None,
            "rate_limits": None,
            "http_403_count": None,
            "http_429_count": None,
            "warnings": [
                "collector_output_partial"
                if artifact_raw is not None or markdown_raw is not None
                else "collector_artifact_missing"
            ],
            "repository_failures": [],
            "repository_keys": sorted(repositories),
            "candidate_keys": [],
        }
    workflow_recorded_at = delivery_gate.parse_utc(
        metadata["recorded_at"], "recorded_at"
    )
    run_at = delivery_gate.parse_utc(derived["run_at"], "run_at")
    if run_at > workflow_recorded_at or workflow_recorded_at - run_at > timedelta(
        minutes=15
    ):
        raise EvidenceError("Workflow metadata must follow collection within 15 minutes")
    provenance = metadata["provenance"]
    run = {
        "run_id": (
            f"github-{provenance['github_run_id']}-attempt-{provenance['run_attempt']}"
        ),
        "run_at": derived["run_at"],
        "workflow_recorded_at": metadata["recorded_at"],
        "attested_at": attested_at or utc_timestamp(now),
        "metadata_sha256": metadata_hash,
        "artifact_sha256": metadata["artifact_sha256"],
        "markdown_sha256": metadata["markdown_sha256"],
        "shadow_contract_sha256": metadata["shadow_contract_sha256"],
        "provenance": provenance,
        "collector_complete": derived["collector_complete"],
        "collector_exit_code": exit_code,
        "request_count": derived["request_count"],
        "rate_limits": derived["rate_limits"],
        "http_403_count": derived["http_403_count"],
        "http_429_count": derived["http_429_count"],
        "discord_delivery_count": metadata["discord_delivery_count"],
        "sort_accuracy_percent": 100 if sort_accurate else 0,
        "freshness_accuracy_percent": 100 if freshness_accurate else 0,
        "warnings": derived["warnings"],
        "repository_failures": derived["repository_failures"],
        "repository_keys": derived["repository_keys"],
        "candidate_keys": derived["candidate_keys"],
    }

    def append(payload: dict[str, Any]) -> dict[str, Any]:
        runs = payload.get("runs")
        if not isinstance(runs, list):
            raise EvidenceError("OSS delivery gate runs must be a list")
        runs.append(run)
        return run

    recorded, _ = mutate_gate(gate_path, repositories_path, append, now=now)
    return recorded


def record_review(
    candidate_key: str,
    source_run_id: str,
    reviewer: str,
    notes: str,
    relevant: bool,
    scope_clear: bool,
    hard_gate_false_positive: bool,
    false_positive_reason: str | None,
    gate_path: Path = DEFAULT_GATE,
    repositories_path: Path = DEFAULT_REPOSITORIES,
    reviewed_at: str | None = None,
    now: datetime | None = None,
    allow_repository_override: bool = False,
) -> dict[str, Any]:
    require_bound_repository_contract(repositories_path, allow_repository_override)
    evidence = {
        "candidate_key": candidate_key,
        "source_run_id": source_run_id,
        "reviewed_at": reviewed_at or utc_timestamp(now),
        "reviewer": reviewer,
        "notes": notes,
        "relevant": relevant,
        "scope_clear": scope_clear,
        "hard_gate_false_positive": hard_gate_false_positive,
        "false_positive_reason": false_positive_reason,
    }

    def append(payload: dict[str, Any]) -> dict[str, Any]:
        reviews = payload.get("candidate_reviews")
        if not isinstance(reviews, list):
            raise EvidenceError("OSS delivery gate candidate_reviews must be a list")
        reviews.append(evidence)
        return evidence

    recorded, _ = mutate_gate(gate_path, repositories_path, append, now=now)
    return recorded


def approve_gate(
    gate_path: Path = DEFAULT_GATE,
    repositories_path: Path = DEFAULT_REPOSITORIES,
    approved_at: str | None = None,
    now: datetime | None = None,
    allow_repository_override: bool = False,
) -> dict[str, int | bool | str]:
    require_bound_repository_contract(repositories_path, allow_repository_override)
    approval_time = approved_at or utc_timestamp(now)

    def approve(payload: dict[str, Any]) -> None:
        payload["status"] = "APPROVED"
        payload["approved_at"] = approval_time

    _, result = mutate_gate(gate_path, repositories_path, approve, now=now)
    return result


def main() -> int:
    args = parse_args()
    try:
        if args.command == "build-metadata":
            result: object = build_metadata(
                args.collector_exit_code,
                args.discord_sent,
                args.artifact,
                args.markdown,
                args.output,
            )
        elif args.command == "record-run":
            result = record_run(
                args.metadata,
                args.artifact,
                args.markdown,
                args.sort_accurate,
                args.freshness_accurate,
                args.gate,
                args.repositories,
                args.attested_at,
            )
        elif args.command == "record-review":
            result = record_review(
                args.candidate_key,
                args.source_run_id,
                args.reviewer,
                args.notes,
                args.relevant,
                args.scope_clear,
                args.hard_gate_false_positive,
                args.false_positive_reason,
                args.gate,
                args.repositories,
                args.reviewed_at,
            )
        else:
            result = approve_gate(
                args.gate,
                args.repositories,
                args.approved_at,
            )
    except (OSError, RuntimeError) as exc:
        print(f"Failed to handle OSS Shadow evidence: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
