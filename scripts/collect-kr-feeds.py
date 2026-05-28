#!/usr/bin/env python3
"""Collect Korean premium briefing candidates from Naver Search and RSS."""

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
USER_AGENT = "career-feed-kr-collector"
SUPPORTED_FEED_TYPES = {"rss", "atom"}
OSS_CATEGORY_ID = "kr-oss-contribution-opportunities"
RELIABILITY_SCORE = {
    "official": 20,
    "major_media": 12,
    "platform": 10,
    "aggregator": 5,
    "unknown": 0,
}
MODE_CATEGORY_IDS = {
    "daily-tech": {"kr-ai-tech-news", "kr-backend-tech-news", OSS_CATEGORY_ID},
    "weekly-career": {"kr-backend-career-events"},
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
OSS_BEGINNER_KEYWORDS = [
    "documentation",
    "docs",
    "sample",
    "example",
    "test",
    "reproducer",
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
    labels: list[str]
    state: str
    assignees_count: int
    comments: int
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
    risk_reason: str
    score: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect KR_PREMIUM_MODE candidates from Korean sources."
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
        choices=["all", "daily-tech", "weekly-career"],
        default="all",
        help="Collection mode for KR Premium v2 workflows.",
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
        if mode_filter != "all" and category_id not in mode_category_ids:
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
    if category_id == "kr-backend-career-events" and text_contains_any(
        text, FRONTEND_MARKETING_KEYWORDS
    ):
        return "frontend-or-marketing-focused"
    if text_contains_any(text, ["주가", "급등", "급락", "목표가", "투자의견", "관련주"]):
        return "stock-or-investment-only"
    if category_id == "kr-backend-career-events" and not text_contains_any(
        text, BACKEND_KEYWORDS + STUDENT_KEYWORDS
    ):
        return "unclear-backend-student-fit"
    return ""


def deadline_urgency_score_for(category_id: str, text: str, exclude_reason: str) -> int:
    if exclude_reason == "expired-deadline":
        return -50
    if category_id != "kr-backend-career-events":
        return 0
    if text_contains_any(text, ["오늘", "내일", "이번 주", "7일", "마감"]):
        return 20
    if text_contains_any(text, ["접수", "모집", "지원"]):
        return 10
    return 0


def actionability_score_for(category_id: str, text: str) -> int:
    score = keyword_fit_score(text, ACTION_KEYWORDS, 5, 20)
    if category_id == "kr-backend-career-events" and text_contains_any(
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
        candidate = build_candidate(
            category=category,
            title=name,
            url=url,
            source_url=url,
            source="Official reference page",
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


def fetch_github_issues(repository: str, token: str | None) -> list[dict[str, object]]:
    params = urllib.parse.urlencode(
        {
            "state": "open",
            "sort": "updated",
            "direction": "desc",
            "per_page": 50,
        }
    )
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/issues?{params}",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        detail = " ".join(body.split())[:300] if body else exc.reason
        if token and exc.code in {403, 404}:
            print(
                f"Warning: GitHub token could not read {repository} ({exc.code}); "
                "retrying with the public unauthenticated API.",
                file=sys.stderr,
            )
            return fetch_github_issues(repository, None)
        if exc.code == 403:
            print(
                f"Warning: GitHub Issues API rate/auth limit for {repository} "
                f"({exc.code}): {detail}",
                file=sys.stderr,
            )
            return []
        raise RuntimeError(
            f"GitHub Issues API request failed for {repository} ({exc.code}): {detail}"
        ) from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GitHub Issues API request failed for {repository}: {exc}") from exc

    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


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


def oss_issue_scores(
    category: dict[str, object],
    *,
    difficulty_model: dict[str, object],
    text: str,
    labels: list[str],
    assignees_count: int,
    comments: int,
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
    good_first_score = 30 if text_contains_any(label_text, ["good first issue", "help wanted"]) else 0
    p5_match = difficulty_model_matches(difficulty_model, "p5_like", labels, searchable)
    p4_match = difficulty_model_matches(difficulty_model, "p4_like", labels, searchable)
    p5_score = 30 if p5_match else 0
    p4_score = 20 if p4_match else 0
    legacy_label_score = 15 if text_contains_any(label_text, positive_labels) else 0
    direct_spring_score = 15 if text_contains_any(searchable, OSS_DIRECT_SPRING_KEYWORDS) else 0
    assignee_score = 20 if assignees_count == 0 else -40
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
    if text_contains_any(searchable, OSS_SECURITY_KEYWORDS):
        risk_penalty += 70
        risk_reasons.append("security-vulnerability")
    if text_contains_any(searchable, OSS_RELEASE_BLOCKER_KEYWORDS):
        risk_penalty += 60
        risk_reasons.append("release-blocker")
    if text_contains_any(searchable, OSS_DEEP_INTERNALS_KEYWORDS):
        risk_penalty += 60
        risk_reasons.append("deep-internals")
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
    if hard_exclusion or "design-or-epic" in risk_reasons:
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
        + legacy_label_score
        + max(assignee_score, 0)
        + recent_score
        + comments_score
        + direct_spring_score
    )
    penalty_score = (
        risk_penalty
        + max(-assignee_score, 0)
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
            + max(assignee_score, 0)
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
            + max(assignee_score, 0)
            + comments_score,
            100,
        ),
        0,
    )
    score = positive_score - penalty_score
    exclude_reasons = []
    if difficulty_band not in {"p5_like", "p4_like"}:
        exclude_reasons.append(difficulty_band)
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
    repository: str,
    issue: dict[str, object],
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
    raw_body = strip_html(str(issue.get("body") or ""))
    summary = truncate_text(raw_body, OSS_SUMMARY_LIMIT)
    assignees = issue.get("assignees", [])
    assignees_count = len(assignees) if isinstance(assignees, list) else 0
    try:
        comments = int(issue.get("comments", 0))
    except (TypeError, ValueError):
        comments = 0
    created_at = parse_datetime(str(issue.get("created_at", "")))
    updated_at = parse_datetime(str(issue.get("updated_at", "")))
    searchable = f"{repository} {title} {summary} {' '.join(labels)}"
    contribution_type = infer_contribution_type(searchable)
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
        assignees_count=assignees_count,
        comments=comments,
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
        labels=labels,
        state=state,
        assignees_count=assignees_count,
        comments=comments,
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
        first_30_min_action=first_30_min_action,
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
                repository,
                issue,
                current_time,
            )
            if candidate and candidate.difficulty_band in {"p5_like", "p4_like"}:
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
) -> list[Candidate]:
    try:
        max_candidates = int(category.get("max_candidates", DEFAULT_MAX_CANDIDATES))
    except (TypeError, ValueError):
        max_candidates = DEFAULT_MAX_CANDIDATES

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
        "repository": candidate.repository,
        "issue_number": candidate.issue_number,
        "labels": candidate.labels,
        "state": candidate.state,
        "assignees_count": candidate.assignees_count,
        "comments": candidate.comments,
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
    payload = {
        "category": category_id,
        "generated_at": format_kst(generated_at),
        "items": [serialize_candidate(candidate) for candidate in candidates],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(candidates)} candidate(s): {output_path}")


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
    return sort_and_limit(category, candidates)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    output_dir = Path(args.output_dir)
    current_time = now_kst()

    try:
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
            write_category_output(output_dir, category, current_time, candidates)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to collect KR candidates: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
