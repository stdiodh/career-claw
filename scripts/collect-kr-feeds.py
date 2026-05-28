#!/usr/bin/env python3
"""Collect Korean Career Feed candidates from Naver Search and RSS."""

from __future__ import annotations

import argparse
import difflib
import email.utils
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
NAVER_CLIENT_ID_ENV = "NAVER_CLIENT_ID"
NAVER_CLIENT_SECRET_ENV = "NAVER_CLIENT_SECRET"
GITHUB_TOKEN_ENV_NAMES = ("GITHUB_TOKEN", "GH_TOKEN")
REQUEST_TIMEOUT_SECONDS = 20
SUMMARY_LIMIT = 240
OSS_SUMMARY_LIMIT = 300
TITLE_LIMIT = 240
DEFAULT_DISPLAY = 10
MAX_DISPLAY = 20
DEFAULT_MAX_CANDIDATES = 30
OSS_REPOSITORIES_CONFIG_PATH = Path("configs/oss-repositories.json")
PS_CURRICULUM_PATH = Path("configs/programmers-ps-curriculum.json")
PS_PROGRESS_PATH = Path("data/ps-progress.json")
PS_ROUTINE_OUTPUT_PATH = Path("reports/candidates/ps-weekly-routine.json")
COMPANY_CAREER_WATCHLIST_PATH = Path("configs/company-career-watchlist.json")
BACKEND_PRACTICAL_CURRICULUM_PATH = Path(
    "configs/backend-practical-knowledge-curriculum.json"
)
BACKEND_PRACTICAL_OUTPUT_PATH = Path(
    "reports/candidates/backend-practical-knowledge.json"
)
USER_AGENT = "career-feed-kr-collector"
SUPPORTED_FEED_TYPES = {"rss", "atom"}
OSS_CATEGORY_ID = "kr-oss-contribution-opportunities"
AI_TECH_CATEGORY_ID = "kr-ai-tech-news"
BACKEND_TECH_CATEGORY_ID = "kr-backend-tech-news"
WEEKLY_CAREER_CATEGORY_ID = "kr-backend-career-events"
WEEKLY_CAREER_SPLIT_OUTPUTS = {
    "intern_job": Path("reports/candidates/kr-backend-intern-jobs.json"),
    "entry_job": Path("reports/candidates/kr-backend-entry-jobs.json"),
    "junior_job": Path("reports/candidates/kr-backend-entry-jobs.json"),
    "hackathon": Path("reports/candidates/kr-backend-career-activities.json"),
    "contest": Path("reports/candidates/kr-backend-career-activities.json"),
    "competition": Path("reports/candidates/kr-backend-career-activities.json"),
    "company_watchlist": Path("reports/candidates/kr-backend-company-watchlist.json"),
}
WEEKLY_CAREER_EMPTY_OUTPUTS = [
    Path("reports/candidates/kr-backend-intern-jobs.json"),
    Path("reports/candidates/kr-backend-entry-jobs.json"),
    Path("reports/candidates/kr-backend-career-activities.json"),
    Path("reports/candidates/kr-backend-company-watchlist.json"),
]
DAILY_TECH_ALIAS_OUTPUTS = {
    AI_TECH_CATEGORY_ID: ("kr-dev-ai-news", Path("reports/candidates/kr-dev-ai-news.json")),
    BACKEND_TECH_CATEGORY_ID: (
        "spring-study-topic",
        Path("reports/candidates/spring-study-topic.json"),
    ),
}
RELIABILITY_SCORE = {
    "official": 20,
    "major_media": 12,
    "platform": 10,
    "aggregator": 5,
    "unknown": 0,
}
MODE_CATEGORY_IDS = {
    "daily-tech": {AI_TECH_CATEGORY_ID, BACKEND_TECH_CATEGORY_ID, OSS_CATEGORY_ID},
    "weekly-career": {WEEKLY_CAREER_CATEGORY_ID},
}
BACKEND_KEYWORDS = [
    "backend",
    "백엔드",
    "서버",
    "api",
    "spring",
    "java",
    "kotlin",
    "db",
    "database",
    "postgresql",
    "redis",
    "kafka",
    "kubernetes",
    "msa",
]
KOTLIN_SPRING_KEYWORDS = ["kotlin", "spring", "spring boot", "java"]
STUDENT_KEYWORDS = [
    "인턴",
    "신입",
    "주니어",
    "대학생",
    "졸업",
    "채용연계형",
    "해커톤",
    "공모전",
    "경진대회",
]
ACTION_KEYWORDS = [
    "지원",
    "접수",
    "모집",
    "참가",
    "신청",
    "마감",
    "업데이트",
    "출시",
    "발표",
    "패치",
    "취약점",
]
SECURITY_ACTION_KEYWORDS = ["취약점", "cve", "보안 업데이트", "패치", "공급망", "랜섬웨어"]
EXPIRED_DEADLINE_KEYWORDS = ["마감 종료", "접수 종료", "모집 종료", "지원 종료", "마감됨"]
SENIOR_ONLY_KEYWORDS = ["시니어", "senior", "경력 3년", "경력 5년", "3년 이상", "5년 이상"]
FRONTEND_MARKETING_KEYWORDS = ["프론트엔드", "frontend", "디자인", "마케팅", "기획자"]
CAREER_EXCLUSION_KEYWORDS = [
    "부트캠프",
    "교육",
    "강의",
    "서포터즈",
    "마케터",
    "영업",
    "pm",
]
CAREER_TECH_KEYWORDS = [
    "Java",
    "Kotlin",
    "Spring Boot",
    "Spring",
    "REST API",
    "API",
    "DB",
    "MySQL",
    "PostgreSQL",
    "Redis",
    "Kafka",
    "AWS",
    "Docker",
    "Kubernetes",
    "AI API",
    "LLM",
    "Python",
]
PORTFOLIO_KEYWORDS = [
    "github",
    "깃허브",
    "배포",
    "결과물",
    "발표",
    "api",
    "db",
    "데이터",
    "ai",
    "서비스",
    "해커톤",
]
GENERIC_CAREER_URLS = {
    "https://www.wanted.co.kr",
    "https://www.wanted.co.kr/",
    "https://dacon.io/competitions",
    "https://linkareer.com",
    "https://linkareer.com/",
    "https://www.saramin.co.kr",
    "https://www.saramin.co.kr/",
    "https://www.saramin.co.kr/zf_user",
    "https://www.saramin.co.kr/zf_user/",
    "https://www.jobkorea.co.kr",
    "https://www.jobkorea.co.kr/",
    "https://programmers.co.kr",
    "https://programmers.co.kr/",
    "https://aifactory.space",
    "https://aifactory.space/",
    "https://www.wevity.com",
    "https://www.wevity.com/",
    "https://www.all-con.co.kr",
    "https://www.all-con.co.kr/",
}
OSS_BEGINNER_KEYWORDS = [
    "documentation",
    "docs",
    "sample",
    "example",
    "test",
    "reproducer",
    "repro",
    "typo",
    "validation",
]
OSS_BEGINNER_TRIAGE_LABELS = [
    "first-timers-only",
    "for: first-timers-only",
    "good first issue",
    "help wanted",
    "status: ideal-for-contribution",
    "good first contribution",
]
OSS_DIRECT_SPRING_KEYWORDS = [
    "Spring Boot",
    "JPA",
    "JDBC",
    "Spring Security",
    "Spring AI",
    "Spring Framework",
    "Spring Data",
    "PetClinic",
    "spring-boot",
    "spring-framework",
    "spring-data-jpa",
    "spring-data-relational",
    "spring-data-commons",
    "spring-security",
    "spring-ai",
    "spring-petclinic",
]
OSS_MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
OSS_SECURITY_KEYWORDS = ["security vulnerability", "CVE"]
OSS_RELEASE_BLOCKER_KEYWORDS = ["release blocker"]
OSS_DEEP_INTERNALS_KEYWORDS = [
    "deep internals",
    "compiler",
    "runtime internals",
    "compiler backend",
    "IR backend",
]
OSS_DESIGN_KEYWORDS = ["design proposal", "RFC", "epic", "requires design"]
OSS_DUPLICATE_KEYWORDS = ["duplicate", "invalid", "superseded"]
OSS_MAJOR_API_KEYWORDS = ["major API", "breaking change"]
OSS_BLOCKED_LABEL_TITLE_KEYWORDS = [
    "security",
    "CVE",
    "release blocker",
    "breaking change",
    "major API",
    "deep internals",
]
OSS_CLAIM_KEYWORDS = [
    "I'll take this",
    "I will take this",
    "I'm working on this",
    "I am working on this",
    "working on this",
    "I can work on this",
    "assign me",
    "please assign",
    "제가 해보겠습니다",
    "작업하겠습니다",
    "제가 맡겠습니다",
    "제가 진행해보겠습니다",
]
OSS_PREFERRED_CONTRIBUTION_TYPES = {"docs", "test", "bug-repro", "sample"}


@dataclass(frozen=True)
class Candidate:
    category: str
    title: str
    url: str
    source_url: str
    source: str
    publisher: str
    published_at: datetime | None
    summary: str
    query: str
    korea_relevance: str
    developer_relevance: str
    source_reliability: str
    tags: list[str]
    persona_fit_score: int
    backend_fit_score: int
    kotlin_spring_fit_score: int
    student_fit_score: int
    deadline_urgency_score: int
    source_reliability_score: int
    actionability_score: int
    security_action_required: bool
    exclude_reason: str
    score: int


@dataclass(frozen=True)
class OssIssueCandidate:
    category: str
    title: str
    url: str
    source_url: str
    source: str
    repository: str
    issue_number: int
    author: str
    author_association: str
    maintainer_authored: bool
    labels: list[str]
    state: str
    assignees: list[str]
    assignees_count: int
    has_assignee: bool
    comments: int
    comments_count: int
    has_claim_comment: bool
    claim_comment_check: str
    linked_prs_count: int
    linked_branches_count: int
    linked_work_check: str
    has_linked_work: bool
    comments_checked_count: int
    created_at: datetime | None
    updated_at: datetime | None
    summary: str
    contribution_type: str
    junior_fit_score: int
    backend_fit_score: int
    kotlin_spring_fit_score: int
    first_pr_potential_score: int
    risk_score: int
    exclude_reason: str
    difficulty_band: str
    why_beginner_friendly: str
    first_30_min_action: str
    pre_contribution_etiquette: str
    claim_comment_author: str
    safe_to_recommend: bool
    status_check: str
    risk_reason: str
    score: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Career Feed candidates from Korean sources."
    )
    parser.add_argument("--config", default="configs/kr-sources.json")
    parser.add_argument("--output-dir", default="reports/candidates")
    parser.add_argument(
        "--category",
        default="all",
        help="Category id to collect, or 'all'.",
    )
    parser.add_argument(
        "--mode",
        choices=["daily-tech", "weekly-career"],
        default="daily-tech",
        help="Collection mode for Career Feed workflows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and write empty schema files without network/API calls.",
    )
    return parser.parse_args()


def now_kst() -> datetime:
    return datetime.now(tz=KST)


def format_kst(value: datetime) -> str:
    return value.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S KST")


def strip_html(value: str) -> str:
    unescaped = html.unescape(value or "")
    without_tags = re.sub(r"<[^>]+>", " ", unescaped)
    return " ".join(without_tags.split())


def truncate_text(value: str, limit: int) -> str:
    cleaned = " ".join((value or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: max(limit - 3, 0)].rstrip()}..."


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None

    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        try:
            parsed = email.utils.parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(KST)


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlsplit((url or "").strip())
    if not parsed.scheme and not parsed.netloc:
        return ""
    path = parsed.path.rstrip("/") or parsed.path
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, "")
    )


def normalize_title(title: str) -> str:
    lowered = html.unescape(title or "").lower()
    normalized = re.sub(r"[\W_]+", " ", lowered, flags=re.UNICODE)
    return " ".join(normalized.split())


def title_is_duplicate(title: str, seen_titles: list[str]) -> bool:
    normalized = normalize_title(title)
    if not normalized:
        return True
    for seen in seen_titles:
        if normalized == seen:
            return True
        if difflib.SequenceMatcher(None, normalized, seen).ratio() >= 0.9:
            return True
    return False


def load_config(path: Path, category_filter: str, mode_filter: str) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    categories = data.get("categories", [])
    if not isinstance(categories, list):
        raise RuntimeError("configs/kr-sources.json must contain a categories array.")

    selected = []
    mode_category_ids = MODE_CATEGORY_IDS.get(mode_filter, set())
    for category in categories:
        if not isinstance(category, dict):
            continue
        category_id = str(category.get("id", "")).strip()
        if not category_id:
            continue
        if category_filter != "all" and category_id != category_filter:
            continue
        if category_id not in mode_category_ids:
            continue
        selected.append(category)

    if category_filter != "all" and not selected:
        raise RuntimeError(f"Unknown KR category or mode mismatch: {category_filter}")

    return {**data, "categories": selected}


def get_naver_credentials(dry_run: bool) -> tuple[str, str] | None:
    client_id = os.environ.get(NAVER_CLIENT_ID_ENV, "").strip()
    client_secret = os.environ.get(NAVER_CLIENT_SECRET_ENV, "").strip()
    if client_id and client_secret:
        return client_id, client_secret

    if dry_run:
        print(
            "Dry-run: NAVER_CLIENT_ID/NAVER_CLIENT_SECRET not required; "
            "Naver API collection skipped."
        )
        return None

    missing = [
        name
        for name, value in (
            (NAVER_CLIENT_ID_ENV, client_id),
            (NAVER_CLIENT_SECRET_ENV, client_secret),
        )
        if not value
    ]
    print(
        "Warning: missing optional environment variable(s): "
        f"{', '.join(missing)}. Naver News Search API collection skipped; "
        "RSS/reference candidates will still be collected.",
        file=sys.stderr,
    )
    return None


def get_github_token() -> str | None:
    for env_name in GITHUB_TOKEN_ENV_NAMES:
        token = os.environ.get(env_name, "").strip()
        if token:
            return token
    print(
        "Warning: GITHUB_TOKEN/GH_TOKEN is not set. "
        "GitHub Issues collection will use the public unauthenticated API "
        "and may hit rate limits.",
        file=sys.stderr,
    )
    return None


def load_oss_repositories_config(path: Path = OSS_REPOSITORIES_CONFIG_PATH) -> dict[str, object]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("configs/oss-repositories.json must contain a JSON object.")
    return data


def category_values(category: dict[str, object], key: str) -> list[str]:
    raw_values = category.get(key, [])
    if not isinstance(raw_values, list):
        return []
    return [str(value).strip() for value in raw_values if str(value).strip()]


def configured_repositories(
    category: dict[str, object],
    oss_config: dict[str, object],
) -> list[str]:
    repositories = category_values(oss_config, "repositories")
    if repositories:
        return repositories
    return category_values(category, "github_repositories")


def difficulty_model_values(
    difficulty_model: dict[str, object],
    band: str,
    key: str,
) -> list[str]:
    model = difficulty_model.get(band, {})
    if not isinstance(model, dict):
        return []
    return category_values(model, key)


def write_json_file(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def load_required_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise RuntimeError(f"Required file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return data


def text_contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords if keyword)


def count_matches(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword and keyword.lower() in lowered)


def keyword_fit_score(text: str, keywords: list[str], points_per_match: int, limit: int) -> int:
    return min(count_matches(text, keywords) * points_per_match, limit)


def contains_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text or ""))


def domain_from_url(url: str) -> str:
    netloc = urllib.parse.urlsplit(url or "").netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def domain_matches(domain: str, candidates: list[str]) -> bool:
    return any(domain == candidate or domain.endswith(f".{candidate}") for candidate in candidates)


def career_text(candidate: Candidate) -> str:
    return " ".join(
        part
        for part in (
            candidate.title,
            candidate.summary,
            candidate.publisher,
            candidate.source,
            candidate.query,
        )
        if part
    )


def source_label_for_url(url: str, fallback: str) -> str:
    domain = domain_from_url(url)
    labels = {
        "linkareer.com": "Linkareer",
        "jobkorea.co.kr": "JobKorea",
        "saramin.co.kr": "Saramin",
        "wanted.co.kr": "Wanted",
        "jumpit.co.kr": "Jumpit",
        "yw.work24.go.kr": "Work24",
        "zero-base.co.kr": "ZeroBase",
        "dacon.io": "DACON",
        "aifactory.space": "AI Factory",
        "programmers.co.kr": "Programmers",
        "school.programmers.co.kr": "Programmers",
        "wevity.com": "Wevity",
        "all-con.co.kr": "All-Con",
        "recruit.navercorp.com": "NAVER Careers",
        "careers.kakao.com": "Kakao Careers",
        "careers.linecorp.com": "LINE Careers",
        "coupang.jobs": "Coupang Jobs",
        "career.woowahan.com": "Woowa Careers",
        "toss.im": "Toss Careers",
        "about.daangn.com": "Daangn Careers",
    }
    for candidate_domain, label in labels.items():
        if domain_matches(domain, [candidate_domain]):
            return label
    return fallback or domain or "unknown"


def is_generic_career_url(url: str) -> bool:
    normalized = normalize_url(url)
    if not normalized:
        return True
    if normalized.rstrip("/") in {item.rstrip("/") for item in GENERIC_CAREER_URLS}:
        return True

    parsed = urllib.parse.urlsplit(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    path = parsed.path.rstrip("/")
    query = parsed.query.lower()

    if path in {"", "/"}:
        return True
    if domain_matches(domain, ["wanted.co.kr"]) and path in {"", "/wdlist", "/search"}:
        return True
    if domain_matches(domain, ["dacon.io"]) and path == "/competitions":
        return True
    if domain_matches(domain, ["linkareer.com"]) and (
        path in {"", "/list"} or path.startswith("/list/")
    ):
        return True
    if domain_matches(domain, ["saramin.co.kr"]) and (
        path in {"", "/zf_user"} or path.startswith("/zf_user/jobs/list")
    ):
        return True
    if domain_matches(domain, ["jobkorea.co.kr"]) and (
        path in {"", "/Recruit/List"} or path.startswith("/Recruit/List")
    ):
        return True
    if domain_matches(domain, ["programmers.co.kr"]) and path in {"", "/"}:
        return True
    if domain_matches(domain, ["aifactory.space"]) and path in {"", "/competition"}:
        return True
    if domain_matches(domain, ["wevity.com", "all-con.co.kr", "jumpit.co.kr"]) and path in {
        "",
        "/",
    }:
        return True
    if domain_matches(domain, ["yw.work24.go.kr"]) and "selectwkexprgmlist" in path.lower():
        return True
    if domain_matches(domain, ["careers.kakao.com"]) and path == "/jobs" and "jobid" not in query:
        return True
    if domain_matches(domain, ["recruit.navercorp.com"]) and path.lower().endswith("/list.do"):
        return True
    if domain_matches(domain, ["careers.linecorp.com"]) and path in {"/ko/jobs", "/en/jobs"}:
        return True
    if domain_matches(domain, ["coupang.jobs"]) and path in {"/en/jobs", "/ko/jobs", "/jobs"}:
        return True
    if domain_matches(domain, ["career.woowahan.com"]) and path in {"", "/", "/jobs"}:
        return True
    if domain_matches(domain, ["toss.im"]) and path in {"/career", "/career/"}:
        return True
    if domain_matches(domain, ["about.daangn.com"]) and path in {"/jobs", "/jobs/"}:
        return True
    return False


def extract_deadline_time(text: str) -> tuple[int, int] | None:
    match = re.search(r"(\d{1,2})\s*:\s*(\d{2})", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.search(r"(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분)?", text)
    if match:
        return int(match.group(1)), int(match.group(2) or 0)
    return None


def deadline_payload_from_date(
    year: int,
    month: int,
    day: int,
    text: str,
    current_time: datetime,
) -> dict[str, object] | None:
    try:
        hour_minute = extract_deadline_time(text)
        if hour_minute:
            deadline = datetime(year, month, day, hour_minute[0], hour_minute[1], tzinfo=KST)
            deadline_text = deadline.strftime("%Y-%m-%d %H:%M KST")
            deadline_value = deadline.strftime("%Y-%m-%d %H:%M:%S KST")
        else:
            deadline = datetime(year, month, day, 23, 59, tzinfo=KST)
            deadline_text = deadline.strftime("%Y-%m-%d KST")
            deadline_value = deadline.strftime("%Y-%m-%d KST")
    except ValueError:
        return None

    today = current_time.astimezone(KST).date()
    days = (deadline.date() - today).days
    status = "closed" if deadline < current_time.astimezone(KST) else "open"
    return {
        "deadline": deadline_value,
        "deadline_text": deadline_text,
        "deadline_status": status,
        "days_until_deadline": days,
    }


def parse_korean_deadline(text: str, current_time: datetime) -> dict[str, object]:
    searchable = strip_html(text)
    lowered = searchable.lower()
    if text_contains_any(searchable, EXPIRED_DEADLINE_KEYWORDS):
        return {
            "deadline": "",
            "deadline_text": "마감 종료",
            "deadline_status": "closed",
            "days_until_deadline": None,
        }
    if text_contains_any(searchable, ["상시채용", "상시 모집", "상시지원", "상시 영입"]):
        return {
            "deadline": "상시채용",
            "deadline_text": "상시채용",
            "deadline_status": "rolling",
            "days_until_deadline": None,
        }
    if text_contains_any(
        searchable,
        ["채용 시 마감", "채용시 마감", "영입종료시", "채용 완료 시", "채용 완료시"],
    ):
        return {
            "deadline": "채용 시 마감",
            "deadline_text": "채용 시 마감",
            "deadline_status": "until_filled",
            "days_until_deadline": None,
        }

    d_day = re.search(r"\bD\s*-\s*(\d{1,3})\b", searchable, flags=re.IGNORECASE)
    if d_day:
        days = int(d_day.group(1))
        deadline = current_time.astimezone(KST) + timedelta(days=days)
        return {
            "deadline": deadline.strftime("%Y-%m-%d 23:59:00 KST"),
            "deadline_text": deadline.strftime("%Y-%m-%d 23:59 KST"),
            "deadline_status": "open",
            "days_until_deadline": days,
        }

    full_date_patterns = [
        r"(20\d{2})\s*[.\-/년]\s*(\d{1,2})\s*[.\-/월]\s*(\d{1,2})",
        r"(20\d{2})(\d{2})(\d{2})",
    ]
    for pattern in full_date_patterns:
        match = re.search(pattern, searchable)
        if not match:
            continue
        parsed = deadline_payload_from_date(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            searchable,
            current_time,
        )
        if parsed:
            return parsed

    month_day_patterns = [
        r"(?:~|마감|접수|지원|모집|까지|기간|일정)?\s*(\d{1,2})\s*[./]\s*(\d{1,2})",
        r"(\d{1,2})\s*월\s*(\d{1,2})\s*일",
    ]
    for pattern in month_day_patterns:
        match = re.search(pattern, searchable)
        if not match:
            continue
        year = current_time.astimezone(KST).year
        month = int(match.group(1))
        day = int(match.group(2))
        parsed = deadline_payload_from_date(year, month, day, searchable, current_time)
        if parsed and parsed["deadline_status"] == "closed":
            parsed = deadline_payload_from_date(year + 1, month, day, searchable, current_time)
        if parsed:
            return parsed

    if "마감임박" in lowered:
        return {
            "deadline": "",
            "deadline_text": "원문 확인 필요",
            "deadline_status": "unknown",
            "days_until_deadline": None,
        }
    return {
        "deadline": "",
        "deadline_text": "원문 확인 필요",
        "deadline_status": "unknown",
        "days_until_deadline": None,
    }


def infer_company_or_host(text: str, candidate: Candidate) -> str:
    known_names = [
        ("NAVER", ["naver", "네이버"]),
        ("Kakao", ["kakao", "카카오"]),
        ("LINE", ["line", "라인"]),
        ("Coupang", ["coupang", "쿠팡"]),
        ("우아한형제들", ["우아한형제들", "배달의민족", "woowa"]),
        ("Toss", ["toss", "토스"]),
        ("당근", ["daangn", "당근"]),
        ("DACON", ["dacon", "데이콘"]),
        ("AI Factory", ["aifactory", "인공지능팩토리", "ai factory"]),
        ("Programmers", ["programmers", "프로그래머스"]),
        ("Linkareer", ["linkareer", "링커리어"]),
        ("ZeroBase", ["zerobase", "zero intern", "제로베이스"]),
    ]
    lowered = text.lower()
    for label, keywords in known_names:
        if any(keyword.lower() in lowered for keyword in keywords):
            return label
    if candidate.publisher and "." not in candidate.publisher:
        return candidate.publisher
    source_label = source_label_for_url(candidate.url, candidate.source)
    return source_label if source_label != "Naver News Search" else candidate.publisher


def classify_career_sub_category(candidate: Candidate) -> str:
    text = career_text(candidate)
    lowered = text.lower()
    if candidate.query == "company_watchlist":
        return "company_watchlist"
    if text_contains_any(text, ["해커톤", "hackathon"]):
        return "hackathon"
    if text_contains_any(text, ["경진대회", "competition", "데이터 대회", "ai 대회"]):
        return "competition"
    if text_contains_any(text, ["공모전", "contest"]):
        return "contest"
    if text_contains_any(text, ["인턴", "intern", "채용연계형", "전환형", "zero intern"]):
        return "intern_job"
    if text_contains_any(text, ["주니어", "junior"]):
        return "junior_job"
    if text_contains_any(text, ["신입", "new grad", "entry"]):
        return "entry_job"
    if "recruit" in lowered or "career" in lowered:
        return "company_watchlist"
    return "entry_job"


def career_type_for_sub_category(sub_category: str) -> str:
    return {
        "intern_job": "인턴",
        "entry_job": "신입",
        "junior_job": "주니어",
        "hackathon": "해커톤",
        "contest": "공모전",
        "competition": "경진대회",
        "company_watchlist": "신입",
    }.get(sub_category, "신입")


def infer_career_role(text: str, career_type: str) -> str:
    if career_type in {"해커톤", "공모전", "경진대회"}:
        if text_contains_any(text, ["ai", "인공지능", "llm"]):
            return "AI 서비스 백엔드"
        if text_contains_any(text, ["데이터", "data"]):
            return "데이터 수집/API 서버 개발"
        return "API 서버 개발"
    if text_contains_any(text, ["server", "서버"]):
        return "서버 개발"
    if text_contains_any(text, ["backend", "백엔드"]):
        return "백엔드 개발"
    return "백엔드 개발"


def infer_target(text: str, career_type: str) -> str:
    if text_contains_any(text, ["졸업예정", "졸업 예정"]):
        return "졸업예정자 가능"
    if text_contains_any(text, ["대학생", "재학생"]):
        return "대학생 참여 가능"
    if text_contains_any(text, ["신입", "new grad", "entry"]):
        return "신입 지원 가능"
    if text_contains_any(text, ["인턴", "intern"]):
        return "인턴 가능"
    if career_type in {"해커톤", "공모전", "경진대회"}:
        return "팀 참가 가능"
    return "원문에서 지원 조건 확인"


def infer_process_or_deliverable(text: str, career_type: str) -> list[str]:
    if career_type in {"해커톤", "공모전", "경진대회"}:
        deliverables = []
        if text_contains_any(text, ["github", "깃허브"]):
            deliverables.append("GitHub")
        if text_contains_any(text, ["발표", "ppt"]):
            deliverables.append("발표자료")
        if text_contains_any(text, ["url", "배포", "서비스", "결과물"]):
            deliverables.append("결과물 URL")
        return deliverables or ["기획서", "GitHub", "발표자료"]

    process = []
    if text_contains_any(text, ["서류", "이력서", "resume"]):
        process.append("서류")
    if text_contains_any(text, ["코딩테스트", "coding test", "과제"]):
        process.append("코딩테스트" if "과제" not in text else "과제")
    if text_contains_any(text, ["면접", "interview"]):
        process.append("면접")
    return process or ["원문에서 전형 확인"]


def infer_tech_keywords(text: str) -> list[str]:
    matched = []
    for keyword in CAREER_TECH_KEYWORDS:
        if keyword.lower() in text.lower() and keyword not in matched:
            matched.append(keyword)
    if matched:
        return matched[:6]
    if text_contains_any(text, ["백엔드", "backend", "서버", "api"]):
        return ["백엔드", "API", "DB"]
    return []


def is_backend_career_candidate(candidate: Candidate) -> bool:
    return text_contains_any(career_text(candidate), BACKEND_KEYWORDS)


def is_entry_or_intern_candidate(candidate: Candidate) -> bool:
    return text_contains_any(career_text(candidate), STUDENT_KEYWORDS + ["new grad", "entry"])


def is_portfolio_activity_candidate(candidate: Candidate) -> bool:
    text = career_text(candidate)
    return text_contains_any(text, ["해커톤", "공모전", "경진대회", "competition"]) and text_contains_any(
        text,
        PORTFOLIO_KEYWORDS,
    )


def career_deadline_scores(deadline: dict[str, object]) -> tuple[int, int]:
    status = str(deadline.get("deadline_status", "unknown"))
    days = deadline.get("days_until_deadline")
    clarity_score = 30 if status == "open" else 20 if status in {"rolling", "until_filled"} else 0
    available_score = 30 if status in {"open", "rolling", "until_filled"} else 0
    if isinstance(days, int) and 1 <= days <= 14:
        available_score += 15
    elif isinstance(days, int) and days == 0:
        available_score += 10
    return clarity_score, available_score


def score_career_candidate(candidate: Candidate, current_time: datetime) -> dict[str, int]:
    text = career_text(candidate)
    sub_category = classify_career_sub_category(candidate)
    career_type = career_type_for_sub_category(sub_category)
    deadline = parse_korean_deadline(text, current_time)
    deadline_clarity_score, deadline_available_score = career_deadline_scores(deadline)
    backend_fit_score = 25 if is_backend_career_candidate(candidate) else 0
    entry_fit_score = 25 if is_entry_or_intern_candidate(candidate) else 0
    portfolio_fit_score = 10 if is_portfolio_activity_candidate(candidate) else 0
    tech_score = 10 if infer_tech_keywords(text) else 0
    source_reliability_score = 10 if candidate.source_reliability in {"official", "platform"} else 0
    process_score = 5 if infer_process_or_deliverable(text, career_type) else 0
    actionability_score = candidate.actionability_score

    score = (
        deadline_clarity_score
        + deadline_available_score
        + backend_fit_score
        + entry_fit_score
        + portfolio_fit_score
        + tech_score
        + source_reliability_score
        + process_score
        + actionability_score
    )

    if is_generic_career_url(candidate.url):
        score -= 40
    if deadline["deadline_status"] == "unknown":
        score -= 30
    if not infer_company_or_host(text, candidate):
        score -= 15
    if re.fullmatch(r".*(백엔드|서버).*(인턴|채용|신입).*", candidate.title) and len(candidate.title) < 16:
        score -= 20
    if deadline["deadline_status"] == "closed" or candidate.exclude_reason:
        score -= 100

    return {
        "score": score,
        "deadline_clarity_score": deadline_clarity_score,
        "backend_fit_score": backend_fit_score,
        "entry_fit_score": entry_fit_score,
        "portfolio_fit_score": portfolio_fit_score,
        "source_reliability_score": source_reliability_score,
        "actionability_score": max(actionability_score, 0),
    }


def classify_reliability(
    url: str,
    configured: str,
    reliability_domains: dict[str, object],
) -> str:
    if configured in RELIABILITY_SCORE:
        return configured

    domain = domain_from_url(url)
    for reliability in ("official", "major_media", "platform", "aggregator"):
        domains = reliability_domains.get(reliability, [])
        if isinstance(domains, list) and domain_matches(domain, [str(item) for item in domains]):
            return reliability
    return "unknown"


def classify_korea_relevance(category: dict[str, object], text: str, url: str) -> str:
    keywords = category_values(category, "korea_keywords")
    domain = domain_from_url(url)
    if text_contains_any(text, keywords) or domain.endswith(".kr"):
        return "high"
    if contains_korean(text):
        return "medium"
    return "low"


def classify_developer_relevance(category: dict[str, object], text: str) -> str:
    keywords = category_values(category, "developer_keywords")
    matches = count_matches(text, keywords)
    if matches >= 2:
        return "high"
    if matches == 1:
        return "medium"
    return "low"


def build_tags(category: dict[str, object], text: str) -> list[str]:
    tags = set(category_values(category, "tags"))
    lowered = text.lower()
    keyword_tags = {
        "ai": ["ai", "llm", "생성형", "인공지능", "에이전트", "모델"],
        "backend": ["backend", "백엔드", "서버", "spring", "java", "kotlin", "kubernetes"],
        "security": ["security", "보안", "취약점", "cve", "랜섬웨어", "공급망"],
        "internship": ["인턴", "intern", "채용", "신입", "주니어"],
        "hackathon": ["해커톤", "공모전", "경진대회", "대회"],
    }
    for tag, keywords in keyword_tags.items():
        if any(keyword in lowered for keyword in keywords):
            tags.add(tag)
    return sorted(tags)


def infer_exclude_reason(category_id: str, text: str) -> str:
    if text_contains_any(text, EXPIRED_DEADLINE_KEYWORDS):
        return "expired-deadline"
    if text_contains_any(text, SENIOR_ONLY_KEYWORDS):
        return "senior-only"
    if category_id == WEEKLY_CAREER_CATEGORY_ID and text_contains_any(
        text, FRONTEND_MARKETING_KEYWORDS
    ):
        return "frontend-or-marketing-focused"
    if category_id == WEEKLY_CAREER_CATEGORY_ID and text_contains_any(
        text, CAREER_EXCLUSION_KEYWORDS
    ):
        return "education-or-non-developer-focused"
    if text_contains_any(text, ["주가", "급등", "급락", "목표가", "투자의견", "관련주"]):
        return "stock-or-investment-only"
    if category_id == WEEKLY_CAREER_CATEGORY_ID and not text_contains_any(
        text, BACKEND_KEYWORDS + STUDENT_KEYWORDS
    ):
        return "unclear-backend-student-fit"
    return ""


def deadline_urgency_score_for(category_id: str, text: str, exclude_reason: str) -> int:
    if exclude_reason == "expired-deadline":
        return -50
    if category_id != WEEKLY_CAREER_CATEGORY_ID:
        return 0
    if text_contains_any(text, ["오늘", "내일", "이번 주", "7일", "마감"]):
        return 20
    if text_contains_any(text, ["접수", "모집", "지원"]):
        return 10
    return 0


def actionability_score_for(category_id: str, text: str) -> int:
    score = keyword_fit_score(text, ACTION_KEYWORDS, 5, 20)
    if category_id == WEEKLY_CAREER_CATEGORY_ID and text_contains_any(
        text, ["공식", "채용", "대회", "공모전", "해커톤"]
    ):
        score += 10
    return min(score, 30)


def score_candidate(
    candidate: Candidate,
    current_time: datetime,
    penalty_keywords: list[str],
) -> int:
    score = 0
    if candidate.published_at:
        age = current_time - candidate.published_at
        if age <= timedelta(hours=24):
            score += 30
        elif age <= timedelta(hours=72):
            score += 15

    if candidate.korea_relevance == "high":
        score += 25
    elif candidate.korea_relevance == "medium":
        score += 10

    if candidate.developer_relevance == "high":
        score += 25
    elif candidate.developer_relevance == "medium":
        score += 10

    score += RELIABILITY_SCORE.get(candidate.source_reliability, 0)
    score += candidate.persona_fit_score // 2
    score += candidate.actionability_score
    score += candidate.deadline_urgency_score

    if candidate.security_action_required:
        score += 10

    searchable = f"{candidate.title} {candidate.summary}"
    if text_contains_any(searchable, penalty_keywords):
        score -= 30
    if candidate.exclude_reason:
        score -= 50

    return score


def build_candidate(
    *,
    category: dict[str, object],
    title: str,
    url: str,
    source_url: str,
    source: str,
    publisher: str,
    published_at: datetime | None,
    summary: str,
    query: str,
    source_reliability: str,
    current_time: datetime,
    penalty_keywords: list[str],
) -> Candidate | None:
    clean_title = truncate_text(strip_html(title), TITLE_LIMIT)
    clean_url = (url or source_url).strip()
    clean_source_url = (source_url or clean_url).strip()
    clean_summary = truncate_text(strip_html(summary), SUMMARY_LIMIT)
    if not clean_title or not clean_url:
        return None

    searchable = f"{clean_title} {clean_summary} {publisher} {query}"
    korea_relevance = classify_korea_relevance(category, searchable, clean_url)
    developer_relevance = classify_developer_relevance(category, searchable)
    tags = build_tags(category, searchable)
    category_id = str(category.get("id", "")).strip()
    backend_fit_score = keyword_fit_score(searchable, BACKEND_KEYWORDS, 10, 30)
    kotlin_spring_fit_score = keyword_fit_score(searchable, KOTLIN_SPRING_KEYWORDS, 10, 30)
    student_fit_score = keyword_fit_score(searchable, STUDENT_KEYWORDS, 10, 25)
    exclude_reason = infer_exclude_reason(category_id, searchable)
    if query == "reference_page" and exclude_reason == "unclear-backend-student-fit":
        exclude_reason = ""
    deadline_urgency_score = deadline_urgency_score_for(
        category_id, searchable, exclude_reason
    )
    source_reliability_score = RELIABILITY_SCORE.get(source_reliability, 0)
    actionability_score = actionability_score_for(category_id, searchable)
    security_action_required = (
        category_id == "kr-backend-tech-news"
        and text_contains_any(searchable, SECURITY_ACTION_KEYWORDS)
    )
    persona_fit_score = min(
        backend_fit_score
        + kotlin_spring_fit_score
        + student_fit_score
        + actionability_score,
        100,
    )

    candidate = Candidate(
        category=category_id,
        title=clean_title,
        url=clean_url,
        source_url=clean_source_url,
        source=source,
        publisher=publisher or domain_from_url(clean_url) or "unknown",
        published_at=published_at,
        summary=clean_summary,
        query=query,
        korea_relevance=korea_relevance,
        developer_relevance=developer_relevance,
        source_reliability=source_reliability,
        tags=tags,
        persona_fit_score=persona_fit_score,
        backend_fit_score=backend_fit_score,
        kotlin_spring_fit_score=kotlin_spring_fit_score,
        student_fit_score=student_fit_score,
        deadline_urgency_score=deadline_urgency_score,
        source_reliability_score=source_reliability_score,
        actionability_score=actionability_score,
        security_action_required=security_action_required,
        exclude_reason=exclude_reason,
        score=0,
    )
    return replace(candidate, score=score_candidate(candidate, current_time, penalty_keywords))


def naver_display(config: dict[str, object], query_config: object) -> int:
    display = config.get("naver", {}).get("display", DEFAULT_DISPLAY) if isinstance(config.get("naver"), dict) else DEFAULT_DISPLAY
    if isinstance(query_config, dict):
        display = query_config.get("display", display)
    try:
        parsed = int(display)
    except (TypeError, ValueError):
        parsed = DEFAULT_DISPLAY
    return min(max(parsed, 1), MAX_DISPLAY)


def naver_query_value(query_config: object) -> str:
    if isinstance(query_config, dict):
        return str(query_config.get("query", "")).strip()
    return str(query_config).strip()


def fetch_naver_items(
    endpoint: str,
    query: str,
    display: int,
    sort: str,
    credentials: tuple[str, str],
) -> list[dict[str, object]]:
    params = urllib.parse.urlencode(
        {"query": query, "display": display, "start": 1, "sort": sort}
    )
    request = urllib.request.Request(
        f"{endpoint}?{params}",
        headers={
            "User-Agent": USER_AGENT,
            "X-Naver-Client-Id": credentials[0],
            "X-Naver-Client-Secret": credentials[1],
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        detail = " ".join(body.split())[:300] if body else exc.reason
        if exc.code in {401, 403}:
            raise RuntimeError(f"Naver News Search API auth failed ({exc.code}): {detail}") from exc
        raise RuntimeError(f"Naver News Search API request failed ({exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Naver News Search API request failed for query '{query}': {exc}") from exc

    items = payload.get("items", [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def collect_naver_candidates(
    config: dict[str, object],
    category: dict[str, object],
    credentials: tuple[str, str],
    current_time: datetime,
    penalty_keywords: list[str],
) -> list[Candidate]:
    naver = config.get("naver", {})
    endpoint = str(naver.get("endpoint", "")).strip() if isinstance(naver, dict) else ""
    sort = str(naver.get("sort", "date")).strip() if isinstance(naver, dict) else "date"
    reliability_domains = config.get("reliability_domains", {})
    if not isinstance(reliability_domains, dict):
        reliability_domains = {}
    if not endpoint:
        raise RuntimeError("Naver endpoint is missing in configs/kr-sources.json.")

    candidates: list[Candidate] = []
    raw_queries = category.get("naver_queries", [])
    if not isinstance(raw_queries, list):
        return candidates

    for query_config in raw_queries:
        query = naver_query_value(query_config)
        if not query:
            continue
        display = naver_display(config, query_config)
        items = fetch_naver_items(endpoint, query, display, sort, credentials)
        for item in items:
            original_link = strip_html(str(item.get("originallink", ""))).strip()
            link = strip_html(str(item.get("link", ""))).strip()
            url = original_link or link
            if not url:
                continue
            source_url = link or original_link
            reliability = classify_reliability(url, "", reliability_domains)
            publisher = domain_from_url(url) or domain_from_url(source_url)
            candidate = build_candidate(
                category=category,
                title=str(item.get("title", "")),
                url=url,
                source_url=source_url,
                source="Naver News Search",
                publisher=publisher,
                published_at=parse_datetime(str(item.get("pubDate", ""))),
                summary=str(item.get("description", "")),
                query=query,
                source_reliability=reliability,
                current_time=current_time,
                penalty_keywords=penalty_keywords,
            )
            if candidate:
                candidates.append(candidate)
    return candidates


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(element: ET.Element, names: set[str]) -> str:
    for child in element:
        if local_name(child.tag) in names:
            return "".join(child.itertext()).strip()
    return ""


def parse_atom_entry(entry: ET.Element) -> tuple[str, str, str, datetime | None]:
    title = strip_html(child_text(entry, {"title"}))
    url = ""
    for child in entry:
        if local_name(child.tag) != "link":
            continue
        rel = child.attrib.get("rel", "alternate")
        href = child.attrib.get("href", "").strip()
        if href and rel in {"alternate", ""}:
            url = href
            break
    if not url:
        url = child_text(entry, {"link", "id"})
    summary = strip_html(child_text(entry, {"summary", "content"}))
    published = parse_datetime(child_text(entry, {"published", "updated"}))
    return title, url, summary, published


def parse_rss_item(item: ET.Element) -> tuple[str, str, str, datetime | None]:
    title = strip_html(child_text(item, {"title"}))
    url = child_text(item, {"link"})
    if not url:
        url = child_text(item, {"guid"})
    summary = strip_html(child_text(item, {"description", "summary", "encoded"}))
    published = parse_datetime(child_text(item, {"pubdate", "published", "updated", "date"}))
    return title, url, summary, published


def parse_feed_items(payload: bytes) -> list[tuple[str, str, str, datetime | None]]:
    root = ET.fromstring(payload)
    root_name = local_name(root.tag)

    if root_name == "feed":
        return [parse_atom_entry(entry) for entry in root if local_name(entry.tag) == "entry"]

    items: list[ET.Element] = []
    if root_name == "rss":
        for child in root:
            if local_name(child.tag) == "channel":
                items.extend(grandchild for grandchild in child if local_name(grandchild.tag) == "item")
    elif root_name == "rdf":
        items = [child for child in root if local_name(child.tag) == "item"]
    else:
        items = [child for child in root.iter() if local_name(child.tag) == "item"]

    return [parse_rss_item(item) for item in items]


def fetch_feed(source: dict[str, object]) -> bytes:
    request = urllib.request.Request(
        str(source.get("url", "")).strip(),
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
        },
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read()


def collect_feed_candidates(
    config: dict[str, object],
    category: dict[str, object],
    current_time: datetime,
    penalty_keywords: list[str],
) -> list[Candidate]:
    reliability_domains = config.get("reliability_domains", {})
    if not isinstance(reliability_domains, dict):
        reliability_domains = {}

    candidates: list[Candidate] = []
    raw_sources = category.get("rss_sources", [])
    if not isinstance(raw_sources, list):
        return candidates

    for source in raw_sources:
        if not isinstance(source, dict):
            continue
        source_type = str(source.get("type", "")).strip()
        source_name = str(source.get("name", "")).strip() or "RSS/Atom"
        feed_url = str(source.get("url", "")).strip()
        if source_type not in SUPPORTED_FEED_TYPES:
            print(f"Warning: unsupported feed type for {source_name}: {source_type}", file=sys.stderr)
            continue
        if not feed_url:
            print(f"Warning: RSS source without URL: {source_name}", file=sys.stderr)
            continue

        try:
            payload = fetch_feed(source)
            parsed_items = parse_feed_items(payload)
        except (ET.ParseError, OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"Warning: failed to collect RSS source '{source_name}': {exc}", file=sys.stderr)
            continue

        configured_reliability = str(source.get("source_reliability", "")).strip()
        for title, url, summary, published_at in parsed_items:
            reliability = classify_reliability(url, configured_reliability, reliability_domains)
            candidate = build_candidate(
                category=category,
                title=title,
                url=url,
                source_url=feed_url,
                source=source_name,
                publisher=source_name,
                published_at=published_at,
                summary=summary,
                query="",
                source_reliability=reliability,
                current_time=current_time,
                penalty_keywords=penalty_keywords,
            )
            if candidate:
                candidates.append(candidate)
    return candidates


def collect_reference_candidates(
    config: dict[str, object],
    category: dict[str, object],
    current_time: datetime,
    penalty_keywords: list[str],
) -> list[Candidate]:
    reliability_domains = config.get("reliability_domains", {})
    if not isinstance(reliability_domains, dict):
        reliability_domains = {}

    candidates: list[Candidate] = []
    raw_pages = category.get("reference_pages", [])
    if not isinstance(raw_pages, list):
        return candidates

    for page in raw_pages:
        if not isinstance(page, dict):
            continue
        name = str(page.get("name", "")).strip()
        url = str(page.get("url", "")).strip()
        if not name or not url:
            continue
        configured_reliability = str(page.get("source_reliability", "")).strip()
        reliability = classify_reliability(url, configured_reliability, reliability_domains)
        category_id = str(category.get("id", "")).strip()
        candidate = build_candidate(
            category=category,
            title=name,
            url=url,
            source_url=url,
            source=name if category_id == WEEKLY_CAREER_CATEGORY_ID else "Official reference page",
            publisher=domain_from_url(url) or name,
            published_at=None,
            summary="공식 페이지 후보입니다. 최신 공고, 발표, 마감 여부는 AI 편집 단계에서 확인해야 합니다.",
            query="reference_page",
            source_reliability=reliability,
            current_time=current_time,
            penalty_keywords=penalty_keywords,
        )
        if candidate:
            candidates.append(candidate)
    return candidates


def fetch_github_api_json(
    url: str,
    token: str | None,
    repository: str,
    description: str,
) -> object | None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        detail = " ".join(body.split())[:300] if body else exc.reason
        if token and exc.code in {403, 404}:
            print(
                f"Warning: GitHub token could not read {description} for {repository} "
                f"({exc.code}); "
                "retrying with the public unauthenticated API.",
                file=sys.stderr,
            )
            return fetch_github_api_json(url, None, repository, description)
        if exc.code == 403:
            print(
                f"Warning: GitHub API rate/auth limit for {description} in {repository} "
                f"({exc.code}): {detail}",
                file=sys.stderr,
            )
            return None
        raise RuntimeError(
            f"GitHub API request failed for {description} in {repository} "
            f"({exc.code}): {detail}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"GitHub API request failed for {description} in {repository}: {exc}"
        ) from exc


def fetch_github_issues(repository: str, token: str | None) -> list[dict[str, object]]:
    params = urllib.parse.urlencode(
        {
            "state": "open",
            "sort": "updated",
            "direction": "desc",
            "per_page": 50,
        }
    )
    payload = fetch_github_api_json(
        f"https://api.github.com/repos/{repository}/issues?{params}",
        token,
        repository,
        "issues",
    )

    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def fetch_github_issue_comments(
    repository: str,
    issue_number: int,
    token: str | None,
    expected_count: int = 0,
) -> list[dict[str, object]] | None:
    comments: list[dict[str, object]] = []
    page = 1
    while True:
        params = urllib.parse.urlencode({"per_page": 100, "page": page})
        payload = fetch_github_api_json(
            f"https://api.github.com/repos/{repository}/issues/{issue_number}/comments?{params}",
            token,
            repository,
            f"issue #{issue_number} comments",
        )
        if payload is None:
            return None
        if not isinstance(payload, list):
            return comments
        page_items = [item for item in payload if isinstance(item, dict)]
        comments.extend(page_items)
        if len(page_items) < 100:
            return comments
        if expected_count and len(comments) >= expected_count:
            return comments
        page += 1


def fetch_github_open_pr_reference_count(
    repository: str,
    issue_number: int,
    token: str | None,
) -> int | None:
    query = f"repo:{repository} is:pr is:open {issue_number}"
    params = urllib.parse.urlencode({"q": query, "per_page": 1})
    payload = fetch_github_api_json(
        f"https://api.github.com/search/issues?{params}",
        token,
        repository,
        f"open PR search for issue #{issue_number}",
    )
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return 0
    try:
        return int(payload.get("total_count", 0))
    except (TypeError, ValueError):
        return 0


def label_names(issue: dict[str, object]) -> list[str]:
    raw_labels = issue.get("labels", [])
    if not isinstance(raw_labels, list):
        return []
    labels = []
    for label in raw_labels:
        if isinstance(label, dict):
            name = str(label.get("name", "")).strip()
            if name:
                labels.append(name)
    return labels


def github_login(issue: dict[str, object]) -> str:
    user = issue.get("user", {})
    if not isinstance(user, dict):
        return ""
    return str(user.get("login", "")).strip()


def issue_assignee_logins(issue: dict[str, object]) -> list[str]:
    raw_assignees = issue.get("assignees", [])
    if not isinstance(raw_assignees, list):
        return []
    assignees = []
    for assignee in raw_assignees:
        if isinstance(assignee, dict):
            login = str(assignee.get("login", "")).strip()
            if login:
                assignees.append(login)
    return assignees


def trusted_maintainers_for(
    repository: str,
    oss_config: dict[str, object],
) -> set[str]:
    trusted = oss_config.get("trusted_maintainers", {})
    if not isinstance(trusted, dict):
        return set()
    maintainers = trusted.get(repository, [])
    if not isinstance(maintainers, list):
        return set()
    return {str(login).strip().lower() for login in maintainers if str(login).strip()}


def is_maintainer_triaged(labels: list[str]) -> bool:
    return text_contains_any(" ".join(labels), OSS_BEGINNER_TRIAGE_LABELS)


def claim_comment_author(comments: list[dict[str, object]] | None) -> str:
    if comments is None:
        return ""
    for comment in comments:
        body = strip_html(str(comment.get("body") or ""))
        if text_contains_any(body, OSS_CLAIM_KEYWORDS):
            user = comment.get("user", {})
            if isinstance(user, dict):
                return str(user.get("login", "")).strip()
            return "unknown"
    return ""


def infer_contribution_type(text: str) -> str:
    lowered = text.lower()
    if text_contains_any(lowered, ["documentation", "docs", "doc", "getting started"]):
        return "docs"
    if text_contains_any(lowered, ["test", "tests", "testing"]):
        return "test"
    if text_contains_any(lowered, ["sample", "example"]):
        return "sample"
    if text_contains_any(lowered, ["reproducer", "reproduce", "repro", "bug"]):
        return "bug-repro"
    if text_contains_any(lowered, ["enhancement", "improvement"]):
        return "small-enhancement"
    return "triage"


def ps_tracks(curriculum: dict[str, object]) -> list[dict[str, object]]:
    tracks = curriculum.get("tracks", [])
    if not isinstance(tracks, list):
        raise RuntimeError("configs/programmers-ps-curriculum.json must contain tracks.")
    return [track for track in tracks if isinstance(track, dict)]


def ps_track(curriculum: dict[str, object], track_id: str) -> dict[str, object]:
    for track in ps_tracks(curriculum):
        if str(track.get("id", "")).strip() == track_id:
            return track
    raise RuntimeError(f"Unknown current_track in progress: {track_id}")


def ps_problems(track: dict[str, object]) -> list[dict[str, object]]:
    problems = track.get("problems", [])
    if not isinstance(problems, list):
        raise RuntimeError(f"Track must contain a problems array: {track.get('id')}")
    return [problem for problem in problems if isinstance(problem, dict)]


def ps_problem_ids(entries: object) -> set[str]:
    if not isinstance(entries, list):
        return set()

    ids = set()
    for entry in entries:
        if isinstance(entry, dict):
            problem_id = str(entry.get("problem_id", "")).strip()
        else:
            problem_id = str(entry).strip()
        if problem_id:
            ids.add(problem_id)
    return ids


def ps_problem_level(problem: dict[str, object]) -> int:
    try:
        return int(problem.get("level", 0))
    except (TypeError, ValueError):
        return 0


def select_ps_problem(
    track: dict[str, object],
    progress: dict[str, object],
) -> dict[str, object] | None:
    solved_ids = ps_problem_ids(progress.get("solved", []))
    candidates = [
        (index, problem)
        for index, problem in enumerate(ps_problems(track))
        if str(problem.get("id", "")).strip() not in solved_ids
    ]
    if not candidates:
        return None
    _, selected = min(candidates, key=lambda item: (ps_problem_level(item[1]), item[0]))
    return selected


def build_ps_advance_recommendation(
    track: dict[str, object],
    progress: dict[str, object],
) -> dict[str, object]:
    solved_ids = ps_problem_ids(progress.get("solved", []))
    solved_problems = [
        problem
        for problem in ps_problems(track)
        if str(problem.get("id", "")).strip() in solved_ids
    ]
    rule = track.get("advance_rule", {})
    if not isinstance(rule, dict):
        rule = {}

    min_solved = int(rule.get("min_solved", 0) or 0)
    target_level_count = int(rule.get("max_level_solved", 0) or 0)
    target_level = int(progress.get("target_level") or track.get("default_target_level") or 0)
    target_level_solved = [
        problem for problem in solved_problems if ps_problem_level(problem) >= target_level
    ]

    if bool(progress.get("manual_advance_requested")) and bool(
        rule.get("allow_manual_advance", False)
    ):
        return {
            "can_advance": True,
            "reason": "수동 track 이동 요청이 설정되어 있습니다.",
        }
    if len(target_level_solved) < target_level_count:
        return {
            "can_advance": False,
            "reason": "target_level 문제를 아직 충분히 풀지 않았습니다.",
        }
    if len(solved_problems) < min_solved:
        return {
            "can_advance": False,
            "reason": "현재 track에서 해결한 문제가 아직 충분하지 않습니다.",
        }
    return {
        "can_advance": True,
        "reason": "현재 track의 최소 진행 조건을 충족했습니다.",
    }


def build_ps_routine_output(
    track: dict[str, object],
    progress: dict[str, object],
    selected: dict[str, object] | None,
    generated_at: datetime,
) -> dict[str, object]:
    problems = ps_problems(track)
    solved_ids = ps_problem_ids(progress.get("solved", []))
    solved_count = sum(
        1 for problem in problems if str(problem.get("id", "")).strip() in solved_ids
    )
    target_level = int(progress.get("target_level") or track.get("default_target_level") or 0)

    return {
        "category": "ps-weekly-routine",
        "generated_at": format_kst(generated_at),
        "current_track": {
            "id": str(track.get("id", "")).strip(),
            "name": str(track.get("name", "")).strip(),
            "goal": str(track.get("goal", "")).strip(),
            "week_started_at": str(progress.get("week_started_at", "")).strip(),
            "target_level": target_level,
            "progress": f"{solved_count}/{len(problems)}",
        },
        "today_problem": selected,
        "advance_recommendation": build_ps_advance_recommendation(track, progress),
    }


def record_ps_assignment(
    progress: dict[str, object],
    selected: dict[str, object] | None,
    current_time: datetime,
) -> None:
    if selected is None:
        return

    assigned = progress.setdefault("assigned", [])
    if not isinstance(assigned, list):
        raise RuntimeError("data/ps-progress.json assigned must be an array.")

    problem_id = str(selected.get("id", "")).strip()
    assigned.append(
        {
            "date": current_time.strftime("%Y-%m-%d"),
            "problem_id": problem_id,
        }
    )
    progress["last_recommended_problem_id"] = problem_id


def write_ps_routine_output(
    current_time: datetime,
    *,
    dry_run: bool,
    record_assignment: bool,
) -> None:
    curriculum = load_required_json(PS_CURRICULUM_PATH)
    progress = load_required_json(PS_PROGRESS_PATH)
    current_track = str(progress.get("current_track", "")).strip()
    if not current_track:
        raise RuntimeError("data/ps-progress.json current_track is required.")

    track = ps_track(curriculum, current_track)
    selected = select_ps_problem(track, progress)
    payload = build_ps_routine_output(track, progress, selected, current_time)
    write_json_file(PS_ROUTINE_OUTPUT_PATH, payload)

    if record_assignment and not dry_run:
        record_ps_assignment(progress, selected, current_time)
        write_json_file(PS_PROGRESS_PATH, progress)

    if selected is None:
        print(f"Wrote PS routine with no remaining problem: {PS_ROUTINE_OUTPUT_PATH}")
    else:
        print(
            "Wrote PS routine: "
            f"{selected.get('id')} / {selected.get('title')} -> {PS_ROUTINE_OUTPUT_PATH}"
        )
    if record_assignment and dry_run:
        print("Dry-run: PS assignment was not recorded.")


def load_backend_practical_curriculum(
    path: Path = BACKEND_PRACTICAL_CURRICULUM_PATH,
) -> dict[str, object]:
    curriculum = load_required_json(path)
    lessons = curriculum.get("lessons", [])
    if not isinstance(lessons, list) or not lessons:
        raise RuntimeError(
            "configs/backend-practical-knowledge-curriculum.json must contain lessons."
        )
    return curriculum


def select_backend_practical_lesson(
    curriculum: dict[str, object],
    current_time: datetime,
) -> dict[str, object]:
    lessons = curriculum.get("lessons", [])
    if not isinstance(lessons, list) or not lessons:
        raise RuntimeError("Backend practical curriculum lessons must not be empty.")

    selection_policy = curriculum.get("selection_policy", {})
    if not isinstance(selection_policy, dict):
        raise RuntimeError("Backend practical curriculum selection_policy is required.")
    if str(selection_policy.get("type", "")).strip() != "date_rotation":
        raise RuntimeError("Backend practical curriculum must use date_rotation policy.")
    if str(selection_policy.get("timezone", "")).strip() != "Asia/Seoul":
        raise RuntimeError("Backend practical curriculum timezone must be Asia/Seoul.")

    start_date_value = str(selection_policy.get("start_date", "")).strip()
    try:
        start_date = datetime.strptime(start_date_value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise RuntimeError(
            "Backend practical curriculum start_date must use YYYY-MM-DD."
        ) from exc

    today = current_time.astimezone(KST).date()
    days_since_start = max((today - start_date).days, 0)
    selected = lessons[days_since_start % len(lessons)]
    if not isinstance(selected, dict):
        raise RuntimeError("Selected backend practical lesson must be an object.")
    return selected


def write_backend_practical_candidate(current_time: datetime) -> None:
    curriculum = load_backend_practical_curriculum()
    selected = select_backend_practical_lesson(curriculum, current_time)
    payload = {
        "category": "backend-practical-knowledge",
        "generated_at": format_kst(current_time),
        "selection_policy": "date_rotation",
        "today": selected,
    }
    write_json_file(BACKEND_PRACTICAL_OUTPUT_PATH, payload)
    print(f"Wrote backend practical knowledge: {BACKEND_PRACTICAL_OUTPUT_PATH}")


def difficulty_model_matches(
    difficulty_model: dict[str, object],
    band: str,
    labels: list[str],
    searchable: str,
) -> bool:
    label_text = " ".join(labels)
    return text_contains_any(
        label_text,
        difficulty_model_values(difficulty_model, band, "positive_labels"),
    ) or text_contains_any(
        searchable,
        difficulty_model_values(difficulty_model, band, "positive_keywords"),
    )


def beginner_reason_for_band(difficulty_band: str, contribution_type: str) -> str:
    if difficulty_band == "p5_like":
        return "문서, 예제, 테스트, 재현처럼 첫 기여 범위가 작은 작업입니다."
    if difficulty_band == "p4_like":
        return "작은 개선 또는 명확한 버그로 주니어가 범위를 제한해 도전할 수 있습니다."
    if difficulty_band == "too_hard":
        return "보안, 릴리스, 내부 구현, 설계 논의 성격이 있어 첫 기여로 부적합합니다."
    if contribution_type != "triage":
        return "작업 유형은 보이지만 초보 친화 label 또는 난이도 근거가 부족합니다."
    return "초보 친화 근거가 부족합니다."


def first_action_for_contribution_type(contribution_type: str) -> str:
    if contribution_type == "docs":
        return "관련 문서 위치를 찾고 오탈자, 설명 누락, 예제 실행 여부를 확인한다."
    if contribution_type == "sample":
        return "예제 프로젝트를 실행하고 README 절차와 실제 동작 차이를 기록한다."
    if contribution_type == "test":
        return "관련 테스트 위치를 찾고 재현 가능한 최소 테스트 케이스를 확인한다."
    if contribution_type == "bug-repro":
        return "이슈 본문 기준으로 최소 재현 프로젝트나 실패 테스트를 만들 수 있는지 확인한다."
    if contribution_type == "small-enhancement":
        return "관련 설정, AutoConfiguration, 기존 테스트 경로를 먼저 추적한다."
    return "이슈 본문, label, 관련 파일 위치를 읽고 30분 안에 재현 가능성을 판단한다."


def first_action_for_issue(repository: str, contribution_type: str, searchable: str) -> str:
    if repository.startswith("spring-projects/spring-data") and contribution_type == "docs":
        return (
            "`src/docs/asciidoc`에서 관련 문서 위치를 찾고, "
            "`mvn package -Pdistribute` 문서 빌드 경로를 확인한다."
        )
    if contribution_type in OSS_PREFERRED_CONTRIBUTION_TYPES:
        return first_action_for_contribution_type(contribution_type)
    if text_contains_any(searchable, ["validation"]):
        return "검증 조건이 드러나는 테스트나 문서 위치를 먼저 찾고 재현 가능성을 메모한다."
    return first_action_for_contribution_type(contribution_type)


def pre_contribution_etiquette_for_issue() -> str:
    return (
        "작업 전 이슈에 "
        "“문서 위치를 확인해보고 작은 PR을 준비해도 괜찮을까요?”라고 짧게 확인한다."
    )


def status_check_for_issue(
    *,
    maintainer_authored: bool,
    maintainer_triaged: bool,
    has_assignee: bool,
    linked_prs_count: int,
    linked_work_check: str,
    comments_count: int,
    has_claim_comment: bool,
) -> str:
    checks = []
    if maintainer_authored:
        checks.append("maintainer가 연 이슈")
    elif maintainer_triaged:
        checks.append("maintainer triage label 확인")
    if not has_assignee:
        checks.append("담당자 없음")
    if linked_work_check != "unknown" and linked_prs_count == 0:
        checks.append("연결 PR/branch 없음")
    if comments_count == 0:
        checks.append("claim 댓글 없음")
    elif not has_claim_comment:
        checks.append("작업 claim 댓글 없음")
    return "이고, ".join(checks) + "입니다." if checks else ""


def oss_issue_scores(
    category: dict[str, object],
    *,
    difficulty_model: dict[str, object],
    text: str,
    labels: list[str],
    label_title_text: str,
    assignees_count: int,
    comments: int,
    maintainer_authored: bool,
    maintainer_qualified: bool,
    has_linked_work: bool,
    linked_work_check: str,
    has_claim_comment: bool,
    body_is_clear: bool,
    updated_at: datetime | None,
    current_time: datetime,
    state: str,
    is_pull_request: bool,
) -> tuple[int, int, int, int, int, str, str, str, str, str, int]:
    label_text = " ".join(labels)
    searchable = f"{label_text} {text}"
    positive_labels = category_values(category, "positive_labels")
    negative_keywords = category_values(category, "negative_keywords")

    status_score = 50 if text_contains_any(label_text, ["status: ideal-for-contribution"]) else 0
    docs_label_score = 40 if text_contains_any(label_text, ["type: documentation", "in: docs"]) else 0
    beginner_keyword_score = 35 if text_contains_any(searchable, OSS_BEGINNER_KEYWORDS) else 0
    good_first_score = 20 if text_contains_any(label_text, OSS_BEGINNER_TRIAGE_LABELS) else 0
    p5_match = difficulty_model_matches(difficulty_model, "p5_like", labels, searchable)
    p4_match = difficulty_model_matches(difficulty_model, "p4_like", labels, searchable)
    p5_score = 30 if p5_match else 0
    p4_score = 20 if p4_match else 0
    category_label_score = 15 if text_contains_any(label_text, positive_labels) else 0
    direct_spring_score = 15 if text_contains_any(searchable, OSS_DIRECT_SPRING_KEYWORDS) else 0
    maintainer_score = 40 if maintainer_authored else 0
    focused_scope_score = 20 if infer_contribution_type(searchable) in OSS_PREFERRED_CONTRIBUTION_TYPES else 0
    body_clarity_score = 10 if body_is_clear else -20
    assignee_score = 20 if assignees_count == 0 else -40
    linked_work_score = 20 if linked_work_check != "unknown" and not has_linked_work else -80
    recent_score = 0
    stale_penalty = 0
    if updated_at:
        age = current_time - updated_at
        if age <= timedelta(days=90):
            recent_score = 15
        elif age > timedelta(days=180):
            stale_penalty = -40
    comments_score = 15 if comments <= 10 else 0
    comments_penalty = -40 if comments >= 30 else 0

    risk_penalty = 0
    risk_reasons = []
    if state != "open" or is_pull_request:
        risk_penalty += 70
        risk_reasons.append("not-open-issue")
    if not maintainer_qualified:
        risk_penalty += 80
        risk_reasons.append("external-author-without-maintainer-triage")
    if has_linked_work:
        risk_penalty += 80
        risk_reasons.append("linked-work")
    if linked_work_check == "unknown":
        risk_penalty += 60
        risk_reasons.append("linked-work-check-unknown")
    if has_claim_comment:
        risk_penalty += 80
        risk_reasons.append("claim-comment")
    if text_contains_any(searchable, OSS_SECURITY_KEYWORDS):
        risk_penalty += 70
        risk_reasons.append("security-vulnerability")
    if text_contains_any(searchable, OSS_RELEASE_BLOCKER_KEYWORDS):
        risk_penalty += 60
        risk_reasons.append("release-blocker")
    if text_contains_any(searchable, OSS_DEEP_INTERNALS_KEYWORDS):
        risk_penalty += 60
        risk_reasons.append("deep-internals")
    if text_contains_any(searchable, OSS_MAJOR_API_KEYWORDS):
        risk_penalty += 60
        risk_reasons.append("major-api-or-breaking-change")
    if text_contains_any(label_title_text, OSS_BLOCKED_LABEL_TITLE_KEYWORDS):
        risk_penalty += 60
        risk_reasons.append("blocked-label-or-title")
    if text_contains_any(searchable, OSS_DESIGN_KEYWORDS):
        risk_penalty += 50
        risk_reasons.append("design-or-epic")
    if assignees_count > 0:
        risk_reasons.append("assigned")
    if comments >= 30:
        risk_reasons.append("many-comments")
    if stale_penalty:
        risk_reasons.append("stale-over-180-days")
    if text_contains_any(searchable, ["dependency upgrade", "dependency updates", "upgrade dependency"]) and not text_contains_any(
        searchable,
        ["test", "tests", "testing", "coverage"],
    ):
        risk_penalty += 30
        risk_reasons.append("dependency-upgrade-unclear-test-scope")
    if text_contains_any(searchable, OSS_DUPLICATE_KEYWORDS):
        risk_penalty += 30
        risk_reasons.append("duplicate-invalid-or-superseded")
    if text_contains_any(searchable, negative_keywords):
        risk_penalty += 10

    contribution_type = infer_contribution_type(searchable)
    hard_exclusion = any(
        reason in risk_reasons
        for reason in ("security-vulnerability", "release-blocker", "deep-internals")
    )
    if hard_exclusion or "design-or-epic" in risk_reasons or "major-api-or-breaking-change" in risk_reasons:
        difficulty_band = "too_hard"
    elif p5_match:
        difficulty_band = "p5_like"
    elif p4_match:
        difficulty_band = "p4_like"
    else:
        difficulty_band = "unclear"

    positive_score = (
        status_score
        + docs_label_score
        + beginner_keyword_score
        + good_first_score
        + p5_score
        + p4_score
        + category_label_score
        + maintainer_score
        + focused_scope_score
        + body_clarity_score
        + max(assignee_score, 0)
        + max(linked_work_score, 0)
        + recent_score
        + comments_score
        + direct_spring_score
    )
    penalty_score = (
        risk_penalty
        + max(-assignee_score, 0)
        + max(-linked_work_score, 0)
        + max(-comments_penalty, 0)
        + max(-stale_penalty, 0)
    )
    junior_fit_score = max(
        min(
            status_score
            + docs_label_score
            + beginner_keyword_score
            + good_first_score
            + p5_score
            + maintainer_score
            + focused_scope_score
            + max(assignee_score, 0)
            + max(linked_work_score, 0)
            + comments_score,
            100,
        ),
        0,
    )
    backend_fit_score = 25 if text_contains_any(searchable, BACKEND_KEYWORDS) else 0
    kotlin_spring_fit_score = 25 if text_contains_any(searchable, OSS_DIRECT_SPRING_KEYWORDS) else 0
    first_pr_potential_score = max(
        min(
            status_score
            + docs_label_score
            + beginner_keyword_score
            + good_first_score
            + p5_score
            + p4_score
            + maintainer_score
            + focused_scope_score
            + max(assignee_score, 0)
            + max(linked_work_score, 0)
            + comments_score,
            100,
        ),
        0,
    )
    score = positive_score - penalty_score
    exclude_reasons = []
    if difficulty_band not in {"p5_like", "p4_like"}:
        exclude_reasons.append(difficulty_band)
    hard_exclude_reasons = {
        "external-author-without-maintainer-triage",
        "assigned",
        "linked-work",
        "linked-work-check-unknown",
        "claim-comment",
        "security-vulnerability",
        "release-blocker",
        "deep-internals",
        "major-api-or-breaking-change",
        "blocked-label-or-title",
    }
    exclude_reasons.extend(reason for reason in risk_reasons if reason in hard_exclude_reasons)
    if hard_exclusion:
        exclude_reasons.extend(
            reason
            for reason in risk_reasons
            if reason in {"security-vulnerability", "release-blocker", "deep-internals"}
        )

    risk_reason = ", ".join(dict.fromkeys(risk_reasons)) if risk_reasons else "low"
    return (
        junior_fit_score,
        backend_fit_score,
        kotlin_spring_fit_score,
        first_pr_potential_score,
        penalty_score,
        ",".join(dict.fromkeys(exclude_reasons)),
        difficulty_band,
        beginner_reason_for_band(difficulty_band, contribution_type),
        first_action_for_contribution_type(contribution_type),
        risk_reason,
        score,
    )


def build_oss_issue_candidate(
    category: dict[str, object],
    difficulty_model: dict[str, object],
    oss_config: dict[str, object],
    repository: str,
    issue: dict[str, object],
    token: str | None,
    current_time: datetime,
) -> OssIssueCandidate | None:
    if "pull_request" in issue:
        return None
    state = str(issue.get("state", "")).strip()
    if state != "open":
        return None

    title = truncate_text(strip_html(str(issue.get("title", ""))), TITLE_LIMIT)
    html_url = str(issue.get("html_url", "")).strip()
    number = issue.get("number", 0)
    try:
        issue_number = int(number)
    except (TypeError, ValueError):
        issue_number = 0
    if not title or not html_url or issue_number <= 0:
        return None

    labels = label_names(issue)
    author = github_login(issue)
    author_association = str(issue.get("author_association", "")).strip().upper()
    trusted_maintainers = trusted_maintainers_for(repository, oss_config)
    maintainer_authored = (
        author_association in OSS_MAINTAINER_ASSOCIATIONS
        or author.lower() in trusted_maintainers
    )
    maintainer_triaged = is_maintainer_triaged(labels)
    maintainer_qualified = maintainer_authored or maintainer_triaged
    raw_body = strip_html(str(issue.get("body") or ""))
    summary = truncate_text(raw_body, OSS_SUMMARY_LIMIT)
    assignees = issue_assignee_logins(issue)
    assignees_count = len(assignees)
    has_assignee = assignees_count > 0
    try:
        comments_count = int(issue.get("comments", 0))
    except (TypeError, ValueError):
        comments_count = 0
    created_at = parse_datetime(str(issue.get("created_at", "")))
    updated_at = parse_datetime(str(issue.get("updated_at", "")))
    searchable = f"{repository} {title} {summary} {' '.join(labels)}"
    label_title_text = f"{' '.join(labels)} {title}"
    if not maintainer_qualified:
        return None
    if has_assignee:
        return None
    if text_contains_any(f"{title} {raw_body}", OSS_CLAIM_KEYWORDS):
        return None
    if text_contains_any(label_title_text, OSS_BLOCKED_LABEL_TITLE_KEYWORDS):
        return None
    if text_contains_any(searchable, OSS_SECURITY_KEYWORDS + OSS_RELEASE_BLOCKER_KEYWORDS):
        return None
    if text_contains_any(searchable, OSS_DEEP_INTERNALS_KEYWORDS + OSS_MAJOR_API_KEYWORDS):
        return None
    if text_contains_any(searchable, OSS_DESIGN_KEYWORDS):
        return None
    if not (
        difficulty_model_matches(difficulty_model, "p5_like", labels, searchable)
        or difficulty_model_matches(difficulty_model, "p4_like", labels, searchable)
    ):
        return None

    contribution_type = infer_contribution_type(searchable)
    comments_payload: list[dict[str, object]] | None = []
    claim_comment_check = "checked"
    comments_checked_count = 0
    claim_author = ""
    if comments_count > 0:
        comments_payload = fetch_github_issue_comments(
            repository,
            issue_number,
            token,
            comments_count,
        )
        if comments_payload is None:
            claim_comment_check = "unknown"
        else:
            comments_checked_count = len(comments_payload)
            claim_author = claim_comment_author(comments_payload)
        if claim_author:
            return None
    linked_prs_result = fetch_github_open_pr_reference_count(repository, issue_number, token)
    linked_prs_count = linked_prs_result if linked_prs_result is not None else 0
    linked_branches_count = -1
    linked_work_check = "unknown"
    has_linked_work = linked_prs_count > 0 or linked_branches_count > 0
    safe_to_recommend = (
        state == "open"
        and maintainer_authored
        and not has_assignee
        and linked_prs_count == 0
        and linked_branches_count == 0
        and linked_work_check == "verified"
        and claim_comment_check == "checked"
        and not claim_author
        and contribution_type in OSS_PREFERRED_CONTRIBUTION_TYPES
    )
    if has_linked_work or not safe_to_recommend:
        return None

    body_is_clear = len(raw_body) >= 80 or text_contains_any(
        searchable,
        ["src/", ".java", ".kt", ".adoc", ".md", "documentation", "docs", "test"],
    )
    (
        junior_fit_score,
        backend_fit_score,
        kotlin_spring_fit_score,
        first_pr_potential_score,
        risk_score,
        exclude_reason,
        difficulty_band,
        why_beginner_friendly,
        first_30_min_action,
        risk_reason,
        score,
    ) = oss_issue_scores(
        category,
        difficulty_model=difficulty_model,
        text=searchable,
        labels=labels,
        label_title_text=label_title_text,
        assignees_count=assignees_count,
        comments=comments_count,
        maintainer_authored=maintainer_authored,
        maintainer_qualified=maintainer_qualified,
        has_linked_work=has_linked_work,
        linked_work_check=linked_work_check,
        has_claim_comment=False,
        body_is_clear=body_is_clear,
        updated_at=updated_at,
        current_time=current_time,
        state=state,
        is_pull_request=False,
    )

    return OssIssueCandidate(
        category=OSS_CATEGORY_ID,
        title=title,
        url=html_url,
        source_url=f"https://github.com/{repository}",
        source="GitHub Issues",
        repository=repository,
        issue_number=issue_number,
        author=author,
        author_association=author_association,
        maintainer_authored=maintainer_authored,
        labels=labels,
        state=state,
        assignees=assignees,
        assignees_count=assignees_count,
        has_assignee=has_assignee,
        comments=comments_count,
        comments_count=comments_count,
        has_claim_comment=False,
        claim_comment_check=claim_comment_check,
        linked_prs_count=linked_prs_count,
        linked_branches_count=linked_branches_count,
        linked_work_check=linked_work_check,
        has_linked_work=has_linked_work,
        comments_checked_count=comments_checked_count,
        created_at=created_at,
        updated_at=updated_at,
        summary=summary,
        contribution_type=contribution_type,
        junior_fit_score=junior_fit_score,
        backend_fit_score=backend_fit_score,
        kotlin_spring_fit_score=kotlin_spring_fit_score,
        first_pr_potential_score=first_pr_potential_score,
        risk_score=risk_score,
        exclude_reason=exclude_reason,
        difficulty_band=difficulty_band,
        why_beginner_friendly=why_beginner_friendly,
        first_30_min_action=first_action_for_issue(repository, contribution_type, searchable),
        pre_contribution_etiquette=pre_contribution_etiquette_for_issue(),
        claim_comment_author=claim_author,
        safe_to_recommend=safe_to_recommend,
        status_check=status_check_for_issue(
            maintainer_authored=maintainer_authored,
            maintainer_triaged=maintainer_triaged,
            has_assignee=has_assignee,
            linked_prs_count=linked_prs_count,
            linked_work_check=linked_work_check,
            comments_count=comments_count,
            has_claim_comment=False,
        ),
        risk_reason=risk_reason,
        score=score,
    )


def collect_oss_issue_candidates(
    category: dict[str, object],
    current_time: datetime,
) -> list[OssIssueCandidate]:
    oss_config = load_oss_repositories_config()
    repositories = configured_repositories(category, oss_config)
    difficulty_model = oss_config.get("difficulty_model", {})
    if not isinstance(difficulty_model, dict):
        difficulty_model = {}
    token = get_github_token()
    candidates: list[OssIssueCandidate] = []

    for repository in repositories:
        if "/" not in repository:
            print(f"Warning: invalid GitHub repository id: {repository}", file=sys.stderr)
            continue
        for issue in fetch_github_issues(repository, token):
            candidate = build_oss_issue_candidate(
                category,
                difficulty_model,
                oss_config,
                repository,
                issue,
                token,
                current_time,
            )
            if (
                candidate
                and candidate.difficulty_band in {"p5_like", "p4_like"}
                and not candidate.exclude_reason
            ):
                candidates.append(candidate)

    try:
        max_candidates = int(category.get("max_candidates", DEFAULT_MAX_CANDIDATES))
    except (TypeError, ValueError):
        max_candidates = DEFAULT_MAX_CANDIDATES

    return sorted(
        candidates,
        key=lambda item: (
            1 if item.difficulty_band == "p5_like" else 0,
            item.score,
            item.updated_at or datetime.min.replace(tzinfo=KST),
        ),
        reverse=True,
    )[:max(max_candidates, 0)]


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    deduped: list[Candidate] = []
    seen_urls: set[str] = set()
    seen_titles: list[str] = []

    for candidate in sorted(
        candidates,
        key=lambda item: (
            item.score,
            item.published_at or datetime.min.replace(tzinfo=KST),
        ),
        reverse=True,
    ):
        normalized_url = normalize_url(candidate.url)
        normalized_source_url = normalize_url(candidate.source_url)
        if normalized_url and normalized_url in seen_urls:
            continue
        if normalized_source_url and normalized_source_url in seen_urls:
            continue
        if title_is_duplicate(candidate.title, seen_titles):
            continue
        if normalized_url:
            seen_urls.add(normalized_url)
        if normalized_source_url:
            seen_urls.add(normalized_source_url)
        seen_titles.append(normalize_title(candidate.title))
        deduped.append(candidate)
    return deduped


def sort_and_limit(
    category: dict[str, object],
    candidates: list[Candidate],
    current_time: datetime,
) -> list[Candidate]:
    try:
        max_candidates = int(category.get("max_candidates", DEFAULT_MAX_CANDIDATES))
    except (TypeError, ValueError):
        max_candidates = DEFAULT_MAX_CANDIDATES

    category_id = str(category.get("id", "")).strip()
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        return sorted(
            dedupe_candidates(candidates),
            key=lambda item: (
                score_career_candidate(item, current_time)["score"],
                item.published_at or datetime.min.replace(tzinfo=KST),
            ),
            reverse=True,
        )[:max(max_candidates, 0)]

    return sorted(
        dedupe_candidates(candidates),
        key=lambda item: (
            item.score,
            item.published_at or datetime.min.replace(tzinfo=KST),
        ),
        reverse=True,
    )[:max(max_candidates, 0)]


def serialize_oss_issue_candidate(candidate: OssIssueCandidate) -> dict[str, object]:
    return {
        "title": candidate.title,
        "url": candidate.url,
        "source_url": candidate.source_url,
        "source": candidate.source,
        "repo": candidate.repository,
        "repository": candidate.repository,
        "issue_number": candidate.issue_number,
        "author": candidate.author,
        "author_association": candidate.author_association,
        "maintainer_authored": candidate.maintainer_authored,
        "labels": candidate.labels,
        "state": candidate.state,
        "assignees": candidate.assignees,
        "assignees_count": candidate.assignees_count,
        "has_assignee": candidate.has_assignee,
        "comments": candidate.comments,
        "comments_count": candidate.comments_count,
        "comments_checked_count": candidate.comments_checked_count,
        "has_claim_comment": candidate.has_claim_comment,
        "claim_comment_check": candidate.claim_comment_check,
        "claim_comment_author": candidate.claim_comment_author,
        "linked_prs_count": candidate.linked_prs_count,
        "linked_branches_count": candidate.linked_branches_count,
        "linked_work_check": candidate.linked_work_check,
        "has_linked_work": candidate.has_linked_work,
        "created_at": format_kst(candidate.created_at) if candidate.created_at else "",
        "updated_at": format_kst(candidate.updated_at) if candidate.updated_at else "",
        "summary": candidate.summary,
        "contribution_type": candidate.contribution_type,
        "junior_fit_score": candidate.junior_fit_score,
        "backend_fit_score": candidate.backend_fit_score,
        "kotlin_spring_fit_score": candidate.kotlin_spring_fit_score,
        "first_pr_potential_score": candidate.first_pr_potential_score,
        "risk_score": candidate.risk_score,
        "exclude_reason": candidate.exclude_reason,
        "difficulty_band": candidate.difficulty_band,
        "why_beginner_friendly": candidate.why_beginner_friendly,
        "first_30_min_action": candidate.first_30_min_action,
        "first_30m_action": candidate.first_30_min_action,
        "pre_contribution_etiquette": candidate.pre_contribution_etiquette,
        "safe_to_recommend": candidate.safe_to_recommend,
        "status_check": candidate.status_check,
        "risk_reason": candidate.risk_reason,
        "score": candidate.score,
    }


def serialize_candidate(candidate: Candidate | OssIssueCandidate) -> dict[str, object]:
    if isinstance(candidate, OssIssueCandidate):
        return serialize_oss_issue_candidate(candidate)

    return {
        "title": candidate.title,
        "url": candidate.url,
        "source_url": candidate.source_url,
        "source": candidate.source,
        "publisher": candidate.publisher,
        "published_at": format_kst(candidate.published_at) if candidate.published_at else "",
        "summary": candidate.summary,
        "query": candidate.query,
        "korea_relevance": candidate.korea_relevance,
        "developer_relevance": candidate.developer_relevance,
        "source_reliability": candidate.source_reliability,
        "tags": candidate.tags,
        "persona_fit_score": candidate.persona_fit_score,
        "backend_fit_score": candidate.backend_fit_score,
        "kotlin_spring_fit_score": candidate.kotlin_spring_fit_score,
        "student_fit_score": candidate.student_fit_score,
        "deadline_urgency_score": candidate.deadline_urgency_score,
        "source_reliability_score": candidate.source_reliability_score,
        "actionability_score": candidate.actionability_score,
        "security_action_required": candidate.security_action_required,
        "exclude_reason": candidate.exclude_reason,
        "score": candidate.score,
    }


def standardize_weekly_career_candidate(
    candidate: Candidate,
    generated_at: datetime,
) -> dict[str, object]:
    text = career_text(candidate)
    sub_category = classify_career_sub_category(candidate)
    career_type = career_type_for_sub_category(sub_category)
    deadline = parse_korean_deadline(text, generated_at)
    score_payload = score_career_candidate(candidate, generated_at)
    company_or_host = infer_company_or_host(text, candidate)
    exclude_reasons = []
    if candidate.exclude_reason:
        exclude_reasons.append(candidate.exclude_reason)
    if is_generic_career_url(candidate.url):
        exclude_reasons.append("generic-url")
    if deadline["deadline_status"] == "closed":
        exclude_reasons.append("expired-deadline")

    source = candidate.source
    if source in {"Official reference page", "Naver News Search"}:
        source = source_label_for_url(candidate.url, source)
    elif source.startswith("http"):
        source = source_label_for_url(candidate.url, source)

    return {
        "category": WEEKLY_CAREER_CATEGORY_ID,
        "sub_category": sub_category,
        "title": candidate.title,
        "url": candidate.url,
        "source_url": candidate.source_url,
        "source": source,
        "company_or_host": company_or_host,
        "type": career_type,
        "role": infer_career_role(text, career_type),
        "deadline": deadline["deadline"],
        "deadline_text": deadline["deadline_text"],
        "deadline_status": deadline["deadline_status"],
        "days_until_deadline": deadline["days_until_deadline"],
        "target": infer_target(text, career_type),
        "tech_keywords": infer_tech_keywords(text),
        "process_or_deliverable": infer_process_or_deliverable(text, career_type),
        "summary": candidate.summary,
        "published_at": format_kst(candidate.published_at) if candidate.published_at else "",
        "query": candidate.query,
        "score": score_payload["score"],
        "deadline_clarity_score": score_payload["deadline_clarity_score"],
        "backend_fit_score": score_payload["backend_fit_score"],
        "entry_fit_score": score_payload["entry_fit_score"],
        "portfolio_fit_score": score_payload["portfolio_fit_score"],
        "source_reliability_score": score_payload["source_reliability_score"],
        "actionability_score": score_payload["actionability_score"],
        "exclude_reason": ",".join(dict.fromkeys(exclude_reasons)),
    }


def dedupe_weekly_career_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen_urls: set[str] = set()
    seen_keys: set[tuple[str, str, str]] = set()
    for item in sorted(items, key=lambda value: int(value.get("score", 0)), reverse=True):
        normalized_url = normalize_url(str(item.get("url", "")))
        if normalized_url and normalized_url in seen_urls:
            continue
        key = (
            normalize_title(str(item.get("title", ""))),
            normalize_title(str(item.get("company_or_host", ""))),
            str(item.get("deadline_text", "")),
        )
        if key in seen_keys:
            continue
        if normalized_url:
            seen_urls.add(normalized_url)
        seen_keys.add(key)
        deduped.append(item)
    return deduped


def build_weekly_career_payload(
    category_id: str,
    generated_at: datetime,
    items: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "category": category_id,
        "generated_at": format_kst(generated_at),
        "items": dedupe_weekly_career_items(items),
    }


def output_path_for_category(
    output_dir: Path,
    category: dict[str, object],
) -> Path:
    configured = str(category.get("output_file", "")).strip()
    if configured:
        return Path(configured)
    category_id = str(category.get("id", "")).strip()
    return output_dir / f"{category_id}.json"


def write_category_output(
    output_dir: Path,
    category: dict[str, object],
    generated_at: datetime,
    candidates: list[Candidate] | list[OssIssueCandidate],
) -> None:
    category_id = str(category.get("id", "")).strip()
    output_path = output_path_for_category(output_dir, category)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        weekly_items = [
            standardize_weekly_career_candidate(candidate, generated_at)
            for candidate in candidates
            if isinstance(candidate, Candidate)
        ]
        payload = build_weekly_career_payload(category_id, generated_at, weekly_items)
    elif category_id == OSS_CATEGORY_ID:
        payload = {
            "schema_version": 2,
            "category": category_id,
            "generated_at": format_kst(generated_at),
            "verification_policy": (
                "Only safe_to_recommend=true issues are included in items. "
                "Maintainer authorship, assignee absence, linked work absence, "
                "and claim comment absence must all be verified."
            ),
            "items": [
                serialize_oss_issue_candidate(candidate)
                for candidate in candidates
                if isinstance(candidate, OssIssueCandidate) and candidate.safe_to_recommend
            ],
            "excluded": [],
        }
    else:
        payload = {
            "category": category_id,
            "generated_at": format_kst(generated_at),
            "items": [serialize_candidate(candidate) for candidate in candidates],
        }
    write_json_file(output_path, payload)
    print(f"Wrote {len(candidates)} candidate(s): {output_path}")


def write_daily_tech_alias_outputs(
    generated_at: datetime,
    candidates_by_category: dict[str, list[Candidate] | list[OssIssueCandidate]],
) -> None:
    for source_category_id, (alias_category_id, output_path) in DAILY_TECH_ALIAS_OUTPUTS.items():
        candidates = candidates_by_category.get(source_category_id, [])
        payload = {
            "category": alias_category_id,
            "generated_at": format_kst(generated_at),
            "source_category": source_category_id,
            "items": [serialize_candidate(candidate) for candidate in candidates],
        }
        write_json_file(output_path, payload)
        print(f"Wrote {len(candidates)} candidate(s): {output_path}")


def write_weekly_career_split_outputs(
    generated_at: datetime,
    candidates: list[Candidate] | list[OssIssueCandidate],
) -> None:
    weekly_items = [
        standardize_weekly_career_candidate(candidate, generated_at)
        for candidate in candidates
        if isinstance(candidate, Candidate)
    ]
    grouped: dict[Path, list[dict[str, object]]] = {
        output_path: [] for output_path in WEEKLY_CAREER_EMPTY_OUTPUTS
    }
    for item in weekly_items:
        sub_category = str(item.get("sub_category", ""))
        output_path = WEEKLY_CAREER_SPLIT_OUTPUTS.get(sub_category)
        if output_path is None:
            continue
        grouped.setdefault(output_path, []).append(item)

    category_by_path = {
        Path("reports/candidates/kr-backend-intern-jobs.json"): "kr-backend-intern-jobs",
        Path("reports/candidates/kr-backend-entry-jobs.json"): "kr-backend-entry-jobs",
        Path("reports/candidates/kr-backend-career-activities.json"): (
            "kr-backend-career-activities"
        ),
        Path("reports/candidates/kr-backend-company-watchlist.json"): (
            "kr-backend-company-watchlist"
        ),
    }
    for output_path, items in grouped.items():
        payload = build_weekly_career_payload(
            category_by_path.get(output_path, output_path.stem),
            generated_at,
            items,
        )
        write_json_file(output_path, payload)
        print(f"Wrote {len(payload['items'])} candidate(s): {output_path}")


def load_company_watchlist(path: Path = COMPANY_CAREER_WATCHLIST_PATH) -> list[dict[str, object]]:
    if not path.exists():
        return []
    data = load_required_json(path)
    companies = data.get("companies", [])
    if not isinstance(companies, list):
        raise RuntimeError("configs/company-career-watchlist.json must contain companies.")
    return [company for company in companies if isinstance(company, dict)]


def collect_company_watchlist_candidates(
    category: dict[str, object],
    current_time: datetime,
    penalty_keywords: list[str],
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for company in load_company_watchlist():
        name = str(company.get("name", "")).strip()
        source = str(company.get("source", "")).strip() or f"{name} Careers"
        url = str(company.get("career_url", "")).strip()
        if not name or not url:
            continue
        positive = " ".join(str(item) for item in company.get("positive_keywords", []) if item)
        summary = (
            f"{name} 공식 채용 watchlist 후보입니다. "
            f"백엔드 인턴, 신입, 주니어, 서버 개발 공고를 확인합니다. "
            f"positive_keywords: {positive}."
        )
        candidate = build_candidate(
            category=category,
            title=f"{source} official backend entry/intern watchlist",
            url=url,
            source_url=url,
            source=source,
            publisher=name,
            published_at=None,
            summary=summary,
            query="company_watchlist",
            source_reliability="official",
            current_time=current_time,
            penalty_keywords=penalty_keywords,
        )
        if candidate:
            candidates.append(candidate)
    return candidates


def collect_category(
    config: dict[str, object],
    category: dict[str, object],
    credentials: tuple[str, str] | None,
    current_time: datetime,
    penalty_keywords: list[str],
    dry_run: bool,
) -> list[Candidate] | list[OssIssueCandidate]:
    if dry_run:
        return []

    category_id = str(category.get("id", "")).strip()
    if category_id == OSS_CATEGORY_ID:
        return collect_oss_issue_candidates(category, current_time)

    candidates = collect_feed_candidates(config, category, current_time, penalty_keywords)
    candidates.extend(
        collect_reference_candidates(config, category, current_time, penalty_keywords)
    )
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        candidates.extend(
            collect_company_watchlist_candidates(category, current_time, penalty_keywords)
        )
    if credentials:
        candidates.extend(
            collect_naver_candidates(
                config,
                category,
                credentials,
                current_time,
                penalty_keywords,
            )
        )
    return sort_and_limit(category, candidates, current_time)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    output_dir = Path(args.output_dir)
    current_time = now_kst()

    try:
        if args.mode == "daily-tech":
            write_backend_practical_candidate(current_time)

        config = load_config(config_path, args.category, args.mode)
        credentials = get_naver_credentials(args.dry_run)
        penalty_keywords = [
            str(keyword).strip()
            for keyword in config.get("penalty_keywords", [])
            if str(keyword).strip()
        ]
        categories = config.get("categories", [])
        if not isinstance(categories, list):
            raise RuntimeError("configs/kr-sources.json must contain a categories array.")

        candidates_by_category: dict[str, list[Candidate] | list[OssIssueCandidate]] = {}
        for category in categories:
            if not isinstance(category, dict):
                continue
            candidates = collect_category(
                config,
                category,
                credentials,
                current_time,
                penalty_keywords,
                args.dry_run,
            )
            category_id = str(category.get("id", "")).strip()
            if category_id:
                candidates_by_category[category_id] = candidates
            write_category_output(output_dir, category, current_time, candidates)

        if args.mode == "daily-tech":
            write_daily_tech_alias_outputs(current_time, candidates_by_category)
            write_ps_routine_output(
                current_time,
                dry_run=args.dry_run,
                record_assignment=True,
            )
        if args.mode == "weekly-career":
            write_weekly_career_split_outputs(
                current_time,
                candidates_by_category.get(WEEKLY_CAREER_CATEGORY_ID, []),
            )
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to collect KR candidates: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
