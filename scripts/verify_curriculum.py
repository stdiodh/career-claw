#!/usr/bin/env python3
"""Verify curriculum contracts and return only reproducibly verified lessons."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND_CONFIG = ROOT / "configs/backend-practice.json"
MATRIX_CONFIG = ROOT / "configs/curriculum-matrix.json"
PROFILE_CONFIG = ROOT / "configs/verification-profile.json"
TAXONOMY_CONFIG = ROOT / "configs/competency-taxonomy.json"
JOB_MARKET_AUDIT = ROOT / "audits/job-market-2026q3.json"
MANIFEST_FILE = ROOT / "data/curriculum-verification.json"
LAB_DIR = ROOT / "lab"
EXCLUDED_LAB_PARTS = {".gradle", ".kotlin", ".idea", "build", ".DS_Store"}
LAB_TEST_ID_RE = re.compile(r"\bLAB-[A-Z]+-\d{3}\b")
ALLOWED_JOB_SCOPE_CODES = {
    "ENTRY",
    "ENTRY_ACCEPTED",
    "INTERNSHIP",
    "INTERNSHIP_NO_PRIOR_EXPERIENCE",
    "INTERNSHIP_OR_ENTRY",
    "MINIMUM_SIX_MONTHS",
    "ZERO_TO_TWO_YEARS",
    "ZERO_TO_THREE_YEARS",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-config", type=Path, default=BACKEND_CONFIG)
    parser.add_argument("--matrix", type=Path, default=MATRIX_CONFIG)
    parser.add_argument("--profile", type=Path, default=PROFILE_CONFIG)
    parser.add_argument("--taxonomy", type=Path, default=TAXONOMY_CONFIG)
    parser.add_argument("--job-market-audit", type=Path, default=JOB_MARKET_AUDIT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_FILE)
    parser.add_argument("--lab", type=Path, default=LAB_DIR)
    parser.add_argument(
        "--emit-contracts",
        action="store_true",
        help="Print calculated hashes even when the verification manifest is stale.",
    )
    return parser.parse_args()


def read_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return payload


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def is_immutable_revision_url(url: str) -> bool:
    github_match = re.search(
        r"^https://github\.com/[^/]+/[^/]+/(?:tree|commit|releases/tag)/([^/?#]+)",
        url,
    )
    if github_match:
        return github_match.group(1).lower() not in {"main", "master", "head", "latest"}
    return bool(
        re.search(
            r"(?:/editions/\d{4}/|/rfc\d+(?:\.html)?(?:$|[?#])|/(?:v|rel_|jdk-)?\d[\w.+-]*(?:/|$))",
            url,
            re.IGNORECASE,
        )
    )


def calculate_lab_revision(lab_dir: Path) -> str:
    if not lab_dir.is_dir():
        raise RuntimeError(f"Lab directory does not exist: {lab_dir}")

    digest = hashlib.sha256()
    files = [
        path
        for path in lab_dir.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_LAB_PARTS for part in path.relative_to(lab_dir).parts)
    ]
    if not files:
        raise RuntimeError(f"Lab directory has no tracked inputs: {lab_dir}")

    for path in sorted(files, key=lambda candidate: candidate.relative_to(lab_dir).as_posix()):
        relative = path.relative_to(lab_dir).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lab_test_id_counts(lab_dir: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    source_root = lab_dir / "src"
    if not source_root.is_dir():
        return counts
    for path in source_root.rglob("*"):
        if path.is_file() and path.suffix in {".kt", ".java"}:
            counts.update(LAB_TEST_ID_RE.findall(path.read_text(encoding="utf-8")))
    return counts


def lab_source_paths(lab_dir: Path) -> set[str]:
    return {
        f"lab/{path.relative_to(lab_dir).as_posix()}"
        for path in lab_dir.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_LAB_PARTS for part in path.relative_to(lab_dir).parts)
    }


def validate_lab_profile(lab_dir: Path, profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    build_path = lab_dir / "build.gradle.kts"
    wrapper_properties_path = lab_dir / "gradle/wrapper/gradle-wrapper.properties"
    wrapper_jar_path = lab_dir / "gradle/wrapper/gradle-wrapper.jar"
    dependency_lock_path = lab_dir / "gradle.lockfile"
    postgres_test_path = lab_dir / "src/postgresTest"
    required_paths = (
        build_path,
        wrapper_properties_path,
        wrapper_jar_path,
        dependency_lock_path,
    )
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        return [f"Missing lab profile file(s): {', '.join(missing)}"]

    build = build_path.read_text(encoding="utf-8")
    boot_version = str(profile.get("spring_boot", {}).get("version", ""))
    kotlin_version = str(profile.get("kotlin", {}).get("version", ""))
    jdk_version = str(profile.get("jdk", {}).get("version", ""))
    jdk_major_match = re.match(r"(\d+)", jdk_version)
    jdk_major = jdk_major_match.group(1) if jdk_major_match else ""
    if f'id("org.springframework.boot") version "{boot_version}"' not in build:
        errors.append("Lab Spring Boot plugin does not match the verification profile")
    for plugin in ("jvm", "plugin.spring", "plugin.jpa"):
        if f'kotlin("{plugin}") version "{kotlin_version}"' not in build:
            errors.append(f"Lab Kotlin {plugin} plugin does not match the verification profile")
    if not jdk_major or f"JavaLanguageVersion.of({jdk_major})" not in build:
        errors.append("Lab Java toolchain does not match the verification profile")
    if not jdk_major or f"JvmTarget.JVM_{jdk_major}" not in build:
        errors.append("Lab Kotlin JVM target does not match the verification profile")
    if "dependencyLocking" not in build or "lockAllConfigurations()" not in build:
        errors.append("Lab must enforce dependency locking for every configuration")

    locked_versions: dict[str, str] = {}
    for raw_line in dependency_lock_path.read_text(encoding="utf-8").splitlines():
        coordinate, separator, _ = raw_line.partition("=")
        parts = coordinate.split(":")
        if separator and len(parts) == 3:
            locked_versions[f"{parts[0]}:{parts[1]}"] = parts[2]
    managed_coordinates = {
        "spring_framework": "org.springframework:spring-core",
        "spring_security": "org.springframework.security:spring-security-core",
        "spring_data_jpa": "org.springframework.data:spring-data-jpa",
        "flyway": "org.flywaydb:flyway-core",
        "hibernate_orm": "org.hibernate.orm:hibernate-core",
        "jackson_kotlin": "tools.jackson.module:jackson-module-kotlin",
    }
    managed_dependencies = profile.get("managed_dependencies")
    if not isinstance(managed_dependencies, dict):
        errors.append("Verification profile managed_dependencies must be an object")
    else:
        for profile_key, coordinate in managed_coordinates.items():
            expected = managed_dependencies.get(profile_key)
            if not isinstance(expected, str) or not expected:
                errors.append(f"Verification profile lacks managed dependency {profile_key}")
            elif locked_versions.get(coordinate) != expected:
                errors.append(
                    f"Lab dependency lock for {coordinate} does not match the profile"
                )

    properties: dict[str, str] = {}
    for raw_line in wrapper_properties_path.read_text(encoding="utf-8").splitlines():
        if "=" in raw_line:
            key, value = raw_line.split("=", 1)
            properties[key] = value.replace("\\:", ":")
    gradle = profile.get("gradle", {})
    if properties.get("distributionUrl") != gradle.get("distribution"):
        errors.append("Gradle distribution URL does not match the verification profile")
    if properties.get("distributionSha256Sum") != gradle.get("distribution_sha256"):
        errors.append("Gradle distribution checksum does not match the verification profile")
    if file_sha256(wrapper_jar_path) != gradle.get("wrapper_jar_sha256"):
        errors.append("Gradle wrapper JAR checksum does not match the verification profile")

    postgres_digest = str(profile.get("postgresql", {}).get("oci_index_digest", ""))
    postgres_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in postgres_test_path.rglob("*.kt")
        if path.is_file()
    ) if postgres_test_path.is_dir() else ""
    if postgres_digest not in postgres_sources:
        errors.append("PostgreSQL Testcontainers image is not pinned to the profile OCI digest")
    return errors


def indexed_items(items: object, kind: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    indexed: dict[str, dict[str, Any]] = {}
    if not isinstance(items, list) or not items:
        return {}, [f"{kind} must be a non-empty list"]
    for item in items:
        if not isinstance(item, dict):
            errors.append(f"Every {kind} item must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"Every {kind} item must have a non-empty id")
            continue
        if item_id in indexed:
            errors.append(f"Duplicate {kind} id: {item_id}")
            continue
        indexed[item_id] = item
    return indexed, errors


def validate_job_market_audit(
    job_market: dict[str, Any], taxonomy: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    today = date.today()
    if job_market.get("status") != "COMPLETE":
        errors.append("Job-market audit status must be COMPLETE")

    market_keywords = taxonomy.get("market_keywords")
    if not isinstance(market_keywords, dict) or not market_keywords:
        errors.append("Taxonomy market_keywords must be a non-empty object")
        market_keywords = {}

    method = job_market.get("method")
    threshold = method.get("market_demand_threshold") if isinstance(method, dict) else None
    sample_size = method.get("sample_size") if isinstance(method, dict) else None
    if type(threshold) is not int or threshold <= 0:
        errors.append("Job-market audit threshold must be a positive integer")
        threshold = None
    if type(sample_size) is not int or sample_size <= 0:
        errors.append("Job-market audit sample_size must be a positive integer")
        sample_size = None

    sample_limits: dict[str, int] = {}
    for key in (
        "minimum_companies",
        "maximum_per_company",
        "maximum_industry_share_percent",
    ):
        value = method.get(key) if isinstance(method, dict) else None
        if type(value) is not int or value <= 0:
            errors.append(f"Job-market audit {key} must be a positive integer")
        else:
            sample_limits[key] = value

    try:
        checked_at = date.fromisoformat(str(job_market["checked_at"]))
        window_start = date.fromisoformat(str(job_market["window_start"]))
        valid_until = date.fromisoformat(str(job_market["valid_until"]))
        if window_start > checked_at or (checked_at - window_start).days > 60:
            errors.append("Job-market audit must use a window of at most 60 days")
        if checked_at > today or window_start > today:
            errors.append("Job-market audit dates must not be in the future")
        if valid_until < checked_at or (valid_until - checked_at).days > 92:
            errors.append("Job-market audit validity must end within one quarter")
        if today > valid_until:
            errors.append("Job-market audit has expired and must be refreshed")
    except (KeyError, ValueError):
        errors.append("Job-market audit dates and valid_until must use ISO YYYY-MM-DD values")
        checked_at = None
        window_start = None

    taxonomy_threshold = taxonomy.get("market_demand_threshold")
    if not isinstance(taxonomy_threshold, dict):
        errors.append("Taxonomy market_demand_threshold must be an object")
    else:
        if threshold is not None and taxonomy_threshold.get("minimum_occurrences") != threshold:
            errors.append("Job-market audit threshold does not match the frozen taxonomy")
        if sample_size is not None and taxonomy_threshold.get("sample_size") != sample_size:
            errors.append("Job-market audit sample_size does not match the frozen taxonomy")
        limit_mapping = {
            "minimum_companies": "minimum_companies",
            "maximum_per_company": "maximum_postings_per_company",
            "maximum_industry_share_percent": "maximum_industry_share_percent",
        }
        for audit_key, taxonomy_key in limit_mapping.items():
            if (
                audit_key in sample_limits
                and taxonomy_threshold.get(taxonomy_key) != sample_limits[audit_key]
            ):
                errors.append(
                    f"Job-market audit {audit_key} does not match the frozen taxonomy"
                )

    postings = job_market.get("postings")
    calculated: Counter[str] = Counter()
    companies: Counter[str] = Counter()
    industries: Counter[str] = Counter()
    posting_keys: set[tuple[str, str]] = set()
    source_urls: set[str] = set()
    if not isinstance(postings, list) or not postings:
        errors.append("Job-market audit postings must be a non-empty list")
        postings = []
    elif sample_size is not None and len(postings) != sample_size:
        errors.append("Job-market audit posting count does not match sample_size")
    for posting in postings:
        if not isinstance(posting, dict):
            errors.append("Every job-market posting must be an object")
            continue
        text_fields = ("company", "role", "experience", "industry", "date_posted", "source_url")
        if not all(
            isinstance(posting.get(field), str) and posting[field].strip()
            for field in text_fields
        ):
            errors.append("Every job-market posting needs identity, scope, date, and source fields")
        else:
            if (
                posting.get("scope_rule") != "INTERNSHIP_ENTRY_OR_MAX_3Y"
                or posting.get("scope_verified") is not True
                or posting.get("experience") not in ALLOWED_JOB_SCOPE_CODES
            ):
                errors.append(
                    "Every job-market posting needs a controlled, explicitly verified <=3-year "
                    "scope attestation"
                )
            company = posting["company"]
            role = posting["role"]
            source_url = posting["source_url"]
            identity = (company, role)
            if identity in posting_keys:
                errors.append("Job-market postings must not duplicate company and role")
            posting_keys.add(identity)
            if source_url in source_urls:
                errors.append("Job-market source URLs must be unique")
            source_urls.add(source_url)
            if not source_url.startswith("https://"):
                errors.append("Job-market source URLs must use HTTPS")
            companies.update([company])
            industries.update([str(posting.get("industry_group", posting["industry"]))])
            try:
                posted_at = date.fromisoformat(posting["date_posted"])
                if (
                    checked_at is not None
                    and window_start is not None
                    and not window_start <= posted_at <= checked_at
                ):
                    errors.append("Job-market posting date is outside the frozen window")
            except ValueError:
                errors.append("Job-market posting dates must use ISO YYYY-MM-DD values")
        keyword_ids = posting.get("keyword_ids")
        if not isinstance(keyword_ids, list) or not keyword_ids or not all(
            isinstance(keyword_id, str) for keyword_id in keyword_ids
        ):
            errors.append("Every job-market posting needs non-empty keyword_ids")
            continue
        if len(keyword_ids) != len(set(keyword_ids)):
            errors.append("Job-market posting keyword_ids must not contain duplicates")
        unknown = sorted(set(keyword_ids) - set(market_keywords))
        if unknown:
            errors.append(f"Unknown job-market keyword id(s): {', '.join(unknown)}")
        calculated.update(keyword_ids)

    if companies and "minimum_companies" in sample_limits:
        if len(companies) < sample_limits["minimum_companies"]:
            errors.append("Job-market audit has too few distinct companies")
    if companies and "maximum_per_company" in sample_limits:
        if max(companies.values()) > sample_limits["maximum_per_company"]:
            errors.append("Job-market audit exceeds the per-company sample limit")
    if postings and industries and "maximum_industry_share_percent" in sample_limits:
        share = max(industries.values()) * 100 / len(postings)
        if share > sample_limits["maximum_industry_share_percent"]:
            errors.append("Job-market audit exceeds the industry concentration limit")

    frequency = job_market.get("frequency")
    if not isinstance(frequency, dict) or not frequency or not all(
        isinstance(key, str) and type(value) is int and value >= 0
        for key, value in frequency.items()
    ):
        errors.append("Job-market frequency must contain non-negative integer counts")
        frequency = {}
    elif dict(calculated) != frequency:
        errors.append("Job-market frequency is not reproducible from postings")

    supported_ids = job_market.get("market_supported_ids")
    if not isinstance(supported_ids, list) or not all(
        isinstance(value, str) for value in supported_ids
    ):
        errors.append("Job-market market_supported_ids must be a list of ids")
    elif threshold is not None:
        expected = {key for key, value in frequency.items() if value >= threshold}
        if set(supported_ids) != expected or len(supported_ids) != len(set(supported_ids)):
            errors.append("Job-market market_supported_ids do not match the threshold")
    return errors


def lesson_contract(
    lesson: dict[str, Any],
    matrix_entry: dict[str, Any],
    profile: dict[str, Any],
    taxonomy: dict[str, Any],
    job_market: dict[str, Any],
    lab_revision: str,
) -> str:
    return canonical_hash(
        {
            "lesson": lesson,
            "matrix": matrix_entry,
            "profile": profile,
            "taxonomy": taxonomy,
            "job_market": job_market,
            "lab_revision": lab_revision,
        }
    )


def evaluate_curriculum(
    backend: dict[str, Any],
    matrix: dict[str, Any],
    profile: dict[str, Any],
    taxonomy: dict[str, Any],
    job_market: dict[str, Any],
    manifest: dict[str, Any],
    lab_revision: str,
    test_id_counts: Counter[str] | None = None,
    lab_profile_errors: list[str] | None = None,
    available_lab_paths: set[str] | None = None,
) -> dict[str, Any]:
    lessons, errors = indexed_items(backend.get("lessons"), "lesson")
    errors.extend(lab_profile_errors or [])
    errors.extend(validate_job_market_audit(job_market, taxonomy))
    entries, entry_errors = indexed_items(matrix.get("lessons"), "matrix lesson")
    errors.extend(entry_errors)

    expected_schema_versions = (
        ("backend catalog", backend, 2),
        ("curriculum matrix", matrix, 1),
        ("verification profile", profile, 1),
        ("competency taxonomy", taxonomy, 1),
        ("job-market audit", job_market, 1),
        ("verification manifest", manifest, 1),
    )
    for name, payload, expected in expected_schema_versions:
        if payload.get("schema_version") != expected:
            errors.append(f"{name} schema_version must equal {expected}")

    missing_entries = sorted(set(lessons) - set(entries))
    extra_entries = sorted(set(entries) - set(lessons))
    if missing_entries:
        errors.append(f"Missing matrix lesson(s): {', '.join(missing_entries)}")
    if extra_entries:
        errors.append(f"Unknown matrix lesson(s): {', '.join(extra_entries)}")

    profile_id = profile.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        errors.append("Verification profile must have a profile_id")
    if matrix.get("profile_id") != profile_id:
        errors.append("Curriculum matrix profile_id does not match the verification profile")
    if backend.get("profile_id") != profile_id:
        errors.append("Backend catalog profile_id does not match the verification profile")
    if matrix.get("lab_revision") != lab_revision:
        errors.append("Curriculum matrix lab_revision does not match current lab contents")
    if matrix.get("job_market_audit") != "audits/job-market-2026q3.json":
        errors.append("Curriculum matrix must reference the frozen job-market audit")

    competencies, competency_errors = indexed_items(
        taxonomy.get("competencies"), "competency"
    )
    errors.extend(competency_errors)
    market_keywords = taxonomy.get("market_keywords")
    if not isinstance(market_keywords, dict):
        market_keywords = {}
    frequency = job_market.get("frequency")
    if not isinstance(frequency, dict):
        frequency = {}
    method = job_market.get("method")
    market_threshold = method.get("market_demand_threshold") if isinstance(method, dict) else None
    required = matrix.get("required_competencies")
    if not isinstance(required, list) or not required or not all(
        isinstance(value, str) for value in required
    ):
        errors.append("required_competencies must be a non-empty list of ids")
        required = []
    elif len(required) != len(set(required)):
        errors.append("required_competencies must not contain duplicates")
    unknown_required = sorted(set(required) - set(competencies))
    if unknown_required:
        errors.append(f"Unknown required competency id(s): {', '.join(unknown_required)}")

    core_entries: list[dict[str, Any]] = []
    covered: set[str] = set()
    contracts: dict[str, str] = {}
    assigned_test_ids: set[str] = set()
    source_review_dates: list[tuple[str, date]] = []
    for lesson_id in sorted(set(lessons) & set(entries)):
        entry = entries[lesson_id]
        tier = entry.get("tier")
        core_type = entry.get("core_type")
        if tier not in {"CORE", "OPTIONAL"}:
            errors.append(f"{lesson_id}: tier must be CORE or OPTIONAL")
        if core_type not in {"JVM_CORE", "PLATFORM_CORE", "OPTIONAL"}:
            errors.append(f"{lesson_id}: invalid core_type")
        if tier == "CORE":
            core_entries.append(entry)
            if core_type not in {"JVM_CORE", "PLATFORM_CORE"}:
                errors.append(f"{lesson_id}: CORE lesson needs a core type")
        elif tier == "OPTIONAL" and core_type != "OPTIONAL":
            errors.append(f"{lesson_id}: OPTIONAL lesson must use OPTIONAL core_type")

        competency_ids = entry.get("competency_ids")
        if not isinstance(competency_ids, list) or not competency_ids or not all(
            isinstance(value, str) for value in competency_ids
        ):
            errors.append(f"{lesson_id}: competency_ids must be a non-empty list")
            competency_ids = []
        elif len(competency_ids) != len(set(competency_ids)):
            errors.append(f"{lesson_id}: competency_ids contain duplicates")
        unknown = sorted(set(competency_ids) - set(competencies))
        if unknown:
            errors.append(f"{lesson_id}: unknown competency id(s): {', '.join(unknown)}")
        if tier == "CORE":
            covered.update(competency_ids)

        scores = entry.get("scores")
        score_keys = {
            "necessity",
            "source_fit",
            "stack_relevance",
            "failure_reproduction",
            "executable_evidence",
        }
        if not isinstance(scores, dict) or set(scores) != score_keys or not all(
            type(value) is int and 0 <= value <= 2 for value in scores.values()
        ):
            errors.append(f"{lesson_id}: scores must contain five integer values from 0 to 2")
        elif tier == "CORE":
            if sum(scores.values()) < 8:
                errors.append(f"{lesson_id}: core score is below 8/10")
            for mandatory in ("source_fit", "failure_reproduction", "executable_evidence"):
                if scores[mandatory] != 2:
                    errors.append(f"{lesson_id}: {mandatory} must equal 2")
            if core_type == "JVM_CORE" and scores["stack_relevance"] != 2:
                errors.append(f"{lesson_id}: JVM_CORE stack_relevance must equal 2")
            if core_type == "PLATFORM_CORE" and scores["stack_relevance"] < 1:
                errors.append(f"{lesson_id}: PLATFORM_CORE stack_relevance must be at least 1")

        necessity = entry.get("necessity_evidence")
        if not isinstance(necessity, dict):
            errors.append(f"{lesson_id}: necessity_evidence must be an object")
        elif necessity.get("kind") == "MARKET":
            if set(necessity) != {"kind", "keyword_ids"}:
                errors.append(f"{lesson_id}: MARKET evidence needs only kind and keyword_ids")
            keyword_ids = necessity.get("keyword_ids")
            if not isinstance(keyword_ids, list) or not keyword_ids or not all(
                isinstance(value, str) for value in keyword_ids
            ):
                errors.append(f"{lesson_id}: MARKET evidence needs non-empty keyword_ids")
            else:
                if len(keyword_ids) != len(set(keyword_ids)):
                    errors.append(f"{lesson_id}: MARKET keyword_ids contain duplicates")
                unknown_market = sorted(set(keyword_ids) - set(market_keywords))
                if unknown_market:
                    errors.append(
                        f"{lesson_id}: unknown MARKET keyword id(s): {', '.join(unknown_market)}"
                    )
                unsupported = sorted(
                    keyword_id
                    for keyword_id in keyword_ids
                    if type(market_threshold) is not int
                    or type(frequency.get(keyword_id)) is not int
                    or frequency[keyword_id] < market_threshold
                )
                if unsupported:
                    errors.append(
                        f"{lesson_id}: MARKET keyword(s) are below the frozen threshold: "
                        f"{', '.join(unsupported)}"
                    )
        elif isinstance(necessity, dict) and necessity.get("kind") == "PREREQUISITE":
            if set(necessity) != {"kind", "reason", "market_context_ids"}:
                errors.append(
                    f"{lesson_id}: PREREQUISITE evidence needs kind, reason, and market_context_ids"
                )
            reason = necessity.get("reason")
            context_ids = necessity.get("market_context_ids")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{lesson_id}: PREREQUISITE evidence needs a reason")
            if not isinstance(context_ids, list) or not context_ids or not all(
                isinstance(value, str) for value in context_ids
            ):
                errors.append(
                    f"{lesson_id}: PREREQUISITE evidence needs non-empty market_context_ids"
                )
            else:
                if len(context_ids) != len(set(context_ids)):
                    errors.append(
                        f"{lesson_id}: PREREQUISITE market_context_ids contain duplicates"
                    )
                unknown_context = sorted(set(context_ids) - set(market_keywords))
                missing_context = sorted(set(context_ids) - set(frequency))
                if unknown_context:
                    errors.append(
                        f"{lesson_id}: unknown PREREQUISITE market context id(s): "
                        f"{', '.join(unknown_context)}"
                    )
                if missing_context:
                    errors.append(
                        f"{lesson_id}: PREREQUISITE context is absent from the audit: "
                        f"{', '.join(missing_context)}"
                    )
        elif isinstance(necessity, dict):
            errors.append(f"{lesson_id}: necessity_evidence kind is invalid")

        source_claims = entry.get("source_claims")
        if not isinstance(source_claims, list) or not source_claims:
            errors.append(f"{lesson_id}: source_claims must be a non-empty list")
        else:
            for claim in source_claims:
                if not isinstance(claim, dict):
                    errors.append(f"{lesson_id}: source claim must be an object")
                    continue
                if not all(
                    isinstance(claim.get(key), str) and claim[key].strip()
                    for key in ("claim", "url", "revision", "revision_url", "reviewed_at")
                ):
                    errors.append(
                        f"{lesson_id}: source claim needs claim, url, revision, "
                        "revision_url, and reviewed_at"
                    )
                elif not claim["url"].startswith("https://") or not claim[
                    "revision_url"
                ].startswith("https://"):
                    errors.append(f"{lesson_id}: source claim URLs must use HTTPS")
                elif not is_immutable_revision_url(claim["revision_url"]):
                    errors.append(
                        f"{lesson_id}: source claim revision_url must pin a version, tag, or commit"
                    )
                else:
                    try:
                        reviewed_date = date.fromisoformat(claim["reviewed_at"])
                    except ValueError:
                        errors.append(
                            f"{lesson_id}: source claim reviewed_at must be a valid YYYY-MM-DD date"
                        )
                    else:
                        if reviewed_date > date.today():
                            errors.append(
                                f"{lesson_id}: source claim reviewed_at must not be in the future"
                            )
                        source_review_dates.append((lesson_id, reviewed_date))

        lab = entry.get("lab")
        if not isinstance(lab, dict) or not all(
            isinstance(lab.get(key), str) and lab[key].strip()
            for key in ("path", "verify_command")
        ):
            errors.append(f"{lesson_id}: lab path and verify_command are required")
        elif not lab["path"].startswith("lab/") or not lab["verify_command"].startswith(
            "./lab/gradlew"
        ):
            errors.append(f"{lesson_id}: lab contract must use the pinned lab Gradle wrapper")
        elif (
            Path(lab["path"]).is_absolute()
            or ".." in Path(lab["path"]).parts
            or (available_lab_paths is not None and lab["path"] not in available_lab_paths)
        ):
            errors.append(f"{lesson_id}: lab path must resolve to a current tracked lab file")
        if not isinstance(lab, dict) or not isinstance(lab.get("test_ids"), list) or not lab.get("test_ids"):
            errors.append(f"{lesson_id}: lab test_ids must be a non-empty list")
            test_ids: list[str] = []
        else:
            test_ids = lab["test_ids"]
            if not all(isinstance(test_id, str) and LAB_TEST_ID_RE.fullmatch(test_id) for test_id in test_ids):
                errors.append(f"{lesson_id}: lab test_ids must use stable LAB-*-NNN ids")
            if len(test_ids) != len(set(test_ids)):
                errors.append(f"{lesson_id}: lab test_ids contain duplicates")
            reused = sorted(set(test_ids) & assigned_test_ids)
            if reused:
                errors.append(f"{lesson_id}: lab test id reused by another lesson: {', '.join(reused)}")
            assigned_test_ids.update(test_ids)
            if test_id_counts is not None:
                missing_or_duplicate = [
                    test_id for test_id in test_ids if test_id_counts.get(test_id, 0) != 1
                ]
                if missing_or_duplicate:
                    errors.append(
                        f"{lesson_id}: lab test id must occur exactly once in source: "
                        f"{', '.join(missing_or_duplicate)}"
                    )
        expected_assertions = lab.get("expected_assertions") if isinstance(lab, dict) else None
        if not isinstance(expected_assertions, list) or not expected_assertions or not all(
            isinstance(assertion, str) and assertion.strip()
            for assertion in expected_assertions
        ):
            errors.append(
                f"{lesson_id}: expected_assertions must contain non-empty strings"
            )
        elif len(expected_assertions) != len(test_ids):
            errors.append(
                f"{lesson_id}: expected_assertions must map one-to-one to test_ids"
            )

        contracts[lesson_id] = lesson_contract(
            lessons[lesson_id], entry, profile, taxonomy, job_market, lab_revision
        )

    if len(core_entries) > 16:
        errors.append("Core curriculum must have at most 16 lessons")
    if core_entries:
        jvm_count = sum(entry.get("core_type") == "JVM_CORE" for entry in core_entries)
        if jvm_count / len(core_entries) < 0.70:
            errors.append("JVM_CORE ratio must be at least 70 percent")
    missing_coverage = sorted(set(required) - covered)
    if missing_coverage:
        errors.append(f"Core competency gap(s): {', '.join(missing_coverage)}")

    if manifest.get("profile_id") != profile_id:
        errors.append("Verification manifest profile_id does not match")
    if manifest.get("lab_revision") != lab_revision:
        errors.append("Verification manifest lab_revision does not match current lab contents")
    manifest_lessons = manifest.get("lessons")
    if not isinstance(manifest_lessons, dict):
        errors.append("Verification manifest lessons must be an object")
        manifest_lessons = {}
    unknown_manifest_lessons = sorted(set(manifest_lessons) - set(entries))
    if unknown_manifest_lessons:
        errors.append(
            f"Unknown verification manifest lesson(s): {', '.join(unknown_manifest_lessons)}"
        )

    verified_at = manifest.get("verified_at")
    verified_date: date | None = None
    try:
        verified_date = date.fromisoformat(str(verified_at))
        profile_date = date.fromisoformat(str(profile.get("created_at")))
        if verified_date < profile_date:
            errors.append("Verification manifest predates the verification profile")
        if profile_date > date.today() or verified_date > date.today():
            errors.append("Verification profile and manifest dates must not be in the future")
        job_checked_date = date.fromisoformat(str(job_market.get("checked_at")))
        if verified_date < job_checked_date:
            errors.append("Verification manifest predates the job-market audit")
    except ValueError:
        errors.append(
            "Verification manifest, profile, and job-market dates must be valid ISO dates"
        )
    if verified_date is not None:
        for lesson_id, reviewed_date in source_review_dates:
            if reviewed_date > verified_date:
                errors.append(
                    f"{lesson_id}: source claim review postdates the verification manifest"
                )

    commands = manifest.get("commands")
    if not isinstance(commands, list) or not commands or not all(
        isinstance(command, str) and command.strip() for command in commands
    ):
        errors.append("Verification manifest commands must be a non-empty string list")
        commands = []
    runtime_version = str(profile.get("jdk", {}).get("version", ""))
    runtime_tag = runtime_version.removesuffix("-LTS").replace("+", "_")
    docker_commands = [command for command in commands if "docker run" in command]
    if not any(
        "--platform linux/amd64" in command
        and f"eclipse-temurin:{runtime_tag}-jdk" in command
        and "-v \"$PWD:/workspace\"" in command
        and "-w /workspace" in command
        and "clean test" in command
        and "--no-build-cache" in command
        for command in docker_commands
    ):
        errors.append("Verification manifest lacks a reproducible exact-JDK clean-test command")
    if not any(
        "postgresTest" in command and "--rerun-tasks" in command
        for command in commands
    ):
        errors.append("Verification manifest lacks a rerun PostgreSQL test command")

    verified: list[str] = []
    stale: list[str] = []
    for entry in core_entries:
        lesson_id = str(entry["id"])
        record = manifest_lessons.get(lesson_id)
        expected_test_ids = set(entry.get("lab", {}).get("test_ids", []))
        valid_assertions = (
            isinstance(record, dict)
            and isinstance(record.get("assertions"), dict)
            and bool(record["assertions"])
            and set(record["assertions"]) == expected_test_ids
            and all(value == "PASS" for value in record["assertions"].values())
        )
        if (
            isinstance(record, dict)
            and record.get("status") == "VERIFIED"
            and record.get("contract_hash") == contracts.get(lesson_id)
            and valid_assertions
        ):
            verified.append(lesson_id)
        else:
            stale.append(lesson_id)
    if stale:
        errors.append(f"Core lesson(s) are not VERIFIED: {', '.join(sorted(stale))}")

    expected_runtime = profile.get("jdk", {}).get("version")
    if expected_runtime and manifest.get("verification_runtime") != expected_runtime:
        errors.append("Verification manifest runtime does not match the exact profile JDK build")

    return {
        "profile_id": profile_id,
        "lab_revision": lab_revision,
        "core_count": len(core_entries),
        "jvm_core_count": sum(
            entry.get("core_type") == "JVM_CORE" for entry in core_entries
        ),
        "verified_lesson_ids": sorted(verified),
        "stale_lesson_ids": sorted(stale),
        "contracts": contracts,
        "errors": errors,
        "valid": not errors,
    }


def verify_paths(
    backend_path: Path = BACKEND_CONFIG,
    matrix_path: Path = MATRIX_CONFIG,
    profile_path: Path = PROFILE_CONFIG,
    taxonomy_path: Path = TAXONOMY_CONFIG,
    manifest_path: Path = MANIFEST_FILE,
    lab_dir: Path = LAB_DIR,
    job_market_path: Path = JOB_MARKET_AUDIT,
) -> dict[str, Any]:
    profile = read_object(profile_path)
    return evaluate_curriculum(
        read_object(backend_path),
        read_object(matrix_path),
        profile,
        read_object(taxonomy_path),
        read_object(job_market_path),
        read_object(manifest_path),
        calculate_lab_revision(lab_dir),
        lab_test_id_counts(lab_dir),
        validate_lab_profile(lab_dir, profile),
        lab_source_paths(lab_dir),
    )


def main() -> int:
    args = parse_args()
    try:
        summary = verify_paths(
            args.backend_config,
            args.matrix,
            args.profile,
            args.taxonomy,
            args.manifest,
            args.lab,
            args.job_market_audit,
        )
    except (OSError, RuntimeError) as exc:
        print(f"Curriculum verification failed: {exc}", file=sys.stderr)
        return 1

    output = summary if args.emit_contracts else {
        key: value for key, value in summary.items() if key != "contracts"
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
