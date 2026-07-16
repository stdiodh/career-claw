#!/usr/bin/env python3
"""Validate tracked OSS Shadow evidence and emit a delivery decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = ROOT / "configs/oss-delivery-gate.json"
DEFAULT_REPOSITORIES = ROOT / "configs/oss-repositories.json"
SHADOW_CONTRACT_PATHS = (
    ROOT / ".github/workflows/oss-weekly.yml",
    ROOT / "configs/oss-repositories.json",
    ROOT / "scripts/collect_oss_candidates.py",
    ROOT / "scripts/check_oss_delivery_gate.py",
    ROOT / "scripts/record_oss_shadow.py",
)
REQUIREMENTS = {
    "minimum_distinct_weeks": 4,
    "minimum_consecutive_qualifying_weeks": 4,
    "minimum_unique_candidates": 10,
    "minimum_relevance_percent": 80,
    "minimum_scope_clarity_percent": 80,
    "maximum_hard_gate_false_positives": 0,
    "maximum_approval_lag_days": 14,
}
SCHEDULED_WORKFLOW = {
    "repository": "stdiodh/career-feed",
    "workflow_ref": (
        "stdiodh/career-feed/.github/workflows/oss-weekly.yml@refs/heads/main"
    ),
    "event_name": "schedule",
    "ref": "refs/heads/main",
    "runner_environment": "github-hosted",
    "runner_os": "Linux",
}
FALSE_POSITIVE_REASONS = {
    "assigned",
    "claim_comment",
    "closed",
    "excluded_label",
    "linked_pull_request",
    "maintainer_activity_stale",
    "not_jvm_backend_relevant",
    "scope_too_large_or_unclear",
}
RATE_LIMIT_MAXIMUMS = {"core": 60, "search": 10}
SHA256_RE = re.compile(r"sha256:[0-9a-f]{64}")
COMMIT_RE = re.compile(r"[0-9a-f]{40}")
CANDIDATE_RE = re.compile(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)")
UTC_TIMESTAMP_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z"
)
GATE_KEYS = {
    "schema_version",
    "status",
    "requirements",
    "scheduled_workflow",
    "shadow_contract_sha256",
    "runs",
    "candidate_reviews",
    "approved_at",
}
PROVENANCE_KEYS = {
    "repository",
    "workflow_ref",
    "workflow_sha",
    "event_name",
    "github_run_id",
    "run_attempt",
    "head_sha",
    "ref",
    "runner_environment",
    "runner_os",
}
RUN_KEYS = {
    "run_id",
    "run_at",
    "workflow_recorded_at",
    "attested_at",
    "metadata_sha256",
    "artifact_sha256",
    "markdown_sha256",
    "shadow_contract_sha256",
    "provenance",
    "collector_complete",
    "collector_exit_code",
    "request_count",
    "rate_limits",
    "http_403_count",
    "http_429_count",
    "discord_delivery_count",
    "sort_accuracy_percent",
    "freshness_accuracy_percent",
    "warnings",
    "repository_failures",
    "repository_keys",
    "candidate_keys",
}
REVIEW_KEYS = {
    "candidate_key",
    "source_run_id",
    "reviewed_at",
    "reviewer",
    "notes",
    "relevant",
    "scope_clear",
    "hard_gate_false_positive",
    "false_positive_reason",
}


class GateError(RuntimeError):
    """Raised when tracked Shadow evidence is malformed or contradictory."""


def calculate_shadow_contract() -> str:
    digest = hashlib.sha256()
    for path in SHADOW_CONTRACT_PATHS:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


CURRENT_SHADOW_CONTRACT = calculate_shadow_contract()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--repositories", type=Path, default=DEFAULT_REPOSITORIES)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--print-shadow-contract", action="store_true")
    return parser.parse_args()


def read_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GateError(f"Required JSON does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GateError(f"JSON root must be an object: {path}")
    return payload


def parse_utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or UTC_TIMESTAMP_RE.fullmatch(value) is None:
        raise GateError(f"{field} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise GateError(f"{field} must be an aware UTC timestamp")
    return parsed


def allowed_repositories(payload: dict[str, Any]) -> set[str]:
    repositories = payload.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise GateError("OSS repository config must contain repositories")
    names = {
        entry.get("repository")
        for entry in repositories
        if isinstance(entry, dict) and isinstance(entry.get("repository"), str)
    }
    if len(names) != len(repositories):
        raise GateError("OSS repository config contains an invalid or duplicate repository")
    return names


def valid_hash(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def validate_provenance(provenance: object, index: int) -> tuple[str, int]:
    if not isinstance(provenance, dict) or set(provenance) != PROVENANCE_KEYS:
        raise GateError("Every OSS Shadow run needs GitHub Actions provenance")
    for key, expected in SCHEDULED_WORKFLOW.items():
        if provenance.get(key) != expected:
            raise GateError(f"runs[{index}].provenance.{key} does not match the schedule")
    github_run_id = provenance.get("github_run_id")
    run_attempt = provenance.get("run_attempt")
    if (
        not isinstance(github_run_id, str)
        or not github_run_id.isdigit()
        or int(github_run_id) <= 0
    ):
        raise GateError("GitHub Actions run id must be a positive decimal string")
    if type(run_attempt) is not int or run_attempt <= 0:
        raise GateError("GitHub Actions run attempt must be a positive integer")
    for field in ("head_sha", "workflow_sha"):
        if not isinstance(provenance.get(field), str) or not COMMIT_RE.fullmatch(
            provenance[field]
        ):
            raise GateError(f"runs[{index}].provenance.{field} must be a commit SHA")
    return github_run_id, run_attempt


def validate_rate_limits(value: object, run_at: datetime, required: bool) -> bool:
    if value is None and not required:
        return False
    if not isinstance(value, dict):
        raise GateError("Complete OSS Shadow runs need exact core/search rate-limit evidence")
    buckets = set(value)
    if not buckets <= {"core", "search"} or (
        required and buckets != {"core", "search"}
    ):
        raise GateError("Complete OSS Shadow runs need exact core/search rate-limit evidence")
    for bucket in buckets:
        entry = value[bucket]
        if (
            not isinstance(entry, dict)
            or set(entry) != {"remaining", "reset_at"}
            or type(entry.get("remaining")) is not int
        ):
            raise GateError("OSS Shadow rate-limit evidence is malformed")
        if required and not 0 <= entry["remaining"] <= RATE_LIMIT_MAXIMUMS[bucket]:
            raise GateError("OSS Shadow rate-limit remaining exceeds the anonymous API policy")
        reset_at = parse_utc(entry.get("reset_at"), f"rate_limits.{bucket}.reset_at")
        if required and (reset_at < run_at or reset_at > run_at + timedelta(days=7)):
            raise GateError("OSS Shadow rate-limit reset must precede the next weekly run")
    return buckets == {"core", "search"}


def max_consecutive_weeks(weeks: set[tuple[int, int]]) -> int:
    mondays = sorted(date.fromisocalendar(year, week, 1) for year, week in weeks)
    longest = 0
    current = 0
    previous: date | None = None
    for monday in mondays:
        current = current + 1 if previous and monday - previous == timedelta(days=7) else 1
        longest = max(longest, current)
        previous = monday
    return longest


def evaluate_gate(
    gate: dict[str, Any],
    repositories: set[str],
    now: datetime | None = None,
) -> dict[str, int | bool | str]:
    evaluation_time = now or datetime.now(timezone.utc)
    if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
        raise GateError("OSS delivery gate evaluation time must be timezone-aware")
    evaluation_time = evaluation_time.astimezone(timezone.utc)

    if set(gate) != GATE_KEYS or gate.get("schema_version") != 3:
        raise GateError("OSS delivery gate schema_version must equal 3")
    status = gate.get("status")
    if status not in {"LOCKED", "APPROVED"}:
        raise GateError("OSS delivery gate status must be LOCKED or APPROVED")
    if gate.get("requirements") != REQUIREMENTS:
        raise GateError("OSS delivery gate requirements must match the hard-coded policy")
    if gate.get("scheduled_workflow") != SCHEDULED_WORKFLOW:
        raise GateError("OSS delivery gate scheduled_workflow must match the hard-coded policy")
    if gate.get("shadow_contract_sha256") != CURRENT_SHADOW_CONTRACT:
        raise GateError("OSS delivery gate Shadow contract is stale")

    runs = gate.get("runs")
    if not isinstance(runs, list):
        raise GateError("OSS delivery gate runs must be a list")
    run_ids: set[str] = set()
    github_run_attempts: set[tuple[str, int]] = set()
    attempts_by_run: dict[str, set[int]] = {}
    provenance_by_run: dict[str, tuple[str, str]] = {}
    attempt_times_by_run: dict[str, dict[int, tuple[datetime, datetime, datetime]]] = {}
    metadata_hashes: set[str] = set()
    artifact_hashes: set[str] = set()
    markdown_hashes: set[str] = set()
    observed_weeks: set[tuple[int, int]] = set()
    qualifying_weeks: set[tuple[int, int]] = set()
    run_times: dict[str, datetime] = {}
    run_attestation_times: dict[str, datetime] = {}
    run_candidates: dict[str, set[str]] = {}
    qualifying_run_ids: set[str] = set()
    total_delivery_count = 0
    first_attempt_times: dict[str, datetime] = {}

    for index, run in enumerate(runs):
        if not isinstance(run, dict) or set(run) != RUN_KEYS:
            raise GateError("Every OSS Shadow run must be an object")
        provenance = run.get("provenance")
        github_run_id, run_attempt = validate_provenance(provenance, index)
        run_id = run.get("run_id")
        expected_run_id = f"github-{github_run_id}-attempt-{run_attempt}"
        attempt_key = (github_run_id, run_attempt)
        if run_id != expected_run_id or run_id in run_ids or attempt_key in github_run_attempts:
            raise GateError("OSS Shadow run identity must be derived and unique")
        run_ids.add(run_id)
        github_run_attempts.add(attempt_key)
        attempts_by_run.setdefault(github_run_id, set()).add(run_attempt)
        provenance_identity = (provenance["head_sha"], provenance["workflow_sha"])
        previous_identity = provenance_by_run.setdefault(github_run_id, provenance_identity)
        if previous_identity != provenance_identity:
            raise GateError("Rerun provenance must keep the original head and workflow SHA")

        run_at = parse_utc(run.get("run_at"), f"runs[{index}].run_at")
        workflow_recorded_at = parse_utc(
            run.get("workflow_recorded_at"), f"runs[{index}].workflow_recorded_at"
        )
        attested_at = parse_utc(run.get("attested_at"), f"runs[{index}].attested_at")
        if (
            not run_at <= workflow_recorded_at <= attested_at <= evaluation_time
            or workflow_recorded_at - run_at > timedelta(minutes=15)
        ):
            raise GateError("OSS Shadow run and attestation times must not be future or reversed")
        week = run_at.isocalendar()[:2]
        if run_attempt == 1:
            if week in observed_weeks:
                raise GateError("Only one first-attempt scheduled run may be recorded per ISO week")
            observed_weeks.add(week)
            first_attempt_times[run_id] = run_at
        run_times[run_id] = run_at
        run_attestation_times[run_id] = attested_at
        attempt_times_by_run.setdefault(github_run_id, {})[run_attempt] = (
            run_at,
            workflow_recorded_at,
            attested_at,
        )

        if run.get("shadow_contract_sha256") != CURRENT_SHADOW_CONTRACT:
            raise GateError("OSS Shadow run contract does not match current code")
        metadata_hash = run.get("metadata_sha256")
        if not valid_hash(metadata_hash) or metadata_hash in metadata_hashes:
            raise GateError("OSS Shadow metadata_sha256 must be valid and unique")
        metadata_hashes.add(metadata_hash)

        collector_complete = run.get("collector_complete")
        collector_exit_code = run.get("collector_exit_code")
        if type(collector_complete) is not bool:
            raise GateError("OSS Shadow collector_complete must be boolean")
        if type(collector_exit_code) is not int or not 0 <= collector_exit_code <= 255:
            raise GateError("OSS Shadow collector_exit_code must be an exit status")
        if collector_complete != (collector_exit_code == 0):
            raise GateError("OSS Shadow collector completion contradicts its exit code")

        artifact_hash = run.get("artifact_sha256")
        markdown_hash = run.get("markdown_sha256")
        if collector_complete and (
            not valid_hash(artifact_hash) or not valid_hash(markdown_hash)
        ):
            raise GateError("Complete OSS Shadow runs need JSON and Markdown hashes")
        if artifact_hash is not None:
            if not valid_hash(artifact_hash) or artifact_hash in artifact_hashes:
                raise GateError("OSS Shadow artifact_sha256 must be unique")
            artifact_hashes.add(artifact_hash)
        if markdown_hash is not None:
            if not valid_hash(markdown_hash) or markdown_hash in markdown_hashes:
                raise GateError("OSS Shadow markdown_sha256 must be unique")
            markdown_hashes.add(markdown_hash)

        candidate_keys = run.get("candidate_keys")
        repository_keys = run.get("repository_keys")
        if repository_keys != sorted(repositories):
            raise GateError("OSS Shadow run repository coverage does not match the allowlist")
        if not isinstance(candidate_keys, list) or not all(
            isinstance(key, str) and CANDIDATE_RE.fullmatch(key) for key in candidate_keys
        ):
            raise GateError("OSS Shadow candidate_keys must contain repository#number values")
        if len(candidate_keys) != len(set(candidate_keys)):
            raise GateError("OSS Shadow candidate_keys must not contain duplicates")
        if len(candidate_keys) > 3 or (not collector_complete and candidate_keys):
            raise GateError("OSS Shadow candidate_keys exceed the collector artifact contract")
        candidate_repositories = {
            CANDIDATE_RE.fullmatch(key).group(1) for key in candidate_keys
        }
        if not candidate_repositories <= repositories:
            raise GateError("OSS Shadow candidate_keys contain a repository outside the allowlist")
        run_candidates[run_id] = set(candidate_keys)

        request_count = run.get("request_count")
        maximum_request_count = 2 * len(repositories) + 3 * 3
        if request_count is not None and (
            type(request_count) is not int
            or not 0 <= request_count <= maximum_request_count
        ):
            raise GateError("OSS Shadow request_count exceeds the allowlist request plan")
        if collector_complete and request_count is None:
            raise GateError("Complete OSS Shadow runs need a request count")
        rate_limits_valid = validate_rate_limits(
            run.get("rate_limits"), run_at, required=collector_complete
        )

        for field in ("http_403_count", "http_429_count", "discord_delivery_count"):
            value = run.get(field)
            if value is not None and (type(value) is not int or value < 0):
                raise GateError(f"OSS Shadow {field} must be a non-negative integer or null")
        if collector_complete and any(
            run.get(field) is None for field in ("http_403_count", "http_429_count")
        ):
            raise GateError("Complete OSS Shadow runs need HTTP status counts")
        delivery_count = run.get("discord_delivery_count")
        if delivery_count is None:
            raise GateError("OSS Shadow runs need a Discord delivery count")
        total_delivery_count += delivery_count

        for field in ("sort_accuracy_percent", "freshness_accuracy_percent"):
            if run.get(field) not in {0, 100}:
                raise GateError(f"OSS Shadow {field} must be an explicit 0 or 100 attestation")
        warnings = run.get("warnings")
        if not isinstance(warnings, list) or not all(
            isinstance(value, str) and value.strip() for value in warnings
        ) or len(warnings) != len(set(warnings)):
            raise GateError("OSS Shadow warnings must be unique non-empty strings")
        repository_failures = run.get("repository_failures")
        if not isinstance(repository_failures, list):
            raise GateError("OSS Shadow repository_failures must be a list")
        seen_failure_repositories: set[str] = set()
        for failure in repository_failures:
            if (
                not isinstance(failure, dict)
                or set(failure) != {"repository", "reason"}
                or failure.get("repository") not in repositories
                or not isinstance(failure.get("reason"), str)
                or not failure["reason"].strip()
                or failure["repository"] in seen_failure_repositories
            ):
                raise GateError("OSS Shadow repository failure evidence is invalid")
            seen_failure_repositories.add(failure["repository"])

        clean_request_counts = {
            2 * len(repositories) + 3 * candidate_count
            for candidate_count in range(len(candidate_keys), 4)
        }
        if (
            collector_complete
            and not warnings
            and not repository_failures
            and request_count not in clean_request_counts
        ):
            raise GateError(
                "OSS Shadow request_count contradicts successful repository coverage"
            )

        qualifies = (
            run_attempt == 1
            and collector_complete
            and collector_exit_code == 0
            and request_count is not None
            and rate_limits_valid
            and run.get("http_403_count") == 0
            and run.get("http_429_count") == 0
            and delivery_count == 0
            and run.get("sort_accuracy_percent") == 100
            and run.get("freshness_accuracy_percent") == 100
            and not warnings
            and not repository_failures
        )
        if qualifies:
            qualifying_run_ids.add(run_id)
            qualifying_weeks.add(week)

    for github_run_id, attempts in attempts_by_run.items():
        if attempts != set(range(1, max(attempts) + 1)):
            raise GateError(
                f"GitHub Actions run {github_run_id} has a missing rerun attempt"
            )
        ordered = [
            attempt_times_by_run[github_run_id][attempt]
            for attempt in sorted(attempts)
        ]
        if any(
            not all(
                previous_time < current_time
                for previous_time, current_time in zip(previous, current)
            )
            for previous, current in zip(ordered, ordered[1:])
        ):
            raise GateError("GitHub Actions rerun timestamps must increase by attempt")
        if any(
            current[0] <= previous[1]
            for previous, current in zip(ordered, ordered[1:])
        ):
            raise GateError("A GitHub Actions rerun must start after prior workflow metadata")

    reviews = gate.get("candidate_reviews")
    if not isinstance(reviews, list):
        raise GateError("OSS delivery gate candidate_reviews must be a list")
    reviewed_candidates: set[str] = set()
    relevant = 0
    scope_clear = 0
    false_positives = 0
    review_times: list[datetime] = []
    for index, review in enumerate(reviews):
        if not isinstance(review, dict) or set(review) != REVIEW_KEYS:
            raise GateError("Every OSS candidate review must be an object")
        key = review.get("candidate_key")
        match = CANDIDATE_RE.fullmatch(key) if isinstance(key, str) else None
        if match is None or key in reviewed_candidates:
            raise GateError("OSS candidate_key must be a unique repository#number")
        if match.group(1) not in repositories:
            raise GateError(f"OSS candidate is outside the allowlist: {match.group(1)}")
        reviewed_candidates.add(key)
        source_run_id = review.get("source_run_id")
        if source_run_id not in qualifying_run_ids:
            raise GateError("OSS candidate review must reference a qualifying Shadow run")
        if key not in run_candidates[str(source_run_id)]:
            raise GateError("OSS candidate review must reference a candidate in its source artifact")
        reviewed_at = parse_utc(review.get("reviewed_at"), f"candidate_reviews[{index}].reviewed_at")
        if (
            reviewed_at < run_attestation_times[str(source_run_id)]
            or reviewed_at > evaluation_time
        ):
            raise GateError("OSS candidate review must follow its attestation and not be future")
        review_times.append(reviewed_at)
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            raise GateError("OSS candidate review needs a reviewer")
        if not isinstance(review.get("notes"), str) or not review["notes"].strip():
            raise GateError("OSS candidate review needs concise evidence notes")
        for field in ("relevant", "scope_clear", "hard_gate_false_positive"):
            if type(review.get(field)) is not bool:
                raise GateError(f"OSS candidate review {field} must be boolean")
        false_positive_reason = review.get("false_positive_reason")
        if review["hard_gate_false_positive"]:
            if false_positive_reason not in FALSE_POSITIVE_REASONS:
                raise GateError("Hard-gate false positives need a controlled reason")
        elif false_positive_reason is not None:
            raise GateError("Non-false-positive reviews must not have a false-positive reason")
        relevant += int(review["relevant"])
        scope_clear += int(review["scope_clear"])
        false_positives += int(review["hard_gate_false_positive"])

    review_count = len(reviewed_candidates)
    relevance_percent = (relevant * 100 // review_count) if review_count else 0
    scope_percent = (scope_clear * 100 // review_count) if review_count else 0
    consecutive_weeks = max_consecutive_weeks(qualifying_weeks)
    latest_first_attempt_qualifies = (
        not first_attempt_times
        or max(first_attempt_times, key=first_attempt_times.get) in qualifying_run_ids
    )
    evidence_passes = (
        len(qualifying_weeks) >= REQUIREMENTS["minimum_distinct_weeks"]
        and consecutive_weeks >= REQUIREMENTS["minimum_consecutive_qualifying_weeks"]
        and review_count >= REQUIREMENTS["minimum_unique_candidates"]
        and relevance_percent >= REQUIREMENTS["minimum_relevance_percent"]
        and scope_percent >= REQUIREMENTS["minimum_scope_clarity_percent"]
        and false_positives <= REQUIREMENTS["maximum_hard_gate_false_positives"]
        and total_delivery_count == 0
        and latest_first_attempt_qualifies
    )

    approved_at = gate.get("approved_at")
    if status == "LOCKED":
        if approved_at is not None:
            raise GateError("LOCKED OSS delivery gate must not have approved_at")
        approved = False
    else:
        approval_time = parse_utc(approved_at, "approved_at")
        if approval_time > evaluation_time:
            raise GateError("OSS delivery approval must not be in the future")
        if not evidence_passes:
            raise GateError("APPROVED OSS delivery gate does not satisfy its evidence policy")
        latest_evidence = max([*run_attestation_times.values(), *review_times])
        if approval_time < latest_evidence:
            raise GateError("OSS delivery approval predates its latest evidence")
        latest_qualifying = max(run_times[run_id] for run_id in qualifying_run_ids)
        if approval_time - latest_qualifying > timedelta(
            days=REQUIREMENTS["maximum_approval_lag_days"]
        ):
            raise GateError("OSS delivery approval is too old relative to Shadow evidence")
        approved = True

    return {
        "status": str(status),
        "approved": approved,
        "observed_runs": len(runs),
        "qualifying_weeks": len(qualifying_weeks),
        "consecutive_qualifying_weeks": consecutive_weeks,
        "unique_candidates": review_count,
        "relevance_percent": relevance_percent,
        "scope_clarity_percent": scope_percent,
        "hard_gate_false_positives": false_positives,
        "shadow_discord_deliveries": total_delivery_count,
    }


def write_github_output(path: Path, result: dict[str, int | bool | str]) -> None:
    with path.open("a", encoding="utf-8") as output:
        output.write(f"approved={'true' if result['approved'] else 'false'}\n")
        output.write(f"qualifying_weeks={result['qualifying_weeks']}\n")
        output.write(f"unique_candidates={result['unique_candidates']}\n")


def main() -> int:
    args = parse_args()
    if args.print_shadow_contract:
        print(CURRENT_SHADOW_CONTRACT)
        return 0
    try:
        result = evaluate_gate(
            read_object(args.gate),
            allowed_repositories(read_object(args.repositories)),
        )
        if args.github_output is not None:
            write_github_output(args.github_output, result)
    except (GateError, OSError) as exc:
        print(f"OSS delivery gate failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
