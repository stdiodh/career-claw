#!/usr/bin/env python3
"""Collect RSS/Atom feed candidates without using AI or live web search."""

from __future__ import annotations

import argparse
import difflib
import email.utils
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
MAX_CANDIDATES_PER_CATEGORY = 10
SUMMARY_LIMIT = 240
REQUEST_TIMEOUT_SECONDS = 20
USER_AGENT = "career-feed-rss-collector"
SUPPORTED_TYPES = {"rss", "atom"}


@dataclass(frozen=True)
class FeedItem:
    category: str
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary: str
    matched_keywords: list[str]
    score: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect RSS/Atom feed candidates.")
    parser.add_argument("--sources", default="configs/sources.json")
    parser.add_argument("--refs-dir", default="refs/categories")
    parser.add_argument("--output-dir", default="reports/candidates")
    parser.add_argument(
        "--category",
        default="all",
        help="Category id to collect, or 'all'.",
    )
    return parser.parse_args()


def now_kst() -> datetime:
    return datetime.now(tz=KST)


def truncate_text(value: str, limit: int) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: max(limit - 3, 0)].rstrip()}..."


def strip_html(value: str) -> str:
    unescaped = html.unescape(value or "")
    without_tags = re.sub(r"<[^>]+>", " ", unescaped)
    return " ".join(without_tags.split())


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(element: ET.Element, names: set[str]) -> str:
    for child in element:
        if local_name(child.tag) in names:
            return "".join(child.itertext()).strip()
    return ""


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
    parsed = urllib.parse.urlsplit(url.strip())
    normalized_path = parsed.path.rstrip("/") or parsed.path
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc.lower(), normalized_path, parsed.query, "")
    )


def normalize_title(title: str) -> str:
    normalized = html.unescape(title).lower()
    normalized = re.sub(r"[\W_]+", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def title_is_duplicate(title: str, seen_titles: list[str]) -> bool:
    normalized = normalize_title(title)
    if not normalized:
        return True
    for seen in seen_titles:
        if normalized == seen:
            return True
        if difflib.SequenceMatcher(None, normalized, seen).ratio() >= 0.92:
            return True
    return False


def load_sources(path: Path, category_filter: str) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise RuntimeError("configs/sources.json must contain a sources array.")

    selected = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        category = str(source.get("category", "")).strip()
        if category_filter != "all" and category != category_filter:
            continue
        selected.append(source)
    return selected


def extract_section_keywords(reference_path: Path, heading: str) -> list[str]:
    if not reference_path.exists():
        return []

    keywords: list[str] = []
    in_section = False
    for raw_line in reference_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            in_section = line == f"## {heading}"
            continue
        if not in_section or not line.startswith("- "):
            continue
        keyword = line[2:].strip()
        if keyword:
            keywords.append(keyword)
    return keywords


def load_category_rules(refs_dir: Path, category: str) -> tuple[list[str], list[str]]:
    reference = refs_dir / f"{category}.md"
    priority = extract_section_keywords(reference, "우선순위 키워드")
    excluded = extract_section_keywords(reference, "제외 키워드")
    return priority, excluded


def keyword_matches(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    matches = []
    for keyword in keywords:
        key = keyword.lower()
        if not key:
            continue
        if len(key) <= 2 and re.match(r"^[a-z0-9]+$", key):
            pattern = rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])"
            if re.search(pattern, lowered):
                matches.append(keyword)
            continue
        if key in lowered:
            matches.append(keyword)
    return matches


def score_item(
    title: str,
    summary: str,
    published_at: datetime | None,
    current_time: datetime,
    priority_keywords: list[str],
    excluded_keywords: list[str],
) -> tuple[int, list[str]]:
    searchable = f"{title} {summary}".lower()
    title_lower = title.lower()
    matched = keyword_matches(searchable, priority_keywords)
    excluded = keyword_matches(searchable, excluded_keywords)

    score = 1
    if published_at:
        age = current_time - published_at
        if age <= timedelta(hours=24):
            score += 10
        elif age <= timedelta(hours=72):
            score += 5

    for keyword in matched:
        score += 3
        if keyword.lower() in title_lower:
            score += 2

    score -= 5 * len(excluded)
    return score, matched


def fetch_feed(source: dict[str, str]) -> bytes:
    request = urllib.request.Request(
        str(source["url"]),
        headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read()


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


def parse_feed_items(source: dict[str, str], payload: bytes) -> list[tuple[str, str, str, datetime | None]]:
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


def collect_source_items(
    source: dict[str, str],
    refs_dir: Path,
    current_time: datetime,
) -> list[FeedItem]:
    source_type = str(source.get("type", "")).strip()
    url = str(source.get("url", "")).strip()
    name = str(source.get("name", "")).strip() or "Unknown Source"
    category = str(source.get("category", "")).strip()

    if source_type not in SUPPORTED_TYPES:
        print(f"Skipping unsupported source type for {name}: {source_type}", file=sys.stderr)
        return []
    if not url:
        print(f"Skipping source without URL: {name}", file=sys.stderr)
        return []

    priority_keywords, excluded_keywords = load_category_rules(refs_dir, category)

    try:
        payload = fetch_feed(source)
        parsed_items = parse_feed_items(source, payload)
    except (ET.ParseError, OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Warning: failed to collect source '{name}': {exc}", file=sys.stderr)
        return []

    items = []
    for title, item_url, summary, published_at in parsed_items:
        if not title or not item_url:
            continue
        summary = truncate_text(summary, SUMMARY_LIMIT)
        score, matched = score_item(
            title,
            summary,
            published_at,
            current_time,
            priority_keywords,
            excluded_keywords,
        )
        items.append(
            FeedItem(
                category=category,
                title=truncate_text(title, 240),
                url=item_url.strip(),
                source=name,
                published_at=published_at,
                summary=summary,
                matched_keywords=matched,
                score=score,
            )
        )
    return items


def dedupe_items(items: list[FeedItem]) -> list[FeedItem]:
    deduped: list[FeedItem] = []
    seen_urls: set[str] = set()
    seen_titles: list[str] = []

    for item in sorted(items, key=lambda value: value.score, reverse=True):
        normalized_url = normalize_url(item.url)
        if normalized_url in seen_urls:
            continue
        if title_is_duplicate(item.title, seen_titles):
            continue
        seen_urls.add(normalized_url)
        seen_titles.append(normalize_title(item.title))
        deduped.append(item)

    return deduped


def select_recent_items(items: list[FeedItem], current_time: datetime) -> list[FeedItem]:
    def has_age_within(item: FeedItem, hours: int) -> bool:
        return item.published_at is not None and current_time - item.published_at <= timedelta(hours=hours)

    recent_24 = [item for item in items if has_age_within(item, 24)]
    recent_72 = [item for item in items if has_age_within(item, 72) and item not in recent_24]
    undated = [item for item in items if item.published_at is None]

    selected = recent_24[:]
    if len(selected) < MAX_CANDIDATES_PER_CATEGORY:
        selected.extend(recent_72[: MAX_CANDIDATES_PER_CATEGORY - len(selected)])
    if len(selected) < MAX_CANDIDATES_PER_CATEGORY:
        selected.extend(undated[: MAX_CANDIDATES_PER_CATEGORY - len(selected)])

    return sorted(
        selected,
        key=lambda item: (
            item.score,
            item.published_at or datetime.min.replace(tzinfo=KST),
        ),
        reverse=True,
    )[:MAX_CANDIDATES_PER_CATEGORY]


def serialize_item(item: FeedItem) -> dict[str, object]:
    return {
        "title": item.title,
        "url": item.url,
        "source": item.source,
        "published_at": item.published_at.isoformat() if item.published_at else "",
        "summary": item.summary,
        "matched_keywords": item.matched_keywords,
        "score": item.score,
    }


def write_category_output(
    output_dir: Path,
    category: str,
    generated_at: datetime,
    items: list[FeedItem],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "category": category,
        "generated_at": generated_at.isoformat(),
        "items": [serialize_item(item) for item in items],
    }
    output_path = output_dir / f"{category}.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(items)} candidate(s): {output_path}")


def main() -> int:
    args = parse_args()
    sources_path = Path(args.sources)
    refs_dir = Path(args.refs_dir)
    output_dir = Path(args.output_dir)
    current_time = now_kst()

    try:
        sources = load_sources(sources_path, args.category)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Failed to load source config: {exc}", file=sys.stderr)
        return 1

    collected_by_category: dict[str, list[FeedItem]] = {}
    categories = {str(source.get("category", "")).strip() for source in sources}
    categories.discard("")

    for source in sources:
        category = str(source.get("category", "")).strip()
        if not category:
            continue
        collected_by_category.setdefault(category, [])
        collected_by_category[category].extend(collect_source_items(source, refs_dir, current_time))

    if args.category != "all":
        categories.add(args.category)

    for category in sorted(categories):
        deduped = dedupe_items(collected_by_category.get(category, []))
        selected = select_recent_items(deduped, current_time)
        write_category_output(output_dir, category, current_time, selected)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
