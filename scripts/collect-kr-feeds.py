#!/usr/bin/env python3
"""Collect Korean Career Feed candidates and Weekly Career site radar data."""

from __future__ import annotations

import argparse
import copy
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
from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
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
WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE = 24
WEEKLY_MAX_DETAIL_PAGES = 80
DEFAULT_DISPLAY = 10
MAX_DISPLAY = 20
DEFAULT_MAX_CANDIDATES = 30
OSS_REPOSITORIES_CONFIG_PATH = Path("configs/oss-repositories.json")
PS_CURRICULUM_PATH = Path("configs/programmers-ps-curriculum.json")
PS_PROGRESS_PATH = Path("data/ps-progress.json")
PS_ROUTINE_OUTPUT_PATH = Path("reports/candidates/ps-weekly-routine.json")
COMPANY_CAREER_WATCHLIST_PATH = Path("configs/company-career-watchlist.json")
WEEKLY_CAREER_SOURCES_CONFIG_PATH = Path("configs/weekly-career-sources.json")
WEEKLY_CAREER_COVERAGE_CONFIG_PATH = Path("configs/weekly-career-coverage.json")
WEEKLY_CAREER_SITE_RADAR_CONFIG_PATH = Path("configs/weekly-career-site-radar.json")
WEEKLY_CAREER_SITE_RADAR_OUTPUT_PATH = Path(
    "reports/candidates/weekly-career-site-radar.json"
)
WEEKLY_CAREER_BRIEF_OUTPUT_PATH = Path("reports/briefs/kr-backend-career-weekly.md")
WEEKLY_SITE_RADAR_SECTION_IDS = {
    "official-careers",
    "job-intern-platforms",
    "activities-competitions",
}
WEEKLY_SITE_RADAR_REQUIRED_SITE_FIELDS = (
    "id",
    "name",
    "applies_to",
    "links",
    "search_keywords",
    "exclude_keywords",
    "check_rule",
)
WEEKLY_SITE_RADAR_NEWS_DOMAINS = {
    "news.naver.com",
    "n.news.naver.com",
    "etnews.com",
    "zdnet.co.kr",
    "bloter.net",
    "aitimes.com",
    "itworld.co.kr",
    "ciokorea.com",
    "ddaily.co.kr",
    "hankyung.com",
    "chosun.com",
    "joongang.co.kr",
    "donga.com",
    "yna.co.kr",
    "newsis.com",
    "newswire.co.kr",
    "prnewswire.com",
    "prtimes.jp",
}
BACKEND_PRACTICAL_CURRICULUM_PATH = Path(
    "configs/backend-practical-knowledge-curriculum.json"
)
BACKEND_PRACTICAL_OUTPUT_PATH = Path(
    "reports/candidates/backend-practical-knowledge.json"
)
BACKEND_CORE_CS_CURRICULUM_PATH = Path("configs/backend-core-cs-curriculum.json")
BACKEND_CORE_CS_OUTPUT_PATH = Path("reports/candidates/cs-core-daily-topic.json")
BACKEND_TERMS_GLOSSARY_PATH = Path("configs/backend-terms-glossary.json")
BACKEND_TERM_OUTPUT_PATH = Path("reports/candidates/backend-term-daily.json")
CS_CORE_REQUIRED_TRACKS = {
    "computer-architecture",
    "operating-system",
    "network",
    "database",
    "jvm-runtime",
}
USER_AGENT = "career-feed-kr-collector"
SUPPORTED_FEED_TYPES = {"rss", "atom"}
OSS_CATEGORY_ID = "kr-oss-contribution-opportunities"
AI_TECH_CATEGORY_ID = "kr-ai-tech-news"
BACKEND_TECH_CATEGORY_ID = "kr-backend-tech-news"
SPRING_JVM_STUDY_CATEGORY_ID = "spring-jvm-study-topics"
WEEKLY_CAREER_CATEGORY_ID = "kr-backend-career-events"
WEEKLY_CATEGORY_ORDER = ["job", "intern", "hackathon", "contest", "competition"]
WEEKLY_CATEGORY_LABELS = {
    "job": "채용",
    "intern": "인턴",
    "hackathon": "해커톤",
    "contest": "공모전",
    "competition": "경진대회",
}
WEEKLY_CATEGORY_OUTPUTS = {
    "job": Path("reports/candidates/kr-backend-jobs.json"),
    "intern": Path("reports/candidates/kr-backend-interns.json"),
    "hackathon": Path("reports/candidates/kr-backend-hackathons.json"),
    "contest": Path("reports/candidates/kr-backend-contests.json"),
    "competition": Path("reports/candidates/kr-backend-competitions.json"),
}
WEEKLY_COMPAT_SUB_CATEGORY_TO_WEEKLY_CATEGORY = {
    "entry_job": "job",
    "junior_job": "job",
    "company_watchlist": "job",
    "intern_job": "intern",
    "hackathon": "hackathon",
    "contest": "contest",
    "competition": "competition",
}
WEEKLY_CAREER_SPLIT_OUTPUTS = {
    "intern_job": Path("reports/candidates/kr-backend-intern-jobs.json"),
    "entry_job": Path("reports/candidates/kr-backend-entry-jobs.json"),
    "junior_job": Path("reports/candidates/kr-backend-entry-jobs.json"),
    "hackathon": Path("reports/candidates/kr-backend-career-activities.json"),
    "contest": Path("reports/candidates/kr-backend-career-activities.json"),
    "competition": Path("reports/candidates/kr-backend-career-activities.json"),
    "company_watchlist": Path("reports/candidates/kr-backend-company-watchlist.json"),
}
WEEKLY_COMPAT_EMPTY_OUTPUTS = [
    Path("reports/candidates/kr-backend-intern-jobs.json"),
    Path("reports/candidates/kr-backend-entry-jobs.json"),
    Path("reports/candidates/kr-backend-career-activities.json"),
    Path("reports/candidates/kr-backend-company-watchlist.json"),
]
WEEKLY_CAREER_EMPTY_OUTPUTS = WEEKLY_COMPAT_EMPTY_OUTPUTS + list(WEEKLY_CATEGORY_OUTPUTS.values())
WEEKLY_CAREER_COMPAT_OUTPUT_CATEGORIES = {
    Path("reports/candidates/kr-backend-career-events.json"): (
        "kr-backend-career-events"
    ),
    Path("reports/candidates/kr-backend-jobs.json"): "kr-backend-jobs",
    Path("reports/candidates/kr-backend-interns.json"): "kr-backend-interns",
    Path("reports/candidates/kr-backend-hackathons.json"): "kr-backend-hackathons",
    Path("reports/candidates/kr-backend-contests.json"): "kr-backend-contests",
    Path("reports/candidates/kr-backend-competitions.json"): "kr-backend-competitions",
}
WEEKLY_CATEGORY_DISCOVERY_BUDGETS = {
    "job": {"listing_pages": 12, "detail_urls": 80, "detail_pages": 30},
    "intern": {"listing_pages": 10, "detail_urls": 80, "detail_pages": 30},
    "hackathon": {"listing_pages": 8, "detail_urls": 50, "detail_pages": 20},
    "contest": {"listing_pages": 8, "detail_urls": 50, "detail_pages": 20},
    "competition": {"listing_pages": 8, "detail_urls": 50, "detail_pages": 20},
}
WEEKLY_CATEGORY_CACHE_MAX_AGE_DAYS = {
    "job": 45,
    "intern": 45,
    "hackathon": 60,
    "contest": 60,
    "competition": 60,
}
DAILY_TECH_ALIAS_OUTPUTS: dict[str, tuple[str, Path]] = {}
RELIABILITY_SCORE = {
    "official": 20,
    "major_media": 12,
    "platform": 10,
    "aggregator": 5,
    "unknown": 0,
}
MODE_CATEGORY_IDS = {
    "daily-tech": {
        AI_TECH_CATEGORY_ID,
        BACKEND_TECH_CATEGORY_ID,
        SPRING_JVM_STUDY_CATEGORY_ID,
        OSS_CATEGORY_ID,
    },
    "daily-backend": {
        SPRING_JVM_STUDY_CATEGORY_ID,
        OSS_CATEGORY_ID,
    },
    "daily-news": {
        AI_TECH_CATEGORY_ID,
        BACKEND_TECH_CATEGORY_ID,
    },
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
WEEKLY_BACKEND_DIRECT_KEYWORDS = BACKEND_KEYWORDS + [
    "rest api",
    "spring boot",
    "database",
    "데이터베이스",
    "mysql",
    "postgresql",
    "redis",
    "클라우드",
    "aws",
    "인프라",
    "devops",
    "웹서비스 개발",
]
WEEKLY_BACKEND_ADJACENT_KEYWORDS = [
    "시스템개발",
    "시스템 개발",
    "응용프로그램개발",
    "응용프로그램 개발",
    "it/인터넷",
    "it·인터넷",
    "it 인터넷",
    "erp/시스템개발",
    "데이터",
    "ai 서비스",
    "llm",
    "플랫폼",
    "웹서비스 개발",
]
WEEKLY_NON_DEVELOPER_ONLY_KEYWORDS = [
    "마케팅",
    "광고",
    "홍보",
    "디자인",
    "영업",
    "경영",
    "사무",
    "콘텐츠",
    "미디어",
    "기획",
    "pm",
]
WEEKLY_DISCOVERY_SOURCE_PRIORITY = {
    "Linkareer Intern": 0,
    "Linkareer Activities": 1,
    "DACON Competitions": 2,
    "AI Factory": 3,
    "Programmers": 4,
    "Wanted": 5,
    "JobKorea": 6,
    "Jumpit": 7,
    "Saramin": 8,
}
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
WEEKLY_ALLOWED_SOURCE_KINDS = {
    "official_company_career_detail",
    "job_platform_detail",
    "activity_platform_detail",
    "government_program_detail",
}
WEEKLY_PAST_EVENT_KEYWORDS = [
    "수상",
    "2등 수상",
    "대상 수상",
    "개최했다",
    "성료",
    "마무리",
    "결과 발표",
    "선정",
    "후기",
    "리뷰",
    "참가 후기",
    "지난",
    "종료",
    "마감 종료",
    "접수 종료",
    "모집 종료",
    "지원 종료",
    "발표했다",
    "뉴스브리핑",
    "리뉴얼",
    "출시",
    "보도자료",
]
WEEKLY_DEADLINE_CONTEXT_KEYWORDS = [
    "마감",
    "접수",
    "지원",
    "모집",
    "신청",
    "참가",
    "서류",
    "기간",
    "까지",
    "~",
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
WEEKLY_CAREER_SOURCE_POLICY_CACHE: dict[str, object] | None = None
WEEKLY_CAREER_COVERAGE_CONFIG_CACHE: dict[str, object] | None = None
WEEKLY_CAREER_DISCOVERY_DIAGNOSTICS: dict[str, object] = {}
WEEKLY_CAREER_LAST_PAYLOAD: dict[str, object] | None = None
WEEKLY_CAREER_LAST_CATEGORY_PAYLOADS: dict[str, dict[str, object]] = {}
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
SOURCE_ERRORS: list[dict[str, str]] = []
WARNINGS: list[str] = []
OSS_GATE_EXCLUSION_COUNTS: Counter[str] = Counter()
OSS_REPOSITORY_DIAGNOSTICS: list[dict[str, object]] = []


def record_warning(message: str) -> None:
    WARNINGS.append(message)
    print(f"Warning: {message}", file=sys.stderr)


def record_source_error(
    source_name: str,
    message: str,
    *,
    category: str = "",
    source_type: str = "",
    error_type: str = "",
) -> None:
    error = {
        "source_name": source_name,
        "source_type": source_type,
        "category": category,
        "error": message,
    }
    if error_type:
        error["error_type"] = error_type
    SOURCE_ERRORS.append(error)
    print(f"Warning: {source_name}: {message}", file=sys.stderr)


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
class DeadlineInfo:
    deadline: str
    deadline_text: str
    deadline_status: str
    deadline_confidence: str
    deadline_source: str
    days_until_deadline: int | None


@dataclass(frozen=True)
class FieldWithConfidence:
    value: str
    confidence: str
    source: str


@dataclass(frozen=True)
class WeeklyDiscoveredUrl:
    url: str
    source: str
    listing_url: str


@dataclass(frozen=True)
class WeeklyCareerSourceAdapter:
    name: str
    domains: list[str]
    weekly_categories: list[str]
    listing_urls: list[str]
    detail_url_patterns: list[str]
    generic_url_patterns: list[str]
    source_kind: str
    priority: int
    max_listing_links: int
    max_detail_pages: int


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
    maintainer_triaged: bool
    maintainer_qualified: bool
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


@dataclass(frozen=True)
class GitHubLinkedWorkCheck:
    check_status: str
    linked_prs_count: int
    linked_branches_count: int
    has_linked_work: bool
    source: str
    timeline_page_complete: bool


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
        choices=["daily-tech", "daily-backend", "daily-news", "weekly-career"],
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


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.links.append(value)


class VisibleTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth and data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def html_to_visible_text(value: str) -> str:
    parser = VisibleTextExtractor()
    parser.feed(value or "")
    return parser.text()


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
    lowered = re.sub(
        r"\s*[-–—|:]\s*(전자신문|zdnet korea|지디넷코리아|블로터|"
        r"ai타임스|디지털데일리|itworld|cio korea)\s*$",
        " ",
        lowered,
        flags=re.IGNORECASE,
    )
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
        record_warning(
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
    record_warning(
        "missing optional environment variable(s): "
        f"{', '.join(missing)}. Naver News Search API collection skipped; "
        "RSS/reference candidates will still be collected."
    )
    return None


def get_github_token() -> str | None:
    for env_name in GITHUB_TOKEN_ENV_NAMES:
        token = os.environ.get(env_name, "").strip()
        if token:
            return token
    record_warning(
        "GITHUB_TOKEN/GH_TOKEN is not set. "
        "GitHub Issues collection will use the public unauthenticated API "
        "and may hit rate limits."
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


def load_weekly_career_site_radar_config(
    path: Path = WEEKLY_CAREER_SITE_RADAR_CONFIG_PATH,
) -> dict[str, object]:
    data = load_required_json(path)
    normalized, _diagnostics = normalize_weekly_career_site_radar_config(data)
    return normalized


def weekly_site_radar_domain(url: str) -> str:
    domain = urllib.parse.urlsplit(url).netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def is_weekly_site_radar_news_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    domain = weekly_site_radar_domain(url)
    if any(
        domain == blocked or domain.endswith(f".{blocked}")
        for blocked in WEEKLY_SITE_RADAR_NEWS_DOMAINS
    ):
        return True
    lowered = f"{domain}{parsed.path}".lower()
    return bool(re.search(r"(?:^|[./_-])(news|press|pr)(?:[./_-]|$)", lowered))


def require_non_empty_string_list(value: object, field: str, context: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"Weekly career radar {context} needs non-empty {field}.")
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    if not cleaned:
        raise RuntimeError(f"Weekly career radar {context} needs non-empty {field}.")
    return cleaned


def normalize_weekly_career_site_radar_config(
    data: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    normalized = copy.deepcopy(data)
    sections = data.get("sections", [])
    if not isinstance(sections, list) or not sections:
        raise RuntimeError("configs/weekly-career-site-radar.json must contain sections.")

    seen_ids: set[str] = set()
    seen_site_ids: set[str] = set()
    seen_site_names: set[str] = set()
    seen_urls: set[str] = set()
    duplicate_urls: list[str] = []
    site_count = 0
    link_count = 0
    normalized_sections = normalized.get("sections", [])
    if not isinstance(normalized_sections, list):
        raise RuntimeError("configs/weekly-career-site-radar.json must contain sections.")

    for section_index, section in enumerate(sections):
        if not isinstance(section, dict):
            raise RuntimeError("Every weekly career radar section must be an object.")
        section_id = str(section.get("id", "")).strip()
        label = str(section.get("label", "")).strip()
        description = str(section.get("description", "")).strip()
        sites = section.get("sites", [])
        if not section_id or not label or not description:
            raise RuntimeError("Every weekly career radar section needs id, label, and description.")
        if section_id in seen_ids:
            raise RuntimeError(f"Duplicate weekly career radar section id: {section_id}")
        seen_ids.add(section_id)
        if not isinstance(sites, list) or not sites:
            raise RuntimeError(f"Weekly career radar section has no sites: {section_id}")
        normalized_section = normalized_sections[section_index]
        if not isinstance(normalized_section, dict):
            raise RuntimeError("Every weekly career radar section must be an object.")
        normalized_sites = normalized_section.get("sites", [])
        if not isinstance(normalized_sites, list):
            raise RuntimeError(f"Weekly career radar section has no sites: {section_id}")

        for site_index, site in enumerate(sites):
            if not isinstance(site, dict):
                raise RuntimeError(f"Weekly career radar site must be an object: {section_id}")
            context = f"{section_id}/{site.get('id', site.get('name', 'unknown'))}"
            for field in WEEKLY_SITE_RADAR_REQUIRED_SITE_FIELDS:
                if field not in site:
                    raise RuntimeError(
                        f"Weekly career radar site is missing {field}: {context}"
                    )
            site_id = str(site.get("id", "")).strip()
            name = str(site.get("name", "")).strip()
            check_rule = str(site.get("check_rule", "")).strip()
            if not site_id or not name or not check_rule:
                raise RuntimeError(f"Weekly career radar site needs id, name, and check_rule: {context}")
            if site_id in seen_site_ids:
                raise RuntimeError(f"Duplicate weekly career radar site id: {site_id}")
            if name in seen_site_names:
                raise RuntimeError(f"Duplicate weekly career radar site name: {name}")
            seen_site_ids.add(site_id)
            seen_site_names.add(name)
            require_non_empty_string_list(site.get("applies_to"), "applies_to", context)
            require_non_empty_string_list(site.get("search_keywords"), "search_keywords", context)
            require_non_empty_string_list(site.get("exclude_keywords"), "exclude_keywords", context)

            links = site.get("links", [])
            if not isinstance(links, list) or not links:
                raise RuntimeError(f"Weekly career radar site needs links: {context}")
            normalized_site = normalized_sites[site_index]
            if not isinstance(normalized_site, dict):
                raise RuntimeError(f"Weekly career radar site must be an object: {section_id}")
            normalized_links: list[dict[str, str]] = []
            for link in links:
                if not isinstance(link, dict):
                    raise RuntimeError(f"Weekly career radar link must be an object: {context}")
                label = str(link.get("label", "")).strip()
                url = str(link.get("url", "")).strip()
                if not label or not url:
                    raise RuntimeError(f"Weekly career radar link needs label and url: {context}")
                parsed = urllib.parse.urlsplit(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise RuntimeError(f"Weekly career radar link must use http(s): {context}")
                if is_weekly_site_radar_news_url(url):
                    raise RuntimeError(f"Weekly career radar link must not use news URL: {context}")
                normalized_url = normalize_url(url)
                if normalized_url in seen_urls:
                    duplicate_urls.append(url)
                    continue
                seen_urls.add(normalized_url)
                normalized_links.append({"label": label, "url": url})
            if not normalized_links:
                raise RuntimeError(f"Weekly career radar site has no unique links: {context}")
            normalized_site["links"] = normalized_links
            site_count += 1
            link_count += len(normalized_links)

    required_ids = WEEKLY_SITE_RADAR_SECTION_IDS
    if seen_ids != required_ids:
        missing = sorted(required_ids - seen_ids)
        extra = sorted(seen_ids - required_ids)
        raise RuntimeError(
            "Weekly career radar section id mismatch: "
            f"missing={missing} extra={extra}"
        )
    diagnostics = {
        "site_count": site_count,
        "link_count": link_count,
        "duplicate_urls_removed": len(duplicate_urls),
        "duplicate_urls": duplicate_urls,
    }
    return normalized, diagnostics


def build_weekly_career_site_radar_payload(generated_at: datetime) -> dict[str, object]:
    config = load_required_json(WEEKLY_CAREER_SITE_RADAR_CONFIG_PATH)
    normalized, diagnostics = normalize_weekly_career_site_radar_config(config)
    return {
        "category": "weekly-career-site-radar",
        "generated_at": format_kst(generated_at),
        "schema_version": int(normalized.get("schema_version", 1) or 1),
        "timezone": str(normalized.get("timezone", "Asia/Seoul")),
        "audience": str(normalized.get("audience", "")),
        "title": str(normalized.get("title", "Backend Career Site Radar")),
        "site_count": diagnostics["site_count"],
        "link_count": diagnostics["link_count"],
        "duplicate_urls_removed": diagnostics["duplicate_urls_removed"],
        "diagnostics": diagnostics,
        "sections": normalized["sections"],
    }


def build_disabled_weekly_career_compat_payload(
    category: str,
    generated_at: datetime,
) -> dict[str, object]:
    return {
        "category": category,
        "generated_at": format_kst(generated_at),
        "items": [],
        "diagnostics": {
            "status": "disabled",
            "reason": "Weekly Career now uses manual site radar instead of automated candidate recommendation.",
        },
    }


def render_weekly_career_site_radar_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Career Feed - Backend Career Site Radar",
        f"기준시각: {payload['generated_at']}",
        "",
        "이번 실행 목적:",
        "- 자동 추천 없이, 직접 확인할 백엔드 커리어 사이트와 검색 키워드를 정리합니다.",
        "",
    ]

    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        raise RuntimeError("Weekly career radar payload sections must be a list.")
    for index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            continue
        lines.append(f"## {index}. {section.get('label', '')}")
        sites = section.get("sites", [])
        if not isinstance(sites, list):
            sites = []
        for site in sites:
            if not isinstance(site, dict):
                continue
            name = str(site.get("name", "")).strip()
            applies_to = ", ".join(
                str(item).strip()
                for item in site.get("applies_to", [])
                if str(item).strip()
            )
            links = site.get("links", [])
            if not isinstance(links, list):
                links = []
            rendered_links = ", ".join(
                f"[{str(link.get('label', '')).strip()}]({str(link.get('url', '')).strip()})"
                for link in links
                if isinstance(link, dict)
                and str(link.get("label", "")).strip()
                and str(link.get("url", "")).strip()
            )
            search_keywords = ", ".join(
                str(item).strip()
                for item in site.get("search_keywords", [])
                if str(item).strip()
            )
            exclude_keywords = ", ".join(
                str(item).strip()
                for item in site.get("exclude_keywords", [])
                if str(item).strip()
            )
            check_rule = str(site.get("check_rule", "")).strip()
            lines.extend(
                [
                    f"### {name}",
                    f"- 확인 유형: {applies_to}",
                    f"- 바로가기: {rendered_links}",
                    f"- 검색 키워드: {search_keywords}",
                    f"- 제외 키워드: {exclude_keywords}",
                    f"- 확인 기준: {check_rule}",
                    "",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## 30분 확인 루틴",
            "1. 공식 채용 사이트 2곳을 열고 Backend/Server/Intern 키워드로 확인합니다.",
            "2. 채용·인턴 플랫폼 2곳을 열고 채용연계형/체험형 인턴을 확인합니다.",
            "3. 대외활동/대회 플랫폼 2곳을 열고 API 서버나 DB 산출물이 남는 활동만 북마크합니다.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_weekly_career_site_radar_payload(generated_at: datetime) -> dict[str, object]:
    radar_payload = build_weekly_career_site_radar_payload(generated_at)
    write_json_file(WEEKLY_CAREER_SITE_RADAR_OUTPUT_PATH, radar_payload)
    return radar_payload


def write_weekly_career_site_radar_report(
    generated_at: datetime,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    radar_payload = payload or write_weekly_career_site_radar_payload(generated_at)
    if payload is not None:
        write_json_file(WEEKLY_CAREER_SITE_RADAR_OUTPUT_PATH, radar_payload)
    WEEKLY_CAREER_BRIEF_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEEKLY_CAREER_BRIEF_OUTPUT_PATH.write_text(
        render_weekly_career_site_radar_markdown(radar_payload),
        encoding="utf-8",
    )
    return radar_payload


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


def load_weekly_career_source_policy(
    path: Path = WEEKLY_CAREER_SOURCES_CONFIG_PATH,
) -> dict[str, object]:
    global WEEKLY_CAREER_SOURCE_POLICY_CACHE
    if WEEKLY_CAREER_SOURCE_POLICY_CACHE is not None:
        return WEEKLY_CAREER_SOURCE_POLICY_CACHE
    if not path.exists():
        WEEKLY_CAREER_SOURCE_POLICY_CACHE = {
            "allowed_final_sources": [],
            "company_watchlist": [],
            "blocked_final_domains": [],
        }
        return WEEKLY_CAREER_SOURCE_POLICY_CACHE
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("configs/weekly-career-sources.json must contain a JSON object.")
    WEEKLY_CAREER_SOURCE_POLICY_CACHE = data
    return data


def default_weekly_career_coverage_config() -> dict[str, object]:
    return {
        "schema_version": 1,
        "timezone": "Asia/Seoul",
        "weekly_categories": [
            {
                "id": "job",
                "label": "채용",
                "target_min": 1,
                "target_max": 1,
                "fresh_first": True,
                "allow_cache_backfill": True,
                "max_cache_age_days": 45,
                "source_priority": [
                    "NAVER Careers",
                    "Kakao Careers",
                    "LINE Careers",
                    "Coupang Jobs",
                    "Woowa Careers",
                    "Toss Careers",
                    "Daangn Careers",
                    "Wanted",
                    "Jumpit",
                    "Saramin",
                    "JobKorea",
                ],
            },
            {
                "id": "intern",
                "label": "인턴",
                "target_min": 1,
                "target_max": 1,
                "fresh_first": True,
                "allow_cache_backfill": True,
                "max_cache_age_days": 45,
                "source_priority": [
                    "Linkareer Intern",
                    "Work24",
                    "ZeroBase Zero Intern",
                    "Saramin",
                    "JobKorea",
                    "Wanted",
                ],
            },
            {
                "id": "hackathon",
                "label": "해커톤",
                "target_min": 1,
                "target_max": 1,
                "fresh_first": True,
                "allow_cache_backfill": True,
                "max_cache_age_days": 60,
                "source_priority": [
                    "Linkareer Activities",
                    "Programmers",
                    "AI Factory",
                    "DACON",
                    "Wevity",
                    "All-Con",
                ],
            },
            {
                "id": "contest",
                "label": "공모전",
                "target_min": 1,
                "target_max": 1,
                "fresh_first": True,
                "allow_cache_backfill": True,
                "max_cache_age_days": 60,
                "source_priority": [
                    "Linkareer Activities",
                    "Wevity",
                    "All-Con",
                    "DACON",
                    "Programmers",
                    "AI Factory",
                ],
            },
            {
                "id": "competition",
                "label": "경진대회",
                "target_min": 1,
                "target_max": 1,
                "fresh_first": True,
                "allow_cache_backfill": True,
                "max_cache_age_days": 60,
                "source_priority": [
                    "DACON",
                    "AI Factory",
                    "Programmers",
                    "Linkareer Activities",
                    "Wevity",
                    "All-Con",
                ],
            },
        ],
    }


def load_weekly_career_coverage_config(
    path: Path = WEEKLY_CAREER_COVERAGE_CONFIG_PATH,
) -> dict[str, object]:
    global WEEKLY_CAREER_COVERAGE_CONFIG_CACHE
    if WEEKLY_CAREER_COVERAGE_CONFIG_CACHE is not None:
        return WEEKLY_CAREER_COVERAGE_CONFIG_CACHE
    if not path.exists():
        WEEKLY_CAREER_COVERAGE_CONFIG_CACHE = default_weekly_career_coverage_config()
        return WEEKLY_CAREER_COVERAGE_CONFIG_CACHE
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("configs/weekly-career-coverage.json must contain a JSON object.")
    WEEKLY_CAREER_COVERAGE_CONFIG_CACHE = data
    return data


def weekly_coverage_categories(config: dict[str, object] | None = None) -> list[dict[str, object]]:
    payload = config or load_weekly_career_coverage_config()
    categories = payload.get("weekly_categories", [])
    if not isinstance(categories, list):
        return []
    by_id = {
        str(category.get("id", "")).strip(): category
        for category in categories
        if isinstance(category, dict)
    }
    return [by_id[key] for key in WEEKLY_CATEGORY_ORDER if key in by_id]


def weekly_category_config(
    weekly_category: str,
    config: dict[str, object] | None = None,
) -> dict[str, object]:
    for category in weekly_coverage_categories(config):
        if str(category.get("id", "")).strip() == weekly_category:
            return category
    return {
        "id": weekly_category,
        "label": WEEKLY_CATEGORY_LABELS.get(weekly_category, weekly_category),
        "target_min": 1,
        "target_max": 1,
        "fresh_first": True,
        "allow_cache_backfill": True,
        "max_cache_age_days": WEEKLY_CATEGORY_CACHE_MAX_AGE_DAYS.get(weekly_category, 45),
        "source_priority": [],
    }


def weekly_policy_list(key: str) -> list[dict[str, object]]:
    values = load_weekly_career_source_policy().get(key, [])
    return [value for value in values if isinstance(value, dict)] if isinstance(values, list) else []


def weekly_blocked_domains() -> list[str]:
    values = load_weekly_career_source_policy().get("blocked_final_domains", [])
    if not isinstance(values, list):
        return []
    return [str(value).strip().lower() for value in values if str(value).strip()]


def weekly_url_parts(url: str) -> tuple[str, str, str]:
    parsed = urllib.parse.urlsplit(url or "")
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    path = parsed.path or "/"
    signature = path.rstrip("/") if path != "/" else "/"
    if parsed.query:
        signature = f"{signature}?{parsed.query}"
    return domain, path.rstrip("/") if path != "/" else "/", signature


def is_weekly_career_static_asset_url(url: str) -> bool:
    path = urllib.parse.urlsplit(url or "").path.lower()
    return bool(
        re.search(
            r"\.(?:png|jpg|jpeg|gif|svg|webp|ico|css|js|woff2?|ttf|map)$",
            path,
        )
    )


def is_weekly_company_watchlist_detail_url(url: str) -> bool:
    domain, path, signature = weekly_url_parts(url)
    lowered_signature = signature.lower()
    if is_weekly_career_static_asset_url(url):
        return False
    if domain_matches(domain, ["recruit.navercorp.com"]):
        return "/rcrt/view.do" in lowered_signature
    if domain_matches(domain, ["careers.kakao.com"]):
        return path.startswith("/jobs/") or ("jobid=" in lowered_signature and path == "/jobs")
    if domain_matches(domain, ["careers.linecorp.com"]):
        return bool(re.search(r"^/(?:ko|en)/jobs/\d+", path))
    if domain_matches(domain, ["coupang.jobs"]):
        return bool(re.search(r"^/(?:en|ko/)?jobs/\d+", path))
    if domain_matches(domain, ["career.woowahan.com"]):
        return bool(re.search(r"^/jobs/\d+", path))
    if domain_matches(domain, ["toss.im"]):
        return path.startswith("/career/job-detail") or "job_id=" in lowered_signature
    if domain_matches(domain, ["about.daangn.com", "team.daangn.com"]):
        return bool(re.search(r"/jobs/\d+", path))
    return False


def weekly_pattern_matches(
    path: str,
    signature: str,
    pattern: str,
    *,
    allow_prefix: bool = True,
) -> bool:
    cleaned = pattern.strip()
    if not cleaned:
        return False
    if cleaned == "/":
        return path in {"", "/"} and signature in {"", "/"}
    if "?" in cleaned:
        return signature == cleaned or signature.startswith(f"{cleaned}&")
    normalized = cleaned.rstrip("/")
    if not allow_prefix:
        return path == normalized or signature.startswith(f"{normalized}?")
    return (
        path == normalized
        or path.startswith(f"{normalized}/")
        or signature.startswith(f"{normalized}?")
    )


def is_weekly_career_generic_url(url: str) -> bool:
    if is_weekly_career_static_asset_url(url):
        return True
    if is_generic_career_url(url):
        return True
    domain, path, signature = weekly_url_parts(url)
    for source in weekly_policy_list("allowed_final_sources"):
        source_domain = str(source.get("domain", "")).strip().lower()
        if not source_domain or not domain_matches(domain, [source_domain]):
            continue
        patterns = source.get("generic_url_patterns", [])
        if isinstance(patterns, list) and any(
            weekly_pattern_matches(path, signature, str(pattern), allow_prefix=False)
            for pattern in patterns
        ):
            return True
    return False


def is_weekly_reference_material_url(url: str) -> bool:
    domain, path, _signature = weekly_url_parts(url)
    return domain_matches(domain, ["linkareer.com"]) and path.startswith("/cover-letter/")


def is_allowed_weekly_career_final_domain(url: str) -> bool:
    domain = domain_from_url(url)
    if not domain or domain_matches(domain, weekly_blocked_domains()):
        return False
    for source in weekly_policy_list("allowed_final_sources"):
        source_domain = str(source.get("domain", "")).strip().lower()
        if source_domain and domain_matches(domain, [source_domain]):
            return True
    for company in weekly_policy_list("company_watchlist"):
        domains = company.get("domains", [])
        if isinstance(domains, list) and domain_matches(
            domain,
            [str(item).strip().lower() for item in domains if str(item).strip()],
        ):
            return True
    return False


def is_weekly_career_detail_url(url: str) -> bool:
    if is_weekly_reference_material_url(url):
        return False
    if not is_allowed_weekly_career_final_domain(url) or is_weekly_career_generic_url(url):
        return False
    domain, path, signature = weekly_url_parts(url)
    for source in weekly_policy_list("allowed_final_sources"):
        source_domain = str(source.get("domain", "")).strip().lower()
        if not source_domain or not domain_matches(domain, [source_domain]):
            continue
        patterns = source.get("detail_url_patterns", [])
        return isinstance(patterns, list) and any(
            weekly_pattern_matches(path, signature, str(pattern)) for pattern in patterns
        )
    for company in weekly_policy_list("company_watchlist"):
        domains = company.get("domains", [])
        if isinstance(domains, list) and domain_matches(
            domain,
            [str(item).strip().lower() for item in domains if str(item).strip()],
        ):
            return is_weekly_company_watchlist_detail_url(url)
    return False


def weekly_source_policy_for_url(url: str) -> dict[str, object] | None:
    domain = domain_from_url(url)
    for source in weekly_policy_list("allowed_final_sources"):
        source_domain = str(source.get("domain", "")).strip().lower()
        if source_domain and domain_matches(domain, [source_domain]):
            return source
    return None


def is_weekly_career_news_article(candidate_or_url: Candidate | str) -> bool:
    if isinstance(candidate_or_url, Candidate):
        source = candidate_or_url.source
        url = candidate_or_url.url
    else:
        source = ""
        url = str(candidate_or_url)
    domain = domain_from_url(url)
    if source == "Naver News Search":
        return True
    return domain_matches(domain, weekly_blocked_domains())


def infer_weekly_source_kind(url: str, source: str) -> str:
    if source == "Naver News Search" or is_weekly_career_news_article(url):
        return "news_article"
    if is_weekly_career_generic_url(url):
        return "generic_listing"
    domain = domain_from_url(url)
    for allowed in weekly_policy_list("allowed_final_sources"):
        source_domain = str(allowed.get("domain", "")).strip().lower()
        if source_domain and domain_matches(domain, [source_domain]) and is_weekly_career_detail_url(url):
            return str(allowed.get("source_kind", "unknown")).strip() or "unknown"
    for company in weekly_policy_list("company_watchlist"):
        domains = company.get("domains", [])
        if isinstance(domains, list) and domain_matches(
            domain,
            [str(item).strip().lower() for item in domains if str(item).strip()],
        ):
            return str(company.get("source_kind", "official_company_career_detail"))
    return "unknown"


def clean_weekly_discovery_url(url: str, base_url: str) -> str:
    absolute = urllib.parse.urljoin(base_url, html.unescape(url or ""))
    absolute, _fragment = urllib.parse.urldefrag(absolute)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    cleaned_pairs = [
        (key, value)
        for key, value in query_pairs
        if not (
            key.lower().startswith("utm_")
            or key.lower() in {"fbclid", "gclid", "igshid", "trk", "source"}
        )
    ]
    query = urllib.parse.urlencode(cleaned_pairs, doseq=True)
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, query, "")
    )


def extract_links_from_listing_page(
    html_body: str,
    base_url: str,
    source_policy: dict[str, object] | None = None,
) -> list[str]:
    parser = LinkExtractor()
    parser.feed(html_body or "")
    raw_links = list(parser.links)
    raw_links.extend(
        match.group(1)
        for match in re.finditer(
            r"""["']((?:https?:)?//[^"']+|/[^"']*(?:activity|competitions|competition|position|Recruit|zf_user/jobs|wd)[^"']*)["']""",
            html_body or "",
            flags=re.IGNORECASE,
        )
    )

    links: list[str] = []
    seen: set[str] = set()
    for raw_link in raw_links:
        cleaned = clean_weekly_discovery_url(raw_link, base_url)
        if not cleaned or cleaned in seen:
            continue
        if not is_allowed_weekly_career_final_domain(cleaned):
            continue
        if is_weekly_career_generic_url(cleaned):
            continue
        if not is_weekly_career_detail_url(cleaned):
            continue
        seen.add(cleaned)
        links.append(cleaned)
    return links


def fetch_weekly_career_detail_page(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 career-feed-kr-collector",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(content_type, errors="replace")


def empty_weekly_career_diagnostics() -> dict[str, object]:
    return {
        "reference_pages_total": 0,
        "reference_pages_fetched": 0,
        "detail_urls_discovered": 0,
        "detail_urls_after_dedup": 0,
        "detail_pages_fetched": 0,
        "detail_candidates_parsed": 0,
        "final_items": 0,
        "excluded_by_reason": {},
        "source_counts": {},
    }


def discover_weekly_career_detail_urls(
    reference_pages: list[dict[str, object]],
    source_policy: dict[str, object],
    max_links_per_source: int = WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE,
) -> tuple[list[WeeklyDiscoveredUrl], dict[str, object]]:
    diagnostics = empty_weekly_career_diagnostics()
    diagnostics["reference_pages_total"] = len(reference_pages)
    source_counts: dict[str, dict[str, object]] = {}
    discovered: list[WeeklyDiscoveredUrl] = []
    seen: set[str] = set()

    for page in reference_pages:
        name = str(page.get("name", "")).strip() or "Weekly source"
        url = str(page.get("url", "")).strip()
        if not url:
            continue
        source_counts.setdefault(
            name,
            {
                "listing_fetched": 0,
                "listing_fetch_failed": 0,
                "detail_urls_discovered": 0,
                "detail_pages_fetched": 0,
                "final_items": 0,
            },
        )

        if is_weekly_career_detail_url(url):
            cleaned = clean_weekly_discovery_url(url, url)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                discovered.append(WeeklyDiscoveredUrl(cleaned, name, url))
                source_counts[name]["detail_urls_discovered"] = (
                    int(source_counts[name]["detail_urls_discovered"]) + 1
                )
            continue

        try:
            listing_html = fetch_weekly_career_detail_page(url)
        except (OSError, UnicodeDecodeError, urllib.error.URLError, TimeoutError) as exc:
            source_counts[name]["listing_fetch_failed"] = (
                int(source_counts[name]["listing_fetch_failed"]) + 1
            )
            source_counts[name]["last_error"] = str(exc)[:160]
            continue

        diagnostics["reference_pages_fetched"] = int(diagnostics["reference_pages_fetched"]) + 1
        source_counts[name]["listing_fetched"] = int(source_counts[name]["listing_fetched"]) + 1
        detail_urls = extract_links_from_listing_page(
            listing_html,
            url,
            weekly_source_policy_for_url(url),
        )[:max_links_per_source]
        source_counts[name]["detail_urls_discovered"] = len(detail_urls)
        for detail_url in detail_urls:
            if detail_url in seen:
                continue
            seen.add(detail_url)
            discovered.append(WeeklyDiscoveredUrl(detail_url, name, url))

    diagnostics["detail_urls_discovered"] = sum(
        int(value.get("detail_urls_discovered", 0)) for value in source_counts.values()
    )
    diagnostics["detail_urls_after_dedup"] = len(discovered)
    diagnostics["source_counts"] = source_counts
    return discovered, diagnostics


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


def empty_deadline_info(source: str = "") -> DeadlineInfo:
    return DeadlineInfo(
        deadline="",
        deadline_text="",
        deadline_status="unknown",
        deadline_confidence="none",
        deadline_source=source,
        days_until_deadline=None,
    )


def deadline_info_from_payload(
    payload: dict[str, object],
    confidence: str,
    source: str,
) -> DeadlineInfo:
    return DeadlineInfo(
        deadline=str(payload.get("deadline", "")),
        deadline_text=str(payload.get("deadline_text", "")),
        deadline_status=str(payload.get("deadline_status", "unknown")),
        deadline_confidence=confidence,
        deadline_source=source,
        days_until_deadline=(
            payload.get("days_until_deadline")
            if isinstance(payload.get("days_until_deadline"), int)
            else None
        ),
    )


def has_deadline_context(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 28) : min(len(text), end + 28)]
    return text_contains_any(window, WEEKLY_DEADLINE_CONTEXT_KEYWORDS)


def extract_deadline_from_text(text: str, now_kst: datetime) -> DeadlineInfo:
    searchable = strip_html(text)
    if not searchable:
        return empty_deadline_info()
    if text_contains_any(searchable, EXPIRED_DEADLINE_KEYWORDS):
        return DeadlineInfo("", "", "closed", "high", "expired-keyword", None)
    if text_contains_any(searchable, ["상시채용", "상시 모집", "상시지원", "상시 영입"]):
        return DeadlineInfo("상시채용", "상시채용", "rolling", "high", "text", None)
    if text_contains_any(
        searchable,
        ["채용 시 마감", "채용시 마감", "영입종료시", "채용 완료 시", "채용 완료시"],
    ):
        return DeadlineInfo("채용 시 마감", "채용 시 마감", "until_filled", "high", "text", None)

    d_day = re.search(r"\bD\s*-\s*(\d{1,3})\b", searchable, flags=re.IGNORECASE)
    if d_day and has_deadline_context(searchable, d_day.start(), d_day.end()):
        days = int(d_day.group(1))
        deadline = now_kst.astimezone(KST) + timedelta(days=days)
        return DeadlineInfo(
            deadline.strftime("%Y-%m-%d 23:59:00 KST"),
            deadline.strftime("%Y-%m-%d 23:59 KST"),
            "open",
            "high",
            "d-day-text",
            days,
        )

    full_date_patterns = [
        r"(20\d{2})\s*[.\-/년]\s*(\d{1,2})\s*[.\-/월]\s*(\d{1,2})",
        r"(20\d{2})(\d{2})(\d{2})",
    ]
    for pattern in full_date_patterns:
        for match in re.finditer(pattern, searchable):
            if not has_deadline_context(searchable, match.start(), match.end()):
                continue
            parsed = deadline_payload_from_date(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                searchable,
                now_kst,
            )
            if parsed:
                return deadline_info_from_payload(parsed, "high", "deadline-text")

    month_day_patterns = [
        r"(?:~|마감|접수|지원|모집|까지|기간|일정)\s*(\d{1,2})\s*[./]\s*(\d{1,2})",
        r"(?:~|마감|접수|지원|모집|까지|기간|일정)\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일",
    ]
    for pattern in month_day_patterns:
        for match in re.finditer(pattern, searchable):
            year = now_kst.astimezone(KST).year
            month = int(match.group(1))
            day = int(match.group(2))
            parsed = deadline_payload_from_date(year, month, day, searchable, now_kst)
            if parsed and parsed["deadline_status"] != "closed":
                return deadline_info_from_payload(parsed, "high", "deadline-text")

    return empty_deadline_info()


def extract_company_or_host_from_text_or_url(text: str, url: str) -> FieldWithConfidence:
    if is_weekly_career_news_article(url):
        return FieldWithConfidence("", "none", "")
    domain = domain_from_url(url)
    for company in weekly_policy_list("company_watchlist"):
        domains = company.get("domains", [])
        if isinstance(domains, list) and domain_matches(
            domain,
            [str(item).strip().lower() for item in domains if str(item).strip()],
        ):
            return FieldWithConfidence(str(company.get("name", "")).strip(), "high", "domain")

    for pattern in [
        r"(?:회사|기업|주최|주관|운영기관|기관)\s*[:：]\s*(.+?)(?=\s+(?:마감일|채용형태|모집직무|지원자격|상태|유형|직무)|$)",
        r"(?:회사|기업|주최|주관|운영기관|기관)\s*[:：]\s*([^\n,;/|]{2,40})",
        r"(?:host|company|organizer)\s*[:：]\s*([^\n,;/|]{2,40})",
    ]:
        match = re.search(pattern, strip_html(text), flags=re.IGNORECASE)
        if not match:
            continue
        value = re.sub(r"\s+", " ", match.group(1)).strip(" -")
        if value == "NAVER" and not domain_matches(domain, ["recruit.navercorp.com"]):
            return FieldWithConfidence("", "none", "")
        return FieldWithConfidence(value, "high", "text")

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
        ("ZeroBase", ["zerobase", "zero intern", "제로베이스"]),
    ]
    lowered = text.lower()
    for label, keywords in known_names:
        if any(keyword.lower() in lowered for keyword in keywords):
            if label == "NAVER" and not domain_matches(domain, ["recruit.navercorp.com"]):
                return FieldWithConfidence("", "none", "")
            return FieldWithConfidence(label, "medium", "text")
    return FieldWithConfidence("", "none", "")


def extract_meta_content(html_body: str, key: str) -> str:
    patterns = [
        rf'<meta[^>]+property=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+name=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(key)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_body, flags=re.IGNORECASE)
        if match:
            return strip_html(match.group(1))
    return ""


def extract_html_title(html_body: str) -> str:
    meta_title = extract_meta_content(html_body, "og:title")
    if meta_title:
        return meta_title.split("|", 1)[0].strip()
    match = re.search(r"<title[^>]*>(.*?)</title>", html_body, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return strip_html(match.group(1)).split("|", 1)[0].strip()
    return ""


def extract_json_ld_objects(html_body: str) -> list[dict[str, object]]:
    objects: list[dict[str, object]] = []
    for match in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_body or "",
        flags=re.IGNORECASE | re.DOTALL,
    ):
        raw = html.unescape(match.group(1)).strip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            objects.append(parsed)
        elif isinstance(parsed, list):
            objects.extend(item for item in parsed if isinstance(item, dict))
    return objects


def extract_linkareer_field(html_body: str, field_name: str) -> str:
    pattern = (
        rf"<dt[^>]*>\s*{re.escape(field_name)}\s*</dt>\s*"
        r"<dd[^>]*>(.*?)</dd>"
    )
    match = re.search(pattern, html_body, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def deadline_info_from_datetime(value: str, now_kst: datetime, source: str) -> DeadlineInfo:
    parsed = parse_datetime(value)
    if parsed is None:
        return empty_deadline_info(source)
    parsed = parsed.astimezone(KST)
    days = (parsed.date() - now_kst.astimezone(KST).date()).days
    return DeadlineInfo(
        deadline=parsed.strftime("%Y-%m-%d %H:%M:%S KST"),
        deadline_text=parsed.strftime("%Y-%m-%d %H:%M KST"),
        deadline_status="closed" if parsed < now_kst.astimezone(KST) else "open",
        deadline_confidence="high",
        deadline_source=source,
        days_until_deadline=days,
    )


def weekly_role_is_non_developer_only(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    has_non_developer = any(
        keyword.lower() in lowered for keyword in WEEKLY_NON_DEVELOPER_ONLY_KEYWORDS
    )
    has_developer = any(
        keyword.lower() in lowered
        for keyword in WEEKLY_BACKEND_DIRECT_KEYWORDS + WEEKLY_BACKEND_ADJACENT_KEYWORDS
    )
    return has_non_developer and not has_developer


def weekly_selection_tier_for_text(text: str, career_type: str) -> str:
    if weekly_role_is_non_developer_only(text):
        return ""
    if text_contains_any(text, WEEKLY_BACKEND_DIRECT_KEYWORDS):
        return "backend_direct"
    if career_type in {"인턴", "신입", "주니어"} and text_contains_any(
        text,
        WEEKLY_BACKEND_ADJACENT_KEYWORDS,
    ):
        return "backend_adjacent"
    if career_type in {"해커톤", "공모전", "경진대회"} and text_contains_any(
        text,
        PORTFOLIO_KEYWORDS + WEEKLY_BACKEND_ADJACENT_KEYWORDS + ["ai api", "데이터 파이프라인"],
    ):
        return "portfolio_activity"
    return ""


def parse_weekly_career_detail_page(
    url: str,
    html_body: str,
    category: dict[str, object],
    discovered: WeeklyDiscoveredUrl,
    now_kst: datetime,
    penalty_keywords: list[str],
) -> Candidate | None:
    source = source_label_for_url(url, discovered.source)
    visible_text = html_to_visible_text(html_body)
    if len(visible_text) < 40 and not extract_html_title(html_body):
        return None
    json_ld_objects = extract_json_ld_objects(html_body)
    structured = next(
        (
            item
            for item in json_ld_objects
            if str(item.get("@type", "")).lower()
            in {"jobposting", "event", "creativework", "course"}
        ),
        {},
    )

    title = (
        str(structured.get("title", "")).strip()
        or str(structured.get("name", "")).strip()
        or str(structured.get("headline", "")).strip()
        or extract_html_title(html_body)
    )
    if not title:
        return None

    company = ""
    for org_key in ("hiringOrganization", "organizer", "provider", "author"):
        org_value = structured.get(org_key)
        if isinstance(org_value, dict):
            company = str(org_value.get("name", "")).strip()
        elif isinstance(org_value, list):
            company = " ".join(
                str(item.get("name", "")).strip()
                for item in org_value
                if isinstance(item, dict) and str(item.get("name", "")).strip()
            ).strip()
        elif org_value:
            company = str(org_value).strip()
        if company:
            break

    description = (
        str(structured.get("description", "")).strip()
        or extract_meta_content(html_body, "og:description")
        or visible_text
    )
    role = extract_linkareer_field(html_body, "모집직무")
    if not role:
        role_match = re.search(r"모집직무\s*[:：]\s*([^\n]+)", description)
        role = role_match.group(1).strip() if role_match else ""
    employment = extract_linkareer_field(html_body, "채용형태")
    if not employment:
        employment_type = structured.get("employmentType")
        if isinstance(employment_type, list):
            employment = " ".join(str(item) for item in employment_type)
        else:
            employment = str(employment_type or "")
    target = ""
    requirements = structured.get("experienceRequirements")
    if isinstance(requirements, list):
        target = " ".join(str(item) for item in requirements)
    else:
        target = str(requirements or "")

    deadline = empty_deadline_info()
    valid_through = str(structured.get("validThrough", "")).strip()
    if valid_through:
        deadline = deadline_info_from_datetime(valid_through, now_kst, "json-ld-validThrough")
    if deadline.deadline_confidence != "high":
        deadline = extract_deadline_from_text(visible_text, now_kst)

    summary_parts = [
        f"회사: {company}" if company else "",
        f"마감일 {deadline.deadline_text}" if deadline.deadline_text else "",
        f"채용형태: {employment}" if employment else "",
        f"모집직무: {role}" if role else "",
        f"지원자격: {target}" if target else "",
        "상태: 모집 중",
        truncate_text(description or visible_text, 500),
    ]
    summary = " ".join(part for part in summary_parts if part)

    candidate = build_candidate(
        category=category,
        title=title,
        url=url,
        source_url=discovered.listing_url,
        source=source,
        publisher=company or domain_from_url(url) or source,
        published_at=parse_datetime(str(structured.get("datePosted", ""))),
        summary=summary,
        query="weekly_detail",
        source_reliability="platform",
        current_time=now_kst,
        penalty_keywords=penalty_keywords,
    )
    return candidate


def is_expired_or_past_event(text: str, now_kst: datetime) -> bool:
    searchable = strip_html(text)
    if text_contains_any(searchable, WEEKLY_PAST_EVENT_KEYWORDS):
        return True
    current_year = now_kst.astimezone(KST).year
    years = [int(match.group(0)) for match in re.finditer(r"\b20\d{2}\b", searchable)]
    if any(year < current_year for year in years):
        return True
    return extract_deadline_from_text(searchable, now_kst).deadline_status == "closed"


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


def classify_weekly_category_from_text(text: str, url: str = "", source: str = "") -> str:
    searchable = text or ""
    lowered = searchable.lower()
    domain = domain_from_url(url)
    source_label = source_label_for_url(url, source).lower() if url else source.lower()
    is_activity_platform = domain_matches(
        domain,
        ["dacon.io", "aifactory.space", "programmers.co.kr", "wevity.com", "all-con.co.kr"],
    )

    if text_contains_any(searchable, ["해커톤", "hackathon"]):
        return "hackathon"
    if text_contains_any(
        searchable,
        ["경진대회", "competition", "challenge", "챌린지", "데이터 대회", "ai 대회", "ai 경진대회"],
    ):
        return "competition"
    if domain_matches(domain, ["dacon.io", "aifactory.space"]):
        return "competition"
    if text_contains_any(searchable, ["공모전", "contest"]):
        return "contest"
    if is_activity_platform and text_contains_any(searchable, ["대회", "데이터", "ai", "인공지능"]):
        return "competition"
    if text_contains_any(
        searchable,
        ["인턴", "internship", "intern", "채용연계형", "전환형", "일경험", "work experience", "zero intern"],
    ):
        return "intern"
    if text_contains_any(
        searchable,
        [
            "신입",
            "주니어",
            "정규직",
            "entry",
            "new grad",
            "junior",
            "백엔드 개발자",
            "서버 개발자",
            "backend engineer",
            "server engineer",
        ],
    ):
        return "job"
    if "career" in lowered or "recruit" in lowered or "careers" in source_label:
        return "job"
    return "job"


def weekly_category_for_candidate(candidate: Candidate) -> str:
    if candidate.query == "company_watchlist":
        return "job"
    return classify_weekly_category_from_text(career_text(candidate), candidate.url, candidate.source)


def classify_career_sub_category(candidate: Candidate) -> str:
    weekly_category = weekly_category_for_candidate(candidate)
    if candidate.query == "company_watchlist":
        return "company_watchlist"
    if weekly_category == "job":
        text = career_text(candidate)
        if text_contains_any(text, ["주니어", "junior"]):
            return "junior_job"
        return "entry_job"
    if weekly_category == "intern":
        return "intern_job"
    return weekly_category


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
            return "AI 서비스 API 역할"
        if text_contains_any(text, ["데이터", "data"]):
            return "데이터 수집/API 서버 개발"
        return "API 서버 개발"
    if not text_contains_any(text, WEEKLY_BACKEND_DIRECT_KEYWORDS):
        if text_contains_any(text, ["erp/시스템개발", "시스템개발", "시스템 개발"]):
            return "IT/시스템개발 인턴"
        if text_contains_any(text, ["응용프로그램개발", "응용프로그램 개발"]):
            return "응용프로그램개발 인턴"
        if text_contains_any(text, ["데이터"]):
            return "데이터/플랫폼 개발 인턴"
        if text_contains_any(text, ["ai 서비스", "llm"]):
            return "AI 서비스 개발 인턴"
        if text_contains_any(text, ["it/인터넷", "it·인터넷", "it 인터넷"]):
            return "IT/인터넷 인턴"
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
    return "상세 페이지 기준 지원/참가 조건 확인"


def infer_process_or_deliverable(text: str, career_type: str) -> list[str]:
    if career_type in {"해커톤", "공모전", "경진대회"}:
        deliverables = []
        if text_contains_any(text, ["github", "깃허브"]):
            deliverables.append("GitHub")
        if text_contains_any(text, ["발표", "ppt"]):
            deliverables.append("발표자료")
        if text_contains_any(text, ["url", "배포", "서비스", "결과물"]):
            deliverables.append("결과물 URL")
        return deliverables

    process = []
    if text_contains_any(text, ["서류", "이력서", "resume"]):
        process.append("서류")
    if text_contains_any(text, ["코딩테스트", "coding test", "과제"]):
        process.append("코딩테스트" if "과제" not in text else "과제")
    if text_contains_any(text, ["면접", "interview"]):
        process.append("면접")
    return process


def infer_tech_keywords(text: str) -> list[str]:
    matched = []
    for keyword in CAREER_TECH_KEYWORDS:
        if keyword.lower() in text.lower() and keyword not in matched:
            matched.append(keyword)
    if matched:
        return matched[:6]
    adjacent = [
        keyword
        for keyword in [
            "시스템개발",
            "응용프로그램개발",
            "IT/인터넷",
            "데이터",
            "AI 서비스",
            "플랫폼",
            "웹서비스 개발",
        ]
        if keyword.lower() in text.lower()
    ]
    if adjacent:
        return adjacent[:6]
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
        record_source_error(
            "Naver News Search",
            "Naver endpoint is missing in configs/kr-sources.json.",
            category=str(category.get("id", "")).strip(),
            source_type="naver",
        )
        return []

    candidates: list[Candidate] = []
    raw_queries = category.get("naver_queries", [])
    if not isinstance(raw_queries, list):
        return candidates

    for query_config in raw_queries:
        query = naver_query_value(query_config)
        if not query:
            continue
        display = naver_display(config, query_config)
        try:
            items = fetch_naver_items(endpoint, query, display, sort, credentials)
        except RuntimeError as exc:
            record_source_error(
                "Naver News Search",
                f"query '{query}' failed: {exc}",
                category=str(category.get("id", "")).strip(),
                source_type="naver",
            )
            continue
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
            record_warning(f"unsupported feed type for {source_name}: {source_type}")
            continue
        if not feed_url:
            record_warning(f"RSS source without URL: {source_name}")
            continue

        try:
            payload = fetch_feed(source)
            parsed_items = parse_feed_items(payload)
        except (
            ET.ParseError,
            OSError,
            TimeoutError,
            urllib.error.URLError,
            urllib.error.HTTPError,
        ) as exc:
            record_source_error(
                source_name,
                f"failed to collect RSS source: {exc}",
                category=str(category.get("id", "")).strip(),
                source_type="rss",
            )
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
            record_warning(
                f"GitHub token could not read {description} for {repository} "
                f"({exc.code}); "
                "retrying with the public unauthenticated API."
            )
            return fetch_github_api_json(url, None, repository, description)
        lowered_detail = detail.lower()
        rate_limit_remaining = str(exc.headers.get("X-RateLimit-Remaining", "")).strip()
        error_type = "github_api_request_failed"
        if rate_limit_remaining == "0" or "rate limit" in lowered_detail:
            error_type = "github_rate_limit"
        elif exc.code in {401, 403, 404}:
            error_type = "github_repository_access_failed"
        record_source_error(
            f"GitHub {repository}",
            f"GitHub API request failed for {description} ({exc.code}): {detail}",
            category=OSS_CATEGORY_ID,
            source_type="github",
            error_type=error_type,
        )
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        record_source_error(
            f"GitHub {repository}",
            f"GitHub API request failed for {description}: {exc}",
            category=OSS_CATEGORY_ID,
            source_type="github",
            error_type="github_api_request_failed",
        )
        return None


def fetch_github_graphql_json(
    query: str,
    variables: dict[str, object],
    token: str | None,
    repository: str,
    description: str,
) -> dict[str, object] | None:
    if not token:
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL request skipped for {description}: token is required.",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type="github_graphql_token_missing",
        )
        return None

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        detail = " ".join(body.split())[:300] if body else exc.reason
        lowered_detail = detail.lower()
        rate_limit_remaining = str(exc.headers.get("X-RateLimit-Remaining", "")).strip()
        error_type = "github_graphql_request_failed"
        if rate_limit_remaining == "0" or "rate limit" in lowered_detail:
            error_type = "github_rate_limit"
        elif exc.code in {401, 403, 404}:
            error_type = "github_repository_access_failed"
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL request failed for {description} ({exc.code}): {detail}",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type=error_type,
        )
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL request failed for {description}: {exc}",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type="github_graphql_request_failed",
        )
        return None

    if not isinstance(payload, dict):
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL response was not an object for {description}.",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type="github_graphql_invalid_response",
        )
        return None

    errors = payload.get("errors", [])
    if isinstance(errors, list) and errors:
        detail = json.dumps(errors[:2], ensure_ascii=False)[:300]
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL response included errors for {description}: {detail}",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type="github_graphql_response_error",
        )
        return None

    data = payload.get("data")
    if not isinstance(data, dict):
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL response had no data object for {description}.",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type="github_graphql_invalid_response",
        )
        return None
    return data


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


def graphql_pull_request_reference_count(node: object) -> int:
    if not isinstance(node, dict):
        return 0
    count = 0
    for field in ("source", "subject", "target"):
        value = node.get(field)
        if isinstance(value, dict) and value.get("__typename") == "PullRequest":
            count += 1
    return count


def fetch_github_linked_work_check(
    repository: str,
    issue_number: int,
    token: str | None,
) -> GitHubLinkedWorkCheck | None:
    owner, name = repository.split("/", 1)
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        issue(number: $number) {
          linkedBranches(first: 20) {
            totalCount
          }
          timelineItems(first: 100, itemTypes: [CONNECTED_EVENT, CROSS_REFERENCED_EVENT]) {
            pageInfo {
              hasNextPage
            }
            nodes {
              __typename
              ... on ConnectedEvent {
                source {
                  __typename
                  ... on PullRequest { number state url }
                  ... on Issue { number state url }
                }
                subject {
                  __typename
                  ... on PullRequest { number state url }
                  ... on Issue { number state url }
                }
              }
              ... on CrossReferencedEvent {
                willCloseTarget
                source {
                  __typename
                  ... on PullRequest { number state url }
                  ... on Issue { number state url }
                }
                target {
                  __typename
                  ... on PullRequest { number state url }
                  ... on Issue { number state url }
                }
              }
            }
          }
        }
      }
    }
    """
    data = fetch_github_graphql_json(
        query,
        {"owner": owner, "name": name, "number": issue_number},
        token,
        repository,
        f"linked work check for issue #{issue_number}",
    )
    if data is None:
        return None

    repository_payload = data.get("repository")
    issue_payload = repository_payload.get("issue") if isinstance(repository_payload, dict) else None
    if not isinstance(issue_payload, dict):
        record_source_error(
            f"GitHub {repository}",
            f"GitHub GraphQL linked work check found no issue #{issue_number}.",
            category=OSS_CATEGORY_ID,
            source_type="github_graphql",
            error_type="github_graphql_issue_missing",
        )
        return None

    linked_branches = issue_payload.get("linkedBranches", {})
    try:
        linked_branches_count = int(
            linked_branches.get("totalCount", 0)
            if isinstance(linked_branches, dict)
            else 0
        )
    except (TypeError, ValueError):
        linked_branches_count = 0

    timeline = issue_payload.get("timelineItems", {})
    nodes = timeline.get("nodes", []) if isinstance(timeline, dict) else []
    page_info = timeline.get("pageInfo", {}) if isinstance(timeline, dict) else {}
    timeline_page_complete = not bool(
        page_info.get("hasNextPage") if isinstance(page_info, dict) else True
    )
    linked_prs_count = sum(graphql_pull_request_reference_count(node) for node in nodes)
    has_linked_work = linked_prs_count > 0 or linked_branches_count > 0
    check_status = "verified" if timeline_page_complete else "unknown"
    return GitHubLinkedWorkCheck(
        check_status=check_status,
        linked_prs_count=linked_prs_count,
        linked_branches_count=linked_branches_count,
        has_linked_work=has_linked_work,
        source="graphql",
        timeline_page_complete=timeline_page_complete,
    )


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


def record_oss_gate_exclusion(reason: str) -> None:
    OSS_GATE_EXCLUSION_COUNTS[reason] += 1


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
    required_fields = {
        "id",
        "track",
        "title",
        "situation",
        "core_concept",
        "failure_mode",
        "practice_30m",
        "practice_steps",
        "official_refs",
        "check_question",
        "search_keywords",
    }
    for lesson in lessons:
        if not isinstance(lesson, dict):
            raise RuntimeError("Every backend practical lesson must be an object.")
        missing: list[str] = []
        for field in sorted(required_fields):
            if field not in lesson:
                missing.append(field)
                continue
            value = lesson.get(field)
            if value is None or value == "" or value == []:
                missing.append(field)
        if missing:
            lesson_id = str(lesson.get("id", "unknown"))
            raise RuntimeError(
                "Backend practical lesson is missing required field(s): "
                f"{lesson_id} ({', '.join(missing)})"
            )
        if not isinstance(lesson.get("practice_steps"), list):
            raise RuntimeError(
                "Backend practical lesson practice_steps must be a list: "
                f"{lesson.get('id')}"
            )
        if not isinstance(lesson.get("official_refs"), list):
            raise RuntimeError(
                "Backend practical lesson official_refs must be a list: "
                f"{lesson.get('id')}"
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


def date_rotation_index(
    item_count: int,
    selection_policy: dict[str, object],
    current_time: datetime,
    context: str,
) -> int:
    if item_count <= 0:
        raise RuntimeError(f"{context} needs at least one selectable item.")
    if str(selection_policy.get("type", "")).strip() != "date_rotation":
        raise RuntimeError(f"{context} must use date_rotation policy.")
    if str(selection_policy.get("timezone", "")).strip() != "Asia/Seoul":
        raise RuntimeError(f"{context} timezone must be Asia/Seoul.")

    start_date_value = str(selection_policy.get("start_date", "")).strip()
    try:
        start_date = datetime.strptime(start_date_value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise RuntimeError(f"{context} start_date must use YYYY-MM-DD.") from exc

    today = current_time.astimezone(KST).date()
    days_since_start = max((today - start_date).days, 0)
    return days_since_start % item_count


def require_non_empty_list(value: object, field: str, context: str) -> None:
    if not isinstance(value, list) or not value:
        raise RuntimeError(f"{context} needs non-empty {field}.")
    if not all(str(item).strip() for item in value):
        raise RuntimeError(f"{context} {field} must not contain empty values.")


def require_curated_fields(
    item: dict[str, object],
    required_fields: set[str],
    list_fields: set[str],
    context: str,
) -> None:
    missing = []
    for field in sorted(required_fields):
        value = item.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    if missing:
        raise RuntimeError(f"{context} is missing field(s): {', '.join(missing)}")
    for field in sorted(list_fields):
        require_non_empty_list(item.get(field), field, context)


def load_backend_core_cs_curriculum(
    path: Path = BACKEND_CORE_CS_CURRICULUM_PATH,
) -> dict[str, object]:
    curriculum = load_required_json(path)
    topics = curriculum.get("topics", [])
    if not isinstance(topics, list) or not topics:
        raise RuntimeError("configs/backend-core-cs-curriculum.json must contain topics.")

    required_fields = {
        "id",
        "track",
        "title",
        "why_backend",
        "key_concept",
        "practice_steps",
        "done_criteria",
        "interview_question",
        "refs",
    }
    seen_ids: set[str] = set()
    seen_tracks: set[str] = set()
    for topic in topics:
        if not isinstance(topic, dict):
            raise RuntimeError("Every CS Core topic must be an object.")
        topic_id = str(topic.get("id", "")).strip()
        context = f"CS Core topic {topic_id or 'unknown'}"
        require_curated_fields(topic, required_fields, {"practice_steps", "done_criteria", "refs"}, context)
        if topic_id in seen_ids:
            raise RuntimeError(f"Duplicate CS Core topic id: {topic_id}")
        seen_ids.add(topic_id)
        seen_tracks.add(str(topic.get("track", "")).strip())

    missing_tracks = sorted(CS_CORE_REQUIRED_TRACKS - seen_tracks)
    if missing_tracks:
        raise RuntimeError(
            "CS Core curriculum misses required track(s): "
            f"{', '.join(missing_tracks)}"
        )
    return curriculum


def select_backend_core_cs_topic(
    curriculum: dict[str, object],
    current_time: datetime,
) -> dict[str, object]:
    topics = curriculum.get("topics", [])
    if not isinstance(topics, list):
        raise RuntimeError("CS Core curriculum topics must be a list.")
    selection_policy = curriculum.get("selection_policy", {})
    if not isinstance(selection_policy, dict):
        raise RuntimeError("CS Core curriculum selection_policy is required.")
    index = date_rotation_index(
        len(topics),
        selection_policy,
        current_time,
        "CS Core curriculum",
    )
    selected = topics[index]
    if not isinstance(selected, dict):
        raise RuntimeError("Selected CS Core topic must be an object.")
    return selected


def write_backend_core_cs_candidate(current_time: datetime) -> None:
    curriculum = load_backend_core_cs_curriculum()
    selected = select_backend_core_cs_topic(curriculum, current_time)
    payload = {
        "category": "cs-core-daily-topic",
        "generated_at": format_kst(current_time),
        "selection_policy": "date_rotation",
        "candidate_count": 1,
        "today": selected,
    }
    write_json_file(BACKEND_CORE_CS_OUTPUT_PATH, payload)
    print(f"Wrote CS Core daily topic: {BACKEND_CORE_CS_OUTPUT_PATH}")


def load_backend_terms_glossary(
    path: Path = BACKEND_TERMS_GLOSSARY_PATH,
) -> dict[str, object]:
    glossary = load_required_json(path)
    terms = glossary.get("terms", [])
    if not isinstance(terms, list) or len(terms) < 30:
        raise RuntimeError("configs/backend-terms-glossary.json must contain at least 30 terms.")

    required_fields = {
        "id",
        "term",
        "one_line_definition",
        "backend_context",
        "common_misunderstanding",
        "spring_or_api_connection",
        "check_question",
        "refs",
    }
    seen_ids: set[str] = set()
    for term in terms:
        if not isinstance(term, dict):
            raise RuntimeError("Every backend glossary term must be an object.")
        term_id = str(term.get("id", "")).strip()
        context = f"Backend glossary term {term_id or 'unknown'}"
        require_curated_fields(term, required_fields, {"refs"}, context)
        if term_id in seen_ids:
            raise RuntimeError(f"Duplicate backend glossary term id: {term_id}")
        seen_ids.add(term_id)
    return glossary


def select_backend_term(
    glossary: dict[str, object],
    current_time: datetime,
) -> dict[str, object]:
    terms = glossary.get("terms", [])
    if not isinstance(terms, list):
        raise RuntimeError("Backend terms glossary terms must be a list.")
    selection_policy = glossary.get("selection_policy", {})
    if not isinstance(selection_policy, dict):
        raise RuntimeError("Backend terms glossary selection_policy is required.")
    index = date_rotation_index(
        len(terms),
        selection_policy,
        current_time,
        "Backend terms glossary",
    )
    selected = terms[index]
    if not isinstance(selected, dict):
        raise RuntimeError("Selected backend term must be an object.")
    return selected


def write_backend_term_candidate(current_time: datetime) -> None:
    glossary = load_backend_terms_glossary()
    selected = select_backend_term(glossary, current_time)
    payload = {
        "category": "backend-term-daily",
        "generated_at": format_kst(current_time),
        "selection_policy": "date_rotation",
        "candidate_count": 1,
        "today": selected,
    }
    write_json_file(BACKEND_TERM_OUTPUT_PATH, payload)
    print(f"Wrote backend term daily: {BACKEND_TERM_OUTPUT_PATH}")


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
        record_oss_gate_exclusion("pull-request-item")
        return None
    state = str(issue.get("state", "")).strip()
    if state != "open":
        record_oss_gate_exclusion("not-open")
        return None

    title = truncate_text(strip_html(str(issue.get("title", ""))), TITLE_LIMIT)
    html_url = str(issue.get("html_url", "")).strip()
    number = issue.get("number", 0)
    try:
        issue_number = int(number)
    except (TypeError, ValueError):
        issue_number = 0
    if not title or not html_url or issue_number <= 0:
        record_oss_gate_exclusion("missing-required-issue-fields")
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
        record_oss_gate_exclusion("external-author-without-maintainer-triage")
        return None
    if has_assignee:
        record_oss_gate_exclusion("assigned")
        return None
    if text_contains_any(f"{title} {raw_body}", OSS_CLAIM_KEYWORDS):
        record_oss_gate_exclusion("claim-in-issue-body")
        return None
    if text_contains_any(label_title_text, OSS_BLOCKED_LABEL_TITLE_KEYWORDS):
        record_oss_gate_exclusion("blocked-label-or-title")
        return None
    if text_contains_any(searchable, OSS_SECURITY_KEYWORDS + OSS_RELEASE_BLOCKER_KEYWORDS):
        record_oss_gate_exclusion("security-or-release-blocker")
        return None
    if text_contains_any(searchable, OSS_DEEP_INTERNALS_KEYWORDS + OSS_MAJOR_API_KEYWORDS):
        record_oss_gate_exclusion("deep-internals-or-major-api")
        return None
    if text_contains_any(searchable, OSS_DESIGN_KEYWORDS):
        record_oss_gate_exclusion("design-or-epic")
        return None
    if not (
        difficulty_model_matches(difficulty_model, "p5_like", labels, searchable)
        or difficulty_model_matches(difficulty_model, "p4_like", labels, searchable)
    ):
        record_oss_gate_exclusion("no-beginner-difficulty-signal")
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
            record_oss_gate_exclusion("claim-comment")
            return None
    linked_work_result = fetch_github_linked_work_check(repository, issue_number, token)
    if linked_work_result is None:
        linked_prs_count = 0
        linked_branches_count = 0
        linked_work_check = "unknown"
        has_linked_work = False
        record_oss_gate_exclusion("linked-work-check-unknown")
    else:
        linked_prs_count = linked_work_result.linked_prs_count
        linked_branches_count = linked_work_result.linked_branches_count
        linked_work_check = linked_work_result.check_status
        has_linked_work = linked_work_result.has_linked_work
        if has_linked_work:
            record_oss_gate_exclusion("linked-work")
        elif linked_work_check != "verified":
            record_oss_gate_exclusion("linked-work-check-unknown")
    if claim_comment_check != "checked":
        record_oss_gate_exclusion("claim-comment-check-unknown")
    safe_to_recommend = (
        state == "open"
        and maintainer_qualified
        and not has_assignee
        and linked_prs_count == 0
        and linked_branches_count == 0
        and linked_work_check == "verified"
        and claim_comment_check == "checked"
        and not claim_author
        and contribution_type in OSS_PREFERRED_CONTRIBUTION_TYPES
    )
    if contribution_type not in OSS_PREFERRED_CONTRIBUTION_TYPES:
        record_oss_gate_exclusion("unsupported-contribution-type")
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
        maintainer_triaged=maintainer_triaged,
        maintainer_qualified=maintainer_qualified,
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
    OSS_GATE_EXCLUSION_COUNTS.clear()
    OSS_REPOSITORY_DIAGNOSTICS.clear()
    oss_config = load_oss_repositories_config()
    repositories = configured_repositories(category, oss_config)
    difficulty_model = oss_config.get("difficulty_model", {})
    if not isinstance(difficulty_model, dict):
        difficulty_model = {}
    token = get_github_token()
    candidates: list[OssIssueCandidate] = []

    for repository in repositories:
        if "/" not in repository:
            record_warning(f"invalid GitHub repository id: {repository}")
            continue
        issues = fetch_github_issues(repository, token)
        OSS_REPOSITORY_DIAGNOSTICS.append(
            {
                "repository": repository,
                "issues_fetched": len(issues),
            }
        )
        for issue in issues:
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
        normalized_url = canonical_candidate_url(candidate.url)
        normalized_source_url = canonical_candidate_url(candidate.source_url)
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
                max(
                    score_career_candidate(item, current_time)["score"],
                    score_weekly_career_detail_candidate(item, current_time),
                ),
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


def canonical_candidate_url(url: str) -> str:
    normalized = normalize_url(url)
    if not normalized:
        return ""
    parsed = urllib.parse.urlsplit(normalized)
    query_items = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in {"fbclid", "gclid", "igshid"}
    ]
    query = urllib.parse.urlencode(query_items, doseq=True)
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path.rstrip("/") or parsed.path, query, "")
    )


def candidate_category_hint(candidate: Candidate) -> str:
    text = " ".join(
        [
            candidate.category,
            candidate.title,
            candidate.summary,
            " ".join(candidate.tags),
        ]
    ).lower()
    if any(keyword in text for keyword in ["security", "보안", "cve", "취약점"]):
        return "Security"
    if any(keyword in text for keyword in ["cloud", "클라우드", "kubernetes", "aws", "ncloud"]):
        return "Cloud"
    if any(keyword in text for keyword in ["data", "데이터", "postgresql", "mysql", "redis", "kafka"]):
        return "Data"
    if any(keyword in text for keyword in ["open source", "opensource", "오픈소스"]):
        return "Open Source"
    if any(keyword in text for keyword in ["productivity", "생산성", "ci", "코딩 에이전트"]):
        return "Developer Productivity"
    if any(keyword in text for keyword in ["ai", "llm", "모델", "에이전트"]):
        return "AI"
    return "Backend"


def candidate_source_name(candidate: object) -> str:
    if isinstance(candidate, dict):
        return str(candidate.get("source_name") or candidate.get("source") or "").strip()
    return str(getattr(candidate, "source", "")).strip()


def candidate_source_count(candidates: list[object]) -> int:
    sources = {
        source
        for source in (candidate_source_name(candidate) for candidate in candidates)
        if source
    }
    return len(sources)


def common_candidate_metadata(
    mode: str,
    generated_at: datetime,
    candidates: list[object],
) -> dict[str, object]:
    return {
        "mode": mode,
        "generated_at_kst": format_kst(generated_at),
        "candidate_count": len(candidates),
        "source_count": candidate_source_count(candidates),
        "source_errors": SOURCE_ERRORS,
        "warnings": WARNINGS,
    }


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
        "maintainer_triaged": candidate.maintainer_triaged,
        "maintainer_qualified": candidate.maintainer_qualified,
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
        "canonical_url": canonical_candidate_url(candidate.url),
        "normalized_title": normalize_title(candidate.title),
        "source_name": candidate.source,
        "source_url": candidate.source_url,
        "source": candidate.source,
        "publisher": candidate.publisher,
        "published_at": format_kst(candidate.published_at) if candidate.published_at else "",
        "published_at_kst": format_kst(candidate.published_at) if candidate.published_at else "",
        "category_hint": candidate_category_hint(candidate),
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


def weekly_source_confidence(source_kind: str, is_detail_url: bool) -> str:
    if source_kind in WEEKLY_ALLOWED_SOURCE_KINDS and is_detail_url:
        return "high"
    if source_kind in {"generic_listing", "search_result"}:
        return "low"
    return "none"


def score_weekly_career_detail_candidate(candidate: Candidate, now_kst: datetime) -> int:
    text = career_text(candidate)
    career_type = career_type_for_sub_category(classify_career_sub_category(candidate))
    selection_tier = weekly_selection_tier_for_text(text, career_type)
    score = {
        "backend_direct": 90,
        "backend_adjacent": 70,
        "portfolio_activity": 60,
    }.get(selection_tier, 0)
    deadline = extract_deadline_from_text(text, now_kst)
    if deadline.deadline_status == "open":
        score += 15
    if isinstance(deadline.days_until_deadline, int) and 0 <= deadline.days_until_deadline <= 14:
        score += 10
    if extract_company_or_host_from_text_or_url(text, candidate.url).confidence == "high":
        score += 5
    return score


def is_weekly_candidate_active(text: str, deadline: DeadlineInfo, now_kst: datetime) -> bool:
    if is_expired_or_past_event(text, now_kst):
        return False
    if deadline.deadline_status in {"open", "rolling", "until_filled"}:
        return True
    return text_contains_any(
        text,
        [
            "모집 중",
            "모집중",
            "접수 중",
            "접수중",
            "지원 가능",
            "참가 가능",
            "채용 중",
            "채용중",
            "open",
        ],
    )


def normalize_weekly_career_candidate(
    candidate: Candidate,
    now_kst: datetime,
) -> dict[str, object]:
    text = career_text(candidate)
    sub_category = classify_career_sub_category(candidate)
    weekly_category = WEEKLY_COMPAT_SUB_CATEGORY_TO_WEEKLY_CATEGORY.get(
        sub_category,
        weekly_category_for_candidate(candidate),
    )
    category_label = WEEKLY_CATEGORY_LABELS.get(weekly_category, weekly_category)
    career_type = career_type_for_sub_category(sub_category)
    deadline = extract_deadline_from_text(text, now_kst)
    score_payload = score_career_candidate(candidate, now_kst)
    company_or_host = extract_company_or_host_from_text_or_url(text, candidate.url)
    is_detail_url = is_weekly_career_detail_url(candidate.url)
    is_generic_url = is_weekly_career_generic_url(candidate.url)
    is_news_article = is_weekly_career_news_article(candidate)
    is_reference_material = is_weekly_reference_material_url(candidate.url)
    source_kind = infer_weekly_source_kind(candidate.url, candidate.source)
    is_active = is_weekly_candidate_active(text, deadline, now_kst)
    selection_tier = weekly_selection_tier_for_text(text, career_type)
    exclude_reasons = []
    if candidate.exclude_reason:
        exclude_reasons.append(candidate.exclude_reason)
    if candidate.source == "Naver News Search":
        exclude_reasons.append("naver-news-not-career-source")
    if is_news_article:
        exclude_reasons.append("news-article-not-career-detail")
    if is_reference_material:
        exclude_reasons.append("reference-material-not-career-opportunity")
    if not is_allowed_weekly_career_final_domain(candidate.url):
        exclude_reasons.append("domain-not-allowed")
    if source_kind not in WEEKLY_ALLOWED_SOURCE_KINDS:
        exclude_reasons.append(f"source-kind-{source_kind}")
    if is_generic_url:
        exclude_reasons.append("generic-url")
    if not is_detail_url:
        exclude_reasons.append("not-detail-url")
    if is_expired_or_past_event(text, now_kst):
        exclude_reasons.append("expired-or-past-event")
    if not is_active:
        exclude_reasons.append("not-confirmed-active")
    if weekly_role_is_non_developer_only(text):
        exclude_reasons.append("non-developer-role")
    if not selection_tier:
        exclude_reasons.append("not_backend_related")

    source = candidate.source
    if source in {"Official reference page", "Naver News Search"}:
        source = source_label_for_url(candidate.url, source)
    elif source.startswith("http"):
        source = source_label_for_url(candidate.url, source)
    if source == "Naver News Search":
        source = domain_from_url(candidate.url) or "unknown"

    verification_status = "verified_active" if is_active else "unknown"
    if deadline.deadline_status == "closed" or "expired-or-past-event" in exclude_reasons:
        verification_status = "verified_closed"
    elif "not-detail-url" in exclude_reasons or "generic-url" in exclude_reasons:
        verification_status = "parse_failed"

    return {
        "category": WEEKLY_CAREER_CATEGORY_ID,
        "sub_category": sub_category,
        "weekly_category": weekly_category,
        "category_label": category_label,
        "title": candidate.title,
        "url": candidate.url,
        "source_url": candidate.source_url,
        "source": source,
        "source_kind": source_kind,
        "source_confidence": weekly_source_confidence(source_kind, is_detail_url),
        "discovered_via": "naver_news_search" if candidate.source == "Naver News Search" else "",
        "is_detail_url": is_detail_url,
        "is_generic_url": is_generic_url,
        "is_news_article": is_news_article,
        "is_active": is_active,
        "selection_tier": selection_tier,
        "company_or_host": company_or_host.value,
        "company_or_host_confidence": company_or_host.confidence,
        "company_or_host_source": company_or_host.source,
        "type": career_type,
        "role": infer_career_role(text, career_type),
        "deadline": deadline.deadline,
        "deadline_text": deadline.deadline_text,
        "deadline_status": deadline.deadline_status,
        "deadline_confidence": deadline.deadline_confidence,
        "deadline_source": deadline.deadline_source,
        "days_until_deadline": deadline.days_until_deadline,
        "target": infer_target(text, career_type),
        "tech_or_output_keywords": infer_tech_keywords(text),
        "process_or_deliverable": infer_process_or_deliverable(text, career_type),
        "summary": candidate.summary,
        "freshness_tier": "fresh_this_week",
        "first_seen_at": format_kst(now_kst),
        "last_seen_at": format_kst(now_kst),
        "last_verified_at": format_kst(now_kst),
        "verification_status": verification_status,
        "coverage_reason": "",
        "published_at": format_kst(candidate.published_at) if candidate.published_at else "",
        "collected_at": format_kst(now_kst),
        "query": candidate.query,
        "score": max(score_payload["score"], score_weekly_career_detail_candidate(candidate, now_kst)),
        "deadline_clarity_score": score_payload["deadline_clarity_score"],
        "backend_fit_score": score_payload["backend_fit_score"],
        "entry_fit_score": score_payload["entry_fit_score"],
        "portfolio_fit_score": score_payload["portfolio_fit_score"],
        "source_reliability_score": score_payload["source_reliability_score"],
        "actionability_score": score_payload["actionability_score"],
        "exclude_reason": ",".join(dict.fromkeys(exclude_reasons)),
    }


def standardize_weekly_career_candidate(
    candidate: Candidate,
    generated_at: datetime,
) -> dict[str, object]:
    return normalize_weekly_career_candidate(candidate, generated_at)


def filter_weekly_career_candidates(
    candidates: list[Candidate],
    now_kst: datetime,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    normalized = [normalize_weekly_career_candidate(candidate, now_kst) for candidate in candidates]
    eligible = [item for item in normalized if not str(item.get("exclude_reason", ""))]
    excluded = [item for item in normalized if str(item.get("exclude_reason", ""))]
    return dedupe_weekly_career_items(eligible), dedupe_weekly_career_items(excluded)


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


def weekly_selection_rank(item: dict[str, object], coverage_config: dict[str, object]) -> tuple[int, int, int, int, int, int, int]:
    weekly_category = str(item.get("weekly_category", ""))
    tier = str(item.get("selection_tier", ""))
    freshness = str(item.get("freshness_tier", "fresh_this_week"))
    source = str(item.get("source", ""))
    source_priority = weekly_category_source_priorities(weekly_category, coverage_config)
    if weekly_category in {"hackathon", "contest", "competition"}:
        tier_order = {"portfolio_activity": 3, "backend_direct": 2, "backend_adjacent": 1}
    else:
        tier_order = {"backend_direct": 3, "backend_adjacent": 2, "portfolio_activity": 1}
    source_rank = len(source_priority) - source_priority.index(source) if source in source_priority else 0
    deadline_confidence = 2 if str(item.get("deadline_confidence", "")) == "high" else 0
    active = 1 if str(item.get("verification_status", "")) == "verified_active" else 0
    freshness_score = 2 if freshness == "fresh_this_week" else 1
    detail_score = 1 if item.get("is_detail_url") is True else 0
    return (
        active,
        freshness_score,
        tier_order.get(tier, 0),
        detail_score,
        deadline_confidence,
        source_rank,
        int(item.get("score", 0) or 0),
    )


def select_weekly_career_by_category(
    final_items: list[dict[str, object]],
    cache_items: list[dict[str, object]],
    coverage_config: dict[str, object],
    now_kst: datetime,
) -> dict[str, dict[str, object] | None]:
    del now_kst
    selected: dict[str, dict[str, object] | None] = {}
    all_items = [
        item
        for item in final_items + cache_items
        if not str(item.get("exclude_reason", ""))
        and str(item.get("verification_status", "verified_active")) == "verified_active"
        and str(item.get("weekly_category", "")) in WEEKLY_CATEGORY_ORDER
        and not is_weekly_career_news_article(str(item.get("url", "")))
        and not is_weekly_career_generic_url(str(item.get("url", "")))
    ]
    for weekly_category in WEEKLY_CATEGORY_ORDER:
        candidates = [
            item
            for item in all_items
            if str(item.get("weekly_category", "")) == weekly_category
        ]
        if not candidates:
            selected[weekly_category] = None
            continue
        selected[weekly_category] = sorted(
            candidates,
            key=lambda item: weekly_selection_rank(item, coverage_config),
            reverse=True,
        )[0]
    return selected


def weekly_company_watchlist_diagnostics(source_counts: dict[str, object]) -> dict[str, object]:
    checked = []
    for company in load_company_watchlist():
        source = str(company.get("source", "")).strip()
        name = str(company.get("name", "")).strip()
        career_url = str(company.get("career_url", "")).strip()
        if not source or not career_url:
            continue
        source_payload = source_counts.get(source, {})
        checked.append(
            {
                "name": name,
                "source": source,
                "career_url": career_url,
                "checked": isinstance(source_payload, dict) and bool(source_payload),
            }
        )
    return {
        "checked": checked,
        "checked_sources": [
            item["source"] for item in checked if bool(item.get("checked"))
        ],
    }


def build_weekly_career_diagnostics(
    base_diagnostics: dict[str, object],
    final_items: list[dict[str, object]],
    excluded: list[dict[str, object]],
    selected_by_category: dict[str, dict[str, object] | None] | None = None,
    cache_diagnostics: dict[str, int] | None = None,
    coverage_config: dict[str, object] | None = None,
) -> dict[str, object]:
    diagnostics = dict(empty_weekly_career_diagnostics())
    diagnostics.update(base_diagnostics or {})
    reason_counts: Counter[str] = Counter()
    for item in excluded:
        reasons = [
            reason.strip()
            for reason in str(item.get("exclude_reason", "")).split(",")
            if reason.strip()
        ]
        reason_counts.update(reasons or ["unknown"])
    diagnostics["final_items"] = len(final_items)
    diagnostics["excluded_by_reason"] = dict(sorted(reason_counts.items()))

    source_counts = diagnostics.get("source_counts", {})
    if not isinstance(source_counts, dict):
        source_counts = {}
    source_counts = {
        str(name): dict(value) if isinstance(value, dict) else {}
        for name, value in source_counts.items()
    }
    for item in final_items:
        source = str(item.get("source", "unknown")) or "unknown"
        source_counts.setdefault(source, {})
        source_counts[source]["final_items"] = int(source_counts[source].get("final_items", 0)) + 1
    diagnostics["source_counts"] = source_counts
    diagnostics["company_watchlist"] = weekly_company_watchlist_diagnostics(source_counts)

    coverage_source = diagnostics.get("coverage", {})
    coverage: dict[str, dict[str, object]] = {}
    if not isinstance(coverage_source, dict):
        coverage_source = {}
    selected_by_category = selected_by_category or {}
    coverage_config = coverage_config or load_weekly_career_coverage_config()
    for category_config in weekly_coverage_categories(coverage_config):
        weekly_category = str(category_config.get("id", "")).strip()
        if weekly_category not in WEEKLY_CATEGORY_ORDER:
            continue
        base = coverage_source.get(weekly_category, {})
        category_coverage = dict(base) if isinstance(base, dict) else {}
        category_items = [
            item for item in final_items if str(item.get("weekly_category", "")) == weekly_category
        ]
        category_excluded = [
            item for item in excluded if str(item.get("weekly_category", "")) == weekly_category
        ]
        category_reasons: Counter[str] = Counter()
        for item in category_excluded:
            category_reasons.update(
                reason
                for reason in str(item.get("exclude_reason", "")).split(",")
                if reason.strip()
            )
        selected = selected_by_category.get(weekly_category)
        category_coverage.update(
            {
                "label": str(category_config.get("label", "")).strip()
                or WEEKLY_CATEGORY_LABELS[weekly_category],
                "target_min": int(category_config.get("target_min", 1) or 1),
                "selected": 1 if selected else 0,
                "fresh_items": sum(
                    1
                    for item in category_items
                    if str(item.get("freshness_tier", "")) == "fresh_this_week"
                ),
                "cached_revalidated_items": sum(
                    1
                    for item in category_items
                    if str(item.get("freshness_tier", "")) == "cached_revalidated"
                ),
                "excluded_by_reason": dict(sorted(category_reasons.items()))
                or category_coverage.get("excluded_by_reason", {}),
                "sources": category_coverage.get("sources", {}),
            }
        )
        sources = category_coverage.get("sources", {})
        if not isinstance(sources, dict):
            sources = {}
        for item in category_items:
            source = str(item.get("source", "unknown")) or "unknown"
            source_payload = sources.setdefault(source, {})
            if isinstance(source_payload, dict):
                source_payload["final"] = int(source_payload.get("final", 0)) + 1
        category_coverage["sources"] = sources
        if not selected:
            category_coverage["why_empty"] = "No active detail candidate after filtering."
        coverage[weekly_category] = category_coverage
    diagnostics["coverage"] = coverage
    diagnostics["final_selected_total"] = sum(
        1 for key in WEEKLY_CATEGORY_ORDER if selected_by_category.get(key)
    )
    diagnostics["empty_categories"] = [
        key for key in WEEKLY_CATEGORY_ORDER if not selected_by_category.get(key)
    ]
    diagnostics["cache"] = cache_diagnostics or {
        "loaded": 0,
        "revalidated": 0,
        "used_for_backfill": 0,
        "expired_removed": 0,
    }
    return diagnostics


def build_weekly_career_payload(
    category_id: str,
    generated_at: datetime,
    items: list[dict[str, object]],
    excluded: list[dict[str, object]] | None = None,
    diagnostics: dict[str, object] | None = None,
    category_config: dict[str, object] | None = None,
    penalty_keywords: list[str] | None = None,
    update_cache: bool = True,
) -> dict[str, object]:
    del category_config, penalty_keywords, update_cache
    coverage_config = load_weekly_career_coverage_config()
    fresh_items = dedupe_weekly_career_items(items)
    deduped_excluded = dedupe_weekly_career_items(excluded or [])
    selected = select_weekly_career_by_category(fresh_items, [], coverage_config, generated_at)
    cache_diagnostics = {
        "loaded": 0,
        "revalidated": 0,
        "used_for_backfill": 0,
        "expired_removed": 0,
    }
    deduped_items = fresh_items
    return {
        "schema_version": 4,
        "category": category_id,
        "generated_at": format_kst(generated_at),
        "items": deduped_items,
        "selected_by_category": selected,
        "excluded": deduped_excluded,
        "diagnostics": build_weekly_career_diagnostics(
            diagnostics or WEEKLY_CAREER_DISCOVERY_DIAGNOSTICS,
            deduped_items,
            deduped_excluded,
            selected,
            cache_diagnostics,
            coverage_config,
        ),
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
    mode: str,
    penalty_keywords: list[str] | None = None,
    update_cache: bool = True,
) -> None:
    global WEEKLY_CAREER_LAST_PAYLOAD
    category_id = str(category.get("id", "")).strip()
    output_path = output_path_for_category(output_dir, category)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        del candidates, penalty_keywords, update_cache
        radar_payload = write_weekly_career_site_radar_payload(generated_at)
        payload = build_disabled_weekly_career_compat_payload(category_id, generated_at)
        WEEKLY_CAREER_LAST_PAYLOAD = payload
    elif category_id == OSS_CATEGORY_ID:
        items = [
            serialize_oss_issue_candidate(candidate)
            for candidate in candidates
            if isinstance(candidate, OssIssueCandidate) and candidate.safe_to_recommend
        ]
        source_error_types = Counter(
            str(error.get("error_type", "unknown"))
            for error in SOURCE_ERRORS
            if error.get("category") == OSS_CATEGORY_ID
        )
        payload = {
            "schema_version": 2,
            "category": category_id,
            "generated_at": format_kst(generated_at),
            **common_candidate_metadata(mode, generated_at, items),
            "verification_policy": (
                "Only safe_to_recommend=true issues are included in items. "
                "Maintainer authorship or maintainer triage, assignee absence, linked work absence, "
                "and claim comment absence must all be verified."
            ),
            "diagnostics": {
                "safe_items_count": len(items),
                "repository_count": len(OSS_REPOSITORY_DIAGNOSTICS),
                "repositories": OSS_REPOSITORY_DIAGNOSTICS,
                "gate_exclusion_counts": dict(sorted(OSS_GATE_EXCLUSION_COUNTS.items())),
                "source_error_type_counts": dict(sorted(source_error_types.items())),
                "github_api_error_count": sum(source_error_types.values()),
                "github_rate_limit_error_count": int(source_error_types.get("github_rate_limit", 0)),
                "github_repository_access_error_count": int(
                    source_error_types.get("github_repository_access_failed", 0)
                ),
                "linked_work_verification": "graphql_required",
                "fallback_when_empty": "oss-preparation-routine",
            },
            "items": items,
            "excluded": [],
        }
    else:
        items = [serialize_candidate(candidate) for candidate in candidates]
        payload = {
            "category": category_id,
            "generated_at": format_kst(generated_at),
            **common_candidate_metadata(mode, generated_at, items),
            "items": items,
        }
    write_json_file(output_path, payload)
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        print(
            "Wrote weekly career site radar "
            f"({radar_payload['site_count']} site(s), {radar_payload['link_count']} link(s)): "
            f"{WEEKLY_CAREER_SITE_RADAR_OUTPUT_PATH}"
        )
        print(f"Wrote disabled weekly career candidate payload: {output_path}")
        return
    print(f"Wrote {len(candidates)} candidate(s): {output_path}")


def write_daily_tech_alias_outputs(
    generated_at: datetime,
    candidates_by_category: dict[str, list[Candidate] | list[OssIssueCandidate]],
) -> None:
    spring_candidates = candidates_by_category.get(BACKEND_TECH_CATEGORY_ID, [])
    spring_urls = {
        normalize_url(candidate.url)
        for candidate in spring_candidates
        if isinstance(candidate, Candidate)
    }
    for source_category_id, (alias_category_id, output_path) in DAILY_TECH_ALIAS_OUTPUTS.items():
        candidates = candidates_by_category.get(source_category_id, [])
        if source_category_id == AI_TECH_CATEGORY_ID:
            candidates = [
                candidate
                for candidate in candidates
                if not isinstance(candidate, Candidate)
                or normalize_url(candidate.url) not in spring_urls
            ]
        payload = {
            "category": alias_category_id,
            "generated_at": format_kst(generated_at),
            "source_category": source_category_id,
            "items": [serialize_candidate(candidate) for candidate in candidates],
        }
        write_json_file(output_path, payload)
        print(f"Wrote {len(candidates)} candidate(s): {output_path}")
        if source_category_id == AI_TECH_CATEGORY_ID:
            ai_payload = {
                "category": source_category_id,
                "generated_at": format_kst(generated_at),
                "items": [serialize_candidate(candidate) for candidate in candidates],
            }
            ai_output_path = Path("reports/candidates/kr-ai-tech-news.json")
            write_json_file(ai_output_path, ai_payload)
            print(f"Wrote {len(candidates)} candidate(s): {ai_output_path}")


def write_weekly_career_split_outputs(
    generated_at: datetime,
    candidates: list[Candidate] | list[OssIssueCandidate],
) -> None:
    del candidates
    global WEEKLY_CAREER_LAST_CATEGORY_PAYLOADS
    WEEKLY_CAREER_LAST_CATEGORY_PAYLOADS = {}
    for output_path, category in WEEKLY_CAREER_COMPAT_OUTPUT_CATEGORIES.items():
        payload = build_disabled_weekly_career_compat_payload(category, generated_at)
        WEEKLY_CAREER_LAST_CATEGORY_PAYLOADS[str(output_path)] = payload
        write_json_file(output_path, payload)
        print(f"Wrote disabled weekly career candidate payload: {output_path}")


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


def weekly_reference_pages_for_discovery(category: dict[str, object]) -> list[dict[str, object]]:
    pages = [
        page
        for page in category.get("reference_pages", [])
        if isinstance(page, dict)
    ]
    existing_urls = {str(page.get("url", "")).strip() for page in pages}
    for company in load_company_watchlist():
        name = str(company.get("name", "")).strip()
        url = str(company.get("career_url", "")).strip()
        if not name or not url or url in existing_urls:
            continue
        pages.append(
            {
                "name": str(company.get("source", "")).strip() or f"{name} Careers",
                "url": url,
                "source_reliability": "official",
            }
        )
        existing_urls.add(url)
    return pages


def normalized_weekly_source_name(name: str, url: str = "") -> str:
    aliases = {
        "DACON Competitions": "DACON",
        "Work24 Youth Work Experience": "Work24",
        "Woowa Brothers": "Woowa Careers",
    }
    if name in aliases:
        return aliases[name]
    label = source_label_for_url(url, name) if url else name
    if label in {"DACON", "Work24", "Woowa Careers"}:
        return label
    return name or label


def weekly_category_source_priorities(
    weekly_category: str,
    coverage_config: dict[str, object],
) -> list[str]:
    category_config = weekly_category_config(weekly_category, coverage_config)
    values = category_config.get("source_priority", [])
    return [str(value).strip() for value in values if str(value).strip()] if isinstance(values, list) else []


def source_policy_for_adapter(url: str) -> dict[str, object]:
    policy = weekly_source_policy_for_url(url)
    if policy:
        return policy
    domain = domain_from_url(url)
    for company in weekly_policy_list("company_watchlist"):
        domains = company.get("domains", [])
        if isinstance(domains, list) and domain_matches(
            domain,
            [str(item).strip().lower() for item in domains if str(item).strip()],
        ):
            return {
                "name": company.get("name", ""),
                "domain": domain,
                "source_kind": company.get("source_kind", "official_company_career_detail"),
                "detail_url_patterns": [],
                "generic_url_patterns": [],
            }
    return {}


def build_weekly_career_source_adapters(
    category: dict[str, object],
    coverage_config: dict[str, object],
) -> list[WeeklyCareerSourceAdapter]:
    pages = weekly_reference_pages_for_discovery(category)
    adapters: list[WeeklyCareerSourceAdapter] = []
    for page in pages:
        raw_name = str(page.get("name", "")).strip()
        url = str(page.get("url", "")).strip()
        if not raw_name or not url:
            continue
        name = normalized_weekly_source_name(raw_name, url)
        weekly_categories = [
            weekly_category
            for weekly_category in WEEKLY_CATEGORY_ORDER
            if name in weekly_category_source_priorities(weekly_category, coverage_config)
        ]
        if not weekly_categories:
            continue
        priority = min(
            weekly_category_source_priorities(weekly_category, coverage_config).index(name)
            for weekly_category in weekly_categories
            if name in weekly_category_source_priorities(weekly_category, coverage_config)
        )
        policy = source_policy_for_adapter(url)
        detail_patterns = policy.get("detail_url_patterns", [])
        generic_patterns = policy.get("generic_url_patterns", [])
        source_kind = str(policy.get("source_kind", "")).strip() or str(
            page.get("source_kind", "")
        ).strip() or "unknown"
        budget = WEEKLY_CATEGORY_DISCOVERY_BUDGETS.get(
            weekly_categories[0],
            {"detail_urls": WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE, "detail_pages": WEEKLY_MAX_DETAIL_PAGES},
        )
        adapters.append(
            WeeklyCareerSourceAdapter(
                name=name,
                domains=[domain_from_url(url)],
                weekly_categories=weekly_categories,
                listing_urls=[url],
                detail_url_patterns=[
                    str(value) for value in detail_patterns
                ] if isinstance(detail_patterns, list) else [],
                generic_url_patterns=[
                    str(value) for value in generic_patterns
                ] if isinstance(generic_patterns, list) else [],
                source_kind=source_kind,
                priority=priority,
                max_listing_links=min(
                    WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE,
                    int(budget.get("detail_urls", WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE)),
                ),
                max_detail_pages=int(budget.get("detail_pages", WEEKLY_MAX_DETAIL_PAGES)),
            )
        )
    return sorted(adapters, key=lambda item: (item.priority, item.name))


def weekly_reference_pages_for_category(
    category: dict[str, object],
    weekly_category: str,
    coverage_config: dict[str, object],
) -> list[dict[str, object]]:
    adapters = [
        adapter
        for adapter in build_weekly_career_source_adapters(category, coverage_config)
        if weekly_category in adapter.weekly_categories
    ]
    budget = WEEKLY_CATEGORY_DISCOVERY_BUDGETS.get(weekly_category, {})
    try:
        max_listing_pages = int(budget.get("listing_pages", len(adapters)))
    except (TypeError, ValueError):
        max_listing_pages = len(adapters)
    pages: list[dict[str, object]] = []
    for adapter in adapters[:max_listing_pages]:
        for url in adapter.listing_urls:
            pages.append(
                {
                    "name": adapter.name,
                    "url": url,
                    "source_kind": adapter.source_kind,
                }
            )
    return pages


def merge_weekly_source_counts(
    base: dict[str, object],
    updates: dict[str, object],
) -> dict[str, object]:
    merged = {
        str(name): dict(value) if isinstance(value, dict) else {}
        for name, value in base.items()
    }
    for name, value in updates.items():
        if not isinstance(value, dict):
            continue
        target = merged.setdefault(str(name), {})
        for key, count in value.items():
            if isinstance(count, int):
                target[key] = int(target.get(key, 0)) + count
            elif key == "last_error":
                target[key] = str(count)
    return merged


def collect_weekly_career_candidates(
    category: dict[str, object],
    current_time: datetime,
    penalty_keywords: list[str],
) -> list[Candidate]:
    global WEEKLY_CAREER_DISCOVERY_DIAGNOSTICS
    coverage_config = load_weekly_career_coverage_config()
    diagnostics = empty_weekly_career_diagnostics()
    diagnostics["coverage"] = {}
    source_policy = load_weekly_career_source_policy()
    candidates: list[Candidate] = []
    parsed_by_url: dict[str, Candidate | None] = {}
    global_seen_urls: set[str] = set()
    global_source_counts: dict[str, object] = {}
    excluded_by_reason: Counter[str] = Counter()

    for category_config in weekly_coverage_categories(coverage_config):
        weekly_category = str(category_config.get("id", "")).strip()
        if weekly_category not in WEEKLY_CATEGORY_ORDER:
            continue
        label = str(category_config.get("label", "")).strip() or WEEKLY_CATEGORY_LABELS[weekly_category]
        budget = WEEKLY_CATEGORY_DISCOVERY_BUDGETS.get(
            weekly_category,
            {"detail_urls": WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE, "detail_pages": WEEKLY_MAX_DETAIL_PAGES},
        )
        pages = weekly_reference_pages_for_category(category, weekly_category, coverage_config)
        discovered, category_diagnostics = discover_weekly_career_detail_urls(
            pages,
            source_policy,
            WEEKLY_MAX_DETAIL_LINKS_PER_SOURCE,
        )
        source_priority = weekly_category_source_priorities(weekly_category, coverage_config)
        discovered = sorted(
            discovered[: int(budget.get("detail_urls", len(discovered)))],
            key=lambda item: (
                source_priority.index(item.source) if item.source in source_priority else 100,
                WEEKLY_DISCOVERY_SOURCE_PRIORITY.get(item.source, 100),
                item.url,
            ),
        )
        source_counts = category_diagnostics.get("source_counts", {})
        if not isinstance(source_counts, dict):
            source_counts = {}
        diagnostics["reference_pages_total"] = int(diagnostics["reference_pages_total"]) + int(
            category_diagnostics.get("reference_pages_total", 0)
        )
        diagnostics["reference_pages_fetched"] = int(diagnostics["reference_pages_fetched"]) + int(
            category_diagnostics.get("reference_pages_fetched", 0)
        )
        diagnostics["detail_urls_discovered"] = int(diagnostics["detail_urls_discovered"]) + int(
            category_diagnostics.get("detail_urls_discovered", 0)
        )
        for item in discovered:
            global_seen_urls.add(item.url)

        category_coverage = {
            "label": label,
            "target_min": int(category_config.get("target_min", 1) or 1),
            "selected": 0,
            "fresh_items": 0,
            "cached_revalidated_items": 0,
            "detail_urls_discovered": int(category_diagnostics.get("detail_urls_after_dedup", 0)),
            "detail_pages_fetched": 0,
            "excluded_by_reason": {},
            "sources": source_counts,
        }
        per_category_excluded: Counter[str] = Counter()
        for discovered_url in discovered[: int(budget.get("detail_pages", WEEKLY_MAX_DETAIL_PAGES))]:
            source_count = source_counts.setdefault(discovered_url.source, {})
            if not isinstance(source_count, dict):
                source_count = {}
                source_counts[discovered_url.source] = source_count
            if discovered_url.url in parsed_by_url:
                source_count["detail_pages_reused"] = int(source_count.get("detail_pages_reused", 0)) + 1
                candidate = parsed_by_url[discovered_url.url]
                if candidate is not None:
                    candidates.append(candidate)
                continue
            try:
                detail_html = fetch_weekly_career_detail_page(discovered_url.url)
            except (OSError, UnicodeDecodeError, urllib.error.URLError, TimeoutError) as exc:
                per_category_excluded.update(["detail_page_fetch_failed"])
                source_count["detail_fetch_failed"] = int(source_count.get("detail_fetch_failed", 0)) + 1
                source_count["last_error"] = str(exc)[:160]
                parsed_by_url[discovered_url.url] = None
                continue
            diagnostics["detail_pages_fetched"] = int(diagnostics["detail_pages_fetched"]) + 1
            category_coverage["detail_pages_fetched"] = int(category_coverage["detail_pages_fetched"]) + 1
            source_count["detail_pages_fetched"] = int(source_count.get("detail_pages_fetched", 0)) + 1

            candidate = parse_weekly_career_detail_page(
                discovered_url.url,
                detail_html,
                category,
                discovered_url,
                current_time,
                penalty_keywords,
            )
            parsed_by_url[discovered_url.url] = candidate
            if candidate is None:
                per_category_excluded.update(["detail_page_unparseable"])
                source_count["detail_page_unparseable"] = (
                    int(source_count.get("detail_page_unparseable", 0)) + 1
                )
                continue
            candidates.append(candidate)
            diagnostics["detail_candidates_parsed"] = int(diagnostics["detail_candidates_parsed"]) + 1
        category_coverage["excluded_by_reason"] = dict(sorted(per_category_excluded.items()))
        category_coverage["sources"] = source_counts
        diagnostics["coverage"][weekly_category] = category_coverage
        global_source_counts = merge_weekly_source_counts(global_source_counts, source_counts)
        excluded_by_reason.update(per_category_excluded)

    diagnostics["detail_urls_after_dedup"] = len(global_seen_urls)
    diagnostics["excluded_by_reason"] = dict(sorted(excluded_by_reason.items()))
    diagnostics["source_counts"] = global_source_counts
    WEEKLY_CAREER_DISCOVERY_DIAGNOSTICS = diagnostics
    return dedupe_candidates(candidates)


def collect_category(
    config: dict[str, object],
    category: dict[str, object],
    credentials: tuple[str, str] | None,
    current_time: datetime,
    penalty_keywords: list[str],
    dry_run: bool,
) -> list[Candidate] | list[OssIssueCandidate]:
    category_id = str(category.get("id", "")).strip()
    if dry_run:
        return []

    if category_id == OSS_CATEGORY_ID:
        return collect_oss_issue_candidates(category, current_time)
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        return []

    candidates = collect_feed_candidates(config, category, current_time, penalty_keywords)
    candidates.extend(
        collect_reference_candidates(config, category, current_time, penalty_keywords)
    )
    if category_id == WEEKLY_CAREER_CATEGORY_ID:
        candidates.extend(
            collect_company_watchlist_candidates(category, current_time, penalty_keywords)
        )
    if credentials and category_id != WEEKLY_CAREER_CATEGORY_ID:
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
        if args.mode == "weekly-career":
            radar_payload = write_weekly_career_site_radar_payload(current_time)
            print(
                "Wrote weekly career site radar "
                f"({radar_payload['site_count']} site(s), {radar_payload['link_count']} link(s)): "
                f"{WEEKLY_CAREER_SITE_RADAR_OUTPUT_PATH}"
            )
            write_weekly_career_split_outputs(current_time, [])
            return 0

        if args.mode in {"daily-tech", "daily-backend"}:
            write_backend_practical_candidate(current_time)
            write_backend_core_cs_candidate(current_time)
            write_backend_term_candidate(current_time)

        config = load_config(config_path, args.category, args.mode)
        credentials = (
            get_naver_credentials(args.dry_run)
            if args.mode in {"daily-tech", "daily-news"}
            else None
        )
        penalty_keywords = [
            str(keyword).strip()
            for keyword in config.get("penalty_keywords", [])
            if str(keyword).strip()
        ]
        categories = config.get("categories", [])
        if not isinstance(categories, list):
            raise RuntimeError("configs/kr-sources.json must contain a categories array.")

        candidates_by_category: dict[str, list[Candidate] | list[OssIssueCandidate]] = {}
        selected_categories: list[dict[str, object]] = []
        for category in categories:
            if not isinstance(category, dict):
                continue
            selected_categories.append(category)
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

        for category in selected_categories:
            category_id = str(category.get("id", "")).strip()
            write_category_output(
                output_dir,
                category,
                current_time,
                candidates_by_category.get(category_id, []),
                args.mode,
                penalty_keywords=penalty_keywords,
                update_cache=not args.dry_run,
            )

        if args.mode == "daily-tech":
            write_daily_tech_alias_outputs(current_time, candidates_by_category)
        if args.mode in {"daily-tech", "daily-backend"}:
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
