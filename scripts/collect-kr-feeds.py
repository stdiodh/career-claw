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
REQUEST_TIMEOUT_SECONDS = 20
SUMMARY_LIMIT = 240
TITLE_LIMIT = 240
DEFAULT_DISPLAY = 10
MAX_DISPLAY = 20
DEFAULT_MAX_CANDIDATES = 30
USER_AGENT = "career-feed-kr-collector"
SUPPORTED_FEED_TYPES = {"rss", "atom"}
RELIABILITY_SCORE = {
    "official": 20,
    "major_media": 12,
    "platform": 10,
    "aggregator": 5,
    "unknown": 0,
}


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


def load_config(path: Path, category_filter: str) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    categories = data.get("categories", [])
    if not isinstance(categories, list):
        raise RuntimeError("configs/kr-sources.json must contain a categories array.")

    selected = []
    for category in categories:
        if not isinstance(category, dict):
            continue
        category_id = str(category.get("id", "")).strip()
        if not category_id:
            continue
        if category_filter != "all" and category_id != category_filter:
            continue
        selected.append(category)

    if category_filter != "all" and not selected:
        raise RuntimeError(f"Unknown KR category: {category_filter}")

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


def category_values(category: dict[str, object], key: str) -> list[str]:
    raw_values = category.get(key, [])
    if not isinstance(raw_values, list):
        return []
    return [str(value).strip() for value in raw_values if str(value).strip()]


def text_contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords if keyword)


def count_matches(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword and keyword.lower() in lowered)


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

    searchable = f"{candidate.title} {candidate.summary}"
    if text_contains_any(searchable, penalty_keywords):
        score -= 30

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

    candidate = Candidate(
        category=str(category.get("id", "")).strip(),
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


def serialize_candidate(candidate: Candidate) -> dict[str, object]:
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
    candidates: list[Candidate],
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
) -> list[Candidate]:
    if dry_run:
        return []

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
        config = load_config(config_path, args.category)
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
